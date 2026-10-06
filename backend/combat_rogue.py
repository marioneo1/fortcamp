"""Bounded Rogue position, quick-action and placement rules."""
from copy import deepcopy
from . import combat_conditions as conditions
from . import combat_abilities as abilities
from .combat_feedback import record as feedback

KINDS={'cheap_shot','crippling_cut','exploit_weakness','shadowstep','caltrops','backflip','throwing_knife'}
NEGATIVE={'pestilence','bleed','hobbled','poison','burn','blind','slow','stun','sleep','freeze','bind','paralyze','fear','mute','armor_fracture','vulnerable','mark','open_guard','panic','pit_trapped','palm_exposure','charm','confuse','berserk','reckless_exposure'}
UTILITY={'shadowstep','backflip','caltrops','throwing_knife'}

def active(u):return u.get('alive',True) and u.get('conscious',True) and not u.get('extracted') and not u.get('carried_by')
def trap_expert(u):return any(p.get('id')=='job:rogue:trap_expert' for p in u.get('passives',[]))
def counts(target):
    found={}
    for s in target.get('statuses',[]):
        if s['id'] in NEGATIVE:
            count=len(s['layers']) if 'layers' in s else s.get('stacks',1)
            found[s['id']]=max(found.get(s['id'],0),max(1,int(count)))
    return found

def strike_side(actor,target,thrown=False):
    dx,dy=actor['x']-target['x'],actor['y']-target['y']
    if not thrown:return (dx,dy) if abs(dx)+abs(dy)==1 else None
    return ((1 if dx>0 else -1),0) if abs(dx)>=abs(dy) else (0,1 if dy>0 else -1)

def position_power(battle,actor,target,thrown=False):
    from . import combat as c
    side=strike_side(actor,target,thrown);sides=set()
    if side:sides.add(side)
    for ally in battle['units'].values():
        if ally['id']==actor['id'] or ally['team']!=actor['team'] or not active(ally):continue
        d=(ally['x']-target['x'],ally['y']-target['y'])
        if abs(d[0])+abs(d[1])==1 and not c.crossed_walls(battle,(ally['x'],ally['y']),(target['x'],target['y'])):sides.add(d)
    power=250 if len(sides)>=4 else 220 if len(sides)==3 else 200 if side and (-side[0],-side[1]) in sides else 150 if len(sides)>=2 else 100
    return power,sorted(sides)

def attack_skill(battle,actor,target,skill,thrown=False):
    result=deepcopy(skill);kind=skill.get('rogue_kind')
    if kind=='cheap_shot':power,_=position_power(battle,actor,target,thrown)
    elif kind=='exploit_weakness':power=min(400,100+50*sum(counts(target).values()))
    else:return result
    result['effects'][0]['power_percent']=power
    return result

def freeze_walking(unit):
    unit['rogue_walk_locked']=True
    unit.pop('movement_origin',None);unit.pop('movement_path',None)

def mobile(unit):
    return active(unit) and not unit.get('carrying') and not unit.get('carrying_object') and not unit.get('stationary') and not any(conditions.has(unit,s) for s in {'bind','freeze','pit_trapped','stun','sleep','ambush_sleep'}) and not unit.get('paralyzed_move')

def legal_land(battle,actor,x,y):
    from . import combat as c
    return mobile(actor) and 0<=x<battle['width'] and 0<=y<battle['height'] and not c._blocked(battle,x,y,actor['id'],actor.get('movement_type')) and not c.tactics.pit_at(battle,x,y) and c._ground_at(battle,x,y)[0]!='water'

def landings(battle,actor,target):
    from . import combat as c
    if not mobile(actor) or not active(target) or c.concealment.unseen(target) or c._distance(actor,target)>3 or not c._line_of_sight(battle,actor,target):return []
    return [{'x':target['x']+dx,'y':target['y']+dy} for dx,dy in ((0,-1),(1,0),(0,1),(-1,0))
            if legal_land(battle,actor,target['x']+dx,target['y']+dy) and not c.crossed_walls(battle,(target['x'],target['y']),(target['x']+dx,target['y']+dy))
            and abs(c._tile_height(battle,target['x']+dx,target['y']+dy)-c._tile_height(battle,actor['x'],actor['y']))<=2]

def flips(battle,actor):
    from . import combat as c
    probe={**actor};probe.pop('rogue_walk_locked',None)
    return [{'x':actor['x']+dx*n,'y':actor['y']+dy*n} for dx,dy in ((0,-1),(1,0),(0,1),(-1,0)) for n in range(1,4)
            if legal_land(battle,actor,actor['x']+dx*n,actor['y']+dy*n) and c._leap_eligible(battle,probe,c._ground_target(actor['x']+dx*n,actor['y']+dy*n),{'range':3})]

def strip(battle,actor,x,y,rotation=0):
    from . import combat as c
    if rotation not in (0,1):return []
    center={'x':x,'y':y}
    if c._distance(actor,center)>3 or not c._line_of_sight(battle,actor,center):return []
    cells=[{'x':x+(i if not rotation else 0),'y':y+(i if rotation else 0)} for i in (-1,0,1)]
    for cell in cells:
        cx,cy=cell['x'],cell['y']
        if not (0<=cx<battle['width'] and 0<=cy<battle['height']) or c.tactics.pit_at(battle,cx,cy) or c._ground_at(battle,cx,cy)[0]=='water' or not c._line_of_sight(battle,actor,cell):return []
        if any(t.get('blocking') and not t.get('edge_wall') and not t.get('destroyed') for t in c._terrain_at(battle,cx,cy)):return []
        if any(o.get('blocking',True) and (cx,cy) in c.occupied_tiles(o) for o in battle.get('objects',{}).values() if o.get('state') not in {'destroyed','removed','broken'} and not o.get('carried_by')):return []
    return cells

