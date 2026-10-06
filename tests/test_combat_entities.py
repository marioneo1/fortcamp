import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_entities as entities, combat_abilities as abilities
from tests import test_combat_abilities as fixtures


class CombatEntityTests(unittest.TestCase):
    def fixture(self):
        b,a,t=fixtures.AbilityFoundationTests().fixture('fighter')
        for u in b['units'].values():
            if u['id'] not in (a['id'],t['id']):u.update(x=7,y=7)
        a.update(move=3,acted=False);t.update(x=4,y=2)
        return b,a,t

    def activate(self,b,a,round=2):
        a['acted']=False;b.update(round=round,turn_index=0);combat._current_unit(b)

    def deploy(self,b,a,kind):
        return entities.deploy(b,a,kind,combat._deployment_positions(b,a,kind))

    def hit(self):
        return patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1))

    def test_resource_limits_atomic_pairs_and_no_extra_turns(self):
        b,a,t=self.fixture();before=list(b['turn_order'])
        pair=self.deploy(b,a,'wisps');self.assertEqual(entities.usage(b,a),2)
        self.assertEqual(b['turn_order'],before)
        with self.assertRaises(ValueError):self.deploy(b,a,'companion')
        entities.dismiss(b,a,pair[0]);self.assertEqual(entities.usage(b,a),0)
        turret=self.deploy(b,a,'scrap_turret')[0];self.assertEqual(a['components'],1)
        entities.dismiss(b,a,turret);self.assertEqual(a['components'],1)
        with self.assertRaises(ValueError):self.deploy(b,a,'scrap_turret')

    def test_obstructed_pair_placement_does_not_spend(self):
        b,a,t=self.fixture();b['void_tiles']=[{'x':2,'y':1},{'x':1,'y':2},{'x':2,'y':3}]
        before=deepcopy(b)
        with self.assertRaises(ValueError):self.deploy(b,a,'wisps')
        self.assertEqual(b,before)

    def test_new_deployment_no_shot_then_shared_output_and_reload(self):
        b,a,t=self.fixture();self.deploy(b,a,'wisps')
        combat._finish_entities(b,a);self.assertEqual(t['hp'],100)
        b=json.loads(json.dumps(b));a=b['units']['player'];t=b['units'][t['id']]
        self.activate(b,a)
        with self.hit():combat._finish_entities(b,a)
        self.assertEqual(a['entity_budget_spent'],6);self.assertEqual(t['hp'],94)
        hp=t['hp'];combat._finish_entities(b,a);self.assertEqual(t['hp'],hp)
        self.assertEqual(a['combat_record']['total_damage'],6)
        self.assertFalse(any(u.get('combat_record',{}).get('total_damage') for u in entities.owned(b,a)))

    def test_two_turrets_split_six_not_twelve(self):
        b,a,t=self.fixture();a['components']=6
        turrets=[self.deploy(b,a,'scrap_turret')[0],self.deploy(b,a,'scrap_turret')[0]]
        self.activate(b,a)
        with self.hit():combat._finish_entities(b,a)
        self.assertEqual(t['hp'],94);self.assertEqual(a['entity_budget_spent'],6)
        self.assertTrue(all(u['acted'] for u in turrets))

    def test_manual_turret_replaces_auto_shot_and_physical_device_works_muted(self):
        b,a,t=self.fixture();turret=self.deploy(b,a,'scrap_turret')[0]
        self.activate(b,a);a['statuses']=[{'id':'mute','turns':2}]
        with self.hit():combat._entity_command(b,a,{'action':'operate_turret','entity_id':turret['id'],'target_id':t['id']})
        self.assertEqual(t['hp'],94);self.assertTrue(a['acted'])
        with self.hit():combat._finish_entities(b,a)
        self.assertEqual(t['hp'],94)
        self.activate(b,a,3)
        with self.hit():combat._finish_entities(b,a)
        self.assertEqual(t['hp'],88)

    def test_commanded_move_budget_owner_action_and_ownership(self):
        b,a,t=self.fixture();wolf=self.deploy(b,a,'companion')[0];self.activate(b,a)
        initial=wolf['move']
        for x,y in [(3,1),(4,1)]:combat._entity_command(b,a,{'action':'summon_move','entity_id':wolf['id'],'x':x,'y':y})
        self.assertFalse(a['acted']);self.assertEqual(wolf['move'],initial)
        with self.assertRaises(ValueError):combat._entity_command(b,a,{'action':'summon_move','entity_id':wolf['id'],'x':7,'y':1})
        other={**a,'id':'other'}
        with self.assertRaises(ValueError):combat._entity_command(b,other,{'action':'summon_attack','entity_id':wolf['id'],'target_id':t['id']})
        with self.hit():combat._entity_command(b,a,{'action':'summon_attack','entity_id':wolf['id'],'target_id':t['id']})
        self.assertTrue(a['acted']);self.assertEqual(t['hp'],93)
        with self.assertRaises(ValueError):combat._entity_command(b,a,{'action':'summon_attack','entity_id':wolf['id'],'target_id':t['id']})

    def test_owner_defeat_extraction_and_summon_death_do_not_make_corpses(self):
        for reason in ('dead','extracted','unconscious'):
            b,a,t=self.fixture();wolf=self.deploy(b,a,'companion')[0]
            if reason=='dead':a.update(hp=0,alive=False)
            elif reason=='extracted':a['extracted']=True
            else:a['conscious']=False
            combat._check_end(b);self.assertTrue(wolf['extracted']);self.assertEqual(wolf['condition'],'dismissed')
        b,a,t=self.fixture();wolf=self.deploy(b,a,'companion')[0]
        combat._deal_damage(b,{**t,'attack':999},wolf)
        self.assertEqual(wolf['condition'],'dismissed')
        with self.assertRaises(ValueError):combat._carry_body(b,a,wolf['id'])

    def test_temporary_targets_no_capture_loot_or_kill_credit(self):
        b,a,t=self.fixture();t['summon_capacity']=2
        enemy=entities.deploy(b,t,'companion',[(5,2)])[0]
        with self.assertRaises(ValueError):combat._capture_attempt(b,a,enemy)
        kills=a['combat_record']['kills'];damage=a['combat_record']['total_damage']
        combat._deal_damage(b,{**a,'attack':999},enemy)
        self.assertEqual(a['combat_record']['kills'],kills);self.assertEqual(a['combat_record']['total_damage'],damage)
        combat._secure_battlefield_loot(b);self.assertNotIn(enemy['id'],b['auto_looted_ids'])

    def test_manifestation_once_but_capacity_release_is_separate(self):
        b,a,t=self.fixture();guardian=self.deploy(b,a,'manifestation')[0]
        entities.dismiss(b,a,guardian);self.assertEqual(entities.usage(b,a),0)
        with self.assertRaises(ValueError):self.deploy(b,a,'manifestation')
        self.assertTrue(entities.available(b,a,'companion'))

    def test_views_do_not_tick_entities_and_controls_explain_costs(self):
        b,a,t=self.fixture();wolf=self.deploy(b,a,'companion')[0];self.activate(b,a)
        before=deepcopy(b)
        for _ in range(4):view=combat.battle_view(b)
        self.assertEqual(b,before)
        self.assertEqual(view['deployment_resources']['capacity_used'],1)
        self.assertTrue(any(s['id']=='deployment' for s in view['units'][wolf['id']]['statuses']))
        actions=combat._context_actions(b,a)
        self.assertTrue(any(e['command']['action']=='summon_move' for e in actions))
        self.assertTrue(any(e['command']['action']=='dismiss_summon' for e in actions))

    def test_deploy_effect_full_manual_command_spends_main_action_not_immediate_shot(self):
        b,a,t=self.fixture();s={'id':'deploy','name':'Call Wisps','ability_version':1,'source_kind':'character',
            'target':'ally','range':1,'elevation_rule':'line_of_effect','cost':{'cooldown':3,'charges':None},
            'effects':[{'type':'deploy','entity':'wisps'}]}
        a['skills'].append(abilities.validate(s))
        with patch('backend.combat._advance_to_player'):
            combat.apply_player_command(b,{'action':'skill','skill_id':'deploy','target_id':a['id']})
        self.assertEqual(len(entities.owned(b,a)),2);self.assertTrue(a['acted']);self.assertEqual(t['hp'],100)
        self.assertEqual(abilities.availability(a,s)['cooldown_remaining'],3)

    def test_hidden_targets_and_controlled_entities_cannot_fire(self):
        b,a,t=self.fixture();turret=self.deploy(b,a,'scrap_turret')[0];self.activate(b,a)
        with patch('backend.combat.concealment.unseen',return_value=True):
            with self.hit():combat._finish_entities(b,a)
        self.assertEqual(t['hp'],100)
        self.activate(b,a,3);turret['forced_skip']=True
        with self.hit():combat._finish_entities(b,a)
        self.assertEqual(t['hp'],100)

    def test_entity_status_clock_ticks_once_and_magic_link_respects_mute(self):
        b,a,t=self.fixture();wisp=self.deploy(b,a,'wisps')[0]
        wisp['statuses']=[{'id':'burn','turns':2}]
        self.activate(b,a);hp=wisp['hp'];self.assertEqual(hp,8)
        for _ in range(5):combat._current_unit(b);combat.battle_view(b)
        self.assertEqual(wisp['hp'],hp)
        a['statuses']=[{'id':'mute','turns':2}]
        with self.hit():combat._finish_entities(b,a)
        self.assertEqual(t['hp'],100)
        self.assertEqual(wisp['hp'],7)
        combat._finish_entities(b,a)
        self.assertEqual(wisp['hp'],7)

    def test_command_api_changes_owner_turn_and_rejected_actions_do_not_spend(self):
        b,a,t=self.fixture();wolf=self.deploy(b,a,'companion')[0];self.activate(b,a)
        with self.assertRaises(ValueError):combat._entity_command(b,a,{'action':'summon_attack','entity_id':wolf['id'],'target_id':t['id']})
        self.assertFalse(a['acted']);self.assertEqual(t['hp'],100)
        with patch('backend.combat._advance_to_player'):
            combat.apply_player_command(b,{'action':'summon_move','entity_id':wolf['id'],'x':3,'y':1})
        self.assertEqual(b['turn_index'],0);self.assertFalse(a['acted'])
        with patch('backend.combat._advance_to_player'):
            combat.apply_player_command(b,{'action':'summon_move','entity_id':wolf['id'],'x':4,'y':1})
            with self.hit():combat.apply_player_command(b,{'action':'summon_attack','entity_id':wolf['id'],'target_id':t['id']})
        self.assertEqual(b['turn_index'],1);self.assertTrue(a['acted']);self.assertEqual(t['hp'],93)

    def test_enemy_owner_uses_the_same_activation_clock(self):
        b,a,t=self.fixture();turret=entities.deploy(b,t,'scrap_turret',[(4,1)])[0]
        self.assertTrue(t['ability_version'])
        b.update(round=2,turn_index=1);combat._current_unit(b)
        self.assertGreater(t['ability_activation'],turret['deployed_at'])
        with self.hit():combat._finish_entities(b,t)
        self.assertLess(a['hp'],100)
        t['alive']=False
        self.assertFalse(entities.can_command(b,t,turret))


if __name__=='__main__':unittest.main()
