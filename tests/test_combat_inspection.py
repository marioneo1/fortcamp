import unittest
from copy import deepcopy

from backend import combat
from backend.combat_inspection import explanations
from backend.game import new_game


class CombatInspectionTests(unittest.TestCase):
    def test_ranked_player_and_enemy_help_is_readable_numeric_and_read_only(self):
        state = new_game({'name': 'Reader'})
        state['characters'][0]['adventurer_rank'] = 'D'
        battle = combat.create_contract_battle(state, ['player'], 'readable-help', 'highway_ambush', True)
        original = deepcopy(battle)
        for unit in combat.battle_view(battle)['units'].values():
            help_text = explanations(unit)
            self.assertIn('÷ 2, rounded down', help_text['Attack'])
            self.assertIn('×1.3', help_text['Attack'])
            for name, text in help_text.items():
                with self.subTest(unit=unit['id'],stat=name):
                    self.assertNotIn('//', text)
                    self.assertNotIn('ceil(', text)
                    self.assertIn('\n', text)
                    self.assertLessEqual(len(text.split('\n')[0].split('. ')), 2)
        self.assertEqual(battle, original)

    def test_rat_help_does_not_present_the_humanoid_attack_formula(self):
        unit = {'attack':1,'effective_attack':1,'form':{'id':'rat','persistent':True},
                'stat_sources':{'Attack':'2 + STR 8 ÷ 2 + weapon'},'statuses':[]}
        help_text = explanations(unit)
        self.assertIn('Rat profile = 1', help_text['Attack'])
        self.assertNotIn('STR 8', help_text['Attack'])
        self.assertIn('100% − 90% = 10%', help_text['Evasion'])

    def test_old_saved_formula_is_readable_without_recalculating_stats(self):
        unit = {'attack':9,'effective_attack':9,'armor':3,
                'stat_sources':{'Attack':'5 base + 8//2 STR'},'statuses':[]}
        self.assertIn('8 ÷ 2, rounded down',explanations(unit)['Attack'])
        self.assertEqual(unit['attack'],9)

    def test_minimum_hp_is_explicit_when_the_racial_formula_hits_it(self):
        from backend.combat_stats import sources, health
        from backend.races import race_gameplay
        from unittest.mock import patch
        racial = {**race_gameplay('Human'),'hp_multiplier':.2,'hp_bonus':0}
        with patch('backend.combat_stats.race_gameplay',return_value=racial):
            text = sources(dict.fromkeys(('str','dex','agi','vit','int','luk'),1),'Human')['Health']
        self.assertIn('minimum 8 HP',text)
        self.assertIn(f'= {health(1,racial)}',text)
