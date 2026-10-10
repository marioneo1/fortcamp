"""Defense preparation reuses real Job deployments and committed movement hooks."""
import math

from . import combat_conditions as conditions, combat_engineer as engineer
from .combat_feedback import record as feedback


def options(units):
    party = [u for u in units.values() if u['team'] == 'player' and not u.get('defense_objective')]
    has_engineer = any(u.get('job_id') == 'engineer' for u in party)
    result = [
        {'id':'barricade','name':'Barricade','cost':1,'description':'Blocks walking but leaves a firing lane; 12 HP.'},
        {'id':'palisade','name':'Palisade','cost':1,'description':'Blocks walking and sight; 18 HP.'},
        {'id':'wall','name':'Stone Wall','cost':1,'description':'Armored cover blocks walking and sight; 18 HP.'},
        {'id':'pit','name':'Trap Pit','cost':2,'description':'An enemy falls for 25% max HP damage and loses movement and attacks; climbing out costs an action.'},
        {'id':'proximity_dynamite','name':'Proximity Dynamite','cost':2 if has_engineer else 3,
         'description':'Explodes when anyone comes within one cell, dealing explosive damage and pushing nearby units one cell.'},
    ]
    for unit in party:
        if unit.get('job_id') == 'engineer':
            unit['defense_mine_limit'] = 1
            kinds = {s.get('engineer_kind') for s in unit.get('skills', [])}
            for kind, name, limit, description in [
                ('sentry_turret','Sentry Turret',3,'Ready to fire; shares the Engineer’s three Sentry slots.'),
                ('heavy_emplacement','Heavy Emplacement',1,'Ready to fire; shares the Engineer’s one Heavy slot.'),
                ('proximity_charge','Engineer Mine',1,'One armed mine; anyone within one cell triggers its disruption.'),
                ('dynamite','Timed Dynamite',None,'Explodes at this Engineer’s next activation after their first turn.'),
            ]:
                if kind in kinds:
                    option={'id':f"job:{unit['id']}:{kind}",'name':name,'cost':0,'owner_id':unit['id'],
                            'deploy_kind':kind,'description':description,'owner_name':unit['name']}
                    if limit is not None:option['limit']=limit
                    result.append(option)
        if unit.get('job_id') == 'rogue' and any(s.get('id') == 'job:rogue:caltrops' for s in unit.get('skills', [])):
            result.append({'id':f"job:{unit['id']}:caltrops",'name':'Caltrops','cost':0,'owner_id':unit['id'],
                           'owner_name':unit['name'],'deploy_kind':'caltrops','footprint':[3,1],
                           'description':'A rotatable three-cell strip applies Bleed and Hobble on entry for two Rogue turns.'})
    return result


def cells(definition, x, y, vertical=False):
    if definition.get('deploy_kind') == 'caltrops':
        return [{'x':x + (0 if vertical else n),'y':y + (n if vertical else 0)} for n in (-1,0,1)]
    return [{'x':x,'y':y}]


