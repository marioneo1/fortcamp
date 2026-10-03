from __future__ import annotations
import random
import time
import uuid
from urllib.parse import urlparse
from copy import deepcopy
from typing import Any

from .content import (
    ATTRIBUTE_NAMES, BUILDINGS, CELESTIALS, CHAMPIONS, EQUIPMENT_SLOTS, GENERIC_ARCHETYPES, GENERIC_FIRST_NAMES,
    GENERIC_LAST_NAMES, GENERAL_LOOT_TABLE, GENERAL_RECRUIT_TABLE, GUILD_HALL_UPGRADES, ITEMS, MISSION_EVENTS, MISSION_RANKS,
    MISSION_TEMPLATES, EVENT_REWARD_TABLES, RANK_REWARD_SCALING, PERK_LEVELS, PERK_TRACKS,
    PERK_TRAINING_ITEMS, RECRUIT_PROFILES, STANDALONE_PERKS, STAT_NAMES,
)
from .portraits import champion_portrait, choose_pool_portrait, portrait_pool_key, version_pool_url
from .portrait_framing import resolve_frame
from .appearance import has_appearance, sanitize_appearance, tagged_appearance
from .perk_effects import modifiers
from .mission_loot import roll_item_pool
from .economy import initialize as initialize_economy, settle as settle_economy, public_economy, earn_relationship, practice
from .races import RACE_CATALOG, RACE_FAMILIES, RACE_GAMEPLAY, REGIONAL_RECRUIT_TABLES, race_families, race_mission_bonus

from .outcome_balance import CRITICAL_SOFT_CAPS, CRITICAL_STAT_LIMITS, classify_roll, outcome_probabilities

from .relationships import ensure_character, record_mission, PERSONALITIES
from .prison_recruitment import initialize_prisoner, prisoner_interaction, credit_allegiance

GRID_W = 12
GRID_H = 8


def normalize_portrait_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if len(value) > 1000:
        raise ValueError("Portrait URL is too long")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Portrait URL must start with http:// or https://")
    return value


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def new_game(character: dict[str, Any]) -> dict[str, Any]:
    stats = {k: int(character.get("stats", {}).get(k, 2)) for k in STAT_NAMES}
    stats = {k: max(1, min(v, 10)) for k, v in stats.items()}
    attributes = {k: int(character.get("attributes", {}).get(k, 4)) for k in ATTRIBUTE_NAMES}
    attributes = {k: max(1, min(v, 10)) for k, v in attributes.items()}
    from .starter_equipment import STARTING_ROLES
    role_id = character.get('starting_role')
    if role_id is not None and role_id not in STARTING_ROLES:
        raise ValueError('Choose a valid starting role')
    role = STARTING_ROLES.get(role_id)
    traits = [role['perk']] if role else list(dict.fromkeys(character.get("traits", [])))[:4]
    perks = {track: "none" for track in PERK_TRACKS}
    for track, level in character.get("perks", {}).items():
        if track in perks and level in PERK_LEVELS:
            perks[track] = level

    if role:
        perks = {track: ('basic' if track == role['proficiency'] else 'none') for track in PERK_TRACKS}
    from .starter_equipment import starter_kit
    kit=role['kit'] if role else starter_kit(traits,perks)
    inventory = [
        {"instance_id": uid("item"), "item_id": kit[0]},
        {"instance_id": uid("item"), "item_id": "worn_jacket"},
        {"instance_id": uid("item"), "item_id": "work_boots"},
    ]
    equipment = {slot: None for slot in EQUIPMENT_SLOTS}
    equipment["weapon"] = inventory[0]["instance_id"]
    equipment["body"] = inventory[1]["instance_id"]
    equipment["feet"] = inventory[2]["instance_id"]
    for item_id in kit[1:]:
        item={'instance_id':uid('item'),'item_id':item_id};inventory.append(item)
        equipment[ITEMS[item_id]['slot']]=item['instance_id']

    return {
        "version": 9,
        "created_at": int(time.time()),
        "resources": {"gold": 0, "food": 5, "wood": 10, "scrap": 4, "stone": 8, "medicine": 0},
        "learned_blueprints": ["guild_hall", "training_ground", "prison_cell", "lumbermill", "quarry", "salvage_yard", "farm", "herb_garden", "kitchen", "workshop", "infirmary", "storage_shed"],
        "mission_rank": "E",
        "buildings": [
            {"id": "tent_1", "type": "tent", "x": 1, "y": 1, "assigned": []},
            {"id": "campfire_1", "type": "campfire", "x": 5, "y": 4, "assigned": []},
        ],
        "characters": [{
            "id": "player", "is_player": True, "source_kind": "player",
            "name": character.get("name", "Wanderer")[:32],
            "portrait": normalize_portrait_url(character.get("portrait", "")),
            "portrait_thumbnail": normalize_portrait_url(character.get("portrait", "")),
            "portrait_source": "override" if character.get("portrait") else "none",
            "race": character.get("race", "Human")[:32],
            "series": character.get("series", "Player")[:64] or "Player",
            "traits": traits,
            "specialty": role["name"] if role else character.get("specialty", "Survivor")[:32],
            "starting_role": role_id,
            "stats": stats,
            "perks": perks,
            "attributes": attributes,
            "equipment": equipment,
            "assignment": None, "status": "idle",
            "hp": 100, "max_hp": 100, "morale": 75,
        }],
        "inventory": inventory,
        "prisoners": [],
        "mission_history": [],
        "flags": {},
    }


def public_content() -> dict[str, Any]:
    from .inventory import sale_price
    from .starter_equipment import STARTING_ROLES
    return {
        "starting_roles": STARTING_ROLES,
        "economy": public_economy({}),
        "personalities": {key:{"name":value[0],"description":value[1]} for key,value in PERSONALITIES.items()},
        "buildings": BUILDINGS,
        "items": ITEMS,
        "sale_prices": {iid:sale_price(iid) for iid in ITEMS},
        "starter_kits": {"guard":["chipped_sword","splintered_shield"],"fire_magic":["cracked_wand"],"scout":["frayed_bow"],"engineer":["worn_mallet"],"medic":["knotted_staff"]},
        "slots": EQUIPMENT_SLOTS,
        "perk_tracks": PERK_TRACKS,
        "proficiency_tracks": PERK_TRACKS,
        "perk_levels": PERK_LEVELS,
        "perk_training_items": PERK_TRAINING_ITEMS,
        "standalone_perks": STANDALONE_PERKS,
        "attributes": ATTRIBUTE_NAMES,
        "mission_ranks": MISSION_RANKS,
        "guild_hall_upgrades": GUILD_HALL_UPGRADES,
        "mission_events": MISSION_EVENTS,
        "races": {
            race: {
                "rarity": details[0], "discovery": details[1],
                "family": (RACE_FAMILIES.get(race) or (None,))[0],
                "families": list(RACE_FAMILIES.get(race, ())),
                "gameplay": RACE_GAMEPLAY.get(race, RACE_GAMEPLAY["Human"]),
            }
            for race, details in RACE_CATALOG.items()
        },
        "champions": {
            champion_id: {
                "name": profile["name"], "series": profile["series"], "race": profile["race"],
                "specialty": profile["specialty"], "rank": profile.get("champion_rank", "A"),
            }
            for champion_id, profile in CHAMPIONS.items()
        },
        "celestials": {
            celestial_id: {
                "name": profile["name"], "pantheon": profile["pantheon"], "race": profile["race"],
                "specialty": profile["specialty"], "limited": True,
            }
            for celestial_id, profile in CELESTIALS.items()
        },
        "grid": {"w": GRID_W, "h": GRID_H},
    }


STOCKADE_LIMIT_SECONDS = 60 * 60


def prison_capacity(state: dict) -> int:
    return sum(
        int(BUILDINGS.get(building.get("type"), {}).get("cells", 0))
        for building in state.get("buildings", [])
    )


def prisoner_sale_value(prisoner: dict) -> int:
    value = 8
    if prisoner.get("kind") in {"archer", "horncaller", "reinforcement"}:
        value += 6
    if prisoner.get("boss") or prisoner.get("kind") == "chieftain":
        value += 32
    return value


def _enter_stockade(prisoner: dict, now: int) -> None:
    remaining = max(0, int(prisoner.get("stockade_remaining_seconds", STOCKADE_LIMIT_SECONDS)))
    prisoner["holding"] = "temporary_stockade"
    prisoner["stockade_remaining_seconds"] = remaining
    prisoner["stockade_expires_at"] = now + remaining


def _secure_prisoner(prisoner: dict, now: int) -> None:
    if prisoner.get("holding") == "temporary_stockade":
        prisoner["stockade_remaining_seconds"] = max(
            0, int(prisoner.get("stockade_expires_at", now)) - now,
        )
    prisoner["holding"] = "prison_cell"
    prisoner.pop("stockade_expires_at", None)


