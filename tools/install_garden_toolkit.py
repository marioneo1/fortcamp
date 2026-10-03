"""Install the new overhead 6x4 garden prop kit, retaining complete silhouettes.

Run .venv/Scripts/python.exe tools/install_garden_toolkit.py from dev.
Disconnected pieces belong to their nearest atlas cell. No older kit is replaced.
"""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from audit_catalogue_crops import components

ROOT=Path(__file__).resolve().parents[1]
IDS=['fence_full','fence_half','fence_corner','fence_junction','fence_cross','fence_post',
     'gate_closed','gate_open','fence_damaged','scarecrow','hand_pump','round_stool',
     'round_table','potting_bench','watering_can','wheelbarrow','tool_crate','soil_sack',
     'clay_pots','seedling_tray','herb_basket','compost_bin','drying_screen','hose_coil']

def main():
    folder=ROOT/'staging-terrain/garden-toolkit-v2'
    image=Image.open(folder/'garden_toolkit_24.png').convert('RGBA')
    parts,labels=components(image)
    groups={i:[] for i in range(24)}
    for part in parts:
        if part['area']<30:continue
        x,y=part['center'];col=min(5,int(x/image.width*6));row=min(3,int(y/image.height*4))
        groups[row*6+col].append(part)
    out=ROOT/'frontend/public/assets/combat-terrain/props/garden-toolkit-v2';out.mkdir(parents=True,exist_ok=True)
    registry_path=ROOT/'frontend/src/map-prop-art.json';registry=json.loads(registry_path.read_text())
    gallery=Image.new('RGB',(6*192,4*216),'#25302a');draw=ImageDraw.Draw(gallery)
    records=[]
    for index,name in enumerate(IDS):
        group=groups[index]
        if not group:raise ValueError(f'Empty atlas slot: {name}')
        bounds=[min(p['box'][0] for p in group),min(p['box'][1] for p in group),
                max(p['box'][2] for p in group),max(p['box'][3] for p in group)]
        l,t,r,b=bounds
        if min(l,t,image.width-r,image.height-b)<3:raise ValueError(f'{name}: source edge crop')
        owned={p['label'] for p in group}
        # Silhouette ownership removes neighboring art while keeping disconnected
        # pots, an open gate's hinge post and all tools from this same atlas slot.
        box=(max(0,l-4),max(0,t-4),min(image.width,r+4),min(image.height,b+4))
        mask=Image.new('L',(box[2]-box[0],box[3]-box[1]))
        mask.putdata([255 if labels[y*image.width+x] in owned else 0 for y in range(box[1],box[3]) for x in range(box[0],box[2])])
        mask=mask.filter(ImageFilter.MaxFilter(7))
        cut=image.crop(box);alpha=cut.getchannel('A')
        alpha.frombytes(bytes(v if keep else 0 for v,keep in zip(alpha.tobytes(),mask.tobytes())));cut.putalpha(alpha)
        canvas=(384,192) if name in {'potting_bench','wheelbarrow','drying_screen'} else (384,384)
        cut=cut.crop(cut.getbbox());cut.thumbnail((canvas[0]-40,canvas[1]-40),Image.Resampling.LANCZOS)
        icon=Image.new('RGBA',canvas);icon.alpha_composite(cut,((canvas[0]-cut.width)//2,(canvas[1]-cut.height)//2))
        ident='horticulture_'+name;icon.save(out/f'{ident}.png',optimize=True)
        registry[ident]=f'props/garden-toolkit-v2/{ident}.png'
        preview=icon.copy();preview.thumbnail((192,192),Image.Resampling.LANCZOS)
        x,y=index%6*192,index//6*216;gallery.paste(preview,(x+(192-preview.width)//2,y+(192-preview.height)//2),preview);draw.text((x+3,y+195),name,fill='white')
        records.append({'id':ident,'slot':index,'source_box':bounds,'parts':len(group),'canvas':list(canvas)})
    # A connected edging rail omits terminal posts. Keep the complete original
    # full rail above; this middle section is a separate reusable mating part.
    l,t,r,b=records[0]['source_box'];w,h=r-l,b-t
    rail=image.crop((round(l+w*.18),round(t+h*.35),round(r-w*.18),round(t+h*.7)))
    rail=rail.resize((384,38),Image.Resampling.LANCZOS)
    module=Image.new('RGBA',(384,384));module.alpha_composite(rail,(0,173))
    ident='horticulture_fence_joined';module.save(out/f'{ident}.png',optimize=True)
    registry[ident]=f'props/garden-toolkit-v2/{ident}.png'
    registry_path.write_text(json.dumps(registry,indent=2)+'\n')
    (folder/'extraction.json').write_text(json.dumps(records,indent=2)+'\n');gallery.save(folder/'extracted-gallery.jpg',quality=94)
    print('Installed 24 complete overhead props and one connected edging rail.')

if __name__=='__main__':main()
