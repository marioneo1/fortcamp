"""Install reviewed Engineer atlas cells with shared animation anchors."""
from pathlib import Path
import json,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NAMES=['heavy_idle','heavy_fire','heavy_recoil','heavy_destroyed','sentry_idle','sentry_fire','sentry_recoil','sentry_destroyed','mine','dynamite','bolt','explosion','man_the_guns','overclock','scuttle_protocol','rapid_assembly']
def install(source):
 source=Path(source);stage=ROOT/'staging-terrain/engineer-v1';dest=ROOT/'frontend/public/assets/engineer-v1'
 stage.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True,exist_ok=True)
 shutil.copy2(source,stage/'atlas.png') if source.resolve()!=(stage/'atlas.png').resolve() else None
 im=Image.open(source).convert('RGBA');assert im.getchannel('A').getextrema()[0]==0
 # Generated rows were visually reviewed; use their actual gutters, not assumed quarters.
 rows=[0,365/1254,670/1254,978/1254,1];records=[]
 for i,name in enumerate(NAMES):
  row,col=divmod(i,4);box=(round(col*im.width/4),round(rows[row]*im.height),round((col+1)*im.width/4),round(rows[row+1]*im.height))
  tile=im.crop(box);side=max(tile.size);out=Image.new('RGBA',(side,side));out.paste(tile,((side-tile.width)//2,(side-tile.height)//2));out.resize((384,384),Image.Resampling.LANCZOS).save(dest/(name+'.png'))
  records.append({'name':name,'box':box,'anchor':'shared row canvas'})
 for key,frame in [('sentry_turret','sentry_idle'),('heavy_emplacement','heavy_idle'),('proximity_charge','mine')]:shutil.copy2(dest/(frame+'.png'),dest/(key+'.png'))
 (stage/'manifest.json').write_text(json.dumps({'source':str(source),'size':im.size,'cells':records},indent=2),encoding='utf-8')
 print('Installed Engineer atlas: 16 cells and three icon aliases.')
if __name__=='__main__':
 import sys;install(sys.argv[1])
