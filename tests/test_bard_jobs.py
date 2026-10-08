import unittest
from copy import deepcopy
from unittest.mock import patch

from backend import combat
from backend import job_loadouts as jobs
from tests.test_combat_abilities import AbilityFoundationTests


class BardJobTests(unittest.TestCase):
    def test_songs_do_not_create_additional_unit_tokens(self):
        for kind in ('accelerando','quickening_chorus'):
            battle, bard, ally, enemy = self.fixture()
            bard['skills'] = [deepcopy(jobs.SKILLS['job:bard:'+kind])]
            before = set(battle['units'])
            combat.apply_player_command(battle, {'action':'skill','skill_id':bard['skills'][0]['id'],'target_id':bard['id']})
            self.assertEqual(set(battle['units']), before)
            self.assertEqual(set(combat.battle_view(battle)['units']), before)

    def fixture(self):
        battle, bard, enemy = AbilityFoundationTests().fixture('mage')
        bard.update(job_id='bard', name='Bard', team='player', x=2, y=2, acted=False)
        enemy.update(x=5, y=2, hp=100, max_hp=100, armor=0, evasion=0)
        ally = deepcopy(bard)
        ally.update(id='ally', name='Ally', x=3, y=2, acted=False, statuses=[], skills=[])
        battle['units']['ally'] = ally
        battle['turn_order'] = ['player', 'ally', enemy['id']]
        bard['skills'] = []
        return battle, bard, ally, enemy

    def test_lingering_and_no_linger_song_refresh(self):
        battle, bard, ally, enemy = self.fixture()
        war = deepcopy(jobs.SKILLS['job:bard:war_anthem'])
        bard['skills'] = [war]
        combat._resolve_ability(battle, bard, bard, war)
        self.assertTrue(any(s['id'] == 'bard_war_anthem' for s in ally['statuses']))
        war_status = next(s for s in ally['statuses'] if s['id'] == 'bard_war_anthem')
        war_status['turns'] = 1
        combat.bard.refresh(battle, ally)
        self.assertEqual(war_status['turns'], 1)
        ally.update(x=7, y=2)
        combat.bard.refresh(battle, ally)
        self.assertTrue(any(s['id'] == 'bard_war_anthem' for s in ally['statuses']))

        combat.bard.stop_song(battle, bard)
        accel = deepcopy(jobs.SKILLS['job:bard:accelerando'])
        bard['skills'] = [accel]
        bard['acted'] = False
        ally.update(x=3, y=2, statuses=[])
        combat._resolve_ability(battle, bard, bard, accel)
        self.assertTrue(any(s['id'] == 'bard_accelerando' for s in ally['statuses']))
        ally.update(x=7, y=2)
        combat.bard.refresh(battle, ally)
        self.assertFalse(any(s['id'] == 'bard_accelerando' for s in ally['statuses']))

    def test_cue_the_strike_keeps_ally_activation_available(self):
        battle, bard, ally, enemy = self.fixture()
        cue = deepcopy(jobs.SKILLS['job:bard:cue_the_strike'])
        cue['bard_ally_id'] = ally['id']
        bard['skills'] = [cue]
        positions = {uid: (unit['x'], unit['y']) for uid, unit in battle['units'].items()}
        ally_activation = ally.get('ability_activation')
        with patch('backend.combat._attack_hits', return_value=(True, {'damage_bonus': 0, 'chance': 100}, 1)):
            combat._resolve_ability(battle, bard, enemy, cue)
        self.assertFalse(bard['acted'])
        self.assertFalse(ally['acted'])
        self.assertEqual(ally['ability_activation'], ally_activation)
        self.assertEqual(positions, {uid: (unit['x'], unit['y']) for uid, unit in battle['units'].items()})
        self.assertLess(enemy['hp'], 100)

    def test_cue_command_accepts_explicit_ally_and_keeps_bard_activation(self):
        battle, bard, ally, enemy = self.fixture()
        ally.update(x=4, y=2, attack_range=1)
        enemy.update(x=5, y=2)
        cue = deepcopy(jobs.SKILLS['job:bard:cue_the_strike'])
        bard['skills'] = [cue]
        battle['turn_order'] = [bard['id'], ally['id']]
        battle['turn_index'] = 0
        combat._current_unit(battle)
        before = enemy['hp']
        combat.apply_player_command(battle, {'action': 'skill', 'skill_id': cue['id'], 'ally_id': ally['id'], 'target_id': enemy['id']})
        self.assertLess(enemy['hp'], before)
        self.assertEqual(battle['turn_index'], 0)
        self.assertFalse(ally['acted'])

    def test_cue_api_schemas_preserve_the_second_target(self):
        from backend.main import CombatCommandRequest
        from backend.battle_lab import CommandRequest
        for schema in (CombatCommandRequest, CommandRequest):
            command = schema(action='skill', skill_id='job:bard:cue_the_strike',
                             ally_id='ally', target_id='enemy').model_dump(exclude_none=True)
            self.assertEqual(command['ally_id'], 'ally')

    def test_maestro_switches_song_without_a_stop_action(self):
        battle, bard, ally, enemy = self.fixture()
        bard['passives'] = [deepcopy(jobs.SKILLS['job:bard:maestro'])]
        combat.bard.begin_song(battle, bard, 'war_anthem')
        combat.bard.begin_song(battle, bard, 'accelerando')
        self.assertEqual(bard.get('bard_song'), 'accelerando')
        self.assertTrue(any(s.get('id') == 'bard_war_anthem' for s in ally['statuses']))

    def test_maestro_switch_keeps_lingering_war_anthem(self):
        battle, bard, ally, enemy = self.fixture()
        bard['passives'] = [deepcopy(jobs.SKILLS['job:bard:maestro'])]
        combat.bard.begin_song(battle, bard, 'war_anthem')
        self.assertTrue(any(s.get('id') == 'bard_war_anthem' for s in ally['statuses']))
        combat.bard.begin_song(battle, bard, 'accelerando')
        self.assertTrue(any(s.get('id') == 'bard_war_anthem' for s in ally['statuses']))

    def test_defeated_bard_ends_performance_but_keeps_acquired_lingering_buff(self):
        battle, bard, ally, enemy = self.fixture()
        combat.bard.begin_song(battle, bard, 'war_anthem')
        self.assertTrue(any(s.get('id') == 'bard_war_anthem' for s in ally['statuses']))
        bard['hp'] = 1
        combat._deal_damage(battle, enemy, bard, resolved_damage=10)
        self.assertTrue(any(s.get('id') == 'bard_war_anthem' for s in ally['statuses']))
        self.assertIsNone(bard.get('bard_song'))

    def test_song_of_peace_blocks_every_unit_including_bard_and_has_long_cooldown(self):
        battle, bard, ally, enemy = self.fixture()
        peace = deepcopy(jobs.SKILLS['job:bard:song_of_peace'])
        bard['skills'] = [peace]
        enemy.update(x=3, y=3)
        combat.bard.begin_song(battle, bard, 'song_of_peace')
        self.assertFalse(combat.bard.can_attack(bard))
        self.assertFalse(combat.bard.can_attack(ally))
        self.assertFalse(combat.bard.can_attack(enemy))
        self.assertEqual(peace['cost']['cooldown'], 5)

    def test_song_of_peace_ends_after_two_bard_activations(self):
        battle, bard, ally, enemy = self.fixture()
        bard['ability_activation'] = 1
        combat.bard.begin_song(battle, bard, 'song_of_peace')
        self.assertEqual(bard.get('bard_song'), 'song_of_peace')
        bard['ability_activation'] = 2
        combat.bard.refresh(battle, bard)
        self.assertEqual(bard.get('bard_song'), 'song_of_peace')
        bard['ability_activation'] = 3
        combat.bard.refresh(battle, bard)
        self.assertIsNone(bard.get('bard_song'))

    def test_jeering_verse_ai_will_not_switch_to_a_nearby_ally(self):
        battle, bard, ally, enemy = self.fixture()
        bard.update(x=2, y=2)
        ally.update(x=3, y=2)
        enemy.update(x=4, y=2, attack_range=1)
        combat.bard.apply_jeering(battle, bard, enemy)
        battle['turn_order'] = [enemy['id']]
        battle['turn_index'] = 0
        combat._current_unit(battle)
        before = ally['hp']
        combat._enemy_turn(battle, enemy)
        self.assertEqual(ally['hp'], before)

    def test_jeering_verse_overrides_confusion_target_redirection(self):
        battle, bard, ally, enemy = self.fixture()
        bard.update(x=2, y=2)
        ally.update(x=3, y=2)
        enemy.update(x=3, y=3, attack_range=2, statuses=[{'id':'confuse','turns':2}])
        combat.bard.apply_jeering(battle, bard, enemy)
        battle['turn_order'] = [enemy['id']]
        battle['turn_index'] = 0
        combat._current_unit(battle)
        with patch('backend.combat._perform_attack', return_value=(bard, False, 0, {'chance': 100}, 1)) as attack:
            combat._enemy_turn(battle, enemy)
        self.assertEqual(attack.call_args.args[2]['id'], bard['id'])

    def test_song_plants_bard_and_exposes_performance_overlay(self):
        battle, bard, ally, enemy = self.fixture()
        combat.bard.begin_song(battle, bard, 'war_anthem')
        self.assertEqual(combat._movement_limit(bard), 0)
        overlay = combat.bard.presentation(battle)
        self.assertEqual(overlay[0]['kind'], 'bard_song')
        self.assertEqual(overlay[0]['song'], 'war_anthem')
        self.assertIn({'x': bard['x'], 'y': bard['y']}, overlay[0]['cells'])
        self.assertIn({'x': bard['x'] + 1, 'y': bard['y']}, overlay[0]['cells'])
        self.assertNotIn({'x': bard['x'] + 2, 'y': bard['y']}, overlay[0]['cells'])

    def test_song_of_peace_blocks_ai_after_walking_into_the_radius(self):
        battle, bard, ally, enemy = self.fixture()
        bard.update(x=2, y=2)
        enemy.update(x=5, y=2, attack_range=1, move=3)
        combat.bard.begin_song(battle, bard, 'song_of_peace')
        battle['turn_order'] = [enemy['id']]
        battle['turn_index'] = 0
        combat._current_unit(battle)
        before = enemy['hp']
        combat._enemy_turn(battle, enemy)
        self.assertEqual(enemy['hp'], before)
        self.assertLessEqual(max(abs(enemy['x'] - bard['x']), abs(enemy['y'] - bard['y'])), 2)
        self.assertTrue(enemy['acted'])

    def test_song_of_peace_blocks_damaging_ability_from_inside(self):
        battle, bard, ally, enemy = self.fixture()
        bard.update(x=2, y=2)
        ally.update(x=3, y=2, skills=[deepcopy(jobs.SKILLS['job:mage:fireball'])])
        enemy.update(x=4, y=2)
        combat.bard.begin_song(battle, bard, 'song_of_peace')
        battle['turn_order'] = [ally['id']]
        battle['turn_index'] = 0
        combat._current_unit(battle)
        with self.assertRaisesRegex(ValueError, 'Song of Peace'):
            combat.apply_player_command(battle, {'action': 'skill', 'skill_id': ally['skills'][0]['id'], 'target_id': enemy['id']})

    def test_stop_song_command_is_explicit_and_advances_once(self):
        battle, bard, ally, enemy = self.fixture()
        skill = deepcopy(jobs.SKILLS['job:bard:war_anthem'])
        bard['skills'] = [skill]
        battle['turn_order'] = [bard['id'], ally['id']]
        battle['turn_index'] = 0
        combat._current_unit(battle)
        combat.bard.begin_song(battle, bard, 'war_anthem')
        view = combat.apply_player_command(battle, {'action': 'stop_song'})
        self.assertIsNone(bard.get('bard_song'))
        self.assertEqual(battle['turn_index'], 1)
        self.assertEqual(view['current_unit_id'], ally['id'])


    def test_stopped_lingering_songs_expire_at_end_of_next_recipient_turn(self):
        for song in ('war_anthem', 'quickening_chorus'):
            battle, bard, ally, enemy = self.fixture()
            ally.update(status_version=1, status_activation=[1, 1])
            combat.bard.begin_song(battle, bard, song)
            combat.bard.stop_song(battle, bard)
            combat.bard.refresh(battle)
            combat.conditions.finish_activation(ally)
            self.assertTrue(ally['statuses'])  # current activation is free
            ally['status_activation'] = [2, 1]
            combat.conditions.finish_activation(ally)
            self.assertFalse(ally['statuses'])

    def test_no_linger_ends_on_stop_and_peace_leaving_restores_attack(self):
        for song in ('accelerando', 'song_of_peace'):
            battle, bard, ally, enemy = self.fixture()
            combat.bard.begin_song(battle, bard, song)
            self.assertTrue(ally['statuses'])
            ally.update(x=7, y=2)
            combat.bard.refresh(battle, ally)
            self.assertFalse(ally['statuses'])
            self.assertTrue(combat.bard.can_attack(ally))
            ally.update(x=3, y=2)
            combat.bard.refresh(battle, ally)
            combat.bard.stop_song(battle, bard)
            self.assertFalse(ally['statuses'])

    def test_different_bards_refresh_one_buff_without_stacking(self):
        battle, bard, ally, enemy = self.fixture()
        other = deepcopy(bard)
        other.update(id='other', x=4, y=2)
        battle['units']['other'] = other
        combat.bard.begin_song(battle, bard, 'war_anthem')
        combat.bard.begin_song(battle, other, 'war_anthem')
        combat.bard.stop_song(battle, bard)
        combat.bard.refresh(battle)
        buffs = [s for s in ally['statuses'] if s['id'] == 'bard_war_anthem']
        self.assertEqual(len(buffs), 1)
        self.assertEqual(buffs[0]['source_id'], 'other')

    def test_performance_overlay_and_preview_share_wall_filtered_cells(self):
        battle, bard, ally, enemy = self.fixture()
        bard['skills'] = [deepcopy(jobs.SKILLS['job:bard:war_anthem'])]
        with patch('backend.combat_bard._line_of_sight', side_effect=lambda b, a, t: t['x'] <= a['x']):
            combat.bard.begin_song(battle, bard, 'war_anthem')
            cells = combat.bard.presentation(battle)[0]['cells']
            self.assertEqual(cells, combat.bard.performance_cells(battle, bard))
            self.assertNotIn({'x':3, 'y':2}, cells)
            self.assertFalse(ally['statuses'])
            view = combat.battle_view(battle)
            preview = view['skill_previews'][bard['skills'][0]['id']][bard['id']]
            self.assertEqual(preview['zones'][0]['cells'], cells)

    def test_quickening_ticks_once_per_activation_and_progress_is_permanent(self):
        battle, bard, ally, enemy = self.fixture()
        ally.update(ability_activation=1, ability_state={'attack': {'ready_at': 6}})
        combat.bard.begin_song(battle, bard, 'quickening_chorus')
        combat.abilities.start_activation(ally, [2, 1])
        self.assertEqual(ally['ability_state']['attack']['ready_at'], 5)
        combat.abilities.start_activation(ally, [2, 1])
        self.assertEqual(ally['ability_state']['attack']['ready_at'], 5)
        combat.bard.stop_song(battle, bard)
        ally['statuses'] = []
        combat.abilities.start_activation(ally, [3, 1])
        self.assertEqual(ally['ability_state']['attack']['ready_at'], 5)
        self.assertEqual(ally['ability_activation'], 3)


    def test_accelerando_meteor_is_immediate_without_stale_channel_or_delay(self):
        battle, bard, ally, enemy = self.fixture()
        meteor = deepcopy(jobs.SKILLS['job:mage:meteor'])
        ally['skills'] = [meteor]
        combat.bard.begin_song(battle, bard, 'accelerando')
        with patch('backend.combat._attack_hits', return_value=(True, {'damage_bonus': 0, 'chance': 100}, 1)):
            combat.mage.execute(battle, ally, enemy, meteor)
        self.assertLess(enemy['hp'], 100)
        self.assertFalse(battle.get('mage_delays'))
        self.assertNotIn('mage_channel', ally)
        self.assertFalse(any(s['id'] == 'channeling' for s in ally['statuses']))
        self.assertTrue(ally['acted'])
        self.assertGreater(ally['ability_state'][meteor['id']]['ready_at'], ally.get('ability_activation', 0))

    def test_no_song_acquisition_merely_crossing_radius_on_committed_route(self):
        battle, bard, ally, enemy = self.fixture()
        ally.update(x=5, y=2)
        combat.bard.begin_song(battle, bard, 'war_anthem')
        combat._apply_zone_route(battle, ally, [(4,2), (3,2), (4,2), (5,2)])
        combat.bard.refresh(battle, ally)
        self.assertFalse(ally['statuses'])

    def test_peace_auto_expiry_clears_restrictions_for_everyone(self):
        battle, bard, ally, enemy = self.fixture()
        bard['ability_activation'] = 1
        enemy.update(x=3, y=3)
        combat.bard.begin_song(battle, bard, 'song_of_peace')
        bard['ability_activation'] = 3
        combat.bard.refresh(battle)
        for unit in (bard, ally, enemy):
            self.assertTrue(combat.bard.can_attack(unit))
        self.assertEqual(combat.bard.presentation(battle), [])


if __name__ == '__main__':
    unittest.main()
