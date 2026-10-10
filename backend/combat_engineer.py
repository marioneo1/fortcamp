"""Engineer machinery: owner clocks, committed movement hazards and mounted fire."""
from copy import deepcopy
import math
from . import combat_conditions as conditions, combat_entities as entities
from .combat_feedback import record as feedback
from .combat_bard import attack_skill

KINDS={'sentry_turret','heavy_emplacement','man_the_guns','overclock','scuttle_protocol','proximity_charge','dynamite','rapid_assembly'}
BUILDS={'sentry_turret':(3,2),'heavy_emplacement':(1,3)}
def clock(a):return a.get('ability_activation',0)
def sid(k):return 'job:engineer:'+k
def machines(b,a):return [u for u in entities.owned(b,a) if u.get('engineer_machine')]
def mounted(b,a):
 u=b['units'].get(a.get('mounted_machine'))
 return u if u and u.get('alive') and not u.get('extracted') else None

def restriction(a,s):
 k=s.get('engineer_kind')
 if a.get('defense_pit') and conditions.has(a,'pit_trapped') and attack_skill(s):return 'Climb out of the trap pit before attacking'
 if a.get('engineer_disrupted')==clock(a) and k in {'dynamite','scuttle_protocol'}:return 'Mine disruption prevents offensive actions this turn'
 if not k:return 'Exit the emplacement before using character skills' if a.get('mounted_machine') else None
 if a.get('mounted_machine') and k not in {'man_the_guns','overclock','scuttle_protocol'}:return 'Exit the emplacement first'
 if a.get('construction') and k not in BUILDS:return 'Finish or cancel construction first'
 if k=='man_the_guns' and a.get('overclock_until') is not None:return 'Cannot exit during Overclock'
 if k=='overclock' and not a.get('mounted_machine'):return 'Operate an owned emplacement first'
 if k=='overclock' and a.get('overclock_until') is not None:return 'Already Overclocked'
 if a.get('mounted_machine') and k in {*BUILDS,'proximity_charge','dynamite','rapid_assembly'}:return 'Exit the emplacement first'
 return None

def placement(b,a,reach=2):
 from . import combat as c
 return [{'x':x,'y':y} for y in range(max(0,a['y']-reach),min(b['height'],a['y']+reach+1)) for x in range(max(0,a['x']-reach),min(b['width'],a['x']+reach+1))
         if c._distance(a,{'x':x,'y':y})<=reach and not c._blocked(b,x,y) and not c.tactics.pit_at(b,x,y) and c._ground_at(b,x,y)[0]!='water' and c._line_of_sight(b,a,{'x':x,'y':y})]

def state(a,k):return a.setdefault('ability_state',{}).setdefault(sid(k),{})
def ready(a,k,cd):state(a,k)['ready_at']=clock(a)+cd

def spawn(b,a,k,p,unfinished=False):
 from . import combat as c
 b['entity_serial']=b.get('entity_serial',0)+1
 uid=f"machine_{b['entity_serial']}";heavy=k=='heavy_emplacement'
 hp=max(1,math.ceil(a['max_hp']*.5)) if heavy else 2
 u={'id':uid,'name':'Heavy Emplacement' if heavy else 'Sentry Turret','kind':'summon','temporary':True,'engineer_machine':True,'machine_kind':k,
    'entity_kind':'heavy_emplacement' if heavy else 'scrap_turret','owner_id':a['id'],'deployment_id':uid,'resource_pool':'machinery','capacity_cost':0,
    'policy':'automatic','stationary':True,'displacement_resistance':100,'deployed_at':clock(a),'team':a['team'],**p,'hp':hp,'max_hp':hp,'armor':a.get('armor',0) if heavy else max(30,a['attack']*2),
    'attack':max(1,round(a['attack']*(1.5 if heavy else .75))),'attack_range':7 if heavy else 4,'attack_elevation_rule':'ballistic',
    'move':0,'initiative':0,'accuracy':a.get('accuracy',100),'evasion':0,'movement_type':'ground','weapon':'Heavy ballista' if heavy else 'Sentry bolt','weapon_type':'bow',
    'strength':a.get('strength',4),'intelligence':a.get('intelligence',4),'weight':20,'race':'Automaton','alive':True,'conscious':True,'condition':'active',
    'moved':False,'acted':False,'statuses':[],'skills':[],'passives':[],'reactions':[],'gear_rules':{},'perk_modifiers':{},'racial_resistances':[],
    'racial_weaknesses':[],'status_version':1,'ability_version':1,'ability_activation':0,'ability_state':{},'capture_weapon':None,'portrait':'','loyalty':100,'player_avatar':False,
    'next_fire':clock(a)+1}
 u['under_construction']=unfinished
 b['units'][uid]=u;feedback(b,u,'deploy');c.druid.visual(b,u,'engineer_build','engineer_assembly')
 b['log'].append(f"{a['name']} {'starts building' if unfinished else 'completes'} {u['name']}.")
 return u

