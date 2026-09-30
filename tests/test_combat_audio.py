import unittest
from unittest.mock import patch

from backend.combat import apply_player_command, auto_step, battle_view, create_goblin_warcamp_battle
from backend.game import new_game


class CombatAudioTests(unittest.TestCase):
    def battle(self):
        state = new_game({'name': 'Sound Tester', 'attributes': {'str': 8, 'vit': 8}})
        battle = create_goblin_warcamp_battle(state, [state['characters'][0]['id']], 'audio-test')
        actor = battle['units'][battle_view(battle)['current_unit_id']]
        actor.update({'x': 3, 'y': 1, 'attack': 100})
        chief = battle['units']['gob_chief']
        chief.update({'x': 4, 'y': 1, 'hp': 1, 'evasion': 0})
        return battle, actor, chief

    def test_ranged_and_magic_hits_include_release_impact_and_actual_death(self):
        for rule, release, impact in [('ballistic', 'bow_release', 'arrow_hit'), ('ignore', 'magic_cast', 'magic_hit')]:
            with self.subTest(rule=rule):
                battle, actor, chief = self.battle()
                actor['attack_elevation_rule'] = rule
                with patch('backend.combat._attack_hits', return_value=(True, {'damage_bonus': 0, 'chance': 95}, 1)):
                    view = apply_player_command(battle, {'action': 'attack', 'target_id': chief['id']})
                self.assertEqual(chief['condition'], 'dead')
                cues = [cue['name'] for event in view['animation_events'] if event['type'] == 'sound' for cue in event['cues']]
                self.assertEqual(cues, [release, impact, 'unit_death'])
                self.assertFalse(any(event['type'] == 'melee_attack' for event in view['animation_events']))

    def test_missed_ranged_attack_never_plays_hit_or_death(self):
        battle, actor, chief = self.battle()
        actor['attack_elevation_rule'] = 'ballistic'
        with patch('backend.combat._attack_hits', return_value=(False, {'damage_bonus': 0, 'chance': 95}, 100)):
            view = apply_player_command(battle, {'action': 'attack', 'target_id': chief['id']})
        attack = next(event for event in view['animation_events'] if event['type'] == 'sound' and event.get('duration') == 490)
        self.assertEqual([cue['name'] for cue in attack['cues']], ['bow_release', 'attack_miss'])
        self.assertEqual(chief['hp'], 1)

    def test_auto_turn_discards_previous_feedback(self):
        battle, _, _ = self.battle()
        battle['animation_events'] = [{'type': 'sound', 'cues': [{'name': 'stale_feedback'}]}]
        view = auto_step(battle)
        cues = [cue['name'] for event in view['animation_events'] if event['type'] == 'sound' for cue in event['cues']]
        self.assertNotIn('stale_feedback', cues)


if __name__ == '__main__':
    unittest.main()
