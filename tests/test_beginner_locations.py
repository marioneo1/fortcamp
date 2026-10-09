import unittest
from collections import deque
from copy import deepcopy

from backend import battle_lab
from backend.battle_maps import occupied_tiles, validate_battle_map
from backend.combat import create_contract_battle, _can_step
from backend.game import new_game
from backend.location_maps import location_blueprint, MISSION_LOCATIONS


class BeginnerLocationTests(unittest.TestCase):
    def test_activity_variations_keep_art_separate_from_collision(self):
        for location in ['herb_garden','occupied_training_yard']:
            variants={}
            for index in range(40):
                board=location_blueprint(location,f'layout-{index}')
                variants[board['map_variation']]=board
            self.assertEqual(len(variants),4)
            for variant,board in variants.items():
                self.assertTrue(board.get('ground_art'))
                self.assertEqual(len(board['activity_areas']),4)
                for tile in board['ground_art']:
                    self.assertTrue(0<=tile['x']<board['width'] and 0<=tile['y']<board['height'])
                    self.assertNotIn('blocking',tile)
                furniture=[p for p in board['terrain']+board['decorations'] if p['id'].startswith(location+'_')]
                self.assertTrue(any(p.get('art_offset') and any(p['art_offset']) for p in furniture))
                if location=='herb_garden':
                    edges=[p for p in board['decorations'] if p.get('ground_edging')]
                    self.assertTrue(edges)
                    self.assertEqual(len({p['id'] for p in edges}),len(edges))
                    walking={**deepcopy(board),'units':{}}
                    # Crossing a low edging rail leaves ordinary crop ground
                    # walkable; the fence never becomes a full-cell obstacle.
                    if variant==1:
                        self.assertTrue(_can_step(walking,7,4,7,5,{'id':'walker'}))
                        self.assertTrue(_can_step(walking,9,5,8,5,{'id':'walker'}))

    def test_current_dressing_keeps_every_spawn_connected_to_an_exit(self):
        locations={'provision_store','farm_clearing','herb_garden','purse_road','well_yard',
                   'supply_stop','occupied_training_yard','command_camp','timber_redoubt','vanguard_camp'}
        for location in locations:
            for index in range(40):
                board=location_blueprint(location,f'layout-{index}')
                walking={**deepcopy(board),'units':{}}
                for obj in walking['terrain']:
                    if obj['kind']=='gate':obj['blocking']=False
                reached={(p['x'],p['y']) for p in board['extraction']['tiles']+board['enemy_extraction']['tiles']}
                queue=deque(reached)
                # Reverse reachability checks every spawn in one traversal;
                # these authored sites have no directional elevation changes.
                while queue:
                    x,y=queue.popleft()
                    for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                        if (nx,ny) not in reached and _can_step(walking,nx,ny,x,y,{'id':'walker'}):
                            # _can_step tests the destination; the reverse source
                            # must also be walkable to avoid expanding walls.
                            if not _can_step(walking,x,y,nx,ny,{'id':'walker'}):continue
                            reached.add((nx,ny));queue.append((nx,ny))
                for zone in board['spawn_zones'].values():
                    self.assertTrue(all((p['x'],p['y']) in reached for p in zone),(location,index))

    def test_locations_have_matching_landmarks_and_four_distinct_layouts(self):
        cases=[('rats_storehouse','grain_sacks'),('wolves_fence','water_trough'),
               ('herbs_wall','herb_planter'),('goblin_pickpockets','dropped_coin_purse'),
               ('ruined_well','village_well'),('supply_watch','wooden_handcart'),
               ('prison_proof_d','straw_training_dummy')]
        for mid,landmark in cases:
            presets=battle_lab.layout_presets('contract:'+mid)
            self.assertEqual(len(presets),4)
            signatures=set()
            for preset in presets:
                board=location_blueprint(MISSION_LOCATIONS[mid],preset['seed'])
                self.assertEqual(validate_battle_map(mid,board),[])
                self.assertTrue(any(obj['sprite']==landmark for obj in board['terrain']+board['decorations']),mid)
                if mid in {'wolves_fence','herbs_wall','prison_proof_d'}:
                    self.assertFalse(any(p['material']=='shed_floor' for p in board['paint']))
                cells=[p for obj in board['terrain'] for p in occupied_tiles(obj)]
                self.assertEqual(len(cells),len(set(cells)),(mid,preset['id']))
                signatures.add(str((board['paint'],[(t['x'],t['y'],t['sprite']) for t in board['terrain']])))
            self.assertEqual(len(signatures),4,mid)

    def test_early_encounters_use_authored_counts(self):
        for mid in ['rats_storehouse','wolves_fence','goblin_pickpockets','ruined_well','supply_watch','prison_proof_e']:
            for preset in battle_lab.layout_presets('contract:'+mid):
                battle=create_contract_battle(new_game({'name':'Tester'}),['player'],preset['seed'],mid,True)
                counts={'rats_storehouse':[3,4,2,4],'wolves_fence':[3,2,4,3],'supply_watch':[2,3,2,3]}
                expected=counts[mid][battle['map_variation']-1] if mid in counts else 2
                self.assertEqual(sum(u['team']=='enemy' for u in battle['units'].values()),expected,mid)
                self.assertEqual(battle['encounter_id'],'contract:'+mid)

    def test_camps_have_activity_areas_without_blocking_deployment(self):
        for mid in ['prison_former_c','goblin_chieftain','hobgoblin_vanguard']:
            for preset in battle_lab.layout_presets('contract:'+mid):
                board=location_blueprint(MISSION_LOCATIONS[mid],preset['seed'])
                sprites={p['sprite'] for p in board['terrain']+board['decorations']}
                self.assertTrue({'archery_target','straw_training_dummy','grain_sacks','camp_cooking_pot'}<=sprites)
                self.assertTrue(sprites & {'tribal_hide_bed','canvas_cot','straw_bed','sleeping_bag'})
                reserved={(p['x'],p['y']) for zone in board['spawn_zones'].values() for p in zone}
                camp=[p for p in board['terrain'] if p['id'].startswith('camp_')]
                self.assertFalse(reserved & {c for obj in camp for c in occupied_tiles(obj)})
                if mid=='hobgoblin_vanguard':
                    self.assertIn('ballista_loaded',sprites)


if __name__ == '__main__':
    unittest.main()
