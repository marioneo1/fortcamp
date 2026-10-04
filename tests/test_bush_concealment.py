import json
import unittest
from copy import deepcopy
from backend import concealment
from backend.combat import (create_contract_battle, battle_view, apply_player_command,
    _line_of_sight, _enemy_turn, _can_attack, _attack_hits, _player_auto_turn)
from backend.game import new_game
from backend.battle_lab import layout_presets


class BushConcealmentTests(unittest.TestCase):
    def battle(self):
        battle = create_contract_battle(new_game({'name':'Scout'}), ['player'],
                                        'bush-test', 'highway_ambush', True)
        battle.update(width=10, height=5, terrain=[], decorations=[
            {'id':'brush', 'name':'Concealing Brush', 'sprite':'dense_shrub', 'x':5, 'y':2}],
            elevation=[], objects={}, ground_tiles=[], turn_index=0,
            turn_order=['player','contract_enemy_0','contract_enemy_1','contract_enemy_2'])
        player = battle['units']['player']; player.update(x=0,y=2,move=8,initiative=100,loyalty=100)
        enemy = battle['units']['contract_enemy_1'];enemy.update(x=5,y=2,bush_ambusher=True)
        battle['units']['contract_enemy_0'].update(x=8,y=3)
        battle['units']['contract_enemy_2'].update(x=8,y=4)
        return battle

    def test_unseen_enemy_is_absent_from_payload_targets_order_and_events(self):
        battle=self.battle();enemy=battle['units']['contract_enemy_1']
        battle['log'].append(enemy['name']+' waits in cover.')
        battle['animation_events']=[{'type':'movement','unit_id':enemy['id'],'points':[{'x':5,'y':2}]}]
        view=battle_view(battle)
        self.assertNotIn(enemy['id'],view['units'])
        self.assertNotIn(enemy['id'],view['turn_order'])
        self.assertNotIn(enemy['id'],view['attack_previews'])
        self.assertNotIn(enemy['name'],json.dumps(view))
        self.assertEqual(view['animation_events'],[])
        self.assertEqual(view['current_unit_id'],'player')
        self.assertTrue(any(p['x']==5 and p['y']==2 for p in view['reachable']))
        for action in ('attack','subdue','skill','throw'):
            with self.assertRaises(ValueError):
                apply_player_command(battle,{'action':action,'target_id':enemy['id']})
        self.assertFalse(enemy['spotted'])

    def test_entering_occupied_brush_reveals_contact_and_keeps_main_action(self):
        battle=self.battle();battle_view(battle)
        result=apply_player_command(battle,{'action':'move','x':7,'y':2})
        self.assertEqual((battle['units']['player']['x'],battle['units']['player']['y']),(4,2))
        self.assertIn('contract_enemy_1',result['units'])
        self.assertFalse(battle['units']['player']['acted'])
        self.assertEqual(result['current_unit_id'],'player')
        self.assertEqual(len([s for s in battle['log'] if 'run into' in s]),1)
        restored=json.loads(json.dumps(battle))
        restored['units']['player'].update(x=0,y=2)
        self.assertIn('contract_enemy_1',battle_view(restored)['units'])

    def test_first_command_cannot_bypass_visibility_without_prior_view(self):
        battle=self.battle()
        with self.assertRaises(ValueError):
            apply_player_command(battle,{'action':'attack','target_id':'contract_enemy_1',
                                         'move_to':{'x':4,'y':2}})
        self.assertFalse(battle['units']['contract_enemy_1']['spotted'])
        self.assertEqual(battle['units']['player']['x'],0)

    def test_combined_move_attack_pauses_on_discovery_without_attacking(self):
        battle=self.battle();battle['units']['contract_enemy_0'].update(x=6,y=2)
        battle_view(battle)
        hp=battle['units']['contract_enemy_0']['hp']
        view=apply_player_command(battle,{'action':'attack','target_id':'contract_enemy_0',
                                          'move_to':{'x':5,'y':2}})
        self.assertEqual((battle['units']['player']['x'],battle['units']['player']['y']),(4,2))
        self.assertEqual(battle['units']['contract_enemy_0']['hp'],hp)
        self.assertFalse(battle['units']['player']['acted'])
        self.assertIn('contract_enemy_1',view['units'])
        self.assertEqual(view['current_unit_id'],'player')
        self.assertIn('cost',view['movement_path'][-1])

    def test_previously_searched_empty_brush_does_not_spot_distant_arrival(self):
        battle=self.battle();battle['units']['player'].update(x=3,y=2)
        enemy=battle['units']['contract_enemy_1'];enemy.update(x=8,y=1)
        battle_view(battle)
        enemy.update(x=5,y=2,spotted=False)
        battle['units']['player'].update(x=0,y=2)
        self.assertNotIn(enemy['id'],battle_view(battle)['units'])

    def test_adjacent_enemy_stays_hidden_even_after_wall_is_destroyed(self):
        battle=self.battle();battle['units']['player'].update(x=3,y=2)
        battle['terrain']=[{'id':'wall','x':4,'y':2,'blocking':True,'blocks_sight':True}]
        self.assertNotIn('contract_enemy_1',battle_view(battle)['units'])
        battle['terrain'][0]['destroyed']=True
        self.assertNotIn('contract_enemy_1',battle_view(battle)['units'])

    def test_hidden_ambusher_waits_without_name_or_movement_leak(self):
        battle=self.battle();battle_view(battle);enemy=battle['units']['contract_enemy_1']
        battle['turn_index']=2
        _enemy_turn(battle,enemy)
        self.assertEqual((enemy['x'],enemy['y']),(5,2))
        self.assertFalse(enemy['spotted'])
        self.assertNotIn(enemy['name'],json.dumps(battle_view(battle)))

    def test_proximity_never_reveals_and_clear_attack_springs_ambush(self):
        battle=self.battle();battle['units']['player'].update(x=4,y=2)
        enemy=battle['units']['contract_enemy_1'];battle['turn_index']=2
        self.assertNotIn(enemy['id'],battle_view(battle)['units'])
        _enemy_turn(battle,enemy)
        self.assertTrue(enemy['spotted'])
        self.assertTrue(battle['ambush_sprung'])
        self.assertIn(enemy['name'],json.dumps(battle_view(battle)))

    def test_two_waits_then_regular_ai_pursues_instead_of_waiting_forever(self):
        battle=self.battle();battle_view(battle);enemy=battle['units']['contract_enemy_1']
        for _ in range(2):
            battle['turn_index']=2
            _enemy_turn(battle,enemy)
            self.assertEqual((enemy['x'],enemy['y']),(5,2))
        self.assertFalse(enemy['spotted'])
        battle['turn_index']=2
        _enemy_turn(battle,enemy)
        self.assertNotEqual((enemy['x'],enemy['y']),(5,2))
        self.assertEqual(enemy['ambush_plan'],'pursue')

    def test_last_hidden_enemy_pursues_immediately_and_view_explains_unfinished_fight(self):
        battle=self.battle()
        for uid in ('contract_enemy_0','contract_enemy_2'):
            battle['units'][uid].update(alive=False,conscious=False,condition='dead')
        view=battle_view(battle)
        self.assertTrue(view['concealment_warning'])
        enemy=battle['units']['contract_enemy_1'];battle['turn_index']=2
        _enemy_turn(battle,enemy)
        self.assertNotEqual((enemy['x'],enemy['y']),(5,2))
        self.assertTrue(enemy['spotted'])
        self.assertFalse(battle_view(battle)['concealment_warning'])

    def test_close_target_behind_wall_does_not_trigger_a_phantom_attack(self):
        battle=self.battle();battle['units']['player'].update(x=3,y=2)
        battle['units']['contract_enemy_1'].update(attack_range=3)
        battle['terrain']=[{'id':'wall','x':4,'y':y,'blocking':True,'blocks_sight':True}
                           for y in range(5)]
        battle_view(battle);enemy=battle['units']['contract_enemy_1'];battle['turn_index']=2
        _enemy_turn(battle,enemy)
        self.assertFalse(enemy['spotted'])
        self.assertEqual(enemy['ambush_waits'],1)
        self.assertEqual((enemy['x'],enemy['y']),(5,2))

    def test_melee_ambusher_waits_for_road_kill_zone_then_strikes(self):
        battle=self.battle();battle['units']['player'].update(x=2,y=2)
        battle['ambush_lane']=[[2,1]]
        battle_view(battle);enemy=battle['units']['contract_enemy_1'];battle['turn_index']=2
        _enemy_turn(battle,enemy)
        self.assertFalse(enemy['spotted'])
        self.assertEqual(enemy['ambush_waits'],1)
        battle['ambush_lane']=[[2,2]];battle['turn_index']=2
        _enemy_turn(battle,enemy)
        self.assertTrue(battle['ambush_sprung'])
        self.assertEqual(enemy['ambush_plan'],'strike')
        self.assertTrue(enemy['spotted'])

    def test_sprung_signal_sends_other_ambusher_into_normal_pursuit(self):
        battle=self.battle();battle_view(battle)
        battle['ambush_sprung']=True
        enemy=battle['units']['contract_enemy_1'];battle['turn_index']=2
        _enemy_turn(battle,enemy)
        self.assertNotEqual((enemy['x'],enemy['y']),(5,2))
        self.assertTrue(enemy['spotted'])
        self.assertEqual(enemy.get('ambush_waits',0),0)

    def test_attack_leaving_cover_and_unconsciousness_reveal(self):
        for trigger in ('attack','move','unconscious'):
            battle=self.battle();battle_view(battle);enemy=battle['units']['contract_enemy_1']
            if trigger=='attack':
                _attack_hits(battle,enemy,battle['units']['player'],'ballistic')
            elif trigger=='move':enemy['x']=6
            else:enemy.update(conscious=False,condition='unconscious')
            self.assertIn(enemy['id'],battle_view(battle)['units'])

    def test_already_seen_enemy_never_hides_again_and_old_save_keeps_visibility(self):
        battle=self.battle();enemy=battle['units']['contract_enemy_1'];enemy['x']=6
        battle_view(battle);enemy['x']=5
        self.assertIn(enemy['id'],battle_view(battle)['units'])
        old=self.battle();old['action_count']=4
        self.assertIn('contract_enemy_1',battle_view(old)['units'])

    def test_auto_searches_brush_without_targeting_secret_enemy(self):
        battle=self.battle()
        for uid in ('contract_enemy_0','contract_enemy_2'):
            battle['units'][uid].update(alive=False,conscious=False,condition='dead')
        battle_view(battle)
        hp=battle['units']['contract_enemy_1']['hp']
        _player_auto_turn(battle,battle['units']['player'],'balanced')
        self.assertTrue(battle['units']['contract_enemy_1']['spotted'])
        self.assertEqual(battle['units']['contract_enemy_1']['hp'],hp)
        self.assertEqual((battle['units']['player']['x'],battle['units']['player']['y']),(4,2))

    def test_real_road_ambush_variants_keep_hidden_scouts_and_normal_budgets(self):
        presets=layout_presets('contract:highway_ambush')
        ambushes=0
        for preset in presets:
            battle=create_contract_battle(new_game({'name':'Scout'}),['player'],preset['seed'],'highway_ambush',True)
            view=battle_view(battle)
            hidden=[u for u in battle['units'].values() if concealment.unseen(u)]
            if battle.get('ambush_enemy_indices'):
                ambushes+=1
                self.assertEqual(len(hidden),2)
                self.assertTrue(all(u.get('bush_ambusher') for u in hidden))
                self.assertTrue(all(u['id'] not in view['units'] for u in hidden))
            else:self.assertFalse(hidden)
        self.assertEqual(ambushes,2)


if __name__=='__main__':unittest.main()