def _normalize_prisoners(state: dict, now: int | None = None) -> None:
    now = int(time.time()) if now is None else int(now)
    state.setdefault("prisoners", [])
    capacity = prison_capacity(state)
    secured = 0
    kept = []
    for prisoner in state["prisoners"]:
        prisoner.setdefault("status", "held")
        prisoner.setdefault("sale_value", prisoner_sale_value(prisoner))
        prisoner["sale_state"] = "available"
        if prisoner.get("holding") == "prison_cell" and secured < capacity:
            secured += 1
            prisoner.pop("stockade_expires_at", None)
            kept.append(prisoner)
            continue
        if prisoner.get("holding") != "temporary_stockade":
            _enter_stockade(prisoner, now)
        else:
            prisoner.setdefault("stockade_remaining_seconds", STOCKADE_LIMIT_SECONDS)
            prisoner.setdefault("stockade_expires_at", now + int(prisoner["stockade_remaining_seconds"]))
        if int(prisoner.get("stockade_expires_at", 0)) > now:
            kept.append(prisoner)
    state["prisoners"] = kept


def manage_prisoner(
    state: dict, prisoner_id: str, action: str,
    swap_prisoner_id: str | None = None, now: int | None = None,
) -> dict:
    now = int(time.time()) if now is None else int(now)
    _normalize_prisoners(state, now)
    prisoner = next((entry for entry in state["prisoners"] if entry.get("id") == prisoner_id), None)
    if not prisoner:
        raise ValueError("Prisoner not found or no longer in custody")
    if action == "sell":
        value = prisoner_sale_value(prisoner)
        state["resources"]["gold"] = int(state["resources"].get("gold", 0)) + value
        state["prisoners"].remove(prisoner)
        return {"action": "sold", "name": prisoner.get("name", "Prisoner"), "gold": value}
    if action == "stockade":
        if prisoner.get("holding") != "temporary_stockade":
            _enter_stockade(prisoner, now)
        return {"action": "stockade", "prisoner": prisoner}
    if action in {"talk", "negotiate", "fulfill", "recruit"}:
        return prisoner_interaction(state, prisoner, action, ITEMS, now)
    if action != "secure":
        raise ValueError("Unknown prisoner action")
    if prisoner.get("holding") == "prison_cell":
        return {"action": "secured", "prisoner": prisoner}
    capacity = prison_capacity(state)
    if capacity <= 0:
        raise ValueError("Build a Prison Cell before securing prisoners")
    secured = [entry for entry in state["prisoners"] if entry.get("holding") == "prison_cell"]
    displaced = None
    if len(secured) >= capacity:
        displaced = next((entry for entry in secured if entry.get("id") == swap_prisoner_id), None)
        if not displaced:
            raise ValueError("Choose a secured prisoner to move into the stockade")
        _enter_stockade(displaced, now)
    _secure_prisoner(prisoner, now)
    return {"action": "secured", "prisoner": prisoner, "displaced": displaced}


