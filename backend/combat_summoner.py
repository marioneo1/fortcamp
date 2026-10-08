"""Autonomous owner-linked creatures and bounded, persistent tactical orders."""
from copy import deepcopy
import math
import random
from . import combat_entities as entities, combat_conditions as conditions
from .combat_feedback import record as feedback

KINDS={'transposition','bound_companion','wisp_swarm','spirit_projection','sacrifice','overload','life_pact'}
SUMMONS={'bound_companion','wisp_swarm'}
ORDERS={'hold','focus','follow','protect','stand_down','clear'}
COMPANIONS={'fire','earth','grass'}
PROFILES={
 'fire':'Half general stats; full INT. Ranged Fire hits apply Burn and scorch one tile. Fire Wall: three fire tiles for three creature turns; each entered tile adds and triggers Burn, plus half INT fire damage. Three-turn ability cooldown.',
 'earth':'Full owner maximum HP; half other stats; one movement. Direct damage received -25%. Melee hits independently roll 25% Push and 25% Stun. Hurl Boulder: range 3, 1.25x ATK, 75% Stun, three creature-turn cooldown. Normal resistance applies.',
 'grass':'Full owner maximum HP and INT; half other stats. Melee spirit attacks use INT with normal accuracy and defenses. Life Offering spends 25% maximum HP, rounded up, to heal its Protect Ally target (otherwise the Summoner) for twice that amount; cannot kill this companion; two creature-turn cooldown. Nature Burst pushes units adjacent to that ally one tile, including allies; three-turn cooldown.',
 'wisp':'One HP, flying, ranged magical attack with 40% owner INT as attack power; normal accuracy and defenses. Occupies a real tile and costs one Summon Capacity.'}
COOLDOWNS={'bound_companion':5,'wisp_swarm':6}

def clock(a):return a.get('ability_activation',0)
def has(a,key):return any(p['id']=='job:summoner:'+key for p in a.get('passives',[]))
def crew(b,a):return [u for u in entities.owned(b,a) if u.get('summoner_creature')]
def group(b,a,kind):return [u for u in crew(b,a) if u['summon_skill']==kind]
def skill_id(kind):return 'job:summoner:'+kind
def roll(b,a,key):
 serial=b.get('summoner_roll',0);b['summoner_roll']=serial+1
 return random.Random(f"{b.get('seed')}:summoner:{a['id']}:{key}:{serial}").randint(1,100)

def placement(b,a,flying=False):
 from . import combat as c
 return [{'x':x,'y':y} for y in range(max(0,a['y']-2),min(b['height'],a['y']+3))
         for x in range(max(0,a['x']-2),min(b['width'],a['x']+3))
         if not c._blocked(b,x,y,None,'flying' if flying else 'ground')
         and c._line_of_sight(b,a,{'x':x,'y':y})
         and (flying or not c.tactics.pit_at(b,x,y) and c._ground_at(b,x,y)[0]!='water')]

def availability(a,s):
 if s.get('summoner_kind')=='orders':return deepcopy(s['availability'])
 if s.get('summoner_kind') not in SUMMONS:return None
 state=a.get('ability_state',{}).get(s['id'],{})
 remaining=max(0,state.get('ready_at',0)-clock(a))
 active=bool(state.get('active_deployment'))
 reason='Main action already used' if a.get('acted') else 'Mute prevents conjuring' if not active and conditions.has(a,'mute') else f'Ready in {remaining} of your turns' if not active and remaining else None
 return {'available':not reason,'reason':reason,'cooldown_remaining':0 if active else remaining,'uses_remaining':None,'reclaim':active}