def place(battle, command):
    from . import combat as c
    prep=battle['preparation']
    definition=c._placement_definition(prep,str(command.get('placement_id','')))
    x,y=int(command.get('x',-1)),int(command.get('y',-1))
    footprint=cells(definition,x,y,command.get('vertical',False))
    legal=c._preparation_cell_set(prep,'zone')
    if any((p['x'],p['y']) not in legal for p in footprint):raise ValueError('Keep the entire defense inside the highlighted zone')
    if prep['remaining'] < definition['cost']:raise ValueError('Not enough preparation points')
    owner=battle['units'].get(definition.get('owner_id'))
    kind=definition.get('deploy_kind')
    if kind:
        skill_kind='rogue_kind' if kind=='caltrops' else 'engineer_kind'
        if not owner or not c._combat_active(owner) or not any(s.get(skill_kind)==kind and (kind!='caltrops' or s.get('id')=='job:rogue:caltrops') for s in owner.get('skills', [])):
            raise ValueError('The equipped deployment skill is no longer available')
        if kind in engineer.BUILDS and sum(u['machine_kind']==kind for u in engineer.machines(battle,owner)) >= engineer.BUILDS[kind][0]:
            raise ValueError('All turret deployment slots are occupied')
        if kind=='proximity_charge' and sum(h['kind']=='mine' and h['owner_id']==owner['id'] for h in battle.get('engineer_hazards', [])) >= 1:
            raise ValueError('This Engineer already has an armed mine')
    for p in footprint:
        if c._blocked(battle,p['x'],p['y']) or c.tactics.pit_at(battle,p['x'],p['y']) or c._ground_at(battle,p['x'],p['y'])[0]=='water':
            raise ValueError('Choose empty, solid ground')
        if any((p['x'],p['y']) in occupied for occupied in (
            {(q['x'],q['y']) for q in row.get('cells', [row])} for row in prep.get('placements',[]))):
            raise ValueError('A prepared defense already occupies that tile')
    if definition['id']=='proximity_dynamite' or kind=='proximity_charge':
        if any(max(abs(u['x']-x),abs(u['y']-y))<=1 and c._line_of_sight(battle,{'x':x,'y':y},u)
               for u in c._living(battle,'enemy')):raise ValueError('Do not place an armed explosive touching an enemy')
    prep['serial']=prep.get('serial',0)+1
    uid=f"prepared_defense_{prep['serial']}"
    row={'id':uid,'type':definition['id'],'name':definition['name'],'cost':definition['cost'],
         'x':x,'y':y,'cells':footprint,'owner_id':definition.get('owner_id')}
    if kind in engineer.BUILDS:
        unit=engineer.spawn(battle,owner,kind,{'x':x,'y':y})
        row['unit_id']=unit['id']
    elif kind=='caltrops':
        old=list(battle.get('zones',[]))
        zone=c.spaces.place_zone(battle,owner,{'zone':'caltrops','turns':3},footprint)
        zone['prepared_defense']=True
        battle['zones']=old+[zone]
        row['zone_id']=zone['id']
    elif kind in {'proximity_charge','dynamite'} or definition['id']=='proximity_dynamite':
        if owner is None:owner=next(u for u in battle['units'].values() if u['team']=='player' and not u.get('defense_objective'))
        battle['engineer_hazard_serial']=battle.get('engineer_hazard_serial',0)+1
        h={'id':f"engineer_hazard_{battle['engineer_hazard_serial']}",'owner_id':owner['id'],'team':owner['team'],
           'kind':'mine' if kind=='proximity_charge' else 'dynamite','x':x,'y':y,
           'placed_at':engineer.clock(owner),'placed_round':battle.get('round',1),'throw_origin':{'x':owner['x'],'y':owner['y']},
           'prepared_defense':True}
        if h['kind']=='dynamite':
            h['power']=owner['attack']*2
            if definition['id']=='proximity_dynamite':h['proximity_trigger']=True
            else:h['expires_at']=engineer.clock(owner)+2
        battle.setdefault('engineer_hazards',[]).append(h)
        row['hazard_id']=h['id']
    else:
        wall=definition['id']=='wall'
        palisade=definition['id']=='palisade'
        pit=definition['id']=='pit'
        tile={'id':uid,'name':definition['name'],'x':x,'y':y,'kind':'pit' if pit else definition['id'],
              'sprite':'terrain:pit_deep_earthen' if pit else 'structure:stone_wall_straight' if wall else 'structure:palisade_straight' if palisade else 'structure:wooden_barricade',
              'blocking':not pit,'blocks_sight':wall or palisade,'prepared_defense':True,
              'destructible':not pit,'hp':0 if pit else 18 if wall or palisade else 12,
              'max_hp':0 if pit else 18 if wall or palisade else 12,'armor':2 if wall else 1,
              'destroyed_kind':'rubble','destroyed_sprite':'structure:palisade_breached','destroyed_movement_cost':2}
        if pit:tile.update(pit_kind='deep',prepared_pit=True)
        battle.setdefault('terrain',[]).append(tile)
    prep.setdefault('placements',[]).append(row)
    prep['remaining']-=definition['cost']
    battle['log'].append(f"Placed {definition['name']} at {x+1},{y+1}.")


def remove(battle, command):
    prep=battle['preparation']
    row=next((r for r in prep['placements'] if r['id']==command.get('target_id')),None)
    if not row:raise ValueError('Choose a prepared defense to remove')
    prep['placements'].remove(row);prep['remaining']+=row['cost']
    if row.get('unit_id'):battle['units'].pop(row['unit_id'],None)
    battle['zones']=[z for z in battle.get('zones',[]) if z['id']!=row.get('zone_id')]
    battle['engineer_hazards']=[h for h in battle.get('engineer_hazards',[]) if h['id']!=row.get('hazard_id')]
    battle['terrain']=[t for t in battle.get('terrain',[]) if t['id']!=row['id']]
    battle['log'].append(f"Removed {row['name']}; points and deployment slots are restored.")


def pit_entry(battle, unit):
    from . import combat as c
    pit=next((t for t in battle.get('terrain',[]) if t.get('prepared_pit') and not t.get('destroyed')
              and (t['x'],t['y'])==(unit['x'],unit['y'])),None)
    if not pit or unit.get('team')!='enemy' or unit.get('movement_type')=='flying' or c.rogue.trap_expert(unit) or conditions.has(unit,'pit_trapped'):
        return
    source={'id':pit['id'],'name':'Trap Pit','weapon':'Trap Pit','attack':max(1,math.ceil(unit['max_hp']*.25)),
            'status_tick':True,'environmental_fall':True}
    c._deal_damage(battle,source,unit,armor_pierce=unit.get('armor',0))
    if c._combat_active(unit):
        unit.setdefault('statuses',[]).append({'id':'pit_trapped'})
        unit['defense_pit']=True
        unit['engineer_interrupted']=True
        unit['acted']=True
        feedback(battle,unit,'status',status_id='pit_trapped')
    battle['log'].append(f"{unit['name']} falls into a trap pit; climbing out takes a main action.")
