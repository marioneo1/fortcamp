"""Resolved Fighter facts: presentation must follow real skill/reaction outcomes."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from tests import test_combat_impact as impacts
from backend import combat, job_loadouts, combat_conditions as conditions


class FighterPresentationTests(unittest.TestCase):
    def fixture(self):
        b,a,t=impacts.CombatImpactTests().fixture()
        a.update(attack=12,attack_elevation_rule='melee',attack_range=1,armor=0)
        t.update(status_version=1,displacement_resistance=0,knockback_resistance=0)
        return b,a,t

    def skill(self,key):
        return deepcopy(job_loadouts.SKILLS['job:fighter:'+key])

    def use(self,b,a,t,key):
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            return combat._resolve_ability(b,a,t,self.skill(key))

    def test_driving_strike_has_attack_contact_collision_and_final_cell(self):
        b,a,t=self.fixture();b['terrain']=[{'id':'wall','x':4,'y':2,'blocking':True}]
        self.use(b,a,t,'bash')
        events=b['animation_events']
        hit=next(e for e in events if e['type']=='melee_attack')
        collision=next(e for e in events if e.get('kind')=='collision')
        self.assertEqual(collision['amount'],6)
        self.assertEqual(hit['attack_packet'],collision['attack_packet'])
        self.assertEqual((t['x'],t['y']),(3,2))
        self.assertTrue(any(e['type']=='collision_recoil' for e in events))

    def test_break_formation_is_a_real_melee_attack_and_currently_hits_caster(self):
        b,a,t=self.fixture();before=a['hp']
        self.use(b,a,t,'pull')
        events=b['animation_events']
        self.assertTrue(any(e['type']=='melee_attack' and e['target_id']==t['id'] for e in events))
        self.assertEqual(a['hp'],before-6)
        self.assertEqual((t['x'],t['y']),(3,2))
        recoil=next(e for e in events if e['type']=='collision_recoil')
        self.assertEqual(recoil['bystander_id'],a['id'])
        self.assertEqual(len([e for e in events if e.get('kind')=='collision']),2)

    def test_cover_and_hold_together_report_only_real_protection(self):
        for key,capacity in [('cover',10),('rally',12)]:
            with self.subTest(key=key):
                b,a,t=self.fixture();t['team']=a['team'];conditions.apply(t,'fear',2,a)
                self.use(b,a,t,key)
                shield=next(s for s in t['statuses'] if s['id']=='barrier')
                self.assertEqual(shield['amount'],capacity)
                kinds=[e['kind'] for e in b['animation_events'] if e['type']=='combat_feedback']
                self.assertIn('barrier',kinds)
                self.assertEqual('cleanse' in kinds,key=='rally')
                self.assertEqual(t['hp'],100)

    def test_intercept_has_named_feedback_and_redirects_actual_damage(self):
        b,a,t=self.fixture();ally=deepcopy(a);ally.update(id='protected',x=2,y=3,reactions=[]);t.update(x=3,y=3)
        b['units'][ally['id']]=ally;a['reactions']=[self.skill('intercept')['reaction']]
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            recipient,*_=combat._perform_attack(b,t,ally,'melee')
        self.assertEqual(recipient['id'],a['id']);self.assertEqual(ally['hp'],100)
        self.assertTrue(any(e.get('kind')=='intercept' and e['unit_id']==a['id'] for e in b['animation_events']))

    def test_riposte_has_its_own_attack_packet_and_counter_cue(self):
        b,a,t=self.fixture();a['reactions']=[self.skill('riposte')['reaction']]
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            combat._perform_attack(b,t,a,'melee')
        attacks=[e for e in b['animation_events'] if e['type']=='melee_attack']
        self.assertEqual(len(attacks),2)
        self.assertNotEqual(attacks[0]['attack_packet'],attacks[1]['attack_packet'])
        cue=next(e for e in b['animation_events'] if e.get('kind')=='counter')
        self.assertEqual(cue['attack_packet'],attacks[1]['attack_packet'])


if __name__=='__main__':unittest.main()
