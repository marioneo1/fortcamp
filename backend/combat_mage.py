"""Mage elemental interactions, bounded delayed casts and existing zone/displacement adapters."""
from copy import deepcopy
import random
from . import combat_conditions as conditions
from .combat_feedback import record as feedback

KINDS={'chain_lightning','flash_freeze','singularity','meteor','fireball','enchant_weapon','typhoon'}
GROUND={'flash_freeze','singularity','meteor','fireball'}
ELEMENTS={'fire','frost','lightning'}

def specialized(a):return any(p.get('id')=='job:mage:debuffer' for p in a.get('passives',[]))
def clock(a):return a.get('ability_activation',0)
def roll(b,a,label):
 serial=b.get('mage_roll',0);b['mage_roll']=serial+1
 return random.Random(f"{b.get('seed')}:mage:{a['id']}:{label}:{serial}").randint(1,100)
def cells(b,center,radius):
 from . import combat as c
 cache=b.get('_mage_preview_cells');key=(center['x'],center['y'],radius)
 if cache is not None and key in cache:return cache[key]
 result=[{'x':x,'y':y} for y in range(max(0,center['y']-radius),min(b['height'],center['y']+radius+1)) for x in range(max(0,center['x']-radius),min(b['width'],center['x']+radius+1)) if abs(x-center['x'])+abs(y-center['y'])<=radius and c._line_of_sight(b,center,{'x':x,'y':y})]
 if cache is not None:cache[key]=result
 return result
def targets(b,a,center,radius,allies=False,include_self=False,preview=False):
 from . import combat as c
 area={(p['x'],p['y']) for p in cells(b,center,radius)}
 candidates=[]
 for u in b['units'].values():
  # Forecast the caster at their proposed approach tile; execution mutates the live unit.
  position=a if u['id']==a['id'] else u
  if c._combat_active(u) and (include_self or u['id']!=a['id']) and (allies or u['team']!=a['team'] or u.get('mercenary_hostile_all')) and (position['x'],position['y']) in area:
   candidates.append(position if preview else u)
 return sorted(candidates,key=lambda u:(c._distance(center,u),u['id']))
def duration(a,turns):return turns*(2 if specialized(a) else 1)
def status(b,a,t,sid,turns=2,chance=100,packet=None,metadata=None):
 from . import combat as c
 if not c._combat_active(t):return False
 applied=roll(b,a,sid)<=conditions.status_chance(t,sid,chance) and conditions.apply(t,sid,turns if sid in conditions.RECOVERY else duration(a,turns),a)
 if applied and metadata:next(s for s in t['statuses'] if s['id']==sid).update(metadata)
 feedback(b,t,'status' if applied else 'resisted',status_id=sid,attack_packet=packet)
 c.martial.flush(b,t)
 return applied
def freeze(b,a,t,turns=2,chance=100,packet=None):
 applied=status(b,a,t,'freeze',turns,chance,packet,metadata={'elemental_freeze':True,'wet_turns':duration(a,2)})
 if not applied:status(b,a,t,'wet',2,packet=packet)
 return applied
def burn(b,a,t,count=1,packet=None):
 from . import combat as c
 if not c._combat_active(t):return
 for _ in range(count*(2 if specialized(a) else 1)):
  if roll(b,a,'burn')<=conditions.status_chance(t,'burn'):conditions.add_stack(t,'burn',1,a)
 if conditions.has(t,'burn'):feedback(b,t,'status',status_id='burn',attack_packet=packet)
 c.martial.flush(b,t)
def ground_burn(b,a,t):
 from . import combat as c
 count=2 if a['scorched_source'].get('burn_debuffer') else 1
 for _ in range(count):conditions.add_stack(t,'burn',1,a)
 feedback(b,t,'status',status_id='burn')
 c._tick_dot_status(b,t,'burn')

def enchant_hit(b,a,t,ability=None):
 from . import combat as c
 live=b['units'].get(a.get('id'),a)
 s=next((s for s in live.get('statuses',[]) if s['id']=='weapon_enchant'),None)
 if not s or a.get('mage_spell') or a.get('nonlethal_floor') or a.get('capture_only') or (ability or {}).get('mage_kind') or (ability and (ability or {}).get('elevation_rule',a.get('attack_elevation_rule')) in {'ignore','line_of_effect','physical_care'}) or a.get('status_tick') or a.get('reaction_attack') or a.get('collision_attack') or not c._combat_active(t):return
 owner=b['units'].get(s.get('source_id')) or {'id':s.get('source_id'),'name':s.get('source_name','Enchantment'),'attack':s['source_attack']}
 owner={**owner,'attack':s['source_attack'],'passives':[{'id':'job:mage:debuffer'}] if s.get('debuffer') else []}
 if s['element']=='fire':burn(b,owner,t)
 elif s['element']=='frost':
  if roll(b,a,'enchant_frost')<=20:freeze(b,owner,t,chance=100)
 elif conditions.has(t,'wet') and t['id'] not in s.setdefault('paralyzed_targets',[]):
  if status(b,owner,t,'paralyze',1,25):s['paralyzed_targets'].append(t['id'])
