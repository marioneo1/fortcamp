import unittest
from backend.combat_feedback import record

class FeedbackSnapshotTests(unittest.TestCase):
    def test_status_snapshot_survives_subsequent_stacking_and_decay(self):
        battle = {}
        unit = {'id': 'rat', 'x': 2, 'y': 3, 'statuses': [{'id': 'burn', 'layers': [{'turns': 2}]}]}
        record(battle, unit, 'status', status_id='burn', attack_packet=7)
        unit['statuses'][0]['layers'][0]['turns'] = 1
        unit['statuses'][0]['layers'].append({'turns': 2})
        event = battle['animation_events'][0]
        self.assertEqual(event['statuses_snapshot'][0]['layers'], [{'turns': 2}])
        self.assertEqual(event['attack_packet'], 7)
        record(battle, unit, 'fire', 3)
        self.assertNotIn('statuses_snapshot', battle['animation_events'][1])
