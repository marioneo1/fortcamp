from copy import deepcopy
import unittest

from backend.game import equip_item, new_game


class EquipmentRecoveryTests(unittest.TestCase):
    def test_recovery_equipment_changes_keep_the_timer(self):
        state = new_game({'name': 'Recovering'})
        char = state['characters'][0]
        weapon = char['equipment']['weapon']
        char.update({'status': 'incapacitated', 'recovers_at': 123456789, 'recovery_location': 'medical_ward'})
        equip_item(state, char['id'], None, 'weapon')
        self.assertIsNone(char['equipment']['weapon'])
        equip_item(state, char['id'], weapon, 'weapon')
        self.assertEqual(char['equipment']['weapon'], weapon)
        self.assertEqual(char['status'], 'incapacitated')
        self.assertEqual(char['recovers_at'], 123456789)
        self.assertEqual(char['recovery_location'], 'medical_ward')

    def test_cannot_take_a_deployed_characters_weapon(self):
        state = new_game({'name': 'Deployed'})
        owner = state['characters'][0]
        owner['status'] = 'deployed'
        recipient = deepcopy(owner)
        recipient.update({'id': 'recovering', 'status': 'incapacitated'})
        recipient['equipment']['weapon'] = None
        state['characters'].append(recipient)
        weapon = owner['equipment']['weapon']
        with self.assertRaisesRegex(ValueError, 'on a mission'):
            equip_item(state, recipient['id'], weapon, 'weapon')
        self.assertEqual(owner['equipment']['weapon'], weapon)
        self.assertIsNone(recipient['equipment']['weapon'])
        with self.assertRaisesRegex(ValueError, 'on a mission'):
            equip_item(state, owner['id'], None, 'weapon')
