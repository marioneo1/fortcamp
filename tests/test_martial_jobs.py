import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_abilities as abilities, combat_conditions as conditions, combat_martial as martial, job_loadouts as jobs
from tests import test_combat_abilities as fixtures


class MartialJobTests(unittest.TestCase):
    def fixture(self, passive_names=()):
        battle, actor, target=fixtures.AbilityFoundationTests().fixture('fighter')
        actor.update(attack=20,armor=0,gear_rules={},perk_modifiers={},element=None,on_hit=None,
                     capture_weapon=None,attack_elevation_rule='melee',fury=0,fury_cap=5,job_id='barbarian',
                     passives=[deepcopy(jobs.SKILLS['job:barbarian:'+name]) for name in passive_names])
        target.update(attack=20,armor=0,gear_rules={},perk_modifiers={},race='Human',statuses=[],reactions=[],
                      attack_elevation_rule='melee',element=None,on_hit=None)
        return battle,actor,target

    def cast(self,b,a,t,key):
        skill=deepcopy(jobs.SKILLS[key]);a['skills']=[skill]
        return combat._resolve_ability(b,a,t,skill)

    def test_innate_fury_direct_low_health_ticks_barrier_and_friendly_damage(self):
        b,a,t=self.fixture(('bloodfury',));a['hp']=70
        combat._deal_damage(b,t,a)
        self.assertEqual((a['hp'],a['fury']),(50,2))
        combat._deal_damage(b,{**t,'attack':2,'status_tick':True},a)
        self.assertEqual(a['fury'],3)
        conditions.barrier(a,100,1,a)
        combat._deal_damage(b,t,a)
        self.assertEqual(a['fury'],3)
        conditions.remove(a,'barrier')
        ally={**t,'id':'ally','team':'player'};b['units']['ally']=ally
        combat._deal_damage(b,ally,a)
        self.assertEqual(a['fury'],3)
        martial.gain_fury(b,a,10);self.assertEqual(a['fury'],5)

    def test_reckless_damage_exposure_and_owner_cooldown(self):
        b,a,t=self.fixture()
        self.cast(b,a,t,'job:barbarian:reckless_blow')
        self.assertEqual((t['hp'],a['fury']),(60,1))
        combat._deal_damage(b,t,a);self.assertEqual(a['hp'],76)
        skill=a['skills'][0]
        self.assertEqual(abilities.availability(a,skill)['cooldown_remaining'],2)
        a['ability_activation']+=1;martial.start_activation(b,a)
        self.assertFalse(conditions.has(a,'reckless_exposure'))

    def test_skullbreaker_spends_two_fury_and_stuns_for_two_turns(self):
        b,a,t=self.fixture();a['fury']=2
        self.cast(b,a,t,'job:barbarian:skullbreaker')
        self.assertEqual((t['hp'],a['fury']),(75,0))
        self.assertEqual(next(s for s in t['statuses'] if s['id']=='stun')['turns'],2)
        b,a,t=self.fixture();before=deepcopy(t)
        with self.assertRaisesRegex(ValueError,'Requires 2 Fury'):
            self.cast(b,a,t,'job:barbarian:skullbreaker')
        self.assertEqual(t,before)

    def test_bloodied_strength_uses_hp_loss_and_does_not_change_base_attack(self):
        b,a,t=self.fixture(('bloodied_strength',))
        self.assertEqual(martial.attack_power(a),20)
        a['hp']=1;self.assertEqual(martial.attack_power(a),30)
        combat._deal_damage(b,a,t);self.assertEqual(t['hp'],70)
        self.assertEqual(a['attack'],20)
        a['hp']=100;self.assertEqual(martial.attack_power(a),20)

    def test_death_defiance_multiple_hits_expiry_and_no_automatic_death(self):
        b,a,t=self.fixture(('too_angry_to_fall',));a['hp']=5
        combat._deal_damage(b,t,a);self.assertEqual(a['hp'],1);self.assertTrue(a['alive'])
        for _ in range(3):combat._deal_damage(b,t,a)
        self.assertEqual(a['hp'],1);self.assertTrue(a['conscious'])
        a['ability_activation']+=1;martial.start_activation(b,a)
        self.assertEqual(a['hp'],1);self.assertTrue(a['alive'])
        combat._deal_damage(b,t,a);self.assertFalse(a['alive'])

    def test_bloodthirst_multi_kill_window_and_three_turn_cooldown(self):
        b,a,t=self.fixture(('bloodthirst',));a['hp']=30;t['hp']=1
        combat._deal_damage(b,a,t);self.assertEqual(a['hp'],50)
        for clock,expected in ((a['ability_activation'],70),(a['ability_activation']+1,70),(a['ability_activation']+3,90)):
            a['ability_activation']=clock
            victim={**t,'id':str(clock)+str(expected),'hp':1,'alive':True,'conscious':True,'condition':'active'}
            b['units'][victim['id']]=victim;combat._deal_damage(b,a,victim)
            self.assertEqual(a['hp'],expected)

    def test_unstoppable_cost_cooldown_and_control_recovery(self):
        b,a,t=self.fixture(('unstoppable',));a['fury']=3
        conditions.apply(a,'stun',2,t)
        self.assertFalse(conditions.has(a,'stun'));self.assertEqual(a['fury'],2)
        conditions.apply(a,'poison',2,t);self.assertTrue(conditions.has(a,'poison'))
        a['ability_activation']+=3;martial.start_activation(b,a)
        self.assertFalse(conditions.has(a,'poison'));self.assertEqual(a['fury'],1)
        self.assertTrue(any(e.get('kind')=='cleanse' for e in b['animation_events']))

    def test_brace_second_wind_and_victory_strike(self):
        b,a,t=self.fixture();a['hp']=40
        self.cast(b,a,a,'job:fighter:brace');combat._deal_damage(b,t,a)
        self.assertEqual(a['hp'],25)
        a['acted']=False
        self.cast(b,a,a,'job:fighter:second_wind');self.assertEqual(a['hp'],75)
        a['acted']=False
        self.assertFalse(abilities.availability(a,a['skills'][0])['available'])
        t['hp']=30
        self.cast(b,a,t,'job:fighter:victory_strike');self.assertEqual(a['hp'],85)

    def test_groundbreaker_hits_diagonal_enemies_spends_fury_and_spares_allies(self):
        b,a,t=self.fixture();a.update(fury=4,hp=30);t.update(x=3,y=3,hp=100)
        ally={**t,'id':'ally','team':'player','x':1,'y':2};b['units']['ally']=ally
        for u in b['units'].values():
            if u['id'] not in (a['id'],t['id'],'ally'):u.update(x=7,y=7)
        self.cast(b,a,a,'job:barbarian:groundbreaker')
        self.assertEqual((t['hp'],a['fury'],ally['hp']),(60,0,100))
        self.assertNotEqual((t['x'],t['y']),(3,3))
        self.assertTrue(any(e['type']=='ground_impact' for e in b['animation_events']))

    def test_brace_and_wind_reject_ally_target(self):
        b,a,t=self.fixture()
        for key in ('brace','second_wind'):
            ally={**a,'id':'ally','hp':10};b['units']['ally']=ally
            with self.assertRaisesRegex(ValueError,'Target yourself'):
                self.cast(b,a,ally,'job:fighter:'+key)

    def test_barbarian_migration_preserves_loadout_and_earned_unlocks(self):
        c={'job_id':'barbarian','learned_skills':['job:barbarian:shove','job:barbarian:drive'],
           'equipped_skills':['job:barbarian:shove'],'job_practice':16}
        jobs.initialize(c)
        self.assertEqual(c['equipped_skills'],['job:barbarian:reckless_blow'])
        self.assertIn('job:barbarian:unstoppable',c['learned_skills'])
        before=deepcopy(c);jobs.initialize(c);self.assertEqual(c,before)

    def test_fury_and_passive_state_survive_save_and_views_do_not_tick(self):
        b,a,t=self.fixture(('bloodfury',));a['fury']=4
        restored=json.loads(json.dumps(b));before=deepcopy(restored)
        for _ in range(3):combat.battle_view(restored)
        self.assertEqual(restored,before)

    def test_death_defiance_does_not_prevent_nonlethal_capture(self):
        b,a,t=self.fixture(('too_angry_to_fall',));a['hp']=1
        combat._deal_damage(b,t,a,intent='nonlethal')
        self.assertFalse(a['conscious'])
        self.assertEqual(a['condition'],'unconscious')
        self.assertFalse(a.get('angry_used',False))

    def test_groundbreaker_wall_occlusion_and_physical_presentation(self):
        b,a,t=self.fixture();a['fury']=4;t.update(x=3,y=2)
        b['terrain']=[{'id':'wall','x':2,'y':2,'blocking':True,'blocks_sight':True,'edge_wall':True,'wall_edges':['east']}]
        before=t['hp'];self.cast(b,a,a,'job:barbarian:groundbreaker')
        self.assertEqual(t['hp'],before)
        sounds=[c['name'] for e in b['animation_events'] if e['type']=='sound' for c in e['cues']]
        self.assertIn('barbarian_groundbreaker',sounds)
        self.assertNotIn('magic_cast',sounds)

    def test_brace_expires_after_three_owner_turns_and_second_wind_has_own_effect(self):
        b,a,t=self.fixture();a.update(status_version=1,status_activation=[1,0])
        self.cast(b,a,a,'job:fighter:brace')
        conditions.finish_activation(a)
        self.assertTrue(conditions.has(a,'brace_defense'))
        for i in range(2,5):
            a['status_activation']=[i,0];conditions.finish_activation(a)
        self.assertFalse(conditions.has(a,'brace_defense'))
        a.update(acted=False,hp=1)
        self.cast(b,a,a,'job:fighter:second_wind')
        self.assertEqual(a['hp'],51)
        self.assertTrue(any(e.get('skill')=='second_wind' for e in b['animation_events']))
