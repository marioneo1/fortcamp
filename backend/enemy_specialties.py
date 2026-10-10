"""Recruitable enemy techniques; bounded board rules using existing primitives."""
from copy import deepcopy
import random

KINDS = {'tripline','shakedown','parting_cut','ankle_bite','goliath_shot','tag_team','heel_cut'}


def register(active, passive, skills):
    rows = [
        ('tripline','Tripline','Lay a three-cell tripline that Hobbles the first enemy to cross it, then snaps.',100,3,4),
        ('shakedown','Shakedown','Strike one enemy for double weapon damage.',200,1,2),
        ('parting_cut','Parting Cut','Strike for 125% weapon damage, then retreat one tile if the way is clear.',125,1,0),
        ('ankle_bite','Ankle Bite','Strike and Hobble; beside another ally, deal 175% damage and apply two Hobble stacks.',100,1,3),
        ('goliath_shot','Goliath Shot','Fire a heavy shot with 75% Stun chance; the target takes 25% more sword damage through its next turn.',100,3,4),
        ('tag_team','Tag Team!','Swap with an ally, gain 25% damage through your next turn, and Stun enemies crossed between you.',100,3,4),
        ('heel_cut','Heel Cut','Strike for 150% damage and Bleed; each new tile farther from the wound adds a Bleed stack and damage tick through the target’s next turn.',150,1,4),
    ]
    for kind,name,description,power,reach,cd in rows:
        key='npc:bandit:'+kind
        if kind=='tripline':
            skill=active(key,name,description,[{'type':'rogue_utility','kind':'caltrops'}],range=3,cooldown=cd)
            skill['rogue_kind']='caltrops'
        elif kind=='tag_team':
            skill=active(key,name,description,[{'type':'guard'}],target='ally',range=reach,cooldown=cd)
        else:
            skill=active(key,name,description,[{'type':'attack','power_percent':power}],range=reach,
                         rule='ballistic' if kind=='goliath_shot' else 'melee',cooldown=cd)
        skill.update(npc_kind=kind,source_name='Enemy specialty')
        skills[key]=skill
    key='npc:bandit:cornered_fury'
    skills[key]=passive(key,'Cornered Fury','Below half HP, single-hit weapon attacks also strike every other adjacent cardinal enemy.')
    skills[key]['source_name']='Warband Bruiser'


def has(unit,key):
    return any(p.get('id')=='npc:bandit:'+key for p in unit.get('passives',[]))


def adapt(battle,actor,target,skill):
    from . import combat as c
    result=deepcopy(skill)
    if skill.get('npc_kind')=='ankle_bite':
        assisted=any(u['id']!=actor['id'] and u.get('team')==actor.get('team') and c._combat_active(u)
                     and abs(u['x']-target['x'])+abs(u['y']-target['y'])==1
                     and not c.crossed_walls(battle,(u['x'],u['y']),(target['x'],target['y']))
                     for u in battle['units'].values())
        result['effects'][0]['power_percent']=175 if assisted else 100
        result['npc_hobble_stacks']=2 if assisted else 1
    return result


def effect(battle,unit,kind,packet=None,**extra):
    event={'type':'martial_effect','skill':'specialty_'+kind,'unit_id':unit['id'],
           'x':unit['x'],'y':unit['y'],**extra}
    if packet is not None:event['attack_packet']=packet
    battle.setdefault('animation_events',[]).append(event)


def status(battle,actor,target,sid,chance=100,stacks=1):
    from . import combat as c
    if not c._combat_active(target):return
    serial=battle.get('proc_counter',0);battle['proc_counter']=serial+1
    roll=random.Random(f"{battle.get('seed')}:specialty:{serial}:{actor['id']}:{target['id']}:{sid}").randint(1,100)
    if roll>c.conditions.status_chance(target,sid,chance):return
    for _ in range(stacks):
        if sid in {'bleed','hobbled'}:c.conditions.add_stack(target,sid,1,actor)
        else:c.conditions.apply(target,sid,1,actor)
    c.feedback(battle,target,'status',status_id=sid,attack_packet=battle.get('attack_serial'))


