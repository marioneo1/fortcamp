"""Routing indexes must preserve rules and stay out of stored battle state."""
import copy
import unittest
from unittest.mock import patch
from backend import combat
from backend.game import new_game


class RoutingLookupTests(unittest.TestCase):
    def fixture(self):
        battle = combat.create_contract_battle(new_game({"name": "QA"}), ["player"], "layout-0", "prison_former_e")
        return battle, battle["units"]["player"]

    def test_rotated_overlapping_footprints_and_ground_keep_original_order(self):
        battle = {"terrain": [
            {"x": 2, "y": 1, "footprint": [3, 1], "rotation": 90},
            {"x": 2, "y": 2, "destroyed": True},
        ], "ground_tiles": [
            {"x": 2, "y": 2, "material": "water"},
            {"x": 2, "y": 2, "material": "grass"},
        ], "ground_materials": {"water": {"movement_cost": 2}}}
        indexed = combat._routing_snapshot(battle)
        for y in range(5):
            for x in range(5):
                self.assertEqual(combat._terrain_at(indexed, x, y), combat._terrain_at(battle, x, y))
                self.assertEqual(combat._ground_at(indexed, x, y), combat._ground_at(battle, x, y))

    def test_paths_match_unindexed_search_after_door_and_footprint_changes(self):
        battle, actor = self.fixture()
        for change in ("initial", "opened", "destroyed", "relocated"):
            gate = next(t for t in battle["terrain"] if t["kind"] == "gate")
            if change == "opened":
                gate.update(state="opened", blocking=False)
            elif change == "destroyed":
                gate.update(destroyed=True)
            elif change == "relocated":
                gate.update(x=0, y=0, footprint=[2, 1], rotation=90)
            indexed_navigation = combat._navigation_tree(battle, actor)
            indexed_movement = combat._movement_tree(battle, actor)
            with patch.object(combat, "_routing_snapshot", side_effect=lambda b: b):
                self.assertEqual(indexed_navigation, combat._navigation_tree(battle, actor))
                self.assertEqual(indexed_movement, combat._movement_tree(battle, actor))
            self.assertFalse(any(k.startswith("_routing_") for k in battle))

    def test_movement_computes_each_terrain_footprint_once(self):
        battle, actor = self.fixture()
        with patch.object(combat, "occupied_tiles", wraps=combat.occupied_tiles) as footprints:
            combat._movement_tree(battle, actor)
        self.assertEqual(footprints.call_count, len(battle["terrain"]))

    def test_navigation_response_and_save_have_no_scratch_indexes(self):
        battle, _ = self.fixture()
        view = combat.apply_player_command(battle, {"action": "navigate", "x": 4, "y": 3})
        for value in (battle, view, copy.deepcopy(battle)):
            self.assertFalse(any(k.startswith("_routing_") for k in value))
