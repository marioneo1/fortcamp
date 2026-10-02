"""Player-owned persistent hired swords and their bounded combat appearances."""
import random
import time
import uuid
from copy import deepcopy

RANKS = 'EDCBAS'
FEES = (6, 9, 16, 28, 48, 80)
BUYOUTS = (100, 180, 360, 750, 1600, 3200)
RELATION_REQUIRED = 30
MARKET_SIZE = 4


def quote(offer):
    tier = RANKS.index(offer['rank'])
    relation = int(offer.get('relationship', 0))
    return {'fee': max(3, round(FEES[tier] * (1 - min(40, relation) / 200))),
            'betrayal_chance': max(0, round((6 + tier * 2) * (1 - relation / 100), 2)),
            'buyout': BUYOUTS[tier], 'relationship_required': RELATION_REQUIRED}


def market(state, seed):
    from .game import _make_generic, mission_rank
    from .relationships import ensure_character
    offers = state.setdefault('mercenaries', [])
    maximum = RANKS.index(mission_rank(state))
    serial = state.get('mercenary_serial', 0)
    while len(offers) < MARKET_SIZE:
        serial += 1
        rng = random.Random(f'{seed}:mercenary:{serial}')
        # Half the board stays affordable even for an established guild.
        tier = 0 if len(offers) < 2 else rng.randint(0, maximum)
        archetype = rng.choice(['fighter', 'scout', 'adept', 'medic', 'builder'])
        c = _make_generic(archetype, rng)
        c['id'] = 'merc_' + uuid.uuid4().hex
        c['attributes'] = {key: max(2, min(18, value + tier)) for key, value in c['attributes'].items()}
        c['perks'] = {('magic' if archetype == 'adept' else 'combat'): 'basic' if tier < 2 else 'skilled' if tier < 4 else 'expert'}
        c['loyalty'] = 95
        ensure_character(c)
        weapon = {'fighter':'chipped_sword', 'scout':'frayed_bow', 'adept':'cracked_wand', 'medic':'knotted_staff', 'builder':'worn_mallet'}[archetype]
        if tier >= 2:
            weapon = {'fighter':'knight_blade', 'scout':'short_bow', 'adept':'ember_staff', 'medic':'knotted_staff', 'builder':'warhammer'}[archetype]
        offers.append({'id':c['id'], 'character':c, 'rank':RANKS[tier], 'weapon':weapon,
                       'relationship':0, 'busy_mission_id':None, 'recovering_until':0})
    state['mercenary_serial'] = serial
    return [{'id':o['id'], 'rank':o['rank'], 'relationship':o['relationship'], **quote(o),
             'available':not o.get('busy_mission_id') and o.get('recovering_until', 0) <= time.time(),
             'recovering_until':o.get('recovering_until', 0),
             'character':{**deepcopy(o['character']), 'temporary_mercenary':True, 'mercenary_weapon':o['weapon']}}
            for o in offers]


