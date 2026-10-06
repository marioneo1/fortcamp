"""Import an equal 4x4 Rogue atlas. Usage: python tools/import_rogue_atlas.py atlas.png."""
from pathlib import Path
import argparse
import json
import shutil
from PIL import Image

NAMES = ('cheap_shot','crippling_cut','exploit_weakness','shadowstep','caltrops','backflip','trap_expert','throwing_knife','knife','knife_trail','shadow_depart','shadow_arrive','caltrop_tile','cut_contact','afterimage','landing_dust')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('atlas',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    source=Image.open(args.atlas).convert('RGB')
    destination=root/'frontend/public/assets/rogue-v1'
    staging=root/'staging-ui/rogue-v1'
    destination.mkdir(parents=True,exist_ok=True);staging.mkdir(parents=True,exist_ok=True)
    if args.atlas.resolve() != (staging/'atlas.png').resolve():
        shutil.copy2(args.atlas,staging/'atlas.png')
    records=[]
    for index,name in enumerate(NAMES):
        row,column=divmod(index,4)
        box=(round(column*source.width/4)+3,round(row*source.height/4)+3,
             round((column+1)*source.width/4)-3,round((row+1)*source.height/4)-3)
        tile=source.crop(box).resize((256,256),Image.Resampling.LANCZOS)
        if index>=8:
            # Black-backed emissive artwork -> alpha, preserving premultiplied radiance.
            pixels=[]
            for r,g,b in tile.getdata():
                alpha=max(r,g,b)
                pixels.append((round(r*255/alpha),round(g*255/alpha),round(b*255/alpha),alpha) if alpha>6 else (0,0,0,0))
            transparent=Image.new('RGBA',tile.size);transparent.putdata(pixels);tile=transparent
        tile.save(destination/(name+'.png'),optimize=True)
        records.append({'name':name,'source_box':box,'kind':'icon' if index<8 else 'effect','size':[256,256]})
    (staging/'manifest.json').write_text(json.dumps({'source_size':source.size,'cells':records},indent=2),encoding='utf-8')
    print(f'Imported {len(records)} sprites into {destination}')


if __name__=='__main__':main()
