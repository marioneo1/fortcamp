import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.run_profile import profile_config

class RunProfileTests(unittest.TestCase):
    def test_trial_overrides_debug_and_pins_code_while_dev_uses_other_ports_and_save(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);release=root/'.fortcamp-releases'/'test';release.mkdir(parents=True)
            (release.parent/'current.json').write_text(json.dumps({'release':'.fortcamp-releases/test'}))
            with patch('tools.run_profile.ROOT',root),patch.dict('os.environ',{'GAME_DEBUG_MODE':'true','DEV_BYPASS_AUTH':'true','MISSION_TIME_SCALE':'0.01','BOT_ENABLED':'true'}):
                env,cwd,ports=profile_config('stable');dev,dcwd,dports=profile_config('dev')
            self.assertEqual((env['DEV_BYPASS_AUTH'],env['GAME_DEBUG_MODE'],env['MISSION_TIME_SCALE']),('false','false','1.0'))
            self.assertEqual(env['DISCORD_TEST_GUILD_ID'],'');self.assertEqual(cwd,release);self.assertEqual(ports,[5173])
            self.assertEqual(dev['BOT_ENABLED'],'false');self.assertEqual(dev['GAME_DEBUG_MODE'],'true');self.assertEqual(dcwd,root)
            self.assertEqual(dports,[8001,5174]);self.assertNotEqual(env['DATABASE_URL'],dev['DATABASE_URL'])
            self.assertNotEqual(env['FORTCAMP_UPLOAD_ROOT'],dev['FORTCAMP_UPLOAD_ROOT'])
    def test_trial_cannot_load_a_release_outside_its_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'.fortcamp-releases').mkdir()
            (root/'.fortcamp-releases'/'current.json').write_text(json.dumps({'release':'../elsewhere'}))
            with patch('tools.run_profile.ROOT',root),self.assertRaises(ValueError):profile_config('stable')
