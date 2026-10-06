import unittest
from unittest.mock import patch
from tests import test_combat_approach as fixtures
from backend.combat import apply_player_command, battle_view

class PlayerNavigationTests(unittest.TestCase):
    def fixture(self,position=(1,3),move=10):
        f=fixtures.AttackApproachTests();f.setUp();b=f.battle;a=f.actor
        a.update(x=position[0],y=position[1],move=move)
        for u in b['units'].values():
            if u['id']!=a['id']:u.update(x=7,y=7)
        b['terrain']=[{'id':f'wall{y}','name':'Wall','kind':'wall','x':3,'y':y,'blocking':True,'destructible':True,'hp':30,'max_hp':30} for y in range(b['height']) if y not in (2,4)]
        b['terrain'].append({'id':'door','name':'Workshop Door','kind':'gate','x':3,'y':2,'blocking':True,'destructible':True,'hp':30,'max_hp':30,'state':'closed','closed_sprite':'closed','open_sprite':'open','sprite':'closed'})
        return b,a
    def navigate(self,b,x,y):
        with patch('backend.combat._advance_to_player'):
            return apply_player_command(b,{'action':'navigate','x':x,'y':y})
    def test_equal_distance_prefers_open_entrance_without_opening_door(self):
        b,a=self.fixture();view=self.navigate(b,5,3)
        self.assertEqual((a['x'],a['y']),(5,3))
        self.assertEqual(b['terrain'][-1]['state'],'closed')
        self.assertNotIn('navigation_prompt',view)
        self.assertTrue(any(p['x']==3 and p['y']==4 for p in a['movement_path']))
    def test_closed_shortcut_is_offered_even_when_a_longer_open_route_is_in_range(self):
        b,a=self.fixture((1,2));view=battle_view(b)
        self.assertIn({'x':5,'y':2},view['reachable'])
        self.assertEqual(view['navigation_doors'].get('5,2'),'door')
        view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2))

    def test_nearer_closed_door_stops_beside_it_and_prompts_explicit_open(self):
        b,a=self.fixture((1,2));view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2));self.assertFalse(a.get('acted',False))
        self.assertEqual(view['navigation_prompt']['command'],{'action':'interact','target_id':'door'})
        self.assertEqual(b['terrain'][-1]['state'],'closed')
        with patch('backend.combat._advance_to_player'):
            opened=apply_player_command(b,view['navigation_prompt']['command'])
        self.assertEqual(b['terrain'][-1]['state'],'opened')
        self.assertNotIn('navigation_prompt',opened)
    def test_insufficient_movement_advances_toward_nearest_door_within_start_budget(self):
        b,a=self.fixture((0,2),1);view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(1,2));self.assertNotIn('navigation_prompt',view)
        self.assertEqual(a['movement_origin'],{'x':0,'y':2})
    def test_sealed_building_does_not_route_through_wall(self):
        b,a=self.fixture();b['terrain'].extend({'id':f'fill{y}','name':'Wall','kind':'wall','x':3,'y':y,'blocking':True} for y in (2,4));b['terrain']=[t for t in b['terrain'] if t['kind']!='gate']
        with self.assertRaises(ValueError):self.navigate(b,5,3)
        self.assertEqual((a['x'],a['y']),(1,3))

    def test_edge_mounted_door_stops_on_its_approach_side(self):
        b,a=self.fixture((1,2));b['terrain']=[t for t in b['terrain'] if t['kind']!='gate']
        door={'id':'edge-door','name':'Door','kind':'gate','x':2,'y':2,'edge_wall':True,'wall_edges':['east'],'blocking':True,'state':'closed','hp':30,'max_hp':30,'destructible':True,'closed_sprite':'closed','open_sprite':'open'}
        b['terrain'].append(door)
        # Seal the other entrance; the sole passage crosses this east boundary.
        b['terrain'].extend({'id':f'seal{y}','kind':'wall','x':3,'y':y,'blocking':True} for y in (4,))
        view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2))
        self.assertEqual(view['navigation_prompt']['command']['target_id'],'edge-door')

    def test_npc_in_closed_door_does_not_hide_the_open_option_or_allow_overlap(self):
        b,a=self.fixture((1,2));npc=next(u for u in b['units'].values() if u['id']!=a['id']);npc.update(x=3,y=2,conscious=True)
        view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2))
        self.assertEqual(view['navigation_prompt']['command']['target_id'],'door')
        self.assertEqual((npc['x'],npc['y']),(3,2))
        for _ in range(25):view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2));self.assertEqual(b['terrain'][-1]['state'],'closed')
