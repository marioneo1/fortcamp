"""Ephemeral, owner-scoped battle previews. Never creates missions or writes saves."""
from copy import deepcopy
from functools import lru_cache
from time import monotonic
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .auth import IdentityDep
from .combat import create_battle, battle_view, apply_player_command, auto_step, auto_resolve, _advance_to_player
from .content import MISSION_TEMPLATES, MISSION_EVENTS
from .db import SessionLocal
from .game import new_game, normalize_state
from .mission_decisions import setup_encounter
from .models import PlayerState
from .settings import settings
from .tactical_contracts import TACTICAL_CONTRACTS
from .location_maps import MISSION_LOCATIONS, location_blueprint
from .location_templates import BUILDING_PLANS
from .building_templates import BUILDINGS
from .building_showcase import FAMILIES, presets as material_presets
from .battle_maps import compile_generated_battle_map

router = APIRouter(prefix='/api/debug/battle-lab')
_sessions = {}
TTL = 3600
MAX_SESSIONS = 64
SUPPORTED = {'goblin_warcamp', 'goblin_captive_cart', 'goblin_smoke_signals', 'frontier_watch_defense'}


def authorize(identity):
    if not settings.game_debug_mode or settings.environment.lower() in {'prod', 'production', 'release', 'stable'}:
        raise HTTPException(404, 'Battle Lab is only available in development debug mode')
    if not identity.guild_admin and not settings.dev_bypass_auth:
        raise HTTPException(403, 'Battle Lab is limited to server admins')


def supported(encounter):
    return encounter in SUPPORTED or (encounter.startswith('contract:') and encounter[9:] in TACTICAL_CONTRACTS)


LAYOUT_LABELS = {
    'enclosed_repair_yard':'Enclosed repair yard',
    'workshops_across_courtyard':'Two workshops across a courtyard',
    'forge_house_and_open_bays':'Forge house with open work bays',
    'armory_north_south_stores':'North and south stores · open courtyard',
    'armory_east_west_stores':'East and west stores · open courtyard',
    'shed_west_door_south_breach':'Shed · southern breach',
    'shed_west_door_north_breach':'Shed · northern breach',
}


@lru_cache(maxsize=128)
def layout_presets(encounter):
    """Find repeatable seeds using the actual map selector, per encounter, not mission."""
    if encounter.startswith('showcase:'):
        return material_presets(encounter.removeprefix('showcase:'))
    mid=encounter.removeprefix('contract:')
    location=MISSION_LOCATIONS.get(mid) if encounter.startswith('contract:') else None
    if not location:return []
    expected=len(BUILDING_PLANS.get(location,[None,None]));found={}
    for index in range(100):
        seed=f'layout-{index}'
        board=location_blueprint(location,seed)
        variant=board['map_variation'];ident=board['template_id']
        if variant not in found:
            label=BUILDINGS.get(ident,{}).get('label') or LAYOUT_LABELS.get(ident,ident.replace('_',' ').title())
            if location in {'broken_creek_bridge','toll_bridge'}:
                family='Stone' if '_stone_' in ident else 'Wood'
                label=f'{family} bridge · {"upper" if ident.endswith("_4") else "lower"} crossing'
            found[variant]={'id':ident,'label':label,'seed':seed}
        if len(found)==expected:break
    return [found[key] for key in sorted(found)]


