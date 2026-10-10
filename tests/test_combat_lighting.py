import json
import unittest
from backend import combat_lighting as lighting
from unittest.mock import patch


class CombatLightingTests(unittest.TestCase):
    def test_roofed_rooms_exclude_open_yard_and_rotation_moves_coverage(self):
        battle={'building_templates':[{'id':'tool_twin_sheds','anchor':[3,2]}]}
        cells=lighting.indoor_cells(battle)
        self.assertIn([3,2],cells)
        self.assertNotIn([7,2],cells)  # loading court between the two sheds
        self.assertNotIn([3,9],cells)  # delivery yard below the sheds
        self.assertEqual(lighting.indoor_cells({'building_templates':[{'id':'workshop_forge_yard','anchor':[0,0]}]}),[])
        rotated=lighting.indoor_cells({'building_templates':[{'id':'tool_twin_sheds','anchor':[3,2],'rotation':90}]})
        self.assertIn([11,2],rotated)
        self.assertNotEqual(cells,rotated)

    def test_arrival_survives_save_reopen_and_time_advances(self):
        battle={}
        lighting.initialize(battle,now=720)
        saved=json.loads(json.dumps(battle))
        view=lighting.presentation(saved,now=1020)
        self.assertEqual(view['arrival_minute'],12)
        self.assertEqual(view['arrived_at'],720)
        self.assertEqual(view['phase'],'day')
        self.assertEqual(view['server_now'],1020)
        self.assertNotIn('server_now',saved['lighting'])
        self.assertEqual(saved,battle)

    def test_authored_phase_override_and_old_battle_migration(self):
        battle={'lighting_phase':'night'}
        lighting.initialize(battle,now=720)
        self.assertEqual(battle['lighting']['phase'],'night')
        self.assertEqual(battle['lighting']['arrival_minute'],44)
        first=lighting.presentation({},now=1800)
        self.assertEqual(first['phase'],'night')

    def test_clock_phase_windows(self):
        for phase,minute in [('day',12),('dusk',29),('night',42),('dawn',59)]:
            battle={}
            lighting.initialize(battle,now=minute*60)
            self.assertEqual(battle['lighting']['phase'],phase)

    def test_cached_lab_view_refreshes_clock_without_recomputing_map(self):
        from backend import battle_lab
        battle={}
        lighting.initialize(battle,now=720)
        snapshot={'lighting':lighting.presentation(battle,now=720),'units':{}}
        row={'battle':battle,'_view':(battle,snapshot),'mission':{},'variant':{},'seed':'qa'}
        with patch('backend.combat_lighting.time',return_value=1020):
            result=battle_lab.session_view('qa',row)
        self.assertEqual(result['battle']['lighting']['server_now'],1020)
        self.assertEqual(result['battle']['lighting']['arrived_at'],720)
        self.assertIs(result['battle']['units'],snapshot['units'])
        self.assertEqual(snapshot['lighting']['server_now'],720)
