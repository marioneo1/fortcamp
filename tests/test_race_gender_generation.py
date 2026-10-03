import random
import unittest

from backend.game import _make_procedural, new_game
from backend.combat import create_contract_battle
from backend.races import generated_genders


class RaceGenderGenerationTests(unittest.TestCase):
    def test_female_only_recruits_always_have_matching_portrait_pool(self):
        for race in ("banshee", "dryad"):
            for seed in range(40):
                character = _make_procedural(race, random.Random(seed))
                self.assertEqual(character["gender"], "female")
                self.assertIn("_female", character["portrait_pool"])

    def test_female_only_combat_enemies_use_matching_identity(self):
        for race in ("Banshee", "Dryad"):
            for seed in range(4):
                state = new_game({"name": "Tester"})
                battle = create_contract_battle(state, ["player"], str(seed), "prison_rival_e", race_override=race)
                enemies = [unit for unit in battle["units"].values() if unit.get("race") == race]
                self.assertTrue(enemies)
                for enemy in enemies:
                    self.assertEqual(enemy["gender"], "female")
                    self.assertIn("_female", enemy["portrait_pool"])

    def test_other_races_retain_both_genders_and_profile_restrictions(self):
        genders = {_make_procedural("foxkin", random.Random(seed))["gender"] for seed in range(40)}
        self.assertEqual(genders, {"male", "female"})
        self.assertEqual(generated_genders("Human", {"genders": ["male"]}), ("male",))
        self.assertEqual(generated_genders("dryad", {"genders": ["male"]}), ("female",))
