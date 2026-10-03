"""Install only the complete v10 polished-stone atlas; other families are untouched."""
import json
from PIL import Image
from install_building_toolset import ROOT, groups, centered
from install_material_building_toolsets import PARTS

def mean(values):
    if not values:raise ValueError('Missing masonry connection')
    return sum(values)/len(values)

def row_anchor(sprite):
    a=sprite.getchannel('A')
    return mean([y for x in list(range(45,100))+list(range(285,335))
                 for y in range(384) if a.getpixel((x,y))>120])

def fit_stem(sprite, center_x, start_y, end_y):
    """Fit only the longitudinal arm; keep its width and the authored joint."""
    a=sprite.getchannel('A')
    left=max(0,round(center_x-42));right=min(384,round(center_x+42))
    section=sprite.crop((left,start_y,right,384))
    bounds=section.getchannel('A').getbbox()
    if not bounds:raise ValueError('Missing connecting stem')
    length=bounds[3]
    sprite.paste((0,0,0,0),(left,start_y,right,384))
    sprite.alpha_composite(section.crop((0,0,right-left,length)).resize(
        (right-left,max(1,end_y-start_y)),Image.Resampling.LANCZOS),(left,start_y))

def main():
    source=ROOT/'staging-terrain/building-toolset-v10-polished'
    cells=groups(Image.open(source/'limestone.png').convert('RGBA'),4,4)
    scale=320/cells[0][0].width
    sprites={name:centered(cut,scale) for name,(cut,_) in zip(PARTS,cells)}
    # User-authored replacements remain separate from the original atlas.
    overrides={}
    for filename,parts in [('part_17.png',['junction','edge_junction']),('part_18.png',['corner'])]:
        path=source/filename
        if path.exists():
            cut=Image.open(path).convert('RGBA')
            bounds=cut.getchannel('A').getbbox()
            if not bounds:raise ValueError(f'{filename}: empty replacement')
            for part in parts:
                sprites[part]=centered(cut.crop(bounds),scale)
                overrides[part]=filename
    # State pairs share both scale and the fixed jamb band anchor, not their
    # complete silhouette height (the open leaf is deliberately below it).
    for prefix in ['door','gate']:
        pair=[cells[PARTS.index(prefix+'_'+state)][0] for state in ['closed','open']]
        anchors=[]
        for cut in pair:
            a=cut.getchannel('A');xs=list(range(min(35,cut.width//7)))+list(range(cut.width-min(35,cut.width//7),cut.width))
            anchors.append(mean([y for x in xs for y in range(cut.height) if a.getpixel((x,y))>120]))
        for state,cut,anchor in zip(['closed','open'],pair,anchors):
            sprites[prefix+'_'+state]=centered(cut,scale,anchor)
    alpha=sprites['corner'].getchannel('A')
    cy=mean([y for x in range(45,115) for y in range(192) if alpha.getpixel((x,y))>120])
    cx=mean([x for y in range(250,325) for x in range(192,384) if alpha.getpixel((x,y))>120])
    # Keep existing wall/door boundary seating when swapping a corner.
    old=json.loads((ROOT/'backend/building_art_geometry.json').read_text())['limestone']
    o=old['join_offset'] if overrides else round(((cx-192)+(192-cy))/384*1.25/2,4)
    offset=lambda x,y:[round(x,4),round(y,4)]
    profile={'join_offset':o,'authored_junctions':True,
             'wall_half_thickness':round((sprites['wall'].getchannel('A').getbbox()[3]-sprites['wall'].getchannel('A').getbbox()[1])/384*1.25/2,4),
             'corner_offset':offset(o-(cx/384-.5)*1.25,-o-(cy/384-.5)*1.25),
             'junction_offset':[0,0]}
    for part in ['junction','cross','edge_junction','window','breach','corner_broken']:
        if part=='cross':anchor=192
        elif part=='corner_broken':
            a=sprites[part].getchannel('A')
            by=mean([y for x in range(80,160) for y in range(192) if a.getpixel((x,y))>120])
            bx=mean([x for y in range(260,325) for x in range(192,384) if a.getpixel((x,y))>120])
            profile['broken_corner_offset']=offset(o-(bx/384-.5)*1.25,-o-(by/384-.5)*1.25)
            continue
        else:anchor=row_anchor(sprites[part])
        stem_x=192
        if part in ['junction','edge_junction']:
            a=sprites[part].getchannel('A')
            stem_x=mean([x for y in range(220,300) for x in range(110,275) if a.getpixel((x,y))>120])
        profile['authored_'+part+'_offset']=offset((192-stem_x)/384*1.25,(.5-anchor/384)*1.25-(o if part=='edge_junction' else 0))
    # Generation varies arm lengths. Seat complete native joints at the measured
    # axes and fit only the straight stem beyond the joint to the next tile.
    for part,center,local,start in [
        ('corner',cx,profile['corner_offset'],180),
        ('edge_junction',192-profile['authored_edge_junction_offset'][0]*384/1.25,profile['authored_edge_junction_offset'],180),
        ('junction',192-profile['authored_junction_offset'][0]*384/1.25,profile['authored_junction_offset'],155)]:
        tip=round(192+(.52-local[1])*384/1.25)
        fit_stem(sprites[part],center,start,min(384,tip))
    dest=ROOT/'frontend/public/assets/combat-terrain/structures/building-v10-polished';dest.mkdir(exist_ok=True)
    path=ROOT/'frontend/src/map-prop-art.json';registry=json.loads(path.read_text())
    for part,sprite in sprites.items():
        filename='limestone_'+part+'.png';sprite.save(dest/filename,optimize=True)
        registry['structure:limestone_'+part]='structures/building-v10-polished/'+filename
    for suffix in ['north_east','north_west','south_east','south_west']:
        registry.pop('structure:limestone_wall_'+suffix,None)
    path.write_text(json.dumps(registry,indent=2)+'\n')
    for file in ['backend/building_art_geometry.json','frontend/src/building-art-geometry.json']:
        path=ROOT/file;data=json.loads(path.read_text());data['limestone']=profile
        path.write_text(json.dumps(data,indent=2)+'\n')
    (source/'installed.json').write_text(json.dumps({'scale':scale,'geometry':profile,'overrides':overrides,
        'parts':[{'piece':part,'source_box':box} for part,(_,box) in zip(PARTS,cells)]},indent=2)+'\n')
    print('Installed the 16-piece polished kit only, including paired native door/gate art.')

if __name__=='__main__':main()
