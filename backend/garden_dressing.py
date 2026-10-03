"""Raised planting beds, a watering station and potting corner with clear aisles."""
from .battle_maps import occupied_tiles
from .prop_sizes import prop_footprint


def dress_garden(board,floor):
    from .location_maps import prop
    t,d=board['terrain'],board['decorations']
    # Replace the earlier sparse placeholders with the supplied garden set.
    t[:]=[item for item in t if item['sprite'] not in {'herb_planter','wash_tub'}]
    d[:]=[item for item in d if item['sprite']!='herb_planter']
    occupied={cell for item in t for cell in occupied_tiles(item)}
    corridors={(x,y) for x,y in floor if y==5 or x in (8,9)}
    for gate in t:
        if gate['kind']=='gate':corridors.update((gate['x']+dx,gate['y']+dy) for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)])

    def place(sprite,x,y,name=None,size=None,loose=False,outside=False):
        size=size or prop_footprint(sprite)
        cells={(x+dx,y+dy) for dx in range(size[0]) for dy in range(size[1])}
        if cells & (occupied|corridors) or (not outside and not cells <= floor):return False
        item=prop(f'garden_{sprite}_{x}_{y}',name or sprite.removeprefix('garden_').replace('_',' ').title(),sprite,x,y,not loose)
        item['footprint']=size
        if size==[2,2]:item['size_variant']='raised-bed'
        (d if loose else t).append(item);occupied.update(cells)
        return True

    # Beds form quadrants around a clear cross-shaped path. The annex plan
    # naturally has one fewer bed instead of forcing plants through its wall.
    for i,(x,y) in enumerate([(5,3),(10,3),(5,6),(10,6)]):
        place(['garden_mixed_herb_box','garden_cut_herb_box','garden_white_flower_box','garden_yellow_flower_box'][i],x,y,'Raised Herb Bed',[2,2])
    place('garden_potting_bench',5,2,'Potting Bench')
    place('garden_water_barrel',7,2,'Water Barrel')
    place('garden_stone_water_trough',10,2,'Garden Water Trough')
    place('garden_compost_bin',12,2,'Compost Bin')
    # Small equipment belongs next to workstations or along the edges.
    for sprite,x,y in [('garden_watering_can',12,3),('garden_soil_sack',7,7),
                       ('garden_lavender_barrel',7,3),('garden_garden_stool',7,4),
                       ('garden_basil_pot',7,8),('garden_tool_caddy',12,7),
                       ('garden_empty_pots',12,8)]:
        place(sprite,x,y,loose=True)
    place('garden_mixed_herb_box',3,2,'Herbs Outside the Wall',loose=True,outside=True)
    board['paint'].extend([{'material':'toll_cobbles','tiles':[[x,y] for x,y in sorted(floor)
                           if (x,y) in corridors and (x,y) not in occupied]}])
    board['garden_activity_areas']=['raised beds','potting corner','watering station','clear cross aisles']
