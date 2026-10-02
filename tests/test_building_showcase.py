import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
from collections import deque
from fastapi import HTTPException
from backend.building_showcase import FAMILIES, PARTS, presets, blueprint
from backend.battle_maps import compile_generated_battle_map,validate_battle_map
from backend.combat import _can_step
from backend.game import new_game
from backend.auth import Identity
from backend import battle_lab as lab


class BuildingShowcaseTests(unittest.TestCase):
    def test_every_material_has_four_distinct_complete_piece_sets_and_reachable_exits(self):
        for family in FAMILIES:
            shown=set();shapes=[]
            for preset in presets(family):
                board=blueprint(family,preset['seed'])
                self.assertEqual(board,blueprint(family,preset['seed']))
                self.assertEqual(board['template_id'],preset['id'])
                self.assertEqual(validate_battle_map('test',board),[])
                shown.update(board['material_showcase']['pieces'])
                shapes.append({(t['x'],t['y']) for t in board['terrain']})
                walking=compile_generated_battle_map('showcase_'+family,preset['seed'])
                walking['units']={}
                for t in walking['terrain']:
                    if t.get('kind')=='gate':t['blocking']=False
                exits={(p['x'],p['y']) for p in walking['extraction']['tiles']}
                for spawn in walking['spawn_zones']['enemy']+walking['spawn_zones']['player']:
                    seen={(spawn['x'],spawn['y'])};queue=deque(seen)
                    while queue:
                        x,y=queue.popleft()
                        for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                            if (nx,ny) not in seen and _can_step(walking,x,y,nx,ny,{'id':'tester'}):
                                seen.add((nx,ny));queue.append((nx,ny))
                    self.assertTrue(seen&exits,(family,preset['id'],spawn))
            self.assertEqual(shown,PARTS,family)
            self.assertEqual(len({tuple(sorted(s)) for s in shapes}),4)

    def test_material_previews_are_owner_scoped_and_do_not_mutate_save(self):
        identity=Identity(guild_id='test',user_id='owner',display_name='Tester',guild_admin=True)
        state=new_game({'name':'Tester'});before=deepcopy(state)
        with patch.object(lab,'settings',SimpleNamespace(environment='dev',game_debug_mode=True,dev_bypass_auth=True)):
            for family in FAMILIES:
                for preset in presets(family):
                    view=lab.start_session(identity,lab.StartRequest(mission_id='material_'+family,seed=preset['seed']),state)
                    self.assertEqual(view['battle']['template_id'],preset['id'])
                    self.assertEqual(view['battle']['units'][view['battle']['current_unit_id']]['team'],'player')
                    stranger=Identity(guild_id='test',user_id='stranger',display_name='Other',guild_admin=True)
                    with self.assertRaises(HTTPException):lab.get_session(view['session_id'],stranger)
            self.assertEqual(state,before)
        with patch.object(lab,'settings',SimpleNamespace(environment='prod',game_debug_mode=True,dev_bypass_auth=True)):
            with self.assertRaises(HTTPException):
                lab.start_session(identity,lab.StartRequest(mission_id='material_iron'),state)
