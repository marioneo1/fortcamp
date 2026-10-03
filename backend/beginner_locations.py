"""Compact early contract sites and a reclaimed training yard.

These change battle scenery/layout only; roll paths, encounter budgets and
reward conditions remain owned by each contract.
"""
from copy import deepcopy

BEGINNER_SETTINGS = {
    'provision_store': ['Long provision shed','Two provision stores','Store with rear annex','Store and delivery court'],
    'farm_clearing': ['Fence and broken rear rail','Offset livestock clearing','Two farm paddocks','Deep fenced pasture'],
    'herb_garden': ['Walled herb beds','Garden with an annex','Divided herb garden','Garden and wash court'],
    'purse_road': ['Road bend and roadside ditch','Fork and abandoned handcart','Narrow road with brush','Passing place and fallen tree'],
    'well_yard': ['Well and ruined cottage','Well behind a broken boundary','Well between two ruins','Village wash court'],
    'supply_stop': ['Single delivery store','Paired supply shelters','Supply post and side store','Delivery yard and store'],
    'occupied_training_yard': ['Sparring yard and archery lane','Practice yard with side range','Two drill courts','Deep training court'],
}


def add_beginner_buildings(buildings):
    # Four reusable store footprints: long hall, separate stores, an L-shaped
    # annex and an attached delivery yard. Neither reflections nor rotations.
    specs = [
        ([(0,0,8,5)],[(0,2,'door'),(7,2,'door')],[(3,4)]),
        ([(0,0,4,5),(5,0,4,5)],[(0,2,'door'),(3,2,'door'),(5,2,'door')],[]),
        ([(0,0,7,4),(3,3,4,4)],[(0,2,'door')],[(6,5)]),
        ([(0,0,9,7)],[(0,3,'gate'),(8,3,'door')],[(4,6)]),
    ]
    yards = [
        ([(0,0,10,8)],[(0,4,'gate'),(9,4,'gate')],[(9,6)]),
        ([(0,0,10,6),(3,5,7,4)],[(0,4,'gate'),(9,6,'gate')],[(6,8)]),
        ([(0,0,11,9)],[(0,4,'gate'),(10,4,'gate')],[(10,7)]),
        ([(0,0,9,10)],[(0,4,'gate'),(8,7,'gate')],[(4,9)]),
    ]
    for i,(rooms,doors,breaches) in enumerate(specs,1):
        buildings[f'provision_store_{i}']={'label':BEGINNER_SETTINGS['provision_store'][i-1],
            'family':'timber','floor':'shed_floor','rooms':rooms,'doors':doors,
            'breaches':breaches,'enemies':[],'door_name':'Store Door','gate_name':'Delivery Gate'}
    for i,(rooms,doors,breaches) in enumerate(yards,1):
        definition={'label':f'Enclosed activity yard {i}','family':'timber','floor':'dirt',
                    'rooms':rooms,'doors':doors,'breaches':breaches,'enemies':[],
                    'gate_name':'Yard Gate'}
        if i==3:
            definition['partitions']=[(5,y) for y in (1,2,3,5,6,7)]
            definition['internal_doors']=[(5,4,'gate')]
        buildings[f'activity_yard_{i}']=definition


