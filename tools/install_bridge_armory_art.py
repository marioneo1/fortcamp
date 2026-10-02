"""Extract separate 4x3 full-bleed terrain and 4x2 transparent prop packs."""
import json
from pathlib import Path
from PIL import Image
from audit_catalogue_crops import components, recovered_icon

ROOT=Path(__file__).resolve().parents[1]
TILES=['wood_bridge','wood_bridge_damaged','wood_bridge_top','wood_bridge_bottom',
       'stone_bridge','stone_bridge_damaged','stone_bridge_top','stone_bridge_bottom',
       'chapel_moss','chapel_cracked','toll_cobbles','smithy_cobbles']
PROPS=['weapon_rack','shield_rack','armor_stand','arrow_crate','chapel_altar','chapel_pew','fallen_church_bell','toll_desk']

def main():
    source=ROOT/'staging-terrain/bridge-terrain-v1'
    image=Image.open(source/'bridge_terrain_12.png').convert('RGB')
    dest=ROOT/'frontend/public/assets/combat-terrain/bridge-v1';dest.mkdir(parents=True,exist_ok=True)
    for index,ident in enumerate(TILES):
        col,row=index%4,index//4
        box=(round(col*image.width/4),round(row*image.height/3),round((col+1)*image.width/4),round((row+1)*image.height/3))
        image.crop(box).resize((256,256),Image.Resampling.LANCZOS).save(dest/f'{ident}.png')
    source=ROOT/'staging-terrain/armory-props-v1'
    image=Image.open(source/'armory_props_8.png').convert('RGBA')
    parts,labels=components(image);groups=[[] for _ in PROPS]
    for part in parts:
        if part['area']<20:continue
        x,y=part['center'];groups[min(1,int(y*2/image.height))*4+min(3,int(x*4/image.width))].append(part)
    dest=ROOT/'frontend/public/assets/combat-terrain/props/armory-v1';dest.mkdir(parents=True,exist_ok=True)
    registry_path=ROOT/'frontend/src/map-prop-art.json'
    registry=json.loads(registry_path.read_text());report=[]
    for ident,group in zip(PROPS,groups):
        if not group:raise ValueError(f'Empty sprite: {ident}')
        anchor=max(group,key=lambda p:p['area']).copy()
        anchor['box']=[min(p['box'][0] for p in group),min(p['box'][1] for p in group),max(p['box'][2] for p in group),max(p['box'][3] for p in group)]
        owned={p['label'] for p in group}
        for index,label in enumerate(labels):
            if label in owned:labels[index]=anchor['label']
        recovered_icon(image,anchor,parts,labels,size=384,padding=32).save(dest/f'{ident}.png')
        registry[ident]=f'props/armory-v1/{ident}.png'
        report.append({'id':ident,'source_box':anchor['box']})
    registry_path.write_text(json.dumps(registry,indent=2)+'\n')
    (source/'extraction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Installed {len(TILES)} terrain tiles and {len(PROPS)} props in separate libraries')

if __name__=='__main__':main()
