"""Authored, debug-only material maps. No mission content or rewards live here."""
import random
from .location_maps import place_building, wall

FAMILIES={'timber':'Timber','fieldstone':'Rough stone','limestone':'Polished stone','iron':'Metal',
          'limestone_plan':'Polished stone (Pure overhead)',
          'fieldstone_plan':'Rough stone (Pure overhead)',
          'limestone_boxed':'Polished stone (Boxed six-piece trial)'}
PARTS={'wall','corner','junction','cross','end','breach','door_closed','door_open',
       'gate_closed','gate_open','window','pillar','stairs','corner_broken','edge_junction','brace'}
PLANS=[('gatehouse','Gatehouse and courtyard','workshop_forge_yard'),
       ('divided_hall','Divided hall and branching partitions','workshop_repair_hall'),
       ('breached_annex','Breached annex and repairs','tool_annex_yard'),
       ('twin_stores','Twin stores and loading court','tool_twin_sheds')]


def presets(family):
    return [{'id':f'{family}_{ident}','label':label,'seed':f'material-layout-{i+1}'}
            for i,(ident,label,_) in enumerate(PLANS)]


def blueprint(family,seed):
    if family not in FAMILIES:raise ValueError('Unknown showcase material')
    if family=='limestone_boxed':return boxed_blueprint(seed)
    forced=next((i for i,p in enumerate(presets(family)) if p['seed']==seed),None)
    variant=forced if forced is not None else random.Random(f'{family}:{seed}').randrange(4)
    ident,label,building_id=PLANS[variant];anchor=(5,2)
    piece=place_building(building_id,anchor,'showcase',family_override=family)
    terrain=piece['terrain'];decorations=piece['decorations'];ax,ay=anchor

    def at(x,y):return next(t for t in terrain if (t['x'],t['y'])==(ax+x,ay+y))
    def change(x,y,part):
        t=at(x,y);t['sprite']=f'structure:{family}_{part}';t['name']=part.replace('_',' ').title()
        return t
    def add(x,y,part,rotation=0,blocking=True):
        t=wall(ax+x,ay+y,f'showcase_{part}_{x}_{y}',family=family,rotation=rotation)
        t.update(sprite=f'structure:{family}_{part}',name=part.replace('_',' ').title(),blocking=blocking,
                 blocks_sight=blocking)
        (terrain if blocking else decorations).append(t)
        return t
    def opened_gate(x,y,type_):
        t=at(x,y);prefix=f'structure:{family}_{type_}'
        t.update(kind='gate',name='Open '+type_,state='opened',sprite=prefix+'_open',
                 closed_sprite=prefix+'_closed',open_sprite=prefix+'_open',blocking=False,blocks_sight=False)
    if variant==0:
        change(4,0,'window')
        opened_gate(9,4,'gate')
        add(4,4,'pillar')
    elif variant==1:
        change(6,2,'junction')
        change(6,4,'cross')
        add(5,2,'wall');add(4,2,'end')
        add(5,4,'wall');add(4,4,'end');add(7,4,'wall')
        # The branches terminate in the room; the center divider joins the shell.
    elif variant==2:
        opened_gate(0,2,'door')
        t=change(7,0,'corner_broken')
        t.update(kind='rubble',name='Damaged Corner',blocking=False,blocks_sight=False,
                 destructible=False,hp=0,movement_cost=2)
        add(1,6,'brace',blocking=False)
    else:
        change(1,0,'window')
        add(4,2,'stairs',blocking=False)
        add(5,5,'pillar')
        add(5,7,'brace',blocking=False)
    blocked={(t['x'],t['y']) for t in terrain if t.get('blocking') and not t.get('edge_wall')}
    floor={tuple(cell) for p in piece['paint'] for cell in p['tiles']}
    candidates=[(t['x'],t['y']) for t in piece['enemies']]+sorted(floor)
    enemies=[]
    for x,y in candidates:
        if (x,y) not in blocked and (x,y) not in {(p['x'],p['y']) for p in enemies}:
            enemies.append({'x':x,'y':y})
        if len(enemies)==8:break
    width=anchor[0]+piece['width']+2;height=max(12,anchor[1]+piece['height']+2)
    shown=sorted({t['sprite'].removeprefix(f'structure:{family}_') for t in terrain+decorations
                  if t.get('sprite','').startswith(f'structure:{family}_')})
    return {'name':FAMILIES[family]+' · '+label,'theme':'location-workshop',
            'width':width,'height':height,'default_ground':'grass',
            'paint':[{'material':'dirt','rect':[0,4,5,3]},*piece['paint']],
            'terrain':terrain,'decorations':decorations,'elevation':[],'void_tiles':[],
            'extraction':{'name':'Test entrance','tiles':[{'x':0,'y':y} for y in range(3,8)]},
            'enemy_extraction':{'name':'Test entrance','tiles':[{'x':0,'y':y} for y in range(3,8)]},
            'spawn_zones':{'player':[{'x':1,'y':y} for y in (5,4,6,3)],'enemy':enemies},
            'template_id':f'{family}_{ident}','map_variation':variant+1,
            'building_templates':[{'id':building_id,'label':label,'anchor':list(anchor)}],
            'material_showcase':{'family':family,'label':FAMILIES[family], 'pieces':shown,
                'notes':'Art test: stairs and braces are scenery; doors and walls use normal interactions.'}}


