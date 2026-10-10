"""Local-coordinate buildings, independently placeable within a battlefield.

Room rectangles form a union footprint: shared walls disappear, concave joins
remain closed, and doors/breaches are explicit. Furniture never chooses the plan.
"""
BUILDINGS = {
    'road_relay_house': {
        'label':'Road relay office', 'family':'timber', 'floor':'shed_floor',
        'rooms':[(0,0,7,5)], 'doors':[(0,2,'door'),(6,3,'door')],
        'furniture':[('toll_desk',2,1),('crate_closed',4,1)],
        'decorations':[('bound_barrels',1,3)],
        'enemies':[(2,2),(3,2),(4,3)],
    },
    'tool_long_store': {
        'label':'Long tool store', 'family':'timber', 'floor':'shed_floor',
        'rooms':[(0,0,8,6)], 'doors':[(0,3,'door')], 'breaches':[(7,3)],
        'furniture':[('repair_workbench',2,1),('carpenter_tool_rack',5,1),('carpenter_sawhorse',6,4)],
        'decorations':[('stacked_planks',4,4),('open_toolbox',1,4)],
        'enemies':[(2,2),(3,2),(4,2),(5,2),(2,3),(3,3),(4,3),(5,3)],
    },
    'tool_divided_store': {
        'label':'Divided tool house', 'family':'timber', 'floor':'shed_floor',
        'rooms':[(0,0,8,8)], 'doors':[(0,4,'door')], 'breaches':[(7,5)],
        'partitions':[(4,y) for y in (1,2,3,5,6)], 'internal_doors':[(4,4,'door')],
        'furniture':[('repair_workbench',1,1),('carpenter_tool_rack',2,6),('carpenter_sawhorse',6,6)],
        'decorations':[('stacked_planks',6,1)],
        'enemies':[(1,2),(2,2),(3,2),(5,2),(6,2),(1,5),(2,5),(5,5)],
    },
    'tool_annex_yard': {
        'label':'Tool shed with side annex and yard', 'family':'timber', 'floor':'shed_floor',
        'rooms':[(0,0,8,4),(4,3,4,5)], 'doors':[(0,2,'door')], 'breaches':[(7,5)],
        'yard':[(0,4,4,4)],
        'furniture':[('repair_workbench',3,2),('carpenter_tool_rack',5,2),('carpenter_sawhorse',2,6)],
        'decorations':[('stacked_planks',6,6),('open_toolbox',1,5)],
        'enemies':[(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(5,5),(6,5)],
    },
    'tool_twin_sheds': {
        'label':'Twin sheds and loading court', 'family':'timber', 'floor':'shed_floor',
        'rooms':[(0,0,4,7),(6,0,4,7)],
        'doors':[(0,3,'door'),(3,3,'door'),(6,3,'door')], 'breaches':[(9,4)],
        'yard':[(4,0,2,7),(0,7,10,2)],
        'furniture':[('repair_workbench',1,5),('carpenter_tool_rack',2,4),('repair_workbench',7,5),('carpenter_sawhorse',8,4)],
        'decorations':[('stacked_planks',4,6),('open_toolbox',7,4)],
        'enemies':[(1,1),(2,1),(1,2),(2,2),(7,1),(8,1),(7,2),(8,2)],
    },
    'workshop_forge_yard': {
        'label':'Enclosed forge yard', 'family':'fieldstone', 'floor':'workshop_floor',
        'rooms':[(0,0,10,8)], 'doors':[(0,4,'gate')],
        'furniture':[('small_coal_forge',1,1),('iron_anvil',3,1),('repair_workbench',6,1),
                     ('carpenter_tool_rack',8,1),('repair_workbench',3,6),('iron_anvil',6,6)],
        'decorations':[('wagon_wheel',8,6),('wooden_handcart',1,6)],
        'enemies':[(x,3) for x in range(1,9)],
    },
    'workshop_courtyard_pair': {
        'label':'Two workshops around a working courtyard', 'family':'fieldstone', 'floor':'smithy_cobbles',
        'rooms':[(0,0,9,4),(0,7,9,4)], 'doors':[(4,3,'gate'),(4,7,'door')],
        'yard':[(0,4,9,3)],
        'furniture':[('small_coal_forge',7,1),('iron_anvil',6,1),('repair_workbench',1,1),
                     ('repair_workbench',6,9),('carpenter_tool_rack',7,9),('carpenter_sawhorse',7,5)],
        'decorations':[('wooden_handcart',2,5),('wagon_wheel',1,9)],
        'enemies':[(1,2),(2,2),(3,2),(4,2),(1,8),(2,8),(3,8),(4,8)],
    },
    'workshop_l_forge': {
        'label':'L-shaped forge and repair wing', 'family':'fieldstone', 'floor':'smithy_cobbles',
        'rooms':[(0,0,6,9),(5,0,6,5)], 'doors':[(0,4,'gate'),(10,2,'door')],
        'yard':[(6,5,5,4)],
        'furniture':[('small_coal_forge',1,1),('iron_anvil',3,1),('repair_workbench',8,1),
                     ('carpenter_tool_rack',9,3),('repair_workbench',2,7),('carpenter_sawhorse',8,7)],
        'decorations':[('wooden_handcart',7,6),('wagon_wheel',4,7)],
        'enemies':[(1,3),(2,3),(3,3),(4,3),(6,2),(7,2),(8,2),(9,2)],
    },
    'workshop_repair_hall': {
        'label':'Partitioned repair hall with rear delivery door', 'family':'fieldstone', 'floor':'workshop_floor',
        'rooms':[(0,0,11,7)], 'doors':[(0,3,'gate'),(10,3,'door')],
        'partitions':[(6,y) for y in (1,2,4,5)], 'internal_doors':[(6,3,'door')],
        'furniture':[('repair_workbench',2,1),('repair_workbench',4,5),('carpenter_tool_rack',1,5),
                     ('small_coal_forge',9,1),('iron_anvil',8,5)],
        'decorations':[('wagon_wheel',8,1),('wooden_handcart',3,5)],
        'enemies':[(1,2),(2,2),(3,2),(4,2),(7,2),(8,2),(9,2),(7,4)],
    },
}


from .location_buildings import add_location_buildings
add_location_buildings(BUILDINGS)

# Explicit lighting coverage: room footprints exclude separately authored yards.
# Mixed/open compounds need individual roof regions before opting in.
for _lighting_id, _lighting_template in BUILDINGS.items():
    _lighting_template.setdefault('roofed',
        _lighting_id.startswith(('tool_', 'chapel_', 'armory_', 'cache_')) or
        _lighting_id in {'road_relay_house','workshop_courtyard_pair','workshop_l_forge','workshop_repair_hall'})
from .command_locations import add_command_buildings
add_command_buildings(BUILDINGS)
from .beginner_locations import add_beginner_buildings
add_beginner_buildings(BUILDINGS)


def footprint(template):
    return {(x,y) for rx,ry,w,h in template['rooms'] for x in range(rx,rx+w) for y in range(ry,ry+h)}


def shell(template):
    """Return cells and visible joins of the room union, including inward corners."""
    cells=footprint(template);result={}
    outer_corners={frozenset(('north','east')):0,frozenset(('east','south')):90,
                   frozenset(('south','west')):180,frozenset(('west','north')):270}
    cardinal={'north':(0,-1),'east':(1,0),'south':(0,1),'west':(-1,0)}
    for x,y in sorted(cells):
        exposed=[side for side,(dx,dy) in cardinal.items() if (x+dx,y+dy) not in cells]
        if len(exposed)==2 and frozenset(exposed) in outer_corners:
            result[(x,y)]={'piece':'corner','rotation':outer_corners[frozenset(exposed)],'offset':[0,0]}
        elif exposed:
            side=exposed[0];dx,dy=cardinal[side]
            result[(x,y)]={'piece':'wall','rotation':90 if dx else 0,'offset':[dx*.3125,dy*.3125]}
        else:
            for dx,dy,rotation in [(1,1,270),(-1,1,0),(-1,-1,90),(1,-1,180)]:
                if (x+dx,y+dy) not in cells:
                    result[(x,y)]={'piece':'corner','rotation':rotation,'offset':[dx*.625,dy*.625],'inner':True}
                    break
    for (x,y),piece in result.items():
        piece['edges']=[side for side,(dx,dy) in cardinal.items() if (x+dx,y+dy) not in cells]
    # A centered room divider meets the perimeter with a real T, not a gap.
    dividers=set(template.get('partitions', []))
    dividers.update((x,y) for x,y,_ in template.get('internal_doors', []))
    for (x,y),piece in result.items():
        if len(piece['edges']) != 1:continue
        side=piece['edges'][0];dx,dy=cardinal[side]
        if (x-dx,y-dy) in dividers:
            piece.update(piece='edge_junction',rotation={'north':0,'east':90,'south':180,'west':270}[side],
                         offset=[0,0],centered=True)
    return result
