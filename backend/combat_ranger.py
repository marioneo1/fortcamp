"""Ranger's bounded ranged techniques; existing damage, turns, statuses and actions."""
from copy import deepcopy
import random
from . import combat_conditions as conditions
from .combat_feedback import record as feedback
from . import combat_dots as dots
ATTACKS={'longshot','multi_shot','poison_attack','pestilence_shot','rupturing_blow'}
def has_sharpshooter(u):return any(p.get('id')=='job:ranger:sharpshooter' for p in u.get('passives',[]))
def marked(a,t):return any(s['id']=='mark' and s.get('quarry') and s.get('source_id')==a['id'] for s in t.get('statuses',[]))
def steady(u):return has_sharpshooter(u) and u.get('ranger_stationary_tile')==[u['x'],u['y']]
def sync(u):
 if not has_sharpshooter(u):return
 base=u.setdefault('ranger_base_range',u['attack_range']);u['attack_range']=base+(2 if steady(u) else 0)
 conditions.remove(u,'sharpshooter')
 if steady(u):u.setdefault('statuses',[]).append({'id':'sharpshooter'})
def start(u):
 if not has_sharpshooter(u):return
 u['ranger_turn_start']=[u['x'],u['y']];u['ranger_moved_committed']=False;sync(u)
def committed_move(u):
 if not has_sharpshooter(u):return
 if u.get('ranger_stationary_tile')!=[u['x'],u['y']]:u.pop('ranger_stationary_tile',None)
 if u.get('ranger_turn_start')!=[u['x'],u['y']]:u['ranger_moved_committed']=True
 sync(u)
def finish(u):
 if has_sharpshooter(u) and not u.get('ranger_moved_committed') and u.get('ranger_turn_start')==[u['x'],u['y']] and u.get('alive',True) and u.get('conscious',True):u['ranger_stationary_tile']=[u['x'],u['y']]
 sync(u)
def skill_for(u,s):
 if not s or not s.get('ranger_kind'):return s
 s=deepcopy(s);base=s.setdefault('range_base',s['range']);s['range']=base+(2 if steady(u) else 0)
 return s
def power(a,t,kind):
 from . import combat as c
 d=c._distance(a,t)
 return (100 if d<=2 else 150 if d==3 else 175 if d==4 else 200) if kind=='longshot' else 75 if kind=='multi_shot' else 150 if kind in {'poison_attack','rupturing_blow'} else 100

def roll(b,a,label,low,high):
 serial=b.get('ranger_roll',0);b['ranger_roll']=serial+1
 return random.Random(f"{b.get('seed')}:ranger:{label}:{a['id']}:{serial}").randint(low,high)
def poison(b,a,t,count,packet=None):
 from . import combat as c
 if not c._combat_active(t):return
 for _ in range(count):
  if roll(b,a,'poison',1,100)<=conditions.status_chance(t,'poison'):
   conditions.add_stack(t,'poison',2,a)
 if conditions.has(t,'poison'):feedback(b,t,'status',status_id='poison',attack_packet=packet)
 c.martial.flush(b,t)
def dot_potential(t):
 return sum(dots.potential(t,s['id'],dots.count(s)) for s in t.get('statuses',[]) if s['id'] in {'poison','bleed'})

def candidates(b,a,t):
 from . import combat as c
 return [skill_for(a,s) for s in a.get('skills',[]) if s.get('ranger_kind') in ATTACKS and c.abilities.availability(a,s)['available'] and (s['ranger_kind']!='longshot' or marked(a,t)) and c._can_attack(b,a,t,skill_for(a,s)['range'])]
def legal(b,a,t,s):
 from . import combat as c
 if s.get('ranger_kind')=='longshot' and not marked(a,t):return False
 if s.get('ranger_kind')=='rapid_fire':return bool(candidates(b,a,t)) or c._can_attack(b,a,t,a['attack_range'])
 return True

