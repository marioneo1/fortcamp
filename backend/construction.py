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
FURNITURE = json.loads((ROOT/'frontend/src/construction-furniture.json').read_text())
PROP_ART_BOUNDS = json.loads((ROOT/'frontend/src/construction-prop-bounds.json').read_text())
PROP_SIZING = json.loads((ROOT/'frontend/src/construction-prop-sizing.json').read_text())


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
                'footprint':PROP_SIZING.get(key,sizes.get(key,{})).get('footprint',[1,1]),
                'category':PROP_SIZING.get(key,{}).get('category','prop'),
                'fill':PROP_SIZING.get(key,{}).get('fill',.75)}
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


def prop_bounds(prop):
    art = PROP_ART_BOUNDS.get(prop.get('asset'))
    if not art:
        return (prop['x']+prop['w']*.04+prop.get('offset_x',0), prop['y']+prop['h']*.04+prop.get('offset_y',0),
                prop['x']+prop['w']*.96+prop.get('offset_x',0), prop['y']+prop['h']*.96+prop.get('offset_y',0))
    iw, ih = art['size']; l, t, r, b = art['bounds']
    w, h = (prop['h'], prop['w']) if prop['rotation'] % 180 else (prop['w'], prop['h'])
    fill = art.get('fill')
    scale = min(w*fill/(r-l),h*fill/(b-t)) if fill else min(w*.92/iw,h*.92/ih)
    mx,my = ((l+r)/2,(t+b)/2) if fill else (iw/2,ih/2)
    cx = prop['x']+prop['w']/2+prop.get('offset_x',0)
    cy = prop['y']+prop['h']/2+prop.get('offset_y',0)
    points = []
    for x, y in [(l,t),(r,t),(r,b),(l,b)]:
        dx, dy = (x-mx)*scale, (y-my)*scale
        for _ in range(prop['rotation']//90): dx, dy = -dy, dx
        points.append((cx+dx,cy+dy))
    return min(x for x,y in points), min(y for x,y in points), max(x for x,y in points), max(y for x,y in points)


def props_overlap(a,b):
    al,at,ar,ab=prop_bounds(a); bl,bt,br,bb=prop_bounds(b)
    width=min(ar,br)-max(al,bl); height=min(ab,bb)-max(at,bt)
    if width<=1e-7 or height<=1e-7: return False
    seat = a if a['asset'] in FURNITURE['seats'] and b['asset'] in FURNITURE['tables'] else b if b['asset'] in FURNITURE['seats'] and a['asset'] in FURNITURE['tables'] else None
    if seat:
        l,t,r,bottom=prop_bounds(seat)
        if width*height<=(r-l)*(bottom-t)*FURNITURE['tuck_fraction']+1e-7: return False
    return True


def wall_hits_prop(wall,prop):
    left,top,right,bottom=prop_bounds(prop)
    left-=.08;top-=.08;right+=.08;bottom+=.08
    return any((top<=a[1]<=bottom and max(a[0],b[0])>left and min(a[0],b[0])<right)
               if a[1]==b[1] else (left<=a[0]<=right and max(a[1],b[1])>top and min(a[1],b[1])<bottom)
               for a,b in wall_segments(wall))


def solid_wall(wall):
    return not wall.get('broken') and not (wall['shape']=='gate' and wall.get('open'))


def construction_cell_blocked(plan,x,y):
    if any(p.get('blocking') and p['x']<=x<p['x']+p['w'] and p['y']<=y<p['y']+p['h'] for p in plan.get('props',[])):
        return True
    return any((y<a[1]<y+1 and max(a[0],b[0])>x and min(a[0],b[0])<x+1)
               if a[1]==b[1] else (x<a[0]<x+1 and max(a[1],b[1])>y and min(a[1],b[1])<y+1)
               for w in plan.get('walls',[]) if solid_wall(w) for a,b in wall_segments(w))


def construction_step_allowed(plan,size,x,y,nx,ny):
    """Cardinal cell movement: edge walls block crossings, interior walls block cells."""
    if (abs(x-nx)+abs(y-ny)!=1 or not all(0<=v<size['w'] for v in (x,nx))
            or not all(0<=v<size['h'] for v in (y,ny))
            or construction_cell_blocked(plan,x,y) or construction_cell_blocked(plan,nx,ny)):
        return False
    return not any((a[0]==b[0] and min(x,nx)+.5<a[0]<max(x,nx)+.5 and min(a[1],b[1])<=y+.5<=max(a[1],b[1]))
                   if x!=nx else (a[1]==b[1] and min(y,ny)+.5<a[1]<max(y,ny)+.5 and min(a[0],b[0])<=x+.5<=max(a[0],b[0]))
                   for w in plan.get('walls',[]) if solid_wall(w) for a,b in wall_segments(w))


def validate_plan(plan, size, buildings=(), previous_plan=None):
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
                           offset_x=number(item.get('offset_x',0),-.5,.5),offset_y=number(item.get('offset_y',0),-.5,.5),
                           blocking=bool(item.get('blocking',False)))
                if 'table_spacing' in item:
                    if item['asset'] not in FURNITURE['seats']:raise ValueError('Table spacing is only available for seating')
                    obj['table_spacing']=number(item['table_spacing'],FURNITURE['min_spacing'],FURNITURE['max_spacing'])
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
    # Preserve untouched old overlaps, but never allow new ones or moved conflicts.
    previous={obj['id']:obj for layer in ('props','walls') for obj in (previous_plan or {}).get(layer,[])}
    def unchanged(a,b):
        return previous.get(a['id'])==a and previous.get(b['id'])==b
    # Sweep visible boxes so distant props do not require collision checks.
    ordered=sorted([(prop_bounds(p),p) for p in result['props']],key=lambda row:row[0][0])
    for index,(bounds,prop) in enumerate(ordered):
        for other_bounds,other in ordered[index+1:]:
            if other_bounds[0]>=bounds[2]: break
            if props_overlap(prop,other) and not unchanged(prop,other):
                raise ValueError('Those props overlap. Adjust their positions; seats can tuck slightly under a table.')
    # Index half-cell edge spans once: no quadratic wall-pair scan on large camps.
    occupied={}
    for wall in result['walls']:
        segments=wall_segments(wall)
        for a,b in segments:
            count=max(1,round(max(abs(a[0]-b[0]),abs(a[1]-b[1]))*2))
            for step in range(count):
                start=tuple(a[k]+(b[k]-a[k])*step/count for k in range(2))
                end=tuple(a[k]+(b[k]-a[k])*(step+1)/count for k in range(2))
                key=tuple(sorted((start,end)))
                for other in occupied.get(key,[]):
                    if other['id']!=wall['id'] and not unchanged(wall,other):
                        raise ValueError('A wall already occupies that position. Connecting wall ends is allowed.')
                occupied.setdefault(key,[]).append(wall)
        for prop in result['props']:
            if wall_hits_prop(wall,prop) and not unchanged(wall,prop):
                raise ValueError('A prop overlaps a wall. Adjust its position or choose another cell.')
    return result


def blocked_prop_overlap(state,x,y,w,h):
    return any(p.get('blocking') and x<p['x']+p['w'] and x+w>p['x'] and y<p['y']+p['h'] and y+h>p['y']
               for p in state.get('construction',{}).get('props',[]))
