"""Authored maps assembled from reusable buildings and location pieces."""
from copy import deepcopy
import random
import json
from pathlib import Path
from .location_templates import BUILDING_PLANS
from .building_templates import BUILDINGS, footprint, shell
from .wall_boundaries import SIDES

ART_GEOMETRY=json.loads(Path(__file__).with_name('building_art_geometry.json').read_text())

MATERIALS = {
    'shed_floor': {'name': 'Weathered Shed Boards', 'movement_cost': 1, 'description': 'A worn wooden interior.'},
    'workshop_floor': {'name': 'Repair Yard Cobbles', 'movement_cost': 1, 'description': 'Stone paving around the work bays.'},
    'grave_earth': {'name': 'Graveyard Earth', 'movement_cost': 1, 'description': 'Dark soil between burial plots.'},
    'grave_path': {'name': 'Mossy Cemetery Path', 'movement_cost': 1, 'description': 'Old paving between the graves.'},
    'forest_dark': {'name': 'Shaded Woodland', 'movement_cost': 1, 'description': 'Leaf litter under the trees.'},
    'bridge_deck': {'name': 'Bridge Deck', 'movement_cost': 1, 'description': 'Surviving planks form a crossing over deep water.'},
    'deep_river': {'name': 'Deep River', 'movement_cost': 1, 'description': 'Impassable on foot. Use the bridge; flying units can cross.'},
}
for _material in ['wood_bridge','wood_bridge_damaged','wood_bridge_top','wood_bridge_bottom',
                  'stone_bridge','stone_bridge_damaged','stone_bridge_top','stone_bridge_bottom',
                  'chapel_moss','chapel_cracked','toll_cobbles','smithy_cobbles']:
    MATERIALS[_material]={'name':_material.replace('_',' ').title(),'movement_cost':1,
                          'description':'Solid, traversable bridge decking.' if 'bridge' in _material else 'Worn stone paving.'}

MISSION_LOCATIONS = {
    'tool_shed': 'tool_shed', 'workshop_intruders': 'repair_yard',
    'undead_bone_collectors': 'graveyard', 'bone_patrol': 'cemetery_road',
    'timber_creek': 'broken_creek_bridge', 'goblin_bridge': 'toll_bridge',
    'goblin_armory': 'open_armory',
    'chapel_patrol': 'chapel_approach', 'chapel_gate': 'chapel_approach',
    'roadside_toll': 'toll_post', 'ford_enforcers': 'toll_post',
    'watch_negotiation': 'toll_post', 'titan_road_tolls': 'toll_post',
    'lantern_toll_captain': 'toll_post',
    'road_cache': 'raider_cache', 'bandit_outpost': 'raider_cache',
    'salvage_court': 'salvage_court',
    'goblin_chieftain': 'timber_redoubt', 'hobgoblin_vanguard': 'vanguard_camp',
    'rats_storehouse':'provision_store', 'wolves_fence':'farm_clearing',
    'herbs_wall':'herb_garden', 'goblin_pickpockets':'purse_road',
    'ruined_well':'well_yard', 'supply_watch':'supply_stop',
    'highway_ambush':'highway_cut', 'goblin_boar_riders':'boar_rider_route',
}
for _rank in 'edcbas':
    MISSION_LOCATIONS[f'prison_rival_{_rank}']='road_blockade'
    MISSION_LOCATIONS[f'prison_former_{_rank}']='command_post' if _rank in 'ed' else 'command_camp'
    MISSION_LOCATIONS[f'prison_proof_{_rank}']='occupied_training_yard'


def wall(x, y, ident, wood=False, rotation=0, family=None):
    family=family or ('timber' if wood else 'fieldstone')
    return {'id': ident, 'name': 'Shed Wall' if wood else 'Boundary Wall', 'x': x, 'y': y,
            'kind': 'palisade' if wood else 'wall', 'sprite': f'structure:{family}_wall',
            'art_scale': 1.25,
            'rotation': rotation, 'blocking': True, 'blocks_sight': True, 'destructible': True,
            'hp': 16, 'max_hp': 16, 'armor': 2, 'destroyed_kind': 'rubble', 'destroyed_movement_cost': 2,
            'destroyed_sprite': f'structure:{family}_breach'}


