from pathlib import Path
from PIL import Image
import shutil,json
root=Path(__file__).resolve().parents[1];source=root/'staging-art/captor-v1/atlas.png';out=root/'frontend/public/assets/captor-v1';out.mkdir(parents=True,exist_ok=True);stage=root/'staging-art/captor-v1';stage.mkdir(parents=True,exist_ok=True);
im=Image.open(source);keys=['subduing_blow','bola','hook_and_drag','abduct','restraining_hold','blitz','restraint','clean_capture','bola_prop','hook_prop','rope_prop','manacles_prop'];manifest={}
for i,key in enumerate(keys):
 x=i%4;y=i//4;box=(round(x*im.width/4)+3,round(y*im.height/3)+3,round((x+1)*im.width/4)-3,round((y+1)*im.height/3)-3);tile=im.crop(box).resize((384,384),Image.Resampling.LANCZOS);tile.save(out/(key+'.png'));manifest[key]=box
(stage/'crops.json').write_text(json.dumps(manifest,indent=2))

# Runtime projectiles come from a separate genuinely transparent packed strip.
props=Image.open(stage/'props.png').convert('RGBA')
for i,key in enumerate(keys[8:]):
 box=(round(i*props.width/4),0,round((i+1)*props.width/4),props.height)
 tile=props.crop(box);tile.thumbnail((256,256),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(256,256));canvas.alpha_composite(tile,((256-tile.width)//2,(256-tile.height)//2))
 canvas.save(out/(key+'.png'));manifest[key]={'source':'props.png','box':box}
(stage/'crops.json').write_text(json.dumps(manifest,indent=2))
