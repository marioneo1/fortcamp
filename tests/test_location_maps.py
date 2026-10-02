import unittest
from collections import deque
from copy import deepcopy

from backend.location_maps import MISSION_LOCATIONS, location_blueprint
from backend.battle_maps import compile_generated_battle_map, validate_battle_map, occupied_tiles
from backend.combat import create_contract_battle, _interact, _blocked, battle_view, _damage_terrain
from backend.game import new_game


class LocationMapTests(unittest.TestCase):
    def test_all_variants_have_clear_spawns_and_reachable_exits(self):
        for location in set(MISSION_LOCATIONS.values()):
            variants = set()
            for index in range(12):
                seed = f'layout-{index}'
                blueprint = location_blueprint(location,seed)
                self.assertEqual(blueprint,location_blueprint(location,seed))
                self.assertEqual(validate_battle_map(location,blueprint),[])
                variants.add(blueprint['map_variation'])
                blocked = {(v['x'],v['y']) for v in blueprint['void_tiles']}
                blocked |= {p for t in blueprint['terrain'] if t.get('blocking') for p in occupied_tiles(t)}
                spawns = [p for group in blueprint['spawn_zones'].values() for p in group]
                self.assertEqual(len({(p['x'],p['y']) for p in spawns}),len(spawns))
                self.assertTrue(all((p['x'],p['y']) not in blocked for p in spawns),location)
                # With gates opened, every spawn connects to its advertised exit.
                blocked -= {p for t in blueprint['terrain'] if t['kind']=='gate' for p in occupied_tiles(t)}
                exits = {(p['x'],p['y']) for p in blueprint['extraction']['tiles']+blueprint['enemy_extraction']['tiles']}
                for spawn in spawns:
                    seen={(spawn['x'],spawn['y'])};queue=deque(seen)
                    while queue:
                        x,y=queue.popleft()
                        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                            if 0<=p[0]<blueprint['width'] and 0<=p[1]<blueprint['height'] and p not in blocked|seen:
                                seen.add(p);queue.append(p)
                    self.assertTrue(seen&exits,(location,spawn))
            self.assertEqual(variants,{1,2},location)

    def test_river_is_continuous_and_bridge_is_walkable_floor(self):
        board=compile_generated_battle_map('location_broken_creek_bridge','bridge')
        materials={(t['x'],t['y']):t['material'] for t in board['ground_tiles']}
        water={(t['x'],t['y']) for t in board['void_tiles']}
        self.assertEqual({p for p,m in materials.items() if m=='deep_river'},water)
        self.assertEqual(len([m for m in materials.values() if m=='bridge_deck']),5)
        self.assertEqual(materials[(7,4)],'deep_river')
        self.assertEqual(materials[(7,5)],'bridge_deck')
        self.assertFalse(any(t.get('sprite')=='bridge' for t in board['terrain']))
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'bridge','timber_creek',True)
        self.assertTrue(_blocked(battle,7,4,'player'))
        self.assertFalse(_blocked(battle,7,4,'player','flying'))
        self.assertFalse(_blocked(battle,7,5,'player'))

    def test_enclosure_is_closed_except_door_and_shed_collapse(self):
        for location,prefix in [('tool_shed','shed'),('repair_yard','yard')]:
            board=location_blueprint(location,'enclosure')
            perimeter={(x,y) for x in range(7,13) for y in range(1,10) if x in (7,12) or y in (1,9)}
            covered={(t['x'],t['y']) for t in board['terrain'] if t['id'].startswith(prefix+'_wall') or t['kind']=='gate'}
            self.assertEqual(perimeter-covered,{(10,9)} if location=='tool_shed' else set())
            self.assertEqual(len([t for t in board['terrain'] if t['kind']=='gate']),1)

    def test_gate_opens_closes_refuses_occupied_closure_and_can_be_broken(self):
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'gate','tool_shed',True)
        player=battle['units']['player'];player.update(x=6,y=5)
        battle['turn_order']=['player',*[uid for uid in battle['turn_order'] if uid!='player']];battle['turn_index']=0
        gate=next(t for t in battle['terrain'] if t['kind']=='gate')
        self.assertTrue(_blocked(battle,7,5,'player'))
        self.assertTrue(any(a['command']['target_id']==gate['id'] for a in battle_view(battle)['context_actions']))
        _interact(battle,player,gate['id'])
        self.assertFalse(gate['blocking']);self.assertEqual(gate['sprite'],gate['open_sprite'])
        occupant=battle['units']['contract_enemy_0'];occupant.update(x=7,y=5)
        with self.assertRaisesRegex(ValueError,'standing'):_interact(battle,player,gate['id'])
        occupant.update(x=10,y=5)
        _interact(battle,player,gate['id']);self.assertTrue(gate['blocking'])
        player['attack']=100
        _damage_terrain(battle,player,gate['id'])
        self.assertTrue(gate['destroyed']);self.assertFalse(gate['blocking'])

    def test_active_saved_battle_does_not_regenerate_when_template_changes(self):
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'saved','tool_shed',True)
        before=deepcopy(battle['ground_tiles'])
        view=battle_view(battle)
        self.assertEqual(view['ground_tiles'],before)
        self.assertEqual(view['location_id'],'tool_shed')
