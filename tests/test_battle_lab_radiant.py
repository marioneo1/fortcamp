import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from backend import battle_lab as lab
from backend.auth import Identity
from backend.game import new_game
from backend.combat_radiant import BEAR_ID, ELIGIBLE


class RadiantLabTests(unittest.TestCase):
    def setUp(self):
        self.identity=Identity(guild_id='qa',user_id='qa',display_name='QA',guild_admin=True)
        self.state=new_game({'name':'Radiant QA'})
        self.saved=deepcopy(self.state)
        self.patcher=patch.object(lab,'settings',SimpleNamespace(environment='dev',game_debug_mode=True,dev_bypass_auth=False))
        self.patcher.start();self.addCleanup(self.patcher.stop)
        lab._sessions.clear()

    def start(self, mission, mode):
        return lab.start_session(self.identity,lab.StartRequest(mission_id=mission,seed='lighting-radiant-qa',radiant_mode=mode),self.state)

    def test_catalogue_matches_actual_event_eligibility(self):
        for mission in lab.catalogue():
            for variant in mission['variants']:
                if variant['encounter_id'].startswith('showcase:'):continue
                self.assertEqual(bool(variant['radiant_events']),variant['encounter_id'].removeprefix('contract:') in ELIGIBLE)

    def test_force_bear_on_every_eligible_map_without_touching_save(self):
        for mission in ELIGIBLE:
            with self.subTest(mission=mission):
                result=self.start(mission,'bear')
                battle=lab._sessions[result['session_id']]['battle']
                self.assertEqual(battle['radiant_encounter']['state'],'pending')
                self.assertIn(BEAR_ID,battle['units'])
                self.assertTrue(battle['units'][BEAR_ID]['wildlife_hostile_all'])
        self.assertEqual(self.state,self.saved)

    def test_disabled_event_never_spawns(self):
        for mission in ELIGIBLE:
            result=self.start(mission,'absent')
            battle=lab._sessions[result['session_id']]['battle']
            self.assertEqual(battle['radiant_encounter']['state'],'absent')
            self.assertNotIn(BEAR_ID,battle['units'])

    def test_force_rejected_on_ineligible_map(self):
        with self.assertRaises(HTTPException) as error:self.start('goblin_warcamp','bear')
        self.assertEqual(error.exception.status_code,400)
