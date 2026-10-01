import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.run_profile import profile_config
from tools.prepare_release_copy import release_paths

class RunProfileTests(unittest.TestCase):
    def test_release_copy_uses_own_credentials_code_and_shared_production_save(self):
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d);root,data=release_paths(parent,'0.3.1-trial.1');root.mkdir()
            (root/'.fortcamp-release.json').write_text(json.dumps({'runtime_data':str(data)}))
            with patch('tools.run_profile.ROOT',root),patch.dict('os.environ',{'BOT_ENABLED':'false','DEV_BYPASS_AUTH':'true','DATABASE_URL':'wrong'}):
                env,cwd,ports=profile_config('release')
            self.assertEqual(cwd,root);self.assertEqual(ports,[5173]);self.assertEqual(env['FORTCAMP_ENV_FILE'],str(root/'.env'))
            self.assertEqual(env['DEV_BYPASS_AUTH'],'false');self.assertEqual(env['BOT_ENABLED'],'true')
            self.assertIn('fortcamp-release-data',env['DATABASE_URL']);self.assertEqual(env['FORTCAMP_UPLOAD_ROOT'],str(data/'portraits'))
            with self.assertRaises(ValueError):release_paths(parent,'../../outside')
    def test_release_data_cannot_escape_the_fortcamp_parent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'copy';root.mkdir()
            (root/'.fortcamp-release.json').write_text(json.dumps({'runtime_data':str(Path(d).parent/'outside')}))
            with patch('tools.run_profile.ROOT',root),self.assertRaises(ValueError):profile_config('release')
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
