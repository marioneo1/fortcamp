import unittest

from backend.combat import create_contract_battle
from backend.game import new_game
from backend.location_maps import location_blueprint
from backend.battle_maps import occupied_tiles, validate_battle_map
from backend import battle_lab


class CommandLocationTests(unittest.TestCase):
    def test_named_variations_change_structure_and_have_no_overlapping_solids(self):
        for mid in ['prison_rival_d','prison_former_e','prison_former_c','goblin_chieftain','hobgoblin_vanguard']:
            presets=battle_lab.layout_presets('contract:'+mid)
            self.assertEqual(len(presets),4)
            structures=set()
            for preset in presets:
                state=new_game({'name':'Tester'})
                battle=create_contract_battle(state,['player'],preset['seed'],mid,True)
                self.assertEqual(battle['template_id'],preset['id'])
                solids=[p for t in battle['terrain'] if t.get('blocking') for p in occupied_tiles(t)]
                self.assertEqual(len(solids),len(set(solids)),(mid,preset['id']))
                structures.add(tuple(sorted((t['x'],t['y'],t['kind']) for t in battle['terrain']
                                             if t['kind'] in {'wall','palisade','gate','rubble'})))
            self.assertEqual(len(structures),4,mid)

    def test_chieftain_is_inside_the_second_defensive_layer(self):
        for preset in battle_lab.layout_presets('contract:goblin_chieftain'):
            battle=create_contract_battle(new_game({'name':'Tester'}),['player'],preset['seed'],'goblin_chieftain',True)
            boss=battle['units']['contract_enemy_0']
            command=next(t for t in battle['building_templates'] if t['id']=='command_house_1')
            x,y=command['anchor']
            self.assertTrue(x<boss['x']<x+4 and y<boss['y']<y+4)
            self.assertEqual(boss['adventurer_rank'], 'B')
            self.assertEqual(boss['rank_scaling']['method'], 'attributes_once')
            self.assertTrue(84 <= boss['hp'] <= 110)
            self.assertTrue(any(t['id'].startswith('inner_command_gate') for t in battle['terrain']))
            self.assertTrue(any(t['id'].startswith('outer_camp_gate') for t in battle['terrain']))

    def test_early_command_posts_are_smaller_and_keep_rank_budgets(self):
        state=new_game({'name':'Tester'})
        early=create_contract_battle(state,['player'],'size','prison_former_e',True)
        later=create_contract_battle(state,['player'],'size','prison_former_c',True)
        self.assertLess(early['width']*early['height'],later['width']*later['height'])
        self.assertEqual(sum(u['team']=='enemy' for u in early['units'].values()),2)
        self.assertTrue(any(t['sprite']=='structure:iron_wall' for t in
                            create_contract_battle(state,['player'],'size','hobgoblin_vanguard',True)['terrain']))

    def test_roadblock_has_actual_gates_and_an_intentional_alternative(self):
        for preset in battle_lab.layout_presets('contract:prison_rival_d'):
            board=location_blueprint('road_blockade',preset['seed'])
            self.assertEqual(validate_battle_map('blockade',board),[])
            gates=[t for t in board['terrain'] if t.get('name')=='Roadblock Gate']
            self.assertTrue(gates)
            self.assertTrue(all(g['state']=='closed' and g['open_sprite'] for g in gates))
            self.assertTrue(any(t['x']==gates[0]['x'] and t['y']==0 for t in board['terrain']))
            self.assertTrue(any(p['material']=='dirt' for p in board['paint']))