def cancel_build(b,a):
 build=a.pop('construction',None)
 u=b['units'].get((build or {}).get('machine_id'))
 if u and u.get('alive'):destroy(b,u,'is abandoned')

def mine_placement(b,a):
 from . import combat as c
 enemies=[u for u in c._living(b) if u['team']!=a['team']]
 return [p for p in placement(b,a) if not any(max(abs(p['x']-u['x']),abs(p['y']-u['y']))<=1 and c._line_of_sight(b,p,u) for u in enemies)]

def area_hit(b,source,cells,packet=None):
 """Only actual damaging areas detonate mines; ranged targeting never selects them."""
 occupied={(p['x'],p['y']) for p in cells}
 for h in list(b.get('engineer_hazards',[])):
  if (h['kind']=='mine' or h.get('proximity_trigger')) and (h['x'],h['y']) in occupied:detonate(b,h,packet)

def exits(b,a,u):
 from . import combat as c
 return [{'x':u['x']+dx,'y':u['y']+dy} for dx,dy in ((0,-1),(1,0),(0,1),(-1,0))
         if not c._blocked(b,u['x']+dx,u['y']+dy,a['id']) and not c.tactics.pit_at(b,u['x']+dx,u['y']+dy) and c._can_step(b,u['x'],u['y'],u['x']+dx,u['y']+dy,a)]

def unmount(b,a,u,point=None,emergency=False):
 from . import combat as c
 options=exits(b,a,u)
 if point is None:point=options[0] if options else {'x':u['x'],'y':u['y']} if emergency else None
 if point is None or not emergency and point not in options:raise ValueError('Choose a highlighted legal exit tile')
 start=(a['x'],a['y']);a.pop('mounted_machine',None);u.pop('operator_id',None)
 for key,value in a.pop('mounted_original',{}).items():
  if value is None:a.pop(key,None)
  else:a[key]=value
 a.update(point);a['zone_location']=list(start)
 if start!=(a['x'],a['y']):c._record_movement(b,a,start,[(a['x'],a['y'])]);c._apply_tile_entry(b,a)
 a['summoner_movement_locked']=True


def destroy(b,u,reason='breaks'):
 from . import combat as c
 if not u.get('alive'):return
 u.update(hp=0,alive=False,conscious=False,condition='dead')
 packet=c.druid.visual(b,u,'engineer_explosion','engineer_explosion')
 feedback(b,u,'dissipate',attack_packet=packet)
 b.setdefault('animation_events',[]).append({'type':'death_burst','unit_id':u['id'],'x':u['x'],'y':u['y'],'race':'Automaton','bloodless':True,'attack_packet':packet})
 b['log'].append(f"{u['name']} {reason}.")
 cleanup(b)
 return packet

def cleanup(b):
 from . import combat as c
 for u in b['units'].values():
  if not u.get('engineer_machine'):continue
  if not c._combat_active(u):
   u.setdefault('machine_died_round',b.get('round',1))
   age=b.get('round',1)-u['machine_died_round']
   u['machine_fading']=age>=1
   if age>=2:u['extracted']=True
 for a in b['units'].values():
  build=a.get('construction')
  if build and build.get('machine_id') and not c._combat_active(b['units'].get(build['machine_id'],{})):a.pop('construction')
 for a in list(b['units'].values()):
  uid=a.get('mounted_machine')
  if not uid:continue
  u=b['units'].get(uid)
  if not u or not c._combat_active(u):
   if a.pop('overclock_until',None) is not None:ready(a,'overclock',5)
   if u:unmount(b,a,u,emergency=True)
   else:
    a.pop('mounted_machine',None)
    for key,value in a.pop('mounted_original',{}).items():a[key]=value


