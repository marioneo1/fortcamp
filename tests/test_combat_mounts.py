import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from backend import combat, combat_mounts as mounts, combat_conditions as conditions
from backend.game import new_game
from backend.battle_lab import layout_presets


class AnimalMountTests(unittest.TestCase):
    def test_corpse_records_mounted_death_only(self):
        for mounted in (True,False):
            b=self.battle();rider,boar=self.pair(b)
            if not mounted:mounts.unlink(rider,boar)
            with patch.object(mounts,'fall_outcome',return_value='safe'):
                combat._deal_damage(b,{'id':'test','name':'Test','status_tick':True,'weapon':'Test'},boar,resolved_damage=999)
            self.assertEqual(bool(boar.get('mounted_death')),mounted)

    def test_earthbreaker_moves_surviving_pair_once_but_damages_both(self):
        from backend import job_loadouts
        b,rider,boar,hero=self.charge_fixture(4)
        hero.update(x=1,y=2,attack=4)
        rider.update(x=4,y=2,hp=999,max_hp=999,displacement_resistance=0,knockback_resistance=0)
        boar.update(x=4,y=2,hp=999,max_hp=999)
        with patch.object(combat,'_attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            combat._resolve_ability(b,hero,combat._ground_target(3,2),deepcopy(job_loadouts.SKILLS['job:fighter:pull']))
        self.assertEqual((rider['x'],boar['x']),(6,6))
        self.assertLess(rider['hp'],999);self.assertLess(boar['hp'],999)
        moves=[e for e in b['animation_events'] if e['type']=='movement' and e.get('forced')]
        self.assertEqual(len(moves),1)
        self.assertEqual(moves[0]['mount_partner_id'],boar['id'])

    def test_attack_facing_is_saved_and_unrelated_attack_cannot_turn_enemy_mount(self):
        b,rider,boar,target=self.charge_fixture(1)
        boar['mount_facing']='n'
        with patch.object(combat,'_attack_hits',return_value=(False,{'damage_bonus':0,'chance':100},100)):
            combat._perform_attack(b,rider,target,'melee')
            self.assertEqual(boar['mount_facing'],'e')
            hero=deepcopy(target);hero.update(id='hero',x=5,y=5)
            b['units']['hero']=hero
            combat._perform_attack(b,hero,rider,'melee')
        self.assertEqual(boar['mount_facing'],'e')
        saved=json.loads(json.dumps(b))
        self.assertEqual(saved['units'][boar['id']]['mount_facing'],'e')

    def test_knockback_does_not_change_mount_facing(self):
        b,rider,boar,target=self.charge_fixture(4)
        boar['mount_facing']='n'
        target.update(x=0,y=1)
        combat._apply_displacement(b,target,rider,{'mode':'push','distance':1,'ignore_resistance':True})
        self.assertEqual(rider['x'],2)
        self.assertEqual(boar['mount_facing'],'n')

    def test_unrelated_player_movement_preserves_enemy_mount_facing(self):
        b,rider,boar,player=self.charge_fixture(4)
        boar['mount_facing']='w'
        player.update(moved=False,acted=False)
        b.update(turn_order=[player['id'],rider['id']],turn_index=0)
        combat.apply_player_command(b,{'action':'move','unit_id':player['id'],'x':5,'y':2})
        self.assertEqual(boar['mount_facing'],'w')
        self.assertEqual((boar['x'],boar['y']),(1,1))

    def charge_fixture(self,distance):
        b=self.battle();rider,boar=self.pair(b)
        b['terrain']=[];b['objects']={};b['zones']=[]
        target=deepcopy(rider)
        target.update(id='charge-target',team='player',x=1+distance,y=1,hp=999,max_hp=999,statuses=[],armor=0,evasion=0)
        target.pop('animal_mount_id',None)
        rider.update(x=1,y=1,acted=False,statuses=[],ability_activation=1)
        boar.update(x=1,y=1)
        b['units']={rider['id']:rider,boar['id']:boar,target['id']:target}
        return b,rider,boar,target

    def test_charge_is_rider_skill_and_dismount_removes_it(self):
        b,rider,boar,target=self.charge_fixture(4)
        mounts.ensure_skill(rider)
        self.assertIn('innate:rider:boar_charge',[s['id'] for s in rider['skills']])
        self.assertEqual(boar['skills'],[])
        mounts.unlink(rider,boar)
        self.assertNotIn('innate:rider:boar_charge',[s['id'] for s in rider['skills']])

    def test_charge_scales_distance_moves_pair_and_stuns_only_at_four(self):
        for distance in range(1,5):
            with self.subTest(distance=distance):
                b,rider,boar,target=self.charge_fixture(distance)
                choice=mounts.charge_skill()
                previews=mounts.previews(b,rider,choice)
                self.assertEqual(previews[target['id']]['charge_power'],100+25*distance)
                with patch.object(combat,'_attack_hits',return_value=(True,{'damage_bonus':0},1)):
                    mounts.charge(b,rider,target,choice)
                self.assertEqual(rider['x'],distance)
                self.assertEqual((boar['x'],boar['y']),(rider['x'],rider['y']))
                self.assertEqual(conditions.has(target,'stun'),distance==4)
                self.assertTrue(rider['acted'])
                self.assertEqual(rider['ability_state'][choice['id']]['ready_at'],4)

    def test_charge_cannot_cross_units_or_target_diagonally(self):
        b,rider,boar,target=self.charge_fixture(4)
        blocker=deepcopy(target);blocker.update(id='blocker',x=2,y=1)
        b['units']['blocker']=blocker
        self.assertIsNone(mounts.charge_route(b,rider,target))
        with self.assertRaises(ValueError):mounts.charge(b,rider,target,mounts.charge_skill())
        self.assertEqual(rider['x'],1)
        b['units'].pop('blocker');target['y']=2
        self.assertIsNone(mounts.charge_route(b,rider,target))

    def test_charge_miss_or_stun_immunity_prevents_stun(self):
        for hit,resist in ((False,0),(True,100)):
            b,rider,boar,target=self.charge_fixture(4)
            target['perk_modifiers']={'stun_resistance':resist}
            with patch.object(combat,'_attack_hits',return_value=(hit,{'damage_bonus':0,'chance':100},1)):
                mounts.charge(b,rider,target,mounts.charge_skill())
            self.assertFalse(conditions.has(target,'stun'))

    def test_charge_stops_if_mount_dies_in_hazard_before_hit(self):
        b,rider,boar,target=self.charge_fixture(4)
        def hazard(battle,unit):
            boar.update(hp=0,alive=False,conscious=False)
            mounts.defeat(battle,boar)
        with patch.object(combat,'_apply_tile_entry',side_effect=hazard), patch.object(mounts,'fall_outcome',return_value='safe'), patch.object(combat,'_perform_attack') as attack:
            result=mounts.charge(b,rider,target,mounts.charge_skill())
        self.assertTrue(result['interrupted'])
        attack.assert_not_called()
        self.assertEqual(target['hp'],999)

    def battle(self):
        seed=layout_presets('contract:goblin_boar_riders')[0]['seed']
        return combat.create_contract_battle(new_game({'name':'QA'}),['player'],seed,'goblin_boar_riders',True)

    def pair(self,b):
        rider=next(u for u in b['units'].values() if u.get('animal_mount_id'))
        return rider,b['units'][rider['animal_mount_id']]

    def test_real_bodies_survive_save_and_have_one_combined_activation(self):
        b=json.loads(json.dumps(self.battle()));rider,boar=self.pair(b)
        self.assertEqual((boar['x'],boar['y']),(rider['x'],rider['y']))
        self.assertEqual(boar['hp'],16)
        self.assertEqual(combat._movement_limit(rider),rider['move']+1)
        self.assertIn('rider',rider['recruitable_snapshot']['traits'])
        self.assertEqual(len(rider['skill_slot_order']),len(rider['recruitable_snapshot']['equipped_skills']))
        b['turn_order']=[boar['id'],rider['id']];b['turn_index']=0
        self.assertEqual(combat._current_unit(b)['id'],rider['id'])
        self.assertEqual(b['turn_index'],1)
        self.assertEqual(boar['ability_activation'],1)

    def test_both_bodies_have_mitigation_but_damage_stays_independent(self):
        b=self.battle();rider,boar=self.pair(b)
        source={'id':'test','name':'Test','status_tick':True,'attack':8,'weapon':'hazard'}
        before=rider['hp']
        self.assertEqual(combat._deal_damage(b,source,boar,resolved_damage=8),6)
        self.assertEqual(boar['hp'],10)
        self.assertEqual(rider['hp'],before)
        self.assertEqual(combat._deal_damage(b,source,rider,resolved_damage=8),6)

    def test_killing_boar_causes_exactly_one_fall_and_no_lethal_rider_transfer(self):
        b=self.battle();rider,boar=self.pair(b);hp=rider['hp']
        source={'id':'test','name':'Test','status_tick':True,'attack':100,'weapon':'hazard'}
        with patch.object(mounts,'fall_outcome',return_value='hard'):
            combat._deal_damage(b,source,boar,resolved_damage=100)
        self.assertFalse(boar['alive'])
        self.assertNotIn('animal_mount_id',rider)
        self.assertEqual(rider['hp'],hp-8)
        self.assertTrue(conditions.has(rider,'stun'))
        self.assertTrue(rider['alive'])
        events=b['animation_events'];death=next(i for i,e in enumerate(events) if e.get('type')=='death_burst' and e.get('unit_id')==boar['id'])
        fall=next(i for i,e in enumerate(events) if e.get('type')=='mount_fall')
        self.assertGreater(fall,death)
        before=rider['hp'];mounts.defeat(b,boar);self.assertEqual(rider['hp'],before)

    def test_damage_and_decay_tick_mount_once_per_rider_activation(self):
        b=self.battle();rider,boar=self.pair(b)
        conditions.add_stack(boar,'poison',2,rider)
        conditions.add_stack(boar,'poison',2,rider)
        mounts.start(b,rider,[1,2]);hp=boar['hp']
        mounts.finish(b,rider)
        self.assertLess(boar['hp'],hp)
        self.assertEqual(next(s for s in boar['statuses'] if s['id']=='poison')['stacks'],1)
        after=boar['hp'];mounts.finish(b,rider)
        self.assertEqual(boar['hp'],after)
        self.assertTrue(conditions.has(boar,'poison'))

    def test_mount_dismount_is_quick_once_per_activation_and_no_slot_replacement(self):
        b=self.battle();rider,boar=self.pair(b)
        rider['ability_activation']=1;mounts.ensure_skill(rider)
        slots=[s['id'] for s in rider['skills'] if not s.get('mount_kind')]
        self.assertIn(rider['id'],mounts.previews(b,rider,mounts.skill(rider)))
        mounts.command(b,rider,mounts.skill(rider),{'target_id':rider['id']})
        self.assertFalse(rider.get('acted'))
        self.assertFalse(rider.get('animal_mount_id'))
        with self.assertRaises(ValueError):mounts.command(b,rider,mounts.skill(rider),{'target_id':boar['id']})
        rider['ability_activation']=2
        mounts.command(b,rider,mounts.skill(rider),{'target_id':boar['id']})
        self.assertEqual(rider['animal_mount_id'],boar['id'])
        self.assertEqual(slots,[s['id'] for s in rider['skills'] if not s.get('mount_kind')])
        self.assertFalse(rider.get('acted'))

    def test_mount_rejects_a_hostile_animal(self):
        b=self.battle();rider,boar=self.pair(b)
        mounts.dismount(b,rider)
        self.assertTrue(mounts.legal(b,rider,boar))
        boar['team']='player'
        self.assertFalse(mounts.legal(b,rider,boar))

    def test_movement_and_forced_movement_share_coordinates(self):
        b=self.battle();rider,boar=self.pair(b)
        start=(rider['x'],rider['y']);rider['x']+=1
        combat._record_movement(b,rider,start,[(rider['x'],rider['y'])])
        self.assertEqual((rider['x'],rider['y']),(boar['x'],boar['y']))
        self.assertEqual(b['animation_events'][-1]['mount_partner_id'],boar['id'])
        self.assertFalse(combat._blocked(b,boar['x'],boar['y'],rider['id']))

    def test_rider_defeat_releases_living_boar_without_a_fall(self):
        b=self.battle();rider,boar=self.pair(b)
        combat._deal_damage(b,{'id':'test','name':'Test','status_tick':True,'attack':100,'weapon':'Test'},rider,resolved_damage=100)
        self.assertTrue(boar['alive'])
        self.assertFalse(boar.get('rider_id'))
        self.assertFalse(any(e.get('type')=='mount_fall' for e in b['animation_events']))

    def test_api_dismount_is_targeted_quick_and_preserves_main_action(self):
        b=self.battle();rider,boar=self.pair(b)
        rider.update(team='player',is_player=True,loyalty=100)
        boar['team']='player'
        b.update(turn_order=[rider['id']],turn_index=0)
        combat._current_unit(b)
        view=combat.apply_player_command(b,{'action':'skill','skill_id':'innate:rider:mount','target_id':rider['id']})
        self.assertEqual(view['current_unit_id'],rider['id'])
        self.assertFalse(rider.get('acted'))
        self.assertFalse(rider.get('animal_mount_id'))
        self.assertEqual(next(s for s in view['units'][rider['id']]['skills'] if s.get('mount_kind'))['name'],'Mount')

    def test_fall_on_riders_own_activation_interrupts_remaining_actions(self):
        b=self.battle();rider,boar=self.pair(b)
        b.update(turn_order=[rider['id']],turn_index=0)
        combat._current_unit(b)
        with patch.object(mounts,'fall_outcome',return_value='hard'):
            combat._deal_damage(b,{'id':'test','name':'Test','status_tick':True,'attack':100,'weapon':'Test'},boar,resolved_damage=100)
        self.assertTrue(rider['mount_interrupted'])
        self.assertTrue(rider['forced_skip'])
        self.assertEqual(combat._movement_limit(rider),0)

    def test_rough_landing_uses_mount_hp_and_hobbles_without_skipping_action(self):
        b=self.battle();rider,boar=self.pair(b);hp=rider['hp']
        b.update(turn_order=[rider['id']],turn_index=0)
        combat._current_unit(b)
        boar['max_hp']=18;boar['hp']=1
        with patch.object(mounts,'fall_outcome',return_value='rough'):
            combat._deal_damage(b,{'id':'test','name':'Test','status_tick':True,'attack':100,'weapon':'Test'},boar,resolved_damage=100)
        self.assertEqual(rider['hp'],hp-5)
        self.assertTrue(conditions.has(rider,'hobbled'))
        self.assertFalse(conditions.has(rider,'stun'))
        self.assertFalse(rider.get('mount_interrupted'))
        self.assertFalse(rider.get('forced_skip'))
        self.assertFalse(rider.get('acted'))
        conditions.finish_activation(rider)
        self.assertTrue(conditions.has(rider,'hobbled'))
        rider['status_activation']=[2,0]
        conditions.finish_activation(rider)
        self.assertFalse(conditions.has(rider,'hobbled'))

    def test_clean_landing_removes_mount_without_damage_or_new_control(self):
        b=self.battle();rider,boar=self.pair(b);hp=rider['hp']
        with patch.object(mounts,'fall_outcome',return_value='safe'):
            combat._deal_damage(b,{'id':'test','name':'Test','status_tick':True,'attack':100,'weapon':'Test'},boar,resolved_damage=100)
        self.assertEqual(rider['hp'],hp)
        self.assertFalse(rider.get('animal_mount_id'))
        self.assertFalse(conditions.has(rider,'stun'))
        self.assertFalse(conditions.has(rider,'hobbled'))
        self.assertTrue(any('clean landing' in line for line in b['log']))

    def test_fall_chances_and_save_replay(self):
        b=self.battle();rider,boar=self.pair(b)
        restored=json.loads(json.dumps(b))
        self.assertEqual(mounts.fall_outcome(b,rider,boar),mounts.fall_outcome(restored,rider,boar))
        self.assertEqual(b['mount_fall_counter'],1)
        for roll,expected in ((0,'hard'),(24,'hard'),(25,'rough'),(74,'rough'),(75,'safe'),(99,'safe')):
            with patch('backend.combat_mounts.random.Random') as rng:
                rng.return_value.randrange.return_value=roll
                self.assertEqual(mounts.fall_outcome(b,rider,boar),expected)


if __name__=='__main__':unittest.main()