def landed(battle,actor,target,skill,packet):
    from . import combat as c
    kind=(skill or {}).get('npc_kind')
    if kind not in KINDS:return
    effect(battle,target,kind,packet)
    c._record_sound(battle,'specialty_'+kind,offset=185 if kind=='parting_cut' else 0)
    battle['animation_events'][-1]['attack_packet']=packet
    if kind=='ankle_bite':status(battle,actor,target,'hobbled',stacks=skill.get('npc_hobble_stacks',1))
    if kind=='goliath_shot':
        status(battle,actor,target,'stun',75)
        if c._combat_active(target):
            c.conditions.apply(target,'sword_exposed',1,actor)
            c.feedback(battle,target,'status',status_id='sword_exposed',attack_packet=packet)
    if kind=='heel_cut':
        status(battle,actor,target,'bleed')
        if c._combat_active(target):
            c.conditions.apply(target,'heel_wound',1,actor)
            wound=next(s for s in target['statuses'] if s['id']=='heel_wound')
            wound.update(origin={'x':target['x'],'y':target['y']},distance_paid=0)
            c.feedback(battle,target,'status',status_id='heel_wound',attack_packet=packet)


def retreat(battle,actor,target,packet=None):
    from . import combat as c
    if not c.rogue.mobile(actor):return
    dx,dy=actor['x']-target['x'],actor['y']-target['y']
    step=(1 if dx>0 else -1,0) if abs(dx)>=abs(dy) else (0,1 if dy>0 else -1)
    start={'x':actor['x'],'y':actor['y']};x,y=actor['x']+step[0],actor['y']+step[1]
    if not c._can_step(battle,actor['x'],actor['y'],x,y,actor):return
    actor.setdefault('zone_location',[actor['x'],actor['y']])
    actor.update(x=x,y=y,moved=True,exit_ready=False)
    events=battle.setdefault('animation_events',[])
    attack=next((e for e in reversed(events) if e.get('type')=='melee_attack' and e.get('attacker_id')==actor['id'] and e.get('parting_cut')),None)
    if attack:packet=attack.get('attack_packet')
    # Reactions retain their own ordering. Only fuse an uninterrupted slash;
    # a counter/displacement cannot be erased or jump the token back mid-skid.
    after=events[events.index(attack)+1:] if attack else []
    fuse=bool(attack and attack.get('from')==start and not any(
        e.get('type')=='melee_attack' and e.get('target_id')==actor['id'] or
        e.get('type') in {'movement','collision_recoil','death_burst','knockout'} and e.get('unit_id')==actor['id']
        for e in after))
    movement={'type':'movement','unit_id':actor['id'],'points':[start,{'x':x,'y':y}],'dash':True,'skid_back':True}
    if fuse:
        movement.update(attack_packet=packet,parting_cut=True)
        attack['parting_retreat']={'x':x,'y':y}
    events.append(movement)
    c._apply_tile_entry(battle,actor)
    effect(battle,actor,'retreat',packet if fuse else None,from_point=start,to_point={'x':x,'y':y},skid_back=True)


def crossing(battle,actor,ally):
    x,y,x1,y1=actor['x'],actor['y'],ally['x'],ally['y']
    dx,dy=abs(x1-x),abs(y1-y);sx=1 if x<x1 else -1;sy=1 if y<y1 else -1
    error=dx-dy;cells=[]
    while True:
        cells.append((x,y))
        if (x,y)==(x1,y1):return cells
        e=2*error
        if e>-dy:error-=dy;x+=sx
        if e<dx:error+=dx;y+=sy


def swap_legal(battle,actor,ally):
    from . import combat as c
    if not ally or ally['id']==actor['id'] or ally.get('team')!=actor.get('team') or not c.rogue.mobile(actor) or not c.rogue.mobile(ally):return False
    if c._distance(actor,ally)>3 or not c._line_of_sight(battle,actor,ally):return False
    probe={**battle,'units':{k:u for k,u in battle['units'].items() if k not in {actor['id'],ally['id']}}}
    return all(c.rogue.legal_land(probe,u,v['x'],v['y']) for u,v in ((actor,ally),(ally,actor)))


