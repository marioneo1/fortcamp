import unittest
from copy import deepcopy

from backend import combat
from backend.battle_lab import layout_presets
from backend.game import new_game
from tools.compare_character_growth import ATTRS
from tools.trial_character_growth import prepare_trial, opening_damage


class GrowthCombatTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = new_game({'name': 'Trial test', 'starting_role': 'fighter',
                              'attributes': dict.fromkeys(ATTRS, 6)})
        preset = layout_presets('contract:highway_ambush')[0]
        cls.base = combat.create_contract_battle(cls.state, ['player'], preset['seed'], 'highway_ambush', True)

    def test_trial_and_damage_probe_leave_sources_unchanged(self):
        original = deepcopy(self.base)
        state = deepcopy(self.state)
        trial = prepare_trial(self.base, self.state, 'shared12', 'D')
        enemy = next(u for u in trial['units'].values() if u['team'] == 'enemy')
        before = deepcopy(trial)
        self.assertGreater(opening_damage(trial, 'player', enemy['id']), 0)
        self.assertEqual(trial, before)
        self.assertEqual(self.base, original)
        self.assertEqual(self.state, state)

    def test_player_rank_does_not_multiply_flat_gear_bonus(self):
        trial = prepare_trial(self.base, self.state, 'shared24', 'D')
        old, new = self.base['units']['player'], trial['units']['player']
        self.assertEqual(new['strength'] - old['strength'], 2)
        self.assertEqual(new['attack'] - old['attack'], 4) # +3 base experiment, +1 ranked STR.
        self.assertEqual(new['max_hp'] - old['max_hp'], 20) # +12 base experiment, +8 ranked VIT.

    def test_shared_arms_only_differ_in_fixed_bases(self):
        a = prepare_trial(self.base, self.state, 'shared24', 'D')
        b = prepare_trial(self.base, self.state, 'shared12', 'D')
        for uid, unit in a['units'].items():
            other = b['units'][uid]
            self.assertEqual(unit['strength'], other['strength'])
            self.assertEqual(unit['attack'] - other['attack'], 3)
            self.assertEqual(unit['armor'], other['armor'])
            self.assertEqual(unit['skills'][0]['id'], other['skills'][0]['id'])

    def test_enemy_flat_hp_and_attribute_perks_survive_projection(self):
        base = deepcopy(self.base)
        enemy = next(u for u in base['units'].values() if u['team'] == 'enemy')
        enemy.update(origin_perks=[], battle_attribute_roll=None, perk_modifiers={})
        a = prepare_trial(base, self.state, 'shared24', 'D')['units'][enemy['id']]
        enemy.update(origin_perks=['strong_armed'], perk_modifiers={'hp': 7})
        b = prepare_trial(base, self.state, 'shared24', 'D')['units'][enemy['id']]
        self.assertEqual(b['strength'] - a['strength'], 2)
        self.assertEqual(b['attack'] - a['attack'], 1)
        self.assertEqual(b['max_hp'] - a['max_hp'], 7)


if __name__ == '__main__':
    unittest.main()
