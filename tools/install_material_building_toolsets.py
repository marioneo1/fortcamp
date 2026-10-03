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
        source=ROOT/'staging-terrain/building-toolset-v4'/f'{family}.png'
        version='building-v4'
        if not source.exists():
            source=ROOT/'staging-terrain/building-toolset-v3'/f'{family}.png'
            version='building-v3' if source.exists() else 'building-v2'
        if not source.exists():source=SOURCE/f'{family}.png'
        dest=ROOT/f'frontend/public/assets/combat-terrain/structures/{version}'
        dest.mkdir(parents=True,exist_ok=True)
        cells=groups(Image.open(source).convert('RGBA'),4,4)
        common_scale=320/cells[0][0].width
        sprites={piece:centered(cut,min(common_scale,350/max(cut.size))
                 if version in {'building-v3','building-v4'} or piece in {'end','pillar','stairs','brace'} else None)
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
        wall_bounds=sprites['wall'].getchannel('A').getbbox()
        geometry[family]['wall_half_thickness']=round((wall_bounds[3]-wall_bounds[1])/384*1.25/2,4)
        if version=='building-v4':
            pillar_bounds=sprites['pillar'].getchannel('A').getbbox()
            geometry[family]['cap_mode']='pillar'
            geometry[family]['cap_scale']=round((wall_bounds[3]-wall_bounds[1])/(pillar_bounds[2]-pillar_bounds[0])*1.25*1.08,4)
        elif family=='iron':
            geometry[family]['cap_mode']='trim'
        # The generated corner arms need independent alignment, not one averaged
        # shift. Preserve aspect ratio; the renderer sleeves any short ends.
        geometry[family]['corner_offset']=[round(geometry[family]['join_offset']-(cx-.5)*1.25,4),
            round(-geometry[family]['join_offset']-(cy-.5)*1.25,4)]
        broken=sprites['corner_broken'].getchannel('A')
        rows=[y for x in range(40,110) for y in range(192) if broken.getpixel((x,y))>100]
        columns=[x for y in range(260,335) for x in range(192,384) if broken.getpixel((x,y))>100]
        if not rows or not columns:raise ValueError(f'{family}: missing damaged corner arms')
        geometry[family]['broken_corner_offset']=[
            round(geometry[family]['join_offset']-(sum(columns)/len(columns)/384-.5)*1.25,4),
            round(-geometry[family]['join_offset']-(sum(rows)/len(rows)/384-.5)*1.25,4)]
        end_bounds=sprites['end'].getchannel('A').getbbox()
        geometry[family]['end_offset']=[round(.5-(end_bounds[2]/384-.5)*1.25,4),0]
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
        if version=='building-v4' and family in ('fieldstone','limestone'):
            native=sprites['junction'].getchannel('A')
            bar=[y for y in range(384) if sum(native.getpixel((x,y))>96 for x in range(384))>384*.65]
            if not bar:raise ValueError(f'{family}: incomplete native T bar')
            geometry[family]['native_junction_offset']=[0,round((.5-(min(bar)+max(bar))/2/384)*1.25,4)]
            geometry[family]['native_junction_rotations']=[90]
        for piece,sprite in sprites.items():
            ident=f'{family}_{piece}'
            sprite.save(dest/f'{ident}.png',optimize=True)
            registry['structure:'+ident]=f'structures/{version}/{ident}.png'
            report.append({'id':ident,'source':str(source.relative_to(ROOT)).replace('\\','/'),'source_box':cells[PARTS.index(piece)][1]})
        # Optional user-authored directional corners are kept separately from
        # generated atlas crops. Reinstalling a kit must not erase their anchors.
        directions=['north_east','north_west','south_east','south_west']
        if all((dest/f'{family}_wall_{direction}.png').exists() for direction in directions):
            calibrated={}
            for direction in directions:
                file=dest/f'{family}_wall_{direction}.png'
                alpha=Image.open(file).convert('RGBA').getchannel('A');w,h=alpha.size
                xs=range(int(w*.15),int(w*.35)) if direction.endswith('east') else range(int(w*.65),int(w*.85))
                ys=range(int(h*.65),int(h*.8)) if direction.startswith('north') else range(int(h*.2),int(h*.35))
                rows=[y for y in range(h) if sum(alpha.getpixel((x,y))>96 for x in xs)>len(xs)*.8]
                columns=[x for x in range(w) if sum(alpha.getpixel((x,y))>96 for y in ys)>len(ys)*.8]
                if not rows or not columns:raise ValueError(f'{file.name}: missing connecting wall arms')
                cx=(min(columns)+max(columns))/2/w;cy=(min(rows)+max(rows))/2/h;o=geometry[family]['join_offset']
                calibrated[direction]={'offset':[round((o if direction.endswith('east') else -o)-(cx-.5)*1.25,4),
                    round((-o if direction.startswith('north') else o)-(cy-.5)*1.25,4)]}
                registry[f'structure:{family}_wall_{direction}']=f'structures/{version}/{file.name}'
            geometry[family]['directional_corners']=calibrated
            if family=='limestone':
                geometry[family]['perimeter_face']='outward'
                geometry[family]['corner_overlap']=.035
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
