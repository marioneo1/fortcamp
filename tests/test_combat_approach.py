import unittest
from copy import deepcopy
from unittest.mock import patch
from backend.game import new_game
from backend.combat import create_goblin_warcamp_battle, battle_view, apply_player_command

class AttackApproachTests(unittest.TestCase):
    def setUp(self):
        self.battle=create_goblin_warcamp_battle(new_game({'name':'Fighter'}),['player'],'approach')
        b=self.battle
        b.update(terrain=[],ground_tiles=[],elevation=[],void_tiles=[])
        for obj in b['objects'].values():obj['blocking']=False
        self.actor=b['units']['player']
        self.actor.update(x=1,y=5,move=3,attack_range=1,attack_elevation_rule='melee',nonlethal_capable=True,acted=False,hp=100,max_hp=100)
        self.target=b['units']['gob_guard']
        self.target.update(x=4,y=5,hp=100,max_hp=100)
        for i,u in enumerate(b['units'].values()):
            if u['id'] not in ['player',self.target['id']]:u.update(x=7,y=i)
        b['turn_order']=['player',*[uid for uid in b['units'] if uid!='player']];b['turn_index']=0

    def test_preview_is_cheapest_legal_approach_without_moving_unit(self):
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]['attack']
        self.assertEqual(preview['movement_cost'],2)
        self.assertEqual(preview['move_to'],{'x':3,'y':5})
        self.assertEqual([p['cost'] for p in preview['path']],[1,2])
        self.assertEqual((self.actor['x'],self.actor['y']),(1,5))

    def test_movement_tree_exports_only_validated_routes_without_mutating_battle(self):
        original=deepcopy(self.battle)
        self.battle['elevation']=[{'x':2,'y':5,'height':4}]
        view=battle_view(self.battle)
        nodes={(p['x'],p['y']):p for p in view['movement_tree']}
        self.assertNotIn((2,5),nodes)
        self.assertEqual(set(nodes),{(p['x'],p['y']) for p in view['reachable']})
        for point,node in nodes.items():
            if node['parent'] is not None:
                self.assertIn(tuple(node['parent']),nodes)
                self.assertLess(nodes[tuple(node['parent'])]['cost'],node['cost'])
            accepted=apply_player_command(deepcopy(self.battle),{'action':'move','x':point[0],'y':point[1]})
            self.assertEqual((accepted['units']['player']['x'],accepted['units']['player']['y']),point)
        self.assertNotIn('movement_tree',self.battle)
        self.assertEqual(self.battle['units'],original['units'])

    def test_confirmed_approach_attacks_and_records_walk_before_hit(self):
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]['attack']
        with patch('backend.combat._advance_to_player'):
            result=apply_player_command(self.battle,{'action':'attack','target_id':self.target['id'],'move_to':preview['move_to']})
        self.assertEqual((self.actor['x'],self.actor['y']),(3,5))
        self.assertTrue(self.actor['acted'])
        events=result['animation_events']
        self.assertEqual(events[0]['type'],'movement');self.assertEqual(events[1]['type'],'melee_attack')
        self.assertEqual(events[0]['points'][0],{'x':1,'y':5})

    def test_unconfirmed_attack_does_not_move_and_invalid_destination_does_not_mutate(self):
        for extra in [{},{'move_to':{'x':4,'y':5}},{'move_to':{'x':6,'y':5}}]:
            with self.assertRaises(ValueError):apply_player_command(self.battle,{'action':'attack','target_id':self.target['id'],**extra})
            self.assertEqual((self.actor['x'],self.actor['y']),(1,5));self.assertFalse(self.actor['acted'])
            self.assertEqual(self.target['hp'],100)

    def test_cliffs_and_occupied_routes_are_not_approachable(self):
        self.battle['elevation']=[{'x':3,'y':5,'height':4}]
        self.actor['move']=2
        self.assertIsNone(battle_view(self.battle)['attack_previews'][self.target['id']]['attack'])

    def test_reposition_uses_original_turn_budget(self):
        apply_player_command(self.battle,{'action':'move','x':2,'y':5})
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]['subdue']
        self.assertEqual(preview['movement_cost'],2)
        with patch('backend.combat._advance_to_player'):
            result=apply_player_command(self.battle,{'action':'subdue','target_id':self.target['id'],'move_to':preview['move_to']})
        self.assertTrue(self.actor['acted']);self.assertEqual((self.actor['x'],self.actor['y']),(3,5))
        self.assertEqual(result['animation_events'][0]['points'][0],{'x':2,'y':5})

    def test_in_range_target_needs_no_approach(self):
        self.target['x']=2
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]['attack']
        self.assertNotIn('move_to',preview)

    def test_ranged_approach_respects_line_of_sight(self):
        self.actor.update(attack_range=3,attack_elevation_rule='ballistic',move=1)
        self.battle['terrain']=[{'id':'wall','x':2,'y':5,'kind':'wall','blocking':True}]
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]['attack']
        self.assertIsNone(preview)
        self.actor['move']=2
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]['attack']
        self.assertIsNotNone(preview);self.assertIn('move_to',preview)

    def test_spent_skill_and_nonlethal_incapable_weapon_get_no_approach(self):
        self.actor.update(nonlethal_capable=False,special={'id':'test','range':1,'elevation_rule':'melee'},special_used=True)
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]
        self.assertIsNone(preview['subdue']);self.assertIsNone(preview['skill'])
        with self.assertRaises(ValueError):apply_player_command(self.battle,{'action':'skill','target_id':self.target['id'],'move_to':{'x':3,'y':5}})
        self.assertEqual((self.actor['x'],self.actor['y']),(1,5))
