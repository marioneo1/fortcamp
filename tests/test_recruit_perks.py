import unittest, random
from copy import deepcopy
from unittest.mock import patch
from backend import combat as c, combat_conditions as conditions, recruit_perks as perks, economy
from backend.game import new_game
from backend.prison_recruitment import initialize_prisoner
from tests import test_enemy_specialties as fixtures

class RecruitPerkTests(unittest.TestCase):
    def arena(self):
        b,a,t=fixtures.SpecialtyTests().arena()
        for u in (a,t):u.update(origin_perks=[],traits=[],perk_modifiers={})
        return b,a,t

    def test_poison_rejects_one_stack_not_whole_application(self):
        b,a,t=self.arena();t['traits']=['poison_tolerant']
        for _ in range(3):conditions.add_stack(t,'poison',2,a)
        self.assertEqual(next(s['stacks'] for s in t['statuses'] if s['id']=='poison'),2)
        restored=deepcopy(t);conditions.add_stack(restored,'poison',2,a)
        self.assertEqual(next(s['stacks'] for s in restored['statuses'] if s['id']=='poison'),3)

    def test_extra_attack_once_not_recursive_or_ally_action_spent(self):
        b,a,t=self.arena();leader=deepcopy(a);leader.update(id='leader',x=4,traits=['opportunistic_leader'],current_target_id=t['id'])
        b['units']['leader']=leader
        with patch.object(c,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            c._perform_attack(b,a,t,'melee');self.assertEqual(t['hp'],180)
            c._perform_attack(b,a,t,'melee');self.assertEqual(t['hp'],170)
        self.assertTrue(leader['leader_used']);self.assertFalse(a['acted'])

    def test_extra_attack_not_granted_for_dead_target_or_illegal_range(self):
        b,a,t=self.arena();leader=deepcopy(a);leader.update(id='leader',traits=['opportunistic_leader'],current_target_id=t['id']);b['units']['leader']=leader
        t.update(hp=5)
        with patch.object(c,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            c._perform_attack(b,a,t,'melee')
        self.assertFalse(leader.get('leader_used',False))

    def test_trapper_prefers_not_killer_and_persists_after_defeat(self):
        b,a,t=self.arena();t.update(hp=1,traits=['cunning_trapper'])
        c._deal_damage(b,a,t)
        zone=b['zones'][0]
        self.assertEqual(len(zone['cells']),3)
        self.assertNotIn({'x':a['x'],'y':a['y']},zone['cells'])
        c.spaces.cleanup_zones(b,c._combat_active);self.assertEqual(len(b['zones']),1)
        a.update(x=zone['cells'][0]['x'],y=zone['cells'][0]['y']);c._trigger_zones(b,a,'entry')
        self.assertEqual(b['zones'],[]);self.assertTrue(conditions.has(a,'hobbled'))

    def test_trapper_skips_impossible_strip(self):
        b,a,t=self.arena();b.update(width=2,height=2);a.update(x=0,y=0);t.update(x=1,y=0,hp=1,traits=['cunning_trapper'])
        c._deal_damage(b,a,t);self.assertEqual(b['zones'],[])

    def test_play_dead_survives_not_invincible_and_clears_on_action(self):
        b,a,t=self.arena();t.update(hp=40,traits=['sly_survivor'])
        c._deal_damage(b,a,t);self.assertTrue(conditions.has(t,'feigned_death'))
        self.assertEqual(perks.prefer_targets([t,a]),[a]);self.assertEqual(perks.prefer_targets([t]),[t])
        perks.clear_ruse(t);c._deal_damage(b,a,t)
        self.assertFalse(conditions.has(t,'feigned_death'));self.assertEqual(t['hp'],20)

    def test_defiant_requires_ally_loss_not_solo_or_summon(self):
        b,a,t=self.arena();a['traits']=['defiant'];t['hp']=1;c._deal_damage(b,a,t)
        self.assertFalse(conditions.has(a,'barrier'))
        ally=deepcopy(a);ally.update(id='ally',hp=1,traits=[]);b['units']['ally']=ally
        c._deal_damage(b,t,ally,resolved_damage=1) # a dead direct source cannot damage; use environmental source below
        c._deal_damage(b,{**t,'status_tick':True},ally,resolved_damage=1)
        self.assertTrue(conditions.has(a,'barrier'))
        self.assertEqual(next(s['amount'] for s in a['statuses'] if s['id']=='barrier'),40)

    def test_intimidation_first_kill_only_and_damage_effect(self):
        b,a,t=self.arena();a['traits']=['intimidating'];other=deepcopy(t);other.update(id='other',x=7);b['units']['other']=other;t['hp']=1
        c._deal_damage(b,a,t)
        self.assertTrue(conditions.has(other,'intimidated'))
        self.assertEqual(c._damage_before_barrier(b,other,a),8)
        self.assertTrue(a['example_used'])

    def test_ricochet_half_power_once_against_metal_not_flesh(self):
        b,a,t=self.arena();a.update(traits=['resourceful_slinger'],attack_elevation_rule='ballistic')
        t.update(armor_material='plate');other=deepcopy(t);other.update(id='other',x=7,armor_material='leather');b['units']['other']=other
        with patch.object(c,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            c._perform_attack(b,a,t,'ballistic');self.assertEqual(other['hp'],195)
            c._perform_attack(b,a,t,'ballistic');self.assertEqual(other['hp'],195)
        self.assertTrue(a['ricochet_used'])

    def test_pursuer_only_actual_mobility_and_once_per_activation(self):
        b,a,t=self.arena();a['traits']=['relentless_pursuer']
        b['animation_events']=[{'type':'movement','unit_id':t['id'],'teleport':True}];perks.movement(b,t)
        perks.after_attack(b,a,t,True,1);perks.after_attack(b,a,t,True,1)
        self.assertEqual(next(s['stacks'] for s in t['statuses'] if s['id']=='hobbled'),1)
        perks.finish(b,a);perks.after_attack(b,a,t,True,1)
        self.assertEqual(next(s['stacks'] for s in t['statuses'] if s['id']=='hobbled'),1)

    def test_profession_bonus_matching_assignment_only_and_recruit_preserves(self):
        s=new_game({'name':'QA'});s['buildings']=[{'type':'lumbermill','assigned':['player'],'level':1}]
        s['characters'][0].update(traits=['lumberjack','quarry_worker','salvager'],status='idle',assignment='lumbermill')
        s['production']={'settled_at':1000,'fractions':{}}
        base=deepcopy(s);base['characters'][0]['traits']=[]
        economy.settle(s,4600);economy.settle(base,4600)
        self.assertEqual(s['resources']['wood']-base['resources']['wood'],1)
        self.assertEqual(s['resources']['stone'],base['resources']['stone'])
        prisoner={'id':'p','name':'QA','race':'Human','recruitable_snapshot':{'job_id':'rogue','traits':['lumberjack','strong_armed']}}
        initialize_prisoner(prisoner,now=0)
        self.assertEqual(prisoner['recruitment']['candidate']['traits'],['lumberjack','strong_armed'])

    def test_defense_point_not_extra_party_slot(self):
        s=new_game({'name':'QA'});normal=c.create_frontier_watch_defense_battle(s,['player'],'defense')
        s['characters'][0].setdefault('traits',[]).append('fast_builder')
        buffed=c.create_frontier_watch_defense_battle(s,['player'],'defense')
        self.assertEqual(buffed['preparation']['budget'],normal['preparation']['budget']+1)
        self.assertEqual(len(buffed['units']),len(normal['units']))

    def test_distribution_zero_and_rare_multiple_and_stats(self):
        counts=[0,0,0,0];zero=0
        for i in range(12000):
            recruit={'combat_specialization':'QA'};perks.assign(recruit,'tool_shed','guard',str(i))
            traits=recruit['traits'];zero+=not traits
            counts[len(set(traits)&set(perks.PRODUCTION.values()))]+=1
        self.assertGreater(zero,1000);self.assertGreater(counts[1],counts[2]*10);self.assertGreater(counts[2],0);self.assertGreater(counts[3],0)
        s=new_game({'name':'QA'});char=s['characters'][0];baseline=c._effective_attribute(s,char,'str')
        char.setdefault('traits',[]).append('strong_armed')
        self.assertEqual(c._effective_attribute(s,char,'str'),baseline+2)

    def test_environmental_damage_without_team_and_heel_path_excursion(self):
        b,a,t=self.arena();t['hp']=1
        c._deal_damage(b,{'id':'pit','name':'Fall','attack':5,'status_tick':True},t)
        self.assertEqual(t['hp'],0)
        b,a,t=self.arena();conditions.add_stack(t,'bleed',1,a)
        t['statuses'].append({'id':'heel_wound','origin':{'x':6,'y':5},'distance_paid':0,'source_id':a['id']})
        path=[(7,5),(8,5),(7,5)];t.update(x=7,y=5)
        c._apply_zone_route(b,t,path)
        self.assertEqual(next(s['stacks'] for s in t['statuses'] if s['id']=='bleed'),3)
        self.assertEqual(t['hp'],150)

if __name__=='__main__':unittest.main()