def utility_command(battle,actor,skill,command):
    from . import combat as c
    if not abilities.availability(actor,skill)['available']:raise ValueError(abilities.availability(actor,skill)['reason'])
    kind=skill['rogue_kind'];target=battle['units'].get(command.get('target_id'))
    x,y=int(command.get('x',-1)),int(command.get('y',-1))
    if kind=='shadowstep':
        if not target or target['team']==actor['team'] or {'x':x,'y':y} not in landings(battle,actor,target):raise ValueError('Choose a visible enemy and a legal adjacent landing')
    elif kind=='backflip':
        if {'x':x,'y':y} not in flips(battle,actor):raise ValueError('Choose a legal cardinal landing one to three cells away')
    elif kind=='caltrops':
        cells=strip(battle,actor,x,y,command.get('rotation',0))
        if not cells:raise ValueError('All three Caltrop tiles must be legal ground within reach')
    else:raise ValueError('Choose an equipped attack to deliver with Throwing Knife')
    c._commit_player_movement(battle,actor)
    if not active(actor):return
    abilities.spend(actor,skill);freeze_walking(actor)
    if kind=='caltrops':
        zone=c.spaces.place_zone(battle,actor,{'zone':'caltrops','turns':2},cells)
        occupied={(cell['x'],cell['y']) for cell in cells}
        for occupant in battle['units'].values():
            if (occupant['x'],occupant['y']) in occupied:
                occupant['zone_location']=[occupant['x'],occupant['y']]
                c._trigger_zones(battle,occupant,'placement',zone['id'])
        battle.setdefault('animation_events',[]).append({'type':'rogue_effect','effect':'caltrops','unit_id':actor['id'],'x':x,'y':y})
    else:
        start={'x':actor['x'],'y':actor['y']};actor.update(x=x,y=y,moved=True,exit_ready=False)
        battle.setdefault('animation_events',[]).append({'type':'movement','unit_id':actor['id'],'points':[start,{'x':x,'y':y}], 'leap':kind=='backflip','teleport':kind=='shadowstep','rogue_motion':kind})
        c._apply_tile_entry(battle,actor)
        battle.setdefault('animation_events',[]).append({'type':'rogue_effect','effect':kind,'unit_id':actor['id'],'x':x,'y':y,'from':start})
    actor['quick_actions_used']=actor.get('quick_actions_used',0)+1
    actor['physical_action']=True
    battle['log'].append(f"{actor['name']} uses {skill['name']} as a Quick Action; the main action remains available.")

def knife_skill(battle,actor,target,skill,knife_id):
    from . import combat as c
    knife=next((s for s in actor.get('skills',[]) if s['id']==knife_id and s.get('rogue_kind')=='throwing_knife'),None)
    if not knife or not abilities.availability(actor,knife)['available'] or actor.get('capture_weapon'):raise ValueError('Throwing Knife is unavailable')
    if skill.get('rogue_kind') not in {'cheap_shot','exploit_weakness',None} or skill.get('quick_action'):raise ValueError('Knife supports basic Attack, Cheap Shot or Exploit Weakness only')
    if not active(target) or c.concealment.unseen(target) or target['team']==actor['team'] or c._distance(actor,target)<=actor.get('attack_range',1) or not c._can_attack(battle,actor,target,3):raise ValueError('Choose an enemy beyond melee reach, within three cells and clear sight')
    adapted=attack_skill(battle,actor,target,skill,True);adapted.update(range=3,elevation_rule='ballistic',melee_style=None,rogue_thrown=True)
    return adapted,knife

def previews(battle,actor):
    from . import combat as c
    result={}
    for skill in actor.get('skills',[]):
        if skill.get('rogue_kind') not in UTILITY or not abilities.availability(actor,skill)['available']:continue
        kind=skill['rogue_kind'];row={'kind':kind}
        if kind=='shadowstep':row['targets']={t['id']:landings(battle,actor,t) for t in battle['units'].values() if t['team']!=actor['team'] and active(t) and not c.concealment.unseen(t)}
        if kind=='backflip':row['landings']=flips(battle,actor)
        if kind=='caltrops':
            row['strips']={f'{x},{y},{r}':cells for y in range(max(0,actor['y']-3),min(battle['height'],actor['y']+4)) for x in range(max(0,actor['x']-3),min(battle['width'],actor['x']+4)) for r in (0,1) if (cells:=strip(battle,actor,x,y,r))}
        if kind=='throwing_knife':
            choices=[{'id':'basic','name':'Basic Attack','type':'active','target':'enemy','source_kind':'character','ability_version':1,'range':1,'elevation_rule':'melee','cost':{'cooldown':1,'charges':None},'effects':[{'type':'attack','power_percent':100}]}]+[s for s in actor.get('skills',[]) if s.get('rogue_kind') in {'cheap_shot','exploit_weakness'} and abilities.availability(actor,s)['available']]
            row['attacks']={s['id']:{t['id']:c._strike_preview(battle,actor,t,'ballistic',3,knife_skill(battle,actor,t,s,skill['id'])[0]) for t in battle['units'].values() if t['team']!=actor['team'] and active(t) and not c.concealment.unseen(t) and c._distance(actor,t)>actor.get('attack_range',1) and c._can_attack(battle,actor,t,3)} for s in choices}
        result[skill['id']]=row
    return result
