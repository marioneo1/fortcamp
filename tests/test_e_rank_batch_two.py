import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from backend import combat,combat_conditions,combat_radiant
from backend.battle_lab import layout_presets
from backend.content import ITEMS,GENERAL_LOOT_TABLE
from backend.field_gear import GEAR
from backend.game import new_game
from backend.prison_recruitment import initialize_prisoner
from backend.job_loadouts import snapshot

MISSIONS=('goblin_pickpockets','ruined_well','supply_watch')


class BatchTwoTests(unittest.TestCase):
    def battle(self,mid,seed=None):
        seed=seed or layout_presets('contract:'+mid)[0]['seed']
        return combat.create_contract_battle(new_game({'name':'QA'}),['player'],seed,mid,True)

    def test_all_layouts_honor_counts_legal_spawns_and_nonboss_profiles(self):
        for mid in MISSIONS:
            for p in layout_presets('contract:'+mid):
                b=self.battle(mid,p['seed']);enemies=combat._living(b,'enemy')
                count=([2,3,2,3] if mid=='supply_watch' else [2]*4)[b['map_variation']-1]
                self.assertEqual(len(enemies),count)
                self.assertEqual(len({(u['x'],u['y']) for u in enemies}),count)
                probe={**b,'units':{}}
                for u in enemies:
                    self.assertFalse(combat._blocked(probe,u['x'],u['y']))
                    self.assertFalse(u['boss']);self.assertEqual(u['kind'],'raider')
                    self.assertGreaterEqual(u['hp'],19);self.assertTrue(u['skills'])
                    self.assertTrue(all(s['id'] for s in u['skills']))
                    if mid=='goblin_pickpockets':self.assertEqual((u['race'],u['move'],u['evasion']),('Goblin',4,12))

    def test_mission_dressing_and_rank_budgets(self):
        for mid in MISSIONS:
            totals=[]
            for p in layout_presets('contract:'+mid):
                b=self.battle(mid,p['seed']);es=combat._living(b,'enemy')
                totals.append(sum(u['hp'] for u in es))
                names=' '.join(t.get('name','') for t in b['terrain']+b.get('decorations',[]))
                self.assertIn({'goblin_pickpockets':'Dropped Purse','ruined_well':'Old Village Well','supply_watch':'Grain Sacks'}[mid],names)
                if b['map_variation'] in (2,4) and mid=='supply_watch':self.assertEqual(sum(u['attack'] for u in es),9)
            self.assertLessEqual(max(totals)/min(totals),1.15)

    def test_recruited_roles_preserve_skills_and_personality(self):
        for mid in MISSIONS:
            for p in layout_presets('contract:'+mid):
                for u in combat._living(self.battle(mid,p['seed']),'enemy'):
                    captive={'id':'c','name':u['name'],'race':u['race'],'skills':deepcopy(u['skills']),
                             'recruitable_snapshot':deepcopy(u['recruitable_snapshot']), 'personality_id':u['personality_id']}
                    initialize_prisoner(captive,now=0)
                    candidate=captive['recruitment']['candidate']
                    skills,_,_=snapshot(candidate)
                    self.assertEqual([s['id'] for s in skills],[s['id'] for s in u['skills']])
                    self.assertEqual(candidate['personality_id'],u['personality_id'])


