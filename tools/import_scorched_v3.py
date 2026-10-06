"""Import an aligned 4x4 overhead fire animation; preserve alpha and cell registration."""
from pathlib import Path
import argparse,shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('source',type=Path);args=p.parse_args()
stage=ROOT/'staging-mage-surfaces';stage.mkdir(exist_ok=True)
source=Image.open(args.source).convert('RGBA');shutil.copy2(args.source,stage/'scorched-v3-atlas.png')
out=ROOT/'frontend/public/assets/mage-scorched-v3';out.mkdir(exist_ok=True)
strip=Image.new('RGBA',(320*16,320));review=Image.new('RGB',(1280,1280),(36,44,35));draw=ImageDraw.Draw(review)
for i in range(16):
 row,col=divmod(i,4)
 bounds=tuple(round(v) for v in (col*source.width/4+3,row*source.height/4+3,(col+1)*source.width/4-3,(row+1)*source.height/4-3))
 frame=source.crop(bounds).resize((320,320),Image.Resampling.LANCZOS)
 frame.putalpha(frame.getchannel('A').point(lambda a:0 if a<4 else a))
 frame.save(out/f'fire_{i+1:02}.png');strip.alpha_composite(frame,(i*320,0));review.paste(frame,(col*320,row*320),frame);draw.text((col*320+8,row*320+306),str(i+1),fill='white')
strip.save(out/'fire_strip.png');review.save(stage/'scorched-v3-review.jpg');print(out,source.size)
