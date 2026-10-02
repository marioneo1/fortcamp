"""Authored location pieces; variation changes dressing, never the place's identity."""
from copy import deepcopy
import random

MATERIALS = {
    'shed_floor': {'name': 'Weathered Shed Boards', 'movement_cost': 1, 'description': 'A worn wooden interior.'},
    'workshop_floor': {'name': 'Repair Yard Cobbles', 'movement_cost': 1, 'description': 'Stone paving around the work bays.'},
    'grave_earth': {'name': 'Graveyard Earth', 'movement_cost': 1, 'description': 'Dark soil between burial plots.'},
    'grave_path': {'name': 'Mossy Cemetery Path', 'movement_cost': 1, 'description': 'Old paving between the graves.'},
    'forest_dark': {'name': 'Shaded Woodland', 'movement_cost': 1, 'description': 'Leaf litter under the trees.'},
    'bridge_deck': {'name': 'Bridge Deck', 'movement_cost': 1, 'description': 'Surviving planks form a crossing over deep water.'},
    'deep_river': {'name': 'Deep River', 'movement_cost': 1, 'description': 'Impassable on foot. Use the bridge; flying units can cross.'},
}

MISSION_LOCATIONS = {
    'tool_shed': 'tool_shed', 'workshop_intruders': 'repair_yard',
    'undead_bone_collectors': 'graveyard', 'bone_patrol': 'cemetery_road',
    'timber_creek': 'broken_creek_bridge', 'goblin_bridge': 'toll_bridge',
}


def wall(x, y, ident, wood=False, rotation=0):
    return {'id': ident, 'name': 'Shed Wall' if wood else 'Boundary Wall', 'x': x, 'y': y,
            'kind': 'palisade' if wood else 'wall', 'sprite': 'structure:shed_wall_straight' if wood else 'structure:stone_wall_straight',
            'art_scale': 1.25,
            'rotation': rotation, 'blocking': True, 'blocks_sight': True, 'destructible': True,
            'hp': 16, 'max_hp': 16, 'armor': 2, 'destroyed_kind': 'rubble', 'destroyed_movement_cost': 2,
            'destroyed_sprite': 'structure:shed_wall_broken' if wood else 'structure:wall_rubble'}


def enclosure(ident, rect, doorway, wood=False):
    """Continuous perimeter with one operable/breakable gate. No duplicate corners."""
    x, y, w, h = rect
    edge = {(xx, yy) for xx in range(x, x+w) for yy in range(y, y+h)
            if xx in (x, x+w-1) or yy in (y, y+h-1)}
    terrain = [wall(xx, yy, f'{ident}_wall_{xx}_{yy}', wood, 90 if xx in (x, x+w-1) else 0)
               for xx, yy in sorted(edge) if (xx, yy) != doorway]
    corners={(x,y):270,(x+w-1,y):0,(x+w-1,y+h-1):90,(x,y+h-1):180}
    for segment in terrain:
        if (segment['x'],segment['y']) in corners:
            segment.update(sprite='structure:shed_wall_corner' if wood else 'structure:cemetery_wall_corner',
                           rotation=corners[(segment['x'],segment['y'])])
    dx, dy = doorway
    prefix = 'structure:shed_door' if wood else 'structure:yard_gate'
    terrain.append({'id': f'{ident}_gate', 'name': 'Shed Door' if wood else 'Yard Gate', 'x': dx, 'y': dy,
                    'kind': 'gate', 'state': 'closed', 'sprite': prefix+'_closed', 'closed_sprite': prefix+'_closed',
                    'open_sprite': prefix+'_open', 'rotation': 90 if dx in (x,x+w-1) else 0,
                    'blocking': True, 'blocks_sight': True, 'destructible': True, 'hp': 12, 'max_hp': 12,
                    'armor': 1, 'destroyed_kind': 'rubble', 'destroyed_movement_cost': 2})
    return terrain


