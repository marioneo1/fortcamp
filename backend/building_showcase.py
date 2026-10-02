"""Authored, debug-only material maps. No mission content or rewards live here."""
import random
from .location_maps import place_building, wall

FAMILIES={'timber':'Timber','fieldstone':'Rough stone','limestone':'Polished stone','iron':'Metal'}
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
