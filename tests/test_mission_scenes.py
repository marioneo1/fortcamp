import random
import unittest
from copy import deepcopy
from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine
from backend.content import MISSION_TEMPLATES,ITEMS,GENERAL_LOOT_TABLE,MISSION_RANKS,EVENT_REWARD_TABLES
from backend.db import Base
from backend.game import new_game,analyze_mission,effective_stat,effective_attribute
from backend.models import PlayerState,MissionInstance
from backend.services import claim_instance,choose_decision_instance,get_decision_instance,_resolve_roll_stage,now_ts
from backend.mission_decisions import advance_scene,initial_scene,choice_check,setup_encounter
from backend.mission_loot import roll_item_pool,SIGNATURE_ITEMS,scene_reward_template
from backend.combat import create_battle,_player_unit,_deal_damage,_current_unit

class SceneChecks(unittest.TestCase):
    def setUp(self):
        self.state=new_game({'name':'Tester','attributes':{'str':7,'dex':7,'agi':7,'vit':7,'int':7,'luk':7}})
        self.template=MISSION_TEMPLATES['goblin_smoke_signals']
        self.analysis=analyze_mission(self.state,self.template,['player'])
        self.analysis['scene']=initial_scene()

    def test_failed_optional_clue_continues_without_awarding_it(self):
        seed=next(str(i) for i in range(100) if 2<=random.Random(f'{i}:scene:signals:0:embers').randint(1,20)<=6)
        scene,transition=advance_scene(self.state,self.template,self.analysis,seed,'signals',0,'embers')
        self.assertEqual(transition['next'],'chart');self.assertEqual(scene['bonus_keys'],[])
        self.analysis['scene']=scene
        with self.assertRaisesRegex(ValueError,'already changed'):advance_scene(self.state,self.template,self.analysis,seed,'signals',0,'embers')

    def test_critical_failure_starts_stronger_opposition_and_does_not_injure_early(self):
        template=MISSION_TEMPLATES['restless_graves'];analysis=analyze_mission(self.state,template,['player'])
        seed=next(str(i) for i in range(100) if random.Random(str(i)).randint(1,20)==1)
        mission=MissionInstance(id=seed,template_id='restless_graves',party_ids=['player'],analysis=analysis,status='claimed')
        self.state['characters'][0]['status']='mission'
        original=deepcopy(self.state)
        state,result=_resolve_roll_stage(self.state,mission,['player'],analysis)
        self.assertIsNone(result);self.assertEqual(mission.status,'battle')
        self.assertEqual(state['resources'],original['resources']);self.assertEqual(state['characters'][0]['status'],'mission')
        self.assertNotIn('recovers_at',state['characters'][0])

    def test_bodyguards_do_not_change_choice_odds(self):
        choice=self.template['decision_scene']['nodes']['signals']['choices']['follow']
        before=choice_check(self.state,self.template,self.analysis,choice)
        guard=deepcopy(self.state['characters'][0]);guard.update(id='guard',name='Guard');guard['attributes'].update(vit=99,agi=99)
        self.state['characters'].append(guard);self.analysis['bodyguard_ids']=['guard']
        self.assertEqual(before,choice_check(self.state,self.template,self.analysis,choice))

    def test_ambush_setup_precedes_any_enemy_activation(self):
        battle=create_battle(self.state,['player'],'setup','contract:highway_ambush',defer_start=True)
        self.assertFalse(any(event.get('type')=='movement' for event in battle.get('animation_events',[])))
        setup_encounter(battle,{'setup':'ambush','boss':True})
        self.assertEqual(battle['turn_order'][0],'player')
        self.assertIn('Retrieval Officer',battle['units'][battle['complication_boss']]['name'])

