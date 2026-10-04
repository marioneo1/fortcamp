"""Authored road pieces: readable lanes, climbable banks and reserved approaches."""
ROAD_SETTINGS = {'highway_cut': [
    'Brush ambush along the northern shoulder',
    'Descending bend and stolen-supply pull-off',
    'Brush ambush at the wooded fork',
    'Passing place and southern back trail',
]}


def road_lane(centres, radius=1):
    """A continuous lane from per-column centres; bends overlap at full width."""
    return {(x, y) for x, centre in enumerate(centres)
            for y in range(centre-radius, centre+radius+1)}


def blueprint(location, variant, rng):
    from .location_maps import prop
    from .battle_maps import occupied_tiles
    width, height = 16, 11
    centres = [
        [5]*16,
        [5]*6+[6]*4+[7]*6,
        [5]*16,
        [5]*5+[4]*6+[5]*5,
    ][variant]
    road = road_lane(centres)
    if variant == 3:
        road.update((x, y) for x in range(7, 11) for y in range(3, 8))
    flank_y = 2 if variant in (0, 1) else 8
    flank = {(x, flank_y) for x in range(3, 14)}
    for x in (3, 13):
        flank.update((x, y) for y in range(min(flank_y, centres[x]), max(flank_y, centres[x])+1))
    banks = {(x, centres[x]+side*2) for x in range(4, 14) for side in (-1, 1)} - road - flank
    players = [(x, centres[x]+dy) for x in (1, 2) for dy in (0, -1, 1)]
    players += [(3, centres[3]), (3, centres[3]-1)]
    enemies = [(10, centres[10]), (11, centres[11]-2), (9, centres[9]+1),
               (11, centres[11]-1), (12, centres[12]), (9, centres[9]),
               (12, centres[12]+1), (13, centres[13]-1)]
    if variant in (0, 2):
        enemies[2] = (9, centres[9]+2)
    west = [{'x':0, 'y':y} for y in range(centres[0]-1, centres[0]+2)]
    east = [{'x':width-1, 'y':y} for y in range(centres[-1]-1, centres[-1]+2)]
    board = {'name':location, 'theme':'location-highway', 'width':width, 'height':height,
             'default_ground':'forest_dark', 'paint':[], 'terrain':[], 'decorations':[],
             'void_tiles':[], 'elevation':[], 'ground_art':[], 'location_id':location,
             'map_variation':variant+1, 'template_id':f'{location}_{variant+1}',
             'template_label':ROAD_SETTINGS[location][variant],
             'extraction':{'name':'Western Highway', 'tiles':west},
             'enemy_extraction':{'name':'Eastern Highway', 'tiles':east},
             'spawn_zones':{'player':[{'x':x,'y':y} for x,y in players],
                            'enemy':[{'x':x,'y':y} for x,y in enemies]},
             'building_templates':[]}
    supply = [(11,8), (8,3), (10,1), (11,9)][variant]
    sx, sy = supply
    pull_off = {(x, y) for x in range(sx-1, sx+4) for y in range(sy-1, min(height-1, sy+2))}
    banks -= pull_off
    board['paint'] = [
        {'material':'grass', 'tiles':[list(p) for p in sorted(banks)]},
        {'material':'dirt', 'tiles':[list(p) for p in sorted(flank | road | pull_off)]},
    ]
    # A small wet roadside ditch costs movement, rather than blocking the road.
    ditch = {(x, centres[x]+2) for x in range(5, 8)} - road - flank - pull_off
    board['paint'].append({'material':'mud','tiles':[list(p) for p in sorted(ditch)]})
    board['elevation'] = [{'x':x,'y':y,'height':1,'kind':'highway_bank'} for x,y in sorted(banks-ditch)]
    # Continuous painted dirt keeps the highway coherent instead of alternating
    # unrelated dirt swatches in every square. Physics still uses paint materials.
    board['ground_art'] = [{'x':x,'y':y,'sprite':'garden_worn_soil','texture_span':2,'origin':[0,0]}
                           for x,y in sorted(road | flank | pull_off)]
    reserved = road | flank | set(players) | set(enemies)
    occupied = set()

    def item(sprite, x, y, name, solid=True, offset=(0,0)):
        value = prop(f'highway_{sprite}_{x}_{y}', name, sprite, x, y, solid)
        value['art_offset'] = list(offset)
        cells = set(occupied_tiles(value))
        if occupied & cells or (solid and reserved & cells):
            raise ValueError(f'Highway prop overlaps a route or another prop: {value["id"]}')
        occupied.update(cells)
        (board['terrain'] if solid else board['decorations']).append(value)
        return value

    item('wooden_handcart', sx, sy, 'Stolen Supply Cart', offset=(0,.08))
    item('grain_sacks', sx+2, sy, 'Stolen Provisions', offset=(.12,-.12))
    item('bound_barrels', sx+3, sy, 'Roadside Stores', offset=(.08,.12))
    item('horticulture_tool_crate', sx-1, sy, 'Cart Repair Tools', False, (.18,.15))
    item('camp_lantern', sx+2, sy+1, 'Supply Lantern', False, (.18,-.18))
    # Authored cover pockets, rather than random clutter scattered across lanes.
    pockets = [
        [(5,1),(8,1),(7,9),(10,9),(14,2),(14,9)],
        [(5,1),(8,1),(5,9),(8,9),(14,1),(14,9)],
        [(5,2),(7,2),(7,9),(14,2),(14,9),(4,9)],
        [(5,1),(8,1),(5,9),(8,9),(14,1),(14,7)],
    ][variant]
    for index, (x,y) in enumerate(pockets):
        item('oak_tree' if index%3 else 'mossy_boulder', x, y,
             'Roadside Oak' if index%3 else 'Bank Boulder')
        # Trees obscure sight; low boulders offer route cover without a tall wall.
        board['terrain'][-1]['blocks_sight'] = index%3 != 0
    for x,y in [(1,1),(2,9),(0,9),(15,1),(15,9)]:
        item(rng.choice(['dense_shrub','thorny_bramble']),x,y,'Roadside Brush',False)
    if variant in (0, 2):
        board['ambush_enemy_indices'] = [1, 2]
        for index in board['ambush_enemy_indices']:
            x, y = enemies[index]
            brush = item('dense_shrub', x, y, 'Concealing Brush', False)
            brush.update(kind='bush', conceals_units=True,
                         description='Conceals enemies until spotted nearby, leaving cover, or attacking.')
    board['road_areas'] = ['Highway lane','Climbable low banks','Rejoining flank trail','Stolen-supply pull-off']
    return board
