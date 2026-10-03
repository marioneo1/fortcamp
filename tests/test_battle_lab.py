import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.auth import Identity
from backend import battle_lab as lab
from backend.db import Base
from backend.game import new_game
from backend.models import PlayerState, MissionInstance
from sqlalchemy import select


class BattleLabTests(unittest.TestCase):
    def setUp(self):
        self.settings = SimpleNamespace(game_debug_mode=True, environment='dev', dev_bypass_auth=False)
        self.patcher = patch.object(lab, 'settings', self.settings)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        lab._sessions.clear()
        self.identity = Identity(guild_id='guild', user_id='owner', display_name='Tester', guild_admin=True)
        self.state = new_game({'name': 'Tester', 'starting_role': 'mage'})

    def start(self, mid='goblin_warcamp', variant='direct', **kwargs):
        return lab.start_session(self.identity, lab.StartRequest(mission_id=mid, variant_id=variant, **kwargs), self.state)

    def test_all_catalogued_maps_can_start_and_sources_are_real(self):
        missions = lab.catalogue()
        self.assertGreater(len(missions), 65)
        for mission in missions:
            with self.subTest(mission=mission['id']):
                preview = self.start(mission['id'], mission['variants'][0]['id'])
                self.assertIn(preview['battle']['status'], ('active', 'preparing'))
        court = next(m for m in missions if m['id'] == 'black_banner_court')
        self.assertIn('Private Contracts', court['source'])
        self.assertIn('The Tithe Convoy', court['follows'])
        self.assertEqual(next(m for m in missions if m['id'] == 'goblin_captive_cart')['rank'], 'D')

    def test_ambush_cover_and_boss_use_authored_setups(self):
        ambush = self.start(variant='approach:scout:success')['battle']
        enemies = [u for u in ambush['units'].values() if u['team'] == 'enemy']
        self.assertTrue(all(any(s['id'] == 'ambush_sleep' for s in u['statuses']) for u in enemies))
        cover = self.start(variant='approach:blockade:success')['battle']
        self.assertTrue(any(t['id'].startswith('approach_cover_') for t in cover['terrain']))
        direct = self.start()['battle']
        failed = self.start(variant='approach:scout:critical_failure')['battle']
        chief = next(u for u in failed['units'].values() if u.get('boss'))
        self.assertGreater(chief['max_hp'], direct['units'][chief['id']]['max_hp'])

    def test_investigation_can_force_a_different_commander_map(self):
        preview = self.start('goblin_smoke_signals', 'signals:follow:critical_failure')
        self.assertEqual(preview['variant']['encounter_id'], 'contract:goblin_chieftain')
        self.assertTrue(any(u.get('boss') for u in preview['battle']['units'].values()))

    def test_named_layout_seeds_launch_each_actual_template(self):
        missions=lab.catalogue()
        for mid,count in [('tool_shed',4),('workshop_intruders',4),('goblin_armory',4),('goblin_bridge',2),
                          ('chapel_patrol',4),('chapel_gate',4),('roadside_toll',4),
                          ('ford_enforcers',4),('road_cache',4),('bandit_outpost',4),('salvage_court',4)]:
            mission=next(m for m in missions if m['id']==mid)
            direct=mission['variants'][0]
            presets=direct['layout_presets']
            self.assertEqual(len(presets),count)
            for preset in presets:
                preview=self.start(mid,direct['id'],seed=preset['seed'])
                self.assertEqual(preview['battle']['template_id'],preset['id'])
                self.assertEqual(preview['seed'],preset['seed'])
        # A story complication must describe its encounter's layouts, not the parent map.
        investigation=next(m for m in missions if m['id']=='goblin_smoke_signals')
        for variant in investigation['variants']:
            self.assertEqual(variant['layout_presets'],lab.layout_presets(variant['encounter_id']))

    def test_save_and_roster_are_unchanged_and_seed_is_repeatable(self):
        self.state['characters'][0]['status'] = 'mission'
        snapshot = deepcopy(self.state)
        first = self.start()['battle']
        second = self.start()['battle']
        self.assertEqual(first, second)
        self.assertEqual(self.state, snapshot)
        self.assertEqual(len(self.state['characters']), 1)
        self.assertIn('lab_helper', first['units'])
        self.assertEqual(first['units']['player']['weapon'], second['units']['player']['weapon'])

    def test_sessions_are_tenant_scoped_expire_and_are_bounded(self):
        preview = self.start()
        for stranger in [Identity(guild_id='guild', user_id='other', display_name='Other', guild_admin=True),
                         Identity(guild_id='other', user_id='owner', display_name='Other', guild_admin=True)]:
            with self.assertRaises(HTTPException) as caught:
                lab.get_session(preview['session_id'], stranger)
            self.assertEqual(caught.exception.status_code, 404)
        for _ in range(6):
            self.start()
        self.assertEqual(len(lab._sessions), 4)
        row = next(iter(lab._sessions.values()))
        row['touched'] -= lab.TTL + 1
        lab.prune()
        self.assertEqual(len(lab._sessions), 3)

    def test_debug_disabled_production_and_non_admin_are_rejected(self):
        self.settings.game_debug_mode = False
        with self.assertRaises(HTTPException):
            self.start()
        self.settings.game_debug_mode = True
        self.settings.environment = 'prod'
        with self.assertRaises(HTTPException):
            self.start()
        self.settings.environment = 'dev'
        identity = Identity(guild_id='guild', user_id='owner', display_name='Tester', guild_admin=False)
        with self.assertRaises(HTTPException) as caught:
            lab.authorize(identity)
        self.assertEqual(caught.exception.status_code, 403)

    def test_invalid_approach_and_party_rejected(self):
        for kwargs in [dict(variant_id='traps'), dict(party_ids=['missing']), dict(party_ids=['player', 'player'])]:
            with self.assertRaises(HTTPException):
                lab.start_session(self.identity, lab.StartRequest(mission_id='goblin_warcamp', **kwargs), self.state)


class BattleLabPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_playing_and_resolving_preview_never_changes_database(self):
        engine = create_async_engine('sqlite+aiosqlite:///:memory:')
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        state = new_game({'name': 'Tester'})
        identity = Identity(guild_id='lab', user_id='owner', display_name='Tester', guild_admin=True)
        async with sessions.begin() as session:
            session.add(PlayerState(guild_id='lab', user_id='owner', display_name='Tester', state=state, updated_at=1))
        settings = SimpleNamespace(game_debug_mode=True, environment='dev', dev_bypass_auth=False)
        try:
            with patch.object(lab, 'settings', settings), patch.object(lab, 'SessionLocal', sessions):
                catalogue = await lab.list_battles(identity)
                self.assertEqual(catalogue['characters'][0]['name'], 'Tester')
                preview = await lab.start_battle(lab.StartRequest(mission_id='goblin_warcamp'), identity)
                row = lab.get_session(preview['session_id'], identity)
                before = deepcopy(row['battle'])
                with self.assertRaises(HTTPException):
                    await lab.command_battle(preview['session_id'], lab.CommandRequest(action='not-real'), identity)
                self.assertEqual(row['battle'], before)
                result = await lab.auto_battle(preview['session_id'], lab.AutoRequest(resolve_all=True), identity)
                self.assertEqual(result['battle']['status'], 'complete')
                self.assertNotIn('result', result)
            async with sessions() as session:
                saved = await session.get(PlayerState, {'guild_id':'lab', 'user_id':'owner'})
                self.assertEqual(saved.state, state)
                self.assertEqual(saved.updated_at, 1)
                self.assertEqual((await session.execute(select(MissionInstance))).scalars().all(), [])
        finally:
            await engine.dispose()
