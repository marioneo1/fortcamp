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
        self.assertEqual(collision['amount'],9)
        self.assertEqual(hit['attack_packet'],collision['attack_packet'])
        self.assertEqual((t['x'],t['y']),(3,2))
        self.assertTrue(any(e['type']=='collision_recoil' for e in events))
        self.assertTrue(conditions.has(t,'stun'))

    def test_driving_person_collision_stuns_both_and_respects_immunity(self):
        for immune in (False,True):
            b,a,t=self.fixture()
            other=deepcopy(t);other.update(id='bystander',x=4,team=a['team'],control_immunity=2 if immune else 0)
            b['units'][other['id']]=other
            self.use(b,a,t,'bash')
            self.assertEqual((t['hp'],other['hp']),(73,91))
            self.assertTrue(conditions.has(t,'stun'))
            self.assertEqual(conditions.has(other,'stun'),not immune)

    def test_driving_armor_reduces_scaled_power_and_resisted_push_cannot_stun(self):
        b,a,t=self.fixture();t.update(armor=4,displacement_resistance=100)
        b['terrain']=[{'id':'wall','x':4,'y':2,'blocking':True}]
        self.use(b,a,t,'bash')
        self.assertEqual(t['hp'],86)
        self.assertFalse(conditions.has(t,'stun'))
        self.assertFalse(any(e.get('kind')=='collision' for e in b['animation_events']))

    def test_driving_open_ground_push_does_not_stun(self):
        b,a,t=self.fixture()
        self.use(b,a,t,'bash')
        self.assertEqual((t['x'],t['hp']),(4,82))
        self.assertFalse(conditions.has(t,'stun'))

    def test_driving_scaled_hit_still_respects_guard_and_barrier(self):
        b,a,t=self.fixture();t.update(armor=4,guarding=True)
        conditions.barrier(t,5,2,t)
        self.use(b,a,t,'bash')
        self.assertEqual(t['hp'],94) # (18-4)*75%, rounded up, then 5 shield.
        self.assertFalse(t['guarding'])

    def test_attack_forecast_matches_guard_armor_and_barrier_without_mutating_battle(self):
        b,a,t=self.fixture();t.update(armor=4,guarding=True)
        conditions.barrier(t,5,2,t);before=deepcopy(b)
        skill=self.skill('bash')
        preview=combat._strike_preview(b,a,t,'melee',1,skill)
        self.assertEqual(b,before)
        self.assertEqual(preview['damage_on_hit'],6)
        self.assertEqual(preview['absorbed_damage'],5)
        self.use(b,a,t,'bash')
        self.assertEqual(100-t['hp'],preview['damage_on_hit'])

    def test_forecast_uses_current_fractured_armor(self):
        b,a,t=self.fixture();t.update(armor=10)
        conditions.apply(t,'armor_fracture',2,a)
        preview=combat._strike_preview(b,a,t,'melee',1,self.skill('bash'))
        self.assertEqual(preview['damage_on_hit'],11)

    def test_ground_forecasts_match_each_visible_victim_and_do_not_mutate_battle(self):
        b,a,t=self.fixture();a.update(x=1,y=2,skills=[self.skill('pull')]);a['special']=a['skills'][0]
        t.update(x=4,y=2,armor=4)
        outer=deepcopy(t);outer.update(id='outer',x=5,armor=0);b['units']['outer']=outer
        before=deepcopy(b);view=combat.battle_view(b)
        forecasts=view['ground_skill_previews'][a['special']['id']]['3,2']['target_forecasts']
        self.assertEqual(b['units'],before['units'])
        self.assertEqual(forecasts[t['id']]['damage_on_hit'],20)
        self.assertEqual(forecasts['outer']['damage_on_hit'],24)
        self.assertEqual((forecasts[t['id']]['push'],forecasts['outer']['push']),(2,1))

    def test_chain_armor_fracture_does_not_stack_and_expires_after_two_turns(self):
        b,a,t=self.fixture();t.update(x=5,y=2,armor=11)
        self.use(b,a,t,'cover')
        self.assertEqual(t['hp'],99) # The hit precedes the armor reduction.
        self.assertEqual(combat._effective_armor(t),7)
        self.assertEqual(combat.battle_view(b)['units'][t['id']]['effective_armor'],7)
        conditions.apply(t,'armor_fracture',2,a)
        self.assertEqual(sum(s['id']=='armor_fracture' for s in t['statuses']),1)
        for turn,expected in ((1,7),(2,11)):
            t['status_activation']=turn;conditions.finish_activation(t)
            self.assertEqual(combat._effective_armor(t),expected)
        self.assertEqual(t['armor'],11)

    def test_chain_hits_pulls_and_halves_movement_without_hitting_caster(self):
        b,a,t=self.fixture();t.update(x=5,y=2,move=7);before=a['hp']
        self.use(b,a,t,'cover')
        self.assertEqual((t['x'],t['y']),(3,2))
        self.assertEqual(a['hp'],before)
        self.assertEqual(combat._movement_limit(t),3)
        self.assertTrue(conditions.has(t,'hobbled'))
        self.assertTrue(any(e['type']=='chain_attack' for e in b['animation_events']))
        self.assertFalse(any(e.get('kind')=='collision' for e in b['animation_events']))

    def test_chain_square_range_accepts_diagonal_three_cells_and_rejects_four(self):
        b,a,t=self.fixture();a['skills']=[self.skill('cover')];a['special']=a['skills'][0]
        t.update(x=a['x']+3,y=a['y']+3)
        view=combat.battle_view(b)
        preview=view['skill_previews'][a['special']['id']][t['id']]
        self.assertIsNotNone(preview);self.assertNotIn('move_to',preview)
        self.assertFalse(combat._can_attack(b,a,{'x':a['x']+4,'y':a['y']},3,'square'))

    def test_hook_stops_short_when_caster_would_be_the_next_cell(self):
        for x in (3,4):
            b,a,t=self.fixture();t.update(x=x,y=2)
            self.use(b,a,t,'cover')
            self.assertEqual(t['x'],3);self.assertEqual(a['hp'],100)
            self.assertFalse(any(e.get('kind')=='collision' for e in b['animation_events']))

    def test_rally_cleanses_all_nearby_fear_but_does_not_grant_barriers(self):
        b,a,t=self.fixture();t.update(team=a['team'],x=4,y=4)
        far=deepcopy(t);far.update(id='far',x=5,y=5);b['units']['far']=far
        for u in (a,t,far):conditions.apply(u,'fear',2,a)
        self.use(b,a,a,'rally')
        for u in (a,t):
            self.assertFalse(conditions.has(u,'fear'));self.assertFalse(conditions.has(u,'barrier'))
        self.assertTrue(conditions.has(far,'fear'))
        self.assertEqual(len([e for e in b['animation_events'] if e.get('kind')=='cleanse']),2)

    def test_leap_inner_hits_outer_enemy_then_outer_receives_its_own_impact(self):
        b,a,t=self.fixture();a.update(x=1,y=2);t.update(x=4,y=2,armor=0)
        outer=deepcopy(t);outer.update(id='outer',x=5);b['units']['outer']=outer
        self.use(b,a,combat._ground_target(3,2),'pull')
        self.assertEqual((a['x'],a['y']),(3,2))
        self.assertEqual(t['hp'],64) # 24 impact + 12 collision
        self.assertEqual(outer['hp'],64) # 12 from other body + 24 impact
        self.assertEqual((t['x'],outer['x']),(4,6))
        self.assertEqual(a['ability_state']['job:fighter:pull']['ready_at'],a.get('ability_activation',0)+5)
        self.assertTrue(any(e.get('leap') for e in b['animation_events']))
        root=next(e['attack_packet'] for e in b['animation_events'] if e['type']=='ground_impact')
        hits=[e for e in b['animation_events'] if e.get('kind')=='physical']
        self.assertEqual(len({e['attack_packet'] for e in hits}),2)
        self.assertTrue(all(e['impact_origin_packet']==root for e in hits))
        self.assertEqual(sorted(e['impact_offset'] for e in hits),[133,267])
        moves=[e for e in b['animation_events'] if e.get('forced')]
        self.assertTrue(all(e['impact_origin_packet']==root and e['impact_offset']>0 for e in moves))

    def test_leap_resistance_does_not_cancel_impact_and_illegal_landing_spends_nothing(self):
        b,a,t=self.fixture();a.update(x=1,y=2);t.update(x=4,y=2,armor=0,displacement_resistance=100)
        self.use(b,a,combat._ground_target(3,2),'pull')
        self.assertEqual((t['x'],t['hp']),(4,76))
        b,a,t=self.fixture();state=deepcopy(a)
        with self.assertRaises(ValueError):self.use(b,a,combat._ground_target(t['x'],t['y']),'pull')
        self.assertEqual(a,state)

    def test_leap_cannot_jump_a_wall_or_land_in_a_pit_or_climb_a_cliff(self):
        b,a,t=self.fixture();a.update(x=1,y=2)
        skill=self.skill('pull');landing=combat._ground_target(3,3)
        b['terrain']=[{'id':'pit','kind':'pit','x':3,'y':3,'blocking':True}]
        self.assertFalse(combat._leap_eligible(b,a,landing,skill))
        b['terrain']=[];b['elevation']=[{'x':3,'y':3,'height':4}]
        self.assertFalse(combat._leap_eligible(b,a,landing,skill))
        b['elevation']=[]
        with patch('backend.combat.crossed_walls',return_value=[{'id':'wall'}]):
            self.assertFalse(combat._leap_eligible(b,a,landing,skill))

    def test_missed_hook_does_not_pull_or_hobble(self):
        b,a,t=self.fixture();t.update(x=5,y=2)
        with patch('backend.combat._attack_hits',return_value=(False,{'damage_bonus':0,'chance':0},100)):
            combat._resolve_ability(b,a,t,self.skill('cover'))
        self.assertEqual(t['x'],5);self.assertFalse(conditions.has(t,'hobbled'));self.assertEqual(t['hp'],100)

    def test_ground_preview_and_move_then_leap_command_agree(self):
        b,a,t=self.fixture();a.update(x=1,y=2);t.update(x=6,y=3)
        leap=self.skill('pull');a['skills']=[leap];a['special']=leap
        before=deepcopy(b);view=combat.battle_view(b)
        preview=view['ground_skill_previews'][leap['id']]['5,3']
        self.assertEqual(b,before) # Preview must not spend movement, roll, or reveal enemies.
        self.assertIn('move_to',preview)
        self.assertEqual(preview['landing'],{'x':5,'y':3})
        with patch('backend.combat._advance_to_player'),patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            combat.apply_player_command(b,{'action':'skill','skill_id':leap['id'],'x':5,'y':3,'move_to':preview['move_to']})
        self.assertEqual((a['x'],a['y']),(5,3));self.assertTrue(a['acted'])
        self.assertEqual(len([e for e in b['animation_events'] if e.get('leap')]),1)

    def test_capture_weapon_blocks_leap_and_hook_but_not_rally(self):
        from backend.combat_abilities import availability
        b,a,t=self.fixture();a['capture_weapon']=True
        self.assertFalse(availability(a,self.skill('pull'))['available'])
        self.assertFalse(availability(a,self.skill('cover'))['available'])
        self.assertTrue(availability(a,self.skill('rally'))['available'])

    def test_auto_can_choose_a_real_leap_instead_of_attacking_a_ground_proxy(self):
        b,a,t=self.fixture();a.update(x=1,y=2);t.update(x=4,y=2)
        outer=deepcopy(t);outer.update(id='outer',x=5);b['units']['outer']=outer
        a['skills']=[self.skill('pull')];a['special']=a['skills'][0]
        with patch('backend.combat._finish_turn'),patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            combat._player_auto_turn(b,a,'balanced')
        self.assertTrue(any(e.get('leap') for e in b['animation_events']))
        self.assertTrue(t['hp']<100);self.assertTrue(outer['hp']<100)

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
