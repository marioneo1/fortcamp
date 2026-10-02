import unittest
from collections import deque
from copy import deepcopy

from backend.location_maps import MISSION_LOCATIONS, location_blueprint, place_building
from backend.building_templates import BUILDINGS, footprint, shell
from backend.location_templates import BUILDING_PLANS
from backend.battle_maps import compile_generated_battle_map, validate_battle_map, occupied_tiles
from backend.combat import create_contract_battle, _interact, _blocked, battle_view, _damage_terrain, _move_toward, _auto_open_gate, _flee_turn
from backend.game import new_game


class LocationMapTests(unittest.TestCase):
    def test_all_variants_have_clear_spawns_and_reachable_exits(self):
        for location in set(MISSION_LOCATIONS.values()):
            variants = set()
            for index in range(40):
                seed = f'layout-{index}'
                blueprint = location_blueprint(location,seed)
                self.assertEqual(blueprint,location_blueprint(location,seed))
                self.assertEqual(validate_battle_map(location,blueprint),[])
                variants.add(blueprint['map_variation'])
                blocked = {(v['x'],v['y']) for v in blueprint['void_tiles']}
                blocked |= {p for t in blueprint['terrain'] if t.get('blocking') for p in occupied_tiles(t)}
                spawns = [p for group in blueprint['spawn_zones'].values() for p in group]
                self.assertEqual(len({(p['x'],p['y']) for p in spawns}),len(spawns))
                self.assertTrue(all((p['x'],p['y']) not in blocked for p in spawns),location)
                # With gates opened, every spawn connects to its advertised exit.
                blocked -= {p for t in blueprint['terrain'] if t['kind']=='gate' for p in occupied_tiles(t)}
                exits = {(p['x'],p['y']) for p in blueprint['extraction']['tiles']+blueprint['enemy_extraction']['tiles']}
                for spawn in spawns:
                    seen={(spawn['x'],spawn['y'])};queue=deque(seen)
                    while queue:
                        x,y=queue.popleft()
                        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                            if 0<=p[0]<blueprint['width'] and 0<=p[1]<blueprint['height'] and p not in blocked|seen:
                                seen.add(p);queue.append(p)
                    self.assertTrue(seen&exits,(location,spawn))
            self.assertEqual(variants,set(range(1,len(BUILDING_PLANS.get(location,[None,None]))+1)),location)

    def test_river_is_continuous_and_bridge_is_walkable_floor(self):
        board=compile_generated_battle_map('location_broken_creek_bridge','bridge')
        materials={(t['x'],t['y']):t['material'] for t in board['ground_tiles']}
        water={(t['x'],t['y']) for t in board['void_tiles']}
        self.assertEqual({p for p,m in materials.items() if m=='deep_river'},water)
        decks={p for p,m in materials.items() if m.startswith('wood_bridge')}
        self.assertEqual(len(decks),5)
        upper=min(y for x,y in decks)
        self.assertEqual(materials[(7,upper)],'deep_river')
        self.assertEqual(materials[(7,upper+1)],'wood_bridge_damaged')
        self.assertFalse(any(t.get('sprite')=='bridge' for t in board['terrain']))
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'bridge','timber_creek',True)
        self.assertTrue(_blocked(battle,7,upper,'player'))
        self.assertFalse(_blocked(battle,7,upper,'player','flying'))
        self.assertFalse(_blocked(battle,7,upper+1,'player'))

    def test_enemy_plans_for_a_door_but_can_prefer_a_short_breach(self):
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'gate','tool_shed',True)
        enemy=battle['units']['contract_enemy_0'];target=battle['units']['player']
        for unit in battle['units'].values():unit['extracted']=True
        enemy.update(x=5,y=4,extracted=False,move=4,movement=4,attack_range=1)
        target.update(x=2,y=4,extracted=False)
        battle['terrain']=[{'id':f'wall_{y}','kind':'wall','x':4,'y':y,'blocking':True,'blocks_sight':True}
                           for y in range(11) if y not in (4,10)]
        gate={'id':'test_gate','kind':'gate','name':'Door','x':4,'y':4,'state':'closed',
              'blocking':True,'blocks_sight':True,'open_sprite':'open','closed_sprite':'closed'}
        battle['terrain'].append(gate);battle['void_tiles']=[]
        self.assertTrue(_auto_open_gate(battle,enemy,target))
        self.assertEqual(gate['state'],'opened');self.assertTrue(enemy['acted'])
        gate.update(state='closed',blocking=True,blocks_sight=True)
        enemy.update(x=7,y=4,acted=False,moved=False)
        _move_toward(battle,enemy,target)
        self.assertEqual((enemy['x'],enemy['y']),(5,4))
        self.assertEqual(gate['state'],'closed') # cannot walk through a shut door
        battle['enemy_extraction']={'name':'Road','tiles':[{'x':0,'y':4}]}
        _flee_turn(battle,enemy)
        self.assertEqual(gate['state'],'opened') # panicked units can escape an enclosed room too
        gate.update(state='closed',blocking=True,blocks_sight=True)
        battle['terrain']=[t for t in battle['terrain'] if t['id']!='wall_5']
        self.assertFalse(_auto_open_gate(battle,enemy,target))
        _move_toward(battle,enemy,target)
        self.assertEqual(gate['state'],'closed')
        self.assertLess(enemy['x'],4) # nearby breach is cheaper than an opening action

    def test_templates_change_geometry_and_offsets_survive_destruction(self):
        layouts={location_blueprint('repair_yard',f'layout-{i}')['template_id'] for i in range(40)}
        self.assertEqual(len(layouts),4)
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'offset','tool_shed',True)
        segment=next(t for t in battle['terrain'] if t.get('art_offset'))
        offset=segment['art_offset'][:]
        player=battle['units']['player'];player['attack']=100
        _damage_terrain(battle,player,segment['id'])
        self.assertEqual(segment['art_offset'],offset)

    def test_enclosure_is_closed_except_door_and_shed_collapse(self):
        for ident,template in BUILDINGS.items():
            building=place_building(ident,(3,2),'test')
            covered={(t['x']-3,t['y']-2) for t in building['terrain'] if t['id'].startswith('test_wall') or t['kind']=='gate'}
            self.assertTrue(set(shell(template))<=covered,ident)
            gate_count=len(template['doors'])+len(template.get('internal_doors',[]))
            self.assertEqual(sum(t['kind']=='gate' for t in building['terrain']),gate_count)

    def test_building_shapes_are_distinct_not_mirrors_and_instances_can_be_reused(self):
        def signature(cells):
            variants=[]
            for swap in (False,True):
                for sx,sy in ((1,1),(-1,1),(1,-1),(-1,-1)):
                    points={(sx*(y if swap else x),sy*(x if swap else y)) for x,y in cells}
                    ox=min(x for x,y in points);oy=min(y for x,y in points)
                    variants.append(tuple(sorted((x-ox,y-oy) for x,y in points)))
            return min(variants)
        for location in ('tool_shed','repair_yard'):
            plans=BUILDING_PLANS[location]
            self.assertEqual(len({signature(footprint(BUILDINGS[p['building']])) for p in plans}),4)
        # Stamping the same building at a new anchor and rotation moves all data together.
        first=place_building('workshop_l_forge',(0,0),'a')
        second=place_building('workshop_l_forge',(20,4),'b',90)
        self.assertEqual((second['width'],second['height']),(first['height'],first['width']))
        self.assertFalse({t['id'] for t in first['terrain']}&{t['id'] for t in second['terrain']})
        for a,b in zip(first['terrain'],second['terrain']):
            self.assertEqual((b['x'],b['y']),(20+first['height']-1-a['y'],4+a['x']))
        for building in (first,second):
            occupied={(t['x'],t['y']) for t in building['terrain'] if t.get('blocking')}
            self.assertTrue(all((p['x'],p['y']) not in occupied for p in building['enemies']))
        for ident in BUILDINGS:
            for rotation in (0,90,180,270):
                building=place_building(ident,(2,3),'rotated',rotation)
                coordinates=[(t['x'],t['y']) for t in building['terrain']+building['decorations']+building['enemies']]
                coordinates += [tuple(p) for entry in building['paint'] for p in entry['tiles']]
                self.assertTrue(all(2<=x<2+building['width'] and 3<=y<3+building['height'] for x,y in coordinates),(ident,rotation))

    def test_gate_opens_closes_refuses_occupied_closure_and_can_be_broken(self):
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'gate','tool_shed',True)
        player=battle['units']['player']
        battle['turn_order']=['player',*[uid for uid in battle['turn_order'] if uid!='player']];battle['turn_index']=0
        gate=next(t for t in battle['terrain'] if t['kind']=='gate')
        gx,gy=gate['x'],gate['y'];player.update(x=gx-1,y=gy)
        self.assertTrue(_blocked(battle,gx,gy,'player'))
        self.assertTrue(any(a['command']['target_id']==gate['id'] for a in battle_view(battle)['context_actions']))
        _interact(battle,player,gate['id'])
        self.assertFalse(gate['blocking']);self.assertEqual(gate['sprite'],gate['open_sprite'])
        occupant=battle['units']['contract_enemy_0'];occupant.update(x=gx,y=gy)
        with self.assertRaisesRegex(ValueError,'standing'):_interact(battle,player,gate['id'])
        occupant.update(x=gx+2,y=gy)
        _interact(battle,player,gate['id']);self.assertTrue(gate['blocking'])
        player['attack']=100
        _damage_terrain(battle,player,gate['id'])
        self.assertTrue(gate['destroyed']);self.assertFalse(gate['blocking'])

    def test_active_saved_battle_does_not_regenerate_when_template_changes(self):
        battle=create_contract_battle(new_game({'name':'Tester'}),['player'],'saved','tool_shed',True)
        before=deepcopy(battle['ground_tiles'])
        view=battle_view(battle)
        self.assertEqual(view['ground_tiles'],before)
        self.assertEqual(view['location_id'],'tool_shed')
