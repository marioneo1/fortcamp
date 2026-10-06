"""Install equal 4x4 transparent tactical props; preserve turret frame anchors."""
from pathlib import Path
import argparse,json,shutil
from PIL import Image,ImageDraw
NAMES=('caltrops_rust_a','caltrops_rust_b','caltrops_steel','caltrops_cast','turret_idle','turret_fire','turret_recoil','turret_destroyed','turret_bolt','turret_trail','heavy_turret_idle','heavy_turret_destroyed','repair_tools','spare_bolts','bear_trap_open','bear_trap_closed')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('atlas',type=Path);args=parser.parse_args()
 root=Path(__file__).resolve().parents[1];staging=root/'staging-terrain/tactical-props-v1';dest=root/'frontend/public/assets/tactical-props-v1'
 staging.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True,exist_ok=True)
 source=Image.open(args.atlas).convert('RGBA')
 if source.getchannel('A').getextrema()[0]!=0:raise ValueError('Atlas must have real transparent gutters')
 if args.atlas.resolve()!=(staging/'atlas.png').resolve():shutil.copy2(args.atlas,staging/'atlas.png')
 records=[];gallery=Image.new('RGB',(1024,1152),'#29342a');draw=ImageDraw.Draw(gallery)
 for i,name in enumerate(NAMES):
  row,col=divmod(i,4);left,top,right,bottom=round(col*source.width/4),round(row*source.height/4),round((col+1)*source.width/4),round((row+1)*source.height/4)
  # The firing bolt extends into empty gutter ABOVE its own cell. All four
  # animation frames keep a shared extended canvas, without auto-centering.
  extra=round(source.height/4*.13) if row==1 else 0
  crop_top=top-extra if i==5 else top
  tile=source.crop((left,crop_top,right,bottom));canvas=Image.new('RGBA',(right-left,bottom-top+extra))
  canvas.paste(tile,(0,crop_top-(top-extra)))
  side=max(canvas.size);square=Image.new('RGBA',(side,side));square.paste(canvas,((side-canvas.width)//2,0));canvas=square.resize((384,384),Image.Resampling.LANCZOS);canvas.save(dest/(name+'.png'),optimize=True)
  preview=canvas.resize((256,256),Image.Resampling.LANCZOS);gx,gy=col*256,row*288;gallery.paste(preview,(gx,gy),preview);draw.text((gx+5,gy+259),name,fill='white')
  records.append({'name':name,'source_box':[left,crop_top,right,bottom],'canvas_size':[384,384],'alpha_box':canvas.getbbox(),'shared_turret_anchor':row==1})
 (staging/'manifest.json').write_text(json.dumps({'source':str(args.atlas),'source_size':source.size,'cells':records},indent=2)+'\n',encoding='utf-8');gallery.save(staging/'gallery.jpg',quality=95)
 print('Installed 16 transparent props/frames; turret origins preserved.')
if __name__=='__main__':main()