def preview(b,a,t,s):
 from . import combat as c
 s=skill_for(a,s);kind=s['ranger_kind']
 if not legal(b,a,t,s):return None
 if kind=='rapid_fire':
  choices=candidates(b,a,t);rows=[preview(b,a,t,choice) for choice in choices]
  if not rows:rows=[c._strike_preview(b,a,t,a['attack_elevation_rule'],a['attack_range'])]
  return {'chance':min(r.get('chance',100) for r in rows),'damage_on_hit':min(r.get('damage_on_hit',0) for r in rows),'damage_max':max(r.get('damage_max',r.get('damage_on_hit',0)) for r in rows),'rapid_pool':[s['name'] for s in choices] or ['Basic Attack'],'damage_note':'Random legal attack against this target; only Rapid Fire enters cooldown.'}
 plain=deepcopy(s);plain.pop('ranger_kind',None)
 if kind!='mark_quarry':plain['effects'][0]['power_percent']=power(a,t,kind)
 if kind=='multi_shot':plain['ranger_accuracy']=50
 row=c._strike_preview(b,a,t,s['elevation_rule'],s['range'],plain)
 if kind=='multi_shot':
  recipient=c._interceptor(b,a,t,s['range']);probe=deepcopy(recipient);reversal=deepcopy(next((v for v in probe.get('statuses',[]) if v['id']=='iron_reversal'),None));totals=[];total=0
  for index in range(4):
   source=deepcopy(a)
   if index:
    source['on_hit']=None;source['gear_rules']={k:v for k,v in source.get('gear_rules',{}).items() if 'damage' not in k};source['perk_modifiers']={k:v for k,v in source.get('perk_modifiers',{}).items() if 'damage' not in k}
   if reversal and not conditions.has(probe,'iron_reversal'):probe['statuses'].append(deepcopy(reversal))
   amount=c._damage_before_barrier({'animation_events':[]},source,probe,c._ability_power_bonus(source,plain,plain['effects'][0]))
   amount,_=conditions.absorb(probe,amount);total+=amount;totals.append(total)
  row.update(damage_on_hit=totals[1],damage_max=totals[3],hit_count='2-4',damage_note='2-4 arrows, independent accuracy. Damage range assumes every arrow hits; Barrier is depleted across the volley.')
 if kind=='longshot':row.update(crit_chance=20,crit_damage=max(0,(row['damage_on_hit']+row.get('absorbed_damage',0))*2-row.get('barrier',0)),distance_power=power(a,t,kind))
 if kind=='rupturing_blow':row.update(dot_cashout=round(dot_potential(t)*.5),damage_note='Direct hit plus 50% remaining Poison/Bleed damage; Both tick at target turn end and lose one stack each turn. Consumes both on a landed hit.')
 return row