class RadiantTests(unittest.TestCase):
    def battle(self):
        # A real seeded roll (1/100); no patched RNG or live player saves.
        return combat.create_battle(new_game({'name':'QA'}),['player'],'74','contract:supply_watch',True)

    def test_saved_choice_is_once_only_and_blocks_actions_and_auto(self):
        b=self.battle();self.assertTrue(combat_radiant.pending(b))
        saved=json.loads(json.dumps(b));combat_radiant.prepare(saved)
        self.assertEqual(saved['radiant_encounter'],b['radiant_encounter'])
        for call in (lambda:combat.apply_player_command(b,{'action':'guard'}),lambda:combat.auto_step(b),lambda:combat.auto_resolve(b)):
            with self.assertRaisesRegex(ValueError,'bear'):call()
        before=len(b['units'])
        combat.apply_player_command(b,{'action':'radiant_choice','choice':'continue'})
        self.assertEqual(len(b['units']),before)
        self.assertEqual(b['radiant_encounter']['state'],'active')
        with self.assertRaises(ValueError):combat_radiant.choose(b,'continue')

    def test_present_on_arrival_bear_hates_both_sides_and_uses_normal_loot(self):
        b=self.battle()
        self.assertIn(combat_radiant.BEAR_ID,b['units'])
        self.assertIn('skirmish_target_id',b['radiant_encounter'])
        combat.apply_player_command(b,{'action':'radiant_choice','choice':'continue'})
        bear=b['units'][combat_radiant.BEAR_ID]
        self.assertEqual(b['turn_order'].count(bear['id']),1)
        self.assertFalse(combat._blocked(b,bear['x'],bear['y'],bear['id']))
        scenery={p for obj in b.get('decorations',[]) if not obj.get('ground_edging') for p in combat.occupied_tiles(obj)}
        self.assertNotIn((bear['x'],bear['y']),scenery)
        targets=combat_conditions.hostile_units(b,bear,combat._living(b))
        self.assertEqual({u['team'] for u in targets},{'player','enemy'})
        for u in targets:self.assertIn(bear,combat_conditions.hostile_units(b,u,combat._living(b)))
        self.assertEqual((bear['corpse_item'],bear['corpse_item_chance']),('bear_claws',5))
        bear.update(condition='dead',alive=False,conscious=False)
        combat._secure_battlefield_loot(b)
        self.assertIn(bear['id'],b['auto_looted_ids'])
        bear['lost_in_pit']=True;b.pop('loot_secured',None);combat._secure_battlefield_loot(b)
        self.assertNotIn(bear['id'],b['auto_looted_ids'])

    def test_third_party_ai_attacks_locals_and_locals_attack_bear(self):
        b=self.battle();combat_radiant.choose(b,'continue')
        bear=b['units'][combat_radiant.BEAR_ID]
        local=b['units'][b['radiant_encounter']['skirmish_target_id']]
        combat._enemy_turn(b,bear)
        attacks=[e for e in b.get('animation_events',[]) if e.get('attacker_id')==bear['id']]
        self.assertTrue(any(e.get('target_id')==local['id'] for e in attacks))
        b=self.battle();combat_radiant.choose(b,'continue')
        local=b['units'][b['radiant_encounter']['skirmish_target_id']]
        combat._enemy_turn(b,local)
        attacks=[e for e in b.get('animation_events',[]) if e.get('attacker_id')==local['id']]
        self.assertTrue(any(e.get('target_id')==combat_radiant.BEAR_ID for e in attacks))

    def test_living_bear_does_not_block_contract_or_normal_loot(self):
        b=self.battle();combat_radiant.choose(b,'continue')
        fallen=[]
        for u in combat._living(b,'enemy'):
            if u.get('radiant_id'):continue
            u.update(condition='dead',alive=False,conscious=False)
            fallen.append(u['id'])
        combat._check_contract_end(b)
        self.assertTrue(b['battle_won'])
        self.assertTrue(b['objectives'][0]['complete'])
        self.assertTrue(b['objectives'][1]['complete'])
        self.assertFalse(b['battlefield_secured'])
        combat._claim_victory(b)
        self.assertTrue(set(fallen)<=set(b['auto_looted_ids']))
        self.assertNotIn(combat_radiant.BEAR_ID,b['auto_looted_ids'])
        self.assertEqual(b['status'],'complete')

    def test_other_missions_never_roll_and_trophies_are_exclusive(self):
        b=combat.create_battle(new_game({'name':'QA'}),['player'],'74','contract:rats_storehouse',True)
        self.assertNotIn('radiant_encounter',b)
        self.assertFalse({'bear_claws','thick_bear_pelt'} & {v[0] for v in GENERAL_LOOT_TABLE})
        state={};result={'rewards':{}}
        combat_radiant.corpse_rewards(state,result,{'corpse_bonus_items':['thick_bear_pelt']})
        self.assertEqual(result['rewards']['items'],['thick_bear_pelt'])
        self.assertEqual(state['inventory'][0]['item_id'],'thick_bear_pelt')

    def test_gear_improves_real_monk_damage_and_pelt_trades_speed_for_hp(self):
        state=new_game({'name':'QA','starting_role':'monk'})
        c=state['characters'][0];base=combat._player_unit(state,c,0,0)
        state['inventory'].append({'instance_id':'claws','item_id':'bear_claws'});c['equipment']['weapon']='claws'
        armed=combat._player_unit(state,c,0,0)
        self.assertEqual((armed['melee_style'],armed['attack_elevation_rule']),('fist','melee'))
        self.assertGreater(armed['attack'],base['attack'])
        state['inventory'].append({'instance_id':'pelt','item_id':'thick_bear_pelt'});c['equipment']['body']='pelt'
        protected=combat._player_unit(state,c,0,0)
        self.assertGreater(protected['max_hp'],armed['max_hp']);self.assertLess(protected['initiative'],armed['initiative'])
        for iid in GEAR:self.assertTrue(Path('frontend/public'+ITEMS[iid]['icon']).exists())


