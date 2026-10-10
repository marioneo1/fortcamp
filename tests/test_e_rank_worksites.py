import unittest
from copy import deepcopy

from backend import combat
from backend.battle_lab import layout_presets
from backend.content import MISSION_TEMPLATES
from backend.game import new_game
from backend.job_loadouts import snapshot
from backend.prison_recruitment import initialize_prisoner


MISSIONS = ('timber_creek', 'tool_shed', 'herbs_wall')


class WorksiteEncounterTests(unittest.TestCase):
    def battles(self, mid):
        for preset in layout_presets('contract:' + mid):
            yield combat.create_contract_battle(new_game({'name': 'QA'}), ['player'], preset['seed'], mid, True)

    def test_every_layout_has_accessible_nonoverlapping_opposition(self):
        layouts = 0
        for mid in MISSIONS:
            budgets = []
            for battle in self.battles(mid):
                layouts += 1
                enemies = combat._living(battle, 'enemy')
                self.assertIn(len(enemies), (2, 3))
                positions = {(u['x'], u['y']) for u in combat._living(battle)}
                self.assertEqual(len(positions), len(combat._living(battle)))
                probe = deepcopy(battle)
                probe['units'] = {}
                # Test site connectivity after opening doors, without requiring
                # an enemy to fit inside one activation's movement allowance.
                for obj in probe['terrain']:
                    if obj.get('kind') == 'gate':
                        obj.update(state='opened', blocking=False, blocks_sight=False,
                                   sprite=obj['open_sprite'])
                walker = deepcopy(combat._living(battle, 'player')[0])
                walker.update(move=1000, movement_origin=None)
                reachable, _ = combat._movement_tree(probe, walker)
                for enemy in enemies:
                    self.assertFalse(combat._blocked(probe, enemy['x'], enemy['y']))
                    self.assertIn((enemy['x'], enemy['y']), reachable)
                    self.assertEqual(enemy['race'], 'Goblin')
                    self.assertFalse(enemy['boss'])
                    self.assertGreaterEqual(enemy['max_hp'], 17)
                    self.assertEqual(len(enemy['skills']) + sum(p.get('source_kind')!='background' for p in enemy['passives']), 2)
                budgets.append(sum(u['max_hp'] for u in enemies))
                self.assertGreaterEqual(sum(u['attack'] for u in enemies),6)
                self.assertLessEqual(sum(u['attack'] for u in enemies),12)
            self.assertLessEqual(max(budgets) / min(budgets), 1.15)
        self.assertEqual(layouts, 10)

    def test_capture_preserves_specialization_and_usable_skills(self):
        for mid in MISSIONS:
            for battle in self.battles(mid):
                for unit in combat._living(battle, 'enemy'):
                    captive = {'id': 'c', 'name': unit['name'], 'race': unit['race'],
                               'recruitable_snapshot': deepcopy(unit['recruitable_snapshot'])}
                    initialize_prisoner(captive, now=0)
                    candidate = captive['recruitment']['candidate']
                    skills, _, _ = snapshot(candidate)
                    self.assertEqual([s['id'] for s in skills], [s['id'] for s in unit['skills']])
                    self.assertEqual(candidate['combat_specialization'], unit['combat_specialization'])
                    self.assertEqual(candidate['personality_id'], unit['personality_id'])

    def test_peaceful_route_and_postcombat_handover_remain_available(self):
        for mid in MISSIONS:
            nodes = MISSION_TEMPLATES[mid]['decision_scene']['nodes']
            choices = nodes['approach']['choices']
            for outcome in ('success', 'failure', 'critical_failure'):
                self.assertNotIn('battle', choices['safe'][outcome])
                self.assertIn('finish', choices['safe'][outcome])
            self.assertEqual(choices['risk']['success']['after_battle'], 'handover')
            self.assertIn('handover', nodes)
