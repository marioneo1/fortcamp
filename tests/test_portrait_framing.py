import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException
from backend import portrait_framing as framing, portrait_lab as lab
from backend.auth import Identity


class PortraitFramingTests(unittest.TestCase):
    def test_default_override_survives_audit_and_manual_character_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            registry=Path(directory)/'defaults.json';overrides=Path(directory)/'overrides.json'
            key='/api/portrait-pools/test/full/001.webp'
            registry.write_text(json.dumps({'portraits':{key:{'x':.5,'y':.3,'size':1}}}))
            with patch.object(framing,'REGISTRY_PATH',registry),patch.object(framing,'OVERRIDES_PATH',overrides):
                framing._cache_stamp=None
                corrected=framing.save_default(key,{'x':.4,'y':.2,'size':.8})
                registry.write_text(json.dumps({'portraits':{key:{'x':.6,'y':.6,'size':1}}}))
                character={'portrait':key.replace('/full/','/thumb/')}
                self.assertEqual(framing.resolve_frame(character),corrected)
                character.update(portrait_frame_source='manual',portrait_frame_key=key,portrait_frame={'x':.7,'y':.4,'size':.9})
                self.assertEqual(framing.resolve_frame(character)['x'],.7)
                self.assertEqual(framing.save_default(key)['x'],.6)
                character['portrait']='/api/portrait-pools/test/full/002.webp'
                self.assertEqual(framing.resolve_frame(character)['x'],.5)
        framing._cache_stamp=None

    def test_lab_blocks_production_nonadmin_and_unknown_portrait(self):
        identity=Identity(guild_id='guild',user_id='tester',display_name='Tester',guild_admin=False)
        with patch('backend.battle_lab.settings',SimpleNamespace(game_debug_mode=True,environment='dev',dev_bypass_auth=False)):
            with self.assertRaises(HTTPException) as error:asyncio.run(lab.list_portraits(identity))
            self.assertEqual(error.exception.status_code,403)
            identity.guild_admin=True
            with self.assertRaises(HTTPException) as error:asyncio.run(lab.update_default(lab.DefaultFrameRequest(key='../escape'),identity))
            self.assertEqual(error.exception.status_code,404)
        with patch('backend.battle_lab.settings',SimpleNamespace(game_debug_mode=True,environment='prod',dev_bypass_auth=True)):
            with self.assertRaises(HTTPException) as error:asyncio.run(lab.list_portraits(identity))
            self.assertEqual(error.exception.status_code,404)

    def test_catalogue_has_unique_stable_keys_and_frames(self):
        rows=lab.catalogue()
        self.assertGreater(len(rows),1000)
        self.assertEqual(len(rows),len({r['key'] for r in rows}))
        self.assertTrue(all(r['portrait_frame']['size']>0 for r in rows))


if __name__=='__main__':unittest.main()
