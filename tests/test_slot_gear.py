import random
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from backend.content import ITEMS, MISSION_TEMPLATES, GENERAL_LOOT_TABLE, EVENT_REWARD_TABLES, MISSION_RANKS
from backend.gear_progression import SLOT_GEAR, EXCLUSIVE_DROPS, CAPTURE_DROPS, EVENT_EXCLUSIVES
from backend.equipment_rules import collect_rules
from backend.combat import (_player_unit, _deal_damage, _guard, _step_cost,
                            _throw_profile, _damage_terrain, _player_auto_turn,
                            create_goblin_warcamp_battle, apply_player_command, battle_view)
from backend.game import new_game, resolve_mission, analyze_mission
from backend.mission_loot import roll_item_pool, scene_reward_template
from backend.services import _award_capture_loot


class SlotGearTests(unittest.TestCase):
    def state(self, *ids):
        state = new_game({'name': 'Gear tester', 'attributes': {'str': 10, 'vit': 10, 'int': 10}})
        for iid in ids:
            state['inventory'].append({'instance_id': iid, 'item_id': iid})
            state['characters'][0]['equipment'][ITEMS[iid]['slot']] = iid
        return state

    def battle(self, *ids):
        state = self.state(*ids)
        battle = create_goblin_warcamp_battle(state, ['player'], 'slot-gear')
        battle['turn_order'] = ['player', 'gob_guard', 'gob_chief', 'gob_archer', 'gob_horn']
        battle['turn_index'] = 0
        return battle, battle['units']['player'], battle['units']['gob_guard']

    def test_effects_are_bounded_instead_of_stacking(self):
        rules = collect_rules([{'combat_rules': {'carry_strength': 3, 'guard_heal': 2, 'lifeline': True}},
                               {'combat_rules': {'carry_strength': 99, 'guard_heal': 4, 'lifeline': True}}])
        self.assertEqual(rules['carry_strength'], 6)
        self.assertEqual(rules['guard_heal'], 4)
        self.assertTrue(rules['lifeline'])
        state = self.state('rescue_gloves', 'porters_coat')
        unequipped = deepcopy(state)
        unequipped['characters'][0]['equipment'].update(hands=None, body=None)
        baseline = _player_unit(unequipped, unequipped['characters'][0], 0, 0)
        porter = _player_unit(state, state['characters'][0], 0, 0)
        self.assertEqual(porter['attack'], baseline['attack'])
        self.assertEqual(porter['strength'], baseline['strength'])
        self.assertEqual(porter['gear_rules']['carry_strength'], 6)

    def test_guard_and_survival_tradeoffs_work(self):
        b, actor, enemy = self.battle('field_triage_kit', 'second_chance_button', 'mercythread_robe')
        actor['hp'] = 5
        _guard(b, actor)
        self.assertEqual(actor['hp'], 9)
        actor['guarding'] = False
        enemy.update(attack=1000, on_hit=None)
        _deal_damage(b, enemy, actor)
        self.assertEqual(actor['hp'], 1)
        self.assertTrue(actor['alive'])
        self.assertTrue(actor['lifeline_used'])
        _deal_damage(b, enemy, actor)
        self.assertEqual(actor['condition'], 'dead')

    def test_survival_does_not_prevent_capture_and_protects_status_damage(self):
        b, actor, enemy = self.battle('second_chance_button')
        enemy['attack'] = 1000
        _deal_damage(b, enemy, actor, intent='nonlethal')
        self.assertEqual(actor['condition'], 'unconscious')
        self.assertFalse(actor.get('lifeline_used', False))
        b, actor, enemy = self.battle('second_chance_button')
        actor['hp'] = 1
        enemy.update(attack=5, status_tick=True)
        _deal_damage(b, enemy, actor)
        self.assertEqual(actor['hp'], 1)
        self.assertTrue(actor['lifeline_used'])

    def test_terrain_gear_preserves_climbing_cost(self):
        b, actor, _ = self.battle('creekwarden_waders')
        b['terrain'] = [{'x': 1, 'y': 1, 'kind': 'shallow_water', 'movement_cost': 3}]
        with patch('backend.combat._tile_height', side_effect=lambda battle, x, y: 2 if (x, y) == (1, 1) else 0):
            self.assertEqual(_step_cost(b, 0, 1, 1, 1, actor), 4)
            actor['gear_rules'] = {}
            self.assertEqual(_step_cost(b, 0, 1, 1, 1, actor), 6)

    def test_equipped_techniques_are_selectable_and_share_one_use(self):
        b, actor, enemy = self.battle('mooncord_sling', 'meridian_field_projector')
        names = {s['name'] for s in actor['skills']}
        self.assertIn('Mooncord Takedown', names)
        self.assertIn('Field Lance', names)
        self.assertEqual(len(battle_view(b)['skill_previews']), len(actor['skills']))
        actor.update(x=2, y=2)
        enemy.update(x=3, y=2, hp=100, max_hp=100)
        selected = next(s['id'] for s in actor['skills'] if s['name'] == 'Field Lance')
        with self.assertRaises(ValueError):
            apply_player_command(b, {'action': 'skill', 'skill_id': 'not-equipped', 'target_id': enemy['id']})
        with patch('backend.combat._attack_hits', return_value=(True, {'damage_bonus': 0, 'chance': 100}, 1)):
            apply_player_command(b, {'action': 'skill', 'skill_id': selected, 'target_id': enemy['id']})
        self.assertEqual(actor['special']['name'], 'Field Lance')
        self.assertTrue(actor['special_used'])
        actor['acted'] = False
        with self.assertRaises(ValueError):
            apply_player_command(b, {'action': 'skill', 'skill_id': actor['skills'][0]['id'], 'target_id': enemy['id']})

    def test_exclusives_never_leak_into_any_cache_rank_or_event(self):
        exclusive = {iid for iid, item in ITEMS.items() if 'mission_exclusive' in item.get('tags', [])}
        for rank in MISSION_RANKS:
            for eid in [None, *EVENT_REWARD_TABLES]:
                event = EVENT_REWARD_TABLES.get(eid)
                for seed in range(100):
                    iid, _, _ = roll_item_pool({'event': eid}, rank, random.Random(seed), ITEMS, GENERAL_LOOT_TABLE, event, MISSION_RANKS, bool(event))
                    self.assertNotIn(iid, exclusive)

    def test_authored_checks_have_misses_wins_and_chain_gates(self):
        mission = MISSION_TEMPLATES['rats_storehouse']
        observed = []
        for seed in range(250):
            s = self.state()
            result = resolve_mission(s, mission, ['player'], analyze_mission(s, mission, ['player']), seed=seed, forced_outcome='success')
            observed.append('second_chance_button' in result['rewards']['items'])
        self.assertTrue(any(observed))
        self.assertFalse(all(observed))
        for mid, (iid, chance, bonus, chain) in EXCLUSIVE_DROPS.items():
            direct = scene_reward_template(MISSION_TEMPLATES[mid], {})
            if chain:
                self.assertFalse(any(r['reward'].get('item') == iid for r in direct['reward_rolls']))
            follow = scene_reward_template(MISSION_TEMPLATES[mid], {'chain_parent_id': 'first'})
            row = next(r for r in follow['reward_rolls'] if r['reward'].get('item') == iid)
            self.assertEqual((row['chance'], row['critical_bonus']), (chance, bonus))

    def test_capture_drop_requires_living_recovered_target_and_success(self):
        for mid, drop in CAPTURE_DROPS.items():
            for condition, alive, extracted, outcome in [('dead', False, True, 'success'), ('unconscious', True, False, 'success'), ('unconscious', True, True, 'failure')]:
                b = {'encounter_id': mid, 'seed': 'capture', 'units': {drop['target']: {'id': drop['target'], 'name': 'Target', 'team': 'enemy', 'condition': condition, 'alive': alive, 'extracted': extracted}}}
                result = {'outcome': outcome, 'rewards': {}}
                _award_capture_loot(self.state(), b, result)
                self.assertFalse(any(r['possible_item'] == drop['item'] for r in result['rewards'].get('loot_rolls', [])))
            b['units'][drop['target']].update(condition='unconscious', alive=True, extracted=True)
            b['battlefield_secured'] = True
            rates = []
            for seed in range(200):
                b['seed'] = str(seed)
                result = {'outcome': 'success', 'rewards': {}}
                _award_capture_loot(self.state(), b, result)
                check = next(r for r in result['rewards']['loot_rolls'] if r['possible_item'] == drop['item'])
                self.assertEqual(check['chance'], drop['chance'] + drop['secured_bonus'])
                rates.append(check['item'] is not None)
            self.assertTrue(any(rates))
            self.assertFalse(all(rates))

    def test_catalogue_slots_and_icons_are_complete(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(len(SLOT_GEAR), 56)
        self.assertEqual({i['slot'] for i in SLOT_GEAR.values()}, {'head', 'body', 'hands', 'legs', 'feet', 'offhand', 'accessory', 'weapon'})
        # Media stays local; code-only clones can still run all behavioral tests.
        if (root / 'staging-ui/equipment-icons-v1/items_batch_004.png').exists():
            for iid in ITEMS:
                self.assertTrue((root / f'frontend/public/assets/catalogue/items/{iid}.png').exists(), iid)

    def test_capture_gloves_allow_sharp_weapon_subdue(self):
        b, actor, enemy = self.battle('cinderhook_blade', 'padded_capture_gloves')
        self.assertTrue(actor['nonlethal_capable'])
        actor.update(x=2, y=2, attack=100)
        enemy.update(x=3, y=2, hp=1)
        with patch('backend.combat._attack_hits', return_value=(True, {'damage_bonus': 0, 'chance': 100}, 1)):
            apply_player_command(b, {'action': 'subdue', 'target_id': enemy['id']})
        self.assertEqual(enemy['condition'], 'unconscious')
        self.assertTrue(enemy['alive'])
        self.assertEqual(enemy['statuses'], [])

    def test_throw_and_breach_bonus_have_distinct_limits(self):
        b, actor, _ = self.battle('breach_gauntlets', 'counterweight_boots')
        b['objects']['rock'] = {'id': 'rock', 'name': 'Rock', 'weight': 2, 'impact_damage': 3}
        actor.update(carrying_object='rock', strength=8)
        before = _throw_profile(b, {**actor, 'gear_rules': {}})
        after = _throw_profile(b, actor)
        self.assertEqual(after['range'], before['range'] + 1)
        self.assertEqual(after['damage'], before['damage'])
        actor['strength'] = 100
        self.assertEqual(_throw_profile(b, actor)['range'], 5)
        b['terrain'] = [{'id': 'wall', 'name': 'Wall', 'destructible': True, 'hp': 100, 'armor': 0}]
        _damage_terrain(b, actor, 'wall')
        self.assertEqual(b['terrain'][0]['hp'], 100 - actor['attack'] - 3)

    def test_conditional_damage_and_opening_guard(self):
        self.assertTrue(self.battle('lastwatch_helm')[1]['guarding'])
        b, actor, enemy = self.battle('empty_court_diadem', 'bloodtrail_pendant')
        enemy.update(hp=100, max_hp=200, armor=0, boss=True, guarding=False, racial_resistances=[], racial_weaknesses=[])
        actor.update(attack=5, on_hit=None)
        self.assertEqual(_deal_damage(b, actor, enemy), 9)
        actor['status_tick'] = True
        self.assertEqual(_deal_damage(b, actor, enemy), 5)

    def test_objective_auto_approaches_for_capture_instead_of_firing_lethal_bow(self):
        b, actor, enemy = self.battle('field_crossbow', 'padded_capture_gloves')
        for obj in b['objects'].values():
            obj['state'] = 'opened' if obj['id'] == 'prisoner_pen' else 'disabled'
        for unit in b['units'].values():
            if unit['team'] == 'enemy' and unit is not enemy:
                unit.update(alive=False, conscious=False, condition='dead')
        b['terrain'] = []
        actor.update(x=2, y=2, attack=100)
        enemy.update(x=4, y=2, hp=1, capture_role='live_target')
        with patch('backend.combat._attack_hits', return_value=(True, {'damage_bonus': 0, 'chance': 100}, 1)):
            _player_auto_turn(b, actor, 'objective')
        self.assertEqual(enemy['condition'], 'unconscious')
        self.assertTrue(enemy['alive'])


if __name__ == '__main__':
    unittest.main()