def enclosure(ident, rect, doorway, wood=False):
    """Continuous perimeter with one operable/breakable gate. No duplicate corners."""
    x, y, w, h = rect
    family='timber' if wood else 'fieldstone';offset=ART_GEOMETRY[family]['join_offset']
    edge = {(xx, yy) for xx in range(x, x+w) for yy in range(y, y+h)
            if xx in (x, x+w-1) or yy in (y, y+h-1)}
    terrain = [wall(xx, yy, f'{ident}_wall_{xx}_{yy}', wood, 90 if xx in (x, x+w-1) else 0)
               for xx, yy in sorted(edge) if (xx, yy) != doorway]
    corners={(x,y):270,(x+w-1,y):0,(x+w-1,y+h-1):90,(x,y+h-1):180}
    for segment in terrain:
        segment.update(edge_wall=True,wall_edges=[side for side,active in [('north',segment['y']==y),
                        ('east',segment['x']==x+w-1),('south',segment['y']==y+h-1),('west',segment['x']==x)] if active])
        if (segment['x'],segment['y']) in corners:
            segment.update(sprite=f'structure:{family}_corner',
                           rotation=corners[(segment['x'],segment['y'])])
        else:
            segment['art_offset'] = [(-offset if segment['x']==x else offset) if segment['x'] in (x,x+w-1) else 0,
                                     (-offset if segment['y']==y else offset) if segment['y'] in (y,y+h-1) else 0]
    dx, dy = doorway
    prefix = f'structure:{family}_door' if wood else f'structure:{family}_gate'
    terrain.append({'id': f'{ident}_gate', 'name': 'Shed Door' if wood else 'Yard Gate', 'x': dx, 'y': dy,
                    'kind': 'gate', 'state': 'closed', 'sprite': prefix+'_closed', 'closed_sprite': prefix+'_closed',
                    'open_sprite': prefix+'_open', 'rotation': 90 if dx in (x,x+w-1) else 0,
                    'blocking': True, 'blocks_sight': True, 'destructible': True, 'hp': 12, 'max_hp': 12,
                    'armor': 1, 'destroyed_kind': 'rubble', 'destroyed_movement_cost': 2})
    terrain[-1]['art_scale']=1.25
    terrain[-1].update(edge_wall=True,wall_edges=[side for side,active in [('north',dy==y),
                         ('east',dx==x+w-1),('south',dy==y+h-1),('west',dx==x)] if active])
    terrain[-1]['art_offset'] = [(-offset if dx==x else offset) if dx in (x,x+w-1) else 0,
                                (-offset if dy==y else offset) if dy in (y,y+h-1) else 0]
    return terrain


