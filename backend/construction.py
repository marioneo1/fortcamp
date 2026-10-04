"""Player-owned construction layers, independent of camp facility functions."""
from functools import lru_cache
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHORS = {'center':(.5,.5),'north':(.5,0),'east':(1,.5),'south':(.5,1),'west':(0,.5)}
ARMS = {'straight':[(-.5,0),(.5,0)],'half':[(.5,0)],'corner':[(.5,0),(0,.5)],
        'tee':[(-.5,0),(.5,0),(0,.5)],'cross':[(-.5,0),(.5,0),(0,-.5),(0,.5)],
        'gate':[(-.5,0),(.5,0)]}
AVAILABLE_WALL_PIECES = json.loads((ROOT/'frontend/src/construction-wall-pieces.json').read_text())
WALL_PIECES = {**json.loads((ROOT/'frontend/src/construction-wall-pieces-legacy.json').read_text()),**AVAILABLE_WALL_PIECES}
MATERIALS = ['timber','fieldstone','limestone','iron']


def empty_plan():
    return {'version':1,'revision':0,'ground':{},'props':[],'walls':[]}


@lru_cache(maxsize=1)
def catalogue():
    asset_root=ROOT/'frontend/public/assets/combat-terrain'
    ground={p.stem:{'name':p.stem.replace('_',' ').title(),'file':f'mega-terrain-tiles/{p.name}'}
            for p in sorted((asset_root/'mega-terrain-tiles').glob('*.png'))}
    for p in sorted((asset_root/'environment-ground-v1').glob('*.png')):
        ground[p.stem]={'name':p.stem.replace('_',' ').title(),'file':f'environment-ground-v1/{p.name}'}
    props=json.loads((ROOT/'frontend/src/map-prop-art.json').read_text())
    sizes=json.loads((ROOT/'frontend/src/map-prop-sizes.json').read_text())
    props={key:{'name':key.replace('structure:','').replace('_',' ').title(),'file':file,
                'footprint':sizes.get(key,{}).get('footprint',[1,1])}
           for key,file in props.items() if (file.startswith('props/') or any(s in key for s in ['cage','wagon','tent','stocks']))
           and (asset_root/file).is_file()}
    return {'ground':ground,'props':props,'wall_pieces':AVAILABLE_WALL_PIECES,'wall_shapes':['straight','corner','gate'],'wall_materials':MATERIALS}


def wall_segments(wall):
    if wall.get('piece') in WALL_PIECES:
        ax,ay=ANCHORS[wall['anchor']]
        return [tuple((wall['x']+px+ax-.5,wall['y']+py+ay-.5) for px,py in segment)
                for segment in WALL_PIECES[wall['piece']]['segments']]
    ax,ay=ANCHORS[wall['anchor']]
    center=(wall['x']+ax,wall['y']+ay)
    segments=[]
    for dx,dy in ARMS[wall['shape']]:
        for _ in range(wall['rotation']//90):dx,dy=-dy,dx
        segments.append((center,(center[0]+dx,center[1]+dy)))
    return segments


def validate_plan(plan, size, buildings=()):
    """Whitelist all asset IDs and numeric placement data; no client file paths."""
    cat=catalogue()
    if plan.get('version')!=1:raise ValueError('Unsupported construction format')
    result=empty_plan()
    ground=plan.get('ground',{});props=plan.get('props',[]);walls=plan.get('walls',[])
    if not isinstance(ground,dict) or not isinstance(props,list) or not isinstance(walls,list):
        raise ValueError('Invalid construction layers')
    if len(ground)>size['w']*size['h'] or len(props)>1000 or len(walls)>2000:
        raise ValueError('Construction layer is too large')

    def number(value,lo,hi,whole=False):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError('Invalid placement number')
        if not lo<=value<=hi or (whole and int(value)!=value):raise ValueError('Placement is outside the camp or allowed range')
        return int(value) if whole else round(value,4)

    def rotation(item):
        value=number(item.get('rotation',0),0,270,True)
        if value%90:raise ValueError('Rotation must be a quarter turn')
        return value

    for key,tile in ground.items():
        try:x,y=map(int,key.split(','))
        except (ValueError,AttributeError):raise ValueError('Invalid ground cell')
        number(x,0,size['w']-1,True);number(y,0,size['h']-1,True)
        if key!=f'{x},{y}' or tile.get('asset') not in cat['ground']:raise ValueError('Unknown ground tile')
        result['ground'][key]={'asset':tile['asset'],'rotation':rotation(tile)}
    identifiers=set()
    for layer in ['props','walls']:
        for item in plan.get(layer,[]):
            ident=item.get('id')
            if not isinstance(ident,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',ident) or ident in identifiers:raise ValueError('Construction objects need unique IDs')
            identifiers.add(ident)
            x=number(item.get('x'),0,size['w']-1,True);y=number(item.get('y'),0,size['h']-1,True)
            obj={'id':ident,'x':x,'y':y,'rotation':rotation(item)}
            if layer=='props':
                if item.get('asset') not in cat['props']:raise ValueError('Unknown prop')
                w=number(item.get('w',1),1,4,True);h=number(item.get('h',1),1,4,True)
                if x+w>size['w'] or y+h>size['h']:raise ValueError('Prop footprint extends outside the camp')
                obj.update(asset=item['asset'],w=w,h=h,
                           offset_x=number(item.get('offset_x',0),-.45,.45),offset_y=number(item.get('offset_y',0),-.45,.45),
                           blocking=bool(item.get('blocking',False)))
                if obj['blocking']:
                    from .content import BUILDINGS
                    for b in buildings:
                        d=BUILDINGS[b['type']]
                        if x<b['x']+d['w'] and x+w>b['x'] and y<b['y']+d['h'] and y+h>b['y']:
                            raise ValueError('A blocking prop overlaps a facility')
            else:
                if item.get('piece') is not None and item['piece'] not in WALL_PIECES:
                    raise ValueError('Unknown directional wall asset')
                if item.get('piece') and obj['rotation'] != 0:
                    raise ValueError('Directional walls use their native facing, not image rotation')
                if item.get('anchor') not in ANCHORS or item.get('shape') not in ARMS or item.get('material') not in MATERIALS:
                    raise ValueError('Unknown wall piece, position or material')
                if item.get('posts','auto') not in ['auto','none','both']:raise ValueError('Unknown end-post setting')
                obj.update(anchor=item['anchor'],shape=item['shape'],material=item['material'],posts=item.get('posts','auto'),
                           broken=bool(item.get('broken',False)),open=bool(item.get('open',False)))
                if item.get('piece'):
                    obj.update(piece=item['piece'],shape=WALL_PIECES[item['piece']]['shape'],posts='none')
                for start,end in wall_segments(obj):
                    for px,py in [start,end]:
                        if not 0<=px<=size['w'] or not 0<=py<=size['h']:raise ValueError('Wall extends outside the camp; rotate it or move its anchor')
            result[layer].append(obj)
    return result


def blocked_prop_overlap(state,x,y,w,h):
    return any(p.get('blocking') and x<p['x']+p['w'] and x+w>p['x'] and y<p['y']+p['h'] and y+h>p['y']
               for p in state.get('construction',{}).get('props',[]))