class BearLootCompletionTests(unittest.IsolatedAsyncioTestCase):
    async def test_notice_acknowledgment_survives_both_api_schemas_and_lab_handler(self):
        from types import SimpleNamespace
        from backend import battle_lab
        from backend.main import CombatCommandRequest
        from time import monotonic
        identity=SimpleNamespace(guild_id='radiant-qa',user_id='qa')
        b=combat.create_battle(new_game({'name':'QA'}),['player'],'74','contract:supply_watch',True)
        sid='isolated-radiant-qa'
        battle_lab._sessions[sid]={'owner':('radiant-qa','qa'),'touched':monotonic(),
            'battle':b,'mission':{'name':'QA'},'variant':{},'seed':'74'}
        payload={'action':'radiant_choice','choice':'continue'}
        try:
            for schema in (CombatCommandRequest,battle_lab.CommandRequest):
                self.assertEqual(schema(**payload).model_dump(exclude_none=True)['choice'],'continue')
            with patch.object(battle_lab,'authorize'):
                result=await battle_lab.command_battle(sid,battle_lab.CommandRequest(**payload),identity)
            self.assertEqual(battle_lab._sessions[sid]['battle']['radiant_encounter']['state'],'active')
            self.assertEqual(result['battle']['radiant_encounter']['state'],'active')
        finally:battle_lab._sessions.pop(sid,None)

    async def test_real_completion_roll_five_drops_claws_six_does_not_and_pelt_always(self):
        import random
        from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
        from backend.db import Base
        from backend.models import PlayerState,MissionInstance
        from backend.content import MISSION_TEMPLATES
        from backend.game import analyze_mission
        from backend.services import _finish_battle
        original_random=random.Random
        for item_roll in (5,6):
            engine=create_async_engine('sqlite+aiosqlite:///:memory:')
            try:
                async with engine.begin() as conn:await conn.run_sync(Base.metadata.create_all)
                factory=async_sessionmaker(engine,expire_on_commit=False)
                state=new_game({'name':'QA'})
                b=combat.create_battle(state,['player'],'74','contract:supply_watch',True)
                combat_radiant.choose(b,'continue')
                bear=b['units'][combat_radiant.BEAR_ID];bear.update(condition='dead',alive=False,conscious=False)
                b.update(status='complete',outcome='success',battle_won=True,auto_looted_ids=[bear['id']])
                analysis=analyze_mission(state,MISSION_TEMPLATES['supply_watch'],['player'])
                analysis['battle']=b
                async with factory() as session:
                    player=PlayerState(guild_id='bear-qa',user_id='owner',display_name='QA',state=state,updated_at=0)
                    mission=MissionInstance(id='bear-loot-qa',guild_id='bear-qa',template_id='supply_watch',pool_slot=0,position=0,
                        spawned_at=0,expires_at=9999999999,duration_seconds=0,status='battle',claimed_by_user_id='owner',party_ids=['player'],analysis=analysis)
                    session.add_all([player,mission]);await session.flush()
                    class LootRng:
                        def randint(self,lo,hi):return 0 if (lo,hi)==(0,0) else item_roll
                    def rng(seed=None):return LootRng() if seed=='bear-loot-qa:corpse-loot' else original_random(seed)
                    with patch('backend.services.random.Random',side_effect=rng):
                        result=await _finish_battle(session,mission,player,b)
                    items=result['rewards'].get('items',[])
                    self.assertIn('thick_bear_pelt',items)
                    self.assertEqual('bear_claws' in items,item_roll==5)
                    report=result['battle_report']['corpse_loot'][0]
                    self.assertEqual(report['bonus_items'],['thick_bear_pelt'])
            finally:await engine.dispose()
