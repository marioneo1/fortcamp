import unittest
from collections import deque

from backend.battle_lab import layout_presets
from backend.battle_maps import compile_generated_battle_map, occupied_tiles, validate_battle_map
from backend.combat import _can_step, create_contract_battle
from backend.game import new_game
from backend.location_maps import location_blueprint


class HighwayLocationTests(unittest.TestCase):
    def test_four_repeatable_layouts_preserve_landmarks_and_clear_spawns(self):
        presets = layout_presets('contract:highway_ambush')
        self.assertEqual(len(presets), 4)
        signatures = set()
        for preset in presets:
            board = location_blueprint('highway_cut', preset['seed'])
            self.assertEqual(board, location_blueprint('highway_cut', preset['seed']))
            self.assertEqual(validate_battle_map('highway_cut', board), [])
            cells = [cell for obj in board['terrain'] for cell in occupied_tiles(obj)]
            self.assertEqual(len(cells), len(set(cells)))
            starts = {(p['x'],p['y']) for zone in board['spawn_zones'].values() for p in zone}
            self.assertFalse(starts & set(cells))
            sprites = {obj['sprite'] for obj in board['terrain']+board['decorations']}
            self.assertTrue({'wooden_handcart','grain_sacks','bound_barrels'} <= sprites)
            self.assertTrue(board['elevation'])
            self.assertTrue(all(p['height']==1 for p in board['elevation']))
            signatures.add(str(board['paint']))
        self.assertEqual(len(signatures), 4)

    def test_every_spawn_reaches_both_road_ends_without_destroying_cover(self):
        for index in range(40):
            board = compile_generated_battle_map('location_highway_cut', f'layout-{index}')
            board['units'] = {}
            starts = [p for zone in board['spawn_zones'].values() for p in zone]
            for exit_group in ('extraction','enemy_extraction'):
                reached = {(p['x'],p['y']) for p in board[exit_group]['tiles']}
                queue = deque(reached)
                while queue:
                    x,y = queue.popleft()
                    for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                        if (nx,ny) in reached: continue
                        if _can_step(board,x,y,nx,ny,{'id':'walker'}):
                            reached.add((nx,ny)); queue.append((nx,ny))
                self.assertTrue(all((p['x'],p['y']) in reached for p in starts), (index,exit_group))
                # Both shoulder approaches stay open; breaking vegetation is optional.
                for x in (3,13):
                    self.assertIn((x,2 if board['map_variation'] in (1,2) else 8),reached)

    def test_new_battles_keep_the_existing_d_rank_enemy_budget(self):
        parties = []
        for preset in layout_presets('contract:highway_ambush'):
            battle = create_contract_battle(new_game({'name':'Tester'}), ['player'],
                                            preset['seed'], 'highway_ambush', True)
            enemies = [u for u in battle['units'].values() if u['team']=='enemy']
            self.assertEqual(len(enemies), 3)
            self.assertEqual(battle['encounter_id'], 'contract:highway_ambush')
            self.assertEqual(battle['location_id'], 'highway_cut')
            parties.append([(u['max_hp'],u['attack'],u['armor']) for u in enemies])
        self.assertTrue(all(p==parties[0] for p in parties))


if __name__ == '__main__':
    unittest.main()
