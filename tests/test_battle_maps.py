import unittest

from backend.battle_maps import BATTLE_MAPS, compile_battle_map, compile_generated_battle_map, occupied_tiles, validate_battle_map
from backend.combat import _blocked, _distance_to_entity, _step_cost, apply_player_command, create_captive_cart_battle, create_frontier_watch_defense_battle, create_goblin_warcamp_battle, create_smoke_signals_battle
from backend.game import new_game


class BattleMapAuthoringTests(unittest.TestCase):
    def test_all_authored_maps_compile_to_complete_ground_grids(self):
        for map_id, source in BATTLE_MAPS.items():
            self.assertEqual(validate_battle_map(map_id), [])
            compiled = compile_battle_map(map_id)
            self.assertEqual(len(compiled["ground_tiles"]), source["width"] * source["height"])

    def test_validator_reports_out_of_bounds_paint_and_unknown_material(self):
        invalid = {
            "width": 2, "height": 2, "default_ground": "grass",
            "paint": [{"material": "lava_cheese", "tiles": [[3, 0]]}],
        }
        problems = validate_battle_map("invalid", invalid)
        self.assertTrue(any("unknown material" in problem for problem in problems))
        self.assertTrue(any("outside" in problem for problem in problems))

    def test_validator_checks_every_cell_of_a_large_structure(self):
        invalid = {
            "width": 3, "height": 3, "default_ground": "grass", "paint": [],
            "terrain": [{"id": "large_tent", "x": 2, "y": 2, "footprint": [2, 2]}],
        }
        problems = validate_battle_map("large-structure", invalid)
        self.assertTrue(any("large_tent" in problem and "outside" in problem for problem in problems))

    def test_rotation_swaps_rectangular_footprint(self):
        self.assertEqual(occupied_tiles({"x": 3, "y": 4, "footprint": [2, 1], "rotation": 90}), [(3, 4), (3, 5)])

    def test_encounters_use_named_map_blueprints(self):
        state = new_game({"name": "Mapper", "attributes": {"str": 8, "vit": 8}})
        party_ids = [state["characters"][0]["id"]]
        warcamp = create_goblin_warcamp_battle(state, party_ids, "map-a")
        cart = create_captive_cart_battle(state, party_ids, "map-b")
        self.assertEqual(warcamp["map_id"], "goblin_warcamp")
        self.assertEqual(cart["map_id"], "captive_cart_road")
        self.assertEqual(cart["theme"], "warhost-road")

    def test_painted_ground_drives_movement_cost(self):
        state = new_game({"name": "Mapper", "attributes": {"str": 8, "vit": 8}})
        party_id = state["characters"][0]["id"]
        battle = create_captive_cart_battle(state, [party_id], "map-cost")
        unit = battle["units"][party_id]
        self.assertEqual(_step_cost(battle, 3, 3, 4, 3, unit), 2)
        self.assertEqual(_step_cost(battle, 1, 3, 2, 3, unit), 1)

    def test_large_cage_reserves_its_full_footprint(self):
        state = new_game({"name": "Mapper", "attributes": {"str": 8, "vit": 8}})
        battle = create_goblin_warcamp_battle(state, [state["characters"][0]["id"]], "map-large-props")
        self.assertTrue(_blocked(battle, 6, 6))
        self.assertEqual(_distance_to_entity({"x": 4, "y": 6}, battle["objects"]["prisoner_pen"]), 1)

    def test_generated_scenario_is_stable_and_keeps_a_clear_route(self):
        first = compile_generated_battle_map("hedgerow_signal_site", "mission-17")
        repeated = compile_generated_battle_map("hedgerow_signal_site", "mission-17")
        other = compile_generated_battle_map("hedgerow_signal_site", "mission-18")
        self.assertEqual(first, repeated)
        self.assertNotEqual(first["decorations"], other["decorations"])
        self.assertTrue(any(tile["material"] == "dirt" for tile in first["ground_tiles"]))
        self.assertTrue(any(tile["x"] == 0 for tile in first["extraction"]["tiles"]))

    def test_investigation_encounter_uses_generated_scenario(self):
        state = new_game({"name": "Investigator", "attributes": {"str": 8, "vit": 8}})
        battle = create_smoke_signals_battle(state, [state["characters"][0]["id"]], "signal-map")
        self.assertEqual(battle["scenario_id"], "hedgerow_signal_site")
        self.assertTrue(battle["map_id"].startswith("generated:hedgerow_signal_site:"))
        self.assertEqual(battle["objectives"][0]["id"], "signal_captain")

    def test_defense_scenario_is_repeatable_and_exposes_authored_zones(self):
        first = compile_generated_battle_map("frontier_watch_defense", "watch-17")
        repeated = compile_generated_battle_map("frontier_watch_defense", "watch-17")
        self.assertEqual(first, repeated)
        self.assertEqual((first["width"], first["height"]), (14, 10))
        self.assertTrue(first["preparation_zone"])
        self.assertTrue(first["deployment_zone"])
        self.assertTrue(all(tile["x"] < 5 for tile in first["deployment_zone"]))

    def test_defense_preparation_spends_and_refunds_budget_before_initiative(self):
        state = new_game({"name": "Defender", "race": "Kobold", "traits": ["engineer"], "attributes": {"str": 7, "vit": 7}})
        battle = create_frontier_watch_defense_battle(state, ["player"], "watch-prep")
        self.assertEqual(battle["status"], "preparing")
        self.assertIn("snare_trap", {entry["id"] for entry in battle["preparation"]["available"]})
        self.assertIn("watch_platform", {entry["id"] for entry in battle["preparation"]["available"]})
        starting_budget = battle["preparation"]["remaining"]
        destination = battle["preparation"]["zone"][0]
        apply_player_command(battle, {"action": "place_defense", "placement_id": "spike_trap", **destination})
        placement = battle["preparation"]["placements"][0]
        self.assertEqual(battle["preparation"]["remaining"], starting_budget - 1)
        apply_player_command(battle, {"action": "remove_defense", "target_id": placement["id"]})
        self.assertEqual(battle["preparation"]["remaining"], starting_budget)
        view = apply_player_command(battle, {"action": "start_battle"})
        self.assertEqual(view["status"], "active")
        self.assertIsNotNone(view["current_unit_id"])


if __name__ == "__main__":
    unittest.main()
