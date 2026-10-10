import unittest
from copy import deepcopy
from types import SimpleNamespace
from backend.game import new_game
from backend.services import claim_budget, spend_claim
from backend.economy import camp_action
from backend.main import CharacterCreate

class SoloOnboardingTests(unittest.TestCase):
    def test_mission_refresh_is_five_minutes_only_in_development(self):
        from backend.settings import Settings
        from backend.services import POOL_SECONDS, pool_slot, settings
        for profile in ('dev', 'dev-discord'):
            self.assertEqual(Settings(environment=profile).mission_pool_seconds, 300)
        for profile in ('release', 'prod', 'production', 'stable', 'standalone'):
            self.assertEqual(Settings(environment=profile).mission_pool_seconds, 1800)
        self.assertEqual(POOL_SECONDS, settings.mission_pool_seconds)
        self.assertEqual(pool_slot(POOL_SECONDS * 10 + POOL_SECONDS - 1), POOL_SECONDS * 10)
        self.assertEqual(pool_slot(POOL_SECONDS * 11), POOL_SECONDS * 11)

    def test_starter_api_defaults_to_a_job_and_rejects_retired_medic(self):
        self.assertEqual(CharacterCreate().starting_role,'fighter')
        for job in ('captor','summoner','cleric','rogue'):
            self.assertEqual(CharacterCreate(starting_role=job).starting_role,job)
        with self.assertRaises(ValueError):CharacterCreate(starting_role='medic')

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

    def test_creation_allows_only_starting_races_without_removing_discovery_content(self):
        from backend.game import public_content
        from backend.races import RACE_CATALOG, STARTING_RACES
        content = public_content()['races']
        self.assertEqual(len(STARTING_RACES), 14)
        self.assertEqual(set(content), set(RACE_CATALOG))
        self.assertEqual({race for race, profile in content.items() if profile['starting_selectable']}, STARTING_RACES)
        for race in STARTING_RACES:
            self.assertEqual(CharacterCreate(race=race).race, race)
        for race in (set(RACE_CATALOG) - STARTING_RACES) | {'Invented race'}:
            with self.assertRaises(ValueError):CharacterCreate(race=race)
