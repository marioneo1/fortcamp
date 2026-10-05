import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_spaces as spaces, combat_abilities as abilities
from tests import test_combat_abilities as fixtures


class CombatSpacesTests(unittest.TestCase):
    def fixture(self):
        return fixtures.AbilityFoundationTests().fixture()

    def skill(self,effect,target='enemy'):
        return {'id':'space_test','name':'Space Test','source_kind':'character',
                'ability_version':1,'target':target,'range':4,'elevation_rule':'line_of_effect',
                'cost':{'cooldown':2,'charges':None},'effects':[effect]}

    def zone(self,b,a,t,kind='thorns',turns=2):
        effect={'type':'zone','zone':kind,'radius':1,'turns':turns}
        spaces.place_zone(b,a,effect,combat._zone_cells(b,t,effect))

    def test_validation_snapshots_and_no_speculative_effects(self):
        skill=self.skill({'type':'zone','zone':'ember','radius':1,'turns':2})
        self.assertEqual(abilities.snapshot([skill],8),[skill])
        for key,val in [('radius',True),('radius',2),('zone','invented'),('turns',0)]:
            bad=deepcopy(skill);bad['effects'][0][key]=val
            with self.assertRaises(ValueError):abilities.validate(bad)
        with self.assertRaises(ValueError):abilities.validate(self.skill({'type':'form','form':'prowler','turns':2}))

    def test_zone_ground_clipping_and_owner_expiry(self):
        b,a,t=self.fixture();t.update(x=0,y=0)
        b['void_tiles']=[{'x':0,'y':1}]
        self.zone(b,a,t)
        self.assertEqual(b['zones'][0]['cells'],[{'x':0,'y':0},{'x':1,'y':0}])
        before=deepcopy(b)
        for _ in range(5):combat.battle_view(b)
        self.assertEqual(b,before)
        for turn,count in [(2,1),(3,0)]:
            b.update(round=turn,turn_index=0);combat._current_unit(b)
            self.assertEqual(len(b['zones']),count)

    def test_committed_entry_only_and_dedup_across_owners_reload(self):
        b,a,t=self.fixture();self.zone(b,a,t)
        combat._apply_tile_entry(b,t);self.assertEqual(t['hp'],100)
        t.update(x=4,y=2);combat._apply_tile_entry(b,t);self.assertEqual(t['hp'],97)
        t.update(x=3,y=2);combat._apply_tile_entry(b,t);self.assertEqual(t['hp'],94)
        restored=json.loads(json.dumps(b));t=restored['units'][t['id']]
        t.update(x=4,y=2);combat._apply_tile_entry(restored,t);self.assertEqual(t['hp'],91)
        t['status_activation']=[2,1];t.update(x=3,y=2)
        combat._apply_tile_entry(restored,t);self.assertEqual(t['hp'],88)

    def test_zone_manual_command_previews_and_no_immediate_damage(self):
        b,a,t=self.fixture();s=self.skill({'type':'zone','zone':'ember','radius':1,'turns':2})
        a['skills'].append(s)
        preview=combat._strike_preview(b,a,t,'line_of_effect',4,s)
        self.assertTrue(preview['setup_only']);self.assertEqual(len(preview['zones'][0]['cells']),5)
        with patch('backend.combat._advance_to_player'):
            combat.apply_player_command(b,{'action':'skill','skill_id':s['id'],'target_id':t['id']})
        self.assertEqual(t['hp'],100);self.assertTrue(a['acted']);self.assertEqual(len(b['zones']),1)
        b.update(turn_index=1);combat._current_unit(b)
        self.assertLess(t['hp'],100)
        hp=t['hp'];combat._current_unit(b);self.assertEqual(t['hp'],hp)

    def test_overlap_does_not_multiply_and_owner_defeat_suspends(self):
        b,a,t=self.fixture();self.zone(b,a,t,'sanctuary')
        ally=deepcopy(a);ally.update(id='ally',name='Ally');b['units']['ally']=ally
        self.zone(b,ally,t,'sanctuary')
        a.update(hp=50,x=3,y=2)
        combat._trigger_zones(b,a,'start');self.assertEqual(a['hp'],53)
        a['status_activation']=[2,0];a['statuses']=[{'id':'burn','turns':1}]
        combat._trigger_zones(b,a,'start');self.assertEqual(a['hp'],53)
        a['statuses']=[];a['status_activation']=[3,0];ally['conscious']=False
        a['conscious']=False;combat._trigger_zones(b,t,'start');self.assertEqual(t['hp'],100)

    def test_binding_respects_recovery_and_preview_does_not_consume(self):
        b,a,t=self.fixture();self.zone(b,a,t,'binding');t['control_immunity']=2
        t.update(x=4,y=2);combat._apply_tile_entry(b,t)
        self.assertFalse(any(s['id']=='bind' for s in t['statuses']))
        t['control_immunity']=0;t['status_activation']=[2,1];t.update(x=3,y=2)
        combat._apply_tile_entry(b,t)
        self.assertTrue(any(s['id']=='bind' for s in t['statuses']))

    def test_form_replace_expire_reload_keeps_hp_and_race(self):
        b,a,t=self.fixture();original={k:deepcopy(a.get(k)) for k in spaces.FORM_FIELDS}
        a['hp']=37;race=a['race'];movement=a['movement_type']
        spaces.change_form(a,{'form':'bulwark','turns':2})
        self.assertEqual(a['armor'],original['armor']+3)
        spaces.change_form(a,{'form':'prowler','turns':2})
        self.assertEqual(a['armor'],original['armor']);self.assertEqual(a['move'],original['move']+1)
        self.assertEqual((a['hp'],a['race'],a['movement_type']),(37,race,movement))
        b=json.loads(json.dumps(b));a=b['units']['player'];b.update(round=2,turn_index=0)
        combat._current_unit(b);self.assertIn('form',a)
        b.update(round=3,turn_index=0)
        combat._current_unit(b);self.assertNotIn('form',a)
        self.assertEqual({k:a.get(k) for k in spaces.FORM_FIELDS},original)
        self.assertEqual(a['hp'],37)

    def test_form_action_self_only_blocks_weapon_skills_not_character_skills(self):
        b,a,t=self.fixture();s=self.skill({'type':'form','form':'prowler','turns':2},'ally');a['skills'].append(s)
        with patch('backend.combat._advance_to_player'):
            combat.apply_player_command(b,{'action':'skill','skill_id':s['id'],'target_id':a['id']})
        a['acted']=False
        self.assertFalse(abilities.availability(a,a['skills'][0])['available'])
        own=deepcopy(a['skills'][0]);own.update(id='own',source_kind='character')
        self.assertTrue(abilities.availability(a,own)['available'])
        before=deepcopy(a)
        with self.assertRaises(ValueError):combat._resolve_ability(b,a,t,s)
        self.assertEqual(a,before)
        self.assertTrue(any(st['id']=='wild_form' for st in combat.battle_view(b)['units'][a['id']]['statuses']))

    def test_invalid_form_payload_and_zone_ground_leave_state_untouched(self):
        b,a,t=self.fixture();a['carrying']=t['id']
        before=deepcopy(a)
        with self.assertRaises(ValueError):combat._resolve_ability(b,a,a,self.skill({'type':'form','form':'prowler','turns':2},'ally'))
        self.assertEqual(a,before)
        b['void_tiles']=[{'x':t['x'],'y':t['y']}]
        with self.assertRaises(ValueError):combat._resolve_ability(b,a,t,self.skill({'type':'zone','zone':'thorns','radius':0,'turns':2}))
        self.assertEqual(a,before)

    def test_owner_removal_and_wall_edges_remove_or_clip_zones(self):
        b,a,t=self.fixture()
        b['terrain']=[{'id':'wall','x':t['x'],'y':t['y'],'kind':'wall','edge_wall':True,
                       'blocking':True,'blocks_sight':True,'wall_side':'east'}]
        with patch('backend.combat._line_of_sight',side_effect=lambda battle,origin,end:end['x']<=origin['x']):
            self.zone(b,a,t)
        self.assertFalse(any(p['x']>t['x'] for p in b['zones'][0]['cells']))
        a['extracted']=True;spaces.cleanup_zones(b,combat._combat_active)
        self.assertEqual(b['zones'],[])

    def test_crossing_zone_commits_route_but_preview_does_not(self):
        b,a,t=self.fixture();t.update(x=6,y=6)
        effect={'type':'zone','zone':'thorns','radius':0,'turns':2}
        spaces.place_zone(b,t,effect,[{'x':3,'y':2}])
        a.update(x=4,y=2,movement_origin={'x':2,'y':2},
                 movement_path=[{'x':3,'y':2},{'x':4,'y':2}])
        for _ in range(3):combat.battle_view(b)
        self.assertEqual(a['hp'],100)
        combat._commit_player_movement(b,a)
        self.assertEqual(a['hp'],97);self.assertEqual((a['x'],a['y']),(4,2))
        combat._commit_player_movement(b,a);self.assertEqual(a['hp'],97)

    def test_discarded_ember_preview_is_free_and_final_path_charges_each_tile(self):
        b,a,t=self.fixture();t.update(x=6,y=6)
        for unit in b['units'].values():
            if unit['id'] not in {a['id'],t['id']}:unit.update(x=7,y=7)
        spaces.place_zone(b,t,{'zone':'ember','turns':2},[{'x':2,'y':1},{'x':3,'y':1}])
        a['move']=4
        combat.apply_player_command(b,{'action':'move','x':2,'y':1})
        combat.apply_player_command(b,{'action':'move','x':1,'y':2})
        self.assertEqual(a['hp'],100)
        combat._commit_player_movement(b,a)
        self.assertEqual(a['hp'],100)
        # A new provisional selection crosses both cells only when committed.
        combat.apply_player_command(b,{'action':'move','x':2,'y':2})
        combat.apply_player_command(b,{'action':'move','x':3,'y':1})
        self.assertEqual(a['hp'],100)
        expected=sum((p['x'],p['y']) in {(2,1),(3,1)} for p in a['movement_path'])
        self.assertEqual(expected,2)
        combat._commit_player_movement(b,a)
        self.assertEqual(a['hp'],94)
        combat._commit_player_movement(b,a)
        self.assertEqual(a['hp'],94)

    def test_lethal_zone_entry_stops_route_and_dead_unit_cannot_attack(self):
        b,a,t=self.fixture();a['hp']=2
        spaces.place_zone(b,t,{'type':'zone','zone':'thorns','radius':0,'turns':2},[{'x':3,'y':2}])
        a.update(x=4,y=2,movement_origin={'x':2,'y':2},
                 movement_path=[{'x':3,'y':2},{'x':4,'y':2}])
        combat._commit_player_movement(b,a)
        self.assertEqual(a['hp'],0);self.assertEqual((a['x'],a['y']),(3,2))
        hp=t['hp'];combat._deal_damage(b,a,t);self.assertEqual(t['hp'],hp)


if __name__=='__main__':unittest.main()