def spawn(b,a,kind,positions,element=None):
 from . import combat as c
 count=3 if kind=='wisp_swarm' else 1
 if kind=='bound_companion' and element not in COMPANIONS:raise ValueError('Choose Fire, Earth or Grass Companion')
 if group(b,a,kind):raise ValueError('Reclaim the existing summons first')
 if kind=='wisp_swarm' and entities.usage(b,a)+3>a.get('summon_capacity',3):raise ValueError('Need three free Summon Capacity')
 if not isinstance(positions,list) or len(positions)!=count:raise ValueError(f'Choose {count} initial summon tiles')
 legal={(p['x'],p['y']) for p in placement(b,a,kind=='wisp_swarm')}
 try:points=[(p['x'],p['y']) for p in positions]
 except (KeyError,TypeError):raise ValueError('Choose valid summon tiles')
 if len(set(points))!=count or any(p not in legal for p in points):raise ValueError('Choose distinct legal empty tiles within two cells')
 c._commit_player_movement(b,a)
 if not c._combat_active(a):return
 b['entity_serial']=b.get('entity_serial',0)+1;deployment=f"deployment_{b['entity_serial']}"
 state=a.setdefault('ability_state',{}).setdefault(skill_id(kind),{})
 state.update(active_deployment=deployment,ready_at=0,uses=state.get('uses',0)+1)
 for i,(x,y) in enumerate(points):
  role='wisp' if kind=='wisp_swarm' else element
  hp=1 if role=='wisp' else max(1,round(a['max_hp']*(1 if role in {'earth','grass'} else .5)))
  intelligence=max(1,round(a.get('intelligence',a['attack'])*(1 if role in {'fire','grass'} else .5)))
  attack=max(1,round(a['attack']*.5))
  if role=='fire':attack=intelligence
  if role=='wisp':attack=max(1,round(a.get('intelligence',a['attack'])*.4))
  if role=='grass':attack=intelligence
  uid=f"entity_{b['entity_serial']}_{i}"
  u={'id':uid,'name':('Wisp' if role=='wisp' else role.title()+' Companion')+(f' {i+1}' if count>1 else ''),
     'kind':'summon','temporary':True,'summoner_creature':True,'summon_role':role,'summon_skill':kind,
     'owner_id':a['id'],'deployment_id':deployment,'entity_kind':'summoner_'+role,'resource_pool':'capacity',
     'capacity_cost':1 if role=='wisp' else 0,'policy':'autonomous','stationary':False,'deployed_at':clock(a),
     'team':a['team'],'x':x,'y':y,'hp':hp,'max_hp':hp,'armor':max(0,round(a.get('armor',0)*.5)),
     'attack':attack,'intelligence':intelligence,'strength':max(1,round(a.get('strength',4)*.5)),
     'move':1 if role=='earth' else max(2,round(a.get('move',3)*.5)),
     'attack_range':3 if role in {'fire','wisp'} else 1,'attack_elevation_rule':'line_of_effect' if role in {'fire','wisp'} else 'melee',
     'initiative':0,'accuracy':a.get('accuracy',100),'evasion':max(0,round(a.get('evasion',0)*.5)),
     'movement_type':'flying' if role=='wisp' else 'ground','weapon':role.title()+' spirit attack',
     'weapon_type':'staff' if role in {'fire','wisp'} else 'fist','melee_style':'blunt','element':'fire' if role=='fire' else None,
     'race':'Spirit','weight':1 if role=='wisp' else 3,'alive':True,'conscious':True,'condition':'active',
     'moved':False,'acted':False,'statuses':[],'skills':[],'passives':[],'reactions':[],'gear_rules':{},'perk_modifiers':{},
     'racial_resistances':[],'racial_weaknesses':[],'status_version':1,'ability_version':1,'ability_activation':0,
     'ability_state':{},'capture_weapon':None,'loyalty':100,'player_avatar':False,
     'portrait':f'/assets/summoner-v1/portrait_{role}.png','portrait_frame':{'x':.5,'y':.5,'size':1,'image':'square'}}
  b['units'][uid]=u;feedback(b,u,'deploy')
  u['passives']=[{'id':'summon:profile:'+role,'name':role.title()+' Spirit','type':'passive','source_kind':'innate','description':PROFILES[role]}]
  c.druid.visual(b,u,'summoner_conjure','summoner_conjure')
 b['log'].append(f"{a['name']} conjures {'three Wisps' if count==3 else element.title()+' Companion'}. Autonomous actions begin next owner turn.")

def die(b,u,reason,packet=None):
 from . import combat as c
 if not c._combat_active(u):return
 u.update(hp=0,alive=False,conscious=False,condition='dead',defeat_weapon=reason)
 if packet is None:packet=c.druid.visual(b,u,'summoner_dissolve','summoner_transposition')
 u['departure_visual']=True
 feedback(b,u,'dissipate',attack_packet=packet);b['log'].append(f"{u['name']} {reason}.")

def cleanup(b):
 from . import combat as c
 for u in b['units'].values():
  if u.get('summoner_creature') and not c._combat_active(u) and not u.get('departure_visual'):
   u['departure_visual']=True;c.druid.visual(b,u,'summoner_dissolve','summoner_transposition')
 for a in list(b['units'].values()):
  for kind,cd in COOLDOWNS.items():
   state=a.get('ability_state',{}).get(skill_id(kind),{})
   if state.get('active_deployment') and not group(b,a,kind):
    state.pop('active_deployment');state['ready_at']=clock(a)+cd

