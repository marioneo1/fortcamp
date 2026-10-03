"""Road-spanning blockades and nested military compounds, using approved art."""
from copy import deepcopy

ROAD_PLANS = [
    ('straight_barrier', 'Straight road and guarded barrier'),
    ('bent_road', 'Bent road and supply pull-off'),
    ('staggered_barriers', 'Staggered roadblocks and flank track'),
    ('double_checkpoint', 'Two checkpoints and rear stores'),
]
CAMP_PLANS = [
    ('gate_court', 'Gate court and inner command house'),
    ('annex_camp', 'Offset camp and supply annex'),
    ('paired_barracks', 'Paired barracks around a drill yard'),
    ('breached_camp', 'Deep command camp with damaged rear wall'),
]
COMMAND_SETTINGS = {'road_blockade','command_post','command_camp','timber_redoubt','vanguard_camp'}


def add_command_buildings(buildings):
    for i, (rooms, doors, breaches) in enumerate([
        ([(0,0,12,10)],[(0,5,'gate'),(11,5,'gate')],[]),
        ([(0,0,13,8),(5,7,8,4)],[(0,4,'gate'),(12,8,'gate')],[]),
        ([(0,0,14,12)],[(0,5,'gate'),(7,11,'gate')],[]),
        ([(0,0,12,12)],[(0,6,'gate'),(11,6,'gate')],[(4,11)]),
    ],1):
        buildings[f'camp_shell_{i}']={'label':CAMP_PLANS[i-1][1],'family':'timber','floor':'dirt',
            'rooms':rooms,'doors':doors,'breaches':breaches,'enemies':[],
            'gate_name':'Camp Gate'}
    for i, (rooms, doors, enemies, furniture) in enumerate([
        ([(0,0,5,5)],[(0,2,'door')],[(3,2),(1,1),(2,1),(3,1),(1,3),(2,3),(3,3),(2,2)],
         [('wooden_table',2,3),('weapon_rack',3,3)]),
        ([(0,0,6,5)],[(0,2,'door'),(5,2,'door')],[(4,2),(1,1),(2,1),(3,1),(4,1),(1,3),(2,3),(3,3)],
         [('wooden_table',4,3),('weapon_rack',4,1)]),
        ([(0,0,6,4),(3,3,3,3)],[(0,2,'door')],[(4,2),(1,1),(2,1),(3,1),(4,1),(1,2),(2,2),(4,4)],
         [('wooden_table',3,2),('weapon_rack',4,4)]),
        ([(0,0,4,5),(5,0,4,5)],[(0,2,'door'),(3,2,'door'),(5,2,'door')],
         [(6,2),(1,2),(7,1),(2,1),(6,1),(1,1),(7,3),(2,3)],
         [('wooden_table',1,3),('weapon_rack',6,3)]),
    ],1):
        occupied={(x,y) for _,x,y in furniture}
        # Keep up to eight safe interior candidates; small posts need only 2–3.
        floor={(x,y) for rx,ry,w,h in rooms for x in range(rx,rx+w) for y in range(ry,ry+h)}
        interior={p for p in floor if all((p[0]+dx,p[1]+dy) in floor for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])}
        safe=[p for p in enemies if p in interior and p not in occupied]
        safe+=sorted(interior-occupied-set(safe))
        buildings[f'command_house_{i}']={'label':f'Command post {i}','family':'timber','floor':'shed_floor',
            'rooms':rooms,'doors':doors,'enemies':safe[:8],'furniture':furniture,
            'door_name':'Command Post Door'}
    buildings['command_barracks']={'label':'Guard Barracks','family':'timber','floor':'shed_floor',
        'rooms':[(0,0,5,4)],'doors':[(0,2,'door')],
        'furniture':[('weapon_rack',3,1),('armor_stand',3,2)],
        'enemies':[(1,1),(2,1),(1,2),(2,2)],'door_name':'Barracks Door'}