def prop(ident, name, sprite, x, y, blocking=True):
    from .prop_sizes import prop_footprint
    size=prop_footprint(sprite)
    if not blocking:
        return {'id': ident, 'name': name, 'sprite': sprite, 'x': x, 'y': y,
                'footprint':size,
                **({'art_scale': 1/3} if sprite=='camp_lantern' else {})}
    return {'id': ident, 'name': name, 'sprite': sprite, 'x': x, 'y': y, 'kind': 'furniture',
            'footprint':size,
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


def river_crossing(x, road_y, height, damaged=False, family='wood'):
    """A continuous river strip with a ground-based bridge, not a bridge prop."""
    bridge = {(xx,yy) for xx in range(x,x+3) for yy in (road_y,road_y+1)}
    if damaged:
        bridge.remove((x+1,road_y))
    water = {(xx,yy) for xx in range(x,x+3) for yy in range(height)} - bridge
    paint=[{'material':'deep_river','rect':[x,0,3,height]}]
    for row,suffix in [(road_y,'top'),(road_y+1,'bottom')]:
        paint.append({'material':f'{family}_bridge_{suffix}',
                      'tiles':[list(p) for p in sorted(bridge) if p[1]==row]})
    if damaged:
        paint.append({'material':f'{family}_bridge_damaged','tiles':[[x+1,road_y+1]]})
    return (paint,
            [{'x':xx,'y':yy,'kind':'deep_water'} for xx,yy in sorted(water)])


def place_building(template_id, anchor, ident, rotation=0, family_override=None):
    """Stamp a reusable local building at an anchor, independently of mission/map.

    Multiple instances may share a map; identifiers, joins and spawn candidates
    move/rotate together. No exits, enemy budgets, objectives or rewards live here.
    """
    template=BUILDINGS[template_id]
    if family_override:
        if family_override not in ART_GEOMETRY:raise ValueError('Unknown building material')
        template={**template,'family':family_override,'floor':'shed_floor' if family_override=='timber' else 'smithy_cobbles'}
    cells=footprint(template);boundary=shell(template)
    width=max(x for x,y in cells)+1;height=max(y for x,y in cells)+1
    for x,y,w,h in template.get('yard',[]):
        width=max(width,x+w);height=max(height,y+h)
    if rotation not in (0,90,180,270):raise ValueError('Building rotation must be a quarter turn')
    def position(x,y):
        if rotation==90:x,y=height-1-y,x
        elif rotation==180:x,y=width-1-x,height-1-y
        elif rotation==270:x,y=y,width-1-x
        return x+anchor[0],y+anchor[1]
    def shifted(offset):
        x,y=offset
        if rotation==90:x,y=-y,x
        elif rotation==180:x,y=-x,-y
        elif rotation==270:x,y=y,-x
        return [x,y]
    def edges(sides):
        order=list(SIDES)
        return [order[(order.index(side)+rotation//90)%4] for side in sides]
    family=template['family'];factor=ART_GEOMETRY[family]['join_offset']/.3125
    terrain=[];decorations=[];paint=[]
    for rect in template.get('yard',[]):
        rx,ry,w,h=rect
        paint.append({'material':'dirt' if family=='timber' else 'workshop_floor',
                      'tiles':[list(position(x,y)) for x in range(rx,rx+w) for y in range(ry,ry+h)]})
    paint.append({'material':template['floor'],'tiles':[list(position(x,y)) for x,y in sorted(cells)]})
    for (x,y),piece in boundary.items():
        xx,yy=position(x,y)
        entry=wall(xx,yy,f'{ident}_wall_{x}_{y}',family=='timber',rotation=(piece['rotation']+rotation)%360,family=family)
        entry.update(sprite=f"structure:{family}_{piece['piece']}",art_offset=shifted([v*factor for v in piece['offset']]))
        if piece['piece']=='edge_junction':
            ox,oy=ART_GEOMETRY[family].get('junction_offset',[0,0])
            for _ in range(piece['rotation']//90):ox,oy=-oy,ox
            entry['art_offset']=shifted([ox,oy])
        entry.update(edge_wall=not piece.get('centered',False),wall_edges=edges(piece['edges']))
        terrain.append(entry)
    for x,y in template.get('partitions',[]):
        xx,yy=position(x,y)
        terrain.append(wall(xx,yy,f'{ident}_divider_{x}_{y}',family=='timber',rotation=(90+rotation)%360,family=family))
    for index,(x,y,type_) in enumerate(template['doors']+template.get('internal_doors',[])):
        matches=[t for t in terrain if (t['x'],t['y'])==position(x,y)]
        if (x,y) in boundary:
            piece=boundary[(x,y)];turn=piece['rotation'];offset=[v*factor for v in piece['offset']]
        else:turn=90;offset=[0,0]
        terrain[:]=[t for t in terrain if t not in matches]
        xx,yy=position(x,y);prefix=f'structure:{family}_{type_}'
        gate=wall(xx,yy,f'{ident}_gate_{index}',family=='timber',family=family)
        gate.update(name=template.get('door_name','Store Door') if type_=='door' else template.get('gate_name','Workshop Gate'),kind='gate',state='closed',
                    sprite=prefix+'_closed',closed_sprite=prefix+'_closed',open_sprite=prefix+'_open',
                    rotation=(turn+rotation)%360,art_offset=shifted(offset),hp=12,max_hp=12,armor=1)
        if (x,y) in boundary:
            gate.update(edge_wall=True,wall_edges=edges(boundary[(x,y)]['edges']))
        terrain.append(gate)
    for x,y in template.get('breaches',[]):
        entry=next(t for t in terrain if (t['x'],t['y'])==position(x,y))
        entry.update(kind='rubble',name='Broken Store Wall',sprite=f'structure:{family}_breach',
                     blocking=False,blocks_sight=False,destructible=False,hp=0,movement_cost=2)
    for index,(sprite,x,y) in enumerate(template.get('furniture',[])):
        xx,yy=position(x,y);item=prop(f'{ident}_furniture_{index}',sprite.replace('_',' ').title(),sprite,xx,yy)
        item['rotation']=rotation;terrain.append(item)
    for index,(sprite,x,y) in enumerate(template.get('decorations',[])):
        xx,yy=position(x,y);item=prop(f'{ident}_decoration_{index}',sprite.replace('_',' ').title(),sprite,xx,yy,False)
        item['rotation']=rotation;decorations.append(item)
    return {'id':template_id,'label':template['label'],'terrain':terrain,'decorations':decorations,'paint':paint,
            'enemies':[{'x':x,'y':y} for x,y in (position(x,y) for x,y in template['enemies'])],
            'width':height if rotation in (90,270) else width,'height':width if rotation in (90,270) else height}


def dress_building(piece, rng):
    """Vary contents without putting new blockers in doors or movement lanes.

    Solid furniture swaps between authored furniture slots. Small loose scenery
    can move onto free interior floor, never onto walls, spawns or other props.
    Neither change invents rewards or interactions for decorative containers.
    """
    variation=rng.randrange(4)
    piece['dressing_variation']=variation+1
    furniture=[t for t in piece['terrain'] if t.get('kind')=='furniture']
    if furniture:
        contents=[(t['sprite'],t['name']) for t in furniture]
        shift=variation % len(contents)
        for item, (sprite,name) in zip(furniture,contents[shift:]+contents[:shift]):
            item.update(sprite=sprite,name=name)
    occupied={(t['x'],t['y']) for t in piece['terrain']+piece['enemies']+piece['decorations']}
    floor={tuple(p) for layer in piece['paint'] for p in layer['tiles']}
    free=sorted(floor-occupied)
    rng.shuffle(free)
    if variation and free and piece['decorations']:
        # Use the existing loose prop instead of growing the clutter each visit.
        item=piece['decorations'][0]
        item['x'],item['y']=free[0]


def location_blueprint(location, seed):
    if location not in set(MISSION_LOCATIONS.values()):
        raise ValueError(f'Unknown authored location: {location}')
    rng = random.Random(f'location:{location}:{seed}')
    from .d_rank_locations import LOCATIONS as D_LOCATIONS, blueprint as d_blueprint
    if location in D_LOCATIONS:
        return d_blueprint(location, rng.randrange(4))
    variant = rng.randrange(len(BUILDING_PLANS.get(location, [None,None])))
    from .road_locations import ROAD_SETTINGS, blueprint as road_blueprint
    if location in ROAD_SETTINGS:
        return road_blueprint(location,variant,rng)
    from .command_locations import COMMAND_SETTINGS, blueprint as command_blueprint
    if location in COMMAND_SETTINGS:
        return command_blueprint(location,variant,rng)
    from .beginner_locations import BEGINNER_SETTINGS, blueprint as beginner_blueprint
    if location in BEGINNER_SETTINGS:
        return beginner_blueprint(location,variant,rng)
    width, height = 14, 11
    board = {'name': location, 'theme': f'location-{location}', 'width':width, 'height':height,
             'default_ground':'grass', 'paint':[], 'void_tiles':[], 'elevation':[],
             'terrain':[], 'decorations':[], 'location_id':location, 'map_variation':variant+1,
             'extraction':{'name':'Guild Approach','tiles':[{'x':0,'y':y} for y in range(3,8)]},
             'enemy_extraction':{'name':'Far Approach','tiles':[{'x':13,'y':y} for y in range(3,8)]},
             'spawn_zones':{'player':[{'x':x,'y':y} for x,y in ((1,5),(1,4),(1,6),(2,5))],
                            'enemy':[{'x':x,'y':y} for x,y in ((10,5),(9,4),(10,6),(11,3),(11,7),(9,6),(10,7),(11,5))]}}
    t, d, p = board['terrain'], board['decorations'], board['paint']
    plan = BUILDING_PLANS.get(location, [None]*(variant+1))[variant]
    board['template_id'] = plan['id'] if plan else f'{location}_{variant+1}'
    if plan and plan.get('building'):
        ax,ay=plan['anchor'];anchor=(ax+rng.randrange(2),ay+rng.randrange(2))
        piece=place_building(plan['building'],anchor,'building')
        dress_building(piece, rng)
        board['width']=max(14,anchor[0]+piece['width']+2)
        board['height']=max(11,anchor[1]+piece['height']+2)
        board['theme']=('location-graveyard' if location=='chapel_approach' else
                        'location-shed' if location in {'tool_shed','raider_cache'} else 'location-workshop')
        if location=='chapel_approach':board['default_ground']='forest_dark'
        board['dressing_variation']=piece['dressing_variation']
        board['building_templates']=[{'id':piece['id'],'label':piece['label'],'anchor':list(anchor)}]
        p.append({'material':'dirt','rect':[0,4,anchor[0]+1,3]});p.extend(piece['paint'])
        t.extend(piece['terrain']);d.extend(piece['decorations'])
        d.append(prop('yard_light','Approach Lantern','camp_lantern',anchor[0]-1,anchor[1]+2,False))
        board['spawn_zones']['enemy']=piece['enemies']
        board['enemy_extraction']=deepcopy(board['extraction'])
        return board
    if plan and not plan.get('legacy'):
        board['theme']='location-workshop'
        p.extend([{'material':'dirt','rect':[0,4,14,3]},
                  {'material':'workshop_floor','rect':[7,0,6,11]}])
        if plan.get('players'):
            p.append({'material':'workshop_floor','rect':[2,1,11,8]})
        for ident,rect,door in plan['rooms']:
            t.extend(enclosure(ident,rect,door,wood=location=='open_armory'))
            x,y,w,h=rect
            p.append({'material':'shed_floor' if location=='open_armory' else 'smithy_cobbles',
                      'rect':[x+1,y+1,w-2,h-2]})
        t.extend(prop(f'bay_{index}',sprite.replace('_',' ').title(),sprite,x,y)
                 for index,(sprite,x,y) in enumerate(plan['furniture']))
        board['spawn_zones']['enemy']=[{'x':x,'y':y} for x,y in plan['enemies']]
        if plan.get('players'):
            board['spawn_zones']['player']=[{'x':x,'y':y} for x,y in plan['players']]
            board['extraction']['tiles']=[{'x':x,'y':y} for x,y in plan['exit']]
        board['enemy_extraction']=deepcopy(board['extraction'])
        d.extend([prop('yard_light','Yard Lantern','camp_lantern',6,8,False),
                  prop('yard_cart','Supply Handcart','wooden_handcart',12,5,False)])
        return board
    if location in {'graveyard','cemetery_road'}:
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
        road_y=4 if not variant else 6
        family='stone' if variant and location=='toll_bridge' else 'wood'
        board['template_id']=f'{location}_{family}_{road_y}'
        p.append({'material':'toll_cobbles' if location=='toll_bridge' else 'dirt','rect':[0,road_y,14,2]})
        pp,void=river_crossing(6,road_y,height,location=='broken_creek_bridge',family);p.extend(pp);board['void_tiles']=void
        # Solid abutments border the traversable planks; the bridge itself is floor.
        t.extend(wall(x,y,f'bridge_abutment_{x}_{y}') for x in (5,9) for y in (road_y-1,road_y+2))
        d.extend([prop('bank_pine','Riverbank Pine','pine_tree',3,1 if variant else 9,False),
                  prop('bank_rock','Riverbank Rock','rounded_boulder',10,9 if variant else 1,False),
                  prop('bridge_light','Crossing Lantern','camp_lantern',5,road_y,False)])
        if location=='broken_creek_bridge':
            d.extend([prop('near_logs','Reachable Timber','cut_log_pile',3,7,False),
                      prop('far_planks','Timber Across the Creek','stacked_planks',11,8,False)])
            t.append(prop('repair_saw','Bridge Repair Sawhorse','carpenter_sawhorse',4,8))
        else:
            for y in range(height):
                if y in (road_y,road_y+1):continue
                barricade=wall(9,y,f'toll_barricade_{y}',wood=True,rotation=90)
                barricade.update(name='Toll Barricade',sprite='structure:palisade_straight',
                                 destroyed_sprite='structure:palisade_breached')
                t.append(barricade)
            d.append(prop('gang_goods','Collected Toll Goods','bound_barrels',12,8,False))
            t.append(prop('toll_records','Toll Ledger Desk','toll_desk',12,2))
        board['spawn_zones']['enemy']=[{'x':x,'y':y} for x,y in
            ((10,road_y),(11,road_y),(12,road_y),(13,road_y),(10,road_y+1),(11,road_y+1),(12,road_y+1),(13,road_y+1))]
        board['theme']='location-river'
    return board
