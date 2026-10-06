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
