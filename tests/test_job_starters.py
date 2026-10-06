import json
import random
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from backend import combat, job_loadouts as jobs
from backend.game import new_game, normalize_state, resolve_mission, analyze_mission
from backend.content import ITEMS, MISSION_TEMPLATES
from backend.starter_equipment import STARTING_ROLES
from backend.economy import trade_view
from backend.inventory import sale_price
from tests import test_combat_abilities as fixtures


class JobStarterTests(unittest.TestCase):
    def test_rookie_creature_is_not_a_chieftain_with_boss_capture_resistance(self):
        state=new_game({'starting_role':'captor'})
        b=combat.create_battle(state,['player'],'starter-smoke','contract:rats_storehouse')
        rat=b['units']['contract_enemy_0'];actor=b['units']['player']
        self.assertFalse(rat['boss']);self.assertEqual(rat['kind'],'creature')
        self.assertGreater(combat._capture_preview(b,actor,rat)['chance'],2)

    def test_starters_can_auto_resolve_the_early_storehouse_without_door_stalls(self):
        for job in jobs.JOBS:
            with self.subTest(job=job):
                state=new_game({'starting_role':job})
                b=combat.create_battle(state,['player'],'starter-smoke','contract:rats_storehouse')
                v=combat.auto_resolve(b,max_steps=24)
                self.assertEqual(v['status'],'complete')
                # Capture remains chance-based; victory is not guaranteed by Job.
                self.assertIn(v['outcome'],{'success','critical_success','failure','critical_failure'})

    def test_all_jobs_start_with_their_skills_and_correct_weapon_profile(self):
        self.assertEqual(set(STARTING_ROLES),set(jobs.JOBS))
        self.assertNotIn('medic',STARTING_ROLES)
        for job,definition in STARTING_ROLES.items():
            with self.subTest(job=job):
                state=new_game({'starting_role':job});char=state['characters'][0]
                self.assertEqual(char['job_id'],job);self.assertEqual(char['job_practice'],0)
                self.assertEqual(char['learned_skills'],jobs.JOBS[job]['starter_skills'])
                self.assertEqual(char['equipped_skills'],char['learned_skills'])
                actor=combat._player_unit(state,char,2,2)
                self.assertGreater(actor['attack'] if job!='captor' else actor['capture_attributes']['str'],0)
                if job=='captor':self.assertGreater(actor['attack'],0);self.assertTrue(actor['capture_weapon'])
                if job in {'rogue','monk'}:self.assertEqual((actor['scaling'],actor['attack_range']),('dex',1))
                if job in {'mage','cleric','bard','druid','summoner'}:self.assertEqual((actor['scaling'],actor['attack_range']),('int',3))
                for iid in definition['kit']:
                    self.assertLessEqual(ITEMS[iid].get('power',0),1)
                    icon=ITEMS[iid].get('icon');self.assertTrue((Path('frontend/public')/icon.lstrip('/')).is_file(),icon)
        self.assertEqual(len(jobs.SKILLS),83)

    def test_matching_gear_available_without_resale_profit(self):
        state=new_game({'starting_role':'engineer'});offers={o['item']:o for o in trade_view(state,'qa',100)['camp_items']}
        for role in STARTING_ROLES.values():
            for iid in role['kit']:self.assertIn(iid,offers);self.assertGreater(offers[iid]['price'],sale_price(iid))

    def test_unlock_pacing_is_idempotent_and_does_not_change_equipped_slots_or_stats(self):
        for job in jobs.JOBS:
            with self.subTest(job=job):
                state=new_game({'starting_role':job});char=state['characters'][0]
                original=deepcopy(char)
                for i in range(1,10):
                    result=jobs.credit_contract(state,['player'],'success',f'mission:{i}')
                    self.assertEqual(len(char['learned_skills']),3+sum(i>=n for n in (2,5,9)))
                    self.assertEqual(jobs.credit_contract(state,['player'],'success',f'mission:{i}'),[])
                for key in ('equipped_skills','attributes','equipment','traits','perks','skill_slots'):
                    self.assertEqual(char[key],original[key])
                self.assertEqual(char['job_practice'],9)
                restored=json.loads(json.dumps(state));normalize_state(restored)
                self.assertEqual(restored['characters'][0]['learned_skills'],char['learned_skills'])

    def test_failure_debug_and_nonparticipants_receive_no_practice(self):
        state=new_game({'starting_role':'mage'});before=deepcopy(state)
        for outcome in ('failure','critical_failure'):self.assertEqual(jobs.credit_contract(state,['player'],outcome,'fail'),[])
        self.assertEqual(jobs.credit_contract(state,['player'],'success','debug',debug=True),[])
        self.assertEqual(jobs.credit_contract(state,[],'success','other'),[])
        self.assertEqual(state,before)
        jobs.credit_contract(state,['player'],'critical_success','critical');self.assertEqual(state['characters'][0]['job_practice'],1)

    def test_actual_roll_resolution_awards_once_and_does_not_train_roll_bodyguards(self):
        state=new_game({'starting_role':'fighter'})
        guard=deepcopy(state['characters'][0]);guard.update(id='guard',name='Guard',is_player=False);state['characters'].append(guard)
        mission=next(m for m in MISSION_TEMPLATES.values() if m['rank']=='E' and m.get('slots',1)==1)
        analysis=analyze_mission(state,mission,['player']);analysis['bodyguard_ids']=['guard']
        result=resolve_mission(state,mission,['player'],analysis,'job-resolution',forced_outcome='success')
        self.assertEqual(result['job_progress'][0]['practice'],1)
        self.assertEqual(guard['job_practice'],0)
        resolve_mission(state,mission,['player'],analysis,'job-resolution',forced_outcome='success')
        self.assertEqual(state['characters'][0]['job_practice'],1)

    def test_legacy_equipment_and_manual_loadouts_are_preserved(self):
        state=new_game({'traits':['medic']});char=state['characters'][0];char.pop('job_id')
        before=deepcopy(char);normalize_state(state)
        self.assertIsNone(char['job_id']);self.assertEqual(char['equipment'],before['equipment'])
        jobs.update(state,'player',jobs.JOBS['cleric']['starter_skills'],'cleric')
        jobs.update(state,'player',[]);normalize_state(state)
        self.assertEqual(char['equipped_skills'],[])

    def test_bard_regeneration_is_a_legal_support_action(self):
        b,a,t=fixtures.AbilityFoundationTests().fixture('mage')
        skill=jobs.SKILLS['job:bard:refrain'];a['skills']=[deepcopy(skill)];a['hp']=30
        self.assertTrue(combat._support_eligible(b,a,a,combat._support_effect(skill,a)))
        combat._resolve_ability(b,a,a,skill)
        self.assertTrue(any(s['id']=='regeneration' for s in a['statuses']))

    def test_auto_uses_commanded_unit_without_extra_owner_attack(self):
        b,a,t=fixtures.AbilityFoundationTests().fixture('mage')
        a['skills']=[];a['attack']=1
        entity=combat.entities.deploy(b,a,'companion',combat._deployment_positions(b,a,'companion'))[0]
        a['ability_activation']+=1;entity['acted']=False
        with patch('backend.combat._finish_turn'),patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            self.assertTrue(combat._auto_commanded_entity(b,a,'balanced'))
        self.assertTrue(a['acted']);self.assertTrue(entity['acted']);self.assertGreater(a['combat_record']['total_damage'],0)
        self.assertEqual(len(b['turn_order']),2)


if __name__=='__main__':unittest.main()
