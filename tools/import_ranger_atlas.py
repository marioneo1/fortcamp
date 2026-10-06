"""Import an equal 4x4 Ranger atlas. Usage: python tools/import_ranger_atlas.py atlas.png."""
from pathlib import Path
import argparse
import json
import shutil
from PIL import Image, ImageOps

NAMES = ('mark_quarry','longshot','multi_shot','rapid_fire','poison_attack','pestilence_shot','rupturing_blow','sharpshooter','arrow','arrow_trail','poison_arrow','poison_contact','rupture_burst','quarry_ring','steady_ring','critical_spark')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('atlas',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    source=Image.open(args.atlas).convert('RGB')
    destination=root/'frontend/public/assets/ranger-v1'
    staging=root/'staging-ui/ranger-v1'
    destination.mkdir(parents=True,exist_ok=True);staging.mkdir(parents=True,exist_ok=True)
    if args.atlas.resolve() != (staging/'atlas.png').resolve():
        shutil.copy2(args.atlas,staging/'atlas.png')
    records=[]
    for index,name in enumerate(NAMES):
        row,column=divmod(index,4)
        box=(round(column*source.width/4)+3,round(row*source.height/4)+3,
             round((column+1)*source.width/4)-3,round((row+1)*source.height/4)-3)
        # The generated effect rows have looser gutters than the framed icons.
        # Reviewed per-sprite bounds preserve arrow tips and exclude the next row.
        effect_boxes=[(0,620,344,850),(344,620,630,850),(630,620,972,868),(972,620,1254,868),
                      (0,870,344,1254),(329,880,640,1254),(640,880,951,1254),(951,880,1254,1254)]
        if index>=8:
            reference=effect_boxes[index-8]
            box=tuple(round(v*(source.width/1254 if i%2==0 else source.height/1254)) for i,v in enumerate(reference))
        tile=source.crop(box)
        if index>=8:
            # Black-backed emissive artwork -> alpha, preserving premultiplied radiance.
            pixels=[]
            for r,g,b in tile.getdata():
                alpha=max(r,g,b)
                pixels.append((round(r*255/alpha),round(g*255/alpha),round(b*255/alpha),alpha) if alpha>6 else (0,0,0,0))
            transparent=Image.new('RGBA',tile.size);transparent.putdata(pixels);tile=transparent
            # Keep aspect ratio and full silhouette; do not stretch narrow arrows.
            bounds=tile.getbbox()
            if bounds:tile=tile.crop(bounds)
            tile=ImageOps.pad(tile,(256,256),method=Image.Resampling.LANCZOS,color=(0,0,0,0))
        else:tile=tile.resize((256,256),Image.Resampling.LANCZOS)
        tile.save(destination/(name+'.png'),optimize=True)
        records.append({'name':name,'source_box':box,'kind':'icon' if index<8 else 'effect','size':[256,256]})
    (staging/'manifest.json').write_text(json.dumps({'source_size':source.size,'cells':records},indent=2),encoding='utf-8')
    print(f'Imported {len(records)} sprites into {destination}')


if __name__=='__main__':main()
