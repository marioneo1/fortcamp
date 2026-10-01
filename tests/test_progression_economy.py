import random
import unittest
from copy import deepcopy
from unittest.mock import patch
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from backend.content import BUILDINGS, ITEMS, MISSION_TEMPLATES, GENERAL_LOOT_TABLE, EVENT_REWARD_TABLES, MISSION_RANKS, STANDALONE_PERKS
from backend.game import new_game, normalize_state, train_perk, analyze_mission, resolve_mission, _placement_error
from backend.economy import initialize, settle, camp_action, trade_view, purchase, practice, earn_relationship
from backend.services import reserve_instance, claim_instance, claim_budget, resolve_due, available_chain_missions, _rolled_pool_templates
from backend.models import MissionInstance, PlayerState
from backend.db import Base
from backend.mission_loot import roll_item_pool, scene_reward_template

class EconomyTests(unittest.TestCase):
    def state(self):
        s=new_game({'name':'Solo'});initialize(s,1000);return s

    def test_solo_migration_preserves_currency_once(self):
        s=self.state();s.pop('economy_v1');s['resources']['cloth']=17;s['resources']['stone']=8
        initialize(s,1000);initialize(s,1000)
        self.assertEqual(s['resources']['stone'],25);self.assertNotIn('cloth',s['resources'])
        self.assertEqual(len(s['characters']),1)
        self.assertTrue(all('cloth' not in b.get('cost',{}) for b in BUILDINGS.values()))

    def test_production_is_bounded_idempotent_and_pauses_for_expedition(self):
        s=self.state();s['camp_work']='wood';initial=s['resources']['wood']
        settle(s,4600);self.assertEqual(s['resources']['wood']-initial,18)
        settle(s,4600);self.assertEqual(s['resources']['wood']-initial,18)
        s['characters'][0]['status']='mission';settle(s,8200)
        self.assertEqual(s['resources']['wood']-initial,18)
        s['characters'][0]['status']='idle';settle(s,8200+100*3600)
        self.assertEqual(s['resources']['wood']-initial,18+18*12)

    def test_staff_proficiencies_change_yield_and_learn_by_work(self):
        a=self.state();b=deepcopy(a);a['camp_work']=b['camp_work']='stone'
        b['characters'][0]['perks']['building']='master'
        settle(a,4600);settle(b,4600)
        self.assertGreater(b['resources']['stone'],a['resources']['stone'])
        self.assertGreater(a['characters'][0]['practice']['building'],0)
        a['characters'][0]['practice']['building']=11;settle(a,8200)
        self.assertEqual(a['characters'][0]['perks']['building'],'basic')

    def test_expansion_preserves_placement_and_meals_do_not_create_helpers(self):
        s=normalize_state(self.state());s['resources'].update(wood=100,stone=100,gold=100,food=20)
        positions=deepcopy(s['buildings']);camp_action(s,'expand')
        self.assertEqual(s['buildings'],positions);self.assertIsNone(_placement_error(s,'tent',14,0))
        s['buildings'].append({'id':'k','type':'kitchen','x':8,'y':0,'assigned':[]})
        camp_action(s,'cook',meal='trail_meal',count=2);self.assertEqual(s['meals']['trail_meal'],2)
        camp_action(s,'eat',meal='trail_meal',character_id='player');self.assertEqual(s['characters'][0]['prepared_meal'],'trail_meal')
        self.assertEqual(len(s['characters']),1)

    def test_teaching_requires_better_teacher_above_basic(self):
        s=normalize_state(self.state());s['resources']['gold']=20
        s['buildings'].append({'id':'t','type':'training_ground','x':8,'y':0,'assigned':[]})
        first=train_perk(s,'player','combat');self.assertEqual(first['teacher'],'Local instructor')
        s['inventory'].append({'instance_id':'manual','item_id':'training_manual'})
        with self.assertRaisesRegex(ValueError,'teacher'):train_perk(s,'player','combat')
        teacher=deepcopy(s['characters'][0]);teacher.update(id='teacher',name='Instructor',is_player=False);teacher['perks']['combat']='expert';s['characters'].append(teacher)
        self.assertEqual(train_perk(s,'player','combat')['teacher'],'Instructor')

    def test_visits_and_stock_are_personal_persistent_and_optional(self):
        visits=[]
        for i in range(30):
            s=self.state();first=trade_view(s,f'guild:player{i}',2000)
            self.assertEqual(first,trade_view(s,f'guild:player{i}',2001))
            visits.append(first['merchant'])
        self.assertTrue(any(v is None for v in visits));self.assertTrue(any(v for v in visits))
        self.assertGreater(len({str(v['offers']) for v in visits if v}),1)

    def test_trade_checks_relationship_stock_and_duplicate_purchase(self):
        s=self.state();s['resources']['gold']=1000;key='guild:buyer';view=trade_view(s,key,2000)
        locked=view['factions'][0]['offers'][-1]
        with self.assertRaises(ValueError):purchase(s,key,locked['id'],2000)
        s['factions']['hedgerow']=100;purchase(s,key,locked['id'],2000)
        with self.assertRaises(ValueError):purchase(s,key,locked['id'],2000)
        self.assertEqual(sum(i['item_id']==locked['item'] for i in s['inventory']),1)

    def test_low_rank_exclusives_never_enter_higher_rank_pools(self):
        exclusive={iid for mid in ['rats_storehouse','roadside_toll','timber_creek','caravan_account'] for r in MISSION_TEMPLATES[mid]['reward_rolls'] for iid in [r['reward']['item']]}
        for rank in ['C','B','A','S']:
            for seed in range(100):
                iid,_,_=roll_item_pool({},rank,random.Random(seed),ITEMS,GENERAL_LOOT_TABLE,None,MISSION_RANKS)
                self.assertNotIn(iid,exclusive)
        m=MISSION_TEMPLATES['timber_creek'];self.assertTrue(m['reward_rolls'][0]['requires_combat'])
        self.assertFalse(scene_reward_template(m,{})['completed_combat'])

    def test_all_new_items_have_working_perks_and_blueprints_exist(self):
        for item in ITEMS.values():
            for perk in item.get('granted_perks',[]):self.assertIn(perk,STANDALONE_PERKS)
        for m in MISSION_TEMPLATES.values():
            for key in ['rewards','critical_rewards']:
                if m.get(key,{}).get('blueprint'):self.assertIn(m[key]['blueprint'],BUILDINGS)
        for rank,minimum in [('E',24),('D',14),('C',12)]:
            self.assertGreaterEqual(sum(m.get('rank')==rank and not m.get('event') and not m.get('chain_only') and not m.get('trigger_only') for m in MISSION_TEMPLATES.values()),minimum)

    def test_pool_scales_beyond_sixteen_without_guaranteeing_s(self):
        a=_rolled_pool_templates('economy',10,20)
        self.assertEqual(sum(MISSION_TEMPLATES[mid]['rank']=='E' for mid in a),320)
        self.assertEqual(sum(MISSION_TEMPLATES[mid]['rank']=='D' for mid in a),160)
        self.assertLessEqual(sum(MISSION_TEMPLATES[mid]['rank']=='S' for mid in a),60)

