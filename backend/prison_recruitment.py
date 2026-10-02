"""Persistent captive terms, warden sessions and one-time allegiance rewards."""
from copy import deepcopy
import hashlib
import time
from .relationships import ensure_character

ROUTES = {
 'debt': ('Settle an old debt', 'My family owes a road broker. Pay the debt and they can leave safely.', 'gold'),
 'rebuild': ('Rebuild a refuge', 'Our camp burned. We need timber for roofs and a fence before I can leave my people.', 'wood'),
 'wounded': ('Care for the wounded', 'The survivors are still sick. Bring medicine for them and I will hear your offer.', 'medicine'),
 'heirloom': ('Recover a field tool', 'Bring me a Field Pack. I lost mine during the fighting; I need it to guide the survivors out.', 'field_pack'),
 'rival': ('Break a rival warband', 'A rival warband controls the road my people use. Break their hold and I will join you.', None),
 'former': ('End the old command', 'My former commanders sent us to die. End their warband’s hold over us and I will serve with you.', None),
 'proof': ('Prove your strength', 'You beat me. Now show that you can defeat the fighters who drove us from our ground.', None),
 'rescue': ('Bring someone home', 'Someone from our camp is being moved in a prisoner wagon. Get them out alive.', None),
}

def initialize_prisoner(p, rank='E', now=None):
 now=int(time.time()) if now is None else now
 if 'recruitment' in p:return p
 tier='EDCBAS'.find(rank);tier=max(0,tier)
 elite=bool(p.get('boss'));kind=p.get('kind','combatant')
 digest=hashlib.sha256(str(p.get('capture_key',p['id'])).encode()).digest()
 route=list(ROUTES)[digest[0]%len(ROUTES)]
 attrs={a:4 for a in ('str','dex','agi','vit','int','luk')}
 # Authored recruit baselines, not reverse-engineered encounter HP/damage.
 attrs.update(str=7 if elite else 5,dex=7 if kind=='archer' else 4,agi=6 if kind=='archer' else 5,vit=6 if elite else 4)
 for a in ('str','vit'):attrs[a]+=min(3,tier//2)
 candidate=deepcopy(p.get('recruitable_snapshot') or {})
 candidate.setdefault('attributes',attrs)
 candidate.update(id=p['id'],name=p['name'],race=p.get('race','Human'),gender=p.get('gender',''),
  portrait=p.get('portrait',''),portrait_thumbnail=p.get('portrait_thumbnail',''),portrait_pool=p.get('portrait_pool',''),
  is_player=False,status='idle',assignment=None)
 candidate.setdefault('source_kind','generic');candidate.setdefault('source_id','captive:'+p['id'])
 candidate.setdefault('traits',[]);candidate.setdefault('perks',{'combat':'skilled' if elite else 'basic'})
 candidate.setdefault('equipment',{s:None for s in ('weapon','offhand','head','body','hands','legs','feet','accessory')})
 candidate.setdefault('specialty','scout' if kind=='archer' else 'fighter');candidate.setdefault('archetype_id','scout' if kind=='archer' else 'fighter')
 candidate.update(portrait_locked=bool(p.get('portrait')),portrait_source='pool' if p.get('portrait') else 'none',hp=100,max_hp=100,morale=60,loyalty=65)
 ensure_character(candidate)
 cost={'gold':180+120*tier+(300 if elite else 0),'wood':30+15*tier+(30 if elite else 0),'medicine':8+4*tier+(8 if elite else 0),'field_pack':1}.get(ROUTES[route][2],0)
 item_id='ironcap_buckler' if elite and p.get('race') in ('Goblin','Hobgoblin') else 'breaching_charge' if elite else 'field_pack'
 text=ROUTES[route][1]
 if route=='heirloom' and elite:
  text='Bring an Ironcap Buckler so my new guard can hold the camp road.' if item_id=='ironcap_buckler' else 'Bring a Breaching Charge. My people are trapped behind a sealed gate; I need a way to break it.'
 if route=='wounded' and p.get('race') in ('Undead','Revenant','Banshee','Vampire'):
  text='The living keepers who guard our resting places are sick. Bring medicine for them and I will hear your offer.'
 requires_proof=elite and tier>=3 and ROUTES[route][2] is not None
 if requires_proof:text+=' After that, defeat the fighters occupying our ground. I need proof that you can keep this promise safe.'
 p['recruitment']={'route':route,'rank':rank,'revealed':False,'resistance':36 if elite else 18,
  'terms_text':text,'terms_title':ROUTES[route][0],'requested_item':item_id if route=='heirloom' else None,
  'requires_proof':requires_proof,'payment_met':False,'quest_route':'proof' if requires_proof else route,
  'requires_terms':elite,'terms_met':False,'cost':cost,'quest_id':None,'candidate':candidate,
  'profile_note':'Base attributes before proficiency and equipment bonuses. You supply their equipment; encounter-only health, phases and reinforcements do not carry over.',
  'created_at':now}
 return p

def warden_for(state,p):
 secured=sorted((q for q in state.get('prisoners',[]) if q.get('holding')=='prison_cell'),key=lambda q:(q.get('captured_at',0),q['id']))
 cells=sorted((b for b in state.get('buildings',[]) if b.get('type')=='prison_cell'),key=lambda b:b['id'])
 index=next((i for i,q in enumerate(secured) if q['id']==p['id']),-1)
 if index<0:return None
 building=cells[index//4] if index//4<len(cells) else None
 return next((c for c in state.get('characters',[]) if building and c['id'] in building.get('assigned',[]) and c.get('status')=='idle'),None)

def prisoner_interaction(state,p,action,items,now=None):
 now=int(time.time()) if now is None else now
 initialize_prisoner(p,now=now);r=p['recruitment'];route=r['route'];label,story,resource=ROUTES[route]
 if action=='talk':
  r['revealed']=True
  return {'text':r.get('terms_text',story),'title':label}
 if action=='negotiate':
  if p.get('holding')!='prison_cell':raise ValueError('Secure this prisoner in a cell before negotiating.')
  warden=warden_for(state,p)
  if not warden:raise ValueError('Assign an available warden to this prisoner’s cell first.')
  clocks=state.setdefault('prison_warden_sessions',{})
  if now<int(clocks.get(warden['id'],0)):raise ValueError('This warden needs a rest between negotiations. Sessions are shared across their prisoners.')
  if r['resistance']<=0:raise ValueError('Resistance is already lowered. Offer recruitment or discuss their terms.')
  from .game import effective_attribute
  progress=min(12,4+effective_attribute(state,warden,'int')//2)
  r['resistance']=max(0,r['resistance']-progress);clocks[warden['id']]=now+1800
  return {'text':f"{warden['name']} listened to {p['name']} and worked through their objections. Resistance fell by {progress}.",'progress':progress}
 if action=='fulfill':
  if not r['revealed']:raise ValueError('Talk to the prisoner to learn their terms first.')
  if r['terms_met'] or r.get('payment_met'):raise ValueError('This payment has already been fulfilled.')
  if resource is None:raise ValueError('Complete their Private Contract to meet these terms.')
  if p.get('holding')!='prison_cell':raise ValueError('Secure the prisoner before making an agreement.')
  if resource in ('gold','wood','medicine'):
   if state['resources'].get(resource,0)<r['cost']:raise ValueError(f"You need {r['cost']} {resource}.")
   state['resources'][resource]-=r['cost']
  else:
   equipped={v for c in state.get('characters',[]) for v in c.get('equipment',{}).values()}
   requested=r.get('requested_item') or resource
   item=next((i for i in state.get('inventory',[]) if i['item_id']==requested and i['instance_id'] not in equipped),None)
   if not item:raise ValueError(f"Bring an unequipped {items[requested]['name']}.")
   state['inventory'].remove(item)
  r['payment_met']=True
  if r.get('requires_proof'):
   return {'text':f"{p['name']} accepted the supplies. Complete their proof-of-strength Private Contract to finish the agreement."}
  r['terms_met']=True
  return {'text':f"{p['name']} accepted the agreement. They are ready to join if you offer a place."}
 if action=='recruit':
  if p.get('holding')!='prison_cell':raise ValueError('Secure the prisoner before recruiting.')
  if not r['terms_met'] and (r['requires_terms'] or r['resistance']>0):raise ValueError('Meet their terms, or lower resistance if the ordinary recruitment route is available.')
  c=deepcopy(r['candidate']);c['loyalty']=80 if r['terms_met'] else 70
  if c.get('source_kind') in ('champion','celestial'):
   raise ValueError('This unique character requires an authored acquisition path.')
  c['allegiance_history']={'route':route,'captured_from':p.get('captured_from_name'),'terms_met':r['terms_met']}
  if any(q['id']==c['id'] for q in state.get('characters',[])):raise ValueError('This character has already joined.')
  state['characters'].append(c);state['prisoners'].remove(p)
  return {'text':f"{c['name']} joined your roster with {c['loyalty']} loyalty.",'character_id':c['id']}
 raise ValueError('Unknown prisoner interaction')

def credit_allegiance(state,analysis,outcome,story):
 pid=analysis.get('prisoner_allegiance_id')
 if not pid or outcome not in ('success','critical_success'):return
 p=next((p for p in state.get('prisoners',[]) if p['id']==pid),None)
 if not p:return
 r=p.get('recruitment',{})
 if r.get('route')!=analysis.get('prisoner_allegiance_route') or r.get('terms_met'):return
 if r.get('requires_proof') and not r.get('payment_met'):return
 r['terms_met']=True
 story.append(f"You kept your promise to {p['name']}. Their recruitment terms are fulfilled; speak with them at the prison to offer a place.")

def apply_prison_contracts(missions):
 from .tactical_contracts import TACTICAL_CONTRACTS
 for route in ('rival','former','proof','rescue'):
  for rank in 'EDCBAS':
   key=f'prison_{route}_{rank.lower()}'
   source='goblin_captive_cart' if route=='rescue' else 'highway_ambush'
   if source not in missions:source='goblin_warcamp'
   m=deepcopy(missions[source]);tier='EDCBAS'.index(rank)
   m.update(name={'rival':'Break the Rival Warband','former':'End the Old Command','proof':'A Promise Proven in Battle','rescue':'Bring the Captive Home'}[route],
    rank=rank,description=ROUTES[route][1],party_size=1 if tier<2 else min(4,2+(tier-2)//2),
    difficulty=9+2*tier,durations=[1],chain_only=True,pool_weight=0,roles=[],claim_requirements=[],critical_any=[],
    rewards={},critical_rewards={},reward_rolls=[],reward_preview=['Fulfill a prisoner’s allegiance terms'],
    pays_gold=False,bodyguard_slots=0,mission_form='rescue' if route=='rescue' else 'hunt')
   for field in ('decision_scene','chain_next','board_followups','secret_rewards','story_thread','world_context','chain_id','chain_step','chain_total','event','critical_rewards_by_path','hidden_paths'):
    m.pop(field,None)
   m['narrative']={'approach':'{party} set out to keep a promise made at the prison.',
    'success':'The party finished the agreed task and returned with proof.',
    'critical_success':'The party finished the task and brought everyone home safely.',
    'failure':'The promise remains unfinished. The prisoner will wait for another attempt.',
    'critical_failure':'The attempt went wrong. The party had to withdraw without the proof they needed.'}
   if route!='rescue':
    TACTICAL_CONTRACTS[key]={'race':'Human','layout':'camp','faction':{'rival':'rival raiders','former':'the former warband','proof':'the occupying fighters'}[route],**({'enemy_count':2} if rank=='E' else {})}
    m.update(combat_encounter={'id':'contract:'+key},resolution_mode='tactical',objective='Defeat or subdue the opposing force and secure the field.',combat_critical_condition='Secure the field and keep every party member standing.')
   missions[key]=m
