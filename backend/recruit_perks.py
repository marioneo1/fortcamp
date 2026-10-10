"""Persistent recruit backgrounds; event-driven effects, never polling grants."""
from copy import deepcopy
import random

DEFINITIONS = {
    "rider": ("Rider", "Ride allied mounts to gain their movement, protection and special techniques; losing a mount risks a damaging fall."),
    'cunning_trapper': ('Cunning Trapper', 'On defeat, leaves a legal three-cell tripwire; prefers keeping it off the killer.'),
    'intimidating': ('Intimidating', 'Your first kill each battle reduces nearby enemies’ damage by 15% through their next turn.'),
    'sly_survivor': ('Sly Survivor', 'Once per battle, surviving a hit below 25% HP makes enemies prefer other targets until you act.'),
    'resourceful_slinger': ('Resourceful Slinger', 'Once per activation, a ranged weapon hit on metal armor or machinery ricochets a half-power shot into a nearby enemy.'),
    'opportunistic_leader': ('Opportunistic Leader', 'Once per battle, the first ally attacking your current target makes an additional legal Basic Attack.'),
    'defiant': ('Defiant', 'Once per battle, becoming your deployed party’s last conscious fighter grants a 20% max-HP Barrier for two turns; never triggers solo.'),
    'relentless_pursuer': ('Relentless Pursuer', 'Once per activation, hitting an enemy who used a movement skill since your previous turn adds Hobble.'),
    'lumberjack': ('Lumberjack', 'Produces one extra wood per hour while assigned to a lumber mill.'),
    'quarry_worker': ('Quarry Worker', 'Produces one extra stone per hour while assigned to a quarry.'),
    'salvager': ('Salvager', 'Produces one extra scrap per hour while assigned to a salvage yard.'),
    'poison_tolerant': ('Poison Tolerant', 'Ignores the first incoming Poison stack once per battle.'),
    'fast_builder': ('Fast Builder', 'Adds one preparation point to defense quests while deployed.'),
    'strong_armed': ('Strong-Armed', '+2 STR, −1 AGI.'),
    'nimble': ('Nimble', '+2 AGI, −1 STR.'),
    'bookish': ('Bookish', '+2 INT, −1 STR.'),
    'steady_handed': ('Steady-Handed', '+2 DEX, −1 AGI.'),
}
ATTRIBUTES = {'strong_armed':{'str':2,'agi':-1},'nimble':{'agi':2,'str':-1},
              'bookish':{'int':2,'str':-1},'steady_handed':{'dex':2,'agi':-1}}
from . import general_perks as general
DEFINITIONS.update(general.DEFINITIONS)
ATTRIBUTES.update({key:effects['attributes'] for key,effects in general.EFFECTS.items() if 'attributes' in effects})
PRODUCTION = {'wood':'lumberjack', 'stone':'quarry_worker', 'scrap':'salvager'}
ROLE = {'trapper':'cunning_trapper','enforcer':'intimidating','skirmisher':'sly_survivor',
        'lookout':'resourceful_slinger','light_lookout':'resourceful_slinger',
        'ringleader':'opportunistic_leader','bruiser':'defiant','warden':'relentless_pursuer'}

def has(unit, key):
    return key in unit.get('traits', []) or key in unit.get('origin_perks', []) or bool(unit.get('perk_modifiers', {}).get(key))

def opposed(battle, a, b):
    from .combat_conditions import hostile_units
    a=battle.get('units',{}).get(a.get('id'),a)
    if 'team' not in a:return False
    return any(u['id']==b['id'] for u in hostile_units(battle,a,battle['units'].values()))

def assign(recruit, mission, role, seed):
    rng = random.Random(f'{seed}:background:{mission}:{recruit.get("combat_specialization")}')
    opening=rng.random()
    gifted=opening<.000001 and general.compatible(recruit.get('traits',[]),'naturally_gifted')
    if opening<.2 and not gifted:
        recruit.setdefault('traits',[])
        return
    if gifted:perks=['naturally_gifted']
    elif rng.random()<.2:
        generic=general.roll(recruit.get('traits',[]),rng,job_id=recruit.get('job_id'),encounter=True)
        perks=[generic or rng.choice(['strong_armed','nimble','bookish','steady_handed'])]
    else:perks=[ROLE[role]] if role in ROLE else []
    if mission in {'tool_shed','ruined_well','supply_watch'}:
        pool=list(PRODUCTION.values());rng.shuffle(pool)
        roll=rng.random();perks += pool[:3 if roll<.001 else 2 if roll<.01 else 1]
    elif mission=='herbs_wall':perks.append('poison_tolerant')
    elif mission=='timber_creek':perks.append('fast_builder')
    recruit['traits']=general.extend(recruit.get('traits', []),perks)

