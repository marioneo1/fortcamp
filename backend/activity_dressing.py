"""First reviewed garden/practice-yard compositions; appearance only.

Ground art is separate from movement material. No decorative plants introduce
hidden collision, harvesting or extra rewards. Other layout variants stay intact.
"""
from .location_maps import prop
from .battle_maps import occupied_tiles


def dress_activity_site(board):
    location=board['location_id']
    if board['map_variation']!=1 or location not in {'herb_garden','occupied_training_yard'}:
        return
    # Rebuild furniture deliberately, instead of nudging automatically to the
    # nearest cell. Keep walls, doorways and all other locations unchanged.
    board['terrain'][:]=[p for p in board['terrain'] if not p['id'].startswith(location+'_')]
    board['decorations'][:]=[p for p in board['decorations'] if not p['id'].startswith(location+'_')]
    art={}

    def ground(sprite,x,y,w,h,span=2):
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                art[xx,yy]={'x':xx,'y':yy,'sprite':sprite,'texture_span':span,'origin':[x,y]}

    def furniture(sprite,x,y,name=None,offset=(0,0),rotation=0,loose=False):
        item=prop(f'{location}_{sprite}_{x}_{y}',name or sprite.replace('_',' ').title(),sprite,x,y,not loose)
        item.update(art_offset=list(offset),rotation=rotation)
        occupied={p for obj in board['terrain']+board['decorations'] for p in occupied_tiles(obj)}
        cells=set(occupied_tiles(item))
        if cells & occupied:raise ValueError(f'{location}: furniture overlaps at {x},{y}')
        (board['decorations'] if loose else board['terrain']).append(item)

    garden=location=='herb_garden'
    ground('garden_soil' if garden else 'practice_earth',4,1,10,8)
    # A road into the two gates also gets a coherent palette, rather than
    # alternating pale/brown squares from the general dirt assortment.
    ground('garden_worn_soil',0,4,16,3)
    if garden:
        ground('herbs_broadleaf',5,3,3,2)
        ground('herbs_violet',10,3,3,2)
        ground('herbs_sage',5,6,3,1)
        ground('herbs_white',10,6,3,1)
        ground('garden_worn_soil',8,2,2,6)
        ground('garden_stepping_stones',9,2,1,6,1)
        ground('garden_worn_soil',5,5,8,1)
        ground('garden_irrigation',8,3,1,2)
        ground('garden_irrigation',8,6,1,1)
        ground('garden_weeds',5,7,1,1,1)
        ground('garden_leaf_litter',7,7,1,1,1)
        furniture('food_prep_table',6,2,'Herbalist’s Worktable',offset=(0,-.2))
        furniture('bound_barrels',11,2,'Stored Garden Water',offset=(0,-.18))
        furniture('wash_tub',12,2,'Garden Wash Tub',offset=(.12,-.18))
        furniture('herb_planter',3,2,'Herbs Beside the Entrance',loose=True)
        furniture('mess_bench',11,7,'Gardener’s Bench',offset=(0,.2))
        board['activity_areas']=['Four medicinal herb patches','Cross-path between planting areas','Water and potting corner','Rest bench']
    else:
        # Northern targets face long clear firing lanes. The west half has
        # practice dummies above a broad, visibly worn sparring court.
        ground('practice_scuffs',5,3,4,4)
        ground('practice_grass',5,7,4,1)
        ground('practice_straw',10,2,3,1)
        ground('practice_earth',10,3,3,4)
        ground('practice_footprints',11,3,1,4,1)
        ground('practice_footprints',12,3,1,4,1)
        ground('practice_earth',9,3,1,4)
        ground('practice_straw',5,2,4,1)
        furniture('straw_training_dummy',6,2,'Practice Dummy',offset=(-.12,-.12))
        furniture('straw_training_dummy',8,2,'Practice Dummy',offset=(.12,-.12))
        furniture('archery_target',11,2,'Range Target',offset=(-.12,-.15))
        furniture('hay_archery_butt',12,2,'Straw Range Target',offset=(.12,-.15))
        furniture('practice_weapon_rack',5,7,'Practice Weapons',offset=(-.18,.18))
        furniture('training_shield_rack',7,7,'Practice Shields',offset=(0,.18))
        furniture('mess_bench',10,7,'Rest Bench',offset=(0,.18))
        furniture('arrow_bundle',12,7,'Spare Practice Arrows',offset=(.18,.18),loose=True)
        board['activity_areas']=['Worn sparring court','Dummy practice stations','Two archery lanes','Equipment and rest corner']
    board['ground_art']=list(art.values())
    board['dressing_version']='activity-v1'
