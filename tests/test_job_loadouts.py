import json
import unittest
from copy import deepcopy
from backend import job_loadouts as jobs, combat
from backend.game import new_game, public_content
from tests import test_combat_abilities as fixtures


class JobLoadoutTests(unittest.TestCase):
    def state(self):
        return new_game({'name':'Tester'})

    def test_all_twelve_toolboxes_validate_and_snapshot_without_gear_changes(self):
        self.assertEqual(len(jobs.JOBS),12)
        for job,definition in jobs.JOBS.items():
            with self.subTest(job=job):
                state=self.state();before=deepcopy(state['characters'][0]);inventory=deepcopy(state['inventory'])
                jobs.update(state,'player',definition['starter_skills'],job)
                char=state['characters'][0];actives,passives,mods=jobs.snapshot(char)
                self.assertEqual((len(actives),len(passives)),(3,0) if job in {'monk','rogue','ranger'} else (2,1))
                self.assertEqual(char['equipment'],before['equipment']);self.assertEqual(state['inventory'],inventory)
                self.assertEqual(char['perks'],before['perks']);self.assertEqual(char['traits'],before['traits'])
                unit=combat._player_unit(state,char,2,2)
                self.assertEqual(len([s for s in unit['skills'] if s.get('source_kind')=='character']),3 if job in {'monk','rogue','ranger'} else 2)
                self.assertEqual(unit['passives'],passives)

    def test_legacy_and_champions_do_not_silently_gain_a_job(self):
        char=self.state()['characters'][0];jobs.initialize(char)
        self.assertIsNone(char['job_id']);self.assertEqual(jobs.snapshot(char),([],[],{}))
        champ={'id':'c','source_kind':'champion'};before=deepcopy(champ);jobs.initialize(champ)
        self.assertEqual(champ,before);self.assertEqual(jobs.snapshot(champ),([],[],{}))
        with self.assertRaises(ValueError):jobs.update({'characters':[champ]},'c',[],'mage')

    def test_shared_capacity_duplicates_and_unlearned_fail_atomically(self):
        state=self.state();ids=jobs.JOBS['fighter']['starter_skills'];jobs.update(state,'player',ids,'fighter')
        for invalid in [ids+ids, ['not-a-skill'], [jobs.JOBS['mage']['starter_skills'][0]], [None]]:
            before=deepcopy(state)
            with self.assertRaises(ValueError):jobs.update(state,'player',invalid)
            self.assertEqual(state,before)
        char=state['characters'][0];char['learned_skills']=list(jobs.SKILLS)[:6]
        with self.assertRaisesRegex(ValueError,'five'):jobs.update(state,'player',char['learned_skills'])
        jobs.update(state,'player',char['learned_skills'][:5]);self.assertEqual(len(jobs.snapshot(char)[0])+len(jobs.snapshot(char)[1]),5)

    def test_busy_assignment_and_job_switch_protection(self):
        state=self.state();char=state['characters'][0]
        for field,value in [('status','mission'),('status','incapacitated'),('assignment','training_1')]:
            char[field]=value;before=deepcopy(state)
            with self.assertRaises(ValueError):jobs.update(state,'player',[],'mage')
            self.assertEqual(state,before);char.update(status='idle',assignment=None)
        jobs.update(state,'player',jobs.JOBS['mage']['starter_skills'],'mage')
        with self.assertRaises(ValueError):jobs.update(state,'player',[],'engineer')

    def test_saved_battle_kit_does_not_follow_later_loadout_edits(self):
        state=self.state();ids=jobs.JOBS['fighter']['starter_skills'];jobs.update(state,'player',ids,'fighter')
        unit=combat._player_unit(state,state['characters'][0],2,2);before=deepcopy(unit)
        jobs.update(state,'player',[])
        self.assertEqual(unit,before);self.assertEqual(json.loads(json.dumps(unit)),unit)
        empty=combat._player_unit(state,state['characters'][0],2,2)
        self.assertEqual(empty['passives'],[]);self.assertFalse(any(s.get('source_kind')=='character' for s in empty['skills']))

    def test_passive_removal_changes_real_combat_stats(self):
        state=self.state();char=state['characters'][0];base=combat._player_unit(state,char,2,2)
        jobs.update(state,'player',jobs.JOBS['mage']['starter_skills'],'mage')
        self.assertEqual(combat._player_unit(state,char,2,2)['evasion'],base['evasion']+5)
        jobs.update(state,'player',[])
        self.assertEqual(combat._player_unit(state,char,2,2)['evasion'],base['evasion'])

    def test_auto_deploys_and_does_not_redeploy_while_capacity_full(self):
        b,a,t=fixtures.AbilityFoundationTests().fixture('mage')
        a['skills']=[deepcopy(jobs.SKILLS[jobs.JOBS['summoner']['starter_skills'][1]])]
        self.assertTrue(combat._auto_support(b,a))
        self.assertEqual(len([u for u in b['units'].values() if u.get('temporary')]),2)
        a['acted']=False;a['ability_activation']+=3
        self.assertFalse(combat._auto_support(b,a))

    def test_catalog_copies_cannot_mutate_definitions(self):
        catalog=public_content()['job_loadouts'];catalog['jobs']['mage']['starter_skills'].clear()
        self.assertEqual(len(jobs.JOBS['mage']['starter_skills']),3)


if __name__=='__main__':unittest.main()
