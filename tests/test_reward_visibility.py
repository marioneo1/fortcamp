import unittest
from backend.reward_visibility import public_reward_preview


class RewardVisibilityTests(unittest.TestCase):
    def test_hidden_names_and_odds_are_not_in_briefing(self):
        mission = {'description': 'Check the canal locks.', 'reward_preview': [
            'Gold', 'Lockkeeper’s Lens · 3% discovery', 'Exclusive: Secret Boots (4% / 6% critical success)',
            'Live-capture exclusive: Captor Gloves (drop chance)', 'Chain relic: Crown (14%; 22% on critical success)']}
        self.assertEqual(public_reward_preview(mission), ['Gold', 'Possible equipment discoveries', 'Possible unusual equipment from live captures'])

    def test_explicitly_disclosed_equipment_stays_named_without_rates(self):
        mission = {'description': 'Recover the Storm Rod carried by the bandit captain.',
                   'reward_preview': ['Exclusive: Storm Rod (4% / 6% critical success)']}
        self.assertEqual(public_reward_preview(mission), ['Storm Rod (possible recovery)'])
        mission['description'] = 'A guild commission.'
        mission['disclosed_rewards'] = ['Storm Rod']
        self.assertEqual(public_reward_preview(mission), ['Storm Rod (possible recovery)'])
