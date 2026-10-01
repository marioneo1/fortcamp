import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.run_profile import profile_config, conflicting_application
from tools.prepare_release_copy import release_paths, release_env_source

class RunProfileTests(unittest.TestCase):
    def test_new_releases_preserve_production_env_instead_of_copying_dev(self):
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d);dev=parent/'alpha';dev.mkdir();old=parent/'fortcamp-release-1.0.0';old.mkdir()
            (dev/'.env').write_text('DISCORD_CLIENT_ID=dev-app\n')
            (old/'.env').write_text('DISCORD_CLIENT_ID=production-app\n')
            (old/'.fortcamp-release.json').write_text('{}')
            (dev/'.fortcamp-release-destination.json').write_text(json.dumps({'folder':str(old)}))
            with patch('tools.prepare_release_copy.ROOT',dev):
                self.assertEqual(release_env_source(parent),old/'.env')
                (dev/'.env.release').write_text('DISCORD_CLIENT_ID=explicit-production\n')
                self.assertEqual(release_env_source(parent),dev/'.env.release')
        with tempfile.TemporaryDirectory() as d,patch('tools.prepare_release_copy.ROOT',Path(d)):
            with self.assertRaises(SystemExit):release_env_source(Path(d))
    def test_duplicate_bot_applications_are_blocked_but_local_dev_is_allowed(self):
        from io import BytesIO
        env={'DISCORD_CLIENT_ID':'same-app'}
        with patch('tools.run_profile.urlopen',return_value=BytesIO(b'{"discord_client_id":"same-app","dev_bypass_auth":false}')):
            self.assertTrue(conflicting_application('dev-discord',env))
        with patch('tools.run_profile.urlopen',return_value=BytesIO(b'{"discord_client_id":"other-app","dev_bypass_auth":false}')):
            self.assertFalse(conflicting_application('dev-discord',env))
        with patch('tools.run_profile.urlopen',return_value=BytesIO(b'{"discord_client_id":"same-app","dev_bypass_auth":true}')):
            self.assertFalse(conflicting_application('release',env))
        self.assertFalse(conflicting_application('dev',env))
    def test_discord_dev_uses_public_port_real_auth_and_the_same_dev_save(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'DEV_BYPASS_AUTH':'true','BOT_ENABLED':'false'}):
            root=Path(d)
            with patch('tools.run_profile.ROOT',root):
                env,cwd,ports=profile_config('dev-discord');local,_,_=profile_config('dev')
            self.assertEqual(ports,[8001,5174]);self.assertEqual(cwd,root)
            self.assertEqual(env['DEV_BYPASS_AUTH'],'false');self.assertEqual(env['BOT_ENABLED'],'true')
            self.assertEqual(env['GAME_DEBUG_MODE'],'true')
            self.assertEqual(env['DATABASE_URL'],local['DATABASE_URL'])
            self.assertEqual(env['FORTCAMP_UPLOAD_ROOT'],local['FORTCAMP_UPLOAD_ROOT'])
            self.assertEqual(env['FORTCAMP_API_TARGET'],'http://127.0.0.1:8001')
            self.assertEqual(env['FORTCAMP_PROFILE'],'dev')
            self.assertEqual(env['FORTCAMP_WEB_ORIGIN'],'https://dev.fortcampgame.fyi')
    def test_release_copy_uses_own_credentials_code_and_shared_production_save(self):
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d);root,data=release_paths(parent,'0.3.1-trial.1');root.mkdir()
            (root/'.fortcamp-release.json').write_text(json.dumps({'runtime_data':str(data)}))
            with patch('tools.run_profile.ROOT',root),patch.dict('os.environ',{'BOT_ENABLED':'false','DEV_BYPASS_AUTH':'true','DATABASE_URL':'wrong'}):
                env,cwd,ports=profile_config('release')
            self.assertEqual(cwd,root);self.assertEqual(ports,[5173]);self.assertEqual(env['FORTCAMP_ENV_FILE'],str(root/'.env'))
            self.assertEqual(env['DEV_BYPASS_AUTH'],'false');self.assertEqual(env['BOT_ENABLED'],'true')
            self.assertEqual(env['FORTCAMP_PROFILE'],'release')
            self.assertEqual(env['FORTCAMP_WEB_ORIGIN'],'https://play.fortcampgame.fyi')
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