def interrupt(b,a,reason):
 if a.pop('mage_channel',None):
  conditions.remove(a,'channeling');b['log'].append(f"{a['name']}'s Meteor is interrupted: {reason}.")
  b['mage_delays']=[d for d in b.get('mage_delays',[]) if not (d['owner_id']==a['id'] and d['kind']=='meteor')]
  feedback(b,a,'resisted',status_id='channeling')
def check_channel(b,a):
 from . import combat as c
 channel=a.get('mage_channel')
 if channel and (not c._combat_active(a) or any(conditions.has(a,s) for s in conditions.RECOVERY|{'mute'}) or [a['x'],a['y']]!=channel['origin']):interrupt(b,a,'control, silence, displacement or defeat')
def packet(b,a,kind,center,radius=0,origin=None):
 b['attack_serial']=b.get('attack_serial',0)+1;p=b['attack_serial']
 b.setdefault('animation_events',[]).append({'type':'mage_cast','attack_event':True,'unit_id':a['id'],'mage_skill':kind,'x':center['x'],'y':center['y'],'radius':radius,'from_point':origin or {'x':a['x'],'y':a['y']},'attack_packet':p,'contact_ms':420 if kind=='meteor' else 240})
 return p
def damage(b,a,t,kind,power,p,center=None):
 from . import combat as c
 source={**a,'mage_spell':True,'on_hit':None,'attack_elevation_rule':'ignore','element':'lightning' if kind=='chain_lightning' else 'fire' if kind in {'fireball','meteor'} else None}
 start=len(b['animation_events']);c.concealment.reveal(b,t,'contact')
 hit,preview,_=c._attack_hits(b,source,t,'ignore',{'range':20})
 amount=c._deal_damage(b,source,t,c.martial.attack_power(source)*power//100-c.martial.attack_power(source)+preview['damage_bonus']) if hit else 0
 if not hit:feedback(b,t,'miss')
 for e in b['animation_events'][start:]:e['attack_packet']=p
 b['log'].append(f"{a['name']}'s {kind.replace('_',' ').title()} {'deals '+str(amount)+' damage to' if hit else 'misses'} {t['name']}.")
 return hit,amount

def scorch(b,a,center,radius,impact_packet=None):
 from . import combat as c
 area=cells(b,center,radius)
 effect={'type':'zone','zone':'scorched','radius':0,'turns':2}
 zone=c.spaces.place_zone(b,a,effect,area);zone.update(burn_debuffer=specialized(a))
 if impact_packet is not None:b.setdefault('animation_events',[]).append({'type':'zone_created','zone_id':zone['id'],'cells':area,'attack_packet':impact_packet})

def impact(b,a,kind,center):
 from . import combat as c
 radius=3 if kind in {'meteor','typhoon'} else 2
 # Keep this cast's power stable even if self-contact burns, debuffs or kills its caster.
 victims=targets(b,a,center,radius,True,kind in GROUND);a=deepcopy(a);p=packet(b,a,kind,center,radius)
 # Snapshot positions/area first; push inner units before their outer collision victims.
 for t in victims:
  b['attack_serial']+=1;child=b['attack_serial'];begin=len(b['animation_events'])
  wet=conditions.has(t,'wet');distance=c._distance(center,t)
  power=(400 if distance<=2 else 300) if kind=='meteor' else (150 if distance==0 else 125) if kind=='fireball' else (200 if distance==0 else 25) if kind=='singularity' else 25
  hit,amount=damage(b,a,t,kind,power,child,center)
  if kind=='fireball' and hit:
   burn(b,a,t,packet=child)
   if conditions.has(t,'wet'):conditions.remove(t,'wet');status(b,a,t,'blister',2,packet=child)
  if kind=='meteor' and hit:burn(b,a,t,packet=child)
  if kind=='typhoon':status(b,a,t,'wet',2,packet=child)
  if hit and kind in {'singularity','typhoon'}:
   origin={**a,'x':center['x'],'y':center['y']}
   if distance:c._apply_displacement(b,origin,t,{'mode':'pull' if kind=='singularity' else 'push','distance':1 if kind=='singularity' else 2},amount,child)
  for event in b['animation_events'][begin:]:event.update(attack_packet=child,impact_origin_packet=p,impact_offset=0)
 if kind in {'fireball','meteor'}:scorch(b,a,center,radius,p)
 c.engineer.area_hit(b,a,cells(b,center,radius),p)
 conditions.remove(b['units'].get(a['id'],a),'rally_power')
 return {'attacked':True}
def chain(b,a,t):
 from . import combat as c
 seen=set();primary=True;root_packet=None;origin={'x':a['x'],'y':a['y']}
 while t and t['id'] not in seen:
  seen.add(t['id']);wet=conditions.has(t,'wet');p=packet(b,a,'chain_lightning',t,origin=origin)
  if root_packet is None:root_packet=p
  else:b['animation_events'][-1].update(impact_origin_packet=root_packet,impact_offset=(len(seen)-1)*120)
  begin=len(b['animation_events'])
  hit,_=damage(b,a,t,'chain_lightning',(250 if wet else 150) if primary else (175 if wet else 125),p)
  if hit and wet:status(b,a,t,'paralyze',1,25,p)
  if p!=root_packet:
   for event in b['animation_events'][begin:]:event.update(impact_origin_packet=root_packet,impact_offset=(len(seen)-1)*120)
  candidates=[u for u in b['units'].values() if c._combat_active(u) and u['id'] not in seen and u['team']!=a['team'] and c._distance(t,u)<=2 and c._line_of_sight(b,t,u)]
  origin={'x':t['x'],'y':t['y']};primary=False
  t=min(candidates,key=lambda u:(c._distance(origin,u),u['id'])) if candidates else None
 conditions.remove(a,'rally_power')
 return {'attacked':True}
def execute(b,a,t,s,element=None):
 from . import combat as c
 if not c.abilities.availability(a,s)['available']:raise ValueError(c.abilities.availability(a,s)['reason'])
 if s['mage_kind']=='enchant_weapon' and element not in ELEMENTS:raise ValueError('Choose Fire, Frost or Lightning')
 c._commit_player_movement(b,a)
 if not c._combat_active(a) or a.get('engineer_interrupted') and c.bard.attack_skill(s):return {'interrupted':True}
 kind=s['mage_kind']
 if kind=='chain_lightning':result=chain(b,a,t)
 elif kind in {'fireball','singularity','typhoon'}:result=impact(b,a,kind,t)
 elif kind=='enchant_weapon':
  conditions.apply(t,'weapon_enchant',duration(a,2),a);enchant=next(v for v in t['statuses'] if v['id']=='weapon_enchant')
  enchant.update(element=element,source_attack=c.martial.attack_power(a),debuffer=specialized(a),paralyzed_targets=[])
  packet(b,a,kind,t);b['animation_events'][-1]['enchant_element']=element;feedback(b,t,'status',status_id='weapon_enchant');result={'support':True}
 else:
  delay={'kind':kind,'owner_id':a['id'],'due':clock(a)+1,'center':{'x':t['x'],'y':t['y']},'source':deepcopy(a)}
  b.setdefault('mage_delays',[]).append(delay)
  if kind=='meteor' and not conditions.has(a,'bard_accelerando'):
   conditions.remove(a,'rally_power')
   a['mage_channel']={'origin':[a['x'],a['y']]};a.setdefault('statuses',[]).append({'id':'channeling'})
  if kind=='meteor' and conditions.has(a,'bard_accelerando'):
   b['mage_delays'].remove(delay)
   result=impact(b,{**a,'x':a['x'],'y':a['y']},'meteor',{'x':t['x'],'y':t['y']})
   b['log'].append(f"{a['name']} casts {s['name']} through Accelerando without Channeling.")
  else:
   packet(b,a,kind+'_armed',t,3 if kind=='meteor' else 2)
   b['log'].append(f"{a['name']} prepares {s['name']}: "+('lands on their next activation and spends it; control, silence or displacement interrupts.' if kind=='meteor' else 'freezes everyone still inside, including allies and the caster, after their next activation.'))
   result={'delayed':False if kind=='meteor' and conditions.has(a,'bard_accelerando') else True}
 c.abilities.spend(a,s);a['acted']=True
 return result
def settle(b,a,phase):
 from . import combat as c
 check_channel(b,a)
 for d in list(b.get('mage_delays',[])):
  if d['owner_id']!=a['id'] or d['due']>clock(a) or phase!=('start' if d['kind']=='meteor' else 'end'):continue
  b['mage_delays'].remove(d)
  if not c._combat_active(a):continue
  source={**d['source'],'x':a['x'],'y':a['y'],'ability_activation':clock(a),'status_activation':deepcopy(a.get('status_activation'))}
  if d['kind']=='meteor':
   if not a.get('mage_channel'):continue
   a.pop('mage_channel',None);conditions.remove(a,'channeling');impact(b,source,'meteor',d['center']);a['forced_skip']=True;a['acted']=True
  else:
   p=packet(b,source,'flash_freeze',d['center'],2)
   for t in targets(b,source,d['center'],2,True,True):freeze(b,source,t,packet=p)

def presentation(b):
 from . import combat as c
 return [{'id':f"mage-delay-{i}",'kind':d['kind']+'_armed','name':'Meteor: incoming' if d['kind']=='meteor' else 'Flash Freeze: armed','cells':cells(b,d['center'],3 if d['kind']=='meteor' else 2),'owner_id':d['owner_id'],'owner_name':d['source']['name'],'remaining':max(0,d['due']-clock(b['units'].get(d['owner_id'],{}))),'description':'Danger to allies and caster: leave the marked ground before impact. '+('Interrupt the caster to stop Meteor.' if d['kind']=='meteor' else 'Triggers after the caster’s next action.')} for i,d in enumerate(b.get('mage_delays',[])) if c._combat_active(b['units'].get(d['owner_id'],{}))]
def preview(b,a,t,s):
 from . import combat as c
 kind=s['mage_kind'];radius=3 if kind in {'meteor','typhoon'} else 2
 if kind=='enchant_weapon':return {'chance':100,'support':True,'damage_on_hit':0,'damage_note':'Choose Fire, Frost or Lightning; lasts '+str(duration(a,2))+' ally turns.'}
 if kind=='chain_lightning':
  targets_=[t];seen={t['id']}
  while True:
   options=[u for u in b['units'].values() if c._combat_active(u) and u['team']!=a['team'] and u['id'] not in seen and c._distance(targets_[-1],u)<=2 and c._line_of_sight(b,targets_[-1],u)]
   if not options:break
   nxt=min(options,key=lambda u:(c._distance(targets_[-1],u),u['id']));seen.add(nxt['id']);targets_.append(nxt)
 else:targets_=targets(b,a,t,radius,True,kind in GROUND,preview=True)
 forecasts={};tactics=[]
 for index,victim in enumerate(targets_):
  d=c._distance(t,victim);wet=conditions.has(victim,'wet')
  power=((250 if wet else 150) if index==0 else (175 if wet else 125)) if kind=='chain_lightning' else (400 if d<=2 else 300) if kind=='meteor' else (150 if not d else 125) if kind=='fireball' else (200 if not d else 25) if kind=='singularity' else 25 if kind=='typhoon' else 0
  probe=deepcopy(victim);source={**a,'mage_spell':True,'on_hit':None,'attack_elevation_rule':'ignore','element':'lightning' if kind=='chain_lightning' else 'fire' if kind in {'fireball','meteor'} else None}
  amount=c._damage_before_barrier({'animation_events':[]},source,probe,c.martial.attack_power(a)*power//100-c.martial.attack_power(a)) if power else 0
  shield=max((v.get('amount',0) for v in victim.get('statuses',[]) if v['id']=='barrier'),default=0)
  forecasts[victim['id']]={'chance':c._attack_preview(b,source,victim,'ignore',s)['chance'],'damage_on_hit':max(0,amount-shield),'delayed':kind in {'meteor','flash_freeze'}}
  if kind in {'typhoon','singularity'} and d:
   origin={**a,'x':t['x'],'y':t['y']};entry=c._displacement_preview(b,origin,victim,{'mode':'push' if kind=='typhoon' else 'pull','distance':2 if kind=='typhoon' else 1})
   entry.update(type='push' if kind=='typhoon' else 'pull',unit_id=victim['id'],collision_damage=max(1,amount//2) if entry.get('solid_collision') else 0);tactics.append(entry)
 row=forecasts.get(t.get('id'),{'chance':100,'damage_on_hit':0})
 return {**row,'target_forecasts':forecasts,'zones':[{'kind':'impact','cells':cells(b,t,radius)}] if kind!='chain_lightning' else [],'tactics':tactics,'damage_note':'Forecast uses current positions; units may leave delayed areas. '+('Typhoon also hits and pushes allies.' if kind=='typhoon' else 'Hits allies and caster too. Scorched ground burns everyone.' if kind in {'fireball','meteor'} else 'Affects allies and caster too; collisions and status ticks are separate.' if kind in GROUND else 'Enemy-only chain; direct damage and status ticks are separate.')}
def view_previews(b,a,s,reachable,parents):
 from . import combat as c
 ground={};units={}
 paths=b.get('_mage_preview_paths')
 def position(t):
  key=(a['id'],a['x'],a['y'],t['x'],t['y'],s['range'])
  if paths is not None and key in paths:return paths[key]
  result=c._attack_position(b,a,t,s['range'],reachable,parents)
  if paths is not None:paths[key]=result
  return result
 if not c.abilities.availability(a,s)['available']:return ground,units
 if s['mage_kind'] in GROUND:
  for y in range(b['height']):
   for x in range(b['width']):
    t=c._ground_target(x,y);actor,path=position(t)
    if actor:ground[f'{x},{y}']={**preview(b,actor,t,s),**(path or {})}
 else:
  candidates=[a] if s['mage_kind']=='typhoon' else c._living(b,a['team']) if s['mage_kind']=='enchant_weapon' else [u for u in b['units'].values() if c._combat_active(u) and u['team']!=a['team']]
  for t in candidates:
   actor,path=position(t)
   units[t['id']]={**preview(b,actor,t,s),**(path or {})} if actor else None
 return ground,units

def command(b,a,s,cmd):
 from . import combat as c
 kind=s['mage_kind'];t=b['units'].get(cmd.get('target_id'))
 if not c.abilities.availability(a,s)['available']:raise ValueError(c.abilities.availability(a,s)['reason'])
 if kind=='enchant_weapon' and cmd.get('element') not in ELEMENTS:raise ValueError('Choose Fire, Frost or Lightning')
 if kind in GROUND:
  if t:t=c._ground_target(t['x'],t['y'])
  else:
   x,y=cmd.get('x'),cmd.get('y')
   if isinstance(x,bool) or isinstance(y,bool) or not isinstance(x,int) or not isinstance(y,int) or not 0<=x<b['width'] or not 0<=y<b['height']:raise ValueError('Choose ground inside the map')
   t=c._ground_target(x,y)
 elif kind=='typhoon':
  if t is not a:raise ValueError('Target yourself with Typhoon')
 elif not t or not c._combat_active(t) or (kind=='enchant_weapon' and t['team']!=a['team']) or (kind=='chain_lightning' and (t['team']==a['team'] or c.concealment.unseen(t))):raise ValueError('Choose a valid visible target')
 if c._apply_attack_approach(b,a,t,s['range'],cmd):return False
 if not c._can_attack(b,a,t,s['range']):raise ValueError('Target is outside spell range or sight')
 execute(b,a,t,s,cmd.get('element'));return True

def auto(b,a,opponents):
 from . import combat as c
 if not opponents or a.get('capture_weapon'):return False
 skills=[s for s in a.get('skills',[]) if s.get('mage_kind') and c.abilities.availability(a,s)['available']]
 options=[]
 for s in skills:
  kind=s['mage_kind']
  if kind=='enchant_weapon':
   allies=[u for u in c._living(b,a['team']) if u['id']!=a['id'] and u.get('attack_elevation_rule') in {'melee','ballistic'} and not conditions.has(u,'weapon_enchant') and c._can_attack(b,a,u,s['range'])]
   if allies:options.append((1,s,max(allies,key=lambda u:u['attack'])))
   continue
  for t in ([a] if kind=='typhoon' else opponents):
   if not c._can_attack(b,a,t,s['range']):continue
   area=targets(b,a,t,3 if kind in {'meteor','typhoon'} else 2,kind!='chain_lightning',kind in GROUND)
   if kind in GROUND|{'typhoon'} and any(u['team']==a['team'] and not u.get('mercenary_hostile_all') for u in area):continue
   if kind=='chain_lightning':score=len(preview(b,a,t,s)['target_forecasts'])+3*sum(conditions.has(u,'wet') for u in opponents)
   else:score=len(area)*2+(1 if kind=='fireball' else 0)
   if score:options.append((score,s,t))
 if not options:return False
 _,s,t=max(options,key=lambda row:(row[0],row[1]['id']))
 execute(b,a,t,s,'lightning' if any(conditions.has(u,'wet') for u in opponents) else 'fire');return True