def reclaim(b,a,kind):
 from . import combat as c
 for u in group(b,a,kind):
  packet=c.druid.visual(b,u,'summoner_dissolve','summoner_transposition')
  u.update(extracted=True,alive=False,conscious=False,condition='dismissed',departure_visual=True)
  feedback(b,u,'dissipate',attack_packet=packet)
 cleanup(b);b['log'].append(f"{a['name']} reclaims {kind.replace('_',' ')}. Replacement cooldown begins.")

def order(b,a,cmd):
 from . import combat as c
 mode=cmd.get('order');units=crew(b,a)
 if mode not in ORDERS:raise ValueError('Choose a valid summon order')
 if cmd.get('entity_id')!='all':units=[u for u in units if u['id']==cmd.get('entity_id')]
 if mode=='protect':units=[u for u in units if u.get('summon_skill')=='bound_companion']
 if not units:raise ValueError('Choose one or all owned active summons')
 value={'kind':mode}
 if mode=='protect':
  target=b['units'].get(cmd.get('target_id'))
  if not target or not c._combat_active(target) or target['team']!=a['team'] or target in units or target.get('carried_by'):raise ValueError('Choose a living ally, including the Summoner, other than this companion')
  value['target_id']=target['id']
 if mode=='focus':
  target=b['units'].get(cmd.get('target_id'))
  if not target or target not in c._entity_targets(b,units[0]):raise ValueError('Choose a visible living enemy')
  value['target_id']=target['id']
 if mode=='hold':
  x,y=cmd.get('x'),cmd.get('y')
  if not isinstance(x,int) or not isinstance(y,int) or not (0<=x<b['width'] and 0<=y<b['height']):raise ValueError('Choose a map destination')
  value.update(x=x,y=y)
 for u in units:
  if mode=='clear':u.pop('summon_order',None)
  else:u['summon_order']=deepcopy(value)
 b['log'].append(f"{a['name']} orders {len(units)} summon(s): {mode.replace('_',' ')}.")

def swap_legal(b,a,left,right):
 from . import combat as c
 units=crew(b,a)
 if not left or not right or left['id']==right['id'] or left not in [a,*units] or right not in [a,*units]:return False
 planning={**b,'units':{k:v for k,v in b['units'].items() if k not in {left['id'],right['id']}}}
 return all(not c._blocked(planning,v['x'],v['y'],None,u.get('movement_type','ground')) and
            (u.get('movement_type')=='flying' or not c.tactics.pit_at(b,v['x'],v['y'])) for u,v in [(left,right),(right,left)])

