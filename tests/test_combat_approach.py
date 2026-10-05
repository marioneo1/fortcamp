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

    def test_final_position_and_guard_are_one_validated_command(self):
        with patch('backend.combat._advance_to_player'):
            apply_player_command(self.battle, {'action':'guard','position':{'x':2,'y':5}})
        self.assertEqual((self.actor['x'],self.actor['y']),(2,5))
        self.assertTrue(self.actor['guarding'])
        self.assertTrue(self.actor['acted'])

    def test_combined_position_rejects_out_of_range_and_does_not_guard(self):
        with self.assertRaises(ValueError):
            apply_player_command(self.battle, {'action':'guard','position':{'x':99,'y':99}})
        self.assertFalse(self.actor.get('guarding',False))

    def test_discovery_interrupts_combined_guard_without_spending_the_action(self):
        with patch('backend.combat._scout_path',return_value=[(1,4)]), patch('backend.combat._advance_to_player') as advance:
            apply_player_command(self.battle, {'action':'guard','position':{'x':2,'y':4}})
        self.assertEqual((self.actor['x'],self.actor['y']),(1,4))
        self.assertFalse(self.actor.get('guarding',False))
        self.assertFalse(self.actor.get('acted',False))
        advance.assert_not_called()

    def test_preview_is_cheapest_legal_approach_without_moving_unit(self):
        preview=battle_view(self.battle)['attack_previews'][self.target['id']]['attack']
        self.assertEqual(preview['movement_cost'],2)
        self.assertEqual(preview['move_to'],{'x':3,'y':5})
        self.assertEqual([p['cost'] for p in preview['path']],[1,2])
        self.assertEqual((self.actor['x'],self.actor['y']),(1,5))

    def test_provisional_move_can_return_to_origin_and_choose_another_path(self):
        apply_player_command(self.battle, {'action':'move','x':2,'y':5})
        self.assertEqual((self.actor['x'],self.actor['y']),(2,5))
        apply_player_command(self.battle, {'action':'move','x':1,'y':5})
        self.assertEqual((self.actor['x'],self.actor['y']),(1,5))
        self.assertFalse(self.actor['moved'])
        self.assertFalse(self.actor['acted'])
        self.assertEqual(self.actor['movement_path'],[])
        apply_player_command(self.battle, {'action':'move','x':1,'y':3})
        self.assertEqual((self.actor['x'],self.actor['y']),(1,3))
        self.assertEqual(self.actor['movement_origin'],{'x':1,'y':5})

    def test_adjacent_reposition_walks_directly_between_origin_tree_branches(self):
        from backend.combat import _movement_tree, _movement_path, _reposition_route, _scout_path
        self.actor.update(move=5)
        apply_player_command(self.battle, {'action':'move','x':2,'y':5})
        reachable, parents = _movement_tree(self.battle, self.actor)
        self.assertNotIn({'x':2,'y':5,'cost':1}, _movement_path(parents,reachable,(2,4)))
        self.assertEqual(_reposition_route(self.battle,self.actor,(2,4),reachable),[(2,4)])
        with patch('backend.combat._scout_path', wraps=_scout_path) as scout:
            apply_player_command(self.battle, {'action':'move','x':2,'y':4})
        self.assertEqual(scout.call_args.args[2],[(2,4)])
        self.assertEqual(self.actor['movement_origin'],{'x':1,'y':5})

    def test_direct_reposition_respects_wall_crossings_and_original_budget(self):
        from backend.combat import _movement_tree, _reposition_route
        self.actor.update(move=5)
        apply_player_command(self.battle, {'action':'move','x':2,'y':4})
        self.battle['terrain']=[{'id':'edge','x':2,'y':4,'kind':'wall','blocking':True,'edge_wall':True,'wall_edges':['east']}]
        reachable, _ = _movement_tree(self.battle,self.actor)
        route=_reposition_route(self.battle,self.actor,(3,4),reachable)
        self.assertNotEqual(route,[(3,4)])
        self.assertEqual(route[-1],(3,4))
        self.actor['move']=2
        with self.assertRaises(ValueError):
            apply_player_command(self.battle,{'action':'move','x':3,'y':4})

    def test_unused_end_turn_guards_and_matches_explicit_guard(self):
        from backend.combat import _deal_damage
        with patch('backend.combat._advance_to_player'):
            apply_player_command(self.battle, {'action':'end_turn'})
        self.assertTrue(self.actor['guarding'])
        self.actor.update(hp=100, armor=0, racial_resistances=[], racial_weaknesses=[])
        attacker={**self.target,'attack':20,'element':None,'on_hit':None}
        plain=deepcopy(self.actor);plain['guarding']=False
        baseline=_deal_damage(deepcopy(self.battle),attacker,plain)
        guarded=_deal_damage(self.battle,attacker,self.actor)
        self.assertEqual(guarded,(baseline*3+2)//4)
        self.assertFalse(self.actor['guarding'])

    def test_ground_spell_preview_and_move_cast_use_same_cells(self):
        from backend.job_loadouts import SKILLS
        spell=deepcopy(SKILLS['job:mage:binding']) if 'job:mage:binding' in SKILLS else next(deepcopy(s) for s in SKILLS.values() if s['type']=='active' and all(e['type']=='zone' for e in s['effects']))
        self.actor['skills']=[spell];self.actor['special']=spell
        view=battle_view(self.battle)
        entries=view['ground_skill_previews'][spell['id']]
        chosen=next((key,p) for key,p in entries.items() if p.get('move_to'))
        key,preview=chosen;x,y=map(int,key.split(','))
        expected={(p['x'],p['y']) for p in preview['zones'][0]['cells']}
        with patch('backend.combat._advance_to_player'):
            result=apply_player_command(self.battle,{'action':'skill','skill_id':spell['id'],'x':x,'y':y,'move_to':preview['move_to']})
        self.assertTrue(self.actor['acted'])
        self.assertEqual((self.actor['x'],self.actor['y']),(preview['move_to']['x'],preview['move_to']['y']))
        self.assertEqual({(p['x'],p['y']) for p in result['zones'][0]['cells']},expected)

    def test_ally_spell_previews_and_accepts_move_and_cast(self):
        from backend.job_loadouts import SKILLS
        spell=deepcopy(SKILLS['job:mage:ward'])
        ally=deepcopy(self.actor);ally.update(id='ally',name='Ally',x=4,y=4)
        self.battle['units']['ally']=ally
        self.actor['skills']=[spell];self.actor['special']=spell
        preview=battle_view(self.battle)['skill_previews'][spell['id']]['ally']
        self.assertIsNotNone(preview['move_to'])
        with patch('backend.combat._advance_to_player'):
            apply_player_command(self.battle,{'action':'skill','skill_id':spell['id'],'target_id':'ally','move_to':preview['move_to']})
        self.assertTrue(any(s['id']=='barrier' for s in ally['statuses']))

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
        self.actor['capture_weapon']={'base':8,'range':1,'elevation_rule':'melee'}
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
