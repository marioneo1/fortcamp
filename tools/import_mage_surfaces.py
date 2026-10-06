"""Slice the two reviewed 4x4 surface atlases; preserve frame alignment and alpha."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--frozen',type=Path,default=ROOT/'staging-mage-surfaces/frozen-atlas.png')
parser.add_argument('--scorched',type=Path,default=ROOT/'staging-mage-surfaces/scorched-atlas.png')
args=parser.parse_args()
stage=ROOT/'staging-mage-surfaces';stage.mkdir(exist_ok=True)
groups={
 'frozen':([f'{kind}_{i}' for kind in ('freeze','frozen','break','thaw') for i in range(1,5)],args.frozen),
 'scorched':([f'{kind}_{i}' for kind in ('soot','ash','flame') for i in range(1,5)]+['ember_1','ember_2','smoke_1','smoke_2'],args.scorched),
}
for name,(names,path) in groups.items():
 image=Image.open(path).convert('RGBA')
 image.save(stage/(name+'-atlas.png'))
 out=ROOT/'frontend/public/assets'/('mage-'+name+'-v2');out.mkdir(exist_ok=True)
 review=Image.new('RGB',(1024,1024),(36,44,35));draw=ImageDraw.Draw(review);frames=[]
 for index,label in enumerate(names):
  row,col=divmod(index,4)
  bounds=tuple(round(v) for v in (col*image.width/4,row*image.height/4,(col+1)*image.width/4,(row+1)*image.height/4))
  # Fixed cell crop/resize: independently centring each frame makes animation jitter.
  asset=image.crop(bounds).resize((256,256),Image.Resampling.LANCZOS)
  asset.putalpha(asset.getchannel('A').point(lambda alpha:0 if alpha<4 else alpha))
  asset.save(out/(label+'.png'))
  review.paste(asset,(col*256,row*256),asset);draw.text((col*256+8,row*256+242),label,fill='white')
  if name=='scorched' and label.startswith('flame_'):frames.append(asset)
 if frames:
  strip=Image.new('RGBA',(1024,256))
  for i,frame in enumerate(frames):strip.alpha_composite(frame,(i*256,0))
  strip.save(out/'flame_strip.png')
 review.save(stage/(name+'-review.jpg'))
 print(name,len(names),'RGBA assets',image.size)
