import unittest
from copy import deepcopy
from unittest.mock import patch
from fastapi import HTTPException
from backend.combat_melee import weapon_style, attack_style, impact_surface, armor_material
from backend.combat import _perform_attack, _capture_attempt
from backend.battle_lab import JobTester, job_test_party
from backend.content import ITEMS
from tests import test_combat_abilities as foundation

class MeleePresentationTests(unittest.TestCase):
    def test_profiles_and_authored_push_override(self):
        for kind,style in [('sword','slash'),('axe','hack'),('hammer','crush'),('club','blunt'),('unarmed','fist'),('spear','stab')]:
            self.assertEqual(weapon_style({'weapon_type':kind}),style)
        self.assertEqual(weapon_style({'weapon_type':'blade','weapon':'Rusty Knife','name':'Fighter'}),'stab')
        self.assertEqual(attack_style({'weapon_type':'sword'}, {'id':'job:fighter:bash'}),'blunt')

    def test_melee_delivery_does_not_change_damage_or_displace(self):
        results=[]
        for style in ['slash','hack','crush','blunt','fist','stab']:
            b,a,t=foundation.AbilityFoundationTests().fixture('fighter')
            a.update(melee_style=style,attack=20,element=None,on_hit=None)
            with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
                _perform_attack(b,a,t,'melee')
            results.append(t['hp'])
            event=next(e for e in b['animation_events'] if e['type']=='melee_attack')
            self.assertEqual(event['melee_style'],style)
            self.assertEqual((t['x'],t['y']),(3,2))
        self.assertEqual(len(set(results)),1)

    def test_net_capture_success_and_failure_are_nonlethal(self):
        for success in [True,False]:
            b,a,t=foundation.AbilityFoundationTests().fixture('captor')
            b['animation_events']=[]
            a.update(weapon='Frayed Capture Net',capture_weapon={'base_chance':10},attack_range=1,attack_elevation_rule='melee')
            with patch('backend.combat._capture_preview',return_value={'chance':100 if success else 0}):
                _capture_attempt(b,a,t)
            self.assertEqual(b['animation_events'][0]['type'],'net_cast')
            self.assertTrue(b['animation_events'][0]['hit'])
            self.assertEqual(b['animation_events'][0]['captured'],success)
            self.assertEqual(t['hp'],0) if success else self.assertLess(t['hp'],100)
            self.assertNotEqual(t['condition'],'dead')
            self.assertFalse(any(e.get('kind')=='physical' for e in b['animation_events']))
            self.assertTrue(any(e.get('kind')==('captured' if success else 'capture_failed') for e in b['animation_events']))

    def test_lab_weapon_choices_are_real_distinct_and_not_roster_edits(self):
        weapons=[key for key,item in ITEMS.items() if item.get('slot')=='weapon']
        state,party=job_test_party([JobTester(job_id='fighter',weapon_id=weapons[0]),JobTester(job_id='mage',weapon_id='unarmed')])
        self.assertEqual(len(party),2)
        a,c=state['characters']
        chosen=next(i for i in state['inventory'] if i['instance_id']==a['equipment']['weapon'])
        self.assertEqual(chosen['item_id'],weapons[0])
        self.assertNotIn('weapon',c['equipment'])
        with self.assertRaises(HTTPException):job_test_party([JobTester(job_id='fighter',weapon_id='invalid')])


    def test_contact_material_uses_actual_armor_and_anatomy_not_defense_stat(self):
        self.assertEqual(impact_surface({'race':'Human','armor':99,'armor_material':'leather'}),'flesh')
        self.assertEqual(impact_surface({'race':'Human','armor':0,'armor_material':'chain'}),'metal')
        self.assertEqual(impact_surface({'race':'Automaton','armor_material':'cloth'}),'metal')
        self.assertEqual(impact_surface({'race':'Golem'}),'rigid')
        self.assertEqual(armor_material({'name':'Steel Plate'}),'metal')
        self.assertEqual(armor_material({'name':'Chainmail Coat'}),'metal')
        self.assertEqual(armor_material({'name':'Worn Jacket'}),'cloth')
        self.assertEqual(armor_material({'name':'Thunderhide Coat','armor_material':'leather'}),'leather')

    def test_blunt_and_fist_kills_keep_collapse_without_blood_burst(self):
        for style in ['slash','hack','crush','blunt','fist','stab']:
            b,a,t=foundation.AbilityFoundationTests().fixture('fighter')
            a.update(melee_style=style,attack=1000);t.update(hp=1,race='Human',armor_material='cloth')
            with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):_perform_attack(b,a,t,'melee')
            death=next(e for e in b['animation_events'] if e['type']=='death_burst')
            self.assertEqual(bool(death.get('bloodless')),style in {'fist','blunt'})
            self.assertEqual(t['condition'],'dead')