def route_target(b,a,t,source):
 """Direct aimed hits strike occupied machinery; area/status damage reaches occupant."""
 u=mounted(b,t)
 return u if u and not any(source.get(k) for k in ('status_tick','engineer_area','mage_spell','area_attack','collision_attack','environmental_fall')) else t

def fire(b,a,u,t,manual=False):
 from . import combat as c
 heavy=u['machine_kind']=='heavy_emplacement'
 power=max(1,round(a.get('mounted_original',{}).get('attack',a['attack'])*((2 if heavy else 1.25) if manual else (1.5 if heavy else .75))))
 source={**u,'attack':power,'credit_owner_id':a['id']}
 _,hit,damage,_,_=c._perform_attack(b,source,t,'ballistic')
 if heavy and hit:
  packet=next((e.get('attack_packet') for e in reversed(b['animation_events']) if e.get('attack_event') and e.get('attacker_id')==u['id']),None)
  begin=len(b['animation_events']);c.druid.visual(b,t,'engineer_cross_blast','engineer_bolt_explosion')
  if packet is not None:
   for event in b['animation_events'][begin:]:event.update(impact_origin_packet=packet,impact_offset=0)
  for victim in list(c._living(b)):
   if victim['id']!=t['id'] and c._distance(victim,t)==1 and c._line_of_sight(b,t,victim):
    area={**source,'engineer_area':True}
    begin=len(b['animation_events']);c._deal_damage(b,area,victim,bonus=-power//2)
    if packet is not None:
     for event in b['animation_events'][begin:]:event.update(impact_origin_packet=packet,impact_offset=0)
  area_hit(b,source,[{'x':t['x']+dx,'y':t['y']+dy} for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)) if c._line_of_sight(b,t,{'x':t['x']+dx,'y':t['y']+dy})],packet)
 u['acted']=True;u['next_fire']=clock(a)+(2 if heavy else 1)
 b['log'].append(f"{u['name']} {'hits' if hit else 'misses'} {t['name']}"+(f' for {damage}.' if hit else '.'))


