import unittest
from unittest.mock import patch
from backend.combat import (_blocked, _can_step, _can_attack, _line_of_sight,
                            _route_with_gates, _auto_open_gate, _interact, _damage_terrain)
from backend.location_maps import place_building


class WallBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.actor={'id':'actor','x':2,'y':2,'move':4,'attack_range':1,'attack':100,
                    'team':'enemy','name':'Walker','conscious':True,'hp':20}
        self.wall={'id':'edge','x':2,'y':2,'edge_wall':True,'wall_edges':['north'],
                   'blocking':True,'blocks_sight':True,'kind':'wall','name':'Wall',
                   'destructible':True,'hp':10,'max_hp':10,'armor':0}
        self.battle={'width':5,'height':5,'terrain':[self.wall],'units':{'actor':self.actor},
                     'log':[],'objects':{},'elevation':[]}

    def test_inside_tile_is_walkable_but_both_crossing_directions_are_blocked(self):
        self.assertFalse(_blocked(self.battle,2,2,'actor'))
        self.assertTrue(_can_step(self.battle,2,3,2,2,self.actor))
        self.assertTrue(_can_step(self.battle,2,2,3,2,self.actor))
        self.assertFalse(_can_step(self.battle,2,2,2,1,self.actor))
        self.assertFalse(_can_step(self.battle,2,1,2,2,self.actor))
        self.wall['edge_wall']=False
        self.assertTrue(_blocked(self.battle,2,2,'actor'))

    def test_corner_blocks_two_edges_and_does_not_stop_inside_movement(self):
        self.wall['wall_edges']=['north','west']
        self.assertTrue(_can_step(self.battle,3,2,2,2,self.actor))
        self.assertFalse(_can_step(self.battle,1,2,2,2,self.actor))
        self.assertFalse(_line_of_sight(self.battle,self.actor,{'x':1,'y':1}))
        self.assertTrue(_line_of_sight(self.battle,self.actor,{'x':3,'y':3}))

    def test_melee_ranged_and_magic_line_of_effect_respect_boundary_at_endpoints(self):
        outside={'id':'victim','x':2,'y':1}
        self.assertFalse(_can_attack(self.battle,self.actor,outside,1))
        self.assertFalse(_can_attack(self.battle,outside,self.actor,5))
        self.assertFalse(_line_of_sight(self.battle,outside,self.actor))
        self.wall.pop('blocks_sight') # movement-blocking walls also default to blocking sight
        self.assertFalse(_line_of_sight(self.battle,outside,self.actor))
        # The wall itself can be struck from either side, including its floor tile.
        self.assertTrue(_can_attack(self.battle,outside,self.wall,1))
        self.assertTrue(_can_attack(self.battle,self.actor,self.wall,1))
        self.wall['destroyed']=True
        self.assertTrue(_can_attack(self.battle,self.actor,outside,1))
        self.assertTrue(_can_step(self.battle,2,2,2,1,self.actor))

    def test_gate_can_be_used_from_inside_and_ai_opens_before_crossing(self):
        self.wall.update(kind='gate',state='closed',closed_sprite='closed',open_sprite='open')
        # Box the actor in so opening the north gate is the only possible route.
        self.battle['terrain'] += [dict(self.wall,id=side,kind='wall',wall_edges=[side])
                                  for side in ['east','south','west']]
        target={'id':'victim','x':2,'y':0,'team':'player','hp':20,'conscious':True}
        self.battle['units']['victim']=target
        path,_,gates=_route_with_gates(self.battle,self.actor,{(2,1)})
        self.assertEqual(path,[(2,1)]);self.assertEqual(gates[(2,1)]['id'],'edge')
        with patch('backend.combat._finish_turn'):
            self.assertTrue(_auto_open_gate(self.battle,self.actor,target))
            self.assertTrue(_can_step(self.battle,2,2,2,1,self.actor))
            self.actor['ability_activation']=self.actor.get('ability_activation',0)+1
            _interact(self.battle,self.actor,'edge')
        self.assertEqual(self.wall['state'],'closed') # an interior occupant does not jam it
        self.assertFalse(_can_step(self.battle,2,2,2,1,self.actor))
        _damage_terrain(self.battle,self.actor,'edge')
        self.assertTrue(_can_step(self.battle,2,2,2,1,self.actor))

    def test_divider_has_real_t_joins_and_rotated_edges(self):
        for rotation,top,bottom in [(0,'north','south'),(90,'east','west'),(180,'south','north'),(270,'west','east')]:
            board=place_building('tool_divided_store',(3,3),'test',rotation)
            joins=[t for t in board['terrain'] if t['sprite'].endswith('_edge_junction')]
            self.assertEqual(len(joins),2)
            self.assertEqual({e for t in joins for e in t['wall_edges']},{top,bottom})
            self.assertTrue(all(t['blocking'] and not t['edge_wall'] for t in joins))
            corners=[t for t in board['terrain'] if t['sprite'].endswith('_corner')]
            self.assertTrue(all(t['edge_wall'] and len(t['wall_edges'])==2 for t in corners))