def boxed_blueprint(seed):
    """The same four furnished buildings, rebuilt using the generated wall kit."""
    family='limestone_boxed'
    # Keep former bookmarked lab seeds usable, now selecting real buildings.
    aliases={f'boxed-walls-{i+1}':f'material-layout-{i+1}' for i in range(4)}
    seed=aliases.get(seed,seed)
    base=blueprint('limestone',seed)
    variant=base['map_variation']-1
    ident,label,_=PLANS[variant]
    base.update(name=FAMILIES[family]+' ? '+label,template_id=f'{family}_{ident}')
    shown=set()
    for collection in ('terrain','decorations'):
        kept=[]
        for item in base[collection]:
            sprite=item.get('sprite','')
            if not sprite.startswith('structure:limestone_'):
                kept.append(item);continue
            part=sprite.removeprefix('structure:limestone_')
            if part in {'pillar','stairs','brace'}:
                # Decorative support samples are not part of the candidate atlas.
                # Existing furnished room contents remain unchanged.
                continue
            rotation=item.get('rotation',0)
            old_offset=item.get('art_offset',[0,0])
            item['art_offset']=[0,0]
            if part.startswith(('door_','gate_')):
                # Deliberate wooden leaves in the stone shell, using existing
                # working open/closed gate art; no substitute old stone masonry.
                item.update(sprite='structure:timber_'+part,
                            closed_sprite=item.get('closed_sprite','').replace('limestone_','timber_'),
                            open_sprite=item.get('open_sprite','').replace('limestone_','timber_'),
                            destroyed_sprite='structure:timber_breach',
                            art_scale=1.25,name='Timber '+part.replace('_',' '))
                kept.append(item);continue
            if part in {'breach','corner_broken'}:
                # Real gaps in the same authored broken-wall locations.
                item.update(sprite='structure:wall_rubble',blocking=False,blocks_sight=False,
                            art_scale=.65,destructible=False,hp=0,name='Gap with loose stone debris')
                kept.append(item);continue
            mapped={'window':'wall','end':'half'}.get(part,part)
            offset=.38
            def turned(point):
                x,y=point
                for _ in range(rotation//90):x,y=-y,x
                return [x,y]
            if mapped=='corner':
                dx,dy=turned([offset,-offset])
                item['art_offset']=[old_offset[0]*offset/.3118+dx,
                                    old_offset[1]*offset/.3118+dy]
            elif mapped=='edge_junction':
                item['art_offset']=turned([0,-offset])
            elif item.get('edge_wall') and len(item.get('wall_edges',[]))==1:
                item['art_offset']={'north':[0,-offset],'south':[0,offset],
                                    'east':[offset,0],'west':[-offset,0]}[item['wall_edges'][0]]
            elif mapped=='half':
                item['art_offset']=turned([.25,0])
            if mapped=='wall' and rotation%180==90:
                mapped='vertical';rotation=(rotation-90)%360
            item.update(sprite=f'structure:{family}_{mapped}',rotation=rotation,
                        art_scale=1024/397,destroyed_sprite=None)
            shown.add(mapped);kept.append(item)
        base[collection]=kept
    # Centered masonry occupies its tile. Spawn only on unobstructed room floors.
    blocked={(t['x'],t['y']) for t in base['terrain'] if t.get('blocking')}
    floor=[tuple(cell) for layer in base['paint'] for cell in layer.get('tiles',[])]
    candidates=[(p['x'],p['y']) for p in base['spawn_zones']['enemy']]+floor
    enemies=[]
    for x,y in candidates:
        if (x,y) not in blocked and (x,y) not in {(e['x'],e['y']) for e in enemies}:
            enemies.append({'x':x,'y':y})
        if len(enemies)==8:break
    base['spawn_zones']['enemy']=enemies
    base['material_showcase']={'family':family,'label':FAMILIES[family],'pieces':sorted(shown),
        'notes':'Boundary-fitted stone walls and authored junctions, working timber doors/gates and traversable breaches. Painted texture transitions remain under review.'}
    return base
