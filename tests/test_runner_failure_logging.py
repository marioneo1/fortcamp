import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch,MagicMock
from tools import run_profile

class RunnerFailureLoggingTests(unittest.TestCase):
    def test_abnormal_child_exit_preserves_output_and_returns_failure_for_batch_pause(self):
        with TemporaryDirectory() as temp:
            child=SimpleNamespace(stdout=StringIO('Traceback: simulated child failure\n'),poll=lambda:7,returncode=7,wait=lambda timeout:7)
            sock=MagicMock();sock.__enter__.return_value.connect_ex.return_value=1
            with patch.object(run_profile,'ROOT',Path(temp)),patch.object(run_profile,'profile_config',return_value=({},Path(temp),[65000,65001])),patch.object(run_profile,'conflicting_application',return_value=False),patch.object(run_profile.socket,'socket',return_value=sock),patch.object(run_profile.subprocess,'Popen',return_value=child),patch('sys.argv',['run_profile','dev']),patch('sys.stdout',StringIO()):
                with self.assertRaises(SystemExit) as caught:run_profile.main()
            self.assertEqual(caught.exception.code,7)
            text=(Path(temp)/'data/logs/dev-latest.log').read_text()
            self.assertIn('simulated child failure',text);self.assertIn('exit 7',text)

    def test_normal_dev_serves_source_and_opt_in_reload_is_backend_only(self):
        normal=run_profile.launch_commands('dev-discord',[8001,5174],{})
        self.assertNotIn('--reload',normal[0]);self.assertIn('dev',normal[1]);self.assertIn('5174',normal[1])
        live=run_profile.launch_commands('dev-discord',[8001,5174],{'FORTCAMP_DEV_AUTO_RELOAD':'true'})
        self.assertIn('--reload',live[0]);self.assertEqual(live[0][-1],str(run_profile.ROOT/'backend'));self.assertIn('dev',live[1])
        prod=run_profile.launch_commands('release',[5173],{'FORTCAMP_DEV_AUTO_RELOAD':'true'})
        self.assertEqual(len(prod),1);self.assertNotIn('--reload',prod[0])

    def test_logs_survive_a_second_launch(self):
        with TemporaryDirectory() as temp:
            logs=Path(temp)/'data/logs';logs.mkdir(parents=True);(logs/'dev-latest.log').write_text('previous session diagnostic')
            child=SimpleNamespace(stdout=StringIO('next failure\n'),poll=lambda:7,returncode=7,wait=lambda timeout:7)
            sock=MagicMock();sock.__enter__.return_value.connect_ex.return_value=1
            with patch.object(run_profile,'ROOT',Path(temp)),patch.object(run_profile,'profile_config',return_value=({},Path(temp),[65000,65001])),patch.object(run_profile,'conflicting_application',return_value=False),patch.object(run_profile.socket,'socket',return_value=sock),patch.object(run_profile.subprocess,'Popen',return_value=child),patch('sys.argv',['run_profile','dev']),patch('sys.stdout',StringIO()):
                with self.assertRaises(SystemExit):run_profile.main()
            archives=[p for p in logs.glob('dev-*.log') if p.name!='dev-latest.log']
            self.assertEqual(len(archives),1);self.assertEqual(archives[0].read_text(),'previous session diagnostic')
            self.assertIn('next failure',(logs/'dev-latest.log').read_text())