def tag_team(battle,actor,ally,skill):
    from . import combat as c
    if not swap_legal(battle,actor,ally):raise ValueError('Choose a mobile ally within three cells and clear sight')
    cells=crossing(battle,actor,ally)
    c._commit_player_movement(battle,actor)
    if not c._combat_active(actor):return
    c.abilities.spend(actor,skill)
    starts={u['id']:{'x':u['x'],'y':u['y']} for u in (actor,ally)}
    actor.update(x=starts[ally['id']]['x'],y=starts[ally['id']]['y'])
    ally.update(x=starts[actor['id']]['x'],y=starts[actor['id']]['y'])
    for u in (actor,ally):
        u.update(moved=True,exit_ready=False)
        u.pop('movement_origin',None);u.pop('movement_path',None)
        u['zone_location']=[starts[u['id']]['x'],starts[u['id']]['y']]
        battle.setdefault('animation_events',[]).append({'type':'movement','unit_id':u['id'],
            'points':[starts[u['id']],{'x':u['x'],'y':u['y']}],'teleport':True})
        c._apply_tile_entry(battle,u)
    for enemy in battle['units'].values():
        if enemy in c.conditions.hostile_units(battle,actor,battle['units'].values()) and (enemy['x'],enemy['y']) in cells:
            status(battle,actor,enemy,'stun')
    c.conditions.apply(actor,'tag_team_power',1,actor)
    c.feedback(battle,actor,'status',status_id='tag_team_power')
    effect(battle,actor,'tag_team',from_point=starts[actor['id']])
    c._record_sound(battle,'specialty_tag_team',offset=0)
    actor['acted']=True


def entry(battle,unit):
    from . import combat as c
    wound=next((s for s in unit.get('statuses',[]) if s['id']=='heel_wound'),None)
    if not wound or not c._combat_active(unit):return
    origin=wound['origin'];distance=abs(unit['x']-origin['x'])+abs(unit['y']-origin['y'])
    delta=max(0,distance-wound.get('distance_paid',0))
    if not delta:return
    wound['distance_paid']=distance
    # Use the shared Bleed calculation and mitigation, without consuming layers.
    from . import combat_dots as dots
    source=battle['units'].get(wound.get('source_id'),unit)
    for _ in range(delta):
        if not c._combat_active(unit):break
        c.conditions.add_stack(unit,'bleed',1,source)
        bleed=next(s for s in unit['statuses'] if s['id']=='bleed')
        amount=dots.base_damage(unit,'bleed',dots.count(bleed))
        packet_source={**source,'attack':amount,'status_tick':True,'percent_dot':'bleed','element':None,'on_hit':None}
        c._deal_damage(battle,packet_source,unit,armor_pierce=c._effective_armor(unit))
    battle['log'].append(f"{unit['name']}'s Heel Cut bleeds after moving {delta} more tile(s).")
    effect(battle,unit,'heel_cut')


def extra_targets(battle,actor,target,skill=None,reaction=False):
    from . import combat as c
    if reaction or actor.get('specialty_sweep') or not has(actor,'cornered_fury') or actor['hp']>=actor['max_hp']/2:return []
    if skill and (not any(e['type']=='attack' and e.get('hits',1)==1 for e in skill.get('effects',[])) or skill.get('combo_kind') or skill.get('mage_kind') or skill.get('ranger_kind')):return []
    enemies=[u for u in c.conditions.hostile_units(battle,actor,battle['units'].values()) if c._combat_active(u)
             and abs(u['x']-actor['x'])+abs(u['y']-actor['y'])==1
             and not c.crossed_walls(battle,(actor['x'],actor['y']),(u['x'],u['y']))]
    if len(enemies)<2:return []
    return [u for u in enemies if u['id']!=target['id']]


def auto(battle,actor,target):
    from . import combat as c
    skills=[s for s in actor.get('skills',[]) if s.get('npc_kind') and c.abilities.availability(actor,s)['available']]
    for skill in skills:
        kind=skill['npc_kind']
        if kind=='tag_team':
            hostiles=c.conditions.hostile_units(battle,actor,battle['units'].values())
            allies=[u for u in battle['units'].values() if swap_legal(battle,actor,u)
                    and any((e['x'],e['y']) in crossing(battle,actor,u) for e in hostiles)]
            if allies:tag_team(battle,actor,allies[0],skill);return True
        elif kind=='tripline':
            if any(z['kind']=='tripline' and z['owner_id']==actor['id'] for z in battle.get('zones',[])):continue
            dx=1 if target['x']>actor['x'] else -1 if target['x']<actor['x'] else 0
            dy=1 if target['y']>actor['y'] else -1 if target['y']<actor['y'] else 0
            x,y=actor['x']+dx*2,actor['y']+dy*2
            if c._distance(actor,target)<=2:continue
            rotation=1 if abs(target['x']-actor['x'])>=abs(target['y']-actor['y']) else 0
            if c.rogue.strip(battle,actor,x,y,rotation):
                c.rogue.utility_command(battle,actor,skill,{'x':x,'y':y,'rotation':rotation});return True
        elif c._can_attack(battle,actor,target,skill['range']):
            c._resolve_ability(battle,actor,target,skill);actor['acted']=True;return True
    return False
