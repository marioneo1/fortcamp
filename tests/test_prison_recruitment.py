import unittest
from copy import deepcopy
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from backend.models import Base,PlayerState
from backend.content import ITEMS, MISSION_TEMPLATES
from backend.game import new_game,normalize_state,manage_prisoner
from backend.prison_recruitment import initialize_prisoner,prisoner_interaction,credit_allegiance
from backend.services import spawn_prisoner_contract,claim_instance,_finish_battle
from backend.combat import create_contract_battle,battle_view

def fixture(boss=False,rank='E'):
 s=new_game({'name':'Warden'});s['buildings'].append({'id':'prison','type':'prison_cell','x':8,'y':8,'assigned':['player']})
 p={'id':'captive','capture_key':'capture:a','name':'Vrix','race':'Goblin','gender':'male','kind':'chieftain' if boss else 'raider','boss':boss,'holding':'prison_cell','captured_at':1,'portrait':'fixed.webp'}
 initialize_prisoner(p,rank,100);s['prisoners']=[p];return s,p

class RecruitmentTests(unittest.TestCase):
 def test_terms_identity_and_profile_survive_migration_and_swaps(self):
  s,p=fixture();snapshot=deepcopy(p['recruitment']);normalize_state(s);initialize_prisoner(p,'S',900)
  self.assertEqual(p['recruitment'],snapshot)
  manage_prisoner(s,'captive','stockade',now=100);manage_prisoner(s,'captive','secure',now=200)
  self.assertEqual(p['recruitment'],snapshot)
 def test_warden_cooldown_shared_and_boss_cannot_skip_terms(self):
  s,p=fixture(True);r=p['recruitment'];prisoner_interaction(s,p,'negotiate',ITEMS,100)
  other=deepcopy(p);other['id']='second';s['prisoners'].append(other)
  with self.assertRaises(ValueError):prisoner_interaction(s,other,'negotiate',ITEMS,101)
  r['resistance']=0
  with self.assertRaises(ValueError):prisoner_interaction(s,p,'recruit',ITEMS,101)
 def test_ordinary_negotiation_joins_once_with_stable_identity(self):
  s,p=fixture();p['recruitment']['resistance']=0
  prisoner_interaction(s,p,'recruit',ITEMS,100)
  self.assertEqual(s['characters'][-1]['name'],'Vrix');self.assertEqual(s['characters'][-1]['portrait'],'fixed.webp')
  self.assertEqual(s['characters'][-1]['loyalty'],70);self.assertEqual(s['prisoners'],[])
  with self.assertRaises(ValueError):manage_prisoner(s,'captive','recruit',now=101)
 def test_payment_consumed_once_and_high_boss_needs_proof(self):
  s,p=fixture(True,'A');r=p['recruitment'];r.update(route='rebuild',revealed=True,requires_proof=True,quest_route='proof',cost=90)
  s['resources']['wood']=100;prisoner_interaction(s,p,'fulfill',ITEMS,100)
  self.assertEqual(s['resources']['wood'],10);self.assertFalse(r['terms_met'])
  with self.assertRaises(ValueError):prisoner_interaction(s,p,'fulfill',ITEMS,101)
  analysis={'prisoner_allegiance_id':p['id'],'prisoner_allegiance_route':'rebuild'}
  credit_allegiance(s,analysis,'failure',[]);self.assertFalse(r['terms_met'])
  credit_allegiance(s,analysis,'success',[]);self.assertTrue(r['terms_met'])
  prisoner_interaction(s,p,'recruit',ITEMS,102);self.assertEqual(s['characters'][-1]['loyalty'],80)
 def test_item_payment_refuses_equipped_copies(self):
  s,p=fixture();r=p['recruitment'];r.update(route='heirloom',requested_item='field_pack',revealed=True)
  s['inventory'].append({'item_id':'field_pack','instance_id':'pack'});s['characters'][0]['equipment']['accessory']='pack'
  with self.assertRaises(ValueError):prisoner_interaction(s,p,'fulfill',ITEMS)
  s['characters'][0]['equipment']['accessory']=None;prisoner_interaction(s,p,'fulfill',ITEMS)
  self.assertNotIn('pack',[i['instance_id'] for i in s['inventory']])
 def test_generic_conversion_cannot_claim_a_unique_champion(self):
  s,p=fixture();p['recruitment']['candidate']['source_kind']='champion';p['recruitment']['terms_met']=True
  with self.assertRaises(ValueError):prisoner_interaction(s,p,'recruit',ITEMS)
  self.assertEqual(len(s['prisoners']),1);self.assertEqual(len(s['characters']),1)
 def test_allegiance_templates_are_private_and_maps_use_captive_race(self):
  s,p=fixture()
  for key,m in MISSION_TEMPLATES.items():
   if key.startswith('prison_'):self.assertTrue(m['chain_only']);self.assertEqual(m['pool_weight'],0)
  b=create_contract_battle(s,['player'],'test','prison_rival_e',race_override='Goblin')
  self.assertEqual(len([u for u in b['units'].values() if u['team']=='enemy']),2)
  self.assertTrue(all(u['race']=='Goblin' for u in b['units'].values() if u['team']=='enemy'))
  battle_view(b)

class ContractTests(unittest.IsolatedAsyncioTestCase):
 async def test_private_battle_completion_credits_only_its_prisoner(self):
  engine=create_async_engine('sqlite+aiosqlite:///:memory:')
  try:
   async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
   async with async_sessionmaker(engine,expire_on_commit=False)() as session:
    s,p=fixture();p['recruitment'].update(route='rival',quest_route='rival',revealed=True)
    player=PlayerState(guild_id='guild',user_id='owner',display_name='Owner',state=s,updated_at=1);session.add(player)
    quest=await spawn_prisoner_contract(session,'guild','owner',p);await session.flush()
    claimed=await claim_instance(session,'guild','owner','Owner',quest.id,['player'])
    self.assertEqual(claimed.analysis['prisoner_allegiance_id'],p['id'])
    battle=claimed.analysis['battle'];battle.update(status='complete',outcome='success',battle_won=True,battlefield_secured=True)
    await _finish_battle(session,claimed,player,battle)
    captive=next(p for p in player.state['prisoners'] if p['id']=='captive')
    self.assertTrue(captive['recruitment']['terms_met'])
  finally:await engine.dispose()
 async def test_same_captive_is_idempotent_other_captive_gets_own_contract(self):
  engine=create_async_engine('sqlite+aiosqlite:///:memory:')
  try:
   async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
   async with async_sessionmaker(engine,expire_on_commit=False)() as session:
    s,p=fixture();p['recruitment'].update(route='rival',quest_route='rival',revealed=True)
    a=await spawn_prisoner_contract(session,'guild','owner',p);b=await spawn_prisoner_contract(session,'guild','owner',p)
    self.assertEqual(a.id,b.id)
    other=deepcopy(p);other['id']='other';other['recruitment']['quest_id']=None
    c=await spawn_prisoner_contract(session,'guild','owner',other);self.assertNotEqual(a.id,c.id)
    self.assertEqual(a.analysis['chain_owner_user_id'],'owner')
    a.status='completed';await session.flush();d=await spawn_prisoner_contract(session,'guild','owner',p);self.assertNotEqual(a.id,d.id)
  finally:await engine.dispose()
