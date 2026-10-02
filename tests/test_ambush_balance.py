"""Opening ambush behavior and authored goblin boss pacing."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from backend.game import new_game
from backend.combat import (
    create_goblin_warcamp_battle, create_battle, apply_player_command,
    battle_view, _attack_hits, _deal_damage,
)
from backend.mission_decisions import setup_encounter


class AmbushTests(unittest.TestCase):
    def setUp(self):
        self.state = new_game({'name': 'Scout'})
        self.battle = create_goblin_warcamp_battle(self.state, ['player'], 'sleep-test', defer_start=True)
        setup_encounter(self.battle, {'setup': 'ambush'})

    def sleepers(self):
        return [u['id'] for u in self.battle['units'].values()
                if any(s['id'] == 'ambush_sleep' for s in u['statuses'])]

    def test_three_whole_rounds_without_enemy_movement_or_damage(self):
        positions = {u['id']: (u['x'], u['y']) for u in self.battle['units'].values() if u['team'] == 'enemy'}
        hp = self.battle['units']['player']['hp']
        for expected_round in (1, 2, 3):
            self.assertEqual(self.battle['round'], expected_round)
            self.assertEqual(set(self.sleepers()), set(positions))
            view = battle_view(self.battle)
            self.assertEqual(view['units']['gob_chief']['statuses'][0]['rounds'], 4 - expected_round)
            self.assertEqual({u['id']: (u['x'], u['y']) for u in self.battle['units'].values() if u['team'] == 'enemy'}, positions)
            self.assertEqual(self.battle['units']['player']['hp'], hp)
            apply_player_command(self.battle, {'action': 'end_turn'})
        self.assertEqual(self.battle['round'], 4)
        self.assertFalse(self.sleepers())
        self.assertNotIn('ambush_sleep_until_round', self.battle)

    def test_positioning_and_invalid_attack_do_not_wake_enemies(self):
        view = battle_view(self.battle)
        tile = next(t for t in view['reachable'] if (t['x'], t['y']) != (1, 7))
        apply_player_command(self.battle, {'action': 'move', **tile})
        self.assertEqual(len(self.sleepers()), 4)
        with self.assertRaisesRegex(ValueError, 'outside attack range'):
            apply_player_command(self.battle, {'action': 'attack', 'target_id': 'gob_chief'})
        self.assertEqual(len(self.sleepers()), 4)

    def test_missed_attack_wakes_every_enemy_but_preserves_other_statuses(self):
        target = self.battle['units']['gob_guard']
        target['statuses'].append({'id': 'sleep', 'turns': 2})
        with patch('backend.combat.random.Random') as rng:
            rng.return_value.randint.return_value = 100
            hit, _, _ = _attack_hits(self.battle, self.battle['units']['player'], target, 'ballistic')
        self.assertFalse(hit)
        self.assertFalse(self.sleepers())
        self.assertIn({'id': 'sleep', 'turns': 2}, target['statuses'])
        self.assertEqual(sum('wakes the whole camp' in line for line in self.battle['log']), 1)

    def test_thrown_impact_also_wakes_all_enemies(self):
        _deal_damage(self.battle, {'id': 'player', 'name': 'Scout', 'attack': 5, 'weapon': 'thrown stone'}, self.battle['units']['gob_guard'])
        self.assertFalse(self.sleepers())

    def test_normal_opening_does_not_put_enemies_to_sleep(self):
        battle = create_goblin_warcamp_battle(self.state, ['player'], 'direct', defer_start=True)
        setup_encounter(battle, {'setup': 'alert'})
        self.assertNotIn('ambush_sleep_until_round', battle)
        self.assertFalse(any(u['statuses'] for u in battle['units'].values()))


class GoblinBossBalanceTests(unittest.TestCase):
    def test_prepared_two_person_team_can_win_with_normal_gear(self):
        state = new_game({'name': 'Tank', 'attributes': {'str': 9, 'dex': 9, 'agi': 8, 'vit': 9},
                          'perks': {'combat': 'skilled'}})
        tank = state['characters'][0]
        archer = deepcopy(tank)
        archer.update(id='archer', name='Archer', is_player=False, loyalty=100)
        state['characters'].append(archer)
        state['inventory'] += [{'instance_id': 'blade', 'item_id': 'knight_blade'},
                               {'instance_id': 'bow', 'item_id': 'short_bow'}]
        tank['equipment']['weapon'] = 'blade'
        archer['equipment']['weapon'] = 'bow'
        battle = create_goblin_warcamp_battle(state, ['player', 'archer'], '9', defer_start=True)
        setup_encounter(battle, {'setup': 'ambush'})
        for _ in range(50):
            view = battle_view(battle)
            if battle.get('decision_pending'):
                break
            self.assertEqual(battle['status'], 'active')
            actor = view['current_unit_id']
            if battle['round'] <= 3:
                # Cross the open lane quietly, then put both attackers near the chief.
                destination = (4, 2) if actor == 'player' else (3, 1)
                tile = min(view['reachable'], key=lambda t: (
                    abs(t['x'] - destination[0]) + abs(t['y'] - destination[1]), t['x'], t['y']))
                apply_player_command(battle, {'action': 'move', **tile})
                apply_player_command(battle, {'action': 'end_turn'})
            else:
                targets = [uid for uid in ('gob_chief', 'gob_archer', 'gob_horn', 'gob_guard')
                           if view['attack_previews'].get(uid, {}).get('attack')]
                if targets:
                    target = targets[0]
                    preview = view['attack_previews'][target]['attack']
                    command = {'action': 'attack', 'target_id': target}
                    if preview.get('move_to'):
                        command['move_to'] = preview['move_to']
                    apply_player_command(battle, command)
                else:
                    apply_player_command(battle, {'action': 'guard'})
        self.assertTrue(battle.get('decision_pending'))
        self.assertTrue(battle['objectives'][0]['complete'])
        apply_player_command(battle, {'action': 'claim_victory'})
        self.assertEqual(battle['outcome'], 'success')

    def test_warcamp_is_fixed_boss_encounter_and_redoubt_is_harder(self):
        state = new_game({'name': 'Tank'})
        camp = create_goblin_warcamp_battle(state, ['player'], 'chief', defer_start=True)
        chief = camp['units']['gob_chief']
        self.assertTrue(chief['boss'])
        self.assertGreater(chief['hp'], camp['units']['player']['hp'])
        self.assertGreater(chief['hp'], camp['units']['gob_guard']['hp'] * 2)
        self.assertGreater(chief['attack'], camp['units']['gob_guard']['attack'])
        strong = deepcopy(state)
        strong['characters'][0]['attributes'].update(str=50, vit=50)
        bigger_party = create_goblin_warcamp_battle(strong, ['player'], 'chief', defer_start=True)
        for stat in ('hp', 'armor', 'attack'):
            self.assertEqual(chief[stat], bigger_party['units']['gob_chief'][stat])
        redoubt = create_battle(state, ['player'], 'redoubt', 'contract:goblin_chieftain', defer_start=True)
        commander = redoubt['units']['contract_enemy_0']
        self.assertGreater(commander['hp'], chief['hp'])
        self.assertGreater(commander['attack'], chief['attack'])


if __name__ == '__main__':
    unittest.main()
