"""Import the equal 3x2 Fighter atlas without altering the original source."""
import json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NAMES=['chain-snare','earthbreaker','hold-together','end-turn','chain-effect','earth-impact']
def main():
 source=ROOT/'staging-ui/combat-fighter-v3/fighter-atlas.png'
 image=Image.open(source).convert('RGB')
 if abs(image.width/image.height-1.5)>.02:raise ValueError('Expected equal-square 3x2 atlas')
 output=ROOT/'frontend/public/assets/combat-fighter-v3';output.mkdir(parents=True,exist_ok=True)
 for i,name in enumerate(NAMES):
  x,y=i%3,i//3
  image.crop((round(x*image.width/3),round(y*image.height/2),round((x+1)*image.width/3),round((y+1)*image.height/2))).resize((256 if i>=4 else 128,)*2,Image.Resampling.LANCZOS).save(output/(name+'.png'))
 (source.parent/'manifest.json').write_text(json.dumps({'source_size':image.size,'grid':[3,2],'names':NAMES},indent=2))
 print('Imported six equal square Fighter assets')
if __name__=='__main__':main()