def prop(ident, name, sprite, x, y, blocking=True):
    if not blocking:
        return {'id': ident, 'name': name, 'sprite': sprite, 'x': x, 'y': y}
    return {'id': ident, 'name': name, 'sprite': sprite, 'x': x, 'y': y, 'kind': 'furniture',
            'blocking': True, 'blocks_sight': False, 'destructible': True, 'hp': 10, 'max_hp': 10,
            'armor': 0, 'destroyed_kind': 'rubble', 'destroyed_movement_cost': 2}


def work_bay(ident, x, y, forge=False):
    """A workbench with its tool storage; forge bays substitute anvil and furnace."""
    return [prop(ident+'_bench', 'Repair Workbench', 'repair_workbench', x, y),
            prop(ident+'_tools', 'Tool Rack', 'carpenter_tool_rack', x+2, y),
            *([prop(ident+'_anvil', 'Iron Anvil', 'iron_anvil', x, y+2),
               prop(ident+'_forge', 'Coal Forge', 'small_coal_forge', x+2, y+2)] if forge else [])]


def grave_plots(ident, x, y, rows=2):
    terrain, decorations, paint = [], [], []
    for row in range(rows):
        for col in range(2):
            xx, yy = x+col*3, y+row*3
            sprite = 'grave_cross' if (row+col)%2 else 'mossy_gravestone'
            terrain.append(prop(f'{ident}_{row}_{col}', 'Old Grave Marker', sprite, xx, yy))
            paint.append({'material': 'grave_earth', 'rect': [xx, yy+1, 1, 2]})
    decorations.append(prop(ident+'_fallen', 'Fallen Headstone', 'fallen_gravestone', x+1,y+1,False))
    decorations.append(prop(ident+'_bones', 'Disturbed Remains', 'old_bone_pile', x+3,y+1,False))
    return terrain, decorations, paint


def river_crossing(x, road_y, height, damaged=False):
    """A continuous river strip with a ground-based bridge, not a bridge prop."""
    bridge = {(xx,yy) for xx in range(x,x+3) for yy in (road_y,road_y+1)}
    if damaged:
        bridge.remove((x+1,road_y))
    water = {(xx,yy) for xx in range(x,x+3) for yy in range(height)} - bridge
    return ([{'material':'deep_river','rect':[x,0,3,height]},
             {'material':'bridge_deck','tiles':[list(p) for p in sorted(bridge)]}],
            [{'x':xx,'y':yy,'kind':'deep_water'} for xx,yy in sorted(water)])


