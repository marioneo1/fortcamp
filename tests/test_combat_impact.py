import unittest
from copy import deepcopy
from unittest.mock import patch
from tests import test_combat_abilities as ability_tests
from backend import combat_conditions as conditions, combat_spaces as spaces
from backend.combat import (_apply_displacement, _deal_damage, _resolve_ability,
                           _trigger_zones, _tick_gear_statuses, battle_view)


class CombatImpactTests(unittest.TestCase):
    def fixture(self):
        b,a,t=ability_tests.AbilityFoundationTests().fixture()
        t.update(displacement_resistance=0,statuses=[],boss=False)
        for u in b['units'].values():
            if u['id'] not in {a['id'],t['id']}:u.update(x=7,y=6)
        b['animation_events']=[]
        return b,a,t

    def test_wall_collision_half_resolved_damage_ignores_armor_but_uses_barrier(self):
        b,a,t=self.fixture();t['armor']=90
        b['terrain']=[{'id':'wall','x':4,'y':2,'blocking':True}]
        conditions.barrier(t,3,2,a)
        _apply_displacement(b,a,t,{'mode':'push','distance':2},original_damage=20)
        self.assertEqual(t['hp'],93)
        event=next(e for e in b['animation_events'] if e.get('kind')=='collision')
        self.assertEqual((event['amount'],event['absorbed']),(7,3))

    def test_collision_hurts_both_people_and_never_pushes_second_person(self):
        b,a,t=self.fixture();other=deepcopy(t)
        other.update(id='bystander',name='Bystander',team='player',x=5,y=2,hp=100)
        b['units'][other['id']]=other
        _apply_displacement(b,a,t,{'mode':'push','distance':3},original_damage=20,attack_packet=7)
        self.assertEqual((t['x'],t['hp'],other['x'],other['hp']),(4,90,5,90))
        events=[e for e in b['animation_events'] if e.get('kind')=='collision']
        self.assertEqual(len(events),2)
        self.assertTrue(all(e['attack_packet']==7 and e['after_displacement'] for e in events))
        self.assertEqual(a.get('combat_record',{}).get('total_damage'),10)

    def test_wall_prevents_damage_to_person_behind_it(self):
        b,a,t=self.fixture();other=deepcopy(t);other.update(id='behind',x=4,hp=100)
        b['units'][other['id']]=other;b['terrain']=[{'id':'wall','x':4,'y':2,'blocking':True}]
        _apply_displacement(b,a,t,{'mode':'push','distance':2},original_damage=20)
        self.assertEqual((t['hp'],other['hp']),(90,100))

    def test_resistance_map_edge_and_miss_do_not_create_collision_damage(self):
        for case in ('resist','edge','miss'):
            b,a,t=self.fixture()
            if case=='resist':t['displacement_resistance']=100;b['terrain']=[{'x':4,'y':2,'blocking':True}]
            elif case=='edge':t['x']=b['width']-1
            else:b['terrain']=[{'x':4,'y':2,'blocking':True}]
            _apply_displacement(b,a,t,{'mode':'push','distance':2},original_damage=0 if case=='miss' else 20)
            self.assertEqual(t['hp'],100)

    def test_attack_packet_orders_hit_before_damage_and_forced_movement(self):
        b,a,t=self.fixture()
        skill={**deepcopy(a['skills'][0]),'elevation_rule':'melee','effects':[{'type':'attack'},
            {'type':'displace','mode':'push','distance':1,'conditions':[{'type':'hit'}]}]}
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            _resolve_ability(b,a,t,skill)
        events=b['animation_events']
        hit=next(e for e in events if e['type']=='melee_attack')
        movement=next(e for e in events if e['type']=='movement' and e.get('forced'))
        damage=next(e for e in events if e['type']=='combat_feedback')
        self.assertEqual(hit['attack_packet'],movement['attack_packet'])
        self.assertEqual(hit['attack_packet'],damage['attack_packet'])
        self.assertLess(events.index(hit),events.index(damage))
        self.assertEqual(hit['to'],{'x':3,'y':2})

    def test_ember_entries_add_stacks_start_is_free_and_end_ticks(self):
        b,a,t=self.fixture()
        spaces.place_zone(b,a,{'zone':'ember','turns':2},[{'x':t['x'],'y':t['y']}])
        _trigger_zones(b,t,'entry');self.assertEqual(t['hp'],98)
        _trigger_zones(b,t,'entry');_trigger_zones(b,t,'start');self.assertEqual(t['hp'],94)
        self.assertTrue(conditions.has(t,'burn'))
        t['status_activation']=['next',1];_trigger_zones(b,t,'start');_tick_gear_statuses(b,t)
        self.assertEqual(t['hp'],90)
        self.assertEqual([e['kind'] for e in b['animation_events'] if e['type']=='combat_feedback'],['burn','burn','burn'])
        a['hp']=80;_trigger_zones(b,a,'entry');self.assertEqual(a['hp'],80)

    def test_ember_route_counts_every_burned_cell_and_reentry_not_overlap(self):
        from backend.combat import _apply_zone_route, _record_movement
        b,a,t=self.fixture()
        cells=[{'x':4,'y':2},{'x':5,'y':2}]
        spaces.place_zone(b,a,{'zone':'ember','turns':2},cells)
        other=deepcopy(a);other.update(id='other',name='Other',x=7,y=7)
        b['units'][other['id']]=other
        spaces.place_zone(b,other,{'zone':'ember','turns':2},cells)
        path=[(4,2),(5,2),(4,2),(5,2),(6,2)]
        _record_movement(b,t,(t['x'],t['y']),path)
        t.update(x=6,y=2)
        _apply_zone_route(b,t,path)
        self.assertEqual(t['hp'],80)
        self.assertEqual((t['x'],t['y']),(6,2))
        hits=[e for e in b['animation_events'] if e.get('kind')=='burn']
        self.assertEqual([e['amount'] for e in hits],[2,4,6,8])
        self.assertEqual([(e['x'],e['y']) for e in hits],[(4,2),(5,2),(4,2),(5,2)])
        self.assertEqual([e['ground_step'] for e in hits],[1,2,3,4])
        movement=next(e for e in b['animation_events'] if e['type']=='movement')
        self.assertTrue(all(e['ground_route_id']==movement['ground_route_id'] for e in hits))

    def test_ember_checks_intermediate_tiles_and_stops_at_lethal_entry(self):
        from backend.combat import _apply_zone_route
        b,a,t=self.fixture();t.update(x=6,y=2,hp=5)
        spaces.place_zone(b,a,{'zone':'ember','turns':2},[{'x':4,'y':2},{'x':5,'y':2}])
        _apply_zone_route(b,t,[(4,2),(5,2),(6,2)])
        self.assertEqual((t['x'],t['y'],t['hp']),(5,2,0))

    def test_damage_number_is_actual_loss_not_overkill_and_view_is_read_only(self):
        b,a,t=self.fixture();t['hp']=3
        _deal_damage(b,{**a,'attack':99,'on_hit':None,'element':None},t)
        event=next(e for e in b['animation_events'] if e['type']=='combat_feedback')
        self.assertEqual(event['amount'],3)
        before=deepcopy(b);battle_view(b);battle_view(b);self.assertEqual(b,before)

    def test_collision_animation_identifies_obstacle_and_preserves_final_occupancy(self):
        b,a,t=self.fixture()
        b['terrain']=[{'id':'wall','x':5,'y':2,'blocking':True}]
        _apply_displacement(b,a,t,{'mode':'push','distance':3},original_damage=20,attack_packet=8)
        recoil=next(e for e in b['animation_events'] if e['type']=='collision_recoil')
        self.assertEqual((t['x'],t['y']),(4,2))
        self.assertEqual(recoil['toward'],{'x':5,'y':2})
        self.assertTrue(recoil['after_displacement'])
        self.assertEqual(recoil['attack_packet'],8)

    def test_barrier_break_is_reported_only_when_the_shield_is_spent(self):
        b,a,t=self.fixture()
        conditions.barrier(t,3,2,a)
        _deal_damage(b,{**a,'attack':50,'on_hit':None,'element':None},t)
        hit=next(e for e in b['animation_events'] if e['type']=='combat_feedback')
        self.assertTrue(hit['barrier_broken'])

    def test_guard_and_cleanse_have_feedback_without_invented_damage(self):
        b,a,t=self.fixture()
        t['statuses']=[{'id':'poison','turns':2}]
        skill={**deepcopy(a['skills'][0]),'target':'ally','effects':[
            {'type':'cleanse','statuses':['poison']},{'type':'guard'}]}
        _resolve_ability(b,a,t,skill)
        events=[e for e in b['animation_events'] if e['type']=='combat_feedback']
        self.assertEqual([e['kind'] for e in events],['cleanse','guard'])
        self.assertTrue(all(e['amount']==0 for e in events))
        self.assertEqual(t['hp'],100)

    def test_forced_crossing_over_ember_has_entry_damage(self):
        b,a,t=self.fixture()
        spaces.place_zone(b,a,{'zone':'ember','turns':2},[{'x':4,'y':2}])
        _apply_displacement(b,a,t,{'mode':'push','distance':2},original_damage=10)
        self.assertEqual((t['x'],t['hp']),(5,98))

    def test_fall_does_not_collide_with_wall_beyond_the_pit(self):
        b,a,t=self.fixture()
        b['terrain']=[{'id':'pit','kind':'pit','x':4,'y':2,'blocking':True,'requires_flying':True,'pit_kind':'shallow'},
                      {'id':'wall','x':5,'y':2,'blocking':True}]
        _apply_displacement(b,a,t,{'mode':'push','distance':2},original_damage=20)
        self.assertEqual(t['hp'],88)
        self.assertFalse(any(e.get('kind')=='collision' for e in b['animation_events']))

if __name__=='__main__':unittest.main()