def execute(b,a,t,s,free=False):
 from . import combat as c
 kind=s.get('ranger_kind');s=skill_for(a,s)
 if not c.abilities.availability(a,s)['available']:raise ValueError(c.abilities.availability(a,s)['reason'])
 if not c._can_attack(b,a,t,s['range']):raise ValueError('Target is outside technique range')
 if not legal(b,a,t,s):raise ValueError('Longshot requires your Mark Quarry, or no legal Rapid Fire attack can reach this target')
 c._commit_player_movement(b,a)
 if not c._combat_active(a) or a.get('engineer_interrupted') and c.bard.attack_skill(s):return {'interrupted':True}
 if kind=='mark_quarry':
  conditions.mark(b,a,t,3,0);next(v for v in t['statuses'] if v['id']=='mark' and v['source_id']==a['id'])['quarry']=True
  feedback(b,t,'status',status_id='mark');b['log'].append(f"{a['name']} marks {t['name']}; their own attacks cannot miss while the mark lasts.")
 elif kind=='rapid_fire':
  pool=candidates(b,a,t)
  if pool:
   chosen=pool[roll(b,a,'rapid',0,len(pool)-1)];b['log'].append(f"Rapid Fire selects {chosen['name']}.");execute(b,a,t,chosen,True)
  else:
   c._perform_attack(b,a,t,a['attack_elevation_rule']);b['log'].append(f"Rapid Fire uses a Basic Attack against {t['name']}.")
  a['acted']=False;c.abilities.spend(a,s);c.rogue.freeze_walking(a);a['quick_actions_used']=a.get('quick_actions_used',0)+1
  return {'attacked':True}
 else:
  a['physical_action']=True
  count=roll(b,a,'arrows',2,4) if kind=='multi_shot' else 1;landed=0;damage_total=0
  imbued=conditions.has(a,'poison_imbue');rally=deepcopy(next((v for v in a.get('statuses',[]) if v['id']=='rally_power'),None));original=t;t=c._interceptor(b,a,t,s['range'])
  if t is not original:
   t['reaction_ready']=False;c.concealment.reveal(b,t);b['log'].append(f"{t['name']} intercepts the volley on {original['name']}.")
  remaining=dot_potential(t) if kind=='rupturing_blow' else 0
  reversal=deepcopy(next((v for v in t.get('statuses',[]) if v['id']=='iron_reversal'),None));reversal_used=False
  for index in range(count):
   if not c._combat_active(t):break
   shot=deepcopy(s);shot.pop('ranger_kind',None);shot.update(ranger_attack=True,skip_intercept=True);shot['effects'][0]['power_percent']=power(a,t,kind);shot['on_hit']=a.get('on_hit') if not landed else None
   if kind=='multi_shot':shot['ranger_accuracy']=50
   source=deepcopy(a)
   if rally and not conditions.has(source,'rally_power'):source['statuses'].append(deepcopy(rally))
   if reversal_used and reversal and not conditions.has(t,'iron_reversal'):t['statuses'].append(deepcopy(reversal))
   if landed:
    source['gear_rules']={k:v for k,v in source.get('gear_rules',{}).items() if 'damage' not in k}
    source['perk_modifiers']={k:v for k,v in source.get('perk_modifiers',{}).items() if 'damage' not in k}
   if kind=='longshot':shot['ranger_crit']=roll(b,a,'crit',1,100)<=20
   t,hit,amount,_,_=c._perform_attack(b,source,t,'ballistic',c._ability_power_bonus(source,shot,shot['effects'][0]),ability=shot,defer_reaction=True)
   packet=b.get('attack_serial');landed+=bool(hit);damage_total+=amount
   if hit and reversal:reversal_used=True
   for event in b.get('animation_events',[]):
    if event.get('attack_packet')==packet and event.get('attack_event'):event.update(ranger_skill=kind,hit=hit,arrow_index=index,ranger_poison=imbued or kind in {'poison_attack','pestilence_shot','rupturing_blow'},critical=bool(shot.get('ranger_crit') and hit))
    if event.get('attack_packet')==packet and event.get('type')=='combat_feedback' and event.get('kind')=='physical' and hit and shot.get('ranger_crit'):event['critical']=True
   if hit:
    if imbued and amount>0:poison(b,a,t,1,packet)
    if kind=='poison_attack':poison(b,a,t,4 if marked(a,original) else 2,packet)
    if kind=='pestilence_shot' and c._combat_active(t):
     if roll(b,a,'pestilence',1,100)<=conditions.status_chance(t,'pestilence') and conditions.apply(t,'pestilence',3,a):feedback(b,t,'status',status_id='pestilence',attack_packet=packet)
     else:feedback(b,t,'resisted',status_id='pestilence',attack_packet=packet)
    if kind=='rupturing_blow':
     conditions.remove(t,'poison','bleed')
     if remaining and c._combat_active(t):
      source={'id':a['id'],'name':a['name'],'attack':round(remaining*.5),'weapon':'Rupturing Blow','status_tick':True,'damage_kind':'rupture'}
      before=len(b.get('animation_events',[]));damage_total+=c._deal_damage(b,source,t,armor_pierce=c._effective_armor(t))
      for event in b['animation_events'][before:]:event['attack_packet']=packet
    c.martial.flush(b,t)
   b['log'].append(f"{a['name']} uses {s['name']}: arrow {index+1} {'deals '+str(amount)+' damage' if hit else 'misses'}.")
  if reversal_used:conditions.remove(t,'iron_reversal')
  if imbued and damage_total>0:conditions.remove(a,'poison_imbue')
  if kind=='poison_attack':
   conditions.remove(a,'poison_imbue');a.setdefault('statuses',[]).append({'id':'poison_imbue','source_id':a['id']});feedback(b,a,'status',status_id='poison_imbue')
  c._react_after_attack(b,a,t,bool(landed),'ballistic')
 if not free:c.abilities.spend(a,s)
 a['acted']=True
 return {'hit':bool(landed) if kind!='mark_quarry' else True,'attacked':kind!='mark_quarry'}

