"""Install one complete, consistently styled building atlas per material.

Recover entire alpha components, then fit without distorting their silhouettes.
Keep source crops and old runtime libraries; stable IDs select each family's active pack.
"""
import json
from PIL import Image
from install_building_toolset import ROOT, groups, centered, FAMILIES

SOURCE=ROOT/'staging-terrain/building-toolset-v2'
PARTS=['wall','corner','junction','cross','end','breach','door_closed','door_open',
       'gate_closed','gate_open','window','pillar','stairs','corner_broken','edge_junction','brace']


def main():
    registry_path=ROOT/'frontend/src/map-prop-art.json'
    registry=json.loads(registry_path.read_text())
    dest=ROOT/'frontend/public/assets/combat-terrain/structures/building-v2'
    dest.mkdir(parents=True,exist_ok=True)
    report=[];geometry={}
    for family in FAMILIES:
        source=ROOT/'staging-terrain/building-toolset-v3'/f'{family}.png'
        version='building-v3' if source.exists() else 'building-v2'
        if not source.exists():source=SOURCE/f'{family}.png'
        dest=ROOT/f'frontend/public/assets/combat-terrain/structures/{version}'
        dest.mkdir(parents=True,exist_ok=True)
        cells=groups(Image.open(source).convert('RGBA'),4,4)
        common_scale=320/cells[0][0].width
        sprites={piece:centered(cut,min(common_scale,350/max(cut.size))
                 if version=='building-v3' or piece in {'end','pillar','stairs','brace'} else None)
                 for piece,(cut,_) in zip(PARTS,cells)}
        # Door/gate pairs share a scale and the fixed post centerline. Opening
        # may add a downward leaf, but must never shrink or move the posts.
        for prefix in ('door','gate'):
            closed=cells[PARTS.index(prefix+'_closed')][0]
            opened=cells[PARTS.index(prefix+'_open')][0]
            scale=320/max(closed.width,opened.width)
            anchor=closed.height/2
            scale=min(scale,175/max(anchor,closed.height-anchor,opened.height-anchor))
            sprites[prefix+'_closed']=centered(closed,scale,anchor)
            sprites[prefix+'_open']=centered(opened,scale,anchor)
        alpha=sprites['corner'].getchannel('A')
        horizontal=[y for y in range(192) for x in range(32,145) if alpha.getpixel((x,y))>100]
        vertical=[x for x in range(192,384) for y in range(220,345) if alpha.getpixel((x,y))>100]
        if not horizontal or not vertical:raise ValueError(f'{family}: incomplete corner')
        cy=sum(horizontal)/len(horizontal)/384;cx=sum(vertical)/len(vertical)/384
        geometry[family]={'join_offset':round(((cx-.5)+(.5-cy))/2*1.25,4)}
        # The generated corner arms need independent alignment, not one averaged
        # shift. Preserve aspect ratio; the renderer sleeves any short ends.
        geometry[family]['corner_offset']=[round(geometry[family]['join_offset']-(cx-.5)*1.25,4),
            round(-geometry[family]['join_offset']-(cy-.5)*1.25,4)]
        # Rubble enlarges a breach's lower bounds. Align its surviving beam,
        # measured at the two ends, rather than its whole silhouette's center.
        breach=sprites['breach'].getchannel('A')
        ends=[y for x in list(range(40,95))+list(range(290,340)) for y in range(384) if breach.getpixel((x,y))>100]
        if not ends:raise ValueError(f'{family}: missing surviving breach ends')
        geometry[family]['breach_offset']=[0,round((.5-sum(ends)/len(ends)/384)*1.25,4)]
        junction=sprites['edge_junction'].getchannel('A')
        top=[y for y in range(192) for x in range(32,145) if junction.getpixel((x,y))>100]
        stem=[x for x in range(96,288) for y in range(240,345) if junction.getpixel((x,y))>100]
        if not top or not stem:raise ValueError(f'{family}: incomplete T junction')
        geometry[family]['junction_offset']=[round((.5-sum(stem)/len(stem)/384)*1.25,4),
            round(-geometry[family]['join_offset']-(sum(top)/len(top)/384-.5)*1.25,4)]
        for piece,sprite in sprites.items():
            ident=f'{family}_{piece}'
            sprite.save(dest/f'{ident}.png',optimize=True)
            registry['structure:'+ident]=f'structures/{version}/{ident}.png'
            report.append({'id':ident,'source':str(source.relative_to(ROOT)).replace('\\','/'),'source_box':cells[PARTS.index(piece)][1]})
    aliases={'shed_wall_straight':'timber_wall','shed_wall_corner':'timber_corner','shed_wall_broken':'timber_breach',
             'shed_door_closed':'timber_door_closed','shed_door_open':'timber_door_open',
             'stone_wall_straight':'fieldstone_wall','cemetery_wall_corner':'fieldstone_corner',
             'yard_gate_closed':'fieldstone_gate_closed','yard_gate_open':'fieldstone_gate_open'}
    for old,new in aliases.items():registry['structure:'+old]=registry['structure:'+new]
    registry_path.write_text(json.dumps(registry,indent=2)+'\n')
    (ROOT/'backend/building_art_geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    (ROOT/'frontend/src/building-art-geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    (SOURCE/'extraction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Installed {len(report)} material-specific building parts; geometry: {geometry}')


if __name__=='__main__':main()
