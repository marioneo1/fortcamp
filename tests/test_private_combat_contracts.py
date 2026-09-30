import random
import unittest
from copy import deepcopy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from backend.db import Base
from backend.models import PlayerState, MissionInstance
from backend.game import new_game
from backend.services import _spawn_result_chains, available_chain_missions, mission_summary, analyze_instance, claim_instance, now_ts
from backend.content import MISSION_TEMPLATES
from backend.tactical_contracts import TACTICAL_CONTRACTS
from backend.combat import create_battle, auto_resolve, _check_end, apply_player_command


class TacticalContractTests(unittest.TestCase):
    def test_all_converted_contracts_have_stable_maps_and_complete(self):
        state=new_game({'name':'Tester','attributes':{'str':12,'dex':9,'agi':9,'vit':12,'int':8,'luk':7}})
        for mission_id in TACTICAL_CONTRACTS:
            with self.subTest(mission=mission_id):
                encounter=MISSION_TEMPLATES[mission_id]['combat_encounter']['id']
                battle=create_battle(state,['player'],mission_id,encounter)
                self.assertEqual(battle,create_battle(state,['player'],mission_id,encounter))
                self.assertTrue(all(u['race']==TACTICAL_CONTRACTS[mission_id]['race'] for u in battle['units'].values() if u['team']=='enemy'))
                self.assertEqual(auto_resolve(battle,max_steps=500)['status'],'complete')

    def test_critical_requires_living_capture_and_safe_party(self):
        state=new_game({'name':'Tester'})
        battle=create_battle(state,['player'],'capture','contract:highway_ambush')
        for unit in battle['units'].values():
            if unit['team']=='enemy':
                unit.update(hp=0,alive=False,conscious=False,condition='dead')
        _check_end(battle)
        self.assertFalse(battle['objectives'][1]['complete'])
        leader=battle['units'][battle['primary_target_id']]
        leader.update(alive=True,condition='unconscious')
        battle.pop('loot_secured',None)
        _check_end(battle)
        self.assertTrue(battle['objectives'][1]['complete'])
        self.assertIn(leader['id'],battle['auto_captured_ids'])


class PrivateLeadTests(unittest.IsolatedAsyncioTestCase):
    async def test_immediate_leads_are_owned_idempotent_and_claimable_above_public_rank(self):
        engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with engine.begin() as connection:await connection.run_sync(Base.metadata.create_all)
        sessions=async_sessionmaker(engine,expire_on_commit=False)
        ts=now_ts()
        async with sessions() as session:
            async with session.begin():
                state=new_game({'name':'Tester','attributes':{'int':10,'str':9,'vit':8}})
                ally=deepcopy(state['characters'][0]);ally.update(id='ally',is_player=False,name='Helper');state['characters'].append(ally)
                second=deepcopy(ally);second.update(id='second',name='Second');state['characters'].append(second)
                session.add(PlayerState(guild_id='private',user_id='owner',display_name='Tester',state=state,updated_at=ts))
                source=MissionInstance(id='source',guild_id='private',template_id='highway_ambush',pool_slot=1,position=0,spawned_at=ts,expires_at=ts+100,status='completed',duration_seconds=1,claimed_by_user_id='owner',resolved_at=ts)
                session.add(source);await session.flush()
                result={'outcome':'success','board_followups':[{'template_id':'black_banner_ledger'}]}
                rows=await _spawn_result_chains(session,source,'owner',result,ts)
                source.result=result
                self.assertEqual(len(rows),1)
                self.assertEqual(len(await available_chain_missions(session,'private','owner',ts+1)),1)
                self.assertEqual(await available_chain_missions(session,'private','stranger',ts+1),[])
                self.assertFalse(mission_summary(rows[0],viewer_rank='E')['locked'])
                summary=mission_summary(rows[0]);self.assertIn('private_source',summary)
                with self.assertRaisesRegex(ValueError,'Mission not found'):
                    await analyze_instance(session,'private','stranger',rows[0].id,['player','ally'])
                analysis=await analyze_instance(session,'private','owner',rows[0].id,['player','ally','second'])
                self.assertTrue(analysis['claimable'])
                claimed=await claim_instance(session,'private','owner','Tester',rows[0].id,['player','ally','second'])
                self.assertEqual(claimed.status,'decision')
                self.assertIn('private_source_name',claimed.analysis)
        await engine.dispose()
