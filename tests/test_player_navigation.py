import unittest
from unittest.mock import patch
from tests import test_combat_approach as fixtures
from backend.combat import apply_player_command, battle_view

class PlayerNavigationTests(unittest.TestCase):
    def fixture(self,position=(1,3),move=10):
        f=fixtures.AttackApproachTests();f.setUp();b=f.battle;a=f.actor
        a.update(x=position[0],y=position[1],move=move)
        for u in b['units'].values():
            if u['id']!=a['id']:u.update(x=7,y=7)
        b['terrain']=[{'id':f'wall{y}','name':'Wall','kind':'wall','x':3,'y':y,'blocking':True,'destructible':True,'hp':30,'max_hp':30} for y in range(b['height']) if y not in (2,4)]
        b['terrain'].append({'id':'door','name':'Workshop Door','kind':'gate','x':3,'y':2,'blocking':True,'destructible':True,'hp':30,'max_hp':30,'state':'closed','closed_sprite':'closed','open_sprite':'open','sprite':'closed'})
        return b,a
    def test_door_is_free_once_per_activation_and_movement_remains_available(self):
        from backend import combat
        b,a=self.fixture((2,2));a['ability_activation']=1
        before_index=b['turn_index']
        apply_player_command(b,{'action':'interact','target_id':'door'})
        self.assertFalse(a['acted']);self.assertEqual(b['turn_index'],before_index)
        self.assertTrue(battle_view(b)['door_controls'][0]['disabled'])
        with self.assertRaisesRegex(ValueError,'once per activation'):
            combat._interact(b,a,'door')
        apply_player_command(b,{'action':'move','x':3,'y':2})
        self.assertEqual((a['x'],a['y']),(3,2));self.assertFalse(a['acted'])
        a.update(x=2,y=2,ability_activation=a.get('ability_activation',0)+1)
        combat._interact(b,a,'door')
        self.assertEqual(b['terrain'][-1]['state'],'closed')

    def test_door_commits_approach_cost_without_refilling_movement(self):
        for navigate in (False,True):
            b,a=self.fixture((1,2),move=3)
            b['terrain'][-1]['rotation']=90
            with patch('backend.combat._advance_to_player'):
                if navigate:
                    view=apply_player_command(b,{'action':'navigate','gate_id':'door','x':2,'y':2,'operate_gate':True,'gate_operation':'Open'})
                else:
                    apply_player_command(b,{'action':'move','x':2,'y':2})
                    view=apply_player_command(b,{'action':'interact','target_id':'door'})
                self.assertEqual(view['movement_allowance'],2)
                self.assertNotIn('movement_origin',a)
                self.assertFalse(a['acted'])
                apply_player_command(b,{'action':'move','x':4,'y':2})
                with self.assertRaises(ValueError):
                    apply_player_command(b,{'action':'move','x':5,'y':2})
            a['ability_activation']=a.get('ability_activation',0)+1
            a.pop('movement_origin',None);a.pop('movement_path',None)
            self.assertEqual(battle_view(b)['movement_allowance'],3)

    def test_door_spends_terrain_cost_and_can_leave_zero_movement(self):
        b,a=self.fixture((1,2),move=2)
        b['terrain'].append({'id':'mud','kind':'mud','x':2,'y':2,'movement_cost':2,'blocking':False})
        with patch('backend.combat._advance_to_player'):
            apply_player_command(b,{'action':'move','x':2,'y':2})
            view=apply_player_command(b,{'action':'interact','target_id':'door'})
        self.assertEqual(view['movement_allowance'],0)
        self.assertFalse(a['acted'])
        self.assertEqual(b['terrain'][-2]['state'],'opened')

    def test_enemy_opens_door_and_attacks_in_same_activation(self):
        from backend import combat
        from copy import deepcopy
        b,a=self.fixture((2,2));a.update(team='enemy',ability_activation=1,attack_range=1,attack_elevation_rule='melee',skills=[],special=None,passives=[],job_id='fighter');b['terrain'][-1].update(rotation=90,blocks_sight=True)
        target=deepcopy(a);target.update(id='target',team='player',x=4,y=2,hp=100,max_hp=100)
        b['units']={a['id']:a,target['id']:target};b['turn_order']=[a['id'],'target'];b['turn_index']=0
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            combat._enemy_turn(b,a)
        self.assertEqual(b['terrain'][-1]['state'],'opened')
        self.assertLess(target['hp'],100)

    def test_animals_break_closed_doors_and_end_turn_before_pursuing(self):
        from backend import combat
        from copy import deepcopy
        for profile in ('fence_wolf','store_rat','foraging_bear','saddle_boar'):
            for position in ((1,2),(2,2)):
                for hp in (1,100):
                    b,a=self.fixture(position,move=3)
                    a.update(team='enemy',ability_activation=1,attack_range=1,attack_elevation_rule='melee',skills=[],special=None,passives=[],job_id='fighter',species_profile=profile)
                    gate=b['terrain'][-1];gate.update(rotation=90,blocks_sight=True,hp=hp,max_hp=hp)
                    target=deepcopy(a);target.update(id='target',team='player',species_profile=None,x=4,y=2,hp=100,max_hp=100)
                    b['units']={a['id']:a,'target':target};b['turn_order']=[a['id'],'target'];b['turn_index']=0
                    combat._enemy_turn(b,a)
                    self.assertEqual(gate['state'],'closed')
                    self.assertLess(gate['hp'],hp)
                    self.assertEqual(a['x'],2)
                    self.assertEqual(target['hp'],100)
                    self.assertEqual(b['turn_index'],1)
                    if gate.get('destroyed'):
                        a.update(acted=False,ability_activation=2);b['turn_index']=0
                        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
                            combat._enemy_turn(b,a)
                        self.assertLess(target['hp'],100)

    def test_wolf_resumes_normal_pursuit_when_someone_opens_door(self):
        from backend import combat
        from copy import deepcopy
        b,a=self.fixture((2,2),move=3)
        a.update(team='enemy',ability_activation=1,attack_range=1,attack_elevation_rule='melee',skills=[],special=None,passives=[],job_id='fighter',species_profile='fence_wolf')
        gate=b['terrain'][-1];gate.update(rotation=90)
        target=deepcopy(a);target.update(id='target',team='player',species_profile=None,x=4,y=2,hp=100,max_hp=100)
        b['units']={a['id']:a,'target':target};b['turn_order']=[a['id'],'target'];b['turn_index']=0
        with self.assertRaisesRegex(ValueError,'Animals cannot'):
            combat._interact(b,a,'door')
        gate.update(state='opened',blocking=False,blocks_sight=False)
        with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
            combat._enemy_turn(b,a)
        self.assertLess(target['hp'],100)
        self.assertEqual(gate['hp'],30)

    def navigate(self,b,x,y):
        with patch('backend.combat._advance_to_player'):
            return apply_player_command(b,{'action':'navigate','x':x,'y':y})
    def test_door_intent_chooses_near_side_from_inside_and_outside(self):
        for position,expected in (((1,2),(2,2)),((5,2),(4,2))):
            b,a=self.fixture(position)
            b['terrain'][-1]['rotation']=90
            with patch('backend.combat._advance_to_player'):
                view=apply_player_command(b,{'action':'navigate','gate_id':'door','x':2,'y':2})
            self.assertEqual((a['x'],a['y']),expected)
            self.assertFalse(a.get('acted',False))
            self.assertEqual(b['terrain'][-1]['state'],'closed')
    def test_one_click_approaches_and_operates_from_either_side(self):
        for position in ((1,2),(5,2)):
            for opened in (False,True):
                b,a=self.fixture(position);gate=b['terrain'][-1]
                gate.update(rotation=90,state='opened' if opened else 'closed',blocking=not opened)
                with patch('backend.combat._advance_to_player'):
                    apply_player_command(b,{'action':'navigate','gate_id':'door','x':2,'y':2,
                        'operate_gate':True,'gate_operation':'Close' if opened else 'Open'})
                self.assertEqual(gate['state'],'closed' if opened else 'opened')
                self.assertFalse(a['acted'])
                kinds=[e['type'] for e in b['animation_events']]
                self.assertIn('movement',kinds)

    def test_short_movement_does_not_operate_a_distant_door(self):
        b,a=self.fixture((0,2),1);gate=b['terrain'][-1];gate['rotation']=90
        apply_player_command(b,{'action':'navigate','gate_id':'door','x':2,'y':2,'operate_gate':True,'gate_operation':'Open'})
        self.assertEqual((a['x'],a['y']),(1,2))
        self.assertEqual(gate['state'],'closed');self.assertFalse(a['acted'])

    def test_combined_position_operates_without_a_second_request(self):
        b,a=self.fixture((1,2));gate=b['terrain'][-1];gate['rotation']=90
        with patch('backend.combat._advance_to_player'):
            apply_player_command(b,{'action':'navigate','gate_id':'door','x':2,'y':2,'position':{'x':2,'y':2},'operate_gate':True,'gate_operation':'Open'})
        self.assertEqual(gate['state'],'opened');self.assertFalse(a['acted'])

    def test_hazard_interruption_prevents_automatic_operation(self):
        b,a=self.fixture((1,2));gate=b['terrain'][-1];gate['rotation']=90
        def interrupted(*args,**kwargs):a['engineer_interrupted']=True
        with patch('backend.combat._commit_player_movement',side_effect=interrupted):
            apply_player_command(b,{'action':'navigate','gate_id':'door','x':2,'y':2,
                'operate_gate':True,'gate_operation':'Open'})
        self.assertEqual(gate['state'],'closed');self.assertFalse(a['acted'])

    def test_stale_open_intent_never_closes_an_already_opened_door(self):
        b,a=self.fixture((2,2));gate=b['terrain'][-1]
        gate.update(rotation=90,state='opened',blocking=False)
        apply_player_command(b,{'action':'navigate','gate_id':'door','x':2,'y':2,
            'operate_gate':True,'gate_operation':'Open'})
        self.assertEqual(gate['state'],'opened');self.assertFalse(a['acted'])
    def test_equal_distance_prefers_open_entrance_without_opening_door(self):
        b,a=self.fixture();view=self.navigate(b,5,3)
        self.assertEqual((a['x'],a['y']),(5,3))
        self.assertEqual(b['terrain'][-1]['state'],'closed')
        self.assertNotIn('navigation_prompt',view)
        self.assertTrue(any(p['x']==3 and p['y']==4 for p in a['movement_path']))
    def test_closed_shortcut_is_offered_even_when_a_longer_open_route_is_in_range(self):
        b,a=self.fixture((1,2));view=battle_view(b)
        self.assertIn({'x':5,'y':2},view['reachable'])
        self.assertEqual(view['navigation_doors'].get('5,2'),'door')
        view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2))

    def test_nearer_closed_door_stops_beside_it_and_prompts_explicit_open(self):
        b,a=self.fixture((1,2));view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2));self.assertFalse(a.get('acted',False))
        self.assertEqual(view['navigation_prompt']['command'],{'action':'interact','target_id':'door'})
        self.assertEqual(b['terrain'][-1]['state'],'closed')
        with patch('backend.combat._advance_to_player'):
            opened=apply_player_command(b,view['navigation_prompt']['command'])
        self.assertEqual(b['terrain'][-1]['state'],'opened')
        self.assertNotIn('navigation_prompt',opened)
    def test_insufficient_movement_advances_toward_nearest_door_within_start_budget(self):
        b,a=self.fixture((0,2),1);view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(1,2));self.assertNotIn('navigation_prompt',view)
        self.assertEqual(a['movement_origin'],{'x':0,'y':2})
    def test_sealed_building_does_not_route_through_wall(self):
        b,a=self.fixture();b['terrain'].extend({'id':f'fill{y}','name':'Wall','kind':'wall','x':3,'y':y,'blocking':True} for y in (2,4));b['terrain']=[t for t in b['terrain'] if t['kind']!='gate']
        with self.assertRaises(ValueError):self.navigate(b,5,3)
        self.assertEqual((a['x'],a['y']),(1,3))

    def test_edge_mounted_door_stops_on_its_approach_side(self):
        b,a=self.fixture((1,2));b['terrain']=[t for t in b['terrain'] if t['kind']!='gate']
        door={'id':'edge-door','name':'Door','kind':'gate','x':2,'y':2,'edge_wall':True,'wall_edges':['east'],'blocking':True,'state':'closed','hp':30,'max_hp':30,'destructible':True,'closed_sprite':'closed','open_sprite':'open'}
        b['terrain'].append(door)
        # Seal the other entrance; the sole passage crosses this east boundary.
        b['terrain'].extend({'id':f'seal{y}','kind':'wall','x':3,'y':y,'blocking':True} for y in (4,))
        view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2))
        self.assertEqual(view['navigation_prompt']['command']['target_id'],'edge-door')

    def test_npc_in_closed_door_does_not_hide_the_open_option_or_allow_overlap(self):
        b,a=self.fixture((1,2));npc=next(u for u in b['units'].values() if u['id']!=a['id']);npc.update(x=3,y=2,conscious=True)
        view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2))
        self.assertEqual(view['navigation_prompt']['command']['target_id'],'door')
        self.assertEqual((npc['x'],npc['y']),(3,2))
        for _ in range(25):view=self.navigate(b,5,2)
        self.assertEqual((a['x'],a['y']),(2,2));self.assertEqual(b['terrain'][-1]['state'],'closed')
