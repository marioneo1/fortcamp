import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from tests import test_combat_abilities as ability_tests
from backend import combat_conditions as conditions
from backend.combat import (_deal_damage, _current_unit, _perform_attack, _resolve_ability,
    _displacement_preview, _apply_displacement, _secure_battlefield_loot, _climb_out,
    _context_actions, _player_auto_turn, battle_view, apply_player_command)


class TacticalFoundationTests(unittest.TestCase):
    def fixture(self):return ability_tests.AbilityFoundationTests().fixture()

    def test_leave_action_hidden_away_from_exit_disabled_during_hold_then_usable(self):
        b,a,_=self.fixture()
        b['extraction']={'name':'Western exit','tiles':[{'x':1,'y':2}]}
        self.assertFalse(any(entry['command']['action']=='leave' for entry in _context_actions(b,a)))
        a.update(x=1,y=2,exit_ready=False)
        entry=next(entry for entry in _context_actions(b,a) if entry['command']['action']=='leave')
        self.assertFalse(entry['available'])
        with self.assertRaisesRegex(ValueError,'Hold this exit'):
            apply_player_command(b,entry['command'])
        a['exit_ready']=True
        entry=next(entry for entry in _context_actions(b,a) if entry['command']['action']=='leave')
        self.assertTrue(entry['available'])
        with patch('backend.combat._advance_to_player'):
            apply_player_command(b,entry['command'])
        self.assertTrue(a['extracted'])

    def effect_skill(self,actor,effects,target='enemy'):
        return {**deepcopy(actor['skills'][0]),'id':'test-tactic','range':4,'target':target,
            'effects':effects,'cost':{'cooldown':2,'charges':None},'elevation_rule':'physical_care' if target=='ally' else 'melee'}

    def test_barrier_absorbs_finite_damage_without_stacking_or_duration_refresh(self):
        b,a,t=self.fixture()
        conditions.barrier(t,8,2,a);shield=deepcopy(t['statuses'])
        self.assertFalse(conditions.barrier(t,4,3,a));self.assertEqual(t['statuses'],shield)
        before=t['hp'];damage=_deal_damage(b,{**a,'attack':5,'element':None,'on_hit':None},t)
        self.assertEqual(damage,0);self.assertEqual(t['hp'],before)
        self.assertEqual(next(s for s in t['statuses'] if s['id']=='barrier')['amount'],3)
        _deal_damage(b,{**a,'attack':5,'element':None,'on_hit':None},t)
        self.assertEqual(t['hp'],before-2);self.assertFalse(conditions.has(t,'barrier'))

    def test_self_barrier_survives_cast_end_then_expires_after_next_activation(self):
        b,a,t=self.fixture();conditions.barrier(a,6,1,a)
        conditions.finish_activation(a);self.assertTrue(conditions.has(a,'barrier'))
        restored=json.loads(json.dumps(b));a=restored['units']['player']
        restored.update(round=2,turn_index=0);a['acted']=False;_current_unit(restored)
        before=deepcopy(restored)
        for _ in range(4):battle_view(restored)
        self.assertEqual(restored,before)
        conditions.finish_activation(a);self.assertFalse(conditions.has(a,'barrier'))

    def test_bind_is_conscious_and_control_can_refresh(self):
        b,a,t=self.fixture();t['status_activation']=[1,1]
        self.assertTrue(conditions.apply(t,'bind',3,a))
        self.assertTrue(conditions.apply(t,'bind',3,a))
        t['status_activation']=[2,1];conditions.start_activation(b,t)
        self.assertFalse(t.get('forced_skip',False));self.assertTrue(t['conscious'])
        conditions.finish_activation(t)
        before=deepcopy(t);conditions.finish_activation(t);self.assertEqual(t,before)
        for round in (3,4):
            t['status_activation']=[round,1];conditions.start_activation(b,t);conditions.finish_activation(t)
        self.assertTrue(conditions.apply(t,'bind',2,a))
        self.assertNotIn('control_immunity',t)

    def test_mark_is_owned_single_target_and_first_successful_hit_only(self):
        b,a,t=self.fixture();a['status_activation']=[1,0]
        other=deepcopy(a);other.update(id='other',name='Other');b['units']['other']=other
        conditions.mark(b,a,t,2);conditions.mark(b,other,t,2)
        self.assertEqual(len([s for s in t['statuses'] if s['id']=='mark']),2)
        from backend.combat import _attack_hits,_attack_preview
        t['evasion']=60
        with patch('backend.combat.random.Random') as rng:
            rng.return_value.randint.return_value=100
            self.assertFalse(_attack_hits(b,a,t,'ballistic')[0])
        self.assertEqual(_attack_preview(b,a,t,'ballistic')['mark_accuracy'],10)
        with patch('backend.combat.random.Random') as rng:
            rng.return_value.randint.return_value=1
            self.assertTrue(_attack_hits(b,a,t,'ballistic')[0])
        self.assertEqual(_attack_preview(b,a,t,'ballistic')['mark_accuracy'],0)
        self.assertEqual(_attack_preview(b,other,t,'ballistic')['mark_accuracy'],10)
        second=b['units']['gob_archer'];conditions.mark(b,a,second,2)
        self.assertFalse(any(s['id']=='mark' and s['source_id']==a['id'] for s in t['statuses']))
        self.assertTrue(any(s['id']=='mark' and s['source_id']==other['id'] for s in t['statuses']))

    def test_intercept_and_counter_share_allowance_and_cannot_chain(self):
        b,a,t=self.fixture();a.update(x=4,y=2,attack_elevation_rule='melee',attack=10)
        a['reactions']=[{'id':'riposte','name':'Riposte'}]
        guardian=deepcopy(a);guardian.update(id='guardian',name='Guardian',x=4,y=3)
        guardian['reactions'].append({'id':'intercept','name':'Intercept'});b['units']['guardian']=guardian
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)) as hits:
            recipient,_,_,_,_=_perform_attack(b,t,a,'melee')
            self.assertEqual(recipient['id'],'guardian');self.assertEqual(a['hp'],100)
            self.assertEqual(hits.call_count,1);self.assertFalse(guardian['reaction_ready'])
            _perform_attack(b,t,a,'melee')
            self.assertEqual(hits.call_count,3);self.assertFalse(a['reaction_ready'])
        b.update(round=2,turn_index=0);a['acted']=False;_current_unit(b)
        self.assertTrue(a['reaction_ready'])

    def test_miss_counter_and_disabled_reactions(self):
        for status in (None,'stun','sleep','charm','pit_trapped'):
            b,a,t=self.fixture();t.update(attack_elevation_rule='melee',reactions=[{'id':'returning_hand','name':'Returning Hand'}])
            if status:conditions.apply(t,status,1,a)
            with patch('backend.combat._attack_hits',return_value=(False,{'damage_bonus':0,'chance':100},100)) as hits:
                _perform_attack(b,a,t,'melee')
            self.assertEqual(hits.call_count,1 if status else 2)

    def test_followup_displacement_hits_interceptor_not_original_target(self):
        b,a,t=self.fixture();a.update(x=2,y=2)
        guardian=deepcopy(t);guardian.update(id='guardian',name='Guardian',x=3,y=3,displacement_resistance=100,
            reactions=[{'id':'intercept','name':'Intercept'}]);b['units']['guardian']=guardian
        skill=self.effect_skill(a,[{'type':'attack'},{'type':'displace','mode':'push','distance':1,'conditions':[{'type':'hit'}]}])
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            _resolve_ability(b,a,t,skill)
        self.assertEqual(t['hp'],100);self.assertLess(guardian['hp'],100)
        self.assertEqual((t['x'],t['y']),(3,2));self.assertTrue(any('resists' in line for line in b['log']))

    def test_push_pull_walls_occupancy_resistance_and_preview_purity(self):
        for case in ('push','pull','wall','occupied','resist'):
            b,a,t=self.fixture();t.update(x=4,y=2,displacement_resistance=100 if case=='resist' else 0)
            effect={'type':'displace','mode':'pull' if case=='pull' else 'push','distance':1}
            if case=='wall':b['terrain']=[{'id':'wall','x':5,'y':2,'blocking':True}]
            if case=='occupied':b['units']['gob_archer'].update(x=5,y=2)
            before=deepcopy(b);preview=_displacement_preview(b,a,t,effect);self.assertEqual(b,before)
            _apply_displacement(b,a,t,effect)
            expected=3 if case=='pull' else 5 if case=='push' else 4
            self.assertEqual(t['x'],expected)
            if case in ('wall','occupied'):self.assertTrue(preview['blocked'])

    def test_pit_types_flight_escape_and_lost_loot(self):
        for kind in ('shallow','deep','lethal'):
            b,a,t=self.fixture();t['displacement_resistance']=0
            b['terrain']=[{'id':'pit','kind':'pit','x':4,'y':2,'blocking':True,'requires_flying':True,'pit_kind':kind}]
            effect={'type':'displace','mode':'push','distance':1}
            before=deepcopy(b);self.assertEqual(_displacement_preview(b,a,t,effect)['pit'],kind);self.assertEqual(b,before)
            _apply_displacement(b,a,t,effect);self.assertEqual(t['x'],4)
            if kind=='lethal':
                self.assertEqual(t['condition'],'dead');self.assertTrue(t['lost_in_pit'])
                _secure_battlefield_loot(b);self.assertNotIn(t['id'],b['auto_looted_ids'])
            else:self.assertLess(t['hp'],100)
            if kind=='deep':
                self.assertTrue(conditions.has(t,'pit_trapped'))
                t['acted']=False
                self.assertTrue(any(c['command']['action']=='climb_out' for c in _context_actions(b,t)))
                _climb_out(b,t,(4,1));self.assertFalse(conditions.has(t,'pit_trapped'));self.assertTrue(t['acted'])
            b,a,t=self.fixture();t.update(movement_type='flying',displacement_resistance=0)
            b['terrain']=[{'id':'pit','kind':'pit','x':4,'y':2,'blocking':True,'requires_flying':True,'pit_kind':kind}]
            _apply_displacement(b,a,t,effect);self.assertEqual(t['hp'],100)

    def test_knockback_cannot_ready_extraction_or_leave_carried_body_behind(self):
        b,a,t=self.fixture();t.update(displacement_resistance=0,exit_ready=True,carrying='cargo')
        cargo=deepcopy(t);cargo.update(id='cargo',name='Cargo',alive=True,conscious=False,condition='unconscious',carried_by=t['id'],carrying=None)
        b['units']['cargo']=cargo
        _apply_displacement(b,a,t,{'mode':'push','distance':1})
        self.assertFalse(t['exit_ready']);self.assertEqual((cargo['x'],cargo['y']),(t['x'],t['y']))

    def test_lethal_fall_loses_carried_body_and_cannot_be_looted_by_flying_unit(self):
        b,a,t=self.fixture();t.update(displacement_resistance=0,carrying='cargo')
        cargo=deepcopy(t);cargo.update(id='cargo',name='Cargo',carrying=None,carried_by=t['id'],conscious=False,condition='unconscious')
        b['units']['cargo']=cargo
        t['gear_rules']={'lifeline':True};conditions.barrier(t,200,1,a)
        b['terrain']=[{'id':'pit','kind':'pit','x':4,'y':2,'blocking':True,'requires_flying':True,'pit_kind':'lethal'}]
        _apply_displacement(b,a,t,{'mode':'push','distance':1})
        self.assertTrue(t['lost_in_pit']);self.assertTrue(cargo['lost_in_pit'])
        self.assertEqual(t['hp'],0);self.assertEqual(cargo['condition'],'dead')
        from backend.combat import _carry_body
        a.update(x=4,y=1,movement_type='flying')
        with self.assertRaises(ValueError):_carry_body(b,a,t['id'])
        _secure_battlefield_loot(b);self.assertNotIn(t['id'],b['auto_looted_ids']);self.assertNotIn('cargo',b['auto_looted_ids'])

    def test_wall_boundaries_and_missed_push_do_not_move_target(self):
        b,a,t=self.fixture();before=(t['x'],t['y'])
        with patch('backend.combat.crossed_walls',return_value=[{'id':'edge-wall'}]):
            _apply_displacement(b,a,t,{'mode':'push','distance':1})
        self.assertEqual((t['x'],t['y']),before)
        skill=self.effect_skill(a,[{'type':'attack'},{'type':'displace','mode':'push','distance':1,'conditions':[{'type':'hit'}]}])
        with patch('backend.combat._attack_hits',return_value=(False,{'damage_bonus':0,'chance':100},100)):
            _resolve_ability(b,a,t,skill)
        self.assertEqual((t['x'],t['y']),before)

    def test_auto_and_manual_barrier_use_same_cost_and_effect(self):
        b,a,t=self.fixture();a.update(hp=35,attack_elevation_rule='melee')
        skill=self.effect_skill(a,[{'type':'barrier','amount':6,'turns':1}],'ally')
        a['skills']=[skill];a['special']=skill;auto=deepcopy(b)
        with patch('backend.combat._advance_to_player'):
            apply_player_command(b,{'action':'skill','skill_id':skill['id'],'target_id':a['id']})
        _player_auto_turn(auto,auto['units']['player'],'balanced')
        self.assertEqual(auto['units']['player']['ability_state'],a['ability_state'])
        self.assertEqual(auto['units']['player']['statuses'],a['statuses'])

    def test_barrier_does_not_block_capture_checks(self):
        b,a,t=ability_tests.AbilityFoundationTests().fixture('captor');conditions.barrier(t,200,1,a)
        t['resolve']=1
        from backend.combat import _capture_attempt
        with patch('backend.combat_captor.roll',return_value=0):
            _capture_attempt(b,a,t)
        self.assertEqual(t['condition'],'unconscious');self.assertTrue(t['alive'])