def command(b,a,s,cmd):
 from . import combat as c
 kind=s['summoner_kind'];state=c.abilities.availability(a,s)
 if not state['available']:raise ValueError(state['reason'])
 if kind in SUMMONS:
  if state.get('reclaim'):
   c._commit_player_movement(b,a)
   if c._combat_active(a):reclaim(b,a,kind)
   return False
  spawn(b,a,kind,cmd.get('positions'),cmd.get('element'))
  main=not has(a,'rapid_conjuration');a['acted']=main
  return main
 units=crew(b,a);target=b['units'].get(cmd.get('target_id'))
 left=None
 if kind in {'overload','life_pact'}:
  if target not in units:raise ValueError('Choose an owned active summon')
  if kind=='overload' and target.get('overloaded_once'):raise ValueError('Each summon can be Overloaded only once')
  if kind=='life_pact' and (a['hp']<=math.ceil(a['max_hp']*.25) or target['hp']>=target['max_hp']):raise ValueError('Need more than 25% HP and an injured summon')
 elif kind=='transposition':
  left=b['units'].get(cmd.get('ally_id'))
  if not swap_legal(b,a,left,target):raise ValueError('Choose two distinct legal owned bodies to swap')
 elif kind=='spirit_projection':
  if not target or target not in c._entity_targets(b,{'owner_id':a['id']}) or not c._can_attack(b,a,target,3):raise ValueError('Choose a visible enemy within three cells and sight')
  if not any(c._distance(u,target)<=2 for u in units):raise ValueError('Need a summon within two cells of the target')
 elif kind=='sacrifice':
  x,y=cmd.get('x'),cmd.get('y')
  if not isinstance(x,int) or not isinstance(y,int) or not (0<=x<b['width'] and 0<=y<b['height']) or not c._can_attack(b,a,{'x':x,'y':y},3):raise ValueError('Choose an area within three cells and sight')
  units=[u for u in units if max(abs(u['x']-x),abs(u['y']-y))<=1]
  if not units:raise ValueError('No owned summons inside the sacrifice area')
 c._commit_player_movement(b,a)
 if not c._combat_active(a) or a.get('engineer_interrupted') and c.bard.attack_skill(s):return True
 if kind=='life_pact' and a['hp']<=math.ceil(a['max_hp']*.25):raise ValueError('Movement damage left too little HP for Life Pact')
 c.abilities.spend(a,s)
 recipient=target if kind in {'overload','life_pact'} else a
 packet=None if kind in {'sacrifice','transposition'} else c.druid.visual(b,recipient,'summoner_'+kind,'summoner_projection' if kind=='spirit_projection' else 'summoner_'+kind)
 if kind=='transposition':
  origins=[{'x':u['x'],'y':u['y']} for u in (left,target)]
  packets=[c.druid.visual(b,u,'summoner_transposition','summoner_transposition') for u in (left,target)]
  for u,p in zip((left,target),reversed(origins)):
   u.update(x=p['x'],y=p['y']);u.pop('movement_origin',None);u.pop('movement_path',None)
   b['animation_events'].append({'type':'summoner_swap','unit_id':u['id'],'from_point':origins[0 if u is left else 1],'x':u['x'],'y':u['y'],'attack_packet':packets[0 if u is left else 1]})
   c._apply_tile_entry(b,u)
  a['movement_origin']={'x':a['x'],'y':a['y']};a['movement_path']=[]
  a['summoner_movement_locked']=True
 elif kind=='overload':
  target.update(overloaded_once=True,overload_expires=clock(a)+3,hp=target['hp']*3,max_hp=target['max_hp']*3,attack=target['attack']*3)
  feedback(b,target,'status',status_id='summon_overload',attack_packet=packet)
 elif kind=='life_pact':
  cost=math.ceil(a['max_hp']*.25);a['hp']-=cost
  feedback(b,a,'damage',cost,attack_packet=packet);c.cleric.heal(b,target,cost,'Life Pact')
 elif kind=='spirit_projection':
  for u in units:
   if c._distance(u,target)<=2 and c._combat_active(target):magic_hit(b,a,target,100,origin=u)
 elif kind=='sacrifice':
  centers=[]
  for u in units:
   packet=c.druid.visual(b,u,'summoner_sacrifice','summoner_sacrifice')
   centers.append(({'x':u['x'],'y':u['y']},packet));die(b,u,'is sacrificed',packet)
  for center,packet in centers:
   c.engineer.area_hit(b,a,c.engineer.area_cells(b,center,1),packet)
   for victim in list(c._living(b)):
    if max(abs(victim['x']-center['x']),abs(victim['y']-center['y']))<=1 and c._line_of_sight(b,center,victim):
     source={**a,'attack_elevation_rule':'ignore','on_hit':None,'damage_kind':'magic'}
     before=len(b['animation_events']);c._deal_damage(b,source,victim)
     for e in b['animation_events'][before:]:e['attack_packet']=packet
     if c._combat_active(victim):c.mage.status(b,a,victim,'blind',3,packet=packet)
 cleanup(b)
 main=not s.get('quick_action');a['acted']=main
 return main

