import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat,combat_encounter_ai as ai,combat_conditions as conditions
from backend.game import new_game
from backend.prison_recruitment import initialize_prisoner
from backend.job_loadouts import snapshot

class EncounterBehaviorTests(unittest.TestCase):
    def arena(self,mission='rats_storehouse',seed=None):
        seed=seed or {'rats_storehouse':'layout-0','wolves_fence':'layout-3','roadside_toll':'layout-1'}[mission]
        b=combat.create_contract_battle(new_game({'name':'QA','starting_role':'fighter'}),['player'],seed,mission,True)
        b.update(terrain=[],zones=[],width=16,height=16,animation_events=[])
        p=b['units']['player'];p.update(x=5,y=5,statuses=[],guarding=False,armor=0)
        enemies=combat._living(b,'enemy')
        for i,u in enumerate(enemies):u.update(x=7+i,y=5,statuses=[],guarding=False)
        return b,p,enemies

    def test_merge_preserves_damage_and_adds_stats_with_three_total_cap(self):
        b,p,(a,c,d)=self.arena()
        a.update(x=6,y=5,hp=5,max_hp=8,attack=2);c.update(x=7,y=5,hp=9,max_hp=9,attack=3)
        self.assertTrue(ai.merge(b,a,c))
        merge_event=b['animation_events'][0]
        self.assertTrue(merge_event['receiver_before']['portrait'].endswith('/rat.png'))
        self.assertTrue(merge_event['receiver_after']['portrait'].endswith('/rat_swarm.png'))
        self.assertEqual((a['hp'],a['max_hp'],a['attack'],a['swarm_count']),(14,17,5,2))
        self.assertEqual(c['condition'],'merged');self.assertFalse(c['alive']);self.assertTrue(c['extracted'])
        d.update(x=6,y=6)
        self.assertTrue(ai.merge(b,a,d));self.assertEqual(a['swarm_count'],3)
        e=deepcopy(d);e.update(id='fourth',alive=True,conscious=True,extracted=False,x=5,y=5,swarm_count=1)
        b['units']['fourth']=e
        self.assertFalse(ai.merge(b,a,e))
        self.assertEqual(len([e for e in b['animation_events'] if e['type']=='rat_merge']),2)
        self.assertEqual(len(combat._living(b,'enemy')),2)

    def test_merge_cannot_cross_a_wall_or_absorb_an_incapacitated_body(self):
        b,p,(a,c,d)=self.arena();a.update(x=6,y=5);c.update(x=7,y=5)
        b['terrain']=[{'x':6,'y':5,'wall_edges':['east'],'blocking':True,'blocks_sight':True}]
        self.assertFalse(ai.merge(b,a,c))
        b['terrain']=[];c['statuses']=[{'id':'stun','turns':1}]
        self.assertFalse(ai.merge(b,a,c))

    def test_weakness_caps_effect_not_stacks_and_decays_once_per_activation(self):
        b,p,(a,c,d)=self.arena();a['swarm_count']=3
        ai.bite(b,a,p);ai.bite(b,a,p);ai.bite(b,a,p)
        s=next(s for s in p['statuses'] if s['id']=='rat_weakness')
        self.assertEqual(s['stacks'],9);self.assertEqual(ai.weakness(p),30)
        self.assertAlmostEqual(ai.modify_damage(p,a,100),70)
        self.assertAlmostEqual(ai.modify_damage(a,p,100),130)
        p['status_version']=1;p['status_activation']=[1,0]
        conditions.finish_activation(p);conditions.finish_activation(p)
        self.assertEqual(s['stacks'],8)
        for turn in range(1,5):p['status_activation']=[1,turn];conditions.finish_activation(p)
        self.assertEqual(s['stacks'],4);self.assertEqual(ai.weakness(p),20)

    def test_swarm_is_one_hit_with_multiple_weakness_applications_and_no_poison(self):
        b,p,(a,c,d)=self.arena();a.update(x=6,y=5);c.update(x=6,y=6)
        ai.merge(b,a,c);b['animation_events']=[]
        with patch.object(combat,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            combat._perform_attack(b,a,p,'melee')
        self.assertEqual(next(s for s in p['statuses'] if s['id']=='rat_weakness')['stacks'],2)
        self.assertFalse(conditions.has(p,'poison'))
        attacks=[e for e in b['animation_events'] if e['type']=='melee_attack']
        self.assertEqual(len(attacks),1);self.assertEqual(attacks[0]['bite_count'],2)
        combat._deal_damage(b,{**a,'status_tick':True,'attack':1},p)
        self.assertEqual(next(s for s in p['statuses'] if s['id']=='rat_weakness')['stacks'],2)

    def test_wounded_rat_regroups_but_healthy_rat_attacks(self):
        b,p,(a,c,d)=self.arena();a.update(x=6,y=5,hp=10);c.update(x=7,y=5);d.update(x=12,y=12)
        self.assertTrue(ai.auto(b,a,[p]));self.assertEqual(a.get('swarm_count'),2)
        b,p,(a,c,d)=self.arena();a.update(x=6,y=5);c.update(x=7,y=5)
        with patch.object(combat,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            ai.auto(b,a,[p])
        self.assertEqual(a['swarm_count'],1);self.assertLess(p['hp'],p['max_hp'])

    def test_wolves_fill_opposite_cardinal_flanks_of_the_same_target(self):
        b,p,(a,c,d)=self.arena('wolves_fence');a.update(x=4,y=5);c.update(x=7,y=5);d.update(x=7,y=7)
        other=deepcopy(p);other.update(id='other',x=11,y=11);b['units']['other']=other
        ai.auto(b,c,[p,other]);self.assertEqual((c['x'],c['y']),(6,5))
        self.assertEqual(b['wolf_pack_target:enemy'],p['id'])
        ai.auto(b,d,[p,other]);self.assertEqual(combat._distance(d,p),1)

    def test_bandit_withdraws_below_half_hp_to_healthy_ally_and_line_is_throttled(self):
        b,p,(a,c)=self.arena('roadside_toll');a.update(x=6,y=5,hp=10);c.update(x=8,y=5)
        ai.auto(b,a,[p]);self.assertGreater(combat._distance(a,p),1);self.assertTrue(a['guarding'])
        lines=[e for e in b['animation_events'] if e.get('kind')=='dialogue'];self.assertEqual(len(lines),1)
        ai.say(b,a,'More words','withdraw');self.assertEqual(len([e for e in b['animation_events'] if e.get('kind')=='dialogue']),1)

    def test_taunt_prevents_rat_merging_and_keeps_the_forced_target(self):
        b,p,(a,c,d)=self.arena();a.update(x=6,y=5,hp=10);c.update(x=7,y=5)
        ai.auto(b,a,[p],p);self.assertEqual(a['swarm_count'],1)
        self.assertTrue(any(e.get('target_id')==p['id'] for e in b['animation_events'] if e['type']=='melee_attack'))

    def test_mixed_and_standard_bandit_variants_are_repeatable_and_recruitable(self):
        seen=set()
        for seed in range(16):
            b,p,(a,c)=self.arena('roadside_toll',f'variant-{seed}')
            seen.add(c['combat_specialization'])
            again=self.arena('roadside_toll',f'variant-{seed}')[2][1]
            self.assertEqual(c['combat_specialization'],again['combat_specialization'])
            initialize_prisoner(c,now=0);candidate=c['recruitment']['candidate']
            self.assertEqual(candidate['personality_id'],c['personality_id'])
            skills,_,_=snapshot(candidate)
            self.assertEqual([s['id'] for s in skills],[s['id'] for s in c['skills']])
        self.assertEqual(seen,{'Road Trapper','Road Cutpurse'})

    def test_custom_ai_completes_exactly_one_turn(self):
        for mission in ('rats_storehouse','wolves_fence','roadside_toll'):
            b,p,enemies=self.arena(mission);u=enemies[-1];u.update(x=6,y=5)
            b.update(turn_order=[u['id'],p['id']]+[e['id'] for e in enemies if e is not u],turn_index=0)
            combat._enemy_turn(b,u)
            self.assertEqual(b['turn_index'],1,mission)
