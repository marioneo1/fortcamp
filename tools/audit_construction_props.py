"""Audit installed construction sizes and generate a scale/placement-box gallery."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from backend.construction import catalogue, prop_bounds

ROOT=Path(__file__).resolve().parents[1]

def main():
    cat=catalogue()['props']
    art=json.loads((ROOT/'frontend/src/construction-prop-bounds.json').read_text())
    records=[]
    folder=ROOT/'staging-terrain/construction-prop-audit'
    folder.mkdir(parents=True,exist_ok=True)
    lines=['# Construction prop size audit','',f'{len(cat)} installed construction props checked. All dimensions below are cells, not PNG pixels.',
           'Placement bounds use visible alpha, calibrated scale, rotation and offsets. They do not change character movement or combat footprints.',
           'Older saved coordinates/footprints are retained. Use Standard size on a selected prop to adopt its new default footprint.',
           '', '| Prop | Default footprint | Visible placement box | Category |', '|---|---|---|---|']
    tile=40;cardw=240;cardh=210;per_page=24
    pages=[]
    for index,(key,profile) in enumerate(cat.items()):
        if index%per_page==0:
            sheet=Image.new('RGB',(cardw*6,cardh*4),'#253328');draw=ImageDraw.Draw(sheet);pages.append(sheet)
        n=index%per_page;ox=n%6*cardw;oy=n//6*cardh
        for x in range(5):
            for y in range(4):draw.rectangle((ox+20+x*tile,oy+8+y*tile,ox+20+(x+1)*tile,oy+8+(y+1)*tile),outline='#4a624c')
        w,h=profile['footprint'];p={'asset':key,'x':1,'y':0,'w':w,'h':h,'rotation':0}
        left,top,right,bottom=prop_bounds(p)
        visible=[round(right-left,4),round(bottom-top,4)]
        record={'id':key,'file':profile['file'],'footprint':[w,h],'visible_cells':visible,'category':profile['category'],'fill':profile['fill'],'bounds':art[key]['bounds'],'canvas':art[key]['size']}
        records.append(record)
        lines.append(f"| {key} | {w}x{h} | {visible[0]:.2f}x{visible[1]:.2f} | {profile['category']} |")
        with Image.open(ROOT/'frontend/public/assets/combat-terrain'/profile['file']) as source:
            # Alpha bounds crop here is only for the gallery, never the source.
            sprite=source.convert('RGBA').crop(art[key]['bounds'])
            sprite=sprite.resize((max(1,round(visible[0]*tile)),max(1,round(visible[1]*tile))),Image.Resampling.LANCZOS)
            px=ox+20+round(left*tile);py=oy+8+round(top*tile)
            sheet.paste(sprite,(px,py),sprite)
            draw.rectangle((ox+20+left*tile,oy+8+top*tile,ox+20+right*tile,oy+8+bottom*tile),outline='#8aefc8',width=1)
        draw.text((ox+8,oy+172),key,fill='white')
        draw.text((ox+8,oy+189),f'{w}x{h} / visible {visible[0]:.2f}x{visible[1]:.2f}',fill='#a6d2b4')
    for i,page in enumerate(pages):page.save(folder/f'gallery-{i+1:02}.jpg',quality=94)
    (folder/'audit.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    (ROOT/'docs/art/CONSTRUCTION_PROP_SIZE_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Audited {len(records)} props; wrote {len(pages)} scale/placement-box galleries.')

if __name__=='__main__':main()
