import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_abilities as abilities, combat_conditions as conditions, combat_monk as monk, job_loadouts as jobs
from backend.game import new_game
from tests import test_combat_abilities as fixtures


class MonkJobTests(unittest.TestCase):
    def fixture(self,passives=()):
        b,a,t=fixtures.AbilityFoundationTests().fixture('fighter')
        b.update(units={a['id']:a,t['id']:t},objects={},zones=[],terrain=[],ground_tiles=[],decorations=[])
        a.update(attack=20,job_id='monk',armor=0,evasion=0,perk_modifiers={},gear_rules={},element=None,on_hit=None,
                 capture_weapon=None,attack_elevation_rule='melee',statuses=[],reactions=[],
                 passives=[deepcopy(jobs.SKILLS['job:monk:'+p]) for p in passives])
        t.update(armor=0,evasion=0,perk_modifiers={},gear_rules={},element=None,on_hit=None,statuses=[],reactions=[],
                 attack_elevation_rule='melee',race='Human')
        return b,a,t

    def cast(self,b,a,t,key,hits=None):
        s=deepcopy(jobs.SKILLS['job:monk:'+key]);a['skills']=[s]
        if hits is None:return combat._resolve_ability(b,a,t,s)
        rolls=[(hit,{'chance':100,'damage_bonus':0},1 if hit else 100) for hit in hits]
        with patch('backend.combat._attack_hits',side_effect=rolls):return combat._resolve_ability(b,a,t,s)

    def turn(self,b,a):
        a['ability_activation']+=1;a['acted']=False;monk.start_activation(b,a)

    def test_full_chain_at_start_and_eight_choices(self):
        state=new_game({'starting_role':'monk'});c=state['characters'][0]
        self.assertEqual(len([s for s in jobs.SKILLS if s.startswith('job:monk:')]),8)
        self.assertEqual(c['equipped_skills'],['job:monk:rapid_palm','job:monk:iron_reversal','job:monk:heaven_piercing'])
        self.assertEqual(len(jobs.snapshot(c)[0]),3)

    def test_multi_hit_shares_armor_bonus_and_barrier_budgets(self):
        b,a,t=self.fixture();t['armor']=6;conditions.barrier(t,10,2,t)
        result=self.cast(b,a,t,'rapid_palm',[True,True,True])
        self.assertEqual(t['hp'],90);self.assertEqual(result['hits'],3)
        self.assertFalse(conditions.has(t,'barrier'))
        feedback=[e for e in b['animation_events'] if e.get('kind')=='physical']
        self.assertEqual([(e['amount'],e['absorbed']) for e in feedback],[(0,6),(3,4),(7,0)])
        self.assertEqual(a['combat_record']['total_damage'],10)
        b,a,t=self.fixture();a['perk_modifiers']['melee_damage']=6;t['armor']=6
        self.cast(b,a,t,'rapid_palm',[True,True,True]);self.assertEqual(t['hp'],73)

    def test_partial_hits_have_only_their_allocated_damage(self):
        b,a,t=self.fixture();t['armor']=6
        self.cast(b,a,t,'rapid_palm',[True,False,True]);self.assertEqual(t['hp'],87)
        self.assertEqual(monk.readiness(a)['stage'],'follow_up')
        b,a,t=self.fixture();t['armor']=100
        self.cast(b,a,t,'rapid_palm',[True,True,True]);self.assertEqual(t['hp'],99)

    def test_proc_and_reaction_only_once_per_technique(self):
        b,a,t=self.fixture();a['on_hit']={'id':'poison','turns':2,'chance':100}
        with patch('backend.combat._react_after_attack') as reaction:
            self.cast(b,a,t,'rapid_palm',[False,True,True])
        self.assertEqual(b['proc_counter'],1);self.assertTrue(conditions.has(t,'poison'))
        reaction.assert_called_once()

    def test_lethal_punch_stops_sequence_and_advances_combo(self):
        b,a,t=self.fixture();t['hp']=1
        with patch('backend.combat_monk.random.Random') as rng:
            rng.return_value.randint.return_value=1
            self.cast(b,a,t,'rapid_palm',[True])
        self.assertEqual(monk.readiness(a)['stage'],'follow_up')
        self.assertEqual(len([e for e in b['animation_events'] if e['type']=='melee_attack']),1)
        self.assertEqual(a['combat_record']['kills'],1)

    def test_combo_next_turn_two_turn_window_and_missed_followup(self):
        b,a,t=self.fixture();self.cast(b,a,t,'rapid_palm',[True,True,True])
        follow=jobs.SKILLS['job:monk:iron_reversal'];a['acted']=False
        self.assertIn('next turn',abilities.availability(a,follow)['reason'])
        self.turn(b,a);self.assertTrue(abilities.availability(a,follow)['available'])
        self.cast(b,a,t,'iron_reversal',[False]);self.assertEqual(monk.readiness(a)['stage'],'follow_up')
        self.turn(b,a);self.assertTrue(abilities.availability(a,follow)['available'])
        monk.cleanup(b,a);self.assertEqual(monk.readiness(a)['stage'],'neutral')

    def test_offensive_followup_and_source_owned_expiry(self):
        b,a,t=self.fixture();self.cast(b,a,t,'rapid_palm',[True,True,True]);self.turn(b,a)
        self.cast(b,a,t,'breaking_combination',[True,True]);self.assertTrue(conditions.has(t,'open_guard'))
        for _ in range(4):conditions.finish_activation(t)
        self.assertTrue(conditions.has(t,'open_guard'))
        self.turn(b,a);self.assertTrue(conditions.has(t,'open_guard'))
        self.cast(b,a,t,'heaven_piercing',[True]);self.assertEqual(t['hp'],0)
        monk.cleanup(b,a);self.assertFalse(conditions.has(t,'open_guard'))
        self.assertEqual(monk.readiness(a)['stage'],'neutral')

    def test_open_guard_excludes_ticks_collision_and_falls(self):
        b,a,t=self.fixture();monk._status(t,'open_guard',monk.clock(a)+1,a)
        self.assertEqual(combat._damage_before_barrier(b,a,deepcopy(t)),25)
        for key in ('status_tick','collision_attack','environmental_fall'):
            self.assertEqual(combat._damage_before_barrier(b,{**a,key:True},deepcopy(t)),20)
        a['extracted']=True;monk.cleanup(b);self.assertFalse(conditions.has(t,'open_guard'))

    def test_iron_reversal_whole_technique_and_expiry(self):
        b,a,t=self.fixture();monk._status(t,'iron_reversal',monk.clock(t)+1,t)
        self.cast(b,a,t,'rapid_palm',[True,True,True]);self.assertEqual(t['hp'],79)
        self.assertFalse(conditions.has(t,'iron_reversal'))
        b,a,t=self.fixture();monk._status(a,'iron_reversal',monk.clock(a)+1,a)
        monk.start_activation(b,a);self.assertFalse(conditions.has(a,'iron_reversal'))

    def test_perfect_rhythm_matches_preview_and_finisher_roll(self):
        b,a,t=self.fixture(('perfect_rhythm',));t['evasion']=50
        self.cast(b,a,t,'rapid_palm',[True,True,True]);self.turn(b,a)
        s=jobs.SKILLS['job:monk:iron_reversal'];self.assertEqual(combat._attack_preview(b,a,t,'melee',s)['chance'],80)
        self.cast(b,a,t,'iron_reversal',[True]);self.turn(b,a)
        conditions.apply(a,'blind',2,t);s=jobs.SKILLS['job:monk:heaven_piercing']
        self.assertEqual(combat._strike_preview(b,a,t,'melee',3,s)['chance'],100)
        for _ in range(10):self.assertTrue(combat._attack_hits(b,a,t,'melee',s)[0])

    def test_flowing_footwork_evasion_and_next_turn_move(self):
        b,a,t=self.fixture(('flowing_footwork',));self.cast(b,a,t,'rapid_palm',[True,True,True])
        self.assertEqual(monk.movement_bonus(a),0);self.assertEqual(monk.evasion_bonus(a),10)
        self.assertEqual(combat._attack_preview(b,t,a,'melee')['chance'],94)
        self.assertEqual(combat._attack_preview(b,t,a,'ballistic')['chance'],80)
        self.turn(b,a);self.assertEqual(combat._movement_limit(a),4)
        monk.cleanup(b,a);self.assertEqual(combat._movement_limit(a),3)
        self.assertEqual(monk.evasion_bonus(a),0)

    def test_state_reconnect_and_inspection_are_read_only(self):
        b,a,t=self.fixture();self.cast(b,a,t,'rapid_palm',[True,True,True])
        b=json.loads(json.dumps(b));before=deepcopy(b)
        for _ in range(3):view=combat.battle_view(b)
        self.assertEqual(b,before);self.assertEqual(view['units'][a['id']]['combo']['stage'],'follow_up')

    def test_restart_failure_consumes_old_stage_finisher_miss_consumes(self):
        b,a,t=self.fixture();self.cast(b,a,t,'rapid_palm',[True,True,True]);self.turn(b,a)
        self.cast(b,a,t,'crushing_fist',[False]);self.assertEqual(monk.readiness(a)['stage'],'neutral')
        self.turn(b,a);self.cast(b,a,t,'rapid_palm',[True,True,True]);self.turn(b,a)
        self.cast(b,a,t,'iron_reversal',[True]);self.turn(b,a)
        self.cast(b,a,t,'heaven_piercing',[False]);self.assertEqual(monk.readiness(a)['stage'],'neutral')

    def test_dash_crosses_enemy_and_lands_empty_without_combo(self):
        b,a,t=self.fixture();landing=combat._ground_target(5,2)
        with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            self.cast(b,a,landing,'sweeping_dash')
        self.assertEqual((a['x'],a['y']),(5,2));self.assertEqual(t['hp'],90)
        self.assertEqual(monk.readiness(a)['stage'],'neutral')
        self.assertEqual(sum(e['type']=='movement' and e.get('dash',False) for e in b['animation_events']),1)

    def test_dash_invalid_landings_and_walls_fail_without_costs(self):
        b,a,t=self.fixture();s=jobs.SKILLS['job:monk:sweeping_dash']
        with self.assertRaises(ValueError):combat._resolve_ability(b,a,combat._ground_target(t['x'],t['y']),s)
        b['terrain']=[{'id':'wall','kind':'wall','x':3,'y':2,'blocking':True}]
        before=deepcopy(b)
        with self.assertRaises(ValueError):combat._resolve_ability(b,a,combat._ground_target(5,2),s)
        self.assertEqual(b,before)
        b['terrain']=[];b['void_tiles']=[{'x':3,'y':2,'kind':'lethal','pit_type':'lethal'}]
        self.assertNotIn((5,2),combat._dash_routes(b,a))

    def test_dash_counts_every_committed_burning_cell_and_previews_are_free(self):
        b,a,t=self.fixture();cells=[{'x':x,'y':2} for x in (3,4,5)]
        combat.spaces.place_zone(b,t,{'zone':'ember','turns':2},cells)
        before=deepcopy(b);self.assertEqual(combat._dash_ground_damage(b,a,[(3,2),(4,2),(5,2)]),12)
        self.assertEqual(b,before)
        with patch('backend.combat._attack_hits',return_value=(False,{'chance':100,'damage_bonus':0},100)):
            self.cast(b,a,combat._ground_target(5,2),'sweeping_dash')
        self.assertEqual(a['hp'],88)
        damage=[e for e in b['animation_events'] if e.get('kind')=='burn']
        self.assertEqual([e['ground_step'] for e in damage],[1,2,3])

    def test_dash_ground_preview_reports_route_and_visible_targets(self):
        b,a,t=self.fixture();a['skills']=[deepcopy(jobs.SKILLS['job:monk:sweeping_dash'])]
        before=deepcopy(b);view=combat.battle_view(b)
        self.assertEqual(b,before)
        preview=view['ground_skill_previews']['job:monk:sweeping_dash']['5,2']
        self.assertIn(t['id'],preview['target_forecasts']);self.assertEqual(preview['ground_damage'],0)
        self.assertEqual(preview['landing'],{'x':5,'y':2})

    def test_dash_preview_keeps_hidden_enemy_out_of_forecasts(self):
        b,a,t=self.fixture();a['skills']=[deepcopy(jobs.SKILLS['job:monk:sweeping_dash'])]
        t['spotted']=False;b['decorations'].append({'kind':'bush','x':t['x'],'y':t['y']})
        view=combat.battle_view(b)
        self.assertNotIn(t['id'],view['units'])
        for preview in view['ground_skill_previews']['job:monk:sweeping_dash'].values():
            self.assertNotIn(t['id'],preview.get('target_forecasts',{}))
        self.assertFalse(t['spotted'])

    def test_unstoppable_can_remove_open_guard_on_application(self):
        b,a,t=self.fixture();t['fury']=1;t['passives']=[{'id':'job:barbarian:unstoppable'}]
        a['monk_combo']={'stage':'follow_up','available_at':0,'expires_at':2}
        monk.complete_technique(b,a,t,jobs.SKILLS['job:monk:breaking_combination'],1,'test')
        self.assertFalse(combat.conditions.has(t,'open_guard'));self.assertEqual(t['fury'],0)
        self.assertTrue(any(e.get('kind')=='cleanse' for e in b['animation_events']))

    def test_old_monk_loadout_migration_preserves_earned_skills_and_order(self):
        c={'job_id':'monk','job_practice':9,'learned_skills':['job:monk:'+s for s in jobs.MONK_OLD_IDS],
           'equipped_skills':['job:monk:palm','job:monk:brace','job:monk:riposte'],
           'combat_skill_order':['job:monk:brace','job:monk:palm']}
        jobs.initialize(c);before=deepcopy(c);jobs.initialize(c);self.assertEqual(c,before)
        self.assertEqual(c['job_practice'],9);self.assertIn('job:monk:flowing_footwork',c['learned_skills'])
        self.assertIn('job:monk:heaven_piercing',c['equipped_skills'])
        self.assertEqual(c['combat_skill_order'],['job:monk:iron_reversal','job:monk:rapid_palm'])
        jobs.snapshot(c)

    def test_auto_battle_uses_combo_stage_and_respects_gates(self):
        b,a,t=self.fixture();a['skills']=[deepcopy(jobs.SKILLS[k]) for k in jobs.JOBS['monk']['starter_skills']]
        with patch('backend.combat._finish_turn'),patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            self.assertTrue(combat._auto_monk_turn(b,a,[t]));self.assertEqual(monk.readiness(a)['stage'],'follow_up')
            self.turn(b,a);self.assertTrue(combat._auto_monk_turn(b,a,[t]));self.assertEqual(monk.readiness(a)['stage'],'finisher')
            self.turn(b,a);self.assertTrue(combat._auto_monk_turn(b,a,[t]));self.assertEqual(monk.readiness(a)['stage'],'neutral')


    def test_exposure_caps_refreshes_and_adds_to_open_guard(self):
        b,a,t=self.fixture()
        self.cast(b,a,t,'rapid_palm',[True,True,True])
        status=next(s for s in t['statuses'] if s['id']=='palm_exposure')
        self.assertEqual(status['stacks'],3);self.assertEqual(status['turns'],3)
        status['turns']=1;monk.add_exposure(b,a,t,1)
        self.assertEqual(next(s for s in t['statuses'] if s['id']=='palm_exposure')['turns'],3)
        monk._status(t,'open_guard',1,a)
        self.assertEqual(monk.incoming(t,a,100),155)
        self.assertEqual(monk.incoming(t,{'status_tick':True},100),100)
        for turn in range(3):
            t['status_activation']=[1,turn+10];conditions.finish_activation(t)
        self.assertFalse(conditions.has(t,'palm_exposure'))

    def test_reversal_evasion_only_affects_struck_enemy_and_expires(self):
        b,a,t=self.fixture();a['monk_combo']={'stage':'follow_up','available_at':0,'expires_at':2}
        self.cast(b,a,t,'iron_reversal',[True])
        self.assertEqual(monk.evasion_against(a,t),25)
        self.assertEqual(monk.evasion_against(a,{'id':'other'}),0)
        self.assertEqual(combat._attack_preview(b,t,a,'melee')['chance'],85)
        self.turn(b,a);self.assertEqual(monk.evasion_against(a,t),0)

    def test_rhythm_heals_each_landed_punch_but_not_misses_or_collision(self):
        b,a,t=self.fixture();a['hp']=50
        monk._status(a,'monk_siphon',monk.clock(a)+3,a)
        self.cast(b,a,t,'rapid_palm',[True,False,True]);self.assertEqual(a['hp'],56)
        monk.landed_attack(b,dict(a,collision_attack=True));self.assertEqual(a['hp'],56)
        for _ in range(3):self.turn(b,a);monk.cleanup(b,a)
        self.assertFalse(conditions.has(a,'monk_siphon'))

    def test_rhythm_dash_counts_each_enemy_and_no_overheal(self):
        b,a,t=self.fixture();a['hp']=96
        other=deepcopy(t);other.update(id='other',x=4,y=2);b['units']['other']=other
        monk._status(a,'monk_siphon',3,a)
        with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            self.cast(b,a,combat._ground_target(5,2),'sweeping_dash')
        self.assertEqual(a['hp'],100);self.assertTrue(conditions.has(a,'dash_parry'))
        self.turn(b,a);self.assertFalse(conditions.has(a,'dash_parry'))

    def test_parry_excludes_magic_elements_and_area_skills(self):
        b,a,t=self.fixture();monk._status(a,'dash_parry',1,a)
        self.assertEqual(combat._attack_preview(b,t,a,'melee')['chance'],90)
        self.assertEqual(combat._attack_preview(b,t,a,'ballistic')['chance'],81)
        self.assertEqual(monk.parry_rate(a,t,'ignore'),0)
        self.assertEqual(monk.parry_rate(a,dict(t,element='fire'),'melee'),0)
        self.assertEqual(monk.parry_rate(a,t,'melee',{'effects':[{'type':'area_attack'}]}),0)

    def test_crushing_fist_stun_follows_advancement_and_respects_recovery(self):
        b,a,t=self.fixture();skill=jobs.SKILLS['job:monk:crushing_fist']
        with patch('backend.combat_monk.random.Random') as rng:
            rng.return_value.randint.return_value=1
            monk.complete_technique(b,a,t,skill,1,1)
        self.assertTrue(conditions.has(t,'stun'))
        conditions.remove(t,'stun');t['control_immunity']=1
        with patch('backend.combat_monk.random.Random') as rng:
            rng.return_value.randint.return_value=1
            monk.complete_technique(b,a,t,skill,1,1)
        self.assertFalse(conditions.has(t,'stun'))

    def test_boss_resistances_are_selective_and_visible(self):
        b,a,t=self.fixture();t.update(boss=True,race='Goblin',kind='chieftain')
        self.assertEqual(conditions.status_chance(t,'stun'),75)
        self.assertEqual(conditions.status_chance(t,'stun',50),38)
        self.assertEqual(conditions.status_chance(t,'poison'),100)
        self.assertEqual(conditions.status_chance(t,'burn'),100)
        view=combat.battle_view(b);details=view['units'][t['id']]['resistance_details']
        self.assertEqual(details['statuses'],{'stun':25});self.assertEqual(details['control_duration_limit'],1)
        t.update(race='Automaton');self.assertEqual(conditions.status_chance(t,'poison'),0)
        t.update(race='Human',status_resistances={'poison':70})
        self.assertEqual(conditions.status_chance(t,'poison'),30)
        self.assertEqual(conditions.status_chance(t,'stun'),100)


if __name__=='__main__':unittest.main()