def location_blueprint(location, seed):
    if location not in set(MISSION_LOCATIONS.values()):
        raise ValueError(f'Unknown authored location: {location}')
    rng = random.Random(f'location:{location}:{seed}')
    variant = rng.randrange(2)
    width, height = 14, 11
    board = {'name': location, 'theme': f'location-{location}', 'width':width, 'height':height,
             'default_ground':'grass', 'paint':[], 'void_tiles':[], 'elevation':[],
             'terrain':[], 'decorations':[], 'location_id':location, 'map_variation':variant+1,
             'extraction':{'name':'Guild Approach','tiles':[{'x':0,'y':y} for y in range(3,8)]},
             'enemy_extraction':{'name':'Far Approach','tiles':[{'x':13,'y':y} for y in range(3,8)]},
             'spawn_zones':{'player':[{'x':x,'y':y} for x,y in ((1,5),(1,4),(1,6),(2,5))],
                            'enemy':[{'x':x,'y':y} for x,y in ((10,5),(9,4),(10,6),(11,3),(11,7),(9,6),(10,7),(11,5))]}}
    t, d, p = board['terrain'], board['decorations'], board['paint']
    if location in {'tool_shed','repair_yard'}:
        wood = location=='tool_shed'
        board['theme']='location-shed' if wood else 'location-workshop'
        p.extend([{'material':'dirt','rect':[0,4,8,3]},
                  {'material':'shed_floor' if wood else 'workshop_floor','rect':[7,1,6,9]}])
        t.extend(enclosure('shed' if wood else 'yard',(7,1,6,9),(7,5),wood))
        t.extend(work_bay('north_bay',8,2,not wood))
        if wood:
            t.append(prop('shed_saw','Carpenter Sawhorse','carpenter_sawhorse',11,8))
            d.append(prop('shed_tools','Spilled Toolbox','open_toolbox',8,7,False))
            d.append(prop('shed_planks','Stored Boards','stacked_planks',10,8,False))
        else:
            t.append(prop('south_bay','Repair Bench','repair_workbench',9,8))
            d.append(prop('repair_wheel','Detached Wagon Wheel','wagon_wheel',8,7,False))
            d.append(prop('yard_cart','Repair Handcart','wooden_handcart',11,8,False))
        d.extend([prop('approach_tree','Boundary Pine','pine_tree',3,1,False),
                  prop('yard_light','Yard Lantern','camp_lantern',6,2 if variant else 8,False)])
        # Exit is through the door or a breached wall; no fake exit through the enclosure.
        board['enemy_extraction']=deepcopy(board['extraction'])
        if wood:
            # A collapsed roof section leaves one deliberate alternative entrance.
            t[:] = [entry for entry in t if entry['id']!='shed_wall_10_9']
            t.append({'id':'shed_collapse','name':'Collapsed Shed Wall','x':10,'y':9,'kind':'rubble',
                      'sprite':'structure:shed_wall_broken','art_scale':1.25,'blocking':False,'movement_cost':2})
    elif location in {'graveyard','cemetery_road'}:
        board['default_ground']='forest_dark'
        p.extend([{'material':'grave_earth','rect':[3,1,9,9]},
                  {'material':'grave_path','rect':[0,4,14,3]}])
        for ident,x,y in [('north_graves',5,1),('south_graves',5,7)]:
            tt,dd,pp=grave_plots(ident,x,y,rows=1);t.extend(tt);d.extend(dd);p.extend(pp)
        # Broken cemetery boundary keeps approaches clear and provides flank cover.
        t.extend(wall(x,0,f'cemetery_wall_{x}') for x in range(4,12))
        t.append(wall(12,1,'cemetery_corner',rotation=90))
        d.extend([prop('dead_tree_west','Dead Cemetery Tree','dead_tree',3,2 if variant else 8,False),
                  prop('dead_tree_east','Dead Cemetery Tree','dead_tree',12,8 if variant else 2,False),
                  prop('grave_lantern','Graveyard Lantern','camp_lantern',3,4,False)])
        if location=='cemetery_road':
            p.append({'material':'dirt','rect':[0,5,14,1]})
        board['theme']='location-graveyard'
    else:
        p.append({'material':'dirt','rect':[0,4,14,3]})
        pp,void=river_crossing(6,4,height,location=='broken_creek_bridge');p.extend(pp);board['void_tiles']=void
        # Solid abutments border the traversable planks; the bridge itself is floor.
        t.extend(wall(x,y,f'bridge_abutment_{x}_{y}') for x in (5,9) for y in (3,7))
        d.extend([prop('bank_pine','Riverbank Pine','pine_tree',3,1 if variant else 9,False),
                  prop('bank_rock','Riverbank Rock','rounded_boulder',10,9 if variant else 1,False),
                  prop('bridge_light','Crossing Lantern','camp_lantern',5,4,False)])
        if location=='broken_creek_bridge':
            d.extend([prop('near_logs','Reachable Timber','cut_log_pile',3,7,False),
                      prop('far_planks','Timber Across the Creek','stacked_planks',11,8,False)])
            t.append(prop('repair_saw','Bridge Repair Sawhorse','carpenter_sawhorse',4,8))
        else:
            for y in (1,2,8,9):
                barricade=wall(9,y,f'toll_barricade_{y}',wood=True,rotation=90)
                barricade.update(name='Toll Barricade',sprite='structure:palisade_straight',
                                 destroyed_sprite='structure:palisade_breached')
                t.append(barricade)
            d.append(prop('gang_goods','Collected Toll Goods','bound_barrels',12,8,False))
        board['theme']='location-river'
    return board
