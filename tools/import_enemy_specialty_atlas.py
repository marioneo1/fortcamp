"""Import the reviewed 5x4 specialty sheet; isolated cells prevent crop spill."""
from pathlib import Path
import argparse, json, shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
NAMES=['tripline','shakedown','parting_cut','ankle_bite','goliath_shot','tag_team','cornered_fury','heel_cut',
       'tripline_prop','tripline_broken','tripline_hit','shakedown_hit','parting_cut_hit','retreat',
       'ankle_bite_hit','stone','goliath_shot_hit','tag_team_hit','cornered_fury_hit','heel_cut_hit']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('sheet',type=Path);args=parser.parse_args()
    staging=ROOT/'staging-ui/enemy-specialties-v1';staging.mkdir(parents=True,exist_ok=True)
    saved=staging/'atlas.png'
    if args.sheet.resolve()!=saved.resolve():shutil.copy2(args.sheet,saved)
    image=Image.open(saved).convert('RGBA');folder=ROOT/'frontend/public/assets/enemy-specialties-v1';folder.mkdir(parents=True,exist_ok=True)
    entries=[]
    for i,name in enumerate(NAMES):
        row,col=divmod(i,5);bounds=(col*image.width//5,row*image.height//4,(col+1)*image.width//5,(row+1)*image.height//4)
        tile=image.crop(bounds)
        if i>=8:
            # Black-backed painted effects use brightness alpha, retaining color.
            tile.putalpha(tile.convert('RGB').split()[0].point(lambda _:255))
            pixels=[]
            for r,g,b,_ in tile.getdata():
                a=max(r,g,b);pixels.append((r,g,b,0 if a<12 else a))
            tile.putdata(pixels)
        tile=tile.resize((256,256),Image.Resampling.LANCZOS)
        tile.save(folder/(name+'.png'),optimize=True)
        entries.append({'name':name,'bounds':bounds,'alpha':i>=8})
    (staging/'crop-manifest.json').write_text(json.dumps({'columns':5,'rows':4,'size':image.size,'entries':entries},indent=2),encoding='utf-8')
    print('Installed 8 icons and 12 props/effects; source and crop bounds retained.')

if __name__=='__main__':main()
