import unittest
from copy import deepcopy

from backend import combat
from backend.battle_lab import catalogue, layout_presets
from backend.battle_maps import compile_generated_battle_map
from backend.content import MISSION_TEMPLATES
from backend.game import new_game
from backend.prison_recruitment import initialize_prisoner


ENCOUNTERS = ('frontier_watch_defense', 'prison_rescue_e')


class FinalERankMapsTests(unittest.TestCase):
    def battles(self):
        for encounter in ENCOUNTERS:
            for preset in layout_presets(encounter):
                yield combat.create_battle(new_game({'name':'QA', 'starting_role':'fighter'}),
                                           ['player'], preset['seed'], encounter, True)

    def test_all_eight_layouts_have_legal_connected_spawns_and_comparable_budgets(self):
        budgets = {encounter: [] for encounter in ENCOUNTERS}
        count = 0
        for battle in self.battles():
            count += 1
            enemies = combat._living(battle, 'enemy')
            positions = [(u['x'],u['y']) for u in battle['units'].values()]
            self.assertEqual(len(set(positions)), len(positions))
            probe = deepcopy(battle)
            probe['units'] = {}
            walker = deepcopy(battle['units']['player'])
            walker.update(move=1000, movement_origin=None)
            reachable, _ = combat._movement_tree(probe, walker)
            for unit in battle['units'].values():
                self.assertFalse(combat._blocked(probe, unit['x'], unit['y']))
                self.assertIn((unit['x'],unit['y']), reachable)
            for unit in enemies:
                self.assertGreaterEqual(unit['max_hp'],20)
                self.assertFalse(unit['boss'])
                self.assertEqual(unit['race'],'Goblin')
                self.assertTrue(unit['skills'])
                self.assertTrue(unit.get('combat_voice_key'))
            budgets[battle['encounter_id']].append(sum(u['max_hp'] for u in enemies))
        self.assertEqual(count,8)
        for values in budgets.values():
            self.assertLessEqual(max(values)/min(values),1.15)

    def test_captive_can_be_carried_out_in_every_rescue_layout(self):
        for preset in layout_presets('prison_rescue_e'):
            battle = combat.create_battle(new_game({'starting_role':'fighter'}),['player'],preset['seed'],'prison_rescue_e',True)
            captive = battle['units']['captive_courier']
            actor = battle['units']['player']
            actor.update(x=captive['x']-1,y=captive['y'],move=1000,movement_origin=None,carrying=captive['id'])
            captive['carried_by']=actor['id']
            reachable, _ = combat._movement_tree(battle, actor)
            self.assertTrue(any((t['x'],t['y']) in reachable for t in battle['extraction']['tiles']))
            captive.update(extracted=True,extracted_with='player')
            combat._check_end_rules(battle)
            self.assertTrue(battle['objectives'][0]['complete'])
            self.assertTrue(battle['battle_won'])

    def test_secured_field_rescues_captive_without_dispatch_story(self):
        for preset in layout_presets('prison_rescue_e'):
            battle = combat.create_battle(new_game({}),['player'],preset['seed'],'prison_rescue_e',True)
            for unit in combat._living(battle,'enemy'):
                unit.update(hp=0,alive=False,conscious=False,condition='dead')
            combat._check_end_rules(battle)
            self.assertTrue(battle['units']['captive_courier']['extracted'])
            self.assertTrue(battle['battle_won'])
            self.assertNotIn('dispatch', battle['victory_log'].lower())
            self.assertNotIn('dispatch_satchel',battle['objects'])

    def test_recruits_preserve_kits_and_defense_preparation_keeps_keeper_clear(self):
        for battle in self.battles():
            for unit in combat._living(battle,'enemy'):
                captive={'id':'recruit','name':unit['name'],'race':unit['race'],
                         'recruitable_snapshot':deepcopy(unit['recruitable_snapshot'])}
                initialize_prisoner(captive,now=0)
                candidate=captive['recruitment']['candidate']
                self.assertEqual(candidate['equipped_skills'],unit['skill_slot_order'])
                self.assertEqual(candidate['combat_specialization'],unit['combat_specialization'])
            if battle['encounter_id']=='frontier_watch_defense':
                keeper=battle['units']['watch_keeper']
                self.assertNotIn({'x':keeper['x'],'y':keeper['y']},battle['deployment_zone'])
                self.assertEqual(battle['status'],'preparing')
                combat.apply_player_command(battle,{'action':'start_battle'})
                self.assertEqual(battle['status'],'active')

    def test_only_e_rank_rescue_changes_and_battle_lab_exposes_all_layouts(self):
        self.assertEqual(MISSION_TEMPLATES['prison_rescue_e']['combat_encounter']['id'],'prison_rescue_e')
        self.assertEqual(MISSION_TEMPLATES['prison_rescue_d']['combat_encounter']['id'],'goblin_captive_cart')
        self.assertEqual(MISSION_TEMPLATES['goblin_captive_cart']['rank'],'D')
        original=combat.create_captive_cart_battle(new_game({}),['player'],'legacy-test',True)
        self.assertEqual(len(combat._living(original,'enemy')),4)
        self.assertEqual(len(original['objectives']),3)
        combat._check_captive_cart_end(original)
        indexed={m['id']:m for m in catalogue()}
        for mid,encounter in [('hedgerow_watch_defense','frontier_watch_defense'),('prison_rescue_e','prison_rescue_e')]:
            self.assertEqual(len(indexed[mid]['variants'][0]['layout_presets']),4)
            for preset in layout_presets(encounter):
                self.assertEqual(compile_generated_battle_map(encounter,preset['seed']),
                                 compile_generated_battle_map(encounter,preset['seed']))
