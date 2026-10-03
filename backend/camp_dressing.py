"""Authored camp activity areas, with collision-safe full-footprint furniture."""
from .battle_maps import occupied_tiles


def dress_camp(board, rng):
    from .location_maps import prop
    from .building_templates import BUILDINGS, footprint
    outer = next(p for p in board['building_templates'] if p['id'].startswith('camp_shell'))
    ax,ay = outer['anchor']
    floor = {(x+ax,y+ay) for x,y in footprint(BUILDINGS[outer['id']])}
    occupied = {p for item in board['terrain'] for p in occupied_tiles(item)}
    occupied |= {(p['x'],p['y']) for p in board['decorations']}
    reserved = {(p['x'],p['y']) for side in board['spawn_zones'].values() for p in side}
    # Doors always retain a staging cell on both sides. The western approach
    # and the central fighting lane remain open regardless of dressing.
    for gate in board['terrain']:
        if gate['kind'] == 'gate':
            reserved |= {(gate['x']+dx,gate['y']+dy) for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]}
    reserved |= {(x,y) for x,y in floor if y in (5,6) or x==9}

    def place(sprite, name, preferred, size=(1,1), decorative=False):
        w,h = size
        candidates = sorted(floor, key=lambda p:(abs(p[0]-preferred[0])+abs(p[1]-preferred[1]),p[1],p[0]))
        for x,y in candidates:
            cells={(x+dx,y+dy) for dx in range(w) for dy in range(h)}
            if not cells <= floor or cells & (occupied|reserved):
                continue
            item=prop('camp_'+sprite,name,sprite,x,y,not decorative)
            if size != (1,1): item['footprint']=[w,h]
            (board['decorations'] if decorative else board['terrain']).append(item)
            occupied.update(cells)
            return

    # Reserve the large machine before small clutter can fragment its space.
    if board['location_id']=='vanguard_camp':
        place('ballista_loaded','Stored Ballista',(16,2),size=(2,2))
    # Targets sit along a rear edge; the cleared approach reads as a range.
    # Targets are scenery/obstacles, not practice interactions or loot.
    place('archery_target','Archery Target',(15,8))
    place('hay_archery_butt','Hay Archery Target',(15,9))
    place('straw_training_dummy','Training Dummy',(7,9))
    place('armored_training_dummy','Armored Practice Dummy',(8,9))
    place('practice_weapon_rack','Practice Weapon Rack',(7,8))
    place('arrow_bundle','Training Arrows',(14,9),decorative=True)
    bed = 'tribal_hide_bed' if board['location_id']=='timber_redoubt' else rng.choice(['canvas_cot','straw_bed','sleeping_bag'])
    place(bed,'Camp Sleeping Place',(11,9),size=(1,2))
    place('reed_sleeping_mat','Sleeping Mat',(12,9),decorative=True)
    place('camp_cooking_pot','Cook Pot',(8,8))
    place('grain_sacks','Food Stores',(7,4))
    place('water_trough','Water Trough',(16,8))
    place('war_drum','Signal Drum',(6,3))
    if board['location_id']=='vanguard_camp':
        place('ballista_bolts','Ballista Bolts',(16,4),decorative=True)
    else:
        place('tribal_trophy_pole','Tribal Trophy Pole',(6,4))
    board['camp_activity_areas']=['training','archery','sleeping','cooking','supplies']