def catalogue():
    result = []
    for mid, mission in MISSION_TEMPLATES.items():
        default = (mission.get('combat_encounter') or {}).get('id', '')
        variants = []
        if supported(default):
            variants.append({'id': 'direct', 'label': 'Direct map test', 'node': 'Skip story choices',
                             'outcome': 'direct', 'description': 'Normal deployment. Defense maps retain their preparation phase.',
                             'encounter_id': default, 'transition': {}})
        for nid, node in (mission.get('decision_scene') or {}).get('nodes', {}).items():
            for cid, choice in node.get('choices', {}).items():
                for outcome in ('success', 'failure', 'critical_failure'):
                    transition = choice.get(outcome) or {}
                    encounter = transition.get('battle', '')
                    if encounter == 'default':
                        encounter = default
                    if not supported(encounter):
                        continue
                    variants.append({'id': f'{nid}:{cid}:{outcome}', 'label': choice['label'],
                                     'node': node['title'], 'outcome': outcome, 'description': choice.get('description', ''),
                                     'stat': choice.get('stat'), 'requires': choice.get('requires'),
                                     'encounter_id': encounter, 'transition': deepcopy(transition)})
        if not variants:
            continue
        for variant in variants:
            variant['layout_presets']=deepcopy(layout_presets(variant['encounter_id']))
        event = mission.get('event') or 'general'
        source = MISSION_EVENTS.get(event, {}).get('name', event.replace('_', ' ').title())
        if mission.get('chain_only') or mission.get('trigger_only'):
            source = 'Private Contracts · Follow-up'
        parents = [m['name'] for m in MISSION_TEMPLATES.values()
                   if any(f.get('template_id') == mid for f in m.get('board_followups', []))]
        result.append({'id': mid, 'name': mission['name'], 'rank': mission.get('rank', 'E'),
                       'description': mission.get('description', ''), 'form': mission.get('mission_form', 'combat'),
                       'source': source, 'faction': mission.get('faction', ''), 'follows': parents, 'variants': variants})
    for family,label in FAMILIES.items():
        boxed=family=='limestone_boxed'
        result.append({'id':'material_'+family,'name':label+' building kit','rank':'E',
            'description':('Six generated wall pieces at one shared scale. Compare isolated pieces and connected runs; spans are not exact.' if boxed else 'Four authored material test maps. Every kit piece appears across the four layouts. No rewards or save changes.'),
            'form':'art test','source':'Building material tests','faction':'','follows':[],
            'variants':[{'id':'direct','label':'Material test','node':'Building kit inspection','outcome':'direct',
                         'description':('Inspect full/half straight walls and authored corner/T/cross connections. This candidate has no doors or gates.' if boxed else 'Inspect walls, openings, damage states and supporting parts. Doors and walls work normally; stairs are scenery.'),
                         'encounter_id':'showcase:'+family,'transition':{},'layout_presets':material_presets(family)}]})
    return sorted(result, key=lambda m: ('EDCBAS'.index(m['rank']), m['name']))


def prune():
    cutoff = monotonic() - TTL
    for sid in list(_sessions):
        if _sessions[sid]['touched'] < cutoff:
            del _sessions[sid]


def get_session(sid, identity):
    authorize(identity)
    prune()
    row = _sessions.get(sid)
    if not row or row['owner'] != (identity.guild_id, identity.user_id):
        raise HTTPException(404, 'Test session expired. Start another battle in Battle Lab.')
    row['touched'] = monotonic()
    return row


def session_view(sid, row):
    return {'session_id': sid, 'mission': row['mission'], 'variant': row['variant'],
            'seed': row['seed'], 'battle': battle_view(row['battle'])}


class StartRequest(BaseModel):
    mission_id: str
    variant_id: str = 'direct'
    seed: str = Field(default='battle-test-1', min_length=1, max_length=100)
    party_ids: list[str] = Field(default_factory=list, max_length=4)
    add_helper: bool = True


