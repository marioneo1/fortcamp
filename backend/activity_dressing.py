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

    def crop_border(x,y,w,h):
        # Low step-over rails are scenery, not full-cell obstacles. A joined
        # segment has no terminal posts; one small stake covers each corner.
        def edge(kind,xx,yy,offset,rotation=0,scale=1):
            board['decorations'].append({'id':f'crop_edge_{x}_{y}_{kind}_{xx}_{yy}',
                'name':'Low Crop Edging · step-over border','sprite':'horticulture_fence_post' if kind=='post' else 'horticulture_fence_joined',
                'x':xx,'y':yy,'footprint':[1,1],'art_offset':list(offset),
                'rotation':rotation,'art_scale':scale,'ground_edging':True})
        for xx in range(x,x+w):
            edge('north',xx,y,(0,-.5));edge('south',xx,y+h-1,(0,.5))
        for yy in range(y,y+h):
            edge('west',x,yy,(-.5,0),90);edge('east',x+w-1,yy,(.5,0),90)
        for xx,yy,offset in [(x,y,(-.5,-.5)),(x+w-1,y,(.5,-.5)),
                             (x,y+h-1,(-.5,.5)),(x+w-1,y+h-1,(.5,.5))]:
            # Include the corner offset in the ID: a one-row bed has two posts
            # in the same cell, both of which still need stable unique identity.
            board['decorations'].append({'id':f'crop_post_{x}_{y}_{xx}_{yy}_{offset[0]}_{offset[1]}',
                'name':'Crop Border Stake','sprite':'horticulture_fence_post',
                'x':xx,'y':yy,'footprint':[1,1],'art_offset':list(offset),
                'art_scale':.18,'ground_edging':True})

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
        furniture('horticulture_potting_bench',5,2,'Herbalist’s Potting Bench',offset=(0,-.18))
        furniture('horticulture_round_stool',7,2,'Potting Stool',offset=(-.2,0))
        furniture('horticulture_tool_crate',8,2,'Gardening Tools',offset=(-.18,-.2),loose=True)
        furniture('horticulture_hand_pump',10,2,'Garden Hand Pump',offset=(.18,-.18))
        furniture('bound_barrels',11,2,'Stored Garden Water',offset=(0,-.18))
        furniture('wash_tub',12,2,'Garden Wash Tub',offset=(.12,-.18))
        furniture('horticulture_watering_can',12,3,'Watering Can',offset=(.2,-.18),loose=True)
        furniture('herb_planter',3,2,'Herbs Beside the Entrance',loose=True)
        furniture('horticulture_clay_pots',3,3,'Spare Plant Pots',offset=(.18,-.12),loose=True)
        furniture('horticulture_scarecrow',6,3,'Garden Scarecrow',offset=(0,-.05))
        furniture('horticulture_compost_bin',5,7,'Garden Compost',offset=(-.1,.18))
        furniture('horticulture_soil_sack',6,7,'Potting Soil',offset=(.18,.2),loose=True)
        furniture('horticulture_drying_screen',7,7,'Herbs Drying on a Screen',offset=(0,.18))
        furniture('horticulture_round_table',11,7,'Garden Rest Table',offset=(0,.12))
        furniture('horticulture_round_stool',12,7,'Garden Seat',offset=(-.08,.18))
        furniture('horticulture_herb_basket',10,7,'Cut Herbs',offset=(.18,.15),loose=True)
        furniture('horticulture_wheelbarrow',2,7,'Garden Wheelbarrow',offset=(0,-.08))
        for bed in [(5,3,3,2),(10,3,3,2),(5,6,3,1),(10,6,3,1)]:crop_border(*bed)
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
        furniture('horticulture_tool_crate',6,7,'Equipment Repair Tools',offset=(.15,.2),loose=True)
        furniture('hay_bale',8,7,'Spare Target Straw',offset=(.1,.18))
        furniture('wash_tub',9,7,'Training Yard Water',offset=(0,.2))
        furniture('horticulture_round_stool',11,7,'Rest Stool',offset=(0,.15))
        board['activity_areas']=['Worn sparring court','Dummy practice stations','Two archery lanes','Equipment and rest corner']
    board['ground_art']=list(art.values())
    board['dressing_version']='activity-v2'
