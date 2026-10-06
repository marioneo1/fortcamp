import unittest
from unittest.mock import patch
from backend.combat import _door_controls, _interact
from backend.wall_boundaries import gate_controls, can_operate_gate


class DoorControlTests(unittest.TestCase):
    def fixture(self, edge=True):
        gate = {'id': 'door', 'name': 'Post Door', 'kind': 'gate', 'x': 3, 'y': 3,
                'state': 'closed', 'blocking': True, 'closed_sprite': 'closed', 'open_sprite': 'opened'}
        if edge:
            gate.update(edge_wall=True, wall_edges=['north'])
        actor = {'id': 'hero', 'name': 'Hero', 'team': 'player', 'x': 3, 'y': 3,
                 'conscious': True, 'acted': False}
        return {'width': 8, 'height': 8, 'status': 'active', 'terrain': [gate],
                'units': {'hero': actor}, 'log': []}, actor, gate

    def test_each_edge_orientation_has_two_controls_at_actual_boundary(self):
        battle, actor, gate = self.fixture()
        for side, delta in {'north': (0,-1), 'east': (1,0), 'south': (0,1), 'west': (-1,0)}.items():
            gate['wall_edges'] = [side]
            controls = gate_controls(gate)
            self.assertEqual(len(controls), 2)
            self.assertEqual(controls[0]['approach'], {'x': 3, 'y': 3})
            self.assertEqual(controls[1]['approach'], {'x': 3+delta[0], 'y': 3+delta[1]})
            for control in controls:
                self.assertTrue(can_operate_gate(control['approach'], gate))
                self.assertLess(abs(control['x']-(3+delta[0]*.5)), .5)
                self.assertLess(abs(control['y']-(3+delta[1]*.5)), .5)

    def test_open_and_close_from_inside_or_outside_without_crossing(self):
        for position in ((3,3), (3,2)):
            battle, actor, gate = self.fixture()
            actor.update(x=position[0], y=position[1])
            for operation in ('Open', 'Close'):
                controls = _door_controls(battle, actor)
                self.assertEqual([c['operation'] for c in controls], [operation]*2)
                self.assertTrue(all(c['command']=={'action':'interact','target_id':'door'} for c in controls))
                with patch('backend.combat._finish_turn'):
                    _interact(battle, actor, 'door')
                self.assertEqual((actor['x'],actor['y']), position)
                actor['acted'] = False
            self.assertEqual(gate['state'], 'closed')

    def test_far_controls_approach_selected_side_and_never_auto_operate(self):
        battle, actor, gate = self.fixture()
        actor.update(x=1,y=1)
        controls = _door_controls(battle, actor)
        self.assertEqual([c['command'] for c in controls], [
            {'action':'navigate','x':3,'y':3}, {'action':'navigate','x':3,'y':2}])
        self.assertEqual(gate['state'],'closed')

    def test_centered_rotated_footprints_use_outside_approach_cells(self):
        battle, actor, gate = self.fixture(False)
        gate.update(footprint=[2,1],rotation=90)
        controls = gate_controls(gate)
        self.assertEqual([c['approach'] for c in controls], [{'x':2,'y':3},{'x':4,'y':3}])
        gate['state']='opened'
        actor.update(x=2,y=3)
        controls = _door_controls(battle,actor)
        self.assertTrue(all(c['command']['action']=='interact' for c in controls))

    def test_occupied_centered_gate_explains_why_it_cannot_close(self):
        battle, actor, gate = self.fixture(False)
        gate['state']='opened'
        controls = _door_controls(battle,actor)
        self.assertTrue(all(c['disabled'] for c in controls))
        self.assertIn('standing',controls[0]['help'])
        with self.assertRaises(ValueError):
            _interact(battle, {'x':2,'y':3}, 'door')

    def test_turn_locks_destroyed_gates_and_map_edges(self):
        battle, actor, gate = self.fixture()
        for unit in (None, {**actor,'team':'enemy'}, {**actor,'acted':True}):
            self.assertTrue(all(c['disabled'] for c in _door_controls(battle,unit)))
        gate.update(y=0)
        self.assertEqual(len(_door_controls(battle,actor)),1)
        gate['destroyed']=True
        self.assertEqual(_door_controls(battle,actor),[])
