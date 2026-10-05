"""Extract the uniform 4x3 melee atlas without stretching or changing its alpha."""
import json
import argparse
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
STAGING=ROOT/'staging-ui/melee-families-v1'
PUBLIC=ROOT/'frontend/public/assets/melee-families-v1'
NAMES=[f'{style}_{phase}' for style in ('slash','hack','crush','blunt','fist','stab') for phase in ('contact','fade')]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--net',action='store_true',help='Import the 2x2 net phases instead')
    mode.add_argument('--flesh',action='store_true',help='Import the 4x2 flesh contacts instead')
    args=parser.parse_args()
    staging=ROOT/'staging-ui/capture-net-v1' if args.net else STAGING
    public=ROOT/'frontend/public/assets/capture-net-v1' if args.net else PUBLIC
    names=['folded','opening','spread','cinched'] if args.net else NAMES
    if args.flesh:
        staging=ROOT/'staging-ui/flesh-contact-v1';public=ROOT/'frontend/public/assets/flesh-contact-v1'
        names=[f'{style}_{phase}' for style in ('slash','hack','crush','stab') for phase in ('contact','fade')]
    columns,rows=(4,2) if args.flesh else (2,2) if args.net else (4,3)
    source=Image.open(staging/'atlas.png').convert('RGBA')
    public.mkdir(parents=True,exist_ok=True)
    records=[]
    for i,name in enumerate(names):
        c,r=i%columns,i//columns
        box=tuple(round(v) for v in (c*source.width/columns,r*source.height/rows,(c+1)*source.width/columns,(r+1)*source.height/rows))
        tile=source.crop(box)
        if tile.getchannel('A').getbbox() is None:raise ValueError(f'Empty cell: {name}')
        # The generator may return a different canvas ratio; retain proportions.
        tile.thumbnail((256,256),Image.Resampling.LANCZOS)
        output=Image.new('RGBA',(256,256))
        output.alpha_composite(tile,((256-tile.width)//2,(256-tile.height)//2))
        # These four atlas cells contain a disconnected neighbor fragment at left.
        # Clear only the reviewed 48px gutter; preserve the intended effect and scale.
        if args.flesh and name in {'crush_fade','hack_fade','slash_fade','stab_contact'}:
            output.paste((0,0,0,0),(0,0,48,256))
        if args.flesh and name=='slash_fade':
            output.paste((0,0,0,0),(0,170,80,256))
        output.save(public/f'{name}.png',optimize=True)
        records.append({'name':name,'crop':box,'source':str(staging/'atlas.png'),'size':[256,256]})
    (staging/'manifest.json').write_text(json.dumps({'source_size':source.size,'cells':records},indent=2),encoding='utf-8')
    print(f'Imported {len(records)} transparent effects, preserving aspect and source alpha.')

if __name__=='__main__':main()
