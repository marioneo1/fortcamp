import json
import unittest
from copy import deepcopy
from pathlib import Path

from backend.battle_maps import occupied_tiles
from backend.combat import create_captive_cart_battle, battle_view, _blocked
from backend.game import new_game
from backend.location_maps import prop,location_blueprint
from backend.prop_sizes import PROP_SIZES

ROOT=Path(__file__).resolve().parents[1]

class PropSizeTests(unittest.TestCase):
    def test_new_cart_blocks_its_whole_footprint_with_courier_outside(self):
        battle=create_captive_cart_battle(new_game({'name':'Tester'}),['player'],'size',True)
        cart=next(t for t in battle['terrain'] if t['id']=='cart_body')
        self.assertEqual(cart['footprint'],[2,2])
        self.assertTrue(all(_blocked(battle,x,y) for x,y in occupied_tiles(cart)))
        courier=battle['units']['captive_courier']
        self.assertNotIn((courier['x'],courier['y']),occupied_tiles(cart))

    def test_old_saved_cart_occupancy_is_not_rewritten(self):
        battle=create_captive_cart_battle(new_game({'name':'Tester'}),['player'],'save',True)
        cart=next(t for t in battle['terrain'] if t['id']=='cart_body')
        cart['footprint']=[1,1];before=deepcopy(cart)
        battle_view(battle)
        self.assertEqual(cart['footprint'],before['footprint'])

    def test_defaults_distinguish_large_furniture_and_small_items(self):
        self.assertEqual(prop('well','Well','village_well',2,2)['footprint'],[2,2])
        self.assertEqual(prop('cart','Cart','wooden_handcart',2,2,False)['footprint'],[2,1])
        self.assertEqual(prop('bag','Bag','dropped_coin_purse',2,2,False)['footprint'],[1,1])
        self.assertLess(PROP_SIZES['dropped_coin_purse']['fill'],PROP_SIZES['village_well']['fill'])
        self.assertEqual(PROP_SIZES,json.loads((ROOT/'frontend/src/map-prop-sizes.json').read_text()))

    def test_garden_has_multi_cell_beds_without_blocking_cross_aisles(self):
        variants={}
        for i in range(40):
            board=location_blueprint('herb_garden',f'layout-{i}')
            variants[board['map_variation']]=board
        for board in variants.values():
            beds=[t for t in board['terrain'] if t.get('size_variant')=='raised-bed']
            self.assertGreaterEqual(len(beds),3)
            self.assertTrue(all(t['footprint']==[2,2] for t in beds))
            self.assertFalse(any(y==5 or x in (8,9) for t in beds for x,y in occupied_tiles(t)))
            self.assertTrue(any(t['sprite']=='garden_potting_bench' for t in board['terrain']))

if __name__=='__main__':unittest.main()
