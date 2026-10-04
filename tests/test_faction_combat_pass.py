"""Behavior checks for rotating trade, combat tools and delayed battle handovers."""
import random
import unittest
from copy import deepcopy
from unittest.mock import patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.db import Base
from backend.models import PlayerState, MissionInstance
from backend.content import ITEMS, MISSION_TEMPLATES, GENERAL_LOOT_TABLE
from backend.game import new_game, normalize_state
from backend.economy import trade_view, purchase
from backend.faction_contracts import validate_request, available_jobs, STORY_JOBS
from backend.combat import (create_battle, battle_view, apply_player_command, auto_step,
                            _current_unit, _advance_to_player, _attack_preview, _deal_damage)
from backend.combat_supplies import sync_supplies
from backend import combat_conditions as conditions
from backend.services import (spawn_private_contract, claim_instance, choose_decision_instance,
                              update_battle_instance, get_battle_instance, now_ts)
from backend.mission_decisions import setup_encounter


def crew():
    s = normalize_state(new_game({'name': 'Captain', 'attributes': {'str': 20, 'vit': 20, 'agi': 18, 'int': 16}}))
    ally = deepcopy(s['characters'][0])
    ally.update(id='ally', name='Scout', is_player=False, loyalty=100)
    s['characters'].append(ally)
    s['mission_rank'] = 'C'
    s['resources']['gold'] = 1000
    s['inventory'] += [{'instance_id': f'dressing{i}', 'item_id': 'field_dressing'} for i in range(4)]
    return s


class FactionTradeTests(unittest.TestCase):
    def test_trader_stays_then_rotates_and_expired_offer_cannot_be_bought(self):
        s = crew()
        first = trade_view(s, 'g:u', 1000)
        trader = next(f for f in first['factions'] if f['visiting'])
        self.assertEqual(sum(bool(f['offers']) for f in first['factions']), 1)
        offer = trader['offers'][0]
        purchase(s, 'g:u', offer['id'], 1001)
        repeat = trade_view(s, 'g:u', 170000)
        self.assertEqual(repeat['rotation']['faction'], trader['id'])
        self.assertEqual(next(f for f in repeat['factions'] if f['visiting'])['offers'][0]['stock'], 0)
        next_visit = trade_view(s, 'g:u', 172800)
        self.assertNotEqual(next_visit['rotation']['faction'], trader['id'])
        with self.assertRaises(ValueError):
            purchase(s, 'g:u', offer['id'], 172800)
        # A returning trader restocks; this does not reset an ongoing visit.
        returned = trade_view(s, 'g:u', 3 * 172800)
        self.assertEqual(returned['rotation']['faction'], trader['id'])
        self.assertEqual(next(f for f in returned['factions'] if f['visiting'])['offers'][0]['stock'], 1)

    def test_basics_are_available_without_a_merchant_and_items_are_distinct_copies(self):
        s = crew()
        purchase(s, 'g:u', 'camp:field_dressing', 1000)
        purchase(s, 'g:u', 'camp:field_dressing', 1000)
        ids = [i['instance_id'] for i in s['inventory']]
        self.assertEqual(len(set(ids)), len(ids))
        self.assertEqual(s['resources']['gold'], 984)
        purchase(s, 'g:u', 'supplies:food', 172800)
        self.assertEqual(s['resources']['gold'], 982)

    def test_contacts_have_relationship_rank_and_personal_story_gates(self):
        s = crew()
        with self.assertRaises(ValueError): validate_request(s, 'watch_shared_signals')
        s['factions']['hedgerow'] = 6
        validate_request(s, 'watch_shared_signals')
        s['factions']['hedgerow'] = 45
        with self.assertRaisesRegex(ValueError, 'B-Rank'): validate_request(s, 'watch_horn_network')
        with self.assertRaises(ValueError): validate_request(s, 'hearse_names_returned')
        s['flags']['laid_hearse_to_rest'] = True
        validate_request(s, 'hearse_names_returned')
        self.assertTrue(any(j['id'] == 'hearse_names_returned' for j in available_jobs(s)))
        s['flags']['completed:hearse_names_returned'] = True
        with self.assertRaisesRegex(ValueError, 'already completed'): validate_request(s, 'hearse_names_returned')
        self.assertFalse(any(j['id'] == 'treaty_return_beacon' for j in available_jobs(s)))

    def test_exclusive_keepsakes_never_enter_general_loot(self):
        general = {row[0] for row in GENERAL_LOOT_TABLE}
        exclusive = {iid for iid in ITEMS if iid.endswith('_keepsake')}
        self.assertEqual(len(exclusive), 14)
        self.assertFalse(general & exclusive)
        for _, (_, mid, _, _, *_) in STORY_JOBS.items():
            self.assertTrue(MISSION_TEMPLATES[mid]['chain_only'])


