import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat_abilities as abilities
from backend.combat import (create_goblin_warcamp_battle, apply_player_command, battle_view,
                            _current_unit, _resolve_ability, _player_auto_turn, auto_resolve)
from backend.game import new_game


class AbilityFoundationTests(unittest.TestCase):
    def fixture(self,role='mage'):
        state=new_game({'name':'Test','traits':['medic']} if role=='medic' else {'name':'Test','starting_role':role})
        # These fixtures isolate the equipment ability foundation, not Job kits.
        state['characters'][0].update(job_id=None,learned_skills=[],equipped_skills=[])
        b=create_goblin_warcamp_battle(state,['player'],'ability-fixture')
        a=b['units']['player'];t=b['units']['gob_guard']
        b.update(terrain=[],decorations=[],ground_tiles=[],elevation=[],void_tiles=[],turn_order=['player',t['id']],turn_index=0)
        for obj in b['objects'].values():obj['blocking']=False
        a.update(x=2,y=2,hp=100,max_hp=100,acted=False,move=3)
        t.update(x=3,y=2,hp=100,max_hp=100,armor=0,evasion=0)
        _current_unit(b)
        return b,a,t

    def command(self,b,a,t,skill=None):
        with patch('backend.combat._advance_to_player'):
            return apply_player_command(b,{'action':'skill','skill_id':(skill or a['skills'][0])['id'],'target_id':t['id']})

    def activate(self,b,a,round):
        b.update(round=round,turn_index=0);a['acted']=False
        _current_unit(b)

    def test_cooldown_survives_json_reload_and_repeated_views(self):
        b,a,t=self.fixture();skill=a['skills'][0]
        self.command(b,a,t)
        self.assertEqual(abilities.availability(a,skill)['cooldown_remaining'],2)
        restored=json.loads(json.dumps(b));a=restored['units']['player'];skill=a['skills'][0]
        before=deepcopy(restored)
        for _ in range(8):battle_view(restored)
        self.assertEqual(restored,before)
        self.activate(restored,a,2)
        self.assertEqual(abilities.availability(a,skill)['cooldown_remaining'],1)
        before=deepcopy(restored)
        with self.assertRaisesRegex(ValueError,'Ready in 1'):
            self.command(restored,a,restored['units'][t['id']])
        self.assertEqual(a['ability_state'],before['units']['player']['ability_state'])
        self.assertEqual(a['ability_activation'],before['units']['player']['ability_activation'])
        self.assertEqual(restored['units'][t['id']]['hp'],before['units'][t['id']]['hp'])
        self.activate(restored,a,3)
        self.assertTrue(abilities.availability(a,skill)['available'])

    def test_read_view_never_starts_status_or_activation(self):
        b,a,t=self.fixture();a['statuses']=[{'id':'poison','turns':2}]
        b['round']+=1
        before=deepcopy(b)
        for _ in range(5):battle_view(b)
        self.assertEqual(b,before)
        _current_unit(b);hp=a['hp'];activation=a['ability_activation']
        for _ in range(5):_current_unit(b)
        self.assertEqual(a['hp'],hp);self.assertEqual(a['ability_activation'],activation)
        self.assertEqual(hp,100)  # Poison now waits for target turn end.

    def test_failed_range_mute_and_unknown_skill_do_not_spend(self):
        for case in ('range','mute','unknown'):
            b,a,t=self.fixture()
            if case=='range':t.update(x=7,y=7)
            if case=='mute':a['statuses']=[{'id':'mute','turns':2}]
            command={'action':'skill','skill_id':'missing' if case=='unknown' else a['skills'][0]['id'],'target_id':t['id']}
            before=deepcopy(a['ability_state'])
            with self.assertRaises(ValueError):apply_player_command(b,command)
            self.assertEqual(a['ability_state'],before);self.assertEqual(t['hp'],100)

    def test_miss_spends_only_selected_ability(self):
        b,a,t=self.fixture()
        other=deepcopy(a['skills'][0]);other.update(id='other',cost={'charges':1,'cooldown':0})
        a['skills'].append(other)
        with patch('backend.combat._attack_hits',return_value=(False,{'damage_bonus':0,'chance':5},100)):
            self.command(b,a,t)
        self.assertEqual(t['hp'],100)
        a['acted']=False
        self.assertFalse(abilities.availability(a,a['skills'][0])['available'])
        self.assertTrue(abilities.availability(a,other)['available'])
        b['turn_index']=0
        self.command(b,a,t,other)
        a['acted']=False
        self.assertEqual(abilities.availability(a,other)['uses_remaining'],0)

    def test_support_resolves_heal_then_cleanse_while_muted(self):
        b,a,t=self.fixture('medic')
        a.update(hp=40,statuses=[{'id':'bleed','turns':2},{'id':'mute','turns':2}])
        skill=next(s for s in a['skills'] if s['id']=='field_care')
        self.command(b,a,a,skill)
        self.assertGreater(a['hp'],40)
        self.assertNotIn('bleed',{s['id'] for s in a['statuses']})
        self.assertIn('mute',{s['id'] for s in a['statuses']})
        a['acted']=False
        self.assertEqual(abilities.availability(a,skill)['cooldown_remaining'],3)

    def test_ordered_conditions_observe_actual_hit_and_damage(self):
        for hit in (True,False):
            b,a,t=self.fixture();skill=deepcopy(a['skills'][0])
            skill['effects'].append({'type':'status','status':'vulnerable','turns':1,
                                     'conditions':[{'type':'hit'},{'type':'target_hp_below','fraction':1}]})
            with patch('backend.combat._attack_hits',return_value=(hit,{'damage_bonus':0,'chance':100},1)):
                _resolve_ability(b,a,t,skill)
            self.assertEqual(any(s['id']=='vulnerable' for s in t['statuses']),hit)

    def test_invalid_late_effect_is_rejected_before_any_effect(self):
        b,a,t=self.fixture();skill=deepcopy(a['skills'][0])
        skill['effects'].append({'type':'execute_arbitrary_code'})
        before=deepcopy(b)
        with self.assertRaises(ValueError):_resolve_ability(b,a,t,skill)
        self.assertEqual(b,before)

    def test_legacy_battle_keeps_shared_use(self):
        b,a,t=self.fixture()
        a.pop('ability_version')
        for skill in a['skills']:
            for key in ('ability_version','effects','cost'):skill.pop(key,None)
        a['special']=a['skills'][0]
        self.command(b,a,t)
        self.assertTrue(a['special_used'])
        a['acted']=False
        with self.assertRaises(ValueError):self.command(b,a,t)

    def test_auto_and_manual_use_same_effects_and_costs(self):
        b,a,t=self.fixture();auto=deepcopy(b)
        self.command(b,a,t)
        # Keep only one visible target for a deterministic AI comparison.
        for uid,u in auto['units'].items():
            if uid not in ('player',t['id']):u.update(alive=False,conscious=False)
        _player_auto_turn(auto,auto['units']['player'],'balanced')
        self.assertEqual(auto['units'][t['id']]['hp'],t['hp'])
        self.assertEqual(auto['units']['player']['ability_state'],a['ability_state'])

    def test_long_fight_and_auto_limit_do_not_invent_a_loss(self):
        b,a,t=self.fixture();b.update(round=21,turn_index=0)
        _current_unit(b)
        self.assertEqual(b['status'],'active')
        auto_resolve(b,max_steps=0)
        self.assertEqual(b['status'],'active')
        self.assertIn('paused',b['auto_pause_reason'])
        self.assertIsNone(b.get('outcome'))

    def test_capture_tools_allow_lethal_unarmed_techniques(self):
        b,a,t=self.fixture('captor')
        skill=abilities.snapshot([{'id':'punch','name':'Punch','range':1,'elevation_rule':'melee'}],4)[0]
        a['skills']=[skill];before=t['hp']
        with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            self.command(b,a,t,skill)
        self.assertLess(t['hp'],before)

    def test_validation_rejects_unknown_conditions_bad_costs_and_numbers(self):
        _,a,_=self.fixture()
        for change in ({'cost':{'cooldown':0,'charges':None}}, {'range':True},
                       {'effects':[{'type':'status','status':'invented','turns':1}]},
                       {'effects':[{'type':'attack','conditions':[{'type':'script','code':'x'}]}]}):
            with self.assertRaises(ValueError):abilities.validate({**deepcopy(a['skills'][0]),**change})

    def test_all_equipment_definitions_snapshot_and_preserve_damage(self):
        from backend.content import ITEMS
        for item in ITEMS.values():
            if item.get('combat_skill'):
                with self.subTest(item=item['name']):
                    original=item['combat_skill'];saved=deepcopy(original)
                    result=abilities.snapshot([original],4)[0]
                    self.assertEqual(original,saved)
                    if result['target']=='enemy':
                        self.assertEqual(result['effects'][0]['damage_bonus'],original.get('damage_bonus',3))

    def test_lethal_attack_stops_followup_status_and_poison_immunity_survives(self):
        for lethal in (True,False):
            b,a,t=self.fixture();t['race']='Undead'
            if lethal:t['hp']=1
            skill=deepcopy(a['skills'][0])
            skill['effects'].append({'type':'status','status':'poison','turns':2,'conditions':[{'type':'hit'}]})
            with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
                _resolve_ability(b,a,t,skill)
            self.assertFalse(any(s['id']=='poison' for s in t['statuses']))
            self.assertEqual(t['hp']==0,lethal)
