from pathlib import Path
from PIL import Image,ImageDraw
import shutil
import argparse
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Import the reviewed 1254px Mage atlas without distorting its assets.')
parser.add_argument('source',nargs='?',type=Path,default=root/'staging-mage/mage-atlas.png')
source=parser.parse_args().source.resolve()
stage=root/'staging-mage';stage.mkdir(exist_ok=True)
if source!=(stage/'mage-atlas.png').resolve():shutil.copy2(source,stage/'mage-atlas.png')
out=root/'frontend/public/assets/mage-v1';out.mkdir(parents=True,exist_ok=True)
im=Image.open(source).convert('RGBA');print(im.size)
rows=[(0,307),(307,600),(600,900),(900,1254)];xs=[0,314,628,942,1254]
names=['chain_lightning','flash_freeze','singularity','meteor','fireball','enchant_weapon','typhoon','debuffer','lightning_arc','ice_shell','frost_ground','gravity_vortex','meteor_rock','fire_contact','scorched_tile','wind_ring']
contact=Image.new('RGB',(1024,1024),(23,34,29));draw=ImageDraw.Draw(contact)
for i,name in enumerate(names):
 row,col=divmod(i,4);bounds=(xs[col],rows[row][0],xs[col+1],rows[row][1]);crop=im.crop((bounds[0],bounds[1],bounds[2],880) if name=='lightning_arc' else bounds)
 bbox=crop.getchannel('A').getbbox()
 if bbox:crop=crop.crop(bbox)
 size=256 if i<8 else 384;crop.thumbnail((size-8,size-8),Image.Resampling.LANCZOS);asset=Image.new('RGBA',(size,size));asset.alpha_composite(crop,((size-crop.width)//2,(size-crop.height)//2));asset.save(out/(name+'.png'))
 preview=asset.copy();preview.thumbnail((232,228));contact.paste(preview,(col*256+(256-preview.width)//2,row*256+8),preview);draw.text((col*256+10,row*256+240),name,fill='white')
contact.save(stage/'review.png')