class CombatToolsTests(unittest.TestCase):
    def battle(self):
        b = create_battle(crew(), ['player', 'ally'], 'tools', 'goblin_warcamp', defer_start=True)
        b['terrain'] = []; b['elevation'] = []
        b['turn_order'] = ['player', 'ally'] + [uid for uid in b['turn_order'] if uid not in {'player', 'ally'}]
        b['units']['player'].update(x=1, y=6)
        b['units']['ally'].update(x=2, y=6)
        _advance_to_player(b)
        return b

    def test_heal_caps_hp_cures_bleed_but_does_not_clear_unrelated_control(self):
        b = self.battle(); a = b['units']['ally']; a['hp'] -= 3
        for enemy in b['units'].values():
            if enemy['team'] == 'enemy': enemy.update(x=7, y=0, move=0, attack_range=1)
        a.update(statuses=[{'id': 'bleed', 'turns': 2}, {'id': 'stun', 'turns': 2}], forced_skip=True)
        apply_player_command(b, {'action': 'use_item', 'item_id': 'dressing0', 'target_id': 'ally'})
        self.assertEqual(a['hp'], a['max_hp'])
        self.assertFalse(conditions.has(a, 'bleed'))
        self.assertTrue(conditions.has(a, 'stun'))
        self.assertEqual(b['supplies_used'], ['dressing0'])

    def test_supply_ownership_range_norevive_and_shared_limit(self):
        b = self.battle(); a = b['units']['ally']; a['hp'] -= 20
        with self.assertRaises(ValueError): apply_player_command(b, {'action': 'use_item', 'item_id': 'unowned', 'target_id': 'ally'})
        a['x'] = 7
        with self.assertRaises(ValueError): apply_player_command(b, {'action': 'use_item', 'item_id': 'dressing0', 'target_id': 'ally'})
        a.update(x=2, conscious=False, condition='unconscious')
        with self.assertRaises(ValueError): apply_player_command(b, {'action': 'use_item', 'item_id': 'dressing0', 'target_id': 'ally'})
        a.update(conscious=True, condition='active')
        b['supplies_used'] = ['old1', 'old2', 'old3']
        with self.assertRaises(ValueError): apply_player_command(b, {'action': 'use_item', 'item_id': 'dressing0', 'target_id': 'ally'})
        self.assertEqual(len(b['supplies']), 4)

    def test_legacy_support_techniques_share_focus_and_work_when_physical_actor_is_muted(self):
        b = self.battle(); p = b['units']['player']; a = b['units']['ally']; a['hp'] -= 40
        p['statuses'] = [{'id': 'mute', 'turns': 2}]
        p['skills'] = [dict(ITEMS['medic_coat']['combat_skill']), dict(ITEMS['mourning_censer']['combat_skill'])]
        p['special'] = p['skills'][0]
        view = battle_view(b)
        self.assertIsNotNone(view['skill_previews']['field_care']['ally'])
        self.assertIsNone(view['skill_previews']['restoring_light']['ally'])
        apply_player_command(b, {'action': 'skill', 'skill_id': 'field_care', 'target_id': 'ally'})
        self.assertEqual(a['hp'], a['max_hp'] - 40 + 12 + p['intelligence'] // 2)
        self.assertTrue(p['special_used'])
        # A new activation still cannot spend a second equipped technique.
        b['turn_index'] = 0; b['round'] += 1; p['acted'] = False
        with self.assertRaises(ValueError): apply_player_command(b, {'action': 'skill', 'skill_id': 'restoring_light', 'target_id': 'ally'})

    def test_polling_does_not_repeat_regeneration_or_reroll_paralyze(self):
        b = self.battle(); p = b['units']['player']; p['hp'] -= 15
        p['statuses'] = [{'id': 'regeneration', 'turns': 2}, {'id': 'paralyze', 'turns': 2}]
        b['round'] += 1
        _current_unit(b)
        hp = p['hp']; blocked = p.get('forced_skip'); immobilized = p.get('paralyzed_move')
        for _ in range(5):
            battle_view(b); _current_unit(b)
        self.assertEqual(p['hp'], hp)
        self.assertEqual(p.get('forced_skip'), blocked)
        self.assertEqual(p.get('paralyzed_move'), immobilized)

    def test_control_does_not_stack_and_bosses_get_a_recovery_activation(self):
        unit = {'id': 'boss', 'boss': True, 'statuses': [], 'status_activation': [1, 0]}
        conditions.apply(unit, 'stun', 3)
        conditions.apply(unit, 'stun', 3)
        self.assertEqual(len(unit['statuses']), 1)
        self.assertEqual(unit['statuses'][0]['turns'], 1)
        unit['status_activation'] = [2, 0]
        conditions.finish_activation(unit)
        self.assertFalse(conditions.apply(unit, 'freeze', 2))
        conditions.start_activation({'seed': 'x'}, unit)
        self.assertFalse(conditions.apply(unit, 'freeze', 2))
        conditions.start_activation({'seed': 'x'}, unit)
        self.assertTrue(conditions.apply(unit, 'freeze', 2))

    def test_charm_changes_targets_without_changing_prisoner_ownership(self):
        b = self.battle(); p = b['units']['player']; e = b['units']['gob_guard']
        conditions.apply(e, 'charm', 2, p)
        targets = conditions.hostile_units(b, e, list(b['units'].values()))
        self.assertTrue(all(t['team'] == 'enemy' for t in targets))
        self.assertEqual(e['team'], 'enemy')

    def test_blind_and_fear_reduce_accuracy_and_freeze_can_be_shattered(self):
        b = self.battle(); p = b['units']['player']; target = b['units']['gob_guard']
        chance = _attack_preview(b, p, target, 'ballistic')['chance']
        conditions.apply(p, 'blind', 2)
        self.assertLess(_attack_preview(b, p, target, 'ballistic')['chance'], chance)
        p['statuses'] = []; p.update(attack=12, element='fire'); target.update(hp=100, max_hp=100, armor=0)
        conditions.apply(target, 'freeze', 1)
        self.assertGreater(_deal_damage(b, p, target), 12)
        self.assertFalse(conditions.has(target, 'freeze'))

    def test_autobattle_prepares_quietly_and_never_consumes_inventory(self):
        b = self.battle(); setup_encounter(b, {'setup': 'ambush'})
        for _ in range(6): auto_step(b)
        self.assertEqual(b['round'], 4)
        self.assertTrue(all(u['hp'] == u['max_hp'] for u in b['units'].values() if u['team'] == 'enemy'))
        self.assertEqual(b['supplies_used'], [])

    def test_rank_budgets_increase_without_reading_roster_strength(self):
        from backend.combat_pacing import enemy_budget
        from backend.races import race_gameplay
        budgets = [enemy_budget(r, True, race_gameplay('Human')) for r in ['E', 'D', 'C', 'B', 'A', 'S']]
        self.assertEqual([b['hp'] for b in budgets], sorted(b['hp'] for b in budgets))
        self.assertGreater(budgets[-1]['attack'], budgets[0]['attack'])
        a = crew(); z = deepcopy(a); z['characters'][0]['attributes']['str'] = 999
        ba = create_battle(a, ['player'], 'fixed', 'contract:highway_ambush')
        bz = create_battle(z, ['player'], 'fixed', 'contract:highway_ambush')
        self.assertEqual(ba['units']['contract_enemy_0'], bz['units']['contract_enemy_0'])


class FactionDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine('sqlite+aiosqlite:///:memory:')
        async with self.engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        s = crew(); s['factions'].update(lantern=30, hedgerow=30)
        async with self.sessions() as session:
            async with session.begin(): session.add(PlayerState(guild_id='g', user_id='u', display_name='Captain', state=s, updated_at=now_ts()))

    async def asyncTearDown(self): await self.engine.dispose()

    async def test_private_job_is_deduplicated_and_cannot_be_claimed_by_another_player(self):
        async with self.sessions() as session:
            async with session.begin():
                a = await spawn_private_contract(session, 'g', 'u', 'watch_shared_signals')
                b = await spawn_private_contract(session, 'g', 'u', 'watch_shared_signals')
                self.assertEqual(a.id, b.id)
                session.add(PlayerState(guild_id='g', user_id='other', display_name='Other', state=crew(), updated_at=now_ts()))
            async with session.begin():
                with self.assertRaises(ValueError): await claim_instance(session, 'g', 'other', 'Other', a.id, ['player'])

    async def test_owned_supply_is_spent_immediately_and_not_available_in_a_second_battle(self):
        async with self.sessions() as session:
            async with session.begin():
                p = await session.get(PlayerState, {'guild_id': 'g', 'user_id': 'u'})
                for mid in ('first', 'second'):
                    b = create_battle(p.state, ['player'], mid, 'goblin_warcamp')
                    b['units']['player']['hp'] -= 25
                    session.add(MissionInstance(id=mid, guild_id='g', template_id='goblin_warcamp', pool_slot=1 if mid == 'first' else 2,
                        position=0, spawned_at=now_ts(), expires_at=now_ts()+1000, duration_seconds=60, status='battle',
                        claimed_by_user_id='u', party_ids=['player'], analysis={'battle': b}))
            async with session.begin():
                await update_battle_instance(session, 'g', 'u', 'first', command={'action': 'use_item', 'item_id': 'dressing0', 'target_id': 'player'})
                self.assertNotIn('dressing0', {i['instance_id'] for i in p.state['inventory']})
            async with session.begin():
                view = await get_battle_instance(session, 'g', 'u', 'second')
                self.assertNotIn('dressing0', {i['instance_id'] for i in view['supplies']})
                with self.assertRaises(ValueError): await update_battle_instance(session, 'g', 'u', 'second', command={'action': 'use_item', 'item_id': 'dressing0', 'target_id': 'player'})

    async def test_postbattle_hand_over_awards_once_and_failed_optional_check_preserves_victory(self):
        async with self.sessions() as session:
            async with session.begin():
                m = await spawn_private_contract(session, 'g', 'u', 'lantern_diverted_wagon')
                await claim_instance(session, 'g', 'u', 'Captain', m.id, ['player', 'ally'])
                await choose_decision_instance(session, 'g', 'u', m.id, 'meeting', 0, 'direct')
                p = await session.get(PlayerState, {'guild_id': 'g', 'user_id': 'u'})
                gold = p.state['resources']['gold']; relationship = p.state['factions']['lantern']
                b = deepcopy(m.analysis['battle'])
                for u in b['units'].values():
                    if u['team'] == 'enemy': u.update(hp=0, alive=False, conscious=False, condition='dead')
                metadata = deepcopy(m.analysis); metadata['battle'] = b; m.analysis = metadata
            async with session.begin():
                _, result = await update_battle_instance(session, 'g', 'u', m.id, auto='balanced', resolve_all=True)
                self.assertTrue(result['scene_continuation'])
                self.assertEqual(m.status, 'decision')
                self.assertIsNone(m.result)
                self.assertEqual(p.state['resources']['gold'], gold)
                self.assertEqual(p.state['factions']['lantern'], relationship)
                self.assertEqual(p.state['characters'][0]['status'], 'mission')
                revision = m.analysis['scene']['revision']
            async with session.begin():
                # Force only the optional scene roll to fail. Battle outcome remains saved.
                with patch('backend.mission_decisions.classify', return_value='failure'):
                    final = await choose_decision_instance(session, 'g', 'u', m.id, 'recovery', revision, 'restore')
                self.assertEqual(m.status, 'completed')
                self.assertIn(final['result']['outcome'], {'success', 'critical_success'})
                self.assertGreater(p.state['resources']['gold'], gold)
                self.assertGreater(p.state['factions']['lantern'], relationship)
                self.assertTrue(p.state['flags']['completed:lantern_diverted_wagon'])
                self.assertEqual(p.state['characters'][0]['status'], 'idle')
                after = deepcopy(p.state)
            async with session.begin():
                with self.assertRaises(ValueError): await choose_decision_instance(session, 'g', 'u', m.id, 'recovery', revision, 'restore')
                self.assertEqual(p.state, after)
