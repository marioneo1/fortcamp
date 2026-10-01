import unittest
from copy import deepcopy
from types import SimpleNamespace
from backend.game import new_game
from backend.services import claim_budget, spend_claim
from backend.economy import camp_action
from backend.main import CharacterCreate

class SoloOnboardingTests(unittest.TestCase):
    def test_solo_bonus_only_in_free_phase_and_stacks_with_upgrades(self):
        state=new_game({'name':'Solo'});state['claim_upgrade']=2
        self.assertEqual(claim_budget(state,1000,1000,1059)['limit'],5)
        self.assertEqual(claim_budget(state,1000,1000,1060)['limit'],5)
        self.assertEqual(claim_budget(state,1000,1000,1120)['limit'],15)
        self.assertEqual(claim_budget(state,1000,1000,1120)['solo_bonus'],10)
        state['characters'].append({'id':'worker'})
        self.assertEqual(claim_budget(state,1000,1000,1120)['limit'],5)
        self.assertEqual(claim_budget({},1000,1000,1120)['limit'],3)

    def test_spending_cannot_reset_when_roster_changes_or_bonus_runs_out(self):
        state=new_game({'name':'Solo'})
        mission=SimpleNamespace(analysis={},pool_slot=1000,spawned_at=1000,template_id='market_errand')
        for _ in range(13):spend_claim(state,mission,1120)
        with self.assertRaises(ValueError):spend_claim(state,mission,1120)
        state['characters'].append({'id':'worker'})
        self.assertEqual(claim_budget(state,1000,1000,1120)['remaining'],0)
        state['characters'].pop()
        self.assertEqual(claim_budget(state,1000,1000,1120)['remaining'],0)
        self.assertEqual(claim_budget(state,2000,2000,2120)['remaining'],13)

    def test_camp_hiring_cannot_create_a_worker_or_spend_gold(self):
        state=new_game({'name':'Solo'});state['resources']['gold']=100
        before=deepcopy(state['characters'])
        with self.assertRaisesRegex(ValueError,'missions'):camp_action(state,'hire',archetype='builder')
        self.assertEqual(state['characters'],before);self.assertEqual(state['resources']['gold'],100)

    def test_creation_rejects_unknown_and_limited_races(self):
        self.assertEqual(CharacterCreate(race='Goblin').race,'Goblin')
        for race in ('Invented race','Celestial'):
            with self.assertRaises(ValueError):CharacterCreate(race=race)
