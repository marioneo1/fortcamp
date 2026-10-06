import unittest
from types import SimpleNamespace
from unittest.mock import patch
from backend import battle_lab as lab
from backend.auth import Identity
from backend.game import new_game
from backend.main import CombatCommandRequest

class NavigationApiTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.settings=patch.object(lab,'settings',SimpleNamespace(environment='dev',game_debug_mode=True,dev_bypass_auth=False));self.settings.start();self.addCleanup(self.settings.stop)
        self.identity=Identity(guild_id='qa',user_id='qa',display_name='QA',guild_admin=True)
        mission=next(m for m in lab.catalogue() if m['id']=='prison_former_e')
        self.preview=lab.start_session(self.identity,lab.StartRequest(mission_id=mission['id'],variant_id=mission['variants'][0]['id'],seed='layout-0'),new_game({'name':'QA'}))
        self.sid=self.preview['session_id'];self.row=lab.get_session(self.sid,self.identity)
        self.addCleanup(lambda:lab._sessions.pop(self.sid,None))
    def test_both_public_request_models_retain_final_position(self):
        for model in [lab.CommandRequest,CombatCommandRequest]:
            self.assertEqual(model(action='guard',position={'x':2,'y':3}).model_dump(exclude_none=True)['position'],{'x':2,'y':3})
    async def test_real_lab_handler_commits_the_position_instead_of_discarding_it(self):
        node=next(p for p in self.preview['battle']['movement_tree'] if p['cost']>0)
        unit_id=self.preview['battle']['current_unit_id']
        with patch('backend.combat._advance_to_player'):
            await lab.command_battle(self.sid,lab.CommandRequest(action='guard',position={'x':node['x'],'y':node['y']}),self.identity)
        actor=self.row['battle']['units'][unit_id]
        self.assertEqual((actor['x'],actor['y']),(node['x'],node['y']));self.assertTrue(actor['guarding'])
    async def test_100_repeated_command_post_requests_reuse_one_validated_response(self):
        command=lab.CommandRequest(action='navigate',x=4,y=3)
        with patch.object(lab,'apply_player_command',wraps=lab.apply_player_command) as apply,patch.object(lab,'battle_view',wraps=lab.battle_view) as view:
            for _ in range(100):result=await lab.command_battle(self.sid,command,self.identity)
            self.assertEqual(apply.call_count,1);self.assertEqual(view.call_count,0)
            self.assertIn('battle',result)
            # A different battle state invalidates the response, rather than trapping it in cache.
            actor=self.row['battle']['units'][result['battle']['current_unit_id']]
            await lab.command_battle(self.sid,lab.CommandRequest(action='move',x=actor['x'],y=actor['y']),self.identity)
            await lab.command_battle(self.sid,command,self.identity)
            self.assertEqual(apply.call_count,3)