def normalize_state(state: dict) -> dict:
    state.setdefault("resources", {})
    initialize_economy(state)
    for resource in ("gold", "food", "wood", "scrap", "stone", "medicine"):
        state["resources"].setdefault(resource, 0)
    state.setdefault("learned_blueprints", [])
    for blueprint in ('lumbermill','quarry','salvage_yard','farm','herb_garden','kitchen','workshop','infirmary','storage_shed'):
        if blueprint not in state['learned_blueprints']:state['learned_blueprints'].append(blueprint)
    if "guild_hall" not in state["learned_blueprints"]:
        state["learned_blueprints"].append("guild_hall")
    if "training_ground" not in state["learned_blueprints"]:
        state["learned_blueprints"].append("training_ground")
    if "prison_cell" not in state["learned_blueprints"]:
        state["learned_blueprints"].append("prison_cell")
    _normalize_prisoners(state)
    for prisoner in state.get('prisoners',[]):
        initialize_prisoner(prisoner, MISSION_TEMPLATES.get(prisoner.get('captured_from_template'),{}).get('rank','E'))
    if state.get("mission_rank") not in MISSION_RANKS:
        has_hall = any(building.get("type") == "guild_hall" for building in state.get("buildings", []))
        state["mission_rank"] = "D" if has_hall else "E"
    race_migrations = {
        "Ashborn": "Undead", "Dhampir": "Vampire", "Graveborn": "Undead",
        "Cometkin": "Alien", "Voidborn": "Voidsent", "Starforged": "Automaton",
        "Celestine": "Aasimar",
    }
    profile_migrations = {
        "ashborn": "undead", "dhampir": "vampire", "graveborn": "undead",
        "cometkin": "alien", "voidborn": "voidsent", "starforged": "automaton",
        "celestine": "aasimar",
    }
    trait_migrations = {
        "ash_body": "deathless", "living_constellation": "radiant_soul",
    }
    for char in state.get("characters", []):
        if char.get("race") == "Beastkin":
            beast_profiles = ("catfolk", "faun", "foxkin", "lizardfolk", "harpy")
            selected = beast_profiles[sum(ord(ch) for ch in char.get("id", "")) % len(beast_profiles)]
            char["race"] = RECRUIT_PROFILES[selected]["race"]
            if char.get("generation_profile") == "beastkin":
                char["generation_profile"] = selected
        char["race"] = race_migrations.get(char.get("race"), char.get("race", "Human"))
        if char.get("generation_profile") in profile_migrations:
            char["generation_profile"] = profile_migrations[char["generation_profile"]]
        char["traits"] = list(dict.fromkeys(trait_migrations.get(trait, trait) for trait in char.get("traits", [])))
        if char.get("status") == "incapacitated" and int(char.get("recovers_at", 0)) <= int(time.time()):
            char["status"] = "idle"
            char["hp"] = max(1, int(char.get("max_hp", 100)) // 2)
            char.pop("recovers_at", None)
            char.pop("recovery_location", None)
        ensure_character(char)
        char.setdefault("attributes", {attribute: 5 for attribute in ATTRIBUTE_NAMES})
        char.setdefault("portrait_thumbnail", char.get("portrait", ""))
        char.setdefault("portrait_source", "override" if char.get("portrait") else "none")
        if char.get("portrait_source") == "pool" and char.get("portrait"):
            char["portrait_locked"] = True
        if char.get("source_kind") == "champion" and char.get("source_id") in CHAMPIONS and char.get("portrait_source") != "override":
            authored = CHAMPIONS[char["source_id"]].get("portrait", "")
            if not authored:
                resolved_portrait = champion_portrait(char["source_id"], char.get("portrait_variant", "default"))
                if resolved_portrait["portrait"]:
                    char.update(resolved_portrait)
                    char["portrait_source"] = "champion"
                    char["portrait_locked"] = True
        if char.get("source_kind") == "generic":
            char.setdefault("gender", "female" if sum(ord(ch) for ch in char.get("id", "")) % 2 else "male")
            specialty_to_archetype = {"fighter": "fighter", "scout": "scout", "builder": "builder", "medic": "medic", "adept": "adept"}
            char.setdefault("archetype_id", specialty_to_archetype.get(str(char.get("specialty", "")).lower(), "fighter"))
            expected_pool = portrait_pool_key(
                char.get("race", "Human"), char["gender"], char["archetype_id"],
                "boss" in char.get("traits", []) or "elite" in char.get("traits", []),
            )
            if str(char.get("race", "")).lower() == "werewolf":
                char["portrait_pool"] = expected_pool
            else:
                char.setdefault("portrait_pool", expected_pool)
            if not char.get("portrait") and char.get("portrait_source") == "none":
                portrait = choose_pool_portrait(
                    char["portrait_pool"], random.Random(f"portrait:{char.get('id', '')}:{char['portrait_pool']}"),
                )
                if portrait["portrait"]:
                    char.update(portrait)
                    char["portrait_source"] = "pool"
                    char["portrait_locked"] = True
        for field in ('portrait','portrait_full','portrait_thumbnail'):
            if char.get(field):char[field] = version_pool_url(char[field])
        char['portrait_frame'] = resolve_frame(char)
        char['portrait_frame_default'] = resolve_frame({'portrait':char.get('portrait_full') or char.get('portrait')})
        char["appearance"] = sanitize_appearance(char.get("appearance", {}))
        char.setdefault("appearance_source", "manual" if has_appearance(char["appearance"]) else "none")
        tagged = tagged_appearance(char)
        char["portrait_metadata_available"] = has_appearance(tagged)
        if char["appearance_source"] != "manual" and has_appearance(tagged):
            char["appearance"] = tagged
            char["appearance_source"] = "portrait"
        if "perks" not in char:
            legacy = char.get("stats", {})
            perks = {}
            for track in PERK_TRACKS:
                value = int(legacy.get("cooking" if track == "alchemy" else track, 1))
                perks[track] = "master" if value >= 9 else "expert" if value >= 7 else "skilled" if value >= 5 else "basic" if value >= 3 else "none"
            char["perks"] = perks
        else:
            for track in PERK_TRACKS:
                if char["perks"].get(track) not in PERK_LEVELS:
                    char["perks"][track] = "none"
    settle_economy(state)
    state["version"] = max(10, int(state.get("version", 1)))
    return state


def mission_rank(state: dict) -> str:
    return normalize_state(state).get("mission_rank", "E")


def mission_rank_unlocked(state: dict, rank: str) -> bool:
    if rank not in MISSION_RANKS:
        return False
    return MISSION_RANKS.index(rank) <= MISSION_RANKS.index(mission_rank(state))


def upgrade_guild_hall(state: dict) -> str:
    normalize_state(state)
    if not any(building.get("type") == "guild_hall" for building in state.get("buildings", [])):
        raise ValueError("Build the Guild Hall before upgrading mission visibility")
    current = mission_rank(state)
    if current == "E":
        state["mission_rank"] = "D"
        return "D"
    upgrade_order = {"D": "C", "C": "B", "B": "A", "A": "S"}
    target = upgrade_order.get(current)
    if not target:
        raise ValueError("Guild Hall mission visibility is already S-Rank")
    cost = GUILD_HALL_UPGRADES[target]
    for resource, amount in cost.items():
        if state["resources"].get(resource, 0) < amount:
            raise ValueError(f"Not enough {resource} for the {target}-Rank Guild Hall upgrade")
    for resource, amount in cost.items():
        state["resources"][resource] -= amount
    state["mission_rank"] = target
    return target


def find_char(state: dict, char_id: str) -> dict:
    for c in state.get("characters", []):
        if c["id"] == char_id:
            return c
    raise ValueError("Character not found")


def _inventory_index(state: dict) -> dict[str, dict]:
    return {i["instance_id"]: i for i in state.get("inventory", [])}


def equipped_item_defs(state: dict, char: dict) -> list[dict]:
    inv = _inventory_index(state)
    defs: list[dict] = []
    for instance_id in char.get("equipment", {}).values():
        inst = inv.get(instance_id)
        if inst and inst.get("item_id") in ITEMS:
            defs.append(ITEMS[inst["item_id"]] | {"item_id": inst["item_id"]})
    return defs


def active_traits(state: dict, char: dict) -> set[str]:
    traits = set(char.get("traits", []))
    for item in equipped_item_defs(state, char):
        traits.update(item.get("granted_perks", []))
    return traits


def perk_level(char: dict, track: str) -> str:
    if track == "cooking":
        track = "alchemy"
    level = char.get("perks", {}).get(track, "none")
    return level if level in PERK_LEVELS else "none"


def perk_rank(char: dict, track: str) -> int:
    return PERK_LEVELS.index(perk_level(char, track))


def effective_stat(state: dict, char: dict, stat: str) -> int:
    """Compatibility name for a capability check; old numeric skills no longer contribute."""
    track = "alchemy" if stat == "cooking" else stat
    definition = PERK_TRACKS.get(track, PERK_TRACKS["survival"])
    attributes = [int(char.get("attributes", {}).get(name, 5)) for name in definition["attributes"]]
    total = sum(attributes) // max(1, len(attributes)) + perk_rank(char, track)
    for item in equipped_item_defs(state, char):
        total += int(item.get("bonuses", {}).get(stat, item.get("bonuses", {}).get(track, 0)))
    return total + modifiers(state,char,ITEMS,'capabilities').get(track,0) + (1 if track=='survival' and char.get('prepared_meal')=='trail_meal' else 0)


def effective_attribute(state: dict, char: dict, attribute: str) -> int:
    # Characters saved before physical attributes were added receive a neutral baseline.
    total = int(char.get("attributes", {}).get(attribute, 5))
    for item in equipped_item_defs(state, char):
        total += int(item.get("attribute_bonuses", {}).get(attribute, 0))
    for track, definition in PERK_TRACKS.items():
        if definition.get("attribute_bonus") == attribute:
            total += 1 if perk_rank(char, track) >= 1 else 0
    return total + modifiers(state,char,ITEMS,'attributes').get(attribute,0)


def equipped_weapon_def(state: dict, char: dict) -> dict | None:
    weapon_id = char.get("equipment", {}).get("weapon")
    item = _inventory_index(state).get(weapon_id)
    if not item or item.get("item_id") not in ITEMS:
        return None
    definition = ITEMS[item["item_id"]]
    return definition | {"item_id": item["item_id"]}


def combat_metrics(state: dict, char: dict) -> dict:
    weapon = equipped_weapon_def(state, char)
    scaling = (weapon or {}).get("weapon_scaling", "str")
    dps = effective_attribute(state, char, scaling) + int((weapon or {}).get("power", 0)) + effective_stat(state, char, "combat") // 2
    if weapon and weapon.get("capture_weapon"):
        dps = 0
    return {
        "constitution": effective_attribute(state, char, "vit"),
        "dps": dps,
        "dps_attribute": scaling,
        "weapon": (weapon or {}).get("name", "Unarmed"),
    }


def building_types(state: dict) -> set[str]:
    return {b["type"] for b in state.get("buildings", [])}


def _compare(value: int | float, op: str, target: int | float) -> bool:
    return {
        ">=": value >= target, ">": value > target,
        "<=": value <= target, "<": value < target,
        "==": value == target,
    }.get(op, False)


def character_condition_met(state: dict, char: dict, cond: dict) -> bool:
    kind = cond.get("kind")
    if kind == "all":
        return all(character_condition_met(state, char, nested) for nested in cond.get("conditions", []))
    if kind == "any":
        return any(character_condition_met(state, char, nested) for nested in cond.get("conditions", []))
    if kind == "trait":
        return cond["value"] in active_traits(state, char)
    if kind == "race":
        return char.get("race", "").lower() == cond["value"].lower()
    if kind == "race_family":
        requested = cond["value"].lower()
        return any(family.lower() == requested for family in race_families(char.get("race", "")))
    if kind == "series":
        return char.get("series", "").lower() == cond["value"].lower()
    if kind == "character":
        return char.get("source_id") == cond["value"] or char.get("id") == cond["value"]
    if kind == "source_kind":
        return char.get("source_kind") == cond["value"]
    if kind == "stat":
        return _compare(effective_stat(state, char, cond["stat"]), cond.get("op", ">="), int(cond["value"]))
    if kind == "perk":
        return perk_rank(char, cond["track"]) >= PERK_LEVELS.index(cond.get("level", "basic"))
    if kind == "attribute":
        return _compare(effective_attribute(state, char, cond["attribute"]), cond.get("op", ">="), int(cond["value"]))
    if kind == "equipped_slot":
        return bool(char.get("equipment", {}).get(cond["slot"]))
    if kind in {"item_tag", "weapon_type", "item_id"}:
        for item in equipped_item_defs(state, char):
            if kind == "item_tag" and cond["value"] in item.get("tags", []):
                return True
            if kind == "weapon_type" and item.get("weapon_type") == cond["value"]:
                return True
            if kind == "item_id" and item.get("item_id") == cond["value"]:
                return True
        return False
    return False


def condition_met(state: dict, party: list[dict], cond: dict) -> bool:
    kind = cond.get("kind")
    if kind == "building":
        return cond["value"] in building_types(state)
    if kind == "world_flag":
        return bool(state.get("flags", {}).get(cond["value"]))
    if kind == "count":
        nested = cond.get("condition", {})
        return sum(1 for c in party if character_condition_met(state, c, nested)) >= int(cond.get("min", 1))
    return any(character_condition_met(state, c, cond) for c in party)


def claim_requirements(state: dict, mission: dict, party: list[dict]) -> list[dict]:
    results = []
    for req in mission.get("claim_requirements", []):
        met = condition_met(state, party, req)
        results.append({"label": req.get("label", "Requirement"), "met": met})
    return results


def eligible_secret_events(state: dict, mission: dict, party: list[dict]) -> list[dict]:
    """Return matched definitions without ever exposing their conditions publicly."""
    return [
        event for event in mission.get("secret_events", [])
        if all(condition_met(state, party, condition) for condition in event.get("conditions", []))
    ]


def analyze_mission(
    state: dict, mission: dict, party_ids: list[str], role_assignments: dict[str, str] | None = None,
    bodyguard_ids: list[str] | None = None,
) -> dict:
    role_defs = list(mission.get("roles", []))
    assignments = dict(role_assignments or {})
    role_assignments_ok = True
    if role_defs:
        expected_role_ids = [role["id"] for role in role_defs]
        role_assignments_ok = (
            set(assignments) == set(expected_role_ids)
            and all(assignments.get(role_id) for role_id in expected_role_ids)
            and len(set(assignments.values())) == len(expected_role_ids)
        )
        party_ids = [assignments[role_id] for role_id in expected_role_ids if assignments.get(role_id)]
    party = [find_char(state, cid) for cid in party_ids]
    bodyguard_ids = list(bodyguard_ids or [])
    bodyguards = [find_char(state, cid) for cid in bodyguard_ids]
    bodyguard_slots = int(mission.get("bodyguard_slots", 0))
    bodyguards_ok = (
        len(bodyguard_ids) <= bodyguard_slots
        and len(set(bodyguard_ids)) == len(bodyguard_ids)
        and not set(bodyguard_ids).intersection(party_ids)
        and all(character.get("status") == "idle" for character in bodyguards)
    )
    required_size = int(mission["party_size"])
    party_size_ok = len(party) == required_size and len(set(party_ids)) == len(party_ids) and role_assignments_ok
    availability_ok = all(c.get("status") == "idle" for c in party)
    reqs = claim_requirements(state, mission, party)

    stat = mission["stat"]
    if party:
        lead = max(party, key=lambda c: effective_stat(state, c, stat))
        lead_stat = effective_stat(state, lead, stat)
        support_bonus = min(2, sum(1 for c in party if c["id"] != lead["id"] and effective_stat(state, c, stat) >= 5))
    else:
        lead = None
        lead_stat = 0
        support_bonus = 0

    mercenary_count = sum(bool(c.get('temporary_mercenary')) for c in party + bodyguards)
    criteria_bonus = -min(4, mercenary_count)
    triggered = ([{'label':'Hired party coordination', 'bonus':criteria_bonus}] if mercenary_count else [])

    racial_bonus = 0
    if lead:
        racial_bonus = max(0, min(3, race_mission_bonus(lead.get("race", "Human"), stat, mission.get("mission_form", "operation"))))
        if racial_bonus:
            criteria_bonus += racial_bonus
            triggered.append({
                "label": f"{lead.get('race', 'Unknown')} aptitude",
                "bonus": racial_bonus,
            })

    role_evaluations = []
    role_bonus = 0
    party_by_id = {char["id"]: char for char in party}
    for role in role_defs:
        character_id = assignments.get(role["id"])
        char = party_by_id.get(character_id)
        metric = role.get("metric", "dps")
        metrics = combat_metrics(state, char) if char else {}
        score = int(metrics.get(metric, 0))
        recommended = int(role.get("recommended", 0))
        meets_recommendation = bool(char and score >= recommended)
        contribution = 2 if meets_recommendation else (-1 if char else 0)
        role_bonus += contribution
        evaluation = {
            "id": role["id"], "label": role.get("label", role["id"].title()),
            "character_id": character_id, "character": char.get("name") if char else None,
            "metric": metric, "score": score, "recommended": recommended,
            "meets_recommendation": meets_recommendation, "contribution": contribution,
            "dps_attribute": metrics.get("dps_attribute"), "weapon": metrics.get("weapon"),
        }
        role_evaluations.append(evaluation)
        if meets_recommendation:
            label = f"{evaluation['label']} meets recommended {metric.upper()}"
            triggered.append({"label": label, "bonus": contribution})
    criteria_bonus += role_bonus

    for mod in mission.get("modifiers", []):
        if condition_met(state, party, mod):
            bonus = int(mod.get("bonus", 0))
            criteria_bonus += bonus
            triggered.append({"label": mod.get("label", "Special condition"), "bonus": bonus})

    critical_unlock_labels: list[str] = []
    for cond in mission.get("critical_any", []):
        if condition_met(state, party, cond):
            critical_unlock_labels.append(cond.get("label", "Critical criterion"))

    critical_success_available = not mission.get("critical_any") or bool(critical_unlock_labels)
    secret_event_ids = [event["id"] for event in eligible_secret_events(state, mission, party)]
    crit_threshold = int(mission["difficulty"]) + 8  # Legacy display field, not an automatic critical trigger.
    probabilities = outcome_probabilities(
        lead_stat + support_bonus + criteria_bonus, int(mission["difficulty"]),
        mission.get("rank", "E"), critical_success_available,
    )
    return {
        "party_size_ok": party_size_ok,
        "availability_ok": availability_ok,
        "requirements": reqs,
        "claimable": party_size_ok and availability_ok and bodyguards_ok and all(x["met"] for x in reqs),
        "party_ids": list(party_ids), "role_assignments": assignments,
        "mission_party_ids": list(party_ids), "bodyguard_ids": bodyguard_ids,
        "bodyguards_ok": bodyguards_ok, "bodyguard_slots": bodyguard_slots,
        "bodyguards": [{"id": character["id"], "name": character["name"]} for character in bodyguards],
        "role_assignments_ok": role_assignments_ok, "roles": role_evaluations,
        "lead": lead["name"] if lead else None,
        "lead_id": lead["id"] if lead else None,
        "lead_stat": lead_stat,
        "stat": stat,
        "support_bonus": support_bonus,
        "criteria_bonus": criteria_bonus, "role_bonus": role_bonus, "racial_bonus": racial_bonus,
        "triggered": triggered,
        "critical_unlocks": critical_unlock_labels,
        "critical_success_available": critical_success_available,
        "secret_event_possible": bool(secret_event_ids),
        "eligible_secret_event_ids": secret_event_ids,
        "critical_threshold": crit_threshold,
        "critical_soft_cap": CRITICAL_SOFT_CAPS.get(mission.get("rank", "E"), 20),
        "critical_stat_limit": CRITICAL_STAT_LIMITS.get(mission.get("rank", "E"), 100),
        "probabilities": probabilities,
    }


def snapshot_party(state: dict, party_ids: list[str]) -> list[dict]:
    return deepcopy([find_char(state, cid) for cid in party_ids])


def set_party_status(state: dict, party_ids: list[str], status: str) -> None:
    for cid in party_ids:
        find_char(state, cid)["status"] = status


def _award_item(state: dict, item_id: str, awarded: dict) -> None:
    if item_id in ITEMS:
        state["inventory"].append({"instance_id": uid("item"), "item_id": item_id})
        awarded["items"].append(item_id)


def _make_generic(archetype_id: str, rng: random.Random) -> dict:
    archetype = GENERIC_ARCHETYPES[archetype_id]
    name = f"{rng.choice(GENERIC_FIRST_NAMES)} {rng.choice(GENERIC_LAST_NAMES)}"
    stats = deepcopy(archetype["stats"])
    attributes = deepcopy(archetype.get("attributes", {}))
    # Small variation while keeping the archetype recognizable.
    varied = rng.choice(list(stats))
    stats[varied] = max(1, min(10, stats[varied] + rng.choice([-1, 1])))
    gender = rng.choice(["male", "female"])
    portrait = choose_pool_portrait(portrait_pool_key("Human", gender, archetype_id), rng)
    return {
        "id": uid("char"), "source_id": f"generic:{archetype_id}:{uuid.uuid4().hex[:6]}",
        "source_kind": "generic", "is_player": False, "name": name,
        "race": "Human", "gender": gender, "series": "Original", "traits": list(archetype["traits"]),
        "stats": stats, "attributes": attributes, "specialty": archetype["specialty"],
        **portrait, "portrait_source": "pool" if portrait["portrait"] else "none", "portrait_locked": bool(portrait["portrait"]), "archetype_id": archetype_id,
        "equipment": {slot: None for slot in EQUIPMENT_SLOTS}, "assignment": None,
        "status": "idle", "hp": 100, "max_hp": 100, "morale": 70,
    }


def _make_procedural(profile_id: str, rng: random.Random) -> dict:
    profile = RECRUIT_PROFILES[profile_id]
    archetype_id = rng.choice(profile.get("archetypes") or list(GENERIC_ARCHETYPES))
    archetype = GENERIC_ARCHETYPES[archetype_id]
    first_names = profile.get("first_names") or GENERIC_FIRST_NAMES
    last_names = profile.get("last_names") or GENERIC_LAST_NAMES
    name = f"{rng.choice(first_names)} {rng.choice(last_names)}"
    stats = deepcopy(archetype["stats"])
    attributes = deepcopy(archetype.get("attributes", {}))
    for attribute, bonus in profile.get("attribute_bonuses", {}).items():
        if attribute in attributes:
            attributes[attribute] = max(1, min(12, int(attributes[attribute]) + int(bonus)))
    # Two small variations make generated people less clone-like without creating wild stat spikes.
    for varied in rng.sample(list(stats), k=min(2, len(stats))):
        stats[varied] = max(1, min(10, stats[varied] + rng.choice([-1, 1])))
    traits = list(dict.fromkeys(list(archetype.get("traits", [])) + list(profile.get("extra_traits", []))))
    gender = rng.choice(profile.get("genders", ["male", "female"]))
    special = profile.get("portrait_tier") == "special"
    portrait = choose_pool_portrait(portrait_pool_key(profile.get("race", "Human"), gender, archetype_id, special), rng)
    return {
        "id": uid("char"), "source_id": f"generated:{profile_id}:{uuid.uuid4().hex[:6]}",
        "source_kind": "generic", "generation_profile": profile_id, "is_player": False,
        "name": name, "race": profile.get("race", "Human"), "gender": gender, "series": profile.get("series", "Original"),
        "traits": traits, "stats": stats, "attributes": attributes, "specialty": archetype["specialty"],
        **portrait, "portrait_source": "pool" if portrait["portrait"] else "none", "portrait_locked": bool(portrait["portrait"]), "archetype_id": archetype_id,
        "equipment": {slot: None for slot in EQUIPMENT_SLOTS}, "assignment": None,
        "status": "idle", "hp": 100, "max_hp": 100, "morale": 70,
    }


def _weighted_profile(choice_data: Any, rng: random.Random) -> str | None:
    if isinstance(choice_data, str):
        return choice_data if choice_data in RECRUIT_PROFILES else None
    if isinstance(choice_data, dict):
        choice_data = [choice_data]
    if not isinstance(choice_data, list):
        return None
    valid = [x for x in choice_data if isinstance(x, dict) and x.get("profile") in RECRUIT_PROFILES]
    if not valid:
        return None
    total = sum(max(0.0, float(x.get("weight", 1))) for x in valid)
    if total <= 0:
        return valid[0]["profile"]
    point = rng.random() * total
    cursor = 0.0
    for item in valid:
        cursor += max(0.0, float(item.get("weight", 1)))
        if point <= cursor:
            return item["profile"]
    return valid[-1]["profile"]


def _weighted_event_profile(choice_data: list[tuple[str, str, int]], rank: str, rng: random.Random) -> str | None:
    rank_index = MISSION_RANKS.index(rank) if rank in MISSION_RANKS else 0
    eligible = [(profile, weight) for profile, minimum_rank, weight in choice_data if MISSION_RANKS.index(minimum_rank) <= rank_index and profile in RECRUIT_PROFILES]
    if not eligible:
        return None
    total = sum(weight for _, weight in eligible)
    point = rng.uniform(0, total)
    cursor = 0.0
    for profile, weight in eligible:
        cursor += weight
        if point <= cursor:
            return profile
    return eligible[-1][0]


def _make_champion(champion_id: str) -> dict:
    source = deepcopy(CHAMPIONS[champion_id])
    source["perks"] = {}
    for track in PERK_TRACKS:
        value = int(source.get("stats", {}).get("cooking" if track == "alchemy" else track, 1))
        source["perks"][track] = "master" if value >= 9 else "expert" if value >= 7 else "skilled" if value >= 5 else "basic" if value >= 3 else "none"
    authored_portrait = source.get("portrait", "")
    resolved_portrait = champion_portrait(champion_id) if not authored_portrait else {
        "portrait": authored_portrait, "portrait_thumbnail": authored_portrait, "portrait_variant": "default",
    }
    source.update({
        "id": uid("char"), "source_id": champion_id, "is_player": False,
        **resolved_portrait,
        "portrait_source": "authored" if authored_portrait else "champion" if resolved_portrait["portrait"] else "none",
        "portrait_locked": bool(resolved_portrait["portrait"]),
        "equipment": {slot: None for slot in EQUIPMENT_SLOTS}, "assignment": None,
        "status": "idle", "hp": 100, "max_hp": 100, "morale": 75,
    })
    return source


def _make_celestial(celestial_id: str) -> dict:
    source = deepcopy(CELESTIALS[celestial_id])
    source["perks"] = {}
    for track in PERK_TRACKS:
        value = int(source.get("stats", {}).get("cooking" if track == "alchemy" else track, 1))
        source["perks"][track] = "master" if value >= 9 else "expert" if value >= 7 else "skilled" if value >= 5 else "basic" if value >= 3 else "none"
    source.update({
        "id": uid("char"), "source_id": f"celestial:{celestial_id}", "is_player": False,
        "portrait_thumbnail": source.get("portrait", ""), "portrait_source": "authored" if source.get("portrait") else "none",
        "equipment": {slot: None for slot in EQUIPMENT_SLOTS}, "assignment": None,
        "status": "idle", "hp": 100, "max_hp": 100, "morale": 80,
    })
    return source


def _weighted_champion(choice_data: Any, state: dict, rng: random.Random) -> str | None:
    if not isinstance(choice_data, list):
        return None
    owned = {char.get("source_id") for char in state.get("characters", [])}
    valid = [item for item in choice_data if isinstance(item, dict) and item.get("champion") in CHAMPIONS and item.get("champion") not in owned]
    if not valid:
        return None
    total = sum(max(0.0, float(item.get("weight", 1))) for item in valid)
    if total <= 0:
        return valid[0]["champion"]
    point = rng.random() * total
    cursor = 0.0
    for item in valid:
        cursor += max(0.0, float(item.get("weight", 1)))
        if point <= cursor:
            return item["champion"]
    return valid[-1]["champion"]


def _random_champion(state: dict, rank: str, rng: random.Random) -> str | None:
    owned = {char.get("source_id") for char in state.get("characters", [])}
    rank_index = MISSION_RANKS.index(rank) if rank in MISSION_RANKS else 0
    valid = [
        (champion_id, {"C": 10, "B": 7, "A": 4, "S": 2}.get(profile.get("champion_rank", "A"), 4))
        for champion_id, profile in CHAMPIONS.items()
        if champion_id not in owned and MISSION_RANKS.index(profile.get("champion_rank", "A")) <= rank_index
    ]
    if not valid:
        return None
    total = sum(weight for _, weight in valid)
    point = rng.uniform(0, total)
    cursor = 0.0
    for champion_id, weight in valid:
        cursor += weight
        if point <= cursor:
            return champion_id
    return valid[-1][0]


def _award_reward_block(state: dict, block: dict, awarded: dict, rng: random.Random, target_character_id: str | None = None) -> None:
    for resource, amount in block.get("materials", {}).items():
        resource = "stone" if resource == "cloth" else resource
        state["resources"][resource] = state["resources"].get(resource, 0) + int(amount)
        awarded["materials"][resource] = awarded["materials"].get(resource, 0) + int(amount)

    blueprint = block.get("blueprint")
    if blueprint and blueprint not in state["learned_blueprints"]:
        state["learned_blueprints"].append(blueprint)
        awarded["blueprints"].append(blueprint)

    if block.get("item"):
        _award_item(state, block["item"], awarded)
    for item_id in block.get("items", []):
        _award_item(state, item_id, awarded)
    for item_id in block.get("guaranteed_items", []):
        _award_item(state, item_id, awarded)

    world_flag = block.get("world_flag")
    if isinstance(world_flag, dict) and world_flag.get("id"):
        flag_id = str(world_flag["id"])
        first_unlock = not state.setdefault("flags", {}).get(flag_id)
        state["flags"][flag_id] = True
        if first_unlock:
            awarded["world_flags"].append({"id": flag_id, "name": world_flag.get("name", flag_id)})

    generic_id = block.get("generic_recruit")
    if generic_id in GENERIC_ARCHETYPES:
        recruit = _make_generic(generic_id, rng)
        state["characters"].append(recruit)
        awarded["recruits"].append({"name": recruit["name"], "kind": "generic", "race": recruit["race"], "profile": f"archetype:{generic_id}"})

    profile_id = _weighted_profile(block.get("procedural_recruit"), rng)
    if profile_id:
        recruit = _make_procedural(profile_id, rng)
        state["characters"].append(recruit)
        awarded["recruits"].append({"name": recruit["name"], "kind": "generic", "race": recruit["race"], "profile": profile_id})

    champion_id = block.get("champion") or _weighted_champion(block.get("champion_pool"), state, rng)
    if champion_id in CHAMPIONS and not any(c.get("source_id") == champion_id for c in state["characters"]):
        recruit = _make_champion(champion_id)
        state["characters"].append(recruit)
        awarded["recruits"].append({"name": recruit["name"], "kind": "champion", "race": recruit.get("race", ""), "profile": champion_id})

    celestial_id = block.get("celestial")
    celestial_source_id = f"celestial:{celestial_id}"
    if celestial_id in CELESTIALS and not any(c.get("source_id") == celestial_source_id for c in state["characters"]):
        recruit = _make_celestial(celestial_id)
        state["characters"].append(recruit)
        awarded["recruits"].append({
            "name": recruit["name"], "kind": "celestial", "race": "Celestial", "profile": celestial_id,
        })

    target = next((char for char in state.get("characters", []) if char.get("id") == target_character_id), None)
    perk_reward = block.get("perk")
    if target and isinstance(perk_reward, dict) and perk_reward.get("track") in PERK_TRACKS and perk_reward.get("level") in PERK_LEVELS:
        track, level = perk_reward["track"], perk_reward["level"]
        if perk_rank(target, track) < PERK_LEVELS.index(level):
            target.setdefault("perks", {})[track] = level
            awarded["perks"].append({"character": target["name"], "track": track, "level": level})
    standalone = block.get("standalone_perk")
    if target and standalone and standalone not in target.setdefault("traits", []):
        target["traits"].append(str(standalone))
        awarded["perks"].append({"character": target["name"], "standalone": str(standalone)})
    transform = block.get("transform")
    if target and isinstance(transform, dict) and transform.get("race"):
        old_race = target.get("race", "Unknown")
        target["race"] = str(transform["race"])[:32]
        for standalone in transform.get("standalone_perks", []):
            if standalone not in target.setdefault("traits", []):
                target["traits"].append(standalone)
        if target.get("portrait_source") in {"pool", "none"}:
            replacement = choose_pool_portrait(
                portrait_pool_key(target["race"], target.get("gender", "male"), target.get("archetype_id", "fighter"), True), rng,
            )
            target.update(replacement)
            target["portrait_source"] = "pool" if replacement["portrait"] else "none"
            target["portrait_locked"] = bool(replacement["portrait"])
        awarded["transformations"].append({"character": target["name"], "from": old_race, "to": target["race"]})


def _add_gold(state: dict, awarded: dict, amount: int) -> None:
    amount = max(0, int(amount))
    if not amount:
        return
    state["resources"]["gold"] = state["resources"].get("gold", 0) + amount
    awarded["gold"] = awarded.get("gold", 0) + amount


def _weighted_loot(table: list[tuple[str, str, int]], rank: str, rng: random.Random) -> str | None:
    rank_index = MISSION_RANKS.index(rank) if rank in MISSION_RANKS else 0
    eligible = [(item_id, weight) for item_id, minimum_rank, weight in table if MISSION_RANKS.index(minimum_rank) <= rank_index]
    if not eligible:
        return None
    total = sum(weight for _, weight in eligible)
    point = rng.uniform(0, total)
    cursor = 0.0
    for item_id, weight in eligible:
        cursor += weight
        if point <= cursor:
            return item_id
    return eligible[-1][0]


def _award_mission_block(
    state: dict, block: dict, awarded: dict, rng: random.Random, target_character_id: str | None,
    item_chance: int, pays_gold: bool, rank: str, source: str,
) -> None:
    non_item_block = {key: value for key, value in block.items() if key not in {"item", "items"}}
    _award_reward_block(state, non_item_block, awarded, rng, target_character_id)
    item_ids = ([block["item"]] if block.get("item") else []) + list(block.get("items", []))
    fallback_high = max(1, RANK_REWARD_SCALING[rank]["gold"][0] // 4)
    for item_id in item_ids:
        roll = rng.randint(1, 100)
        won = roll <= item_chance
        fallback = rng.randint(1, fallback_high) if not won and pays_gold else 0
        if won:
            _award_item(state, item_id, awarded)
        else:
            _add_gold(state, awarded, fallback)
        awarded["loot_rolls"].append({
            "source": source, "roll": roll, "chance": item_chance,
            "item": item_id if won else None, "fallback_gold": fallback,
        })


def _award_scaled_rewards(
    state: dict, mission: dict, awarded: dict, rng: random.Random,
    target_character_id: str | None, critical: bool,
) -> None:
    rank = mission.get("rank", "E")
    scale = RANK_REWARD_SCALING[rank]
    pays_gold = bool(mission.get("pays_gold"))
    if pays_gold:
        low, high = scale["gold"]
        _add_gold(state, awarded, rng.randint(low, high))

    authored_chance = min(100, int(scale["authored_item_chance"]) + (20 if critical else 0))
    _award_mission_block(
        state, mission.get("rewards", {}), awarded, rng, target_character_id,
        authored_chance, pays_gold, rank, "mission cache",
    )
    if critical:
        critical_item_chance = min(95, int(scale["authored_item_chance"]) + 15)
        critical_block = dict(mission.get("critical_rewards", {}))
        special_groups = (
            ("critical recruit", ("generic_recruit", "procedural_recruit"), {"E": 25, "D": 30, "C": 35, "B": 42, "A": 50, "S": 60}[rank]),
            ("critical Champion encounter", ("champion", "champion_pool"), {"E": 0, "D": 5, "C": 8, "B": 12, "A": 20, "S": 30}[rank]),
            ("critical boon", ("perk", "standalone_perk", "transform"), {"E": 40, "D": 45, "C": 50, "B": 55, "A": 60, "S": 70}[rank]),
        )
        for source, keys, chance in special_groups:
            reward = {key: critical_block.pop(key) for key in keys if key in critical_block}
            if not reward:
                continue
            roll = rng.randint(1, 100)
            won = roll <= chance
            before_recruits = len(awarded["recruits"])
            before_perks = len(awarded["perks"])
            before_transforms = len(awarded["transformations"])
            if won:
                _award_reward_block(state, reward, awarded, rng, target_character_id)
            awarded["loot_rolls"].append({
                "source": source, "roll": roll, "chance": chance,
                "item": None, "fallback_gold": 0,
                "recruit": awarded["recruits"][-1] if len(awarded["recruits"]) > before_recruits else None,
                "perk": awarded["perks"][-1] if len(awarded["perks"]) > before_perks else None,
                "transformation": awarded["transformations"][-1] if len(awarded["transformations"]) > before_transforms else None,
            })
        _award_mission_block(
            state, critical_block, awarded, rng, target_character_id,
            critical_item_chance, pays_gold, rank, "critical cache",
        )

    for reward_roll in mission.get("reward_rolls", []):
        if reward_roll.get('requires_combat') and not mission.get('completed_combat'):
            continue
        if reward_roll.get("requires_chain_parent") and not mission.get("chain_reward_eligible"):
            continue
        chance = int(reward_roll.get("chance", 0))
        if critical:
            chance += int(reward_roll.get("critical_bonus", 0))
        chance = max(0, min(100, chance))
        roll = rng.randint(1, 100)
        won = roll <= chance
        before_items = len(awarded["items"])
        before_perks = len(awarded["perks"])
        if won:
            _award_reward_block(
                state, reward_roll.get("reward", {}), awarded, rng, target_character_id,
            )
        awarded["loot_rolls"].append({
            "source": reward_roll.get("source", "mission discovery"),
            "roll": roll, "chance": chance,
            "item": awarded["items"][-1] if len(awarded["items"]) > before_items else None,
            "perk": awarded["perks"][-1] if len(awarded["perks"]) > before_perks else None,
            "fallback_gold": 0,
        })

    event = EVENT_REWARD_TABLES.get(mission.get("event"))
    if event:
        keepsake_chance = {"E": 45, "D": 52, "C": 60, "B": 68, "A": 76, "S": 85}[rank]
        if critical:
            keepsake_chance = min(95, keepsake_chance + 10)
        keepsake_roll = rng.randint(1, 100)
        keepsake_won = keepsake_roll <= keepsake_chance
        if keepsake_won:
            _award_item(state, event["keepsake"], awarded)
        awarded["loot_rolls"].append({
            "source": "event keepsake", "roll": keepsake_roll, "chance": keepsake_chance,
            "item": event["keepsake"] if keepsake_won else None, "fallback_gold": 0,
        })

    loot_table = list(GENERAL_LOOT_TABLE) + (list(event.get("loot", [])) if event else [])
    chance = min(95, int(scale["loot_chance"]) + (15 if critical else 0))
    fallback_high = max(1, scale["gold"][0] // 5)
    for roll_index in range(int(scale["loot_rolls"])):
        roll = rng.randint(1, 100)
        won = roll <= chance
        item_id, pool_source, item_rarity = roll_item_pool(mission,rank,rng,ITEMS,GENERAL_LOOT_TABLE,event,MISSION_RANKS,force_faction=bool(event and roll_index==0)) if won else (None,'cache',None)
        if event and roll_index==0:pool_source='event cache'
        fallback = rng.randint(1, fallback_high) if not item_id and pays_gold else 0
        if item_id:
            _award_item(state, item_id, awarded)
        else:
            _add_gold(state, awarded, fallback)
        awarded["loot_rolls"].append({
            "source": pool_source, "roll": roll, "chance": chance, "rarity":item_rarity,
            "item": item_id, "fallback_gold": fallback,
        })

    if event and target_character_id:
        perk_chance = {"E": 0, "D": 2, "C": 4, "B": 7, "A": 10, "S": 14}[rank] + (12 if critical else 0)
        if rng.randint(1, 100) <= perk_chance:
            _award_reward_block(
                state, {"standalone_perk": event["perk"]}, awarded, rng, target_character_id,
            )
    region = mission.get("recruit_region")
    recruit_table = [] if mission.get("chain_only") else (event.get("recruits", []) if event else REGIONAL_RECRUIT_TABLES.get(region, GENERAL_RECRUIT_TABLE))
    if recruit_table and rank != "E":
        base_chance = ({"E": 0, "D": 3, "C": 7, "B": 12, "A": 18, "S": 25} if event else {"E": 0, "D": 1, "C": 2, "B": 4, "A": 6, "S": 10})[rank]
        recruit_chance = base_chance + ((15 if event else 8) if critical else 0)
        recruit_roll = rng.randint(1, 100)
        profile_id = _weighted_event_profile(recruit_table, rank, rng) if recruit_roll <= recruit_chance else None
        recruit_summary = None
        if profile_id:
            recruit = _make_procedural(profile_id, rng)
            state["characters"].append(recruit)
            recruit_summary = {"name": recruit["name"], "kind": "event" if event else "survivor", "race": recruit["race"], "profile": profile_id}
            awarded["recruits"].append(recruit_summary)
        awarded["loot_rolls"].append({
            "source": "event encounter" if event else "survivor encounter", "roll": recruit_roll, "chance": recruit_chance,
            "item": None, "fallback_gold": 0, "recruit": recruit_summary,
        })

    if rank in {"C", "B", "A", "S"} and not mission.get("chain_only"):
        champion_chance = {"C": 5, "B": 10, "A": 25, "S": 60}[rank]
        if critical:
            champion_chance += {"C": 10, "B": 20, "A": 40, "S": 80}[rank]
        champion_roll = rng.randint(1, 1000)
        champion_id = _random_champion(state, rank, rng) if champion_roll <= champion_chance else None
        champion_summary = None
        if champion_id:
            recruit = _make_champion(champion_id)
            state["characters"].append(recruit)
            champion_summary = {"name": recruit["name"], "kind": "champion", "race": recruit.get("race", ""), "profile": champion_id}
            awarded["recruits"].append(champion_summary)
        awarded["loot_rolls"].append({
            "source": "champion encounter", "roll": champion_roll, "chance": champion_chance, "range": 1000,
            "item": None, "fallback_gold": 0, "champion": champion_summary,
        })


def _incapacitate_character(state: dict, party: list[dict], rng: random.Random, now: int) -> dict | None:
    if not party:
        return None
    injured = rng.choice(party)
    building_types_present = {building.get("type") for building in state.get("buildings", [])}
    if "infirmary" in building_types_present:
        location, duration = "Infirmary", 30 * 60
    elif "tent" in building_types_present:
        location, duration = "Tent", 2 * 60 * 60
    else:
        location, duration = "Field rest", 4 * 60 * 60
    for building in state.get("buildings", []):
        if injured["id"] in building.get("assigned", []):
            building["assigned"].remove(injured["id"])
    injured["assignment"] = None
    injured["status"] = "incapacitated"
    injured["hp"] = 1
    injured["recovers_at"] = now + duration
    injured["recovery_location"] = location
    return {"character_id": injured["id"], "name": injured["name"], "location": location, "recovers_at": now + duration}


def _natural_join(parts: list[str]) -> str:
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _mission_story(
    mission: dict, party: list[dict], analysis: dict, outcome: str,
    rng: random.Random, awarded: dict,
) -> list[str]:
    narrative = mission.get("narrative", {})
    lead = analysis.get("lead") or (party[0]["name"] if party else "The expedition")
    names = [c.get("name", "Unknown") for c in party]
    if not names:
        party_text = "The expedition"
    elif len(names) == 1:
        party_text = "The expedition"
    elif len(names) == 2:
        party_text = f"{names[0]} and {names[1]}"
    else:
        party_text = ", ".join(names[:-1]) + f", and {names[-1]}"

    def fmt(text: str) -> str:
        return text.format(lead=lead, party=party_text)

    def choose_text(value: str | list[str] | None) -> str | None:
        if isinstance(value, list):
            value = rng.choice(value) if value else None
        return fmt(value) if value else None

    paragraphs: list[str] = []
    approach = choose_text(narrative.get("approach"))
    outcome_text = choose_text(narrative.get(outcome))
    if approach:
        paragraphs.append(approach)
    if outcome_text:
        paragraphs.append(outcome_text)
    thread_epilogue = choose_text(mission.get("thread_epilogue"))
    if thread_epilogue:
        paragraphs.append(thread_epilogue)

    if party:
        focus = rng.choice(party)
        focus_name = focus.get("name", "One party member")
        stat_moments = {
            "combat": f"{focus_name} caught the first warning of an attack and shifted the line before it landed. The few seconds gained there kept the rest of the plan intact.",
            "scavenging": f"{focus_name} noticed that part of the site had been disturbed recently. Following those marks revealed the route the last searchers had overlooked.",
            "building": f"{focus_name} stopped the work when a support began to move, braced it with what the party carried, and reopened the route without bringing the structure down.",
            "medicine": f"{focus_name} recognized which danger could wait and which could not. Treating the urgent problem first gave everyone enough time to finish the work.",
            "survival": f"{focus_name} read the change in the tracks and moved the party off the obvious route. The danger passed close enough to hear, but never found them.",
            "magic": f"{focus_name} saw the same pattern repeat inside the disturbance. Breaking that rhythm created the opening the party needed.",
            "alchemy": f"{focus_name} identified the unstable mixture before anyone touched it and used a small reaction to make the larger hazard safe.",
        }
        if outcome in {"success", "critical_success"}:
            moments = [
                stat_moments.get(mission.get("stat"), f"{focus_name} noticed the danger changing and redirected the party before the original route closed."),
                f"{focus_name} noticed a safer line through the ground ahead and redirected the party before the opposition could close it. The opening was brief, but it was enough.",
                f"When the original plan stopped matching the situation, {focus_name} improvised. The adjustment was rough, but it gave the expedition its momentum back.",
            ]
        else:
            moments = [
                f"{focus_name} recognized the danger first and prevented the setback from becoming worse, though there was no safe way to recover the objective.",
                f"The mission pressed harder than the party expected. By the time {focus_name} found another approach, the useful window had already closed.",
                f"For a moment {focus_name} found a possible route through, but the rest of the situation collapsed too quickly for the party to exploit it.",
            ]
        paragraphs.append(rng.choice(moments))

    role_lines = []
    for role in analysis.get("roles", []):
        if not role.get("character"):
            continue
        if role.get("meets_recommendation"):
            role_lines.append(f"{role['character']} held the {role['label']} assignment at the level the plan demanded")
        else:
            role_lines.append(f"{role['character']} struggled in the {role['label']} assignment and had to be covered by the others")
    if role_lines:
        paragraphs.append("In the decisive stretch, " + "; while ".join(role_lines) + ".")

    discoveries = []
    if awarded.get("recruits"):
        discoveries.append("returned with " + _natural_join([recruit["name"] for recruit in awarded["recruits"]]))
    if awarded.get("items"):
        item_names = [ITEMS[item_id]["name"] for item_id in awarded["items"] if item_id in ITEMS]
        if item_names:
            discoveries.append("secured " + _natural_join(item_names[:3]))
    material_total = sum(int(amount) for amount in awarded.get("materials", {}).values())
    if material_total:
        discoveries.append(f"brought back {material_total} measures of usable supplies")
    if discoveries and outcome in {"success", "critical_success"}:
        paragraphs.append("At Fortcamp's gate, the result became clear: the party " + _natural_join(discoveries) + ".")
    return paragraphs


def _classify_roll(die: int, total: int, difficulty: int, critical_threshold: int, critical_success_available: bool, rank: str = "E", critical_roll: int = 101) -> str:
    return classify_roll(die, total, difficulty, rank, critical_success_available, critical_roll)


def resolve_mission(state: dict, mission: dict, party_ids: list[str], analysis: dict, seed: str, forced_outcome: str | None = None) -> dict:
    rng = random.Random(seed)
    difficulty = int(mission["difficulty"])
    crit_threshold = int(analysis["critical_threshold"])
    bonus = int(analysis["lead_stat"]) + int(analysis["support_bonus"]) + int(analysis["criteria_bonus"])
    valid_outcomes = {"critical_failure", "failure", "success", "critical_success"}
    if forced_outcome and forced_outcome not in valid_outcomes:
        raise ValueError("Unknown forced mission outcome")
    critical_success_available = bool(analysis.get("critical_success_available", not mission.get("critical_any")))
    if forced_outcome == "critical_success" and not critical_success_available:
        raise ValueError("Critical Success is locked because this party did not meet a special critical criterion")

    if forced_outcome:
        matching = []
        for candidate in range(1, 21):
            candidate_total = candidate + bonus
            if _classify_roll(candidate, candidate_total, difficulty, crit_threshold, critical_success_available) == forced_outcome:
                matching.append(candidate)
        die = rng.choice(matching) if matching else {"critical_failure": 1, "failure": 5, "success": 12, "critical_success": 20}[forced_outcome]
        total = die + bonus
        outcome = forced_outcome
    else:
        die = rng.randint(1, 20)
        total = die + bonus
        critical_roll = rng.randint(1, 10000) / 100
        outcome = _classify_roll(die, total, difficulty, crit_threshold, critical_success_available, mission.get("rank", "E"), critical_roll)

    party = [find_char(state, cid) for cid in party_ids]
    record_mission(state, mission, list(dict.fromkeys(party_ids + list(analysis.get("bodyguard_ids", [])))), outcome, analysis.get("service_record_started",False))
    special_events = []
    for evt in mission.get("special_events", []):
        if condition_met(state, party, evt.get("condition", {})):
            special_events.append(evt.get("label", "Special event"))

    awarded = {
        "gold": 0, "materials": {}, "items": [], "blueprints": [], "recruits": [],
        "perks": [], "transformations": [], "loot_rolls": [], "injuries": [],
        "secret_events": [], "chain_starts": [], "world_flags": [],
    }
    reward_target = analysis.get("lead_id") or (party_ids[0] if party_ids else None)
    if outcome in {"success", "critical_success"}:
        completed=state.setdefault('completed_by_rank',{});rank=mission.get('rank','E');completed[rank]=completed.get(rank,0)+1
        earn_relationship(state, mission, outcome)
        for member in party:
            practice(member, 'alchemy' if mission['stat']=='cooking' else mission['stat'], 6 if outcome=='critical_success' else 3)
        _award_scaled_rewards(state, mission, awarded, rng, reward_target, outcome == "critical_success")
        if mission.get("celestial_reward"):
            _award_reward_block(
                state, {"celestial": mission["celestial_reward"]}, awarded, rng, reward_target,
            )
        eligible_ids = set(analysis.get("eligible_secret_event_ids", []))
        for secret in mission.get("secret_events", []):
            if secret.get("id") not in eligible_ids:
                continue
            chance = int(secret.get("chance", 0))
            if outcome == "critical_success":
                chance += int(secret.get("critical_bonus", 0))
            if rng.randint(1, 100) <= min(100, chance):
                _award_reward_block(state, secret.get("reward", {}), awarded, rng, reward_target)
                label = secret.get("label", "The party uncovered something that should have remained hidden.")
                special_events.append(label)
                awarded["secret_events"].append({"id": secret.get("id"), "label": label})
                if secret.get("chain_start"):
                    awarded["chain_starts"].append(str(secret["chain_start"]))
    elif outcome == "failure" and mission.get("pays_gold"):
        # A patron may cover a token portion of expenses, but a failed mission never
        # returns materials, equipment, recruits, perks, or the normal contract fee.
        scale = RANK_REWARD_SCALING[mission.get("rank", "E")]
        _add_gold(state, awarded, rng.randint(0, max(1, scale["gold"][0] // 5)))

    set_party_status(state, party_ids, "idle")
    resolved_at = int(time.time())
    if outcome == "critical_failure":
        for c in party:
            c["morale"] = max(0, int(c.get("morale", 70)) - 10)
        injury = _incapacitate_character(state, party, rng, resolved_at)
        # A solo beginner must not lose the entire playable roster for hours.
        if injury and mission.get('rank') == 'E' and sum(not c.get('temporary_mercenary') for c in state.get('characters',[])) == 1:
            injured = find_char(state, injury['character_id'])
            injured['recovers_at'] = injury['recovers_at'] = resolved_at + 120
            injured['recovery_location'] = injury['location'] = 'Beginner field rest'
        if injury:
            if not analysis.get("battle"):
                injured=find_char(state,injury["character_id"]);ensure_character(injured)
                injured["service_record"]["times_defeated"]+=1
            awarded["injuries"].append(injury)
    elif outcome == "failure":
        for c in party:
            c["morale"] = max(0, int(c.get("morale", 70)) - 2)

    story = _mission_story(mission, party, analysis, outcome, rng, awarded)
    credit_allegiance(state, analysis, outcome, story)
    if special_events:
        story.extend(special_events)
    if awarded["injuries"]:
        injury = awarded["injuries"][0]
        story.append(f"{injury['name']} was incapacitated and taken to the {injury['location']} to recover.")
    board_followups = []
    if outcome in {"success", "critical_success"}:
        for followup in mission.get("board_followups", []):
            chance = int(followup.get("chance", 0))
            if outcome == "critical_success":
                chance += int(followup.get("critical_bonus", 0))
            template_id = followup.get("template_id")
            followup_template = MISSION_TEMPLATES.get(template_id)
            if followup_template and rng.randint(1, 100) <= min(100, chance):
                board_followups.append({
                    "template_id": template_id, "name": followup_template["name"],
                    "story_thread": followup_template.get("story_thread"),
                    "story_thread_name": followup_template.get("story_thread_name"),
                })
        if board_followups:
            names = ", ".join(entry["name"] for entry in board_followups)
            story.append(f"The expedition uncovered a new lead: {names}. The guild has set aside the follow-up contracts for your party.")
    result = {
        "mission": mission["name"], "outcome": outcome, "die": die, "total": total,
        "rank":mission.get('rank','E'),
        "difficulty": difficulty, "lead": analysis.get("lead"), "stat": mission["stat"],
        "triggered": analysis.get("triggered", []), "critical_unlocks": analysis.get("critical_unlocks", []),
        "roles": analysis.get("roles", []), "role_assignments": analysis.get("role_assignments", {}),
        "critical_success_available": critical_success_available,
        "special_events": special_events, "story": story, "rewards": awarded, "timestamp": resolved_at,
        "board_followups": board_followups,
        "debug_forced": bool(forced_outcome),
    }
    state.setdefault("mission_history", []).insert(0, result)
    state["mission_history"] = state["mission_history"][:30]
    for member in party:member.pop('prepared_meal',None)
    return result


def _placement_error(state: dict, building_type: str, x: int, y: int, ignore_building_id: str | None = None) -> str | None:
    if building_type not in BUILDINGS:
        return "Unknown building"
    bdef = BUILDINGS[building_type]
    w, h = int(bdef["w"]), int(bdef["h"])
    size=state.get('base_size',{'w':GRID_W,'h':GRID_H})
    if x < 0 or y < 0 or x + w > size['w'] or y + h > size['h']:
        return "Building would be outside the base"
    for placed in state.get("buildings", []):
        if ignore_building_id and placed.get("id") == ignore_building_id:
            continue
        pdef = BUILDINGS[placed["type"]]
        if not (x + w <= placed["x"] or placed["x"] + pdef["w"] <= x or y + h <= placed["y"] or placed["y"] + pdef["h"] <= y):
            return "That space is occupied"
    return None


def move_building(state: dict, building_id: str, x: int, y: int) -> dict:
    building = next((b for b in state.get("buildings", []) if b.get("id") == building_id), None)
    if not building:
        raise ValueError("Building not found")
    err = _placement_error(state, building["type"], x, y, ignore_building_id=building_id)
    if err:
        raise ValueError(err)
    building["x"] = x
    building["y"] = y
    return building


def place_building(state: dict, blueprint_id: str, x: int, y: int) -> dict:
    normalize_state(state)
    if blueprint_id not in state.get("learned_blueprints", []):
        raise ValueError("Blueprint has not been learned")
    if blueprint_id not in BUILDINGS:
        raise ValueError("Unknown building")
    if blueprint_id == "guild_hall" and any(b.get("type") == "guild_hall" for b in state.get("buildings", [])):
        raise ValueError("Only one Guild Hall can be built")
    bdef = BUILDINGS[blueprint_id]
    err = _placement_error(state, blueprint_id, x, y)
    if err:
        raise ValueError(err)
    for res, amount in bdef.get("cost", {}).items():
        if state["resources"].get(res, 0) < amount:
            raise ValueError(f"Not enough {res}")
    for res, amount in bdef.get("cost", {}).items():
        state["resources"][res] -= amount
    building = {"id": uid("building"), "type": blueprint_id, "x": x, "y": y, "assigned": []}
    state["buildings"].append(building)
    if blueprint_id == "guild_hall" and MISSION_RANKS.index(mission_rank(state)) < MISSION_RANKS.index("D"):
        state["mission_rank"] = "D"
    return building


def assign_character(state: dict, char_id: str, building_id: str | None) -> None:
    settle_economy(state)
    char = find_char(state, char_id)
    if char.get("status") != "idle":
        raise ValueError("An unavailable character cannot be reassigned")
    for b in state["buildings"]:
        if char_id in b.get("assigned", []):
            b["assigned"].remove(char_id)
    char["assignment"] = None
    if not building_id:
        return
    building = next((b for b in state["buildings"] if b["id"] == building_id), None)
    if not building:
        raise ValueError("Building not found")
    capacity = int(BUILDINGS[building["type"]].get("workers", 0)) + (building.get('level',1)-1 if BUILDINGS[building['type']].get('production') else 0)
    if capacity <= 0:
        raise ValueError("This building has no worker assignment slots")
    if len(building.get("assigned", [])) >= capacity:
        raise ValueError("Building assignment slots are full")
    building.setdefault("assigned", []).append(char_id)
    char["assignment"] = building_id


def train_perk(state: dict, char_id: str, track: str, teacher_id: str | None = None) -> dict:
    normalize_state(state)
    if track not in PERK_TRACKS:
        raise ValueError("Unknown perk track")
    char = find_char(state, char_id)
    if char.get("status") != "idle":
        raise ValueError("Only an idle character can train")
    facility = PERK_TRACKS[track]["facility"]
    if facility not in building_types(state):
        raise ValueError(f"Build a {BUILDINGS[facility]['name']} to train this perk")
    current = perk_level(char, track)
    current_index = PERK_LEVELS.index(current)
    if current_index >= len(PERK_LEVELS) - 1:
        raise ValueError("This perk is already Master tier")
    target = PERK_LEVELS[current_index + 1]
    teachers=[c for c in state['characters'] if c['id']!=char_id and c.get('status')=='idle' and perk_rank(c,track)>=current_index+1]
    teacher=next((c for c in teachers if c['id']==teacher_id),None) if teacher_id else next(iter(teachers),None)
    if not teacher and current_index>0:
        raise ValueError(f'An idle teacher with {target.title()} {PERK_TRACKS[track]["name"]} is required. Relevant work also builds proficiency naturally.')
    # Local instructors teach the fundamentals, so a solo camp is not blocked.
    fee=8 if not teacher else 0
    if state['resources'].get('gold',0)<fee:raise ValueError('A local basic instructor costs 8 gold')
    required_item = PERK_TRAINING_ITEMS.get(target)
    consumed = None
    if required_item:
        consumed = next((item for item in state.get("inventory", []) if item.get("item_id") == required_item), None)
        if not consumed:
            raise ValueError(f"{ITEMS[required_item]['name']} required for {target.title()} training")
        state["inventory"].remove(consumed)
    state['resources']['gold']-=fee
    char.setdefault("perks", {})[track] = target
    return {
        "character_id": char_id, "track": track, "level": target,
        "consumed": required_item, "attribute_bonus": PERK_TRACKS[track]["attribute_bonus"],
        "teacher": teacher['name'] if teacher else 'Local instructor', "fee":fee,
    }


def equip_item(state: dict, char_id: str, instance_id: str | None, slot: str) -> None:
    if slot not in EQUIPMENT_SLOTS:
        raise ValueError("Unknown equipment slot")
    char = find_char(state, char_id)
    if char.get("status") not in {"idle", "incapacitated"}:
        raise ValueError("Equipment is locked while that character is on a mission")
    if not instance_id:
        char["equipment"][slot] = None
        return
    inv = _inventory_index(state)
    inst = inv.get(instance_id)
    if inst and inst.get("mercenary_gear"):
        raise ValueError("Mercenary equipment belongs to its owner")
    if not inst or inst.get("item_id") not in ITEMS:
        raise ValueError("Item not found")
    if ITEMS[inst["item_id"]]["slot"] != slot:
        raise ValueError("Item cannot be equipped in that slot")
    for other in state["characters"]:
        if instance_id in other.get("equipment", {}).values() and other.get("status") not in {"idle", "incapacitated"}:
            raise ValueError("That item is equipped by a character on a mission")
    # A physical item may only be equipped by one character at a time.
    for other in state["characters"]:
        for other_slot, equipped in other.get("equipment", {}).items():
            if equipped == instance_id:
                other["equipment"][other_slot] = None
    char["equipment"][slot] = instance_id
