import time
import unittest
from copy import deepcopy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from backend.db import Base
from backend.models import PlayerState, MissionInstance
from backend.game import new_game, normalize_state, analyze_mission
from backend.services import claim_instance, now_ts
from backend.stamina import initialize, view, spend, preview, COSTS


class StaminaTests(unittest.TestCase):
    def character(self, balance=100, at=1000):
        return {'id':'player', 'name':'Player', 'stamina':{'balance':balance,'updated_at':at}}

    def test_recovery_offline_and_debt(self):
        c=self.character(0)
        self.assertEqual(view(c,1018)['current'],1)
        self.assertEqual(view(c,2800)['current'],100)
        c=self.character(-99)
        self.assertFalse(view(c,2799)['eligible'])
        self.assertTrue(view(c,2800)['eligible'])
        self.assertEqual(view(c,4582)['current'],100)

    def test_fractional_recovery_does_not_allow_early_borrowing(self):
        self.assertFalse(view(self.character(0),1017.99)['eligible'])
        self.assertAlmostEqual(view(self.character(0),1009)['current'],.5)

    def test_reads_and_normalization_do_not_write_recovery(self):
        c=self.character(20);original=deepcopy(c)
        view(c,2000);initialize(c,3000)
        self.assertEqual(c,original)
        state=normalize_state(new_game({'name':'Player'}))
        before=deepcopy(state['characters'][0]['stamina'])
        normalize_state(state)
        self.assertEqual(state['characters'][0]['stamina'],before)

    def test_no_banked_time_or_clock_rollback_recovery(self):
        state={'characters':[self.character(100,0)]}
        spend(state,['player'],'S',10000)
        self.assertEqual(view(state['characters'][0],10000)['current'],0)
        self.assertEqual(view(state['characters'][0],9990)['current'],0)

    def test_rank_costs_and_borrowing(self):
        self.assertEqual(COSTS,dict(E=1,D=3,C=5,B=10,A=50,S=100))
        state={'characters':[self.character(1)]}
        check=spend(state,['player'],'S',1000)
        self.assertTrue(check['characters'][0]['borrowing'])
        self.assertEqual(state['characters'][0]['stamina']['balance'],-99)
        with self.assertRaises(ValueError):spend(state,['player'],'E',1001)

    def test_group_validation_is_atomic_and_hired_debt_persists(self):
        ally=self.character(0);ally.update(id='ally',name='Ally')
        state={'characters':[self.character(),ally]}
        before=deepcopy(state)
        with self.assertRaises(ValueError):spend(state,['player','ally'],'B',1000)
        self.assertEqual(state,before)
        state['characters'][1]['stamina']['balance']=1
        state['mercenaries']=[{'id':'ally','character':deepcopy(ally)}]
        spend(state,['player','ally'],'B',1000)
        self.assertEqual(state['mercenaries'][0]['character']['stamina']['balance'],-9)

    def test_bodyguard_stamina_blocks_analysis_but_not_base_work(self):
        state=normalize_state(new_game({'name':'Player'}))
        ally=deepcopy(state['characters'][0]);ally.update(id='ally',name='Ally')
        ally['stamina']={'balance':-99,'updated_at':time.time()}
        state['characters'].append(ally)
        mission={'party_size':1,'bodyguard_slots':1,'stat':'combat','difficulty':4,'rank':'E'}
        result=analyze_mission(state,mission,['player'],bodyguard_ids=['ally'])
        self.assertFalse(result['claimable'])
        self.assertEqual(ally['status'],'idle')
        self.assertTrue(analyze_mission(state,mission,['player'])['claimable'])


class DeploymentStaminaTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with self.engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
        self.sessions=async_sessionmaker(self.engine,expire_on_commit=False)
        async with self.sessions.begin() as session:
            state=normalize_state(new_game({'name':'Tester'}))
            session.add(PlayerState(guild_id='g',user_id='u',display_name='Tester',state=state,updated_at=now_ts()))
            session.add(MissionInstance(id='m',guild_id='g',template_id='herb_meadow',pool_slot=0,position=0,
                spawned_at=now_ts(),expires_at=now_ts()+3600,status='reserved',claimed_by_user_id='u',
                analysis={'chain_owner_user_id':'u'},duration_seconds=1))

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_deployment_spends_once_and_retry_cannot_spend_again(self):
        async with self.sessions.begin() as session:
            mission=await claim_instance(session,'g','u','Tester','m',['player'])
            self.assertEqual(mission.analysis['stamina']['cost_per_character'],1)
        async with self.sessions.begin() as session:
            with self.assertRaises(ValueError):await claim_instance(session,'g','u','Tester','m',['player'])
        async with self.sessions() as session:
            from sqlalchemy import select
            row=(await session.execute(select(PlayerState))).scalar_one()
            self.assertEqual(row.state['characters'][0]['stamina']['balance'],99)

    async def test_failed_deployment_leaves_save_and_contract_untouched(self):
        async with self.sessions.begin() as session:
            from sqlalchemy import select
            row=(await session.execute(select(PlayerState))).scalar_one()
            state=deepcopy(row.state)
            state['characters'][0]['stamina']={'balance':-99,'updated_at':time.time()}
            row.state=state
        async with self.sessions.begin() as session:
            with self.assertRaisesRegex(ValueError,'stamina'):
                await claim_instance(session,'g','u','Tester','m',['player'])
        async with self.sessions() as session:
            from sqlalchemy import select
            row=(await session.execute(select(PlayerState))).scalar_one()
            self.assertEqual(row.state['characters'][0]['stamina']['balance'],-99)
            self.assertEqual((await session.get(MissionInstance,'m')).status,'reserved')