class LootAndPerks(unittest.TestCase):
    def test_faction_and_general_pools_mix_but_never_contain_exclusives(self):
        mission=MISSION_TEMPLATES['goblin_warcamp'];seen=set()
        for seed in range(250):
            item,source,rarity=roll_item_pool(mission,'D',random.Random(seed),ITEMS,GENERAL_LOOT_TABLE,None,MISSION_RANKS)
            seen.add(source);self.assertNotIn(item,SIGNATURE_ITEMS)
            self.assertIn(rarity,{'common','uncommon','rare'})
        self.assertEqual(seen,{'general cache','faction cache'})

    def test_permanent_and_equipment_perks_stack_once_and_change_units(self):
        state=new_game({'name':'Tester'});char=state['characters'][0]
        baseline=_player_unit(state,char,0,0)
        char['traits']+=['scout','guard','regeneration','fire_magic']
        state['inventory'].append({'instance_id':'lens','item_id':'signal_lens'});char['equipment']['accessory']='lens'
        enhanced=_player_unit(state,char,0,0)
        self.assertEqual(enhanced['move'],baseline['move']+1)
        self.assertEqual(enhanced['armor'],baseline['armor']+1)
        self.assertEqual(effective_attribute(state,char,'int'),char['attributes']['int']+1)
        enhanced['hp']-=5
        battle=create_battle(state,['player'],'regen','contract:highway_ambush',defer_start=True)
        battle['units']['player']['hp']-=5;battle['turn_index']=len(battle['turn_order']);_current_unit(battle)
        self.assertEqual(battle['units']['player']['hp'],battle['units']['player']['max_hp']-3)

class SceneDatabase(unittest.IsolatedAsyncioTestCase):
    async def test_acceptance_response_contains_the_first_playable_decision(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from backend.main import mission_claim, PartyRequest
        engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
        sessions=async_sessionmaker(engine,expire_on_commit=False);ts=now_ts()
        try:
            async with sessions() as session:
                async with session.begin():
                    state=new_game({'name':'Tester'})
                    for i in range(2):
                        ally=deepcopy(state['characters'][0]);ally.update(id=f'ally{i}',is_player=False,name=f'Helper{i}');state['characters'].append(ally)
                    session.add(PlayerState(guild_id='scene',user_id='owner',display_name='Tester',state=state,updated_at=ts))
                    session.add(MissionInstance(id='accept-ledger',guild_id='scene',template_id='black_banner_ledger',pool_slot=-1,position=0,spawned_at=ts,expires_at=ts+3600,duration_seconds=120,status='available',analysis={'chain_owner_user_id':'owner'}))
            with patch('backend.main.SessionLocal',sessions):
                response=await mission_claim('accept-ledger',PartyRequest(party_ids=['player','ally0','ally1']),SimpleNamespace(guild_id='scene',user_id='owner',display_name='Tester'))
            self.assertEqual(response['mission']['status'],'decision')
            self.assertEqual(response['decision']['node_id'],'case')
            self.assertEqual(response['decision']['revision'],0)
            self.assertTrue(response['decision']['choices'])
        finally:await engine.dispose()

    async def test_saved_decisions_are_owner_only_and_cannot_replay_rewards(self):
        engine=create_async_engine('sqlite+aiosqlite:///:memory:')
        async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
        sessions=async_sessionmaker(engine,expire_on_commit=False);ts=now_ts()
        try:
            async with sessions() as session:
                async with session.begin():
                    state=new_game({'name':'Tester'})
                    for i in range(2):
                        ally=deepcopy(state['characters'][0]);ally.update(id=f'ally{i}',is_player=False,name=f'Helper{i}');state['characters'].append(ally)
                    session.add(PlayerState(guild_id='scene',user_id='owner',display_name='Tester',state=state,updated_at=ts))
                    session.add(MissionInstance(id='ledger-scene',guild_id='scene',template_id='black_banner_ledger',pool_slot=-1,position=0,status='available',spawned_at=ts,expires_at=ts+1000,duration_seconds=60,analysis={'chain_owner_user_id':'owner'}))
                async with session.begin():await claim_instance(session,'scene','owner','Tester','ledger-scene',['player','ally0','ally1'])
                async with session.begin():
                    with self.assertRaisesRegex(ValueError,'not found'):await get_decision_instance(session,'scene','stranger','ledger-scene')
                    response=await choose_decision_instance(session,'scene','owner','ledger-scene','case',0,'witness')
                    self.assertEqual(response['decision']['node_id'],'witness')
                async with session.begin():
                    scene=await get_decision_instance(session,'scene','owner','ledger-scene');self.assertEqual(scene['revision'],1)
                    response=await choose_decision_instance(session,'scene','owner','ledger-scene','witness',1,'leave')
                    self.assertEqual(response['mission']['status'],'completed');self.assertFalse(response['result']['debug_forced'])
                async with session.begin():
                    with self.assertRaisesRegex(ValueError,'no longer'):await choose_decision_instance(session,'scene','owner','ledger-scene','witness',1,'leave')
        finally:await engine.dispose()
