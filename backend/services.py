from __future__ import annotations
from .notifications import queue_result_notice
import asyncio
import hashlib
import random
import time
import uuid
from copy import deepcopy

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value

from .combat import apply_player_command, auto_resolve, auto_step, battle_view, create_battle
from .content import MISSION_EVENTS, MISSION_RANKS, MISSION_TEMPLATES
from .game import (
    analyze_mission, mission_rank, mission_rank_unlocked, new_game, normalize_state,
    resolve_mission, set_party_status, snapshot_party,
)
from .models import GuildConfig, MissionInstance, PlayerState
from .settings import settings
from .mission_decisions import initial_scene, decision_view, advance_scene, setup_encounter
from .mission_loot import scene_reward_template
from .reward_visibility import public_reward_preview
from .prison_recruitment import initialize_prisoner
from .economy import POINT_COST
from .combat import _advance_to_player

POOL_SECONDS = 30 * 60
_pool_locks: dict[str, asyncio.Lock] = {}
_player_locks: dict[tuple[str, str], asyncio.Lock] = {}
_debug_pool_overrides: dict[str, dict] = {}
_debug_pool_sequence = 0


def now_ts() -> int:
    return int(time.time())


def pool_slot(ts: int | None = None) -> int:
    ts = ts or now_ts()
    return (ts // POOL_SECONDS) * POOL_SECONDS


def active_pool_slot(guild_id: str, ts: int | None = None) -> int:
    ts = ts or now_ts()
    override = _debug_pool_overrides.get(guild_id)
    if override and int(override["expires_at"]) > ts:
        return int(override["slot"])
    _debug_pool_overrides.pop(guild_id, None)
    return pool_slot(ts)


def force_pool_refresh(guild_id: str, event_id: str) -> int:
    global _debug_pool_sequence
    if event_id not in MISSION_EVENTS:
        raise ValueError("Unknown mission-board event")
    base = pool_slot()
    _debug_pool_sequence += 1
    forced_slot = -(base * 1000 + _debug_pool_sequence)
    _debug_pool_overrides[guild_id] = {
        "slot": forced_slot, "event_id": event_id, "started_at":now_ts(), "expires_at":now_ts() + POOL_SECONDS,
    }
    return forced_slot


def pool_event(guild_id: str, slot: int) -> dict:
    override = _debug_pool_overrides.get(guild_id)
    if override and int(override["slot"]) == slot:
        event_id = override["event_id"]
        return {"id": event_id, "roll": None, "debug_forced": True, **MISSION_EVENTS[event_id]}
    seed = int.from_bytes(hashlib.sha256(f"event:{guild_id}:{slot}".encode()).digest()[:8], "big")
    roll = random.Random(seed).randrange(1000)
    # A natural event must be followed by at least one ordinary board.
    previous_seed=int.from_bytes(hashlib.sha256(f"event:{guild_id}:{slot-POOL_SECONDS}".encode()).digest()[:8],"big")
    previous_roll=random.Random(previous_seed).randrange(1000)
    event_floor=min(int(e['min_roll']) for eid,e in MISSION_EVENTS.items() if eid!='general')
    if previous_roll>=event_floor:
        return {"id":"general","roll":roll,"quiet_board":True,**MISSION_EVENTS['general']}
    event_id = "general"
    for candidate_id, event in sorted(MISSION_EVENTS.items(), key=lambda item: int(item[1].get("min_roll", 0))):
        if roll >= int(event.get("min_roll", 0)):
            event_id = candidate_id
    return {"id": event_id, "roll": roll, **MISSION_EVENTS[event_id]}


def _weighted_template(rng: random.Random, rank: str, event_id: str) -> str:
    general = [(mid, float(m.get("pool_weight", 1))) for mid, m in MISSION_TEMPLATES.items() if m.get("rank", "E") == rank and not m.get("event") and not m.get("chain_only") and not m.get("trigger_only")]
    themed = [(mid, float(m.get("pool_weight", 1))) for mid, m in MISSION_TEMPLATES.items() if m.get("rank", "E") == rank and m.get("event") == event_id and not m.get("trigger_only")]
    pool = themed if event_id != "general" and themed and rng.random() < 0.65 else general
    if not pool:
        pool = themed or general
    total = sum(weight for _, weight in pool)
    point = rng.random() * total
    cursor = 0.0
    for mission_id, weight in pool:
        cursor += weight
        if point <= cursor:
            return mission_id
    return pool[-1][0]


def _rolled_pool_templates(guild_id: str, slot: int, player_count: int) -> list[str]:
    # Stable player cohorts let the current pool grow when another player joins without
    # changing the missions that were already generated earlier in the slot.
    scaled_players = max(1, player_count)
    event_id = pool_event(guild_id, slot)["id"]
    rng = random.Random(int.from_bytes(hashlib.sha256(f"pool:{guild_id}:{slot}".encode()).digest()[:8], "big"))
    template_ids: list[str] = []
    for player_index in range(scaled_players):
        e_count = 16
        template_ids.extend(_weighted_template(rng, "E", event_id) for _ in range(e_count))
        template_ids.extend(_weighted_template(rng, "D", event_id) for _ in range(8))
        for rank, possible, chance in (("C", 5, 0.60), ("B", 3, 0.35), ("A", 2, 0.12), ("S", 3, 0.01)):
            for _ in range(possible):
                if rng.random() < chance:
                    template_ids.append(_weighted_template(rng, rank, event_id))
    return template_ids


async def ensure_guild_config(session: AsyncSession, guild_id: str) -> GuildConfig:
    row = await session.get(GuildConfig, guild_id)
    if row is None:
        row = GuildConfig(guild_id=guild_id, announcement_channel_id=None, created_at=now_ts())
        session.add(row)
        await session.flush()
    return row


async def ensure_pool(session: AsyncSession, guild_id: str, ts: int | None = None) -> tuple[list[MissionInstance], bool]:
    ts = ts or now_ts()
    slot = active_pool_slot(guild_id, ts)
    refresh_window = _debug_pool_overrides.get(guild_id,{}).get('started_at',pool_slot(ts))
    lock = _pool_locks.setdefault(guild_id, asyncio.Lock())
    async with lock:
        existing = (await session.execute(
            select(MissionInstance).where(MissionInstance.guild_id == guild_id, MissionInstance.pool_slot == slot).order_by(MissionInstance.position)
        )).scalars().all()
        from .registration import registered_count
        player_count = await registered_count(session,guild_id)
        template_ids = _rolled_pool_templates(guild_id, slot, player_count)
        pool_size = len(template_ids)
        if len(existing) >= pool_size:
            return [row for row in existing if not MISSION_TEMPLATES[row.template_id].get("trigger_only") and not (row.analysis or {}).get("chain_owner_user_id")], False

        seed_bytes = hashlib.sha256(f"{guild_id}:{slot}".encode()).digest()
        rng = random.Random(int.from_bytes(seed_bytes[:8], "big"))
        spawned = []
        for position in range(len(existing), pool_size):
            template_id = template_ids[position]
            template = MISSION_TEMPLATES[template_id]
            raw_duration = int(rng.choice(template["durations"]))
            effective_duration = max(1, int(raw_duration * settings.mission_time_scale))
            instance = MissionInstance(
                id=f"mis_{uuid.uuid4().hex}", guild_id=guild_id, template_id=template_id,
                pool_slot=slot, position=position, spawned_at=refresh_window, expires_at=refresh_window + POOL_SECONDS,
                duration_seconds=effective_duration, status="available",
                analysis={'public_wave':1 if position%2==0 else 2},
            )
            session.add(instance)
            spawned.append(instance)
        await ensure_guild_config(session, guild_id)
        await session.flush()
        return [row for row in list(existing) + spawned if not MISSION_TEMPLATES[row.template_id].get("trigger_only") and not (row.analysis or {}).get("chain_owner_user_id")], True


async def available_chain_missions(
    session: AsyncSession, guild_id: str, user_id: str, ts: int | None = None,
) -> list[MissionInstance]:
    """Private follow-ups are visible only to the player who unlocked them."""
    ts = ts or now_ts()
    # Recover older earned leads without extending their original claim window.
    sources = (await session.execute(select(MissionInstance).where(
        MissionInstance.guild_id == guild_id,
        MissionInstance.claimed_by_user_id == user_id,
        MissionInstance.status == "completed",
        MissionInstance.resolved_at > ts - 86400,
    ))).scalars().all()
    for source in sources:
        for lead in (source.result or {}).get("board_followups", []):
            await _spawn_chain_instance(session, source, user_id, lead.get("template_id"), source.resolved_at)
    candidates = (await session.execute(
        select(MissionInstance).where(
            MissionInstance.guild_id == guild_id,
            MissionInstance.status.in_(["available", "reserved"]),
            MissionInstance.expires_at > ts,
        ).order_by(MissionInstance.spawned_at, MissionInstance.position)
    )).scalars().all()
    return [
        row for row in candidates
        if (row.analysis or {}).get("chain_owner_user_id") == user_id
    ]


def claim_budget(state, slot, started_at, ts=None):
    ts=now_ts() if ts is None else ts
    age=max(0,ts-started_at)
    phase='wave1' if age<60 else 'wave2' if age<120 else 'free'
    solo_bonus=10 if sum(not c.get('temporary_mercenary') for c in state.get('characters',[]))==1 else 0
    limit=3+int(state.get('claim_upgrade',0))+solo_bonus if phase=='free' else 5
    ledger=state.get('contract_points',{})
    used=int(ledger.get('spent',{}).get(phase,0)) if ledger.get('slot')==slot else 0
    return {'phase':phase,'remaining':max(0,limit-used),'limit':limit,'solo_bonus':solo_bonus if phase=='free' else 0,
            'next_phase_at':started_at+(60 if phase=='wave1' else 120) if phase!='free' else None,
            'costs':POINT_COST}


def spend_claim(state, mission, ts):
    if (mission.analysis or {}).get('chain_owner_user_id'):return
    budget=claim_budget(state,mission.pool_slot,mission.spawned_at,ts)
    if (mission.analysis or {}).get('public_wave',1)==2 and ts<mission.spawned_at+60:
        raise ValueError('This contract arrives in the second wave')
    cost=POINT_COST[MISSION_TEMPLATES[mission.template_id].get('rank','E')]
    if budget['remaining']<cost:raise ValueError(f"Not enough Contract Points: {cost} needed, {budget['remaining']} left in this phase")
    if state.get('contract_points',{}).get('slot')!=mission.pool_slot:state['contract_points']={'slot':mission.pool_slot,'spent':{}}
    spent=state['contract_points']['spent'];spent[budget['phase']]=spent.get(budget['phase'],0)+cost


async def reserve_instance(session,guild_id,user_id,name,mission_id):
    async with _player_locks.setdefault((guild_id,user_id),asyncio.Lock()):
        player=(await session.execute(select(PlayerState).where(PlayerState.guild_id==guild_id,PlayerState.user_id==user_id).with_for_update())).scalar_one_or_none()
        if not player:raise ValueError('Create your character first')
        mission=await session.get(MissionInstance,mission_id);ts=now_ts()
        if not mission or mission.guild_id!=guild_id:raise ValueError('Mission not found')
        _check_chain_owner(mission,user_id)
        if mission.status=='reserved' and mission.claimed_by_user_id==user_id:return mission
        if mission.status!='available' or mission.expires_at<=ts:raise ValueError('This contract was claimed or expired')
        original_state=deepcopy(player.state)
        state=normalize_state(deepcopy(original_state));template=MISSION_TEMPLATES[mission.template_id]
        if not (mission.analysis or {}).get('chain_owner_user_id') and not mission_rank_unlocked(state,template.get('rank','E')):raise ValueError('Unlock this mission rank first')
        spend_claim(state,mission,ts)
        metadata={**(mission.analysis or {}),'chain_owner_user_id':user_id,'private_source_name':'Claimed from the public board'}
        changed=await session.execute(update(MissionInstance).where(MissionInstance.id==mission_id,MissionInstance.status=='available',MissionInstance.expires_at>ts).values(status='reserved',claimed_by_user_id=user_id,claimed_by_name=name,claimed_at=ts,expires_at=ts+86400,analysis=metadata))
        if changed.rowcount!=1:raise ValueError('Someone claimed this contract just before you')
        updated=await session.execute(update(PlayerState).where(PlayerState.guild_id==guild_id,PlayerState.user_id==user_id,PlayerState.state==original_state).values(state=state,updated_at=ts).execution_options(synchronize_session=False))
        if updated.rowcount!=1:raise ValueError('Your camp changed while claiming; try again')
        set_committed_value(player,'state',state);set_committed_value(player,'updated_at',ts)
        await session.flush();return await session.get(MissionInstance,mission_id)


async def abandon_reservation(session,guild_id,user_id,mission_id):
    changed=await session.execute(update(MissionInstance).where(MissionInstance.id==mission_id,MissionInstance.guild_id==guild_id,MissionInstance.claimed_by_user_id==user_id,MissionInstance.status=='reserved').values(status='abandoned'))
    if changed.rowcount!=1:raise ValueError('Only unstarted owned contracts can be abandoned')


def _check_chain_owner(mission: MissionInstance, user_id: str) -> None:
    owner = (mission.analysis or {}).get("chain_owner_user_id")
    if owner and owner != user_id:
        raise ValueError("Mission not found")


async def _spawn_chain_instance(
    session: AsyncSession, parent: MissionInstance, user_id: str, template_id: str, ts: int,
) -> MissionInstance | None:
    template = MISSION_TEMPLATES.get(template_id)
    if not template or not (template.get("chain_only") or template.get("trigger_only")):
        return None
    chain_id = template.get("chain_id")
    player = await session.get(PlayerState, {"guild_id": parent.guild_id, "user_id": user_id})
    final_celestials = {
        candidate.get("celestial_reward") for candidate in MISSION_TEMPLATES.values()
        if chain_id and candidate.get("chain_id") == chain_id and candidate.get("celestial_reward")
    }
    owned_sources = {char.get("source_id") for char in (player.state.get("characters", []) if player else [])}
    if any(f"celestial:{celestial_id}" in owned_sources for celestial_id in final_celestials):
        return None
    candidates = (await session.execute(
        select(MissionInstance).where(MissionInstance.guild_id == parent.guild_id)
    )).scalars().all()
    for legacy in candidates:
        if legacy.template_id == template_id and (legacy.analysis or {}).get("world_trigger_source_id") == parent.id:
            if legacy.status == "available" and not (legacy.analysis or {}).get("chain_owner_user_id"):
                legacy.pool_slot = -(uuid.uuid4().int % 8_000_000_000_000_000 + 1)
                legacy.expires_at = ts + 86400
                legacy.analysis = {**(legacy.analysis or {}), "chain_owner_user_id": user_id,
                    "chain_parent_id": parent.id, "private_source_name": f"Follow-up to {MISSION_TEMPLATES[parent.template_id]['name']}"}
                await session.flush()
                return legacy
            return None
    if any(row.template_id == template_id and (row.analysis or {}).get("chain_parent_id") == parent.id for row in candidates):
        return None
    if any(
        chain_id and row.id != parent.id
        and
        row.status in {"available", "claimed", "battle", "decision"}
        and (row.status != 'available' or row.expires_at > ts)
        and (row.analysis or {}).get("chain_owner_user_id") == user_id
        and (row.analysis or {}).get("chain_id") == chain_id
        for row in candidates
    ):
        return None
    seed = random.Random(f"chain:{parent.id}:{template_id}")
    duration = max(1, int(seed.choice(template["durations"]) * settings.mission_time_scale))
    row = MissionInstance(
        id=f"mis_{uuid.uuid4().hex}", guild_id=parent.guild_id, template_id=template_id,
        pool_slot=-(uuid.uuid4().int % 8_000_000_000_000_000 + 1), position=0,
        spawned_at=ts, expires_at=ts + 24 * 60 * 60, duration_seconds=duration,
        status="available", analysis={
            "chain_owner_user_id": user_id, "chain_parent_id": parent.id,
            "chain_id": template.get("chain_id"), "chain_step": template.get("chain_step"),
            "chain_total": template.get("chain_total"),
            "world_trigger_source_id": parent.id if template.get("trigger_only") else None,
            "world_trigger_source_name": MISSION_TEMPLATES[parent.template_id]["name"],
            "world_triggered_by_name": parent.claimed_by_name,
            "private_source_name": template.get("private_source_name", f"Follow-up to {MISSION_TEMPLATES[parent.template_id]['name']}"),
        },
    )
    session.add(row)
    await session.flush()
    return row


async def spawn_private_contract(
    session: AsyncSession, guild_id: str, user_id: str, template_id: str,
    source_name: str = "Private lead", ts: int | None = None,
) -> MissionInstance:
    """Create an owner-only contract without putting it in the shared pool."""
    ts = ts or now_ts()
    template = MISSION_TEMPLATES.get(template_id)
    if not template or not template.get("chain_only"):
        raise ValueError("Unknown private contract")
    player = await session.get(PlayerState, {"guild_id": guild_id, "user_id": user_id})
    if not player:
        raise ValueError("Create your character first")
    existing = (await session.execute(
        select(MissionInstance).where(
            MissionInstance.guild_id == guild_id,
            MissionInstance.template_id == template_id,
            MissionInstance.status.in_(["available", "reserved", "claimed", "battle", "decision"]),
            (MissionInstance.status != 'available') | (MissionInstance.expires_at > ts),
        )
    )).scalars().all()
    owned = [row for row in existing if (row.analysis or {}).get("chain_owner_user_id") == user_id]
    if owned:
        return owned[0]
    duration = max(1, int(random.Random(f"private:{guild_id}:{user_id}:{template_id}:{ts}").choice(template["durations"]) * settings.mission_time_scale))
    row = MissionInstance(
        id=f"mis_{uuid.uuid4().hex}", guild_id=guild_id, template_id=template_id,
        pool_slot=-(uuid.uuid4().int % 8_000_000_000_000_000 + 1), position=0,
        spawned_at=ts, expires_at=ts + 24 * 60 * 60, duration_seconds=duration,
        status="available", analysis={
            "chain_owner_user_id": user_id, "chain_parent_id": f"private:{source_name}",
            "chain_id": template.get("chain_id"), "chain_step": template.get("chain_step"),
            "chain_total": template.get("chain_total"), "private_source_name": source_name,
        },
    )
    session.add(row)
    await session.flush()
    return row


async def _spawn_result_chains(
    session: AsyncSession, mission: MissionInstance, user_id: str, result: dict, ts: int,
) -> list[MissionInstance]:
    if result.get("outcome") not in {"success", "critical_success"}:
        return []
    template = MISSION_TEMPLATES[mission.template_id]
    next_ids = list(result.get("rewards", {}).get("chain_starts", []))
    if template.get("chain_next"):
        next_ids.append(template["chain_next"])
    next_ids.extend(entry["template_id"] for entry in result.get("board_followups", []) if entry.get("template_id"))
    spawned = []
    for template_id in dict.fromkeys(next_ids):
        row = await _spawn_chain_instance(session, mission, user_id, template_id, ts)
        if row:
            spawned.append(row)
    if spawned:
        result["chain_unlocked"] = [
            {"mission_id": row.id, "name": MISSION_TEMPLATES[row.template_id]["name"], "expires_at": row.expires_at}
            for row in spawned
        ]
    return spawned


async def spawn_prisoner_contract(session, guild_id, user_id, prisoner):
    """One active allegiance quest per captive; failed/expired attempts may be retried."""
    r=prisoner['recruitment']
    if not r['revealed'] or r['terms_met']:
        raise ValueError('Discuss unfinished recruitment terms first.')
    if prisoner.get('holding')!='prison_cell':
        raise ValueError('Secure the prisoner before pursuing their agreement.')
    quest_route=r.get('quest_route',r['route'])
    if quest_route not in ('rival','former','proof','rescue'):
        raise ValueError('This agreement asks for resources or an item, not a mission.')
    if r.get('requires_proof') and not r.get('payment_met'):
        raise ValueError('Fulfill the requested payment before starting the proof contract.')
    prior=await session.get(MissionInstance,r['quest_id']) if r.get('quest_id') else None
    if prior and prior.guild_id==guild_id and (prior.analysis or {}).get('chain_owner_user_id')==user_id and prior.status in ('available','reserved','claimed','battle','decision') and (prior.expires_at>now_ts() or prior.status in ('claimed','battle','decision')):
        return prior
    ts=now_ts();template_id=f"prison_{quest_route}_{r['rank'].lower()}"
    row=MissionInstance(id=f'mis_{uuid.uuid4().hex}',guild_id=guild_id,template_id=template_id,
        pool_slot=-(uuid.uuid4().int%8_000_000_000_000_000+1),position=0,spawned_at=ts,expires_at=ts+86400,
        duration_seconds=1,status='available',analysis={'chain_owner_user_id':user_id,
        'private_source_name':f"Allegiance: {prisoner['name']}",'prisoner_allegiance_id':prisoner['id'],
        'prisoner_allegiance_route':r['route'],'prisoner_allegiance_name':prisoner['name']})
    r['quest_id']=row.id;session.add(row);await session.flush();return row


def mission_summary(row: MissionInstance, include_result: bool = False, viewer_rank: str | None = None) -> dict:
    m = MISSION_TEMPLATES[row.template_id]
    rank = m.get("rank", "E")
    display_status = row.status
    if row.status in {"available","reserved"} and row.expires_at <= now_ts():
        display_status = "expired"
    locked = not (row.analysis or {}).get("chain_owner_user_id") and viewer_rank in MISSION_RANKS and MISSION_RANKS.index(rank) > MISSION_RANKS.index(viewer_rank)
    if locked:
        return {
            "id": row.id, "rank": rank, "locked": True, "status": display_status,
            "name": f"{rank}-Rank missions available", "description": "Upgrade Guild Hall mission visibility to reveal this rank.",
            "party_size": 0, "duration_seconds": 0, "requirements": [], "reward_preview": [],
            "roles": [], "claimed_by_name": None,
        }
    data = {
        "id": row.id, "template_id": row.template_id, "name": m["name"], "description": m["description"],
        "rank": rank, "locked": False,
        "point_cost": POINT_COST[rank],
        "stat": m["stat"], "difficulty": m["difficulty"], "party_size": m["party_size"],
        "duration_seconds": 0, "status": display_status,
        "spawned_at": row.spawned_at, "expires_at": row.expires_at,
        "claimed_by_user_id": row.claimed_by_user_id, "claimed_by_name": row.claimed_by_name,
        "claimed_at": row.claimed_at, "completes_at": row.completes_at,
        "visible_hints": m.get("visible_hints", []),
        "roles": m.get("roles", []),
        "has_special_critical": bool(m.get("critical_any") or m.get("combat_critical_condition")),
        "combat_critical_condition": m.get("combat_critical_condition"),
        "critical_success_available": bool((row.analysis or {}).get("critical_success_available", not m.get("critical_any"))),
        "requirements": [r.get("label", "Requirement") for r in m.get("claim_requirements", [])],
        "reward_preview": public_reward_preview(m),
        "mission_form": m.get("mission_form", "operation"),
        "objective": m.get("objective", ""),
        "resolution_mode": m.get("resolution_mode", "roll"),
        "encounter_plan": m.get("encounter_plan", {}),
        "bodyguard_slots": m.get("bodyguard_slots", 0),
        "story_thread": {"id": m.get("story_thread"), "name": m.get("story_thread_name"), "context": m.get("world_context")},
        "combat_encounter": m.get("combat_encounter"),
        "has_decisions": bool(m.get("decision_scene")),
    }
    if (row.analysis or {}).get("world_trigger_source_id"):
        data["world_trigger"] = {
            "source_mission": (row.analysis or {}).get("world_trigger_source_name"),
            "triggered_by": (row.analysis or {}).get("world_triggered_by_name"),
        }
    if (row.analysis or {}).get("chain_owner_user_id"):
        data["private_source"] = (row.analysis or {}).get("private_source_name", "Earned follow-up")
    if m.get("chain_only"):
        data["chain"] = {
            "id": m.get("chain_id"), "step": m.get("chain_step"), "total": m.get("chain_total"),
            "private": True, "claim_by": row.expires_at,
        }
        data["private_source"] = (row.analysis or {}).get("private_source_name", "Earned follow-up")
    if (row.analysis or {}).get('prisoner_allegiance_name'):
        data['name']+=f" - {row.analysis['prisoner_allegiance_name']}"
    if include_result:
        data["result"] = row.result
    return data


async def get_player(session: AsyncSession, guild_id: str, user_id: str) -> PlayerState | None:
    row = await session.get(PlayerState, {"guild_id": guild_id, "user_id": user_id})
    if row:
        previous=deepcopy(row.state);normalized=normalize_state(deepcopy(previous))
        if normalized!=previous:
            changed=await session.execute(update(PlayerState).where(PlayerState.guild_id==guild_id,PlayerState.user_id==user_id,PlayerState.state==previous).values(state=normalized,updated_at=now_ts()).execution_options(synchronize_session=False))
            if changed.rowcount==1:
                set_committed_value(row,'state',normalized);set_committed_value(row,'updated_at',now_ts())
            else:await session.refresh(row)
    return row


async def create_player(session: AsyncSession, guild_id: str, user_id: str, display_name: str, character: dict) -> PlayerState:
    if await get_player(session, guild_id, user_id):
        raise ValueError("A save already exists in this Discord server")
    from .registration import set_registration
    await set_registration(session,guild_id,user_id,display_name)
    row = PlayerState(guild_id=guild_id, user_id=user_id, display_name=display_name, state=normalize_state(new_game(character)), updated_at=now_ts())
    session.add(row)
    await ensure_guild_config(session, guild_id)
    await session.flush()
    return row


async def analyze_instance(
    session: AsyncSession, guild_id: str, user_id: str, mission_id: str,
    party_ids: list[str], role_assignments: dict[str, str] | None = None,
    bodyguard_ids: list[str] | None = None, mercenary_ids: list[str] | None = None,
) -> dict:
    mission = await session.get(MissionInstance, mission_id)
    if not mission or mission.guild_id != guild_id:
        raise ValueError("Mission not found")
    _check_chain_owner(mission, user_id)
    if mission.status not in {"available","reserved"} or mission.expires_at <= now_ts():
        raise ValueError("Mission is no longer available")
    player = await get_player(session, guild_id, user_id)
    if not player:
        raise ValueError("Create your character first")
    if not (mission.analysis or {}).get("chain_owner_user_id") and not mission_rank_unlocked(player.state, MISSION_TEMPLATES[mission.template_id].get("rank", "E")):
        raise ValueError("Upgrade your Guild Hall to reveal this mission rank")
    from .mercenaries import prepare, quote, contract_rank
    preview = deepcopy(player.state)
    preview['_mercenary_owner'] = user_id
    offers = prepare(preview, mission, mercenary_ids, party_ids, bodyguard_ids, role_assignments)
    analysis = analyze_mission(preview, MISSION_TEMPLATES[mission.template_id], party_ids, role_assignments, bodyguard_ids)
    # Hidden criteria remain hidden before resolution. Players get truthful rates, not the secret recipe.
    return {
        "mercenary_fee": sum(quote(o,contract_rank(mission))["fee"] for o in offers), "mercenary_penalty": -min(4,len(offers)),
        "stamina": analysis["stamina"],
        "party_size_ok": analysis["party_size_ok"], "availability_ok": analysis["availability_ok"],
        "requirements": analysis["requirements"], "claimable": analysis["claimable"],
        "lead": analysis["lead"], "lead_stat": analysis["lead_stat"], "stat": analysis["stat"],
        "probabilities": analysis["probabilities"],
        "critical_path_active": bool(analysis["critical_unlocks"]),
        "critical_success_available": analysis["critical_success_available"],
        "secret_event_possible": analysis["secret_event_possible"],
        "role_assignments_ok": analysis["role_assignments_ok"], "roles": analysis["roles"],
        "bodyguards_ok": analysis["bodyguards_ok"], "bodyguards": analysis["bodyguards"],
    }


async def claim_instance(
    session: AsyncSession, guild_id: str, user_id: str, display_name: str,
    mission_id: str, party_ids: list[str], role_assignments: dict[str, str] | None = None,
    bodyguard_ids: list[str] | None = None, mercenary_ids: list[str] | None = None,
) -> MissionInstance:
    key = (guild_id, user_id)
    lock = _player_locks.setdefault(key, asyncio.Lock())
    async with lock:
        player = (await session.execute(
            select(PlayerState).where(PlayerState.guild_id == guild_id, PlayerState.user_id == user_id).with_for_update()
        )).scalar_one_or_none()
        if not player:
            raise ValueError("Create your character first")
        player.state = normalize_state(deepcopy(player.state))

        mission = await session.get(MissionInstance, mission_id)
        if not mission or mission.guild_id != guild_id:
            raise ValueError("Mission not found")
        _check_chain_owner(mission, user_id)
        if mission.status not in {"available","reserved"} or mission.expires_at <= now_ts():
            raise ValueError("Someone already claimed this mission, or it expired")
        if not (mission.analysis or {}).get("chain_owner_user_id") and not mission_rank_unlocked(player.state, MISSION_TEMPLATES[mission.template_id].get("rank", "E")):
            raise ValueError("Upgrade your Guild Hall to claim this mission rank")

        state = deepcopy(player.state)
        template = MISSION_TEMPLATES[mission.template_id]
        from .mercenaries import prepare, betrayal, decorate_battle, betrayal_battle
        state['_mercenary_owner'] = user_id
        hired = prepare(state, mission, mercenary_ids, party_ids, bodyguard_ids, role_assignments, spend=True)
        state.pop('_mercenary_owner', None)
        captive_id=(mission.analysis or {}).get('prisoner_allegiance_id')
        captive=next((p for p in state.get('prisoners',[]) if p['id']==captive_id),None) if captive_id else None
        if captive_id and (not captive or captive.get('holding')!='prison_cell' or captive.get('recruitment',{}).get('terms_met')):
            raise ValueError('This prisoner must remain secured with unfinished terms to start their contract.')
        chain_metadata = dict(mission.analysis or {})
        if mission.status=='available':spend_claim(state,mission,now_ts())
        analysis = analyze_mission(state, template, party_ids, role_assignments, bodyguard_ids)
        for key in (
            "chain_owner_user_id", "chain_parent_id", "chain_id", "chain_step", "chain_total",
            "world_trigger_source_id", "world_trigger_source_name", "world_triggered_by_name",
            "private_source_name", "prisoner_allegiance_id", "prisoner_allegiance_route", "prisoner_allegiance_name",
        ):
            if key in chain_metadata:
                analysis[key] = chain_metadata[key]
        analysis['mercenary_ids'] = [o['id'] for o in hired]
        analysis['mercenary_traitors'] = betrayal(hired, mission.id)
        resolved_party_ids = list(analysis["party_ids"])
        if not analysis["claimable"]:
            missing = [x["label"] for x in analysis["requirements"] if not x["met"]]
            if not analysis["party_size_ok"]:
                if template.get("roles"):
                    missing.insert(0, "Assign one unique character to every mission role")
                else:
                    missing.insert(0, f"Exactly {template['party_size']} characters required")
            if not analysis["availability_ok"]:
                missing.append("Every selected character must be idle")
            if not analysis["bodyguards_ok"]:
                missing.append("Bodyguards must be idle, unique, and within the available bodyguard slots")
            if not analysis["stamina"]["eligible"]:
                missing.append("Every selected character needs at least 1 stamina point")
            raise ValueError("Cannot claim: " + "; ".join(missing or ["party is not eligible"]))

        claimed_at = now_ts()
        combat_definition = template.get("combat_encounter")
        has_scene = bool(template.get("decision_scene"))
        branch_definition = template.get("branching_encounter")
        if branch_definition and not has_scene:
            branch_roll = random.Random(f"{mission.id}:encounter-branch").randint(1, 100)
            branch_triggered = branch_roll <= int(branch_definition.get("trigger_chance", 0))
            analysis["branch"] = {
                "triggered": branch_triggered, "roll": branch_roll,
                "trigger_text": branch_definition.get("trigger_text", "The mission becomes a tactical encounter."),
            }
            if branch_triggered:
                combat_definition = branch_definition
        deployed_party_ids = [*resolved_party_ids, *analysis.get("bodyguard_ids", [])]
        from .stamina import spend as spend_stamina
        analysis["stamina"] = spend_stamina(state, deployed_party_ids, template.get("rank", "E"))
        from .relationships import record_mission_start
        record_mission_start(state,deployed_party_ids)
        analysis["service_record_started"]=True
        if has_scene:
            analysis['scene'] = initial_scene()
        elif combat_definition:
            analysis["battle"] = create_battle(state, deployed_party_ids, mission.id, combat_definition.get("id", mission.template_id),defer_start=True)
            if captive and combat_definition.get('id','').startswith('contract:'):
                from .combat import create_contract_battle
                analysis['battle']=create_contract_battle(state,deployed_party_ids,mission.id,mission.template_id,defer_start=True,race_override=captive.get('race'))
            if captive and captive['recruitment']['route']=='rescue' and template.get('rank') in ('E','D'):
                enemies=[u for u in analysis['battle']['units'].values() if u.get('team')=='enemy']
                keep={u['id'] for u in enemies if u.get('boss')}|{u['id'] for u in enemies[:1]}
                for u in enemies:
                    if u['id'] not in keep:
                        analysis['battle']['units'].pop(u['id'],None)
                    else:
                        u.update(hp=min(u['hp'],14),max_hp=min(u['max_hp'],14),attack=3,armor=0)
                analysis['battle']['turn_order']=[uid for uid in analysis['battle']['turn_order'] if uid in analysis['battle']['units']]
                analysis['battle']['turn_index']=0
            elif captive and captive['recruitment']['route']=='rescue':
                tier=max(0,'EDCBAS'.index(template.get('rank','C'))-1)
                for unit in analysis['battle']['units'].values():
                    if unit.get('team')=='enemy':
                        unit['hp']=unit['max_hp']=round(unit['max_hp']*(1+.2*tier))
                        unit['attack']+=tier
            decorate_battle(state, analysis, analysis["battle"], mission.id)
            if captive:
                analysis['battle']['name']=f"{template['name']} - {captive['name']}"
            if analysis["battle"]["status"] == "active" and not analysis["mercenary_traitors"]:
                _advance_to_player(analysis["battle"])
        mission_status = "decision" if has_scene else "battle" if combat_definition else "claimed"
        completes_at = None if combat_definition or has_scene else claimed_at
        if analysis['mercenary_traitors']:
            analysis['mercenary_resume_status'] = mission_status
            analysis['mercenary_resume_battle'] = analysis.pop('battle', None)
            analysis['battle'] = betrayal_battle(state, deployed_party_ids, analysis['mercenary_traitors'], mission.id)
            mission_status, completes_at = 'battle', None
        else:
            for unit in analysis.get('battle',{}).get('units',{}).values():
                if unit['id'] in analysis['mercenary_ids']:unit['mercenary_id']=unit['id']
        original_status=mission.status
        stmt = (
            update(MissionInstance)
            .where(
                MissionInstance.id == mission_id,
                MissionInstance.guild_id == guild_id,
                MissionInstance.status == original_status,
                (MissionInstance.claimed_by_user_id.is_(None) | (MissionInstance.claimed_by_user_id==user_id)),
                MissionInstance.expires_at > claimed_at,
            )
            .values(
                status=mission_status, claimed_by_user_id=user_id, claimed_by_name=display_name,
                claimed_at=claimed_at, completes_at=completes_at, party_ids=deployed_party_ids,
                party_snapshot=snapshot_party(state, deployed_party_ids), analysis=analysis,
            )
        )
        result = await session.execute(stmt)
        if result.rowcount != 1:
            raise ValueError("Someone claimed this mission just before you")

        set_party_status(state, deployed_party_ids, "mission")
        player.state = state
        player.display_name = display_name
        player.updated_at = claimed_at
        await session.flush()
        refreshed = await session.get(MissionInstance, mission_id)
        await session.refresh(refreshed)
        return refreshed


async def get_decision_instance(session: AsyncSession, guild_id: str, user_id: str, mission_id: str) -> dict:
    mission = await session.get(MissionInstance, mission_id)
    if not mission or mission.guild_id != guild_id or mission.claimed_by_user_id != user_id:
        raise ValueError('Mission not found')
    if mission.status != 'decision':
        raise ValueError('This mission is not waiting for a decision')
    player = await get_player(session,guild_id,user_id)
    return decision_view(player.state,MISSION_TEMPLATES[mission.template_id],mission.analysis)


def _start_scene_encounter(state: dict, mission: MissionInstance, analysis: dict, transition: dict) -> None:
    template = MISSION_TEMPLATES[mission.template_id]
    encounter = transition['battle']
    if encounter == 'default':
        encounter = template['combat_encounter']['id']
    battle = create_battle(state,mission.party_ids,mission.id,encounter,defer_start=True)
    setup_encounter(battle,transition)
    from .mercenaries import decorate_battle
    decorate_battle(state,analysis,battle,mission.id)
    for unit in battle['units'].values():
        if unit['id'] in analysis.get('mercenary_ids',[]):unit['mercenary_id']=unit['id']
    if battle['status']=='active':
        _advance_to_player(battle)
    analysis['battle']=battle
    analysis['scene_boss']=bool(transition.get('boss'))
    analysis['scene_template_id']=mission.template_id
    if transition.get('after_battle'):
        analysis['post_battle_node'] = transition['after_battle']
    mission.analysis=analysis
    mission.status='battle'
    mission.completes_at=None


async def choose_decision_instance(session: AsyncSession, guild_id: str, user_id: str, mission_id: str, node_id: str, revision: int, choice_id: str) -> dict:
    async with _player_locks.setdefault((guild_id,user_id),asyncio.Lock()):
        mission=(await session.execute(select(MissionInstance).where(MissionInstance.id==mission_id).with_for_update())).scalar_one_or_none()
        if not mission or mission.guild_id!=guild_id or mission.claimed_by_user_id!=user_id:
            raise ValueError('Mission not found')
        if mission.status!='decision':raise ValueError('This mission is no longer waiting for a decision')
        player=(await session.execute(select(PlayerState).where(PlayerState.guild_id==guild_id,PlayerState.user_id==user_id).with_for_update())).scalar_one()
        state=normalize_state(deepcopy(player.state));analysis=deepcopy(mission.analysis)
        template=MISSION_TEMPLATES[mission.template_id]
        scene,transition=advance_scene(state,template,analysis,mission.id,node_id,revision,choice_id)
        analysis['scene']=scene
        changed=await session.execute(update(MissionInstance).where(
            MissionInstance.id==mission_id, MissionInstance.status=='decision',
            MissionInstance.analysis['scene']['revision'].as_integer()==revision,
        ).values(analysis=analysis).execution_options(synchronize_session=False))
        if changed.rowcount!=1:raise ValueError('This decision was already taken. Reopen the mission.')
        mission.analysis=analysis
        result=None
        if transition.get('battle'):
            _start_scene_encounter(state,mission,analysis,transition)
        elif transition.get('finish'):
            if transition['finish'] == 'battle_outcome':
                if not analysis.get('pending_battle_outcome'):
                    raise ValueError('This agreement has no completed battle to hand over')
                analysis['post_battle_resolved'] = True
                mission.analysis = analysis
                player.state = state
                result = await _finish_battle(session, mission, player, analysis['battle'])
                await session.flush()
                return {'mission': mission_summary(mission), 'decision': None, 'result': result}
            party_ids=list(analysis.get('mission_party_ids') or analysis.get('party_ids') or mission.party_ids)
            finish=transition['finish']
            # More dialogue nodes must not multiply the chance of a critical mission finish.
            if finish=='success':
                from .outcome_balance import scene_critical_chance
                chance=scene_critical_chance(scene['history'],template.get('rank','E'),analysis.get('critical_success_available',not template.get('critical_any')))
                if random.Random(f'{mission.id}:scene-finale').randint(1,10000)/100<=chance:finish='critical_success'
            result=resolve_mission(state,scene_reward_template(template,analysis),party_ids,analysis,seed=mission.id,forced_outcome=finish)
            result['debug_forced']=False
            result['resolution_source']='scene'
            result['scene_history']=scene['history']
            result['story']=[entry['text'] for entry in scene['history'] if entry.get('text')] + result['story']
            set_party_status(state,list(analysis.get('bodyguard_ids',[])),'idle')
            from .mercenaries import settle
            settle(state,analysis,result['outcome'])
            await _spawn_result_chains(session,mission,user_id,result,now_ts())
            mission.result=result;mission.status='completed';mission.resolved_at=now_ts();mission.completes_at=now_ts()
            await queue_result_notice(session,mission)
        player.state=state;player.updated_at=now_ts()
        await session.flush()
        return {'mission':mission_summary(mission),'decision':decision_view(state,template,analysis) if mission.status=='decision' else None,'result':result}


async def debug_start_battle(
    session: AsyncSession, guild_id: str, user_id: str, display_name: str, encounter_id: str,
) -> MissionInstance:
    """Create or resume a requirement-free implemented battle for testing."""
    if encounter_id not in {"goblin_warcamp", "goblin_captive_cart", "goblin_smoke_signals", "frontier_watch_defense"}:
        raise ValueError("Unknown debug battle")
    template_id = "hedgerow_watch_defense" if encounter_id == "frontier_watch_defense" else encounter_id
    key = (guild_id, user_id)
    lock = _player_locks.setdefault(key, asyncio.Lock())
    async with lock:
        active = (await session.execute(
            select(MissionInstance).where(
                MissionInstance.guild_id == guild_id,
                MissionInstance.claimed_by_user_id == user_id,
                MissionInstance.status == "battle",
                MissionInstance.template_id == template_id,
            ).order_by(MissionInstance.claimed_at.desc())
        )).scalars().all()
        for mission in active:
            if (mission.analysis or {}).get("debug_battle"):
                return mission

        player = (await session.execute(
            select(PlayerState).where(
                PlayerState.guild_id == guild_id, PlayerState.user_id == user_id,
            ).with_for_update()
        )).scalar_one_or_none()
        if not player:
            raise ValueError("Create your character first")

        state = normalize_state(deepcopy(player.state))
        idle = [character for character in state.get("characters", []) if character.get("status") == "idle"]
        idle.sort(key=lambda character: (not character.get("is_player"), character.get("name", "")))
        party = idle[:2]
        temporary_ids: list[str] = []
        source = party[0] if party else next(iter(state.get("characters", [])), None)
        if not source:
            raise ValueError("No character is available to seed the debug party")
        while len(party) < 2:
            ally = deepcopy(source)
            ally_id = f"debug_{uuid.uuid4().hex[:12]}"
            ally.update({
                "id": ally_id, "source_id": f"debug:{encounter_id}", "source_kind": "debug",
                "is_player": False, "name": f"Battle Tester {len(temporary_ids) + 1}",
                "status": "idle", "assignment": None, "equipment": {},
            })
            ally["attributes"] = {"str": 8, "dex": 7, "agi": 7, "vit": 8, "int": 5, "luk": 5}
            ally.setdefault("perks", {})["combat"] = "skilled"
            state["characters"].append(ally)
            party.append(ally)
            temporary_ids.append(ally_id)

        party_ids = [character["id"] for character in party]
        template = MISSION_TEMPLATES[template_id]
        role_assignments = {"tank": party_ids[0], "dps": party_ids[1]} if template.get("roles") else {}
        analysis = (
            analyze_mission(state, template, party_ids[:1], role_assignments, party_ids[1:2])
            if encounter_id == "goblin_smoke_signals"
            else analyze_mission(state, template, party_ids, role_assignments)
        )
        analysis.update({
            "debug_battle": True,
            "debug_requirement_bypass": True,
            "debug_temporary_character_ids": temporary_ids,
            "battle": create_battle(state, party_ids, f"debug:{guild_id}:{user_id}:{uuid.uuid4().hex}", encounter_id),
        })
        # Keep rewards and narrative effects attached to a real roster member.
        analysis["lead_id"] = next((character["id"] for character in party if character["id"] not in temporary_ids), party_ids[0])

        claimed_at = now_ts()
        mission = MissionInstance(
            id=f"mis_{uuid.uuid4().hex}", guild_id=guild_id, template_id=template_id,
            pool_slot=-(uuid.uuid4().int % 8_000_000_000_000_000 + 1), position=0,
            spawned_at=claimed_at, expires_at=claimed_at + 24 * 60 * 60, duration_seconds=0,
            status="battle", claimed_by_user_id=user_id, claimed_by_name=display_name,
            claimed_at=claimed_at, completes_at=None, party_ids=party_ids,
            party_snapshot=snapshot_party(state, party_ids), analysis=analysis,
        )
        session.add(mission)
        set_party_status(state, party_ids, "mission")
        player.state = state
        player.display_name = display_name
        player.updated_at = claimed_at
        await session.flush()
        return mission


async def debug_start_goblin_battle(
    session: AsyncSession, guild_id: str, user_id: str, display_name: str,
) -> MissionInstance:
    return await debug_start_battle(session, guild_id, user_id, display_name, "goblin_warcamp")


async def get_battle_instance(
    session: AsyncSession, guild_id: str, user_id: str, mission_id: str,
) -> dict:
    mission = await session.get(MissionInstance, mission_id)
    if not mission or mission.guild_id != guild_id or mission.claimed_by_user_id != user_id:
        raise ValueError("Battle not found")
    battle = (mission.analysis or {}).get("battle")
    if not battle or mission.status not in {"battle", "completed"}:
        raise ValueError("This mission does not have an active tactical battle")
    battle = deepcopy(battle)
    player = await get_player(session, guild_id, user_id)
    from .combat_supplies import sync_supplies
    sync_supplies(battle, player.state)
    return battle_view(battle)


def _plain_name_list(names: list[str]) -> str:
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _story_attack(actor: str, target: str, weapon: str, nonlethal: bool = False) -> str:
    weapon_key = str(weapon or "").lower()
    if weapon_key in {"", "unarmed"}:
        return (
            f"{actor} got inside {target}'s reach, forced {target} to the ground, and held on until the struggle stopped."
            if nonlethal else
            f"{actor} met {target} at close range and brought the fight to an end."
        )
    if any(word in weapon_key for word in ("bow", "crossbow")):
        return (
            f"{actor} waited until {target} stepped clear of the other fighters, then sent an arrow into the opening. "
            + (f"The shot dropped {target} without killing them." if nonlethal else f"{target} fell before reaching cover.")
        )
    if any(word in weapon_key for word in ("staff", "wand", "grimoire", "spell", "bolt")):
        return (
            f"{actor} caught {target} with a spell as the fighting closed around the command mound. "
            + (f"The spell left {target} alive but unable to continue." if nonlethal else f"{target} did not get back up.")
        )
    return (
        f"{actor} faced {target} beside the command mound. Their weapons met until {actor} found a way through {target}'s guard. "
        + (f"{target} went down alive." if nonlethal else f"The final strike killed {target}.")
    )


def _warcamp_story(
    battle: dict, primary: dict, resolution: str, killed: list[dict], captured: list[dict],
    subdued: list[dict], fled: list[dict], remaining: list[dict],
) -> list[str]:
    party = [unit for unit in battle.get("units", {}).values() if unit.get("team") == "player"]
    party_names = _plain_name_list([unit["name"] for unit in party]) or "The party"
    chief_name = primary["name"]
    paragraphs = [
        f"{party_names} entered the warcamp from the south. {chief_name} was directing the defense from the command mound, with an archer behind the palisade and an alarm bell ready near the edge of the camp. A locked prisoner pen stood farther inside."
    ]

    pen = battle.get("objects", {}).get("prisoner_pen", {})
    horn = battle.get("objects", {}).get("alarm_horn", {})
    objective_beats = []
    if battle.get("reinforcements_spawned"):
        objective_beats.append("The horn sounded before the party could silence it. Two more goblins came through the perimeter and joined the defense.")
    handled = []
    if pen.get("state") == "opened":
        handled.append((int(pen.get("handled_round", 99)), "pen", pen.get("handled_by", "A party member")))
    if horn.get("state") == "disabled":
        handled.append((int(horn.get("handled_round", 99)), "horn", horn.get("handled_by", "A party member")))
    for _, kind, actor in sorted(handled):
        if kind == "pen":
            objective_beats.append(f"{actor} reached the prisoner pen during the fighting and pulled the door open. The captives needed no urging; they ran for the south exit as soon as the way was clear.")
        elif battle.get("reinforcements_spawned"):
            objective_beats.append(f"{actor} reached the horn after the reinforcements arrived and tore it out of use before another call could be sent.")
        else:
            objective_beats.append(f"{actor} crossed the camp before the horncaller could raise the alarm and put the horn out of use.")
    if objective_beats:
        paragraphs.append(" ".join(objective_beats))

    supporting = next((
        unit for unit in [*killed, *captured]
        if unit is not primary and unit.get("defeated_by") and unit.get("defeated_by") != primary.get("defeated_by")
    ), None)
    confrontation = [f"At the center of the camp, {chief_name} tried to keep the defense together."]
    if supporting:
        attacker = supporting["defeated_by"]
        weapon = supporting.get("defeat_weapon", "")
        confrontation.append(_story_attack(attacker, supporting["name"], weapon, nonlethal=supporting in captured))
        confrontation.append("That gave the others room to reach the mound.")

    attacker = primary.get("defeated_by")
    weapon = primary.get("defeat_weapon", "")
    if resolution in {"killed", "captured_alive", "subdued_but_left_behind", "subdued"}:
        if attacker:
            confrontation.append(_story_attack(attacker, chief_name, weapon, nonlethal=resolution != "killed"))
        elif resolution == "killed":
            confrontation.append(f"The fight around the mound ended with {chief_name} dead.")
        else:
            confrontation.append(f"The fight around the mound ended with {chief_name} unconscious.")
        if resolution == "captured_alive":
            confrontation.append(f"Before {chief_name} could recover, the party bound the chieftain and prepared to carry their prisoner out.")
        elif resolution.startswith("subdued"):
            confrontation.append(f"There was no time to secure {chief_name}. The party left the unconscious chieftain where they fell.")
        if battle.get("battle_won"):
            confrontation.append("The goblins who saw their leader fall lost their nerve. Some threw down what they were carrying; the rest ran for the nearest gap in the camp wall.")
    elif resolution == "escaped":
        confrontation.append(f"The line around the mound broke apart, but {chief_name} slipped through the retreat and escaped with the fleeing goblins.")
    else:
        confrontation.append(f"The party could not break the defense around the mound. {chief_name} was still giving orders when they began to withdraw.")
    paragraphs.append(" ".join(confrontation))

    captured_others = [unit["name"] for unit in captured if unit is not primary]
    escaped_others = [unit["name"] for unit in fled if unit is not primary]
    closing = []
    if captured_others:
        closing.append(f"They brought {_plain_name_list(captured_others)} out with them as prisoners.")
    if battle.get("battlefield_secured"):
        closing.append("No defenders remained to contest the camp. The party searched the tents, gathered what could be carried, and returned through the south approach.")
    elif battle.get("battle_won"):
        closing.append("The party left through the camp exits before the scattered goblins could gather again.")
        if escaped_others:
            closing.append(f"{_plain_name_list(escaped_others)} disappeared beyond the perimeter during the retreat.")
    else:
        closing.append("The survivors covered one another until everyone still able to move had cleared the camp.")
    if closing:
        paragraphs.append(" ".join(closing))
    return paragraphs


def _warcamp_recap(
    primary: dict, resolution: str, killed: list[dict], captured: list[dict],
    subdued: list[dict], fled: list[dict], remaining: list[dict], battle: dict,
) -> list[str]:
    recap = []
    labels = {
        "killed": "killed", "captured_alive": "captured alive",
        "subdued_but_left_behind": "subdued and left behind", "subdued": "subdued",
        "escaped": "escaped", "still_active": "still active",
    }
    recap.append(f"{primary['name']}: {labels.get(resolution, resolution.replace('_', ' '))}.")
    for unit in (enemy for enemy in killed if enemy is not primary):
        actor = unit.get("defeated_by")
        weapon = unit.get("defeat_weapon")
        if actor and str(weapon).lower() == "unarmed":
            recap.append(f"{actor} killed {unit['name']} in close combat.")
        elif actor:
            recap.append(f"{actor} killed {unit['name']}{f' with {weapon}' if weapon else ''}.")
        else:
            recap.append(f"{unit['name']} was killed.")
    if captured:
        others = [unit["name"] for unit in captured if unit is not primary]
        if others:
            recap.append(f"Captured alive: {_plain_name_list(others)}.")
    if subdued:
        recap.append(f"Left unconscious: {_plain_name_list([unit['name'] for unit in subdued])}.")
    if fled:
        recap.append(f"Escaped: {_plain_name_list([unit['name'] for unit in fled])}.")
    if remaining:
        recap.append(f"Still in the camp: {_plain_name_list([unit['name'] for unit in remaining])}.")
    return recap


def _captive_cart_story(battle: dict, cartmaster: dict, resolution: str) -> list[str]:
    party_names = _plain_name_list([
        unit["name"] for unit in battle.get("units", {}).values() if unit.get("team") == "player"
    ]) or "The party"
    courier = battle.get("units", {}).get("captive_courier", {})
    courier_name = courier.get("name", "the wounded courier")
    cartmaster_name = cartmaster.get("name", "the cartmaster")
    paragraphs = [
        f"{party_names} waited beside the hedgerows until the shielded wagon entered the narrow part of the road. {courier_name} lay wounded near the rear wheel, while {cartmaster_name} kept the escort between the guild and the cart."
    ]
    if courier.get("alive") and courier.get("extracted"):
        carrier = battle.get("units", {}).get(courier.get("extracted_with", ""), {}).get("name")
        if carrier:
            paragraphs.append(f"{carrier} reached {courier_name}, lifted the injured courier clear of the wagon, and carried them through the guild line. Only after the courier was safe did the party turn back toward the escort.")
        else:
            paragraphs.append(f"The fighting moved away from the rear wheel long enough for the party to reach {courier_name}. The wounded courier crossed the guild line alive before the escort could close the road again.")
    elif not courier.get("alive"):
        paragraphs.append(f"The escort kept the party away from {courier_name} too long. By the time anyone reached the wagon, the courier had died, and the rescue had become a retreat.")
    else:
        paragraphs.append(f"The party never opened a safe route to {courier_name}. The captive cart began moving again while the guild fell back from the road.")

    attacker = cartmaster.get("defeated_by")
    weapon = cartmaster.get("defeat_weapon", "")
    if resolution == "captured_alive":
        action = _story_attack(attacker, cartmaster_name, weapon, nonlethal=True) if attacker else f"The party pulled {cartmaster_name} from the fight alive."
        paragraphs.append(action + f" They bound {cartmaster_name} beside the wagon and took the cartmaster back for questioning.")
    elif resolution == "killed":
        action = _story_attack(attacker, cartmaster_name, weapon) if attacker else f"{cartmaster_name} died beside the wagon."
        paragraphs.append(action + " Whatever the cartmaster knew about the route died there as well.")
    elif resolution == "escaped":
        paragraphs.append(f"{cartmaster_name} abandoned the wagon when the escort broke and escaped down the road before the party could close the distance.")
    elif resolution.startswith("subdued"):
        paragraphs.append(f"{cartmaster_name} was knocked unconscious, but the party could not carry the cartmaster out before it withdrew.")

    satchel = battle.get("objects", {}).get("dispatch_satchel", {})
    if satchel.get("state") == "extracted":
        paragraphs.append("Before leaving, the party recovered the stolen dispatch satchel from the cart. Its route marks showed that the Black Banner was moving prisoners and supplies toward the same old royal sites named in earlier reports.")
    elif courier.get("alive") and courier.get("extracted"):
        paragraphs.append("With the courier alive, the party left the cart and its remaining cargo behind rather than risk losing the rescue on the road home.")
    return paragraphs


def _smoke_signals_story(battle: dict, captain: dict, resolution: str) -> list[str]:
    party_names = _plain_name_list([
        unit["name"] for unit in battle.get("units", {}).values() if unit.get("team") == "player"
    ]) or "The party"
    captain_name = captain["name"]
    paragraphs = [
        f"{party_names} followed the smoke marks to a farm road and found the real signal site beyond the hedgerow. "
        f"{captain_name} had scouts waiting beside a marked chart of the nearby farms. Once the goblins saw the investigators' notes, they moved to close the road."
    ]
    attacker = captain.get("defeated_by")
    if resolution == "killed":
        paragraphs.append(
            f"{attacker} stopped {captain_name} during the fight. The captain's death broke the signal crew, and the remaining scouts ran for the far hedge."
            if attacker else f"The fighting ended with {captain_name} dead. Without their captain, the remaining scouts ran for the far hedge."
        )
    elif resolution == "captured_alive":
        paragraphs.append(
            f"{attacker} brought {captain_name} down alive. The party bound the captain before the other scouts could return."
            if attacker else f"The party subdued {captain_name}, bound the captain, and scattered the remaining scouts."
        )
    elif resolution.startswith("subdued"):
        paragraphs.append(f"The party knocked {captain_name} unconscious and broke the signal crew, but withdrew before the captain could be secured.")
    elif resolution == "escaped":
        paragraphs.append(f"The signal crew broke apart, but {captain_name} escaped through the far hedgerow with the route back to the warhost.")
    else:
        paragraphs.append(f"The scouts kept control of the clearing. {captain_name} was still directing them when the party withdrew with what notes it could save.")
    chart = battle.get("objects", {}).get("signal_chart", {})
    if chart.get("state") == "extracted":
        paragraphs.append("The party carried the marked farm chart back to Fortcamp. It showed which roads the warhost had watched and which farms it planned to isolate next.")
    elif battle.get("battle_won"):
        paragraphs.append("The party returned with the signal pattern and the location of the scout post, but the marked farm chart remained behind.")
    return paragraphs


def _battle_outcome_details(battle: dict) -> dict:
    enemies = [unit for unit in battle.get("units", {}).values() if unit.get("team") == "enemy"]
    captured_ids = set(battle.get("auto_captured_ids", [])) | {
        unit["id"] for unit in enemies
        if unit.get("condition") == "unconscious" and unit.get("extracted")
    }
    killed = [unit for unit in enemies if unit.get("condition") == "dead" and not unit.get("fled")]
    captured = [unit for unit in enemies if unit.get("condition") == "unconscious" and unit["id"] in captured_ids]
    subdued = [
        unit for unit in enemies
        if unit.get("condition") == "unconscious" and unit["id"] not in captured_ids and not unit.get("fled")
    ]
    fled = [unit for unit in enemies if unit.get("fled")]
    remaining = [
        unit for unit in enemies
        if unit not in killed and unit not in captured and unit not in subdued and unit not in fled
        and not unit.get("extracted")
    ]

    primary_ids = {
        "goblin_warcamp": "gob_chief", "goblin_captive_cart": "cartmaster_vrak",
        "goblin_smoke_signals": "signal_captain",
    }
    primary = battle.get("units", {}).get(battle.get("primary_target_id") or primary_ids.get(battle.get("encounter_id"), ""))
    primary_target = None
    if primary:
        if primary in killed:
            resolution = "killed"
        elif primary in captured:
            resolution = "captured_alive"
        elif primary in subdued:
            resolution = "subdued_but_left_behind"
        elif primary in fled or primary.get("extracted"):
            resolution = "escaped"
        elif primary.get("condition") == "unconscious":
            resolution = "subdued"
        else:
            resolution = "still_active"
        primary_target = {"id": primary["id"], "name": primary["name"], "resolution": resolution}

    aftermath: list[str] = []
    recap: list[str] = []
    if battle.get("encounter_id") == "goblin_warcamp" and primary:
        resolution = primary_target["resolution"]
        aftermath = _warcamp_story(battle, primary, resolution, killed, captured, subdued, fled, remaining)
        recap = _warcamp_recap(primary, resolution, killed, captured, subdued, fled, remaining, battle)
    elif battle.get("encounter_id") == "goblin_captive_cart" and primary:
        resolution = primary_target["resolution"]
        aftermath = _captive_cart_story(battle, primary, resolution)
        recap = _warcamp_recap(primary, resolution, killed, captured, subdued, fled, remaining, battle)
    elif battle.get("encounter_id") == "goblin_smoke_signals" and primary:
        resolution = primary_target["resolution"]
        aftermath = _smoke_signals_story(battle, primary, resolution)
        recap = _warcamp_recap(primary, resolution, killed, captured, subdued, fled, remaining, battle)

    return {
        "primary_target": primary_target,
        "enemy_outcome": {
            "killed": [unit["name"] for unit in killed],
            "captured": [unit["name"] for unit in captured],
            "subdued_unsecured": [unit["name"] for unit in subdued],
            "fled": [unit["name"] for unit in fled],
            "remaining": [unit["name"] for unit in remaining],
        },
        "aftermath": aftermath,
        "recap": recap,
    }


def _store_captured_prisoners(state: dict, battle: dict, mission: MissionInstance) -> list[dict]:
    state.setdefault("prisoners", [])
    existing_sources = {prisoner.get("capture_key") for prisoner in state["prisoners"]}
    from .game import STOCKADE_LIMIT_SECONDS, prison_capacity, prisoner_sale_value
    available_cells = max(0, prison_capacity(state) - sum(
        prisoner.get("holding") == "prison_cell" for prisoner in state["prisoners"]
    ))
    captured_at = now_ts()
    captured_ids = set(battle.get("auto_captured_ids", [])) | {
        unit["id"] for unit in battle.get("units", {}).values()
        if unit.get("team") == "enemy" and unit.get("condition") == "unconscious" and unit.get("extracted")
    }
    stored = []
    mission_name = MISSION_TEMPLATES.get(mission.template_id, {}).get("name", mission.template_id)
    for unit_id in sorted(captured_ids):
        unit = battle.get("units", {}).get(unit_id)
        if not unit or unit.get("team") != "enemy" or unit.get("condition") != "unconscious" or unit.get('creature') or unit.get('mercenary_id'):
            continue
        capture_key = f"{mission.id}:{unit_id}"
        if capture_key in existing_sources:
            continue
        secured = available_cells > 0
        if secured:
            available_cells -= 1
        prisoner = {
            "id": f"prisoner_{uuid.uuid4().hex}", "capture_key": capture_key,
            "name": unit.get("name", "Unknown Prisoner"), "race": unit.get("race", "Unknown"),
            "gender": unit.get("gender", ""), "kind": unit.get("kind", "combatant"),
            "portrait": unit.get("portrait_full") or unit.get("portrait", ""),
            "portrait_thumbnail": unit.get("portrait", ""), "portrait_pool": unit.get("portrait_pool", ""),
            "weapon": unit.get("weapon", "Unarmed"), "boss": bool(unit.get("boss") or unit.get("kind") == "chieftain"),
            "status": "held", "holding": "prison_cell" if secured else "temporary_stockade",
            "captured_at": captured_at, "captured_from_mission_id": mission.id,
            "captured_from_template": mission.template_id, "captured_from_name": mission_name,
            "recruitment_state": "locked", "sale_state": "available",
        }
        if not secured:
            prisoner["stockade_remaining_seconds"] = STOCKADE_LIMIT_SECONDS
            prisoner["stockade_expires_at"] = captured_at + STOCKADE_LIMIT_SECONDS
        prisoner["sale_value"] = prisoner_sale_value(prisoner)
        if unit.get('recruitable_snapshot'):
            prisoner['recruitable_snapshot']=deepcopy(unit['recruitable_snapshot'])
        initialize_prisoner(prisoner, MISSION_TEMPLATES.get(mission.template_id,{}).get('rank','E'),captured_at)
        state["prisoners"].append(prisoner)
        stored.append(prisoner)
    return stored


def _award_capture_loot(state: dict, battle: dict, result: dict) -> list[dict]:
    captured_ids = set(battle.get("auto_captured_ids", [])) | {
        unit["id"] for unit in battle.get("units", {}).values()
        if unit.get("team") == "enemy" and unit.get("condition") == "unconscious" and unit.get("extracted")
    }
    rewards = []
    candidates = []
    encounter_id = battle.get("encounter_id")
    from .gear_progression import CAPTURE_DROPS
    authored=CAPTURE_DROPS.get(encounter_id)
    captive=battle.get('units',{}).get(authored['target'],{}) if authored else {}
    if authored and authored['target'] in captured_ids and captive.get('condition')=='unconscious' and captive.get('alive',True) and result.get('outcome') in {'success','critical_success'}:
        candidates.append({'item_id':authored['item'],'reason':f"Captured {battle['units'][authored['target']]['name']} alive",
                           'chance':authored['chance']+(authored['secured_bonus'] if battle.get('battlefield_secured') else 0)})
    if encounter_id == "goblin_warcamp" and "gob_chief" in captured_ids:
        candidates.append({
            "item_id": "chieftain_command_horn",
            "reason": f"Captured {battle['units']['gob_chief']['name']} alive",
            "chance": 35 if battle.get("battlefield_secured") else 20,
        })
    if encounter_id == "goblin_captive_cart" and "cartmaster_vrak" in captured_ids:
        satchel_recovered = battle.get("objects", {}).get("dispatch_satchel", {}).get("state") == "extracted"
        candidates.append({
            "item_id": "cartmaster_route_book",
            "reason": f"Captured {battle['units']['cartmaster_vrak']['name']} alive",
            "chance": 55 if satchel_recovered else 35,
        })
    for candidate in candidates:
        roll = random.Random(
            f"{battle.get('seed', 'battle')}:capture-loot:{candidate['item_id']}"
        ).randint(1, 100)
        won = roll <= candidate["chance"]
        result["rewards"].setdefault("loot_rolls", []).append({
            "source": candidate["reason"], "roll": roll, "chance": candidate["chance"],
            "item": candidate["item_id"] if won else None,
            "possible_item": candidate["item_id"], "kind": "capture",
        })
        if not won:
            continue
        reward = {"item_id": candidate["item_id"], "reason": candidate["reason"], "roll": roll, "chance": candidate["chance"]}
        rewards.append(reward)
        state.setdefault("inventory", []).append({
            "instance_id": f"item_{uuid.uuid4().hex}", "item_id": reward["item_id"],
        })
        result["rewards"].setdefault("items", []).append(reward["item_id"])
    result["rewards"]["capture_rewards"] = rewards
    return rewards


async def _finish_battle(
    session: AsyncSession, mission: MissionInstance, player: PlayerState, battle: dict,
) -> dict:
    state = normalize_state(deepcopy(player.state))
    analysis = dict(mission.analysis or {})
    tactical_outcome = battle.get("outcome", "failure")
    if analysis.get('post_battle_node') and not analysis.get('post_battle_resolved') and not battle.get('mercenary_interlude') and tactical_outcome in {'success', 'critical_success'}:
        analysis['pending_battle_outcome'] = tactical_outcome
        analysis['scene']['node'] = analysis['post_battle_node']
        analysis['scene']['revision'] += 1
        analysis['battle'] = battle
        mission.analysis = analysis
        mission.status = 'decision'
        mission.completes_at = None
        await session.flush()
        return {'scene_continuation': True, 'mission_id': mission.id}
    from .mercenaries import settle
    if battle.get('mercenary_interlude') and tactical_outcome != 'critical_failure':
        settle(state,analysis,tactical_outcome,battle,final=False)
        traitors = set(analysis.get('mercenary_traitors',[]))
        for offer in state.get('mercenaries',[]):
            if offer['id'] in traitors:offer['busy_mission_id']=None
        # Turncoats leave the expedition. The original objective and reward roll survive.
        state['characters']=[c for c in state['characters'] if c['id'] not in traitors]
        state['inventory']=[i for i in state['inventory'] if not i.get('mercenary_gear') or not any(mid in i['instance_id'] for mid in traitors)]
        mission.party_ids=[cid for cid in (mission.party_ids or analysis.get('party_ids',[])) if cid not in traitors]
        for key in ('party_ids','mission_party_ids','bodyguard_ids'):
            if key in analysis:analysis[key]=[cid for cid in analysis[key] if cid not in traitors]
        analysis['role_assignments']={key:cid for key,cid in analysis.get('role_assignments',{}).items() if cid not in traitors}
        recalculated=analyze_mission(state,MISSION_TEMPLATES[mission.template_id],analysis.get('party_ids',mission.party_ids),analysis.get('role_assignments'),analysis.get('bodyguard_ids'))
        for key in ('lead','lead_stat','support_bonus','criteria_bonus','probabilities','critical_success_available','critical_unlocks','triggered','roles'):
            if key in recalculated:analysis[key]=recalculated[key]
        resume=analysis.pop('mercenary_resume_status','claimed')
        resumed_battle=analysis.pop('mercenary_resume_battle',None)
        analysis.pop('battle',None)
        if resume=='battle' and resumed_battle:
            for mid in traitors:resumed_battle['units'].pop(mid,None)
            resumed_battle['turn_order']=[cid for cid in resumed_battle['turn_order'] if cid not in traitors]
            resumed_battle['turn_index']=0
            for unit in resumed_battle['units'].values():
                if unit['id'] in analysis.get('mercenary_ids',[]):unit['mercenary_id']=unit['id']
            _advance_to_player(resumed_battle)
            analysis['battle']=resumed_battle
        mission.status=resume
        mission.completes_at=now_ts() if resume=='claimed' else None
        mission.analysis=analysis
        player.state=state
        await session.flush()
        return {'mercenary_interlude':True,'resume_status':resume,'mission_id':mission.id}

    if analysis.get('scene_boss'):
        boss=battle.get('units',{}).get(battle.get('complication_boss'),{})
        recovered=set(battle.get('auto_looted_ids',[])) | set(battle.get('auto_captured_ids',[]))
        analysis['scene_boss']=bool(boss.get('condition') in {'dead','unconscious'} and not boss.get('fled') and (boss.get('id') in recovered or boss.get('extracted')))
    if tactical_outcome == "critical_success":
        analysis["critical_success_available"] = True
        analysis.setdefault("critical_unlocks", []).append({
            "label": (
                f"Extracted {battle.get('units', {}).get('captive_courier', {}).get('name', 'the courier')}, captured {battle.get('units', {}).get('cartmaster_vrak', {}).get('name', 'the cartmaster')} alive, and recovered the stolen dispatches"
                if battle.get("encounter_id") == "goblin_captive_cart"
                else MISSION_TEMPLATES[mission.template_id].get("combat_critical_condition", "Completed the battle's bonus objective") if battle.get("encounter_id", "").startswith("contract:")
                else f"Freed captives and silenced the alarm before defeating {battle.get('units', {}).get('gob_chief', {}).get('name', 'the goblin chieftain')}"
            ),
        })
    mission_party_ids = list(analysis.get("mission_party_ids") or mission.party_ids or [])
    result = resolve_mission(
        state, scene_reward_template(MISSION_TEMPLATES[mission.template_id],analysis), mission_party_ids,
        analysis, seed=f"{mission.id}:battle", forced_outcome=tactical_outcome,
    )
    result['debug_forced']=False
    set_party_status(state, list(analysis.get("bodyguard_ids", [])), "idle")
    from .relationships import record_battle
    record_battle(state,battle)
    recovered_ids = set(battle.get("auto_looted_ids", []))
    corpse_loot = []
    loot_rng = random.Random(f"{mission.id}:corpse-loot")
    for unit_id in sorted(recovered_ids):
        unit = battle.get("units", {}).get(unit_id)
        if not unit or unit.get("team") != "enemy" or unit.get("condition") != "dead" or unit.get('lost_in_pit'):
            continue
        kind = unit.get("kind", "raider")
        gold_low, gold_high = (6, 12) if kind == "chieftain" else (1, 5) if kind == "archer" else (0, 4)
        if unit.get('corpse_gold') is not None:gold_low,gold_high=unit['corpse_gold']
        gold = loot_rng.randint(gold_low, gold_high)
        item_id = None
        item_roll = loot_rng.randint(1, 100)
        if kind == "chieftain" and item_roll <= 45:
            item_id = "ironcap_buckler"
        elif kind == "archer" and item_roll <= 40:
            item_id = "short_bow"
        elif kind in {"raider", "horncaller", "reinforcement", "chieftain"} and item_roll <= 30:
            item_id = "rusty_knife"
        if "corpse_item" in unit:
            item_id = unit["corpse_item"] if item_roll <= unit["corpse_item_chance"] else None
        if gold:
            state["resources"]["gold"] = state["resources"].get("gold", 0) + gold
            result["rewards"]["gold"] = result["rewards"].get("gold", 0) + gold
        if item_id:
            state.setdefault("inventory", []).append({"instance_id": f"item_{uuid.uuid4().hex}", "item_id": item_id})
            result["rewards"].setdefault("items", []).append(item_id)
        entry = {"unit_id": unit_id, "name": unit["name"], "gold": gold, "item": item_id}
        corpse_loot.append(entry)
        result["rewards"].setdefault("loot_rolls", []).append({
            "source": f"{unit['name']} corpse", "roll": item_roll, "chance": unit.get("corpse_item_chance", 45 if kind == "chieftain" else 40 if kind == "archer" else 30),
            "item": item_id, "fallback_gold": gold,
        })
    temporary_ids = set(analysis.get("debug_temporary_character_ids", []))
    if temporary_ids:
        state["characters"] = [
            character for character in state.get("characters", [])
            if character.get("id") not in temporary_ids
        ]
    objectives = [objective["name"] for objective in battle.get("objectives", []) if objective.get("complete")]
    extracted = [unit["name"] for unit in battle.get("units", {}).values() if unit.get("extracted")]
    unconscious = [
        unit["name"] for unit in battle.get("units", {}).values()
        if unit.get("condition") == "unconscious" and not unit.get("extracted")
    ]
    corpses = [
        unit["name"] for unit in battle.get("units", {}).values()
        if unit.get("condition") == "dead" and not unit.get("extracted")
    ]
    outcome_details = _battle_outcome_details(battle)
    new_prisoners = _store_captured_prisoners(state, battle, mission)
    capture_rewards = _award_capture_loot(state, battle, result)
    if new_prisoners:
        result["rewards"]["prisoners"] = [
            {"id": prisoner["id"], "name": prisoner["name"], "race": prisoner["race"], "holding": prisoner["holding"]}
            for prisoner in new_prisoners
        ]
    result["battle_report"] = {
        "rounds": battle.get("round", 1), "actions": battle.get("action_count", 0),
        "objectives": objectives, "reinforcements_spawned": battle.get("reinforcements_spawned", False),
        "extracted": extracted, "unconscious": unconscious, "corpses": corpses,
        "captured": [
            unit["name"] for unit in battle.get("units", {}).values()
            if unit.get("team") == "enemy" and unit.get("condition") == "unconscious"
            and (unit.get("extracted") or unit["id"] in battle.get("auto_captured_ids", []))
        ],
        "rescued": [
            unit["name"] for unit in battle.get("units", {}).values()
            if unit.get("team") == "neutral" and unit.get("alive") and unit.get("extracted")
        ],
        "recovered_objects": [
            obj["name"] for obj in battle.get("objects", {}).values()
            if obj.get("objective_item") and obj.get("state") == "extracted"
        ],
        "corpse_loot": corpse_loot, "battlefield_secured": bool(battle.get("battlefield_secured")),
        "primary_target": outcome_details["primary_target"],
        "enemy_outcome": outcome_details["enemy_outcome"],
        "recap": outcome_details["recap"],
        "new_prisoners": [prisoner["name"] for prisoner in new_prisoners],
        "capture_rewards": capture_rewards,
        "log": list(battle.get("log", []))[-12:],
    }
    if outcome_details["aftermath"]:
        result["story"] = outcome_details["aftermath"]
    else:
        result["story"].extend(outcome_details["aftermath"])
    if analysis.get('scene'):
        result['scene_history']=analysis['scene']['history']
        result['story']=[entry['text'] for entry in analysis['scene']['history'] if entry.get('text')] + result['story']
    settle(state,analysis,tactical_outcome,battle)
    mission.analysis=analysis
    await _spawn_result_chains(session, mission, mission.claimed_by_user_id, result, now_ts())
    player.state = state; player.updated_at = now_ts()
    mission.result = result; mission.status = "completed"; mission.completes_at = now_ts(); mission.resolved_at = now_ts()
    await queue_result_notice(session,mission)
    await session.flush()
    return result


async def update_battle_instance(
    session: AsyncSession, guild_id: str, user_id: str, mission_id: str,
    command: dict | None = None, auto: str | None = None, resolve_all: bool = False,
) -> tuple[dict, dict | None]:
    # Combat deaths and hiring/recruitment modify the same persistent contacts.
    async with _player_locks.setdefault((guild_id,user_id),asyncio.Lock()):
        return await _update_battle_instance(session,guild_id,user_id,mission_id,command,auto,resolve_all)


async def _update_battle_instance(
    session: AsyncSession, guild_id: str, user_id: str, mission_id: str,
    command: dict | None = None, auto: str | None = None, resolve_all: bool = False,
) -> tuple[dict, dict | None]:
    mission = (await session.execute(
        select(MissionInstance).where(
            MissionInstance.id == mission_id, MissionInstance.guild_id == guild_id,
            MissionInstance.claimed_by_user_id == user_id,
        ).with_for_update()
    )).scalar_one_or_none()
    if not mission or mission.status != "battle":
        raise ValueError("Active battle not found")
    player = (await session.execute(
        select(PlayerState).where(
            PlayerState.guild_id == guild_id, PlayerState.user_id == user_id,
        ).with_for_update()
    )).scalar_one_or_none()
    if not player:
        raise ValueError("Player save not found")
    metadata = deepcopy(mission.analysis or {})
    battle = deepcopy(metadata.get("battle"))
    if not battle:
        raise ValueError("Battle state is missing")
    from .combat_supplies import sync_supplies
    sync_supplies(battle, player.state)
    supplies_before = set(battle.get('supplies_used', []))
    if resolve_all:
        view = auto_resolve(battle, auto or "balanced")
    elif auto:
        view = auto_step(battle, auto)
    elif command:
        view = apply_player_command(battle, command)
    else:
        view = battle_view(battle)
    spent = set(battle.get('supplies_used', [])) - supplies_before
    if spent:
        previous_state = deepcopy(player.state)
        changed_state = deepcopy(previous_state)
        changed_state['inventory'] = [i for i in changed_state['inventory'] if i['instance_id'] not in spent]
        changed = await session.execute(update(PlayerState).where(
            PlayerState.guild_id == guild_id, PlayerState.user_id == user_id,
            PlayerState.state == previous_state,
        ).values(state=changed_state).execution_options(synchronize_session=False))
        if changed.rowcount != 1:
            raise ValueError('Your inventory changed. Reopen the battle before using this supply.')
        player.state = changed_state
    from .mercenaries import settle
    contacts={o['id']:o for o in player.state.get('mercenaries',[])}
    needs_contact_update=any(u.get('mercenary_id') in contacts and
        (u.get('condition')=='dead' or (u.get('condition')=='unconscious' and contacts[u['mercenary_id']].get('recovering_until',0)<=now_ts()))
        for u in battle.get('units',{}).values())
    if needs_contact_update:
        changed_state=deepcopy(player.state)
        settle(changed_state,metadata,'failure',battle,final=False)
        player.state=changed_state
    metadata["battle"] = battle
    mission.analysis = metadata
    result = await _finish_battle(session, mission, player, battle) if battle.get("status") == "complete" else None
    if result and result.get('mercenary_interlude') and mission.status=='claimed':
        await resolve_due(session,guild_id,user_id)
        result['resume_status']=mission.status
        if mission.status=='completed':result['resumed_result']=mission.result
    await session.flush()
    return view, result


def _resolve_roll_stage(state: dict, mission: MissionInstance, party_ids: list[str], analysis: dict) -> tuple[dict, dict | None]:
    trial=deepcopy(state)
    template=MISSION_TEMPLATES[mission.template_id]
    result=resolve_mission(trial,template,party_ids,analysis,seed=mission.id)
    complication=template.get('critical_failure_encounter')
    if result['outcome']=='critical_failure' and complication:
        analysis['scene']={'history':[{'choice':'Expedition check','outcome':'critical_failure','die':result['die'],'total':result['total'],'difficulty':template['difficulty'],'text':complication['text']}],'bonus_keys':[],'revision':1}
        _start_scene_encounter(state,mission,analysis,complication)
        return state,None
    return trial,result


async def resolve_due(session: AsyncSession, guild_id: str | None = None, user_id: str | None = None) -> list[MissionInstance]:
    now = now_ts()
    due_query = select(MissionInstance.id).where(MissionInstance.status == "claimed", MissionInstance.completes_at <= now)
    if guild_id is not None:
        due_query = due_query.where(MissionInstance.guild_id == guild_id)
    if user_id is not None:
        due_query = due_query.where(MissionInstance.claimed_by_user_id == user_id)
    due_ids = (await session.execute(due_query.limit(50))).scalars().all()
    resolved: list[MissionInstance] = []
    for mission_id in due_ids:
        mission = (await session.execute(select(MissionInstance).where(MissionInstance.id == mission_id).with_for_update())).scalar_one_or_none()
        if not mission or mission.status != "claimed" or not mission.claimed_by_user_id:
            continue
        player = (await session.execute(
            select(PlayerState).where(PlayerState.guild_id == mission.guild_id, PlayerState.user_id == mission.claimed_by_user_id).with_for_update()
        )).scalar_one_or_none()
        if not player:
            mission.status = "error"
            mission.error_text = "Player save disappeared before resolution"
            continue
        try:
            state = normalize_state(deepcopy(player.state))
            analysis = dict(mission.analysis or {})
            mission_party_ids = list(analysis.get("mission_party_ids") or mission.party_ids or [])
            state,result = _resolve_roll_stage(state,mission,mission_party_ids,analysis)
            if result is None:
                player.state=state;player.updated_at=now
                continue
            set_party_status(state, list(analysis.get("bodyguard_ids", [])), "idle")
            from .mercenaries import settle
            settle(state,analysis,result["outcome"])
            await _spawn_result_chains(session, mission, mission.claimed_by_user_id, result, now)
            player.state = state
            player.updated_at = now
            mission.result = result
            mission.status = "completed"
            mission.resolved_at = now
            await queue_result_notice(session,mission)
            resolved.append(mission)
        except Exception as exc:  # keep scheduler alive and make failure visible
            mission.status = "error"
            mission.error_text = str(exc)[:1000]
    await session.flush()
    return resolved


async def debug_resolve_now_instance(
    session: AsyncSession, guild_id: str, user_id: str, mission_id: str,
) -> MissionInstance:
    mission = (await session.execute(
        select(MissionInstance).where(
            MissionInstance.id == mission_id,
            MissionInstance.guild_id == guild_id,
            MissionInstance.claimed_by_user_id == user_id,
        ).with_for_update()
    )).scalar_one_or_none()
    if not mission or mission.status != "claimed":
        raise ValueError("Only one of your active timed missions can be resolved immediately")
    player = (await session.execute(
        select(PlayerState).where(
            PlayerState.guild_id == guild_id, PlayerState.user_id == user_id,
        ).with_for_update()
    )).scalar_one_or_none()
    if not player:
        raise ValueError("Player save not found")
    state = normalize_state(deepcopy(player.state))
    analysis = dict(mission.analysis or {})
    party_ids = list(analysis.get("mission_party_ids") or mission.party_ids or [])
    state,result = _resolve_roll_stage(state,mission,party_ids,analysis)
    if result is None:
        player.state=state;player.updated_at=now_ts()
        await session.flush()
        return mission
    set_party_status(state, list(analysis.get("bodyguard_ids", [])), "idle")
    from .mercenaries import settle
    settle(state,analysis,result["outcome"])
    now = now_ts()
    await _spawn_result_chains(session, mission, user_id, result, now)
    player.state = state
    player.updated_at = now
    mission.result = result
    mission.status = "completed"
    mission.completes_at = now
    mission.resolved_at = now
    await queue_result_notice(session,mission)
    await session.flush()
    return mission


async def debug_complete_instance(
    session: AsyncSession, guild_id: str, user_id: str, mission_id: str,
    forced_outcome: str, requested_party_ids: list[str] | None = None,
    requested_role_assignments: dict[str, str] | None = None,
) -> MissionInstance:
    if forced_outcome not in {"critical_failure", "failure", "success", "critical_success"}:
        raise ValueError("Invalid debug outcome")
    mission = (await session.execute(
        select(MissionInstance).where(
            MissionInstance.id == mission_id,
            MissionInstance.guild_id == guild_id,
        ).with_for_update()
    )).scalar_one_or_none()
    if not mission:
        raise ValueError("Mission not found")
    _check_chain_owner(mission, user_id)
    completing_available = mission.status in {"available","reserved"} and mission.expires_at > now_ts()
    completing_owned = mission.status == "claimed" and mission.claimed_by_user_id == user_id
    if not completing_available and not completing_owned:
        raise ValueError("Mission is no longer available for debug completion")
    player = (await session.execute(
        select(PlayerState).where(
            PlayerState.guild_id == guild_id,
            PlayerState.user_id == user_id,
        ).with_for_update()
    )).scalar_one_or_none()
    if not player:
        raise ValueError("Player save not found")

    state = normalize_state(deepcopy(player.state))
    now = now_ts()
    if completing_available:
        chain_metadata = dict(mission.analysis or {})
        party_ids = list(requested_party_ids or [])
        if len(set(party_ids)) != len(party_ids):
            raise ValueError("A character can only be selected once")
        template = MISSION_TEMPLATES[mission.template_id]
        analysis = analyze_mission(state, template, party_ids, requested_role_assignments)
        for key in (
            "chain_owner_user_id", "chain_parent_id", "chain_id", "chain_step", "chain_total",
            "world_trigger_source_id", "world_trigger_source_name", "world_triggered_by_name",
        ):
            if key in chain_metadata:
                analysis[key] = chain_metadata[key]
        party_ids = list(analysis["party_ids"])
        if not analysis["availability_ok"]:
            raise ValueError("Selected characters must be idle")
        analysis["debug_requirement_bypass"] = True
        mission.status = "claimed"
        mission.claimed_by_user_id = user_id
        mission.claimed_by_name = player.display_name
        mission.claimed_at = now
        mission.completes_at = now
        mission.party_ids = party_ids
        mission.party_snapshot = snapshot_party(state, party_ids)
        mission.analysis = analysis
    else:
        party_ids = list(mission.party_ids or [])
        analysis = dict(mission.analysis or {})

    result = resolve_mission(
        state, MISSION_TEMPLATES[mission.template_id], party_ids,
        analysis, seed=f"{mission.id}:debug:{forced_outcome}", forced_outcome=forced_outcome,
    )
    from .mercenaries import settle
    settle(state,analysis,result["outcome"],analysis.get("battle"))
    await _spawn_result_chains(session, mission, user_id, result, now)
    player.state = state
    player.updated_at = now
    mission.result = result
    mission.status = "completed"
    mission.completes_at = now
    mission.resolved_at = now
    await queue_result_notice(session,mission)
    await session.flush()
    return mission
