"""D-rank roads: four distinct tactical plans per mission, not E-rank reskins."""
from .location_maps import prop, place_building
from .building_templates import BUILDINGS

LOCATIONS={'highway_cut':'highway_ambush','cemetery_road':'bone_patrol','boar_rider_route':'goblin_boar_riders'}
ROSTERS={
 'highway_ambush':[('enforcer','trapper','lookout'),('skirmisher','enforcer','lookout'),
                   ('trapper','skirmisher','enforcer'),('pilferer','pilferer','light_lookout','pilferer')],
 'bone_patrol':[('warden','guard','lookout'),('guard','warden','lookout'),
                ('warden','lookout','guard'),('pilferer','pilferer','light_lookout','pilferer')],
 'goblin_boar_riders':[('guard','skirmisher','lookout'),('skirmisher','guard','lookout'),
                       ('ringleader','guard','lookout'),('pilferer','pilferer','light_lookout','pilferer')],
}
LABELS={
 'highway_cut':['Rock-cut crossfire','Wagon choke and flank','Broken roadside relay','Raiders dividing the haul'],
 'cemetery_road':['Funeral avenue','Chapel relic transfer','Graveyard switchback','Scattered bone procession'],
 'boar_rider_route':['Messenger relay stop','Open cavalry bend','Split weapons convoy','Scattered young riders'],
}
ACTIVITY={
 'highway_cut':['Bandits watch both sides of the rock cut.','Bandits block the wagon lane while a scout covers the bypass.',
                'Raiders hold the broken relay station and its rear road.','Four lighter raiders sort stolen goods along the road.'],
 'cemetery_road':['Armored dead carry relics along the funeral avenue.','The patrol transfers chapel relics outside the ruined doorway.',
                  'The dead march between separated burial plots.','Four lighter bone carriers spread across the procession route.'],
 'boar_rider_route':['Mounted messengers pause beside the relay shelter.','Riders cover the wide road bend from different approaches.',
                     'A ringleader oversees the transfer of stolen weapons.','Four young riders regroup around scattered supplies.'],
}

def blueprint(location, variation):
    mid=LOCATIONS[location];n=len(ROSTERS[mid][variation])
    board={'name':LABELS[location][variation],'theme':f'd-rank-{location}','location_id':location,
           'template_id':f'd_{location}_{variation+1}','template_label':LABELS[location][variation],
           'map_variation':variation+1,'width':16,'height':12,'default_ground':'grass',
           'paint':[{'material':'dirt','rect':[0,5,16,3]}],'terrain':[], 'decorations':[],
           'void_tiles':[],'elevation':[],'extraction':{'name':'Guild Road','tiles':[{'x':0,'y':y} for y in range(4,9)]},
           'enemy_extraction':{'name':'Far Road','tiles':[{'x':15,'y':y} for y in range(4,9)]},
           'spawn_zones':{'player':[{'x':1,'y':6},{'x':1,'y':7},{'x':2,'y':6},{'x':2,'y':7}]}}
    positions={
        'highway_cut':[[(10,3),(10,8),(12,5)],[(10,6),(11,9),(13,3)],
                       [(9,7),(11,8),(14,6)],[(9,4),(11,7),(13,3),(13,9)]],
        'cemetery_road':[[(9,6),(11,6),(13,6)],[(10,6),(11,9),(14,5)],
                        [(8,6),(11,10),(13,7)],[(10,4),(12,7),(14,3),(12,9)]],
        'boar_rider_route':[[(9,6),(11,8),(13,5)],[(8,4),(11,8),(14,5)],
                           [(11,6),(9,8),(14,9)],[(9,3),(11,9),(14,4),(14,8)]],
    }
    board['spawn_zones']['enemy']=[{'x':x,'y':y} for x,y in positions[location][variation][:n]]
    if location=='highway_cut':
        if variation==0:
            for x,y in [(6,3),(7,3),(8,8),(9,8)]:board['terrain'].append(prop(f'cut_{x}_{y}','Road-cut Boulder','rounded_boulder',x,y))
            board['elevation']=[{'x':10,'y':3,'height':1,'kind':'road_cut'},{'x':10,'y':8,'height':1,'kind':'road_cut'}]
        elif variation==1:
            board['terrain'].append(prop('abandoned_wagon','Abandoned Wagon','wooden_handcart',7,6))
            board['paint'].append({'material':'dirt','rect':[5,8,6,2]})
        elif variation==2:
            add_building(board,'road_relay_house',(6,0),'relay_house')
        else:
            board['decorations'] += [prop('loot_'+str(i),'Stolen Goods','stacked_planks',x,y,False) for i,(x,y) in enumerate([(7,3),(9,9),(12,1)])]
    elif location=='cemetery_road':
        board['default_ground']='grave_earth'
        board['paint'][0]['material']='grave_path'
        if variation==1:add_building(board,'chapel_1',(6,0),'ruined_chapel')
        graves=[(6,2),(8,2),(6,9),(8,9)] if variation in (0,1) else [(5,3),(7,8),(9,2),(11,10)]
        for i,(x,y) in enumerate(graves):
            board['decorations'].append(prop(f'grave_{i}','Burial Marker','mossy_gravestone' if i%2 else 'grave_cross',x,y,False))
        if variation==2:
            board['terrain'] += [prop('grave_wall_north','Collapsed Tomb','rounded_boulder',7,3),prop('grave_wall_south','Collapsed Tomb','rounded_boulder',9,9)]
        board['decorations'].append(prop('relics','Carried Chapel Relics','old_bone_pile',14,1,False))
    else:
        if variation==0:add_building(board,'road_relay_house',(6,0),'messenger_shelter')
        if variation==1:board['paint'].append({'material':'dirt','rect':[8,2,3,9]})
        if variation==2:
            board['terrain'].append(prop('weapons_cart','Stolen Weapons Cart','wooden_handcart',7,6))
            board['paint'].append({'material':'dirt','rect':[5,8,9,2]})
        board['decorations'] += [prop('rider_supplies_'+str(i),'Rider Supplies','crate_closed',x,y,False) for i,(x,y) in enumerate([(5,1),(8,10),(14,10)])]
    return board

def add_building(board, template, anchor, ident, family=None):
    piece=place_building(template,anchor,ident,family_override=family)
    for key in ('terrain','decorations','paint'):board[key]+=piece[key]
    board.setdefault('building_templates',[]).append({'id':template,'anchor':list(anchor),'family':family or BUILDINGS[template]['family']})