def prepare(state, mission, ids, party_ids, guards=None, roles=None, spend=False):
    """Validate the exact selection on a copied state; charge only on acceptance."""
    ids = list(ids or [])
    if not ids:
        if any(c.get('temporary_mercenary') and c['id'] in set(party_ids + list(guards or []) + list((roles or {}).values())) for c in state['characters']):
            raise ValueError('Hired swords belong to their current contract only')
        return []
    if len(set(ids)) != len(ids) or len(ids) > 8:
        raise ValueError('Select each mercenary once, with at most eight hires')
    owner=(getattr(mission,'analysis',None) or {}).get('chain_owner_user_id') or mission.claimed_by_user_id
    if owner is None or str(owner) != str(state.get('_mercenary_owner')):
        raise ValueError('Save this contract to Private Contracts before hiring')
    selected = set(party_ids + list(guards or []) + list((roles or {}).values()))
    own = [c for c in state['characters'] if c['id'] in selected and not c.get('temporary_mercenary')]
    if not any(c['id'] in set(party_ids + list((roles or {}).values())) and c.get('status') == 'idle' for c in own):
        raise ValueError('Assign at least one available crew member before hiring')
    if not set(ids) <= selected:
        raise ValueError('Every hired mercenary needs a party or bodyguard slot')
    offers = {o['id']:o for o in state.get('mercenaries', [])}
    chosen = []
    for mid in ids:
        o = offers.get(mid)
        if not o or o.get('busy_mission_id') or o.get('recovering_until', 0) > time.time():
            raise ValueError('A selected mercenary is unavailable. Reopen the hiring board.')
        chosen.append(o)
    fee = sum(quote(o)['fee'] for o in chosen)
    if state['resources'].get('gold', 0) < fee:
        raise ValueError(f'You need {fee} gold to hire this group')
    for o in chosen:
        c = deepcopy(o['character'])
        c.update(temporary_mercenary=True, mercenary_id=o['id'], status='idle', assignment=None)
        c['loyalty'] = 95 + min(5, o['relationship']//6)
        c['equipment'] = {slot:None for slot in c['equipment']}
        iid = f"mercgear_{mission.id}_{o['id']}"
        state['inventory'].append({'instance_id':iid, 'item_id':o['weapon'], 'mercenary_gear':True})
        c['equipment']['weapon'] = iid
        state['characters'].append(c)
        if spend:
            o['busy_mission_id'] = mission.id
    if spend:
        state['resources']['gold'] -= fee
    return chosen


def betrayal(offers, seed):
    if not offers:
        return []
    rng = random.Random(f'{seed}:mercenary-betrayal')
    chance = min(25, sum(quote(o)['betrayal_chance'] for o in offers)/len(offers) + 2*(len(offers)-1)*(1-min(o.get('relationship',0) for o in offers)/100))
    if rng.random()*100 >= chance:
        return []
    traitors = [o['id'] for o in offers]
    if len(traitors) > 1 and rng.random() < .15:
        traitors.remove(rng.choice(traitors))
    return traitors


def recruit(state, mid):
    offer = next((o for o in state.get('mercenaries', []) if o['id'] == mid), None)
    if not offer or offer.get('busy_mission_id') or offer.get('recovering_until', 0) > time.time():
        raise ValueError('This mercenary is unavailable')
    terms = quote(offer)
    if offer['relationship'] < RELATION_REQUIRED:
        raise ValueError('Build 30 relationship through completed contracts first')
    if state['resources'].get('gold', 0) < terms['buyout']:
        raise ValueError(f"Permanent service costs {terms['buyout']} gold")
    c = deepcopy(offer['character'])
    c.update(source_kind='generic', status='idle', loyalty=75 + min(20, offer['relationship']//2))
    iid = 'item_' + uuid.uuid4().hex
    state['inventory'].append({'instance_id':iid, 'item_id':offer['weapon']})
    c['equipment']['weapon'] = iid
    state['resources']['gold'] -= terms['buyout']
    state['characters'].append(c)
    state['mercenaries'].remove(offer)
    return c


def settle(state, analysis, outcome, battle=None, final=True):
    """Deaths never reroll survivors. Settlement is idempotent at mission completion."""
    if final and analysis.get('mercenaries_settled'):
        return
    offers = {o['id']:o for o in state.get('mercenaries', [])}
    for unit in (battle or {}).get('units', {}).values():
        mid = unit.get('mercenary_id')
        if not mid or mid not in offers:
            continue
        o = offers[mid]
        if unit.get('condition') == 'dead':
            state['mercenaries'].remove(o)
            offers.pop(mid)
        elif unit.get('condition') == 'unconscious':
            o['recovering_until'] = time.time() + 1800
    if final:
        for mid in analysis.get('mercenary_guest_ids', []):
            o = offers.get(mid)
            if o:
                o['busy_mission_id'] = None
                unit = (battle or {}).get('units', {}).get(mid,{})
                if unit.get('team') == 'player':o['relationship'] = min(100,o['relationship']+2)
        for mid in analysis.get('mercenary_ids', []):
            o = offers.get(mid)
            if o:
                o['busy_mission_id'] = None
                if mid not in analysis.get('mercenary_traitors', []):
                    o['relationship'] = min(100, o['relationship'] + (2 if outcome in ('success','critical_success') else 1))
                if outcome == 'critical_failure':
                    o['recovering_until'] = max(o.get('recovering_until', 0), time.time()+1800)
        ids = set(analysis.get('mercenary_ids', []))
        state['characters'] = [c for c in state['characters'] if c['id'] not in ids]
        state['inventory'] = [i for i in state['inventory'] if not i.get('mercenary_gear') or not any(mid in i['instance_id'] for mid in ids)]
        analysis['mercenaries_settled'] = True


def add_unit(battle, state, offer, team, rng, corpse=False, rogue=False):
    from .combat import _player_unit, _blocked, _reachable
    players = [u for u in battle['units'].values() if u['team'] == 'player' and u.get('alive')]
    if not players:
        return None
    scout = players[0]
    reach = _reachable(battle, scout, battle['width']*battle['height']*4)
    cells = [(x,y) for x,y in reach if not _blocked(battle,x,y)
             and min(abs(x-u['x'])+abs(y-u['y']) for u in players) >= 3]
    enemies = [u for u in battle['units'].values() if u['team']=='enemy' and u.get('alive')]
    if corpse and enemies:
        cells = [p for p in cells if min(abs(p[0]-u['x'])+abs(p[1]-u['y']) for u in enemies) <= 2]
    else:
        # Enter along an approach, never materialize beside an objective or inside a wall.
        cells = [p for p in cells if min(p[0],p[1],battle['width']-1-p[0],battle['height']-1-p[1]) <= 1
                 and all(abs(p[0]-u['x'])+abs(p[1]-u['y']) >= 2 for u in enemies)]
    if not cells:
        return None
    x,y = rng.choice(sorted(cells))
    preview = deepcopy(state)
    c = deepcopy(offer['character'])
    iid = 'guest_' + offer['id']
    preview['inventory'].append({'instance_id':iid,'item_id':offer['weapon']})
    c['equipment']['weapon'] = iid
    unit = _player_unit(preview,c,x,y)
    unit.update(team=team, mercenary_id=offer['id'], mercenary_guest=True,
                mercenary_hostile=rogue, mercenary_hostile_all=rogue, boss=rogue, player_avatar=False,
                loyalty=100, corpse_item=None, corpse_item_chance=0, corpse_gold=(0,0))
    if corpse:
        unit.update(hp=0,alive=False,conscious=False,condition='dead')
    battle['units'][unit['id']] = unit
    if not corpse:
        battle['turn_order'].append(unit['id'])
    return unit


def decorate_battle(state, analysis, battle, seed, force=None):
    """One rare incident per contract, restricted to believable outdoor approaches."""
    if analysis.get('mercenary_incident_checked'):
        return
    from .tactical_contracts import TACTICAL_CONTRACTS
    encounter = battle.get('encounter_id','')
    spec = TACTICAL_CONTRACTS.get(encounter.removeprefix('contract:'), {})
    appropriate = encounter in ('goblin_warcamp','goblin_captive_cart','goblin_smoke_signals','frontier_watch_defense') or (spec.get('layout') in ('road','camp') and not spec.get('stealth'))
    if not appropriate:
        return
    analysis['mercenary_incident_checked'] = True
    rng = random.Random(f'{seed}:mercenary-incident')
    roll = rng.random()
    kind = force or ('corpse' if roll < .01 else 'hostile' if roll < .0125 else 'friendly' if roll < .015 else None)
    if not kind:
        return
    available = [o for o in state.get('mercenaries',[]) if not o.get('busy_mission_id') and o.get('recovering_until',0) <= time.time()]
    if not available:
        return
    offer = rng.choice(available)
    unit = add_unit(battle,state,offer,'player' if kind=='friendly' else 'enemy',rng,corpse=kind=='corpse',rogue=kind=='hostile')
    if not unit:
        return
    if kind=='corpse':
        state['mercenaries'].remove(offer)
        text = f"You find {unit['name']} dead near the enemy position. Their name is removed from your hiring board."
    else:
        offer['busy_mission_id'] = seed
        analysis.setdefault('mercenary_guest_ids',[]).append(offer['id'])
        if kind=='hostile':
            battle['objectives'].append({'id':'mercenary_threat','name':f"Defeat or subdue {unit['name']}",'required':True,'complete':False})
        text = (f"{unit['name']} has followed the fighting here and offers help." if kind=='friendly' else
                f"{unit['name']} attacks everyone in sight. Defeat or subdue them before leaving with a victory. Escaping while they remain a threat fails the contract.")
    battle['mercenary_notice'] = {'id':f'{seed}:{kind}', 'title':'A hired sword has arrived' if kind!='corpse' else 'A familiar fallen sword', 'text':text}
    battle['log'].append(text)


def betrayal_battle(state, party_ids, traitors, seed):
    from .combat import create_contract_battle, _player_unit, _advance_to_player
    # Reuse the authored road geometry; this isn't a public mission template.
    allies = [cid for cid in party_ids if cid not in traitors]
    battle = create_contract_battle(state,allies,seed,'highway_ambush',defer_start=True)
    enemy_tiles = [dict(x=u['x'],y=u['y']) for u in battle['units'].values() if u['team']=='enemy']
    spawn = battle.get('spawn_zones',{}).get('enemy',enemy_tiles)
    battle['units'] = {uid:u for uid,u in battle['units'].items() if u['team']=='player'}
    for index, mid in enumerate(traitors):
        tile = spawn[index % len(spawn)]
        c = next(c for c in state['characters'] if c['id']==mid)
        u = _player_unit(state,c,tile['x'],tile['y'])
        u.update(team='enemy',mercenary_id=mid,mercenary_hostile=True,mercenary_hostile_all=False,
                 corpse_item=None,corpse_item_chance=0,corpse_gold=(0,0),loyalty=100)
        battle['units'][mid] = u
    for u in battle['units'].values():
        if u['id'] in party_ids and u['id'].startswith('merc_'):
            u['mercenary_id']=u['id']
    battle.update(primary_target_id=traitors[0],turn_order=sorted(battle['units'],key=lambda uid:(-battle['units'][uid]['initiative'],uid)),
                  mercenary_interlude=True,leader_target=False,capture_bonus=False,
                  encounter_id='mercenary_betrayal',name='The hired swords turn')
    battle['objectives']=[{'id':'turncoats','name':'Stop the turncoats or escape to continue the contract','required':True,'complete':False},
                          {'id':'standing','name':'Keep every ally standing','required':False,'complete':False}]
    battle['log']=['The hired swords block the road and demand your purse.']
    battle['mercenary_notice']={'id':seed+':betrayal','title':'Your hired swords turn on you',
                              'text':'They demand your purse. Stop them or escape. Surviving this encounter lets you continue the original contract; the hiring fee is already spent.'}
    _advance_to_player(battle)
    return battle