def start_session(identity, request, saved_state):
    authorize(identity)
    mission = next((m for m in catalogue() if m['id'] == request.mission_id), None)
    variant = next((v for v in (mission or {}).get('variants', []) if v['id'] == request.variant_id), None)
    if not variant:
        raise HTTPException(400, 'Choose a supported mission and battle approach')
    state = normalize_state(deepcopy(saved_state)) if saved_state else new_game({'name': 'Battle Tester'})
    characters = {c['id']: c for c in state['characters']}
    party = request.party_ids or [next(iter(characters))]
    if len(set(party)) != len(party) or any(cid not in characters for cid in party):
        raise HTTPException(400, 'Choose distinct characters from your roster')
    if request.add_helper and len(party) < 2:
        helper = deepcopy(characters[party[0]])
        helper.update(id='lab_helper', name='Lab Companion', is_player=False, status='idle', assignment=None,
                      equipment={}, loyalty=100, attributes=dict(str=8, dex=7, agi=7, vit=8, int=5, luk=5))
        helper['perks'] = {'combat': 'skilled'}
        state['characters'].append(helper)
        party = [*party, helper['id']]
    # Real roster stats/gear are copied; their availability and health in the save are untouched.
    showcase=variant['encounter_id'].startswith('showcase:')
    battle = create_battle(state, party, request.seed, 'contract:tool_shed' if showcase else variant['encounter_id'], defer_start=True)
    if showcase:
        family=variant['encounter_id'].removeprefix('showcase:')
        board=compile_generated_battle_map('showcase_'+family,request.seed)
        battle.update(board,name=mission['name'],log=[board['material_showcase']['notes']+' No rewards or save changes.'])
        for team in ('player','enemy'):
            for unit,tile in zip([u for u in battle['units'].values() if u['team']==team],board['spawn_zones'][team]):
                unit.update(x=tile['x'],y=tile['y'])
        # Give the tester the first activation; art inspection should not start
        # with enemies moving through the scene before the player can see it.
        battle['turn_order']=[*[u['id'] for u in battle['units'].values() if u['team']=='player'],
                              *[u['id'] for u in battle['units'].values() if u['team']=='enemy']]
    setup_encounter(battle, variant['transition'])
    if battle['status'] != 'preparing':
        _advance_to_player(battle)
    sid = uuid4().hex
    row = {'owner': (identity.guild_id, identity.user_id), 'touched': monotonic(), 'battle': battle,
           'mission': {k: v for k, v in mission.items() if k != 'variants'},
           'variant': deepcopy(variant), 'seed': request.seed}
    prune()
    # Keep at most four previews per player and a bounded total across the dev server.
    owned = sorted((key for key, value in _sessions.items() if value['owner'] == row['owner']),
                   key=lambda key: _sessions[key]['touched'])
    for key in owned[:-3] if len(owned) >= 4 else []:
        del _sessions[key]
    while len(_sessions) >= MAX_SESSIONS:
        del _sessions[min(_sessions, key=lambda key: _sessions[key]['touched'])]
    _sessions[sid] = row
    return session_view(sid, row)


@router.get('')
async def list_battles(identity: IdentityDep):
    authorize(identity)
    async with SessionLocal() as session:
        player = await session.get(PlayerState, {'guild_id': identity.guild_id, 'user_id': identity.user_id})
        characters = (player.state if player else {}).get('characters', [])
    return {'missions': catalogue(), 'characters': [
        {'id': c['id'], 'name': c['name'], 'race': c.get('race', ''), 'status': c.get('status', ''),
         'portrait': c.get('portrait_thumbnail') or c.get('portrait', ''), 'attributes': c.get('attributes', {})}
        for c in characters]}


@router.post('')
async def start_battle(request: StartRequest, identity: IdentityDep):
    authorize(identity)
    async with SessionLocal() as session:
        player = await session.get(PlayerState, {'guild_id': identity.guild_id, 'user_id': identity.user_id})
        saved_state = deepcopy(player.state) if player else None
    return start_session(identity, request, saved_state)


@router.get('/{sid}')
async def fetch_battle(sid: str, identity: IdentityDep):
    return session_view(sid, get_session(sid, identity))


class Position(BaseModel):
    x: int
    y: int


class CommandRequest(BaseModel):
    action: str
    x: int | None = None
    y: int | None = None
    target_id: str | None = None
    move_to: Position | None = None
    placement_id: str | None = None
    skill_id: str | None = None
    item_id: str | None = None


@router.post('/{sid}/command')
async def command_battle(sid: str, request: CommandRequest, identity: IdentityDep):
    row = get_session(sid, identity)
    # Invalid commands must not leave partially changed sandbox state.
    battle = deepcopy(row['battle'])
    try:
        apply_player_command(battle, request.model_dump(exclude_none=True))
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(400, str(exc))
    row['battle'] = battle
    return session_view(sid, row)


class AutoRequest(BaseModel):
    tactic: str = 'balanced'
    resolve_all: bool = False


@router.post('/{sid}/auto')
async def auto_battle(sid: str, request: AutoRequest, identity: IdentityDep):
    row = get_session(sid, identity)
    battle = deepcopy(row['battle'])
    (auto_resolve if request.resolve_all else auto_step)(battle, request.tactic)
    row['battle'] = battle
    return session_view(sid, row)
