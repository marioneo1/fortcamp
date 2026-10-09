"""Exercise the offline handoff against defects found in the actual submission."""
import copy
import unittest
from pathlib import Path

from tools.validate_character_blueprints import CONTRACT, read_json, unique_object, validate

CONTENT = CONTRACT.parent


class BlueprintAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = read_json(CONTRACT)
        cls.original = read_json(CONTENT / 'drafts/character_blueprints_pilot_001.json')
        cls.received = read_json(CONTENT / 'drafts/character_blueprints_pilot_001_revision_2.json')

    def corrected_fixture(self):
        # In-memory typed repair only; never rewrites the authored submission.
        def restore(current, previous):
            if isinstance(current, dict) and isinstance(previous, dict):
                for key in current.keys() & previous.keys():
                    if current[key] is None and previous[key] is not None:
                        current[key] = copy.deepcopy(previous[key])
                    else:
                        restore(current[key], previous[key])
            elif isinstance(current, list) and isinstance(previous, list):
                for left, right in zip(current, previous):
                    restore(left, right)
        draft = copy.deepcopy(self.received)
        restore(draft, self.original)
        return draft

    def test_received_revision_fails_all_23_known_typed_defects(self):
        errors, _ = validate(self.received, self.contract, self.original)
        self.assertEqual(len(errors), 23)
        self.assertTrue(any('max_offers' in error for error in errors))
        self.assertTrue(any('prospective_loyalty_cap.value' in error for error in errors))

    def test_typed_repair_passes_structure_but_still_requires_review(self):
        errors, warnings = validate(self.corrected_fixture(), self.contract, self.original)
        self.assertEqual(errors, [])
        self.assertTrue(any('loyalty-cap' in warning for warning in warnings))
        self.assertTrue(any('human review' in warning for warning in warnings))

    def test_dangling_route_and_changed_repeat_key_rejected(self):
        draft = self.corrected_fixture()
        draft['entries'][0]['routing'][0]['to'] = 'missing.node'
        draft['entries'][1]['personal_arcs'][0]['repeat_policy']['repeat_key'] += ':new'
        errors, _ = validate(draft, self.contract, self.original)
        self.assertTrue(any('unresolved local reference' in e for e in errors))
        self.assertTrue(any('stable repeat keys' in e for e in errors))

    def test_duplicate_ids_and_removed_baseline_ids_rejected(self):
        draft = self.corrected_fixture()
        facets = draft['entries'][0]['facets']
        facets[0]['id'] = facets[1]['id']
        errors, _ = validate(draft, self.contract, self.original)
        self.assertTrue(any('duplicate ID' in e for e in errors))
        self.assertTrue(any('baseline ID removed' in e for e in errors))

    def test_pending_decision_passes_structure_without_approval(self):
        draft = self.corrected_fixture()
        draft['decision_points'] = [{
            'id': draft['batch_id'] + '.decision_test', 'question': 'Approve trust test?',
            'recommendation': 'Review first.', 'alternatives': ['Keep', 'Replace'],
            'affected_ids': [draft['entries'][0]['id']], 'blocks_approval': True,
        }]
        errors, warnings = validate(draft, self.contract, self.original)
        self.assertEqual(errors, [])
        self.assertTrue(any('decision blocks approval' in w for w in warnings))

    def test_duplicate_json_keys_cannot_silently_overwrite(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
            unique_object([('revision', 2), ('revision', 3)])


if __name__ == '__main__':
    unittest.main()
