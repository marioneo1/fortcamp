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

    def test_earthbreaker_does_not_append_magic_cast_after_physical_impact(self):
        b,a,t=self.fixture()
        destination=combat._ground_target(3,3)
        self.use(b,a,destination,'pull')
        self.assertTrue(any(e['type']=='ground_impact' for e in b['animation_events']))
        self.assertFalse(any(c['name']=='magic_cast' for e in b['animation_events'] for c in e.get('cues',[])))

    def test_pull_preview_predicts_real_body_collision_and_barrier_absorption(self):
        b,a,t=self.fixture();t.update(x=5,y=2)
        other=deepcopy(t);other.update(id='bystander',name='Bystander',x=4,statuses=[{'id':'barrier','amount':2}])
        b['units'][other['id']]=other
        preview=combat._strike_preview(b,a,t,'melee',3,self.skill('cover'))
        pull=preview['tactics'][0]
        self.assertEqual(pull['destination'],{'x':5,'y':2})
        self.assertEqual(pull['collision_cell'],{'x':4,'y':2})
        self.assertEqual(pull['collision_target_id'],'bystander')
        self.assertEqual(pull['collision_damage'],preview['damage_on_hit']//2)
        self.assertEqual(pull['bystander_damage'],pull['collision_damage']-2)
        self.use(b,a,t,'cover')
        self.assertEqual(100-t['hp'],preview['damage_on_hit']+pull['collision_damage'])
        self.assertEqual(100-other['hp'],pull['bystander_damage'])

    def test_push_preview_does_not_predict_collision_damage_at_map_edge(self):
        b,a,t=self.fixture();a.update(x=b['width']-2,y=2);t.update(x=b['width']-1,y=2)
        pull=combat._strike_preview(b,a,t,'melee',1,self.skill('bash'))['tactics'][0]
        self.assertFalse(pull['solid_collision'])
        self.assertEqual(pull['collision_damage'],0)
        self.assertIsNone(pull['collision_cell'])

    def use(self,b,a,t,key):
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            return combat._resolve_ability(b,a,t,self.skill(key))

    def test_melee_structure_strike_and_break_share_animation_contact_with_audio(self):
        for hp in (100,1):
            b,a,t=self.fixture()
            rack={'id':'rack','name':'Weapon Rack','x':3,'y':2,'kind':'furniture',
                  'destructible':True,'hp':hp,'max_hp':hp,'armor':0,'blocking':True}
            b['terrain']=[rack]
            combat._damage_terrain(b,a,rack['id'])
            swing=next(e for e in b['animation_events'] if e['type']=='melee_attack')
            sound=next(e for e in b['animation_events'] if e['type']=='sound')
            self.assertEqual(swing['target_kind'],'terrain')
            self.assertEqual(swing['to'],{'x':3,'y':2})
            self.assertEqual(swing['attack_packet'],sound['attack_packet'])
            self.assertEqual(rack.get('destroyed',False),hp==1)
            self.assertTrue(a['physical_action'])

    def test_edge_wall_strikes_aim_at_boundary_even_from_the_same_cell(self):
        for side,dx,dy in [('north',0,-.5),('east',.5,0),('south',0,.5),('west',-.5,0)]:
            b,a,t=self.fixture()
            wall={'id':'wall','name':'Wall','x':a['x'],'y':a['y'],'wall_edges':[side],
                  'edge_wall':True,'destructible':True,'hp':1,'armor':0,'blocking':True}
            b['terrain']=[wall]
            combat._damage_terrain(b,a,'wall')
            swing=next(e for e in b['animation_events'] if e['type']=='melee_attack')
            self.assertEqual(swing['to'],{'x':a['x']+dx,'y':a['y']+dy})
            self.assertTrue(wall['destroyed'])

    def test_rally_is_castable_without_fear_and_grants_separate_one_use_bonuses(self):
        b,a,t=self.fixture();t.update(team=a['team'],x=3,y=3)
        skill=self.skill('rally');a.update(skills=[skill],special=skill)
        view=combat.battle_view(b)
        self.assertIsNotNone(view['skill_previews'][skill['id']][a['id']])
        self.use(b,a,a,'rally')
        for u in (a,t):
            self.assertTrue(conditions.has(u,'rally_power'))
            self.assertTrue(conditions.has(u,'rally_protection'))
            u['status_activation']='later';conditions.finish_activation(u)
            self.assertTrue(conditions.has(u,'rally_power'))
        t.update(team='enemy',armor=0);a['attack']=20
        # Protection does not consume the attack bonus; Guard cannot double it.
        a['guarding']=True
        self.assertEqual(combat._deal_damage(b,{'id':'hit','name':'Hit','attack':20},a),15)
        self.assertFalse(conditions.has(a,'rally_protection'))
        self.assertTrue(conditions.has(a,'rally_power'))
        conditions.remove(t,'rally_protection')
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            self.assertEqual(combat._perform_attack(b,a,t,'melee')[2],25)
            self.assertEqual(combat._perform_attack(b,a,t,'melee')[2],20)
        self.assertFalse(conditions.has(a,'rally_power'))

    def test_rally_one_cell_radius_and_four_turn_cooldown(self):
        from backend import combat_abilities as abilities
        b,a,t=self.fixture();t.update(team=a['team'],x=a['x']+2,y=a['y'])
        near=deepcopy(t);near.update(id='near',x=a['x']+1,y=a['y']+1);b['units']['near']=near
        skill=self.skill('rally');start=a.get('ability_activation',0);self.use(b,a,a,'rally')
        self.assertTrue(conditions.has(near,'rally_power'))
        self.assertFalse(conditions.has(t,'rally_power'))
        a['acted']=False
        for activation,remaining in [(0,4),(1,3),(2,2),(3,1),(4,0)]:
            a['ability_activation']=start+activation
            state=abilities.availability(a,skill)
            self.assertEqual(state['cooldown_remaining'],remaining)
            self.assertEqual(state['available'],remaining==0)

    def test_rally_miss_spends_power_and_area_attack_boosts_every_victim(self):
        b,a,t=self.fixture();conditions.apply(a,'rally_power',1,a)
        with patch('backend.combat._attack_hits',return_value=(False,{'damage_bonus':0,'chance':0},100)):
            combat._perform_attack(b,a,t,'melee')
        self.assertFalse(conditions.has(a,'rally_power'))
        b,a,t=self.fixture();a.update(x=1,y=2);t.update(x=4,displacement_resistance=100)
        other=deepcopy(t);other.update(id='other',y=3);b['units']['other']=other
        conditions.apply(a,'rally_power',1,a)
        self.use(b,a,combat._ground_target(3,2),'pull')
        self.assertEqual((t['hp'],other['hp']),(70,70))
        self.assertFalse(conditions.has(a,'rally_power'))

    def test_rally_excludes_corpses_and_allies_behind_walls_and_does_not_stack(self):
        b,a,t=self.fixture();t.update(team=a['team'])
        dead=deepcopy(a);dead.update(id='dead',alive=False,conscious=False,hp=0);b['units']['dead']=dead
        b['terrain']=[{'id':'wall','x':a['x'],'y':a['y'],'wall_edges':['east'],'edge_wall':True,'blocking':True}]
        self.use(b,a,a,'rally')
        self.assertFalse(conditions.has(t,'rally_power'));self.assertFalse(conditions.has(dead,'rally_power'))
        for sid in ('rally_power','rally_protection'):
            self.assertEqual(len([s for s in a['statuses'] if s['id']==sid]),1)
        self.assertFalse(combat._support_eligible(b,a,a,combat._support_effect(self.skill('rally'),a)))

    def test_lethal_driving_hit_still_pushes_and_places_corpse_at_destination(self):
        b,a,t=self.fixture();t['hp']=1
        self.use(b,a,t,'bash')
        self.assertEqual((t['hp'],t['condition'],t['x']),(0,'dead',4))
        self.assertFalse(conditions.has(t,'stun'))
        movement=next(e for e in b['animation_events'] if e['type']=='movement')
        death=next(e for e in b['animation_events'] if e['type']=='death_burst')
        self.assertEqual(movement['points'][-1],{'x':4,'y':2})
        self.assertEqual((death['x'],death['y']),(4,2))
        self.assertEqual(t['combat_record']['times_defeated'],1)

    def test_lethal_driving_collision_damages_and_stuns_only_surviving_bystander(self):
        for immune,hp in ((False,100),(True,100),(False,1)):
            b,a,t=self.fixture();t['hp']=1
            other=deepcopy(a);other.update(id='bystander',x=4,hp=hp,control_immunity=2 if immune else 0)
            b['units'][other['id']]=other
            self.use(b,a,t,'bash')
            self.assertEqual(other['hp'],max(0,hp-9))
            self.assertFalse(conditions.has(t,'stun'))
            self.assertEqual(conditions.has(other,'stun'),hp>9)
            self.assertTrue(any(e['type']=='collision_recoil' for e in b['animation_events']))

    def test_lethal_earthbreaker_pushes_body_into_ally_outside_impact_area(self):
        b,a,t=self.fixture();a.update(x=1,y=2);t.update(x=4,hp=1)
        other=deepcopy(a);other.update(id='bystander',x=6,hp=100)
        b['units'][other['id']]=other
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            combat._resolve_ability(b,a,{'id':'ground','x':3,'y':2,'hp':1},self.skill('pull'))
        self.assertEqual((t['hp'],t['x'],other['hp']),(0,5,88))
        self.assertFalse(conditions.has(t,'stun'));self.assertTrue(conditions.has(other,'stun'))
        death=next(e for e in b['animation_events'] if e['type']=='death_burst')
        self.assertEqual((death['x'],death['y']),(5,2))

    def test_lethal_push_respects_wall_and_never_applies_status_to_corpse(self):
        b,a,t=self.fixture();t['hp']=1
        b['terrain']=[{'id':'wall','x':4,'y':2,'blocking':True}]
        self.use(b,a,t,'bash')
        self.assertEqual(t['x'],3);self.assertFalse(conditions.has(t,'stun'))
        self.assertEqual(len([e for e in b['animation_events'] if e['type']=='death_burst']),1)

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

    def test_driving_person_collision_stuns_both_ignoring_retired_recovery(self):
        for immune in (False,True):
            b,a,t=self.fixture()
            other=deepcopy(t);other.update(id='bystander',x=4,team=a['team'],control_immunity=2 if immune else 0)
            b['units'][other['id']]=other
            self.use(b,a,t,'bash')
            self.assertEqual((t['hp'],other['hp']),(73,91))
            self.assertTrue(conditions.has(t,'stun'))
            self.assertTrue(conditions.has(other,'stun'))

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
        b,a,t=self.fixture();t.update(team=a['team'],x=3,y=3)
        far=deepcopy(t);far.update(id='far',x=4,y=4);b['units']['far']=far
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

    def test_capture_weapon_keeps_fighter_job_techniques_available(self):
        from backend.combat_abilities import availability
        b,a,t=self.fixture();a['capture_weapon']={'range':1,'elevation_rule':'melee'}
        # Capture equipment adds Subdue; it does not replace lethal combat or
        # remove the Fighter's body/chain-based Job techniques.
        self.assertTrue(availability(a,self.skill('pull'))['available'])
        self.assertTrue(availability(a,self.skill('cover'))['available'])
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