def command(b,a,s,cmd):
 from . import combat as c
 k=s['engineer_kind'];reason=restriction(a,s)
 if reason:raise ValueError(reason)
 if a.get('acted') or a.get('forced_skip'):raise ValueError('No action available')
 if k in BUILDS and a.get('construction'):
  cancel_build(b,a);a['acted']=True;b['log'].append(f"{a['name']} cancels construction; the deployment slot is free.");return True
 availability=c.abilities.availability(a,s)
 if not availability['available']:raise ValueError(availability['reason'])
 p={'x':cmd.get('x'),'y':cmd.get('y')}
 if k in {*BUILDS,'proximity_charge','dynamite'}:
  if not all(isinstance(p[v],int) and not isinstance(p[v],bool) for v in p):raise ValueError('Choose a legal ground tile')
  if k=='dynamite':
   if not c._can_attack(b,a,p,3):raise ValueError('Choose a visible tile within three cells')
  elif p not in (mine_placement(b,a) if k=='proximity_charge' else placement(b,a)):raise ValueError('Choose empty ground outside enemy mine trigger range' if k=='proximity_charge' else 'Choose an empty visible ground tile within two cells')
  if k in BUILDS and len([u for u in machines(b,a) if u['machine_kind']==k])>=BUILDS[k][0]:raise ValueError('All deployment slots are occupied')
  if k=='proximity_charge' and sum(h['kind']=='mine' and h['owner_id']==a['id'] for h in b.get('engineer_hazards',[]))>=a.get('defense_mine_limit',2):raise ValueError('All Proximity Charge slots are occupied')
 if k=='man_the_guns':
  u=mounted(b,a)
  if u:
   if p not in exits(b,a,u):raise ValueError('Choose a highlighted legal adjacent exit')
  else:
   u=b['units'].get(cmd.get('target_id'))
   if u not in machines(b,a) or u.get('under_construction') or u.get('operator_id') or c._distance(a,u)!=1 or not c._can_step({**b,'units':{uid:v for uid,v in b['units'].items() if uid!=u['id']}},a['x'],a['y'],u['x'],u['y'],a):raise ValueError('Choose an adjacent completed owned machine with a clear approach')
 if k=='scuttle_protocol':
  u=b['units'].get(cmd.get('target_id')) if cmd.get('target_id') else mounted(b,a)
  if u not in machines(b,a) or a.get('mounted_machine') and u['id']!=a['mounted_machine']:raise ValueError('Choose an owned machine to detonate')
 if k=='rapid_assembly':
  if a.get('rapid_assembly_at')==clock(a):raise ValueError('Rapid Assembly is already prepared')
  a['rapid_assembly_at']=clock(a)
  packet=c.druid.visual(b,a,'engineer_rapid_assembly','engineer_rapid_assembly')
  b['animation_events'][-1]['before_contact']=True
  feedback(b,a,'assembly_ready',attack_packet=packet)
  return False
 c._commit_player_movement(b,a)
 if not c._combat_active(a) or a.get('engineer_interrupted'):return True
 if k in BUILDS:
  if a.pop('rapid_assembly_at',None)==clock(a):spawn(b,a,k,p);ready(a,'rapid_assembly',5)
  else:
   u=spawn(b,a,k,p,True)
   a['construction']={'kind':k,'point':p,'machine_id':u['id'],'remaining':BUILDS[k][1],'started_at':clock(a)}
 elif k=='man_the_guns':
  if a.get('mounted_machine'):unmount(b,a,u,p)
  else:
   a['mount_entry']={'x':a['x'],'y':a['y']}
   a['mounted_original']={key:a.get(key) for key in ('attack','attack_range','attack_elevation_rule','weapon','weapon_type','capture_weapon','displacement_resistance')}
   a.update(x=u['x'],y=u['y'],mounted_machine=u['id'],attack=max(1,round(a['attack']*(2 if u['machine_kind']=='heavy_emplacement' else 1.25))),attack_range=7,attack_elevation_rule='ballistic',weapon=u['weapon'],weapon_type='bow',capture_weapon=None)
   u['operator_id']=a['id'];a['displacement_resistance']=100;a['summoner_movement_locked']=True
  return False
 elif k=='overclock':
  a['overclock_until']=clock(a)+2;a['mounted_shots']=a.get('mounted_shots',0);c._record_sound(b,'engineer_overclock');return False
 elif k=='scuttle_protocol':
  occupied=a.get('mounted_machine')==u['id'];center={'x':u['x'],'y':u['y']};base=math.ceil(a['max_hp']*.5)
  # Restore occupant before detonation; only this explosion has the one-HP floor.
  if occupied:unmount(b,a,u,center,True)
  packet=destroy(b,u,'is scuttled')
  source={**a,'attack':base,'status_tick':True,'engineer_area':True,'damage_kind':'explosion','weapon':'Scuttle Protocol'}
  for t in list(c._living(b)):
   if max(abs(t['x']-center['x']),abs(t['y']-center['y']))<=2 and c._line_of_sight(b,center,t):
    begin=len(b['animation_events']);c._deal_damage(b,{**source,'nonlethal_floor':t['id']==a['id']},t,armor_pierce=t.get('armor',0))
    for event in b['animation_events'][begin:]:event['attack_packet']=packet
  direction=a.get('mount_entry',{'x':center['x'],'y':center['y']+1})
  dx=0 if direction['x']==center['x'] else 1 if direction['x']>center['x'] else -1
  dy=0 if direction['y']==center['y'] else 1 if direction['y']>center['y'] else -1
  if dx==dy==0:dy=1
  launch={**a,'x':center['x']-dx,'y':center['y']-dy}
  old=a.get('knockback_resistance',0);a['knockback_resistance']=0
  if occupied:c._apply_displacement(b,launch,a,{'mode':'push','distance':3,'collision_damage':True,'ignore_resistance':True},base//2,packet)
  a['knockback_resistance']=old
  if a.pop('overclock_until',None) is not None:ready(a,'overclock',5)
  ready(a,k,4)
  area_hit(b,a,area_cells(b,center,2),packet)
 elif k in {'proximity_charge','dynamite'}:
  b['engineer_hazard_serial']=b.get('engineer_hazard_serial',0)+1
  h={'id':f"engineer_hazard_{b['engineer_hazard_serial']}",'owner_id':a['id'],'team':a['team'],'kind':'mine' if k=='proximity_charge' else 'dynamite',**p,'placed_at':clock(a),'placed_round':b.get('round',1),'throw_origin':{'x':a['x'],'y':a['y']}}
  if k=='dynamite':h['expires_at']=clock(a)+1;h['power']=a['attack']*2
  b.setdefault('engineer_hazards',[]).append(h)
  if k=='dynamite':
   b['attack_serial']=b.get('attack_serial',0)+1
   b.setdefault('animation_events',[]).append({'type':'martial_effect','skill':'engineer_dynamite_throw','unit_id':a['id'],'x':p['x'],'y':p['y'],'from':deepcopy(h['throw_origin']),'hazard_id':h['id'],'hazard_snapshot':deepcopy(h),'attack_event':True,'attack_packet':b['attack_serial']})
  if k=='proximity_charge':ready(a,k,4)
 a['acted']=True
 return True


def manual_attack(b,a,cmd):
 from . import combat as c
 u=mounted(b,a)
 if not u:raise ValueError('The emplacement is unavailable')
 if a.get('engineer_disrupted')==clock(a) or not c.bard.can_attack(a):raise ValueError('Cannot initiate an attack here')
 shots=a.get('mounted_shots',0);limit=2 if a.get('overclock_until') is not None else 1
 if shots>=limit or a.get('acted'):raise ValueError('No shots remaining')
 t=b['units'].get(cmd.get('target_id'))
 if not t or not c._combat_active(t) or t['team']==a['team'] or c.concealment.unseen(t) or not c._can_attack(b,a,t,7):raise ValueError('Choose a visible enemy in firing range')
 original=a['mounted_original']['attack'];base={**a,'attack':original}
 fire(b,base,u,t,True);a['mounted_shots']=shots+1
 a['acted']=a['mounted_shots']>=limit
 return a['acted']


def start(b,a):
 from . import combat as c
 a['engineer_location']=[a['x'],a['y']]
 a.pop('engineer_interrupted',None);a.pop('engineer_disrupted',None);a.pop('rapid_assembly_at',None);a['mounted_shots']=0
 cleanup(b)
 if a.get('overclock_until') is not None and clock(a)>=a['overclock_until']:
  a.pop('overclock_until');ready(a,'overclock',5)
  u=mounted(b,a)
  if u:destroy(b,u,'breaks after Overclock')
 for h in list(b.get('engineer_hazards',[])):
  if h['kind']=='dynamite' and not h.get('proximity_trigger') and (h['owner_id']==a['id'] and h['expires_at']<=clock(a) or not c._combat_active(b['units'].get(h['owner_id'],{})) and b.get('round',1)>h.get('placed_round',1)):detonate(b,h)


def finish(b,a):
 from . import combat as c
 stamp=clock(a)
 if a.get('engineer_finished')==stamp:return
 a['engineer_finished']=stamp;a.pop('rapid_assembly_at',None)
 build=a.get('construction')
 if build and c._combat_active(a) and not a.get('forced_skip') and stamp>build['started_at']:
  build['remaining']-=1
  if build['remaining']<=0:
   u=b['units'].get(build.get('machine_id'))
   if u and c._combat_active(u):
    u.update(under_construction=False,deployed_at=stamp,next_fire=stamp+1);a.pop('construction');c.druid.visual(b,u,'engineer_build','engineer_assembly')
   elif not build.get('machine_id') and build['point'] in placement(b,a):spawn(b,a,build['kind'],build['point']);a.pop('construction')
   else:b['log'].append('Construction waits: the destination is occupied or blocked. Cancel or clear it.');build['remaining']=1
 for u in machines(b,a):
  if not u.get('under_construction') and not u.get('operator_id') and u['deployed_at']<stamp and u['next_fire']<=stamp and not u.get('forced_skip') and c._combat_active(a):
   targets=[t for t in c._entity_targets(b,u) if c._can_attack(b,u,t,u['attack_range'])]
   if targets and c.bard.can_attack(u):fire(b,a,u,min(targets,key=lambda t:(t['hp'],c._distance(u,t),t['id'])))
  c._tick_gear_statuses(b,u);conditions.finish_activation(u)
 cleanup(b)


def detonate(b,h,origin_packet=None):
 from . import combat as c
 if h not in b.get('engineer_hazards',[]):return
 b['engineer_hazards'].remove(h)
 a=b['units'].get(h['owner_id'])
 if not a:return
 if h['kind']=='dynamite' and not h.get('proximity_trigger'):ready(a,'dynamite',1)
 packet=c.druid.visual(b,a,'engineer_explosion','engineer_mine' if h['kind']=='mine' else 'engineer_explosion',h)
 for event in b['animation_events']:
  if event.get('attack_packet')==packet:
   event['hazard_id']=h['id'];event['hazard_snapshot']=deepcopy(h)
   if origin_packet is not None:event.update(impact_origin_packet=origin_packet,impact_offset=0)
 source={**a,**h,'id':a['id'],'attack':h.get('power',0),'status_tick':True,'engineer_area':True,'damage_kind':'explosion','weapon':'Dynamite' if h['kind']=='dynamite' else 'Proximity Charge'}
 for t in list(c._living(b)):
  if max(abs(t['x']-h['x']),abs(t['y']-h['y']))>1 or not c._line_of_sight(b,h,t):continue
  if h['kind']=='dynamite':
   begin=len(b['animation_events']);damage=c._deal_damage(b,source,t)
   for event in b['animation_events'][begin:]:event['attack_packet']=packet
   origin=h.get('throw_origin',a) if (t['x'],t['y'])==(h['x'],h['y']) else h
   push={**a,'x':origin['x'],'y':origin['y']}
   c._apply_displacement(b,push,t,{'mode':'push','distance':1,'collision_damage':True},damage,packet)
   if h.get('proximity_trigger'):t['engineer_interrupted']=True
   if not h.get('proximity_trigger') and c._combat_active(t) and not c.mage.status(b,a,t,'stun',1,75,packet) and conditions.resistance(t,'hobbled')<100:
    conditions.apply(t,'hobbled',1,a);feedback(b,t,'status',status_id='hobbled',attack_packet=packet)
  else:
   # Mine disruption explicitly bypasses chance resistance; immunity still matters.
   if conditions.resistance(t,'stun')<100 and conditions.apply(t,'stun',1,a):feedback(b,t,'status',status_id='stun',attack_packet=packet)
   t['engineer_interrupted']=True;t['engineer_disrupted']=clock(t);t['rogue_walk_locked']=True
   t['statuses']=[s for s in t.get('statuses',[]) if s['id']!='engineer_disruption']+[{'id':'engineer_disruption','name':'Mine Disruption','description':'Remaining movement halted; cannot initiate damaging actions until your next turn. Non-attack actions remain legal.','turns':1}]
   feedback(b,t,'status',status_id='engineer_disruption',attack_packet=packet)
 if h['kind']=='dynamite':area_hit(b,a,area_cells(b,h,1),packet)


def entry(b,u):
 from . import combat as c
 location=[u['x'],u['y']]
 if u.get('engineer_location')==location:return
 if u.get('construction'):
  cancel_build(b,u);b['log'].append(f"{u['name']}'s construction is cancelled by displacement.")
 u['engineer_location']=location
 if u.get('temporary') and u.get('engineer_machine'):return
 for h in list(b.get('engineer_hazards',[])):
  if (h['kind']=='mine' or h.get('proximity_trigger')) and max(abs(u['x']-h['x']),abs(u['y']-h['y']))<=1 and c._line_of_sight(b,h,u) and not c.rogue.trap_expert(u):detonate(b,h)


def presentation(b,a):
 from .combat_skill_copy import summarize
 if a.get('engineer_machine'):
  a['statuses'].append({'id':'engineer_machine','name':'Stationary Machine','description':'Owned by '+b['units'].get(a['owner_id'],{}).get('name','Engineer')+'. Independent firing cycle; no shared damage budget. Cannot be pushed or pulled. '+('Under construction: blocks its tile and can be destroyed; cannot fire or be mounted.' if a.get('under_construction') else 'Occupied: no automatic shot; operator fires manually.' if a.get('operator_id') else 'Autonomous targeting: lowest-HP visible enemy in range.')})
 for s in a.get('skills',[]):
  k=s.get('engineer_kind')
  if k:summarize(s)
  if k in {'rapid_assembly','overclock'}:s.update(self_only=True,target='ally')
  if k in {'man_the_guns','scuttle_protocol'}:s['target']='ally'
  if k=='man_the_guns' and a.get('mounted_machine'):s.update(name='Exit Emplacement',quick_action=True,description='Leave the turret onto a nearby tile unless Overclock is active.')
  if k in BUILDS and a.get('construction'):s.update(name='Cancel Construction',description='Abandon your unfinished turret and free its deployment slot.')
 if a.get('construction'):
  build=a['construction'];a['statuses'].append({'id':'engineer_construction','name':'Constructing','description':f"{build['remaining']} full working turns left. Walking locked. Damage does not cancel; hard control pauses work. Select a build skill to cancel.",'turns':build['remaining']})
 if a.get('rapid_assembly_at')==clock(a):a['statuses'].append({'id':'engineer_rapid_assembly','name':'Rapid Assembly Ready','description':'Your next turret build this turn completes instantly; unused preparation expires at turn end.'})
 if a.get('mounted_machine'):a['statuses'].append({'id':'engineer_mounted','name':'Operating Emplacement','description':'Aimed weapon attacks strike machinery first. Area damage and hazards can reach you. Use Attack to fire or Exit Emplacement to leave.'})
 if a.get('overclock_until') is not None:a['statuses'].append({'id':'engineer_overclock','name':'Overclock','description':'Two shots per activation; cannot exit. Machine breaks when this expires.','turns':max(0,a['overclock_until']-clock(a))})


def view(b,a):
 from . import combat as c
 u=mounted(b,a)
 return {'dynamite_cells':[{'x':x,'y':y} for y in range(b['height']) for x in range(b['width']) if c._can_attack(b,a,{'x':x,'y':y},3)],'placement':placement(b,a),'mine_placement':mine_placement(b,a),'mounts':[u['id'] for u in machines(b,a) if not u.get('under_construction') and not u.get('operator_id') and abs(u['x']-a['x'])+abs(u['y']-a['y'])==1 and c._can_step({**b,'units':{uid:v for uid,v in b['units'].items() if uid!=u['id']}},a['x'],a['y'],u['x'],u['y'],a)],
         'exits':exits(b,a,u) if u else [],'machines':[u['id'] for u in machines(b,a)],'sentry_used':sum(u['machine_kind']=='sentry_turret' for u in machines(b,a)),
         'heavy_used':sum(u['machine_kind']=='heavy_emplacement' for u in machines(b,a)),'shots_remaining':(2 if a.get('overclock_until') is not None else 1)-a.get('mounted_shots',0)}

def area_cells(b,center,radius):
 from . import combat as c
 return [{'x':x,'y':y} for y in range(max(0,center['y']-radius),min(b['height'],center['y']+radius+1)) for x in range(max(0,center['x']-radius),min(b['width'],center['x']+radius+1)) if c._line_of_sight(b,center,{'x':x,'y':y})]

def blast_preview(b,a,center,kind):
 from . import combat as c
 radius=2 if kind=='scuttle_protocol' else 1;cells=area_cells(b,center,radius)
 power=math.ceil(a['max_hp']*.5) if kind=='scuttle_protocol' else a['attack']*2
 source={**a,'attack':power,'status_tick':True,'engineer_area':True,'damage_kind':'explosion'}
 forecasts={};tactics=[]
 for t in c._living(b):
  if {'x':t['x'],'y':t['y']} not in cells:continue
  probe=deepcopy(t);damage=c._damage_before_barrier(b,source,probe,armor_pierce=t.get('armor',0) if kind=='scuttle_protocol' else 0)
  damage,_=conditions.absorb(probe,damage)
  if kind=='scuttle_protocol' and t['id']==a['id']:damage=min(damage,max(0,t['hp']-1))
  forecasts[t['id']]={'chance':100,'damage_on_hit':damage,'delayed':kind=='dynamite'}
  if kind=='dynamite' or t['id']==a['id'] and a.get('mounted_machine')==center.get('id'):
   origin=center if (t['x'],t['y'])!=(center['x'],center['y']) else a.get('mount_entry',{'x':center['x'],'y':center['y']+1}) if kind=='scuttle_protocol' else a
   if kind=='scuttle_protocol':origin={**a,'x':2*center['x']-origin['x'],'y':2*center['y']-origin['y']}
   preview=c._displacement_preview(b,origin,t,{'mode':'push','distance':3 if kind=='scuttle_protocol' else 1,'ignore_resistance':kind=='scuttle_protocol'})
   preview.update(type='push',unit_id=t['id'],collision_damage=max(1,damage//2) if preview.get('solid_collision') else 0);tactics.append(preview)
 return {'chance':100,'damage_on_hit':0,'target_forecasts':forecasts,'zones':[{'kind':'impact','cells':cells}],'tactics':tactics,'damage_note':'Hits allies too.'}

def previews(b,a,s):
 from . import combat as c
 ground={};units={};k=s['engineer_kind']
 if not c.abilities.availability(a,s)['available']:return ground,units
 if k in BUILDS:return ground,units
 if k in {'rapid_assembly','overclock'}:units[a['id']]={'support':True,'chance':100,'damage_on_hit':0}
 elif k=='man_the_guns':
  if a.get('mounted_machine'):
   ground={f"{p['x']},{p['y']}":{'support':True,'chance':100,'zones':[{'kind':'impact','cells':[p]}]} for p in exits(b,a,mounted(b,a))}
  else:units={uid:{'support':True,'chance':100,'damage_on_hit':0} for uid in view(b,a)['mounts']}
 elif k=='scuttle_protocol':
  units={u['id']:blast_preview(b,a,u,k) for u in machines(b,a) if not a.get('mounted_machine') or a['mounted_machine']==u['id']}
 elif k=='proximity_charge':
  ground={f"{p['x']},{p['y']}":{'chance':100,'damage_on_hit':0,'zones':[{'kind':'impact','cells':area_cells(b,p,1)}],'target_forecasts':{},'damage_note':'Any unit entering this area triggers the mine.'} for p in mine_placement(b,a)}
 elif k=='dynamite':
  ground={f"{p['x']},{p['y']}":blast_preview(b,a,p,k) for p in view(b,a)['dynamite_cells']}
 return ground,units


def auto(b,a,targets):
 from . import combat as c
 if a.get('construction'):c._guard(b,a);return True
 u=mounted(b,a)
 if u:
  legal=[t for t in targets if c._can_attack(b,a,t,7)]
  if legal and c.bard.can_attack(a):
   target=min(legal,key=lambda t:(t['hp'],t['id']))
   manual_attack(b,a,{'target_id':target['id']})
   if not a.get('acted') and c._combat_active(target):manual_attack(b,a,{'target_id':target['id']})
  else:c._guard(b,a)
  return True
 skills={s['engineer_kind']:s for s in a.get('skills',[]) if s.get('engineer_kind') and c.abilities.availability(a,s)['available']}
 for kind in ('sentry_turret','heavy_emplacement'):
  if kind in skills and len([u for u in machines(b,a) if u['machine_kind']==kind])<BUILDS[kind][0]:
   points=placement(b,a)
   if points:
    target=min(targets,key=lambda t:c._distance(a,t),default=a)
    p=min(points,key=lambda p:c._distance(p,target))
    command(b,a,skills[kind],p);return True
 if 'dynamite' in skills:
  choices=[t for t in targets if c._can_attack(b,a,t,3) and all(max(abs(friend['x']-t['x']),abs(friend['y']-t['y']))>1 for friend in c._living(b,a['team']))]
  if choices:command(b,a,skills['dynamite'],min(choices,key=lambda t:t['hp']));return True
 return False