def blueprint(location, variant, rng):
    from .location_maps import place_building, prop
    from .battle_maps import occupied_tiles
    board={'name':location,'theme':'location-shed','width':16,'height':13,
        'default_ground':'grass','paint':[],'terrain':[],'decorations':[],
        'void_tiles':[],'elevation':[],'location_id':location,'map_variation':variant+1,
        'template_id':f'{location}_{variant+1}','template_label':BEGINNER_SETTINGS[location][variant],
        'extraction':{'name':'Guild Road','tiles':[{'x':0,'y':y} for y in range(3,8)]},
        'spawn_zones':{'player':[{'x':1,'y':y} for y in (5,4,6,3)],'enemy':[]},
        'building_templates':[]}
    board['enemy_extraction']=deepcopy(board['extraction'])
    t,d,p=board['terrain'],board['decorations'],board['paint']
    p.append({'material':'dirt','rect':[0,4,16,3]})
    candidate_floor=set()

    def building(ident,anchor,family=None):
        piece=place_building(ident,anchor,ident,family_override=family)
        if ident.startswith('activity_yard'):
            for layer in piece['paint']:
                layer['material']='grass' if location=='farm_clearing' else 'dirt'
        t.extend(piece['terrain']);d.extend(piece['decorations']);p.extend(piece['paint'])
        board['building_templates'].append({'id':ident,'label':piece['label'],'anchor':list(anchor)})
        candidate_floor.update(tuple(cell) for layer in piece['paint'] for cell in layer.get('tiles',[]))
        return piece

    def item(sprite,x,y,name=None,loose=False,size=None):
        taken={cell for obj in t for cell in occupied_tiles(obj)}
        taken.update((obj['x'],obj['y']) for obj in d)
        if (x,y) in taken:
            alternatives=sorted(candidate_floor-taken,key=lambda cell:(abs(cell[0]-x)+abs(cell[1]-y),cell[1],cell[0]))
            if not alternatives:raise ValueError(f'{location}: no space for {sprite}')
            x,y=alternatives[0]
        value=prop(f'{location}_{sprite}_{x}_{y}',name or sprite.replace('_',' ').title(),sprite,x,y,not loose)
        if size:value['footprint']=list(size)
        (d if loose else t).append(value)

    if location in {'provision_store','supply_stop'}:
        building(f'provision_store_{variant+1}',(5,2))
        # Corner storage leaves each interior aisle and doorway clear.
        if variant==0:
            goods=[(6,3),(10,3),(11,5)]
        elif variant==1:
            goods=[(6,3),(11,3),(12,5)]
        elif variant==2:
            goods=[(6,3),(10,3),(10,7)]
        else:
            goods=[(6,3),(11,3),(12,7)]
        for sprite,(x,y) in zip(['grain_sacks','bound_barrels','blanket_chest'],goods):item(sprite,x,y)
        item('wooden_handcart',4,9,loose=True)
        item('camp_lantern',4,3,loose=True)
        if location=='supply_stop':
            item('water_trough',7,10)
            candidate_floor.update((x,y) for x in range(8,14) for y in range(9,12))
    elif location in {'farm_clearing','herb_garden','occupied_training_yard'}:
        family='limestone' if location=='herb_garden' else 'timber'
        piece=building(f'activity_yard_{variant+1}',(4,1),family)
        if location=='herb_garden':
            for x,y in [(6,2),(7,2),(11,2),(12,2)]:item('herb_planter',x,y)
            item('herb_planter',3,2,loose=True)
            item('wash_tub',6,3)
        elif location=='farm_clearing':
            for x,y in [(6,2),(7,2),(11,2)]:item('hay_bale',x,y)
            item('water_trough',6,3)
            item('dense_shrub',11,3,loose=True)
        else:
            for x,y in [(6,2),(7,2)]:item('straw_training_dummy',x,y)
            for x,y in [(11,2),(12,2)]:item('archery_target',x,y)
            item('practice_weapon_rack',6,3)
            item('training_shield_rack',7,3)
            item('canvas_cot',11,3,loose=True)
            p.append({'material':'dirt','rect':[10,4,3,3]})
    elif location=='well_yard':
        # Ruined cottage pieces are off the open central well courtyard.
        anchors=[(7,1),(6,1),(5,1),(6,2)]
        piece=building(f'provision_store_{variant+1}',anchors[variant],'fieldstone')
        if variant==1:
            # Give the paired ruins a collapsed southern boundary as well as
            # their normal doors, rather than presenting two intact houses.
            fallen=next(obj for obj in reversed(piece['terrain']) if obj['kind']=='wall')
            fallen.update(kind='rubble',blocking=False,blocks_sight=False,destroyed=True,
                          hp=0,sprite='structure:fieldstone_breach',name='Collapsed Cottage Wall')
        item('village_well',7,10,'Old Village Well')
        item('wash_tub',9,10)
        item('fallen_gravestone',12,10,'Broken Village Boundary Stone',loose=True)
        p.append({'material':'toll_cobbles','rect':[5,9,7,3]})
        # The cobbled village yard offers room to approach either ruin.
        candidate_floor.update((x,y) for x in range(5,13) for y in range(9,12))
    else:
        routes=[[[0,4,8,3],[7,4,3,6],[9,7,7,3]],
                [[0,4,16,3],[8,1,3,4]],
                [[0,5,16,2]],[[0,4,16,3],[7,3,5,6]]]
        p[:]=[{'material':'dirt','rect':rect} for rect in routes[variant]]
        purse=[(9,7),(9,5),(8,5),(9,6)][variant]
        item('dropped_coin_purse',*purse,'Dropped Purse',loose=True)
        if variant==1:item('wooden_handcart',11,2,loose=True)
        if variant==3:item('fallen_branches',10,9,loose=True)
        p.append({'material':'forest_dark','rect':[6,9,7,1]})
        for x,y in [(7,3),(10,3),(12,8)]:item('dense_shrub',x,y)
        candidate_floor.update((x,y) for x in range(7,14) for y in range(4,9))

    # Any branch/rank may need up to eight enemies. Candidates are genuinely
    # free floor, not furniture, wall cells, entrance queues or loose scenery.
    if location in {'herb_garden','occupied_training_yard'}:
        from .activity_dressing import dress_activity_site
        dress_activity_site(board)
    occupied={cell for obj in t for cell in occupied_tiles(obj)}
    scenery={cell for obj in d if not obj.get('ground_edging') for cell in occupied_tiles(obj)}
    gateways={(g['x']+dx,g['y']+dy) for g in t if g['kind']=='gate'
              for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]}
    valid=candidate_floor-occupied-scenery-gateways
    preferred=sorted(valid,key=lambda cell:(abs(cell[0]-10)+abs(cell[1]-6),cell[1],cell[0]))
    if location in {'provision_store','supply_stop'} and variant==1:
        # A two-enemy early encounter should occupy both stores.
        left=next(cell for cell in preferred if cell[0]<9)
        right=next(cell for cell in preferred if cell[0]>9)
        preferred=[left,right]+[cell for cell in preferred if cell not in {left,right}]
    minimum=2 if location=='provision_store' else 8
    if len(preferred)<minimum:raise ValueError(f'{location}: not enough clear enemy deployment cells')
    board['spawn_zones']['enemy']=[{'x':x,'y':y} for x,y in preferred[:8]]
    for i,(x,y) in enumerate([(2,1),(2,11),(14,11)]):item('oak_tree' if i==0 else 'dense_shrub',x,y,loose=True)
    return board
