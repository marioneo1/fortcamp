import json
import random
import unittest
from copy import deepcopy
from unittest.mock import Mock, patch
from backend import general_perks as p, recruit_perks, combat as c, combat_conditions as conditions
from backend.game import new_game, _make_generic, resolve_mission
from backend.content import STANDALONE_PERKS, ITEMS
from backend.perk_effects import modifiers
from tests import test_enemy_specialties as fixtures
from tests import test_monk_jobs as monk_fixtures


class GeneralPerkTests(unittest.TestCase):
    def test_conflicts_and_independent_mixed_traits(self):
        for first,second in [('lucky','unlucky'),('hearty','delicate'),('robust','stout'),
            ('strong_armed','keen_eyed'),('broad_shouldered','meticulous'),('scholarly','nimble'),
            ('adaptable','distracted'),('sure_footed','clumsy'),('athletic','light_footed'),
            ('hardy','heat_sensitive'),('restless','wakeful'),('resilient','thin_skinned')]:
            self.assertFalse(p.compatible([first],second),(first,second))
            self.assertFalse(p.compatible([second],first),(second,first))
        self.assertEqual(p.extend(['lucky'],['unlucky','hearty','broad_shouldered','keen_eyed']),
                         ['lucky','hearty','broad_shouldered'])

    def test_rare_traits_possible_at_level_one_in_rank_e(self):
        rng=Mock();rng.random.return_value=.0000005;rng.choice.side_effect=lambda values:values[0]
        self.assertEqual(p.roll([],rng,rank='E',level=1),'naturally_gifted')
        rng.random.return_value=.001
        self.assertEqual(p.RARITY[p.roll([],rng,rank='E',level=1)],'rare')
        rng.random.return_value=.9;self.assertIsNone(p.roll([],rng))

    def test_gifted_probability_boundary_and_single_profile(self):
        rng=Mock();rng.choice.side_effect=lambda values:values[0]
        rng.random.return_value=.000000999;self.assertEqual(p.roll([],rng),'naturally_gifted')
        rng.random.return_value=.000001;self.assertNotEqual(p.roll([],rng),'naturally_gifted')
        rng.random.return_value=0;self.assertEqual(p.roll(['nimble'],rng),'naturally_gifted')

    def test_gifted_is_independent_bonus_not_redistribution_or_luck_tier(self):
        for key in ('broad_shouldered','keen_eyed','nimble','adaptable','distracted','lucky','unlucky'):
            self.assertTrue(p.compatible([key],'naturally_gifted'),key)
            self.assertTrue(p.compatible(['naturally_gifted'],key),key)
        self.assertFalse(p.compatible(['naturally_gifted'],'naturally_gifted'))
        self.assertEqual(p.extend(['broad_shouldered'],['naturally_gifted','keen_eyed']),
                         ['broad_shouldered','naturally_gifted'])

    def test_generated_characters_preserve_identity_draws_and_conflicts(self):
        rng=random.Random('generation');other=random.Random('generation')
        with patch('backend.general_perks.generated_traits',side_effect=lambda traits,*args:list(traits)):
            baseline=_make_generic('fighter',other)
        generated=_make_generic('fighter',rng)
        self.assertEqual(rng.getstate(),other.getstate())
        for field in ('attributes','stats','name','race','gender','portrait'):
            self.assertEqual(baseline[field],generated[field])
        for seed in range(2000):
            traits=p.generated_traits(['nimble'],seed)
            self.assertLessEqual(sum('redistribution' in p.GROUPS.get(key,set()) for key in traits),1)

    def test_catalog_has_matching_tooltips_and_modifiers(self):
        self.assertGreaterEqual(len(p.DEFINITIONS),60)
        for key,(name,description) in p.DEFINITIONS.items():
            self.assertEqual(STANDALONE_PERKS[key]['name'],name)
            self.assertEqual(STANDALONE_PERKS[key]['modifiers'],p.EFFECTS[key])
            self.assertIn(key,{row['id'].split(':',1)[1] for row in recruit_perks.traits({'traits':[key]})})

    def test_full_attribute_bonus_and_single_hp_tier(self):
        state=new_game({'name':'QA'});char=state['characters'][0];char['traits']=[]
        before={s:c._effective_attribute(state,char,s) for s in ('str','dex','agi','vit','int','luk')}
        char['traits']=['naturally_gifted']
        for stat,value in before.items():self.assertEqual(c._effective_attribute(state,char,stat),value+1)
        char['traits']=['stout'];self.assertEqual(modifiers(state,char,ITEMS,'combat')['hp'],10)

    def test_random_attribute_stable_and_does_not_change_character(self):
        state=new_game({'name':'QA'});char=state['characters'][0];char['traits']=['adaptable']
        before=deepcopy(char);unit=c._player_unit(state,char,0,0,battle_seed='battle-1')
        self.assertEqual(char,before)
        reopened=c._player_unit(state,char,0,0,battle_seed='battle-1')
        self.assertEqual(unit['battle_attribute_roll'],reopened['battle_attribute_roll'])
        saved=json.loads(json.dumps(unit));self.assertEqual(saved['battle_attribute_roll'],unit['battle_attribute_roll'])
        overlays={p.battle_character(char,str(i))[1]['attribute'] for i in range(60)}
        self.assertEqual(overlays,{'str','dex','agi','vit','int','luk'})

    def test_negative_random_attribute_floor(self):
        char={'id':'one','traits':['distracted'],'attributes':{s:1 for s in ('str','dex','agi','vit','int','luk')}}
        changed,roll=p.battle_character(char,'seed');self.assertEqual(changed['attributes'][roll['attribute']],1)

    def test_range_only_ranger_bows_and_movement_locks(self):
        state=new_game({'name':'QA'});char=state['characters'][0];char['traits']=['far_sighted']
        bow={'name':'Bow','weapon_type':'bow','power':1};char['job_id']='ranger'
        with patch.object(c,'_equipped_weapon',return_value=bow):
            self.assertEqual(c._player_unit(state,char,0,0)['attack_range'],5)
            char['job_id']='fighter';self.assertEqual(c._player_unit(state,char,0,0)['attack_range'],4)
        unit=c._player_unit(state,char,0,0);unit['statuses']=[{'id':'bind'}]
        self.assertEqual(c._movement_limit(unit),0)
        unit.update(statuses=[],move=1);self.assertEqual(c._movement_limit(unit),1)

    def test_damage_resistance_reduces_ticks_not_stack_application(self):
        b,a,t=fixtures.SpecialtyTests().arena()
        for sid,key in [('burn','hardy'),('poison','iron_stomached'),('bleed','thick_blooded')]:
            t.update(statuses=[],perk_modifiers=p.EFFECTS[key]['combat'])
            self.assertEqual(conditions.status_chance(t,sid),100)
            conditions.add_stack(t,sid,2,a)
            self.assertEqual(next(s['stacks'] for s in t['statuses'] if s['id']==sid),1)
            source={'id':a['id'],'attack':40,'status_tick':True,'percent_dot':sid,'damage_kind':sid}
            self.assertEqual(c._damage_before_barrier(b,source,t,armor_pierce=99),30)
            t['hp']=200;c._deal_damage(b,source,t,resolved_damage=40)
            self.assertEqual(t['hp'],170)

    def test_control_resistance_uses_strongest_never_adds_to_immunity(self):
        unit={'statuses':[],'perk_modifiers':{'stun_resistance':75},'status_resistances':{'stun':25}}
        self.assertEqual(conditions.status_chance(unit,'stun'),25)
        self.assertEqual(conditions.resistance_view(unit)['statuses']['stun'],75)

    def test_all_source_mitigation_and_weakness_rounding(self):
        b,a,t=fixtures.SpecialtyTests().arena();t['perk_modifiers']={'incoming_reduction':1}
        for source in (a,{**a,'status_tick':True,'damage_kind':'fall'}):
            t['hp']=200;c._deal_damage(b,source,t,resolved_damage=100);self.assertEqual(t['hp'],101)
        t.update(hp=200,perk_modifiers={'incoming_reduction':-1})
        c._deal_damage(b,a,t,resolved_damage=100);self.assertEqual(t['hp'],99)

    def test_unarmed_multi_hit_shared_bonus_and_no_spell_bonus(self):
        b,a,t=fixtures.SpecialtyTests().arena();a.update(weapon_type='unarmed',perk_modifiers={'unarmed_bonus':3})
        a.pop('unarmed_perk_spent',None)
        first=c._deal_damage(b,a,t);second=c._deal_damage(b,a,t)
        self.assertEqual((first,second),(13,10))
        a.pop('unarmed_perk_spent',None)
        source={**a,'attack_elevation_rule':'ignore','mage_spell':True}
        self.assertEqual(c._damage_before_barrier(b,source,t),10)

    def test_precomputed_monk_damage_does_not_reduce_twice(self):
        helper=monk_fixtures.MonkJobTests()
        b,a,t=helper.fixture();a['attack']=1000;t.update(hp=10000,max_hp=10000,perk_modifiers={'incoming_reduction':1})
        a['monk_combo']={'stage':'follow_up'}
        # Call the existing multi-hit resolver directly to isolate its damage
        # budget from stage availability, which the Job suite tests separately.
        from backend.job_loadouts import SKILLS
        skill=deepcopy(SKILLS['job:monk:breaking_combination'])
        effect=next(e for e in skill['effects'] if e.get('type')=='attack')
        with patch.object(c,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
            c._perform_monk_attack(b,a,t,skill,effect)
        self.assertEqual(10000-t['hp'],1188) # 1000 x 1.2 x .99, not x .99 twice.

    def test_enemy_perks_survive_recruitment_and_random_stat_is_saved(self):
        b,a,t=fixtures.SpecialtyTests().arena();t.update(perk_battle_seed='enemy-battle',move=3,initiative=12,attack_range=1)
        recruit={'job_id':'rogue','traits':['adaptable','thick_blooded'],'attributes':{s:4 for s in ('str','dex','agi','vit','int','luk')}}
        recruit_perks.decorate_enemy(t,recruit)
        self.assertEqual(t['perk_modifiers']['bleed_damage_reduction'],25)
        self.assertEqual(t['origin_perks'],recruit['traits'])
        saved=json.loads(json.dumps(t));self.assertEqual(saved['battle_attribute_roll'],t['battle_attribute_roll'])

    def test_mission_gold_only_when_base_reward_positive(self):
        from backend.content import MISSION_TEMPLATES
        state=new_game({'name':'QA'});char=state['characters'][0];char['traits']=['enterprising']
        baseline=deepcopy(state);baseline['characters'][0]['traits']=[]
        mission=deepcopy(next(m for m in MISSION_TEMPLATES.values() if m.get('rank')=='E' and m.get('pays_gold')))
        analysis={'critical_threshold':20,'lead_stat':5,'support_bonus':0,'criteria_bonus':0,'lead_id':'player'}
        result=resolve_mission(state,mission,['player'],analysis,'gold',forced_outcome='success')
        normal=resolve_mission(baseline,mission,['player'],analysis,'gold',forced_outcome='success')
        self.assertEqual(result['rewards']['gold'],normal['rewards']['gold']+1)
        self.assertEqual(result['rewards']['perk_gold'],1)
        empty=deepcopy(mission);empty.update(pays_gold=False,rewards={},critical_rewards={})
        empty_result=resolve_mission(state,empty,['player'],analysis,'empty',forced_outcome='success')
        self.assertEqual(empty_result['rewards']['gold'],0)
        self.assertNotIn('perk_gold',empty_result['rewards'])


if __name__=='__main__':unittest.main()
