"""Resolve capture and the Captor's bounded isolation/hold state machine."""
from copy import deepcopy
import heapq
import random
from . import combat_conditions as conditions
from .combat_feedback import record as feedback

KINDS={'subduing_blow','bola','hook_and_drag','abduct','restraining_hold','blitz','restraint'}

def clock(u):return u.get('ability_activation',0)
def has(u,key):return any(p.get('id')=='job:captor:'+key for p in u.get('passives',[]))
def status(u,key):return next((s for s in u.get('statuses',[]) if s['id']==key),None)
def stacks(u,key):
 s=status(u,key)
 return len(s['layers']) if s and 'layers' in s else max(1,s.get('stacks',1)) if s else 0

def normalize(u):
 u.setdefault('max_resolve',max(1,int(u.get('max_hp',1))))
 u['resolve']=max(0,min(u['max_resolve'],u.get('resolve',u['max_resolve'])))
 u['capture_ready']=u['resolve']==0
 if u.get('capture_weapon') and not u.get('capture_attack_version'):
  # Capture tools now leave a normal, lethal unarmed attack available.
  u.update(attack=5+int(u.get('strength',4))//2,attack_range=1,attack_elevation_rule='melee',melee_style='fist',capture_attack_version=1)

def isolated(b,a,t):
 from . import combat as c
 return c._distance(a,t)==1 and not c.crossed_walls(b,(a['x'],a['y']),(t['x'],t['y'])) and not any(
  u['id'] not in {a['id'],t['id']} and c._combat_active(u) and c._distance(u,t)==1 and not c.crossed_walls(b,(u['x'],u['y']),(t['x'],t['y'])) for u in b['units'].values())

def mitigation(t):
 attrs=t.get('attributes',{})
 return 100/(100+2*(max(0,t.get('intelligence',attrs.get('int',4)))+max(0,t.get('agility',attrs.get('agi',4)))))

def power(a):
 attrs=a.get('capture_attributes',{})
 values=[max(1,attrs.get(k,a.get('strength',4) if k=='str' else a.get('intelligence',4) if k=='int' else 4)) for k in ('str','dex','int')]
 balanced=min(values)+(sum(values)/3-min(values))*.35
 return 6+balanced+(a.get('capture_weapon') or {}).get('base',8)/4

def multiplier(b,a,t,k):
 if k=='bola':return 1
 if k=='hook_and_drag':return .75
 if k!='subduing_blow':return 1
 return 1.5+(1+.5*sum(bool(status(t,s)) for s in ('hobbled','disarm','stun')) if isolated(b,a,t) else 0)

def odds(a,t):
 base=float(t.get('base_capture_chance',1 if t.get('boss') or t.get('kind')=='chieftain' else 35))
 bonuses=a.get('perk_modifiers',{}).get('capture_chance',0)+a.get('gear_rules',{}).get('capture_chance',0)
 clean=1+a['hp']/max(1,a['max_hp']) if has(a,'clean_capture') else 1
 return max(0,min(95,(base+bonuses)*(1+max(0,(a.get('capture_weapon') or {}).get('base',8)-8)/100)*clean))

def roll(b,a,t,key):
 serial=b.get('capture_roll',0);b['capture_roll']=serial+1
 return random.Random(f"{b.get('seed')}:resolve:{a['id']}:{t['id']}:{key}:{serial}").random()*100

def preview(b,a,t,k='subdue'):
 from . import combat as c
 normalize(t)
 profile=a.get('capture_weapon') or {'range':1,'elevation_rule':'melee'}
 reach=profile['range'] if k=='subdue' else 3 if k in {'bola','hook_and_drag'} else 1
 rule=profile['elevation_rule'] if k=='subdue' else 'ballistic' if reach>1 else 'melee'
 source={**a,'attack_range':reach,'attack_elevation_rule':rule}
 chance=c._attack_preview(b,source,t,rule)['chance']
 damage=min(t['resolve'],max(1,round(power(a)*multiplier(b,a,t,k)*mitigation(t)))) if k in {'subdue','subduing_blow','bola','hook_and_drag'} else 0
 capture=odds(a,t)
 return {'chance':chance,'hit_chance':chance,'damage_on_hit':0,'resolve_damage':damage,'resolve_remaining':max(0,t['resolve']-damage),'resolve_power':multiplier(b,a,t,k),
  'capture_chance':round(capture,2),'capture':k in {'subdue','subduing_blow','bola','hook_and_drag'},'isolated':isolated(b,a,t),'damage_note':f"{damage} Resolve damage; {t['resolve']}/{t['max_resolve']} Resolve. Capture when ready: {capture:.2f}%."}

def attempt(b,a,t,packet=None):
 from . import combat as c
 normalize(t)
 if t['resolve']>0 or not c._combat_active(t) or t.get('temporary'):return False
 success=roll(b,a,t,'capture')<odds(a,t)
 if success:
  begin=len(b.setdefault('animation_events',[]))
  source={**a,'attack':t['max_hp']*100+t.get('armor',0),'status_tick':True,'capture_only':True,'element':None,'on_hit':None}
  c._deal_damage(b,source,t,intent='nonlethal');t['captured']=True
  for e in b['animation_events'][begin:]:
   if packet is not None:e['attack_packet']=packet
 else:feedback(b,t,'capture_failed',**({'attack_packet':packet} if packet is not None else {}))
 b['log'].append(f"{a['name']} attempts capture: {t['name']} {'is restrained' if success else 'resists'} ({odds(a,t):.2f}%).")
 return success

def control(b,a,t,sid,turns,packet=None):
 if roll(b,a,t,sid)<conditions.status_chance(t,sid,100):
  conditions.apply(t,sid,turns,a)
  feedback(b,t,'status',status_id=sid,**({'attack_packet':packet} if packet is not None else {}))
  return True
 feedback(b,t,'resisted',**({'attack_packet':packet} if packet is not None else {}));return False

def strike(b,a,t,k='subdue'):
 from . import combat as c
 normalize(t);forecast=preview(b,a,t,k)
 landed=roll(b,a,t,'hit')<forecast['hit_chance']
 b['attack_serial']=b.get('attack_serial',0)+1;packet=b['attack_serial']
 profile=a.get('capture_weapon') or {'range':1,'elevation_rule':'melee'}
 if k=='subdue' and c.capture_style(a)=='net':
  b.setdefault('animation_events',[]).append({'type':'net_cast','attacker_id':a['id'],'target_id':t['id'],'from':{'x':a['x'],'y':a['y']},'to':{'x':t['x'],'y':t['y']},'hit':landed,'attack_packet':packet})
 elif k=='subdue':
  c._record_melee_animation(b,a,t,landed,profile['elevation_rule'],style='blunt');b['animation_events'][-1]['attack_packet']=packet
 else:
  c.martial.effect(b,a,'captor_'+k,packet);b['animation_events'][-1].update(attack_event=True,target_id=t['id'],to={'x':t['x'],'y':t['y']},hit=landed)
 c.concealment.reveal(b,a);c._wake_ambush(b,t)
 if not landed:feedback(b,t,'miss',attack_packet=packet);return False,packet
 t['resolve']=max(0,t['resolve']-forecast['resolve_damage']);t['capture_ready']=t['resolve']==0
 feedback(b,t,'resolve',forecast['resolve_damage'],attack_packet=packet,resolve=t['resolve'],max_resolve=t['max_resolve'])
 if t['capture_ready']:feedback(b,t,'capture_ready',attack_packet=packet)
 if t['capture_ready']:attempt(b,a,t,packet)
 return True,packet

def release(b,a):
 hold=a.pop('captor_hold',None)
 if not hold:return
 t=b['units'].get(hold['target_id'])
 if t:t.pop('captor_held_by',None);conditions.remove(t,'captor_held')
 conditions.remove(a,'captor_holding')
 a.setdefault('ability_state',{}).setdefault('job:captor:restraining_hold',{})['ready_at']=clock(a)+3
 b['log'].append(f"{a['name']} releases the hold.")

def cleanup(b):
 from . import combat as c
 for a in b['units'].values():
  h=a.get('captor_hold')
  if not h:continue
  t=b['units'].get(h['target_id'])
  if not c._combat_active(a) or not t or not c._combat_active(t) or any(status(a,s) for s in ('stun','freeze','sleep','paralyze','bind')) or [a['x'],a['y']]!=h['origin'] or [t['x'],t['y']]!=h['target_origin'] or not isolated(b,a,t):release(b,a)

def restriction(u,skill):
 k=skill.get('captor_kind')
 if status(u,'disarm') and k in {'subduing_blow','bola','hook_and_drag','restraint'}:return 'Disarmed: capture attacks are unavailable'
 if k=='abduct' and (u.get('carrying') or u.get('carrying_object')):return 'Put down your payload before Abduct'
 if u.get('captor_held_by'):return 'Restrained: wait for release or interference'
 if u.get('captor_hold') and k!='restraining_hold':return 'Release Hold before acting'
 if k=='blitz' and status(u,'captor_blitz'):return 'Blitz is already active'
 return None

def start(b,a):
 if a.get('captor_blitz_until') is not None and clock(a)>=a['captor_blitz_until']:
  a.pop('captor_blitz_until');conditions.remove(a,'captor_blitz')
  a.setdefault('ability_state',{}).setdefault('job:captor:blitz',{})['ready_at']=clock(a)+2
 if a.get('captor_blitz_until') is not None and not status(a,'captor_blitz'):conditions.apply(a,'captor_blitz',2,a)
 cleanup(b)
 if a.get('captor_held_by'):a['forced_skip']=True

def finish(b,a):
 cleanup(b);h=a.get('captor_hold')
 if not h:return
 # The initiation action secures the hold; subsequent completed activations attempt capture.
 if clock(a)==h['began'] or h.get('last_tick')==clock(a):return
 h['last_tick']=clock(a)
 t=b['units'][h['target_id']]
 from . import combat as c
 packet=c.druid.visual(b,a,'captor_restraining_hold','captor_hold',t)
 normalize(t)
 damage=min(t['resolve'],max(1,round(power(a)*.75*mitigation(t))))
 t['resolve']-=damage;t['capture_ready']=t['resolve']==0
 feedback(b,t,'resolve',damage,attack_packet=packet,resolve=t['resolve'],max_resolve=t['max_resolve'])
 if t['capture_ready']:attempt(b,a,t,packet)
 h['remaining']-=1
 if h['remaining']<=0 or t.get('captured') or not c._combat_active(t):release(b,a)

def drag_routes(b,a,t):
 from . import combat as c
 if c._distance(a,t)!=1 or not stacks(t,'hobbled'):return {}
 probe={**b,'units':{k:v for k,v in b['units'].items() if k not in {a['id'],t['id']}}}
 probe=c._routing_snapshot(probe);limit=c._movement_limit(a);origin=(a['x'],a['y'],t['x'],t['y'])
 costs={origin:0};paths={origin:[]};queue=[(0,origin)];result={}
 while queue:
  cost,node=heapq.heappop(queue)
  if costs[node]!=cost:continue
  x,y,tx,ty=node
  for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
   if (nx,ny)==(tx,ty) or not c._can_step(probe,x,y,nx,ny,a) or not c._can_step(probe,tx,ty,x,y,{**t,'paralyzed_move':False,'statuses':[]}):continue
   if c.tactics.pit_at(b,nx,ny) or c.tactics.pit_at(b,x,y):continue
   total=cost+c._step_cost(probe,x,y,nx,ny,a);dest=(nx,ny,x,y)
   if total>limit or total>=costs.get(dest,limit+1):continue
   path=paths[node]+[{'x':nx,'y':ny}];costs[dest]=total;paths[dest]=path;heapq.heappush(queue,(total,dest))
   key=f'{nx},{ny}'
   if key not in result or total<result[key]['cost']:result[key]={'path':path,'cost':total,'target_end':{'x':x,'y':y}}
 return result

def command(b,a,s,cmd):
 from . import combat as c
 k=s['captor_kind'];cleanup(b)
 if k=='restraining_hold' and a.get('captor_hold'):release(b,a);return False
 state=c.abilities.availability(a,s)
 if not state['available']:raise ValueError(state['reason'])
 t=a if k=='blitz' else b['units'].get(cmd.get('target_id'))
 if k!='blitz':
  if not t or not c._combat_active(t) or t['team']==a['team'] or t.get('temporary') or c.concealment.unseen(t):raise ValueError('Choose a living capturable enemy')
  if c.bard.forced_target(b,a) not in (None,t):raise ValueError('You must target the unit drawing your attention')
  if not c.bard.can_attack(a):raise ValueError('Attacks are prevented here')
  if c._apply_attack_approach(b,a,t,s['range'],cmd):return False
  if not c._can_attack(b,a,t,s['range']):raise ValueError('Target is outside technique range')
 normalize(t)
 if k in {'abduct','restraining_hold'} and not stacks(t,'hobbled'):raise ValueError('Apply Hobble first')
 if k=='restraining_hold' and (not isolated(b,a,t)):raise ValueError('Hold requires an isolated Hobbled target')
 route=None
 if k=='abduct':
  route=drag_routes(b,a,t).get(f"{cmd.get('x')},{cmd.get('y')}")
  if not route:raise ValueError('Choose a legal drag destination')
 c._commit_player_movement(b,a)
 if not c._combat_active(a) or a.get('engineer_interrupted'):a['acted']=True;return True
 quick=k=='blitz' or k=='hook_and_drag' and bool(stacks(t,'hobbled'))
 c.abilities.spend(a,s)
 if k=='blitz':
  conditions.apply(a,'captor_blitz',2,a);a['captor_blitz_until']=clock(a)+2
  a['ability_state'][s['id']]['ready_at']=clock(a)
  c.druid.visual(b,a,'captor_blitz','captor_blitz')
 elif k=='restraining_hold':
  a['captor_hold']={'target_id':t['id'],'remaining':stacks(t,'hobbled'),'began':clock(a),'origin':[a['x'],a['y']],'target_origin':[t['x'],t['y']]}
  conditions.remove(t,'hobbled');t['captor_held_by']=a['id']
  conditions.apply(t,'captor_held',1,a);conditions.apply(a,'captor_holding',1,a)
  for u,sid in ((t,'captor_held'),(a,'captor_holding')):status(u,sid).pop('turns',None);feedback(b,u,'status',status_id=sid)
  a['ability_state'][s['id']]['ready_at']=clock(a)
  c.druid.visual(b,a,'captor_restraining_hold','captor_hold',t)
 elif k=='abduct':
  origin={'x':a['x'],'y':a['y']};target_origin={'x':t['x'],'y':t['y']}
  # Sequential paired steps use the same committed hazard hooks as walking/pushes.
  for point in route['path']:
   old={'x':a['x'],'y':a['y']};a.update(point);t.update(old)
   for u in (a,t):
    if u.get('carrying') in b['units']:b['units'][u['carrying']].update(x=u['x'],y=u['y'])
   c._record_movement(b,a,(old['x'],old['y']),[(a['x'],a['y'])]);c._apply_zone_route(b,a,[(a['x'],a['y'])])
   c._record_movement(b,t,(target_origin['x'],target_origin['y']),[(t['x'],t['y'])]);b['animation_events'][-1]['forced']=True;c._apply_zone_route(b,t,[(t['x'],t['y'])]);target_origin={'x':t['x'],'y':t['y']}
   if not c._combat_active(a) or not c._combat_active(t) or a.get('engineer_interrupted') or t.get('engineer_interrupted'):break
  a.pop('movement_origin',None);a.pop('movement_path',None)
  conditions.apply(t,'captor_abducted',1,a);feedback(b,t,'status',status_id='captor_abducted')
  c.druid.visual(b,a,'captor_abduct','captor_drag')
 elif k=='restraint':
  control(b,a,t,'disarm',2)
  if control(b,a,t,'hobbled',2):status(t,'hobbled')['movement_cap']=1
  c.druid.visual(b,a,'captor_restraint','captor_hold',t)
 else:
  hit,packet=strike(b,a,t,k)
  if hit and c._combat_active(t) and k=='subduing_blow' and roll(b,a,t,'control_proc')<25:
   sid=('hobbled','disarm','stun')[int(roll(b,a,t,'control_choice')//(100/3))];control(b,a,t,sid,2 if sid!='stun' else 1,packet)
  if hit and c._combat_active(t) and k=='bola':
   for _ in range(4):
    if roll(b,a,t,'hobble')<conditions.status_chance(t,'hobbled'):conditions.add_stack(t,'hobbled',4,a)
   feedback(b,t,'status',status_id='hobbled',attack_packet=packet)
  if hit and c._combat_active(t) and k=='hook_and_drag':c._apply_displacement(b,a,t,{'mode':'pull','distance':2,'stop_adjacent':True,'collision_damage':False},0,packet)
  c._record_sound(b,'captor_bola' if k=='bola' else 'captor_drag' if k=='hook_and_drag' else 'captor_hold');b['animation_events'][-1]['attack_packet']=packet
 a['acted']=not quick;cleanup(b);return not quick

def previews(b,a,s,reachable,parents):
 from . import combat as c
 if not c.abilities.availability(a,s)['available']:return {}
 k=s['captor_kind']
 if k=='blitz' or k=='restraining_hold' and a.get('captor_hold'):return {a['id']:{'chance':100,'support':True}}
 result={}
 for t in c._living(b,'enemy' if a['team']=='player' else 'player'):
  if t.get('temporary') or c.concealment.unseen(t):continue
  caster,path=c._attack_position(b,a,t,s['range'],reachable,parents)
  if not caster:continue
  if k in {'abduct','restraining_hold'} and not stacks(t,'hobbled'):continue
  if k=='restraining_hold' and not isolated(b,caster,t):continue
  forecast=preview(b,caster,t,k)
  if k=='restraining_hold':forecast.update(resolve_damage=max(1,round(power(a)*.75*mitigation(t))),damage_note=f"{max(1,round(power(a)*.75*mitigation(t)))} Resolve per tick; capture attempts begin at zero Resolve.")
  if k=='abduct':
   forecast['drag_destinations']=drag_routes(b,caster,t)
   if not forecast['drag_destinations']:continue
  forecast['quick_action']=k=='hook_and_drag' and bool(stacks(t,'hobbled'))
  if k=='hook_and_drag':forecast['displacement']=c._displacement_preview(b,caster,t,{'mode':'pull','distance':2,'stop_adjacent':True,'collision_damage':False})
  result[t['id']]={**forecast,**(path or {})}
 return result

def presentation(b,u):
 normalize(u)
 if u.get('captor_hold'):
  for sid in ('captor_holding',):
   if status(u,sid):status(u,sid)['remaining']=u['captor_hold']['remaining']
  for s in u.get('skills',[]):
   if s.get('captor_kind')=='restraining_hold':s.update(name='Release Hold',description='Release your prisoner without spending an action.',self_only=True,target='ally',quick_action=True)
  if (u.get('special') or {}).get('captor_kind')=='restraining_hold':u['special']=next((s for s in u['skills'] if s.get('captor_kind')=='restraining_hold'),u['special'])
 u['capture_details']={'resolve_reduction':round((1-mitigation(u))*100,1),'base_chance':u.get('base_capture_chance',1 if u.get('boss') or u.get('kind')=='chieftain' else 35)}

def auto(b,a,targets):
 from . import combat as c
 if a.get('captor_hold'):return True
 profile=a.get('capture_weapon')
 ready=next((t for t in targets if t.get('resolve',t.get('max_hp',1))==0 and not t.get('temporary') and profile and c._can_attack(b,a,t,profile['range'])),None)
 if ready and not status(a,'disarm') and c.bard.can_attack(a):
  c._capture_attempt(b,a,ready);a['acted']=True;return True
 skills=[s for s in a.get('skills',[]) if s.get('captor_kind') and c.abilities.availability(a,s)['available']]
 for s in sorted(skills,key=lambda s:0 if s['captor_kind']=='restraining_hold' else 1 if s['captor_kind']=='subduing_blow' else 2):
  if s['captor_kind'] in {'abduct','blitz'}:continue
  t=next((t for t in targets if c._can_attack(b,a,t,s['range']) and not t.get('temporary') and (s['captor_kind']!='restraining_hold' or stacks(t,'hobbled') and isolated(b,a,t))),None)
  if t:
   command(b,a,s,{'target_id':t['id']})
   if a.get('acted'):return True
 return False
