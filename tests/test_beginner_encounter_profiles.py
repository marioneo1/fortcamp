import unittest
from copy import deepcopy
from unittest.mock import patch

from backend import combat
from backend.battle_lab import layout_presets
from backend.combat_encounter_profiles import attack_percent
from backend.game import new_game
from backend.job_loadouts import snapshot
from backend.prison_recruitment import initialize_prisoner


class BeginnerEncounterProfileTests(unittest.TestCase):
    def battle(self, mission='rats_storehouse', seed=None):
        seed = seed or layout_presets('contract:' + mission)[0]['seed']
        return combat.create_contract_battle(new_game({'name': 'Audit', 'starting_role': 'fighter'}),
                                             ['player'], seed, mission, True)

    def test_profiles_use_clear_distinct_authored_tiles_in_every_variation(self):
        for mission in ('rats_storehouse', 'roadside_toll', 'wolves_fence'):
            for preset in layout_presets('contract:' + mission):
                battle = self.battle(mission, preset['seed'])
                enemies = combat._living(battle, 'enemy')
                counts = {'rats_storehouse': [3, 4, 2, 4], 'wolves_fence': [3, 2, 4, 3],
                          'roadside_toll': [2, 2, 2, 2]}
                self.assertEqual(len(enemies), counts[mission][battle['map_variation']-1])
                self.assertEqual(len({(u['x'], u['y']) for u in enemies}), len(enemies))
                for unit in enemies:
                    probe = deepcopy(battle)
                    probe['units'] = {}
                    self.assertFalse(combat._blocked(probe, unit['x'], unit['y']))
                    self.assertFalse(unit['boss'])
                if mission != 'roadside_toll':
                    self.assertTrue(all(u['creature'] and not u.get('job_id') for u in enemies))
                    self.assertTrue(all(u.get('passives') for u in enemies))
                    if mission=='rats_storehouse':self.assertTrue(all(not u.get('on_hit') for u in enemies))

    def test_larger_groups_have_bounded_total_hp_and_attack(self):
        for mission, hp_bounds, attack_bounds in [('rats_storehouse', (50, 56), (8, 9)),
                                                   ('wolves_fence', (62, 68), (10, 12))]:
            for preset in layout_presets('contract:' + mission):
                enemies = combat._living(self.battle(mission, preset['seed']), 'enemy')
                self.assertTrue(hp_bounds[0] <= sum(u['max_hp'] for u in enemies) <= hp_bounds[1])
                self.assertTrue(attack_bounds[0] <= sum(u['attack'] for u in enemies) <= attack_bounds[1])

    def test_delivery_court_has_two_outdoor_scavengers_and_no_spawn_overlap(self):
        preset = layout_presets('contract:rats_storehouse')[3]
        battle = self.battle(seed=preset['seed'])
        enemies = combat._living(battle, 'enemy')
        self.assertEqual(sum(u['x'] >= 14 for u in enemies), 2)
        self.assertEqual(sum(u['x'] < 14 for u in enemies), 2)
        self.assertEqual(len({(u['x'], u['y']) for u in battle['units'].values()}), len(battle['units']))

    def test_toll_keeps_two_humans_but_varies_the_second_role(self):
        roles = []
        for preset in layout_presets('contract:roadside_toll'):
            enemies = combat._living(self.battle('roadside_toll', preset['seed']), 'enemy')
            self.assertEqual(len(enemies), 2)
            self.assertTrue(all(u['race'] == 'Human' for u in enemies))
            roles.append(enemies[1]['combat_specialization'])
        self.assertEqual(roles, ['Road Cutpurse', 'Road Trapper', 'Road Trapper', 'Road Cutpurse'])

    def test_unmerged_rats_no_longer_receive_the_old_adjacent_damage_bonus(self):
        battle=self.battle();battle['terrain']=[]
        a,b,c=combat._living(battle,'enemy')
        a.update(x=5,y=5);b.update(x=6,y=5);c.update(x=5,y=6)
        self.assertEqual(attack_percent(battle,a,battle['units']['player']),100)

    def test_wolves_need_other_wolves_beside_the_victim_not_merely_the_attacker(self):
        battle = self.battle('wolves_fence')
        battle['terrain'] = []
        first, second, third = combat._living(battle, 'enemy')
        target = battle['units']['player']
        target.update(x=5, y=5)
        first.update(x=4, y=5)
        second.update(x=3, y=5)
        third.update(x=7, y=5)
        self.assertEqual(attack_percent(battle, first, target), 100)
        second.update(x=6, y=5)
        self.assertEqual(attack_percent(battle, first, target), 120)
        third.update(x=5, y=6)
        self.assertEqual(attack_percent(battle, first, target), 140)
        third['conscious'] = False
        self.assertEqual(attack_percent(battle, first, target), 120)

    def test_closed_boundary_blocks_pack_pressure_and_opening_it_restores_pressure(self):
        battle = self.battle('wolves_fence')
        actor, neighbor, other = combat._living(battle, 'enemy')
        target = battle['units']['player']
        target.update(x=5, y=5)
        actor.update(x=4, y=5)
        neighbor.update(x=6, y=5)
        other.update(x=12, y=10)
        gate = {'x': 5, 'y': 5, 'wall_edges': ['east'], 'blocking': True, 'blocks_sight': True}
        battle['terrain'] = [gate]
        self.assertEqual(attack_percent(battle, actor, target), 100)
        gate.update(blocking=False, blocks_sight=False)
        self.assertEqual(attack_percent(battle, actor, target), 120)

    def test_captured_toll_humanoids_keep_real_usable_jobs_and_loadouts(self):
        battle = self.battle('roadside_toll')
        for unit in combat._living(battle, 'enemy'):
            prisoner = {**deepcopy(unit), 'captured_at': 0}
            initialize_prisoner(prisoner, now=0)
            candidate = prisoner['recruitment']['candidate']
            self.assertEqual(candidate['job_id'], unit['job_id'])
            self.assertEqual(candidate['equipped_skills'], unit['recruitable_snapshot']['equipped_skills'])
            actives, passives, _ = snapshot(candidate)
            self.assertEqual([s['id'] for s in actives], [s['id'] for s in unit['skills']])
            self.assertEqual([s['id'] for s in passives], [s['id'] for s in unit['passives']])

    def test_enforcer_actually_uses_driving_strike(self):
        battle = self.battle('roadside_toll')
        battle['terrain'] = []
        unit = battle['units']['contract_enemy_0']
        target = battle['units']['player']
        unit.update(x=5, y=5)
        target.update(x=4, y=5)
        battle['units']['contract_enemy_1'].update(x=12, y=10)
        battle.update(turn_order=[unit['id'], target['id'], 'contract_enemy_1'], turn_index=0)
        with patch.object(combat, '_attack_hits', return_value=(True, {'chance': 100, 'damage_bonus': 0}, 1)):
            combat._enemy_turn(battle, unit)
        self.assertIn('job:fighter:bash', unit['ability_state'])
        self.assertLess(target['hp'], target['max_hp'])
        self.assertEqual(target['x'], 3)

    def test_species_forecast_matches_damage_and_dot_ticks_do_not_reapply_bite_procs(self):
        battle = self.battle()
        battle['terrain'] = []
        actor, neighbor, other = combat._living(battle, 'enemy')
        actor.update(x=5, y=5)
        neighbor.update(x=5, y=6)
        other.update(x=12, y=10)
        target = battle['units']['player']
        target.update(x=4, y=5, armor=0, guarding=False, statuses=[])
        forecast = combat._strike_preview(battle, actor, target, 'melee', 1)
        with patch.object(combat, '_attack_hits', return_value=(True, {'chance': 100, 'damage_bonus': 0}, 1)):
            _, _, damage, _, _ = combat._perform_attack(battle, actor, target, 'melee')
        self.assertEqual(forecast['damage_on_hit'], damage)
        target['statuses'] = []
        dot_source = {**actor, 'status_tick': True, 'percent_dot': True, 'attack': 1,
                      'on_hit': {'id': 'poison', 'chance': 100, 'turns': 1}}
        combat._deal_damage(battle, dot_source, target)
        self.assertFalse(any(s['id'] == 'poison' for s in target['statuses']))

    def test_fairy_and_ogre_keep_different_profiles_without_extreme_hp_disparity(self):
        units = {}
        for race in ('Human', 'Fairy', 'Ogre'):
            state = new_game({'name': 'Audit', 'race': race, 'starting_role': 'fighter'})
            units[race] = combat._player_unit(state, state['characters'][0], 1, 1)
        human, fairy, ogre = (units[race] for race in ('Human', 'Fairy', 'Ogre'))
        self.assertLess(fairy['max_hp'], human['max_hp'])
        self.assertGreater(fairy['max_hp'], human['max_hp'] * .65)
        self.assertGreater(fairy['move'], human['move'])
        self.assertEqual(fairy['movement_type'], 'flying')
        self.assertGreater(ogre['max_hp'], human['max_hp'])
        self.assertLess(ogre['max_hp'], fairy['max_hp'] * 2)
        self.assertLess(ogre['move'], human['move'])
        self.assertGreater(ogre['armor'], human['armor'])

    def test_engineer_unsupported_techniques_never_fall_into_generic_auto_resolver(self):
        state = new_game({'name': 'Audit', 'starting_role': 'engineer'})
        battle = combat.create_contract_battle(state, ['player'], 'audit-0', 'roadside_toll', True)
        battle['terrain'] = []
        unit = battle['units']['player']
        unit.update(x=5, y=5)
        battle['units']['contract_enemy_0'].update(x=4, y=5)
        with patch.object(combat.engineer, 'auto', return_value=False):
            combat._player_auto_turn(battle, unit, 'balanced')
        self.assertTrue(unit['acted'])


if __name__ == '__main__':
    unittest.main()