def auto(b,a,targets):
 from . import combat as c
 skills=[skill_for(a,s) for s in a.get('skills',[]) if s.get('ranger_kind') and c.abilities.availability(a,s)['available']]
 if not skills or a.get('capture_weapon'):return False
 options=[];reachable,parents=c._movement_tree(b,a)
 for t in targets:
  for s in skills:
   if not legal(b,a,t,s):continue
   actor,path=position(b,a,t,s,reachable,parents)
   if actor is not None:options.append((s,t,path,actor))
 if not options:return False
 rapid=next(((s,t,path,actor) for s,t,path,actor in options if s['ranger_kind']=='rapid_fire' and not path),None)
 if rapid:
  execute(b,a,rapid[1],rapid[0]);
  if not c._combat_active(a):return True
  targets=[t for t in targets if c._combat_active(t)]
  if not targets:a['acted']=True;return True
  skills=[s for s in skills if s['ranger_kind']!='rapid_fire']
  # Rapid Fire commits walking. Do not reuse approaches computed before the shot.
  options=[(s,t,None,a) for t in targets for s in skills if c.abilities.availability(a,s)['available'] and legal(b,a,t,s) and c._can_attack(b,a,t,skill_for(a,s)['range'])]
 if not options:
  if rapid:a['acted']=True
  return bool(rapid)
 def score(v):
  s,t,path,actor=v;k=s['ranger_kind'];p=preview(b,actor,t,s) or {};value=p.get('damage_on_hit',0)+p.get('dot_cashout',0)
  value=value*p.get('chance',100)/100
  if k=='mark_quarry':value=0 if marked(a,t) else a['attack']*2 if t['hp']>a['attack']*3 else 2
  if k=='pestilence_shot' and not conditions.has(t,'pestilence'):value+=6
  if k=='poison_attack':value+=4 if conditions.resistance(t,'poison')<100 else 0
  return (value-(path or {}).get('movement_cost',0)*2,-t['hp'],s['id'])
 s,t,path,actor=max(options,key=score)
 if path and c._apply_attack_approach(b,a,t,s['range'],path):return True
 execute(b,a,t,s);return True


def position(b,a,t,s,reachable,parents):
 from . import combat as c
 if s:
  s=skill_for(a,s);reach=s['range'];base=s.get('range_base',reach)
  if s.get('ranger_kind')=='rapid_fire':
   pool=[skill_for(a,v) for v in a.get('skills',[]) if v.get('ranger_kind') in ATTACKS and c.abilities.availability(a,v)['available'] and (v['ranger_kind']!='longshot' or marked(a,t))]
   reach=max([a['attack_range']]+[v['range'] for v in pool]);base=max([a.get('ranger_base_range',a['attack_range'])]+[v.get('range_base',v['range']) for v in pool])
 else:reach=a['attack_range'];base=a.get('ranger_base_range',reach)
 if c._can_attack(b,a,t,reach):return a,None
 return c._attack_position(b,a,t,base,reachable,parents)