class BeginnerRecoveryTests(unittest.TestCase):
    def test_solo_early_critical_failure_is_short_but_still_incapacitates(self):
        from backend.game import resolve_mission, analyze_mission
        state=normalize_state(new_game({'name':'Solo'}));mission=MISSION_TEMPLATES['market_errand']
        result=resolve_mission(state,mission,['player'],analyze_mission(state,mission,['player']),'beginner','critical_failure')
        self.assertEqual(state['characters'][0]['status'],'incapacitated')
        self.assertEqual(state['characters'][0]['recovers_at']-result['timestamp'],120)

class ReservationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with self.engine.begin() as connection:await connection.run_sync(Base.metadata.create_all)
        self.sessions=async_sessionmaker(self.engine,expire_on_commit=False)
        self.ts=1800000000
        async with self.sessions() as session:
            async with session.begin():
                session.add(PlayerState(guild_id='g',user_id='u',display_name='Solo',state=normalize_state(new_game({'name':'Solo'})),updated_at=self.ts))
                for i in range(7):session.add(MissionInstance(id=f'm{i}',guild_id='g',template_id='market_errand',pool_slot=self.ts,position=i,spawned_at=self.ts,expires_at=self.ts+1800,duration_seconds=1000,status='available',analysis={'public_wave':1}))
    async def asyncTearDown(self):await self.engine.dispose()

    async def test_claims_are_team_free_and_budget_cannot_be_overspent(self):
        with patch('backend.services.now_ts',return_value=self.ts+5):
            async with self.sessions() as session:
                async with session.begin():
                    for i in range(5):
                        mission=await reserve_instance(session,'g','u','Solo',f'm{i}')
                        self.assertEqual(mission.status,'reserved');self.assertIsNone(mission.party_ids)
                    await reserve_instance(session,'g','u','Solo','m0') # replay does not spend
                    with self.assertRaisesRegex(ValueError,'Points'):await reserve_instance(session,'g','u','Solo','m5')
                    player=await session.get(PlayerState,{'guild_id':'g','user_id':'u'})
                    self.assertEqual(player.state['characters'][0]['status'],'idle')
                    self.assertEqual(claim_budget(player.state,self.ts,self.ts,self.ts+5)['remaining'],0)
                    self.assertEqual(claim_budget(player.state,self.ts,self.ts,self.ts+65)['remaining'],5)
                    self.assertEqual(claim_budget(player.state,self.ts,self.ts,self.ts+125)['remaining'],3)

    async def test_owned_contract_is_private_then_starts_and_resolves_immediately(self):
        with patch('backend.services.now_ts',return_value=self.ts+5):
            async with self.sessions() as session:
                async with session.begin():
                    mission=await reserve_instance(session,'g','u','Solo','m0')
                    self.assertEqual(len(await available_chain_missions(session,'g','u',self.ts+5)),1)
                    self.assertEqual(await available_chain_missions(session,'g','other',self.ts+5),[])
                    with self.assertRaisesRegex(ValueError,'Create your character'):await claim_instance(session,'g','other','Other','m0',['player'])
                    started=await claim_instance(session,'g','u','Solo','m0',['player'])
                    self.assertEqual(started.completes_at,self.ts+5)
                    rows=await resolve_due(session,'g','u');self.assertEqual(len(rows),1)
                    self.assertEqual(started.status,'completed')
                    self.assertEqual(await resolve_due(session,'g','u'),[])
