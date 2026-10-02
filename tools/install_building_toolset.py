"""Recover whole architectural silhouettes; calibrate joins and paired door anchors."""
import json
from pathlib import Path
from PIL import Image, ImageChops
from audit_catalogue_crops import components

ROOT=Path(__file__).resolve().parents[1]
FAMILIES=['timber','fieldstone','limestone','iron']
PARTS=['wall','corner','junction','end','breach','door_closed','door_open','gate_closed','gate_open','stairs']
SOURCE=ROOT/'staging-terrain/building-toolset-v1'

def groups(image,cols,rows):
    parts,labels=components(image)
    cells=[[] for _ in range(cols*rows)]
    for part in parts:
        if part['area']<40:continue
        x,y=part['center'];cells[min(rows-1,int(y*rows/image.height))*cols+min(cols-1,int(x*cols/image.width))].append(part)
    result=[]
    for group in cells:
        if not group:raise ValueError('Empty atlas cell')
        owned={p['label'] for p in group}
        box=(min(p['box'][0] for p in group),min(p['box'][1] for p in group),
             max(p['box'][2] for p in group),max(p['box'][3] for p in group))
        mask=Image.frombytes('L',image.size,bytes(255 if label in owned else 0 for label in labels))
        cut=image.copy();cut.putalpha(ImageChops.multiply(image.getchannel('A'),mask))
        result.append((cut.crop(box),box))
    return result

def centered(image,scale=None,anchor_y=None):
    scale=scale or 320/max(image.size)
    canvas=Image.new('RGBA',(384,384))
    resized=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
    anchor_y=image.height/2 if anchor_y is None else anchor_y
    position=(round(192-image.width*scale/2),round(192-anchor_y*scale))
    if position[0]<0 or position[1]<0 or position[0]+resized.width>384 or position[1]+resized.height>384:
        raise ValueError('Normalization would cut a silhouette')
    canvas.alpha_composite(resized,position)
    return canvas

def main():
    # Prefer the complete material packs; this old entry point must not revert
    # the active registry to the earlier mixed-material draft.
    if all((ROOT/'staging-terrain/building-toolset-v2'/f'{f}.png').exists() for f in FAMILIES):
        from install_material_building_toolsets import main as install_current
        return install_current()
    sprites={};report=[]
    for file,families in [('rustic_structures_20.png',FAMILIES[:2]),('civic_structures_20.png',FAMILIES[2:])]:
        image=Image.open(SOURCE/file).convert('RGBA')
        cells=groups(image,5,4)
        for index,(cut,box) in enumerate(cells):
            family=families[index//10];piece=PARTS[index%10]
            if piece in {'door_closed','door_open','gate_closed','gate_open'}:continue # frontal draft replaced below
            sprites[f'{family}_{piece}']=centered(cut)
            report.append({'id':f'{family}_{piece}','source':file,'source_box':box})
    image=Image.open(SOURCE/'overhead_doors_gates_16.png').convert('RGBA');cells=groups(image,4,4)
    for row,family in enumerate(FAMILIES):
        for pair,name in [(0,'door'),(2,'gate')]:
            closed,opened=cells[row*4+pair],cells[row*4+pair+1]
            scale=320/max(closed[0].width,opened[0].width)
            # Share post height and scale between closed/open art: opening never jumps its anchor.
            anchor=closed[0].height/2
            max_below=max(closed[0].height-anchor,opened[0].height-anchor)
            scale=min(scale,175/max(anchor,max_below))
            for state,(cut,box) in [('closed',closed),('open',opened)]:
                ident=f'{family}_{name}_{state}';sprites[ident]=centered(cut,scale,anchor)
                report.append({'id':ident,'source':'overhead_doors_gates_16.png','source_box':box,'anchor_y':anchor})
    dest=ROOT/'frontend/public/assets/combat-terrain/structures/building-v1';dest.mkdir(parents=True,exist_ok=True)
    registry_path=ROOT/'frontend/src/map-prop-art.json';registry=json.loads(registry_path.read_text())
    geometry={}
    for ident,sprite in sprites.items():
        sprite.save(dest/f'{ident}.png',optimize=True);registry['structure:'+ident]=f'structures/building-v1/{ident}.png'
    for family in FAMILIES:
        alpha=sprites[family+'_corner'].getchannel('A')
        # Sample the unconnected ends of the two corner arms, not the middle junction.
        horizontal=[y for y in range(192) for x in range(32,145) if alpha.getpixel((x,y))>100]
        vertical=[x for x in range(192,384) for y in range(220,345) if alpha.getpixel((x,y))>100]
        if not horizontal or not vertical:raise ValueError(f'{family}: missing corner arms')
        cy=sum(horizontal)/len(horizontal)/384;cx=sum(vertical)/len(vertical)/384
        geometry[family]={'join_offset':round(((cx-.5)+(.5-cy))/2*1.25,4)}
    # Keep existing saved sprite identifiers usable, backed by matching families.
    aliases={'shed_wall_straight':'timber_wall','shed_wall_corner':'timber_corner','shed_wall_broken':'timber_breach',
             'shed_door_closed':'timber_door_closed','shed_door_open':'timber_door_open',
             'stone_wall_straight':'fieldstone_wall','cemetery_wall_corner':'fieldstone_corner',
             'yard_gate_closed':'fieldstone_gate_closed','yard_gate_open':'fieldstone_gate_open'}
    for old,new in aliases.items():registry['structure:'+old]=registry['structure:'+new]
    registry_path.write_text(json.dumps(registry,indent=2)+'\n')
    (ROOT/'backend/building_art_geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    (SOURCE/'extraction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Installed {len(sprites)} structure parts and matching overhead door/gate pairs; geometry: {geometry}')

if __name__=='__main__':main()