def magic_hit(b,a,t,power=100,packet=None,origin=None):
 from . import combat as c
 source={**a,'attack':max(1,a.get('intelligence',a['attack'])),'on_hit':None,'mage_spell':True,'attack_elevation_rule':'line_of_effect'}
 if origin:source.update(x=origin['x'],y=origin['y'])
 before=len(b['animation_events'])
 result=c._perform_attack(b,source,t,'line_of_effect',bonus=source['attack']*(power-100)//100,ability={'id':'summon_magic','range':20,'elevation_rule':'line_of_effect','cost':{'cooldown':0,'charges':None},'effects':[{'type':'attack','power_percent':power}]})
 if packet is not None:
  for e in b['animation_events'][before:]:e['attack_packet']=packet
 if origin:
  for e in b['animation_events'][before:]:
   if e['type']=='magic_projectile':e['attacker_id']=origin['id']
 return result

def start(b,u):
 from . import combat as c
 u.pop('summoner_movement_locked',None)
 if not u.get('summoner_creature'):return
 c.abilities.start_activation(u,['owner',u['owner_id'],clock(b['units'][u['owner_id']])])
 a=b['units'][u['owner_id']]
 if u.get('overload_expires') is not None and clock(a)>=u['overload_expires']:die(b,u,'expires from Overload')

def incoming(target,source,damage):
 return max(1,round(damage*.75)) if damage and target.get('summon_role')=='earth' and not source.get('status_tick') else damage

def attack(b,a,u,t):
 from . import combat as c
 if not c.bard.can_attack(u):return
 _,hit,damage,_,_=c._perform_attack(b,{**u,'credit_owner_id':a['id']},t,u['attack_elevation_rule'])
 packet=b.get('attack_serial')
 if hit and u['summon_role']=='fire':
  c.mage.burn(b,u,t,packet=packet);c.mage.scorch(b,u,t,0,packet)
 if hit and u['summon_role']=='earth':
  if roll(b,u,'push')<=25:c._apply_displacement(b,u,t,{'mode':'push','distance':1,'collision_damage':True},damage,packet)
  if c._combat_active(t):c.mage.status(b,u,t,'stun',1,25,packet)

def protected_ally(b,a,u):
 from . import combat as c
 order=u.get('summon_order',{})
 target=b['units'].get(order.get('target_id')) if order.get('kind')=='protect' else None
 return target if target and c._combat_active(target) and target['team']==a['team'] and not target.get('carried_by') else a

def threat_rank(b,enemy,ally):
 from . import combat as c
 return (not c._can_attack(b,enemy,ally),c._distance(enemy,ally))

def destination(b,a,u,targets):
 """One bounded Dijkstra per creature; never recursively retry an impossible goal."""
 from . import combat as c
 order=u.get('summon_order',{});kind=order.get('kind');costs,parents=c._movement_tree(b,u)
 if kind=='stand_down':return None,None
 focus=next((t for t in targets if t['id']==order.get('target_id')),None)
 ward=protected_ally(b,a,u)
 target=focus or min(targets,key=lambda t:((threat_rank(b,t,ward) if kind=='protect' else ()),not c._can_attack(b,u,t),c._distance(u,t),t['hp'],t['id']),default=None)
 if kind=='hold':goal={'x':order['x'],'y':order['y']}
 elif kind=='follow':goal=a
 elif kind=='protect':goal=ward
 else:goal=target
 if not goal:return None,None
 # Include distance beyond this activation by a terrain-aware global route.
 route=[]
 if kind in {'hold','follow','protect'}:
  # Search past this turn's movement radius; a U-shaped wall must not trap
  # the creature in a greedy 'always move closer' loop. Occupied Hold goals
  # resolve to the nearest legal tile, with a bounded search on this board.
  goals=[(x,y) for y in range(b['height']) for x in range(b['width']) if not c._blocked(b,x,y,u['id'],u.get('movement_type'))]
  if goals:
   nearest=min(max(abs(x-goal['x']),abs(y-goal['y'])) for x,y in goals)
   goals={p for p in goals if max(abs(p[0]-goal['x']),abs(p[1]-goal['y']))<=max(nearest,2 if kind in {'follow','protect'} else 0)}
   route,_,_=c._route_with_gates(b,u,goals)
 elif target:route,_,_=c._route_with_gates(b,u,c._pursuit_goals(b,u,target))
 if kind not in {'hold','follow','protect'} and target and not route and not c._can_attack(b,u,target):
  # Preserve Focus intent but avoid idling forever behind a sealed enclosure.
  fallback=next((t for t in targets if t is not target and c._can_attack(b,u,t)),None)
  if fallback:target=fallback;goal=fallback
 # Never jump across an unreachable door or occupied tile in a planned route.
 reachable_route=[]
 for p in route:
  if p not in costs:break
  reachable_route.append(p)
 route=reachable_route
 candidates=list(costs)
 hazard_cells={(q['x'],q['y']) for z in b.get('zones',[]) if z['kind'] in {'scorched','ember','caltrops','fire_wall'} for q in z['cells']}
 def rank(p):
  probe={**u,'x':p[0],'y':p[1]};dist=c._distance(probe,goal)
  hazard=sum((q['x'],q['y']) in hazard_cells for q in c._movement_path(parents,costs,p))
  suicidal=bool(u['hp']<=1 and hazard)
  progress=-route.index(p) if p in route else 1
  if kind=='hold':return (suicidal,progress if route else dist,hazard,costs[p],p)
  if kind in {'follow','protect'}:return (suicidal,progress if route else max(0,dist-2),hazard,not (target and c._can_attack(b,probe,target)),costs[p],p)
  can=target and c._can_attack(b,probe,target)
  preferred=u['attack_range']
  route_progress=route.index(p) if p in route else -1
  return (suicidal,not can,hazard,abs(dist-preferred) if can else -route_progress if route else dist,costs[p],p)
 best=min(candidates,key=rank)
 return best,target

def autonomous(b,a,u):
 from . import combat as c
 if u.get('forced_skip') or u.get('panicked') or not c._combat_active(u):return
 targets=c._entity_targets(b,u);order=u.get('summon_order',{}).get('kind')
 ward=protected_ally(b,a,u)
 forced=c.bard.forced_target(b,u)
 if forced:targets=[forced]
 if order=='stand_down':c._guard(b,u);return
 goal,target=destination(b,a,u,targets)
 if goal and goal!=(u['x'],u['y']):
  costs,parents=c._movement_tree(b,u);path=c._movement_path(parents,costs,goal)
  # Use committed route hooks for every crossed hazard tile.
  startpos=(u['x'],u['y']);u.update(x=goal[0],y=goal[1],movement_origin={'x':startpos[0],'y':startpos[1]},movement_path=path)
  u['moved']=True;c._record_movement(b,u,startpos,[(p['x'],p['y']) for p in path])
  c._commit_player_movement(b,u)
 if not c._combat_active(u):return
 if u['summon_role']=='grass' and not conditions.has(ward,'burn') and ward['hp']<ward['max_hp'] and clock(u)>=u.get('offering_ready',0):
  cost=math.ceil(u['max_hp']*.25)
  if u['hp']>cost and ward['max_hp']-ward['hp']>=cost:
   u['hp']-=cost;feedback(b,u,'damage',cost);c.cleric.heal(b,ward,cost*2,'Life Offering');u['offering_ready']=clock(u)+2;return
 in_range=[t for t in targets if c._can_attack(b,u,t,u['attack_range'])]
 focus=next((t for t in targets if t['id']==u.get('summon_order',{}).get('target_id')),None)
 target=focus if focus in in_range else min(in_range,key=lambda t:((threat_rank(b,t,ward) if order=='protect' else ()),t['hp'],t['id']),default=None)
 if not c.bard.can_attack(u):return
 if u['summon_role']=='earth' and targets and clock(u)>=u.get('boulder_ready',0):
  distant=[t for t in targets if c._can_attack(b,u,t,3) and c._distance(u,t)>1]
  if distant:
   t=focus if focus in distant else min(distant,key=lambda t:((threat_rank(b,t,ward) if order=='protect' else ()),t.get('resistance_details',{}).get('statuses',{}).get('stun',0),t['hp'],t['id']))
   skill={'id':'hurl_boulder','range':3,'elevation_rule':'ballistic','effects':[{'type':'attack','power_percent':125}]}
   _,hit,_,_,_=c._perform_attack(b,u,t,'ballistic',bonus=u['attack']//4,ability=skill)
   if hit:c.mage.status(b,u,t,'stun',1,75,b.get('attack_serial'))
   u['boulder_ready']=clock(u)+3;return
 if u['summon_role']=='grass' and clock(u)>=u.get('burst_ready',0):
  near=[t for t in targets if c._distance(u,t)<=3 and c._distance(t,ward)<=2]
  adjacent_enemies=[t for t in targets if c._distance(t,ward)<=1]
  adjacent_allies=[t for t in c._living(b) if t['team']==a['team'] and t['id'] not in {ward['id'],u['id']} and c._distance(t,ward)<=1]
  if near and len(adjacent_enemies)>len(adjacent_allies):
   # Center on the supported ally, pushing threatening enemies outward without
   # arbitrarily choosing a victim as the push's direction/source.
   center={**u,'x':ward['x'],'y':ward['y']};packet=c.druid.visual(b,u,'summoner_nature_burst','druid_growth',center)
   for t in list(c._living(b)):
    if t['id']!=u['id'] and max(abs(t['x']-center['x']),abs(t['y']-center['y']))==1:c._apply_displacement(b,center,t,{'mode':'push','distance':1,'collision_damage':True},0,packet)
   u['burst_ready']=clock(u)+3;return
 if u['summon_role']=='fire' and clock(u)>=u.get('wall_ready',0) and targets:
  strips=[]
  for t in targets:
   if not c._can_attack(b,u,t,3):continue
   for rotation in (0,1):
    cells=[{'x':t['x']+(i if not rotation else 0),'y':t['y']+(i if rotation else 0)} for i in (-1,0,1)]
    cells=[p for p in cells if 0<=p['x']<b['width'] and 0<=p['y']<b['height'] and c._line_of_sight(b,u,p)]
    if order=='protect' and any((p['x'],p['y'])==(ward['x'],ward['y']) for p in cells):continue
    score=sum(any((v['x'],v['y'])==(p['x'],p['y']) for p in cells) for v in targets)
    if order=='protect' and not any(not threat_rank(b,v,ward)[0] and any((v['x'],v['y'])==(p['x'],p['y']) for p in cells) for v in targets):continue
    if len(cells)==3:strips.append((score,cells))
  if strips and max(score for score,_ in strips)>=2:
   _,cells=max(strips,key=lambda item:item[0]);z=c.spaces.place_zone(b,u,{'zone':'fire_wall','turns':3},cells);z['entry_damage']=max(1,round(u['intelligence']*.5))
   u['wall_ready']=clock(u)+3;return
 if target:attack(b,a,u,target)
 else:c._guard(b,u)

def finish(b,a):
 from . import combat as c
 units=crew(b,a)
 for u in units:
  if u['deployed_at']>=clock(a):continue
  if u.get('summoner_finished_at')==clock(a):continue
  u['summoner_finished_at']=clock(a)
  if c._combat_active(a):autonomous(b,a,u)
  c._tick_gear_statuses(b,u);conditions.finish_activation(u)
 cleanup(b)

def presentation(b,a):
 from .combat_skill_copy import summarize
 for skill in a.get('skills',[]):summarize(skill)
 for s in a.get('skills',[]):
  if s.get('summoner_kind') in SUMMONS:
   active=bool(group(b,a,s['summoner_kind']))
   if active:s.update(name='Reclaim All Wisps' if s['summoner_kind']=='wisp_swarm' else 'Reclaim Companion',description='Dismiss this group and begin its replacement cooldown.',quick_action=True)
   elif has(a,'rapid_conjuration'):s['quick_action']=True
 if a.get('job_id')=='summoner' or any(s.get('summoner_kind') in KINDS for s in a.get('skills',[])):
  a['skills']=[s for s in a.get('skills',[]) if s['id']!='innate:summoner:orders']
  active=bool(crew(b,a))
  a['skills'].append({'id':'innate:summoner:orders','name':'Summon Orders','description':'Choose one summon or the whole group, then Hold Position, Focus Target, Follow Summoner, Stand Down or Clear Order. Bound Companions can also Protect Ally, including you: prioritize healing or disrupting threats, without intercepting attacks. Orders persist and cost no action or equipped skill slot.',
    'type':'active','ability_version':1,'source_kind':'innate','source_name':'Innate Summoner command','summoner_kind':'orders','free_action':True,'range':0,'target':'self','cost':{'cooldown':0,'charges':None},'effects':[],
    'availability':{'available':active and not a.get('acted'),'reason':None if active else 'No active summons','cooldown_remaining':0,'uses_remaining':None}})
 for skill in a.get('skills',[]):
  if skill.get('summoner_kind')=='orders':summarize(skill)
 if a.get('summoner_creature'):
  order=a.get('summon_order',{'kind':'autonomous'})
  label={'hold':'Hold Position','focus':'Focus Target','follow':'Follow Summoner','protect':'Protect Ally','stand_down':'Stand Down','autonomous':'Autonomous'}.get(order['kind'],'Autonomous')
  desc='Acts independently after its owner. '
  if order['kind']=='hold':desc+=f"Travel to cell {order['x']+1}, {order['y']+1}; remain nearby if blocked."
  elif order['kind']=='focus':desc+='Prioritize '+b['units'].get(order.get('target_id'),{}).get('name','the assigned target')+'; use legal fallback attacks.'
  elif order['kind']=='follow':desc+='Stay within two cells of the owner when possible; attack opportunistically.'
  elif order['kind']=='protect':
   ward=protected_ally(b,b['units'][a['owner_id']],a)
   desc+=f"Stay near {ward['name']}; prioritize healing or disrupting nearby threats according to companion type. Does not intercept attacks. Falls back to the Summoner if the selected ally is unavailable."
  elif order['kind']=='stand_down':desc+='Remain still and Guard; do not attack.'
  else:desc+='Choose a reachable hostile target.'
  a['statuses'].append({'id':'summon_order','name':label,'description':desc})
  if a.get('overload_expires') is not None:a['statuses'].append({'id':'summon_overload','name':'Overload','description':'Triple attack and maximum HP. Dies when the owner-turn countdown ends; cannot refresh.','turns':max(0,a['overload_expires']-clock(b['units'][a['owner_id']]))})

def view(b,a):
 from . import combat as c
 units=crew(b,a)
 return {'owner_id':a['id'],'summons':[u['id'] for u in units],'placement':placement(b,a),
         'protect_summons':[u['id'] for u in units if u.get('summon_skill')=='bound_companion'],
         'protect_targets':[u['id'] for u in c._living(b) if u['team']==a['team'] and not u.get('carried_by') and u not in group(b,a,'bound_companion')],
         'wisp_placement':placement(b,a,True),'capacity_used':entities.usage(b,a),'capacity':a.get('summon_capacity',3),
         'skills':{s['id']:s['summoner_kind'] for s in a.get('skills',[]) if s.get('summoner_kind')},
         'projection':{t['id']:sum(c._distance(u,t)<=2 for u in units) for t in c._entity_targets(b,{'owner_id':a['id']}) if c._can_attack(b,a,t,3)},
         'sacrifice_cells':[{'x':x,'y':y} for y in range(b['height']) for x in range(b['width']) if c._can_attack(b,a,{'x':x,'y':y},3)],
         'swaps':{u['id']:[v['id'] for v in [a,*units] if swap_legal(b,a,u,v)] for u in [a,*units]}}

def previews(b,a,skill):
 from . import combat as c
 if skill.get('summoner_kind')!='spirit_projection':return {}
 result={};source={**a,'attack':max(1,a.get('intelligence',a['attack'])),'mage_spell':True,'on_hit':None,'attack_elevation_rule':'line_of_effect'}
 for target in c._entity_targets(b,{'owner_id':a['id']}):
  contributors=[u for u in crew(b,a) if c._distance(u,target)<=2];count=len(contributors)
  if not count or not c._can_attack(b,a,target,3):continue
  recipient=deepcopy(target);damage=0;previews=[]
  for u in contributors:
   origin={**source,'x':u['x'],'y':u['y']};preview=c._attack_preview(b,origin,target,'line_of_effect');previews.append(preview)
   raw=c._damage_before_barrier({'units':b['units'],'animation_events':[]},origin,recipient,bonus=preview['damage_bonus'])
   amount,_=conditions.absorb(recipient,raw);damage+=min(amount,recipient['hp']);recipient['hp']=max(0,recipient['hp']-amount)
  result[target['id']]={**previews[0],'chance':min(p['chance'] for p in previews),'damage_on_hit':damage,'hit_count':count,'damage_note':f'{count} separate spirit contributions; total if all hit. Accuracy shows the lowest contribution chance; each uses its origin and normal defenses.'}
 return result

def auto(b,a,targets):
 """Conservative owner auto-play; creature decisions remain independent."""
 from . import combat as c
 available={s['summoner_kind']:s for s in a.get('skills',[]) if s.get('summoner_kind') and c.abilities.availability(a,s)['available']}
 if not available or a.get('forced_skip'):return False
 for kind in ('bound_companion','wisp_swarm'):
  if kind not in available or group(b,a,kind):continue
  points=placement(b,a,kind=='wisp_swarm');count=3 if kind=='wisp_swarm' else 1
  if len(points)<count or kind=='wisp_swarm' and entities.usage(b,a)+3>a.get('summon_capacity',3):continue
  target=min(targets,key=lambda t:c._distance(a,t),default=a)
  points.sort(key=lambda p:(c._distance(p,target),p['y'],p['x']))
  if command(b,a,available[kind],{'positions':points[:count],'element':'earth' if a['hp']<a['max_hp']*.4 else 'fire'}):return True
 if 'spirit_projection' in available and c.bard.can_attack(a):
  choices=[(sum(c._distance(u,t)<=2 for u in crew(b,a)),t) for t in targets if c._can_attack(b,a,t,3)]
  if choices:
   count,target=max(choices,key=lambda item:(item[0],-item[1]['hp']))
   if count>=2:return command(b,a,available['spirit_projection'],{'target_id':target['id']})
 if 'life_pact' in available and a['hp']>a['max_hp']*.6:
  injured=[u for u in crew(b,a) if u['summon_role']!='wisp' and u['hp']<u['max_hp']*.4]
  if injured:return command(b,a,available['life_pact'],{'target_id':min(injured,key=lambda u:u['hp']/u['max_hp'])['id']})
 return False
