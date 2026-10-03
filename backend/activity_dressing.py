"""Authored garden/practice-yard compositions; appearance only.

Ground art is separate from movement material. No decorative plants introduce
hidden collision, harvesting or extra rewards.
"""
from .location_maps import prop
from .battle_maps import occupied_tiles


def dress_activity_site(board):
    location=board['location_id']
    if location not in {'herb_garden','occupied_training_yard'}:
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
        occupied={p for obj in board['terrain']+board['decorations'] if not obj.get('ground_edging') for p in occupied_tiles(obj)}
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
    if board['map_variation']!=1:
        _dress_variation(board,ground,furniture,crop_border,garden)
        board['ground_art']=list(art.values())
        board['dressing_version']='activity-v3'
        return
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


def _dress_variation(board,ground,furniture,crop_border,garden):
    """Distinct area layouts fitted to the annex, divider and deep courtyard."""
    variant=board['map_variation']
    # Follow the actual union of building floors, including the L-shaped annex.
    for layer in board['paint']:
        for x,y in layer.get('tiles',[]):
            ground('garden_soil' if garden else 'practice_earth',x,y,1,1,1)
    ground('garden_worn_soil',0,4,16,3)

    def kit(name,x,y,label=None,loose=False,offset=(0,.12)):
        furniture('horticulture_'+name,x,y,label,offset=offset,loose=loose)

    if garden:
        beds={
            2:[('herbs_broadleaf',5,3,3,2),('herbs_violet',9,3,4,2),('herbs_sage',8,7,2,2)],
            3:[('herbs_broadleaf',5,3,3,2),('herbs_sage',5,6,3,2),('herbs_violet',11,3,3,2),('herbs_white',11,6,3,2)],
            4:[('herbs_white',5,3,2,2),('herbs_violet',9,3,3,2),('herbs_broadleaf',5,6,2,3),('herbs_sage',9,6,3,1)],
        }[variant]
        for sprite,x,y,w,h in beds:ground(sprite,x,y,w,h);crop_border(x,y,w,h)
        path_x={2:8,3:10,4:8}[variant]
        ground('garden_stepping_stones',path_x,2,1,7 if variant==4 else 6,1)
        ground('garden_worn_soil',5,5,7 if variant==4 else 9 if variant==3 else 8,1)
        kit('potting_bench',5,2,'Herbalist’s Potting Bench',offset=(0,-.18))
        kit('round_stool',7,2,'Potting Stool',offset=(-.18,0))
        furniture('herb_planter',3,2,'Herbs Beside the Entrance',loose=True)
        kit('clay_pots',3,3,'Spare Pots',loose=True)
        kit('wheelbarrow',2,7,'Garden Wheelbarrow',offset=(0,-.08))
        if variant==2:
            kit('seedling_tray',9,2,'Seedlings',loose=True)
            kit('hand_pump',11,2,'Garden Hand Pump',offset=(.12,-.18))
            furniture('wash_tub',12,2,'Garden Wash Tub',offset=(.12,-.18))
            kit('scarecrow',6,3,'Garden Scarecrow')
            kit('watering_can',12,3,'Watering Can',loose=True)
            kit('compost_bin',8,6,'Garden Compost')
            kit('drying_screen',10,6,'Herb Drying Screen')
            kit('round_table',10,8,'Annex Rest Table')
            kit('round_stool',11,8,'Garden Seat')
            kit('herb_basket',12,8,'Cut Herbs',loose=True)
            board['activity_areas']=['Broad northern herb plots','Cross-path into the annex','Annex drying and compost','Sheltered rest corner']
        elif variant==3:
            kit('hand_pump',11,2,'Garden Hand Pump',offset=(.18,-.18))
            furniture('wash_tub',12,2,'Garden Wash Tub',offset=(0,-.18))
            furniture('bound_barrels',13,2,'Stored Garden Water',offset=(0,-.18))
            kit('scarecrow',6,3,'Garden Scarecrow')
            kit('compost_bin',5,8,'Garden Compost')
            kit('soil_sack',6,8,'Potting Soil',loose=True)
            kit('seedling_tray',7,8,'Seedlings',loose=True)
            kit('drying_screen',11,8,'Herb Drying Screen')
            kit('round_stool',13,8,'Drying-room Stool')
            kit('tool_crate',8,2,'Gardening Tools',loose=True)
            board['activity_areas']=['Western nursery','Eastern flowering herbs','Open route through the divider gate','Separate potting and drying stations']
        else:
            ground('garden_worn_soil',8,8,4,1)
            kit('tool_crate',9,2,'Gardening Tools',loose=True)
            kit('seedling_tray',11,2,'Seedlings',loose=True)
            kit('scarecrow',5,7,'Garden Scarecrow')
            kit('compost_bin',5,9,'Garden Compost')
            kit('soil_sack',6,9,'Potting Soil',loose=True)
            kit('drying_screen',9,7,'Herb Drying Screen')
            kit('watering_can',11,7,'Watering Can',loose=True)
            kit('round_table',7,9,'Garden Rest Table')
            kit('round_stool',7,8,'Garden Seat')
            furniture('wash_tub',9,9,'Wash-court Tub',offset=(0,.12))
            kit('hand_pump',10,9,'Wash-court Pump')
            kit('hose_coil',11,9,'Irrigation Hose',loose=True)
            board['activity_areas']=['Long western herb plot','Northern flower plots','Path to the side gate','Southern wash and compost court']
    else:
        if variant==2:
            ground('practice_scuffs',5,3,4,2)
            ground('practice_straw',5,2,4,1)
            ground('practice_straw',10,2,3,1)
            ground('practice_footprints',11,3,2,5,1)
            for x in [6,8]:furniture('straw_training_dummy',x,2,'Practice Dummy',offset=(0,-.12))
            for x,s in [(11,'archery_target'),(12,'hay_archery_butt')]:furniture(s,x,2,'Range Target',offset=(0,-.12))
            furniture('practice_weapon_rack',8,8,'Practice Weapons')
            furniture('training_shield_rack',9,8,'Practice Shields')
            furniture('mess_bench',10,8,'Annex Rest Bench')
            furniture('arrow_bundle',12,8,'Spare Arrows',loose=True)
            furniture('wash_tub',8,7,'Training Yard Water')
            kit('tool_crate',9,7,'Equipment Repair Tools',loose=True)
            kit('round_stool',11,8,'Rest Stool')
            board['activity_areas']=['Compact sparring yard','Long side archery range','Equipment in the annex','Water and rest corner']
        elif variant==3:
            ground('practice_scuffs',5,3,4,5)
            ground('practice_straw',5,2,4,1)
            ground('practice_straw',10,2,4,1)
            ground('practice_footprints',12,3,2,5,1)
            furniture('straw_training_dummy',6,2,'Practice Dummy')
            furniture('armored_training_dummy',7,2,'Armored Practice Dummy')
            furniture('archery_target',12,2,'Range Target')
            furniture('hay_archery_butt',13,2,'Straw Range Target')
            furniture('practice_weapon_rack',5,8,'Practice Weapons')
            kit('tool_crate',6,8,'Equipment Repair Tools',loose=True)
            furniture('training_shield_rack',7,8,'Practice Shields')
            furniture('wash_tub',8,8,'Training Yard Water')
            furniture('hay_bale',10,8,'Spare Target Straw')
            furniture('mess_bench',11,8,'Rest Bench')
            kit('round_stool',12,8,'Rest Stool')
            furniture('arrow_bundle',13,8,'Spare Arrows',loose=True)
            board['activity_areas']=['Western sparring court','Eastern archery court','Open divider-gate approach','Separate equipment and rest stations']
        else:
            ground('practice_scuffs',5,3,3,5)
            ground('practice_straw',5,2,3,1)
            ground('practice_straw',10,2,2,1)
            ground('practice_footprints',10,3,2,5,1)
            for x in [5,7]:furniture('straw_training_dummy',x,2,'Practice Dummy')
            kit('tool_crate',6,2,'Equipment Repair Tools',loose=True)
            furniture('archery_target',10,2,'Range Target')
            furniture('hay_archery_butt',11,2,'Straw Range Target')
            furniture('practice_weapon_rack',5,9,'Practice Weapons')
            furniture('training_shield_rack',6,9,'Practice Shields')
            furniture('hay_bale',7,9,'Spare Target Straw')
            furniture('mess_bench',9,9,'Rest Bench')
            kit('round_stool',10,9,'Rest Stool')
            furniture('arrow_bundle',11,9,'Spare Arrows',loose=True)
            furniture('wash_tub',9,7,'Training Yard Water')
            board['activity_areas']=['Deep sparring court','Long eastern archery lanes','Clear side-gate approach','Southern equipment and rest area']