def clear_ruse(unit):
    unit['statuses']=[s for s in unit.get('statuses',[]) if s['id']!='feigned_death']

def traits(unit):
    return [{'id':'background:'+key,'name':name,'description':description,'type':'passive',
             'source_kind':'background','source_name':'Background','modifiers':{}}
            for key,(name,description) in DEFINITIONS.items() if has(unit,key)]

def decorate_enemy(unit, recruit):
    _,roll=general.battle_character({**recruit,'id':unit['id']},unit.get('perk_battle_seed',unit['id']))
    if roll:unit['battle_attribute_roll']=roll
    unit['origin_perks']=list(recruit.get('traits',[]))
    unit.setdefault('passives',[]).extend(traits(unit))
    changes={}
    for key in unit['origin_perks']:
        for stat,value in ATTRIBUTES.get(key,{}).items():changes[stat]=changes.get(stat,0)+value
    if roll:changes[roll['attribute']]=changes.get(roll['attribute'],0)+roll['amount']
    for stat,field in [('str','strength'),('agi','agility'),('int','intelligence')]:
        unit[field]=max(1,unit.get(field,4)+changes.get(stat,0))
    unit['initiative']+=changes.get('agi',0)
    scaling='dex' if unit.get('attack_elevation_rule')=='ballistic' else 'str'
    base=recruit.get('attributes',{}).get(scaling,4)
    unit['attack']=max(1,unit['attack']+(base+changes.get(scaling,0))//2-base//2)
    combat={}
    for key in unit['origin_perks']:
        for stat,value in general.EFFECTS.get(key,{}).get('combat',{}).items():combat[stat]=combat.get(stat,0)+value
    unit.setdefault('perk_modifiers',{}).update(combat)
    hp=changes.get('vit',0)*4+combat.get('hp',0)
    unit['hp']=unit['max_hp']=max(1,unit['max_hp']+hp)
    unit['move']=max(1,unit['move']+combat.get('move',0))
    unit['evasion']=max(0,unit.get('evasion',0)+combat.get('evasion',0))
    unit['initiative']+=combat.get('initiative',0)
    unit['displacement_resistance']=max(unit.get('displacement_resistance',0),combat.get('displacement_resistance',0))
    if recruit.get('job_id')=='ranger' and unit.get('attack_elevation_rule')=='ballistic':
        unit['attack_range']=max(1,unit['attack_range']+combat.get('ranged_range',0))

def prefer_targets(targets):
    normal=[u for u in targets if not any(s['id']=='feigned_death' for s in u.get('statuses', []))]
    return normal or targets

def damage_factor(unit):
    return .85 if any(s['id']=='intimidated' for s in unit.get('statuses', [])) else 1

def movement(battle, unit):
    clear_ruse(unit)
    last=next((e for e in reversed(battle.get('animation_events',[])) if e.get('type')=='movement' and e.get('unit_id')==unit['id']),None)
    if last and not last.get('background_noted') and (last.get('mode') in {'dash','teleport','leap'} or any(last.get(k) for k in ('dash','teleport','leap'))):
        last['background_noted']=True
        battle['perk_mobility_serial']=battle.get('perk_mobility_serial',0)+1
        unit['perk_mobility_serial']=battle['perk_mobility_serial']

def finish(battle, unit):
    unit.pop('unarmed_perk_spent',None)
    unit['pursuer_since']=battle.get('perk_mobility_serial',0)
    unit.pop('pursuer_used',None);unit.pop('ricochet_used',None)

def fallen_trap(battle, victim, killer):
    from . import combat as c
    choices=[]
    for dx,dy in ((1,0),(0,1)):
        for offset in range(3):
            cells=[{'x':victim['x']+(i-offset)*dx,'y':victim['y']+(i-offset)*dy} for i in range(3)]
            legal=all(0<=p['x']<battle['width'] and 0<=p['y']<battle['height'] and not c.tactics.pit_at(battle,p['x'],p['y']) and c._ground_at(battle,p['x'],p['y'])[0]!='water' and
                not any(c.crossed_walls(battle,(cells[i]['x'],cells[i]['y']),(cells[i+1]['x'],cells[i+1]['y'])) for i in range(2)) and
                not c._blocked(battle,p['x'],p['y'],next((u['id'] for u in battle['units'].values() if (u['x'],u['y'])==(p['x'],p['y']) and c._combat_active(u)),victim['id'])) for p in cells)
            if legal:choices.append(cells)
    if not choices:return
    choices.sort(key=lambda cells:(any((p['x'],p['y'])==(killer.get('x'),killer.get('y')) for p in cells),
                                    sum(c._combat_active(u) and opposed(battle,victim,u) and any((p['x'],p['y'])==(u['x'],u['y']) for p in cells) for u in battle['units'].values())))
    zone=c.spaces.place_zone(battle,victim,{'zone':'tripline','turns':3},choices[0])
    if not zone:return
    zone.update(persistent_defeat_trap=True,expires_round=battle.get('round',1)+3)
    from .enemy_specialties import effect
    effect(battle,victim,'tripline_set',zone_snapshot=deepcopy(zone))
    c._record_sound(battle,'specialty_tripline_set')
    for enemy in list(battle['units'].values()):
        if c._combat_active(enemy) and opposed(battle,victim,enemy):c._trigger_zones(battle,enemy,'entry',zone['id'])

def after_damage(battle, attacker, target, previous_hp, damage):
    from . import combat as c
    from . import combat_conditions as conditions
    from .combat_feedback import record as feedback
    attacker=battle['units'].get(attacker.get('id'),attacker)
    if damage>0 and target['hp']>0 and target['hp']<=target['max_hp']*.25 and has(target,'sly_survivor') and not target.get('ruse_used'):
        target['ruse_used']=True;target.setdefault('statuses',[]).append({'id':'feigned_death'})
        feedback(battle,target,'status',status_id='feigned_death')
    if previous_hp<=0 or target['hp']>0:return
    if has(target,'cunning_trapper') and not target.get('defeat_trap_used'):
        target['defeat_trap_used']=True;fallen_trap(battle,target,attacker)
    if target.get('condition')=='dead' and opposed(battle,attacker,target) and has(attacker,'intimidating') and not attacker.get('example_used') and c._combat_active(attacker):
        attacker['example_used']=True
        for enemy in c.conditions.hostile_units(battle,attacker,battle['units'].values()):
            if c._combat_active(enemy) and c._distance(enemy,target)<=2:
                conditions.apply(enemy,'intimidated',1,attacker);feedback(battle,enemy,'status',status_id='intimidated')
    # Genuine deployed companions only: summons, protected NPCs and extraction do not manufacture this perk.
    if target.get('temporary') or target.get('kind')=='protected':return
    team=[u for u in battle['units'].values() if u.get('team')==target.get('team') and not u.get('temporary') and u.get('kind')!='protected']
    remaining=[u for u in team if c._combat_active(u)]
    if len(team)>1 and len(remaining)==1:
        survivor=remaining[0]
        if has(survivor,'defiant') and not survivor.get('defiant_used'):
            survivor['defiant_used']=True;conditions.barrier(survivor,max(1,round(survivor['max_hp']*.2)),2,survivor)
            feedback(battle,survivor,'status',status_id='barrier')

def after_attack(battle, actor, target, hit, damage, reaction=False):
    from . import combat as c
    from .combat_feedback import record as feedback
    if reaction or battle.get('background_extra_attack'):return
    real=battle['units'].get(actor['id'],actor);real['current_target_id']=target['id']
    if hit and c._combat_active(target) and has(real,'relentless_pursuer') and not real.get('pursuer_used') and target.get('perk_mobility_serial',0)>real.get('pursuer_since',0):
        real['pursuer_used']=True;c.conditions.add_stack(target,'hobbled',2,real)
        feedback(battle,target,'status',status_id='hobbled')
    if hit and has(real,'resourceful_slinger') and not real.get('ricochet_used') and actor.get('attack_elevation_rule')=='ballistic' and (target.get('armor_material') in {'plate','chain','metal'} or target.get('engineer_machine') or c.impact_surface(target)=='metal'):
        choices=[u for u in c.conditions.hostile_units(battle,real,battle['units'].values()) if u['id']!=target['id'] and c._combat_active(u) and c._distance(u,target)<=2 and c._line_of_sight(battle,target,u)]
        if choices:
            real['ricochet_used']=True;other=min(choices,key=lambda u:(c._distance(u,target),str(u['id'])))
            source={**real,'x':target['x'],'y':target['y'],'attack':max(1,round(real['attack']*.5))}
            battle['background_extra_attack']=True
            try:c._perform_attack(battle,source,other,'ballistic',reaction=True)
            finally:battle.pop('background_extra_attack',None)
            battle['log'].append(f"{real['name']}'s shot ricochets toward {other['name']}.")
    if not c._combat_active(target) or not c._combat_active(real):return
    leaders=[u for u in battle['units'].values() if u['id']!=real['id'] and u.get('team')==real.get('team') and c._combat_active(u) and has(u,'opportunistic_leader') and not u.get('leader_used') and u.get('current_target_id')==target['id']]
    if leaders and c._can_attack(battle,real,target) and c.bard.can_attack(real) and not c.conditions.has(real,'disarm'):
        for leader in leaders:leader['leader_used']=True
        battle['background_extra_attack']=True
        try:c._perform_attack(battle,real,target,real.get('attack_elevation_rule','melee'))
        finally:battle.pop('background_extra_attack',None)
        battle['log'].append(f"{real['name']} follows the opening with an extra Basic Attack.")