def blueprint(location, variant, rng):
    # Lazy import keeps the shared building assembler independent of this map.
    from .location_maps import place_building, prop, wall, dress_building
    width,height=(19,12) if location=='road_blockade' else (14,10) if location=='command_post' else (21,15)
    board={'name':location,'theme':'location-shed','width':width,'height':height,
        'default_ground':'grass','paint':[],'terrain':[],'decorations':[],'void_tiles':[],
        'elevation':[],'location_id':location,'map_variation':variant+1,
        'extraction':{'name':'Guild Road','tiles':[{'x':0,'y':y} for y in range(3,8)]},
        'enemy_extraction':{'name':'Far Road','tiles':[{'x':width-1,'y':y} for y in range(3,8)]},
        'spawn_zones':{'player':[{'x':1,'y':y} for y in (5,4,6,3)],'enemy':[]},
        'building_templates':[]}
    t,d,p=board['terrain'],board['decorations'],board['paint']

    def building(ident,anchor,instance,family=None):
        piece=place_building(ident,anchor,instance,family_override=family)
        # An outdoor camp remains a dirt yard when its walls change material.
        if ident.startswith('camp_shell'):
            for layer in piece['paint']:layer['material']='dirt'
        dress_building(piece,rng)
        t.extend(piece['terrain']);d.extend(piece['decorations']);p.extend(piece['paint'])
        board['building_templates'].append({'id':ident,'label':piece['label'],'anchor':list(anchor)})
        board['building_templates'][-1]['dressing_variation']=piece['dressing_variation']
        board.setdefault('dressing_variation',piece['dressing_variation'])
        return piece

    def solid(sprite,x,y,name=None,footprint=None):
        item=prop(f'{location}_{sprite}_{x}_{y}',name or sprite.replace('_',' ').title(),sprite,x,y)
        if footprint:item['footprint']=footprint
        t.append(item)

    def barrier(x, top, bottom, gate, flank=None):
        for y in range(top,bottom+1):
            if y==flank:continue
            item=wall(x,y,f'barrier_{x}_{y}',wood=True,rotation=90)
            item['name']='Roadblock Wall'
            if y==gate:
                prefix='structure:timber_gate'
                item.update(kind='gate',name='Roadblock Gate',state='closed',sprite=prefix+'_closed',
                            closed_sprite=prefix+'_closed',open_sprite=prefix+'_open',hp=12,max_hp=12)
            t.append(item)

    if location=='road_blockade':
        board['template_id']='road_'+ROAD_PLANS[variant][0]
        board['template_label']=ROAD_PLANS[variant][1]
        p.append({'material':'dirt','rect':[0,4,width,3]})
        if variant==0:
            barrier(8,0,height-1,5,9)
            p.append({'material':'dirt','rect':[4,8,9,2]})
        elif variant==1:
            p[:]=[{'material':'dirt','rect':[0,4,6,2]},
                  {'material':'dirt','rect':[5,4,3,5]},{'material':'dirt','rect':[7,7,12,2]}]
            barrier(10,0,height-1,7,2)
        elif variant==2:
            barrier(7,0,6,4);barrier(10,5,height-1,8)
            p.append({'material':'dirt','rect':[7,4,4,5]})
        else:
            barrier(7,0,height-1,5,9);barrier(11,0,height-1,5,2)
            p.extend([{'material':'dirt','rect':[4,8,6,2]},{'material':'dirt','rect':[9,1,5,2]}])
        piece=building('command_house_1',(13,1),'road_guardhouse')
        solid('bound_barrels',15,8);solid('crate_closed',16,8)
        d.append(prop('road_supplies','Stolen Supply Cart','wooden_handcart',14,9,False))
        d.append(prop('road_fire','Watch Fire','campfire_cold',12,9,False))
        board['spawn_zones']['enemy']=[piece['enemies'][0],*[{'x':x,'y':y} for x,y in
            [(12,6),(12,4),(14,7),(17,6),(16,6),(14,6),(17,7)]]]
    elif location=='command_post':
        board['template_id']=f'small_command_{variant+1}'
        board['template_label']=['Single guard post','Through-door guard post','Post with rear annex','Two small command stores'][variant]
        p.append({'material':'dirt','rect':[0,4,width,3]})
        piece=building(f'command_house_{variant+1}',(4,2),'small_command')
        board['spawn_zones']['enemy']=piece['enemies']
        d.append(prop('post_supplies','Camp Supplies','bound_barrels',3,8,False))
    else:
        board['template_id']=location+'_'+CAMP_PLANS[variant][0]
        board['template_label']=CAMP_PLANS[variant][1]
        family='fieldstone' if location=='vanguard_camp' else 'timber'
        outer=building(f'camp_shell_{variant+1}',(5,1),'outer_camp',family)
        command_anchor=[(10,3),(11,2),(13,2),(10,4)][variant]
        inner_family='iron' if location=='vanguard_camp' else 'timber'
        command=building('command_house_1',command_anchor,'inner_command',inner_family)
        if variant==2:
            building('command_barracks',(13,8),'south_barracks',inner_family)
        p.append({'material':'dirt','rect':[0,4,6,3]})
        # Two-by-two tents occupy their whole footprint, not only their anchor.
        solid('canvas_tent',7,2,'Supply Tent',[2,2])
        solid('crate_closed',7,7);solid('weapon_rack',8,7)
        d.extend([prop('camp_fire','Camp Fire','campfire_lit',9,7,False),
                  prop('camp_bell','Camp Alarm Bell','alarm_bell_active',6,2,False)])
        # The boss occupies the inner house; guards occupy the outer approach.
        board['spawn_zones']['enemy']=[command['enemies'][0],
            *[{'x':x,'y':y} for x,y in [(7,5),(8,5),(9,5),(7,6),(8,6),(9,6),(10,8)]]]
        board['enemy_extraction']=deepcopy(board['extraction'])
    # Decorations define coherent edges without closing deployment/exit lanes.
    for i,(x,y) in enumerate([(3,1),(3,height-2),(width-2,height-2)]):
        d.append(prop(f'camp_edge_{i}','Roadside Tree','pine_tree' if i%2 else 'oak_tree',x,y,False))
    return board
