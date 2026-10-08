"""Import the inspected four-by-four Summoner atlas without recropping neighbours."""
import json
import shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NAMES=['portrait_fire','portrait_earth','portrait_grass','portrait_wisp','transposition','bound_companion','wisp_swarm','spirit_projection','sacrifice','overload','life_pact','rapid_conjuration','conjure','projectile','explosion','nature_burst']
def main(source):
    staging=ROOT/'staging-ui/summoner-v1';dest=ROOT/'frontend/public/assets/summoner-v1'
    staging.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,staging/'atlas.png');atlas=Image.open(source).convert('RGBA');records=[]
    for i,name in enumerate(NAMES):
        x,y=i%4,i//4
        box=tuple(round(v) for v in (x*atlas.width/4,y*atlas.height/4,(x+1)*atlas.width/4,(y+1)*atlas.height/4))
        art=atlas.crop(box)
        # Inset within each cell: the generated atlas has no separator, so never
        # expand bounds into an adjacent image. Effects retain their real alpha.
        art=art.crop((3,3,art.width-3,art.height-3)).resize((256,256),Image.Resampling.LANCZOS)
        art.save(dest/(name+'.png'));records.append({'name':name,'bounds':box})
    (staging/'manifest.json').write_text(json.dumps({'source':'Built-in imagegen; inspected 4x4 atlas','cells':records},indent=2))
    print(dest)
if __name__=='__main__':
    import sys
    main(Path(sys.argv[1]))
