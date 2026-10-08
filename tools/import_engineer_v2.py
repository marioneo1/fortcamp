"""Install the reviewed 4x3 Engineer atlas without neighboring-cell contamination."""
from pathlib import Path
from PIL import Image
import json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
NAMES=['sentry_turret','heavy_emplacement','dynamite','rapid_assembly','man_the_guns','overclock','scuttle_protocol','proximity_charge','sentry_unfinished','heavy_unfinished','explosive_bolt','cross_blast']
def install(source):
 stage=ROOT/'staging-terrain/engineer-v2';dest=ROOT/'frontend/public/assets/engineer-v2'
 stage.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True,exist_ok=True)
 shutil.copy2(source,stage/'atlas.png')
 im=Image.open(source).convert('RGBA');records=[]
 # Reviewed atlas: 1448x1086, black dividers at x=360/722/1084, y=357/716.
 xs=[0,362,724,1086,1448];ys=[0,359,719,1086]
 for i,name in enumerate(NAMES):
  row,col=divmod(i,4);box=(round((xs[col]+3)*im.width/1448),round((ys[row]+3)*im.height/1086),round((xs[col+1]-3)*im.width/1448),round((ys[row+1]-3)*im.height/1086))
  tile=im.crop(box)
  if row<2:tile=tile.resize((384,384),Image.Resampling.LANCZOS)
  else:
   canvas=Image.new('RGBA',(max(tile.size),)*2);canvas.alpha_composite(tile,((canvas.width-tile.width)//2,(canvas.height-tile.height)//2));tile=canvas.resize((384,384),Image.Resampling.LANCZOS)
  tile.save(dest/(name+'.png'));records.append({'name':name,'box':box})
 (stage/'manifest.json').write_text(json.dumps({'size':im.size,'cells':records},indent=2),encoding='utf-8')
if __name__=='__main__':install(sys.argv[1])
