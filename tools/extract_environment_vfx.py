"""Extract the approved 6x4 environmental VFX sheet with preserved soft transparency."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
NAMES=['leaf_oak_gold','leaf_maple_rust','leaf_birch_green','leaf_curled_brown','grass_seeds','petal_ochre','ash_flake','ash_cluster','ember_orange','ember_green','mist_gray','mist_violet','glyph_cyan','glyph_violet','arcane_ribbon','electric_arc','alien_ribbon','alien_mote','alien_comet','impact_violet','snowflake','rain_streaks','wind_curl','dust_gold']
GROUPS=['foliage']*6+['ash']*2+['ember']*2+['mist']*2+['arcane']*4+['alien']*4+['weather']*4

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=ROOT/'staging-ui/vfx-atlas-v1/environment_vfx_6x4.png');args=parser.parse_args()
    sheet=Image.open(args.source).convert('RGBA');destination=ROOT/'frontend/public/assets/vfx/environment-v1';destination.mkdir(parents=True,exist_ok=True)
    manifest={'pack':'environment-v1','source':args.source.name,'dimensions':sheet.size,'columns':6,'rows':4,'assets':{}}
    montage=Image.new('RGB',(960,640),'#151b18');draw=ImageDraw.Draw(montage)
    for index,name in enumerate(NAMES):
        row,col=divmod(index,6);bounds=(round(col*sheet.width/6),round(row*sheet.height/4),round((col+1)*sheet.width/6),round((row+1)*sheet.height/4));cell=sheet.crop(bounds)
        # Do not threshold or discard separated fragments: these effects need feathered alpha and satellite sparks.
        visible=cell.getchannel('A').point(lambda a:255 if a>=5 else 0).getbbox()
        if not visible:raise ValueError('Empty effect: '+name)
        trimmed=cell.crop((max(0,visible[0]-4),max(0,visible[1]-4),min(cell.width,visible[2]+4),min(cell.height,visible[3]+4)))
        output=Image.new('RGBA',(trimmed.width+16,trimmed.height+16));output.alpha_composite(trimmed,(8,8));output.save(destination/(name+'.png'))
        manifest['assets'][name]={'file':name+'.png','group':GROUPS[index],'crop':bounds,'size':output.size,'anchor':[.5,.5],'alpha':'feathered','role':'particle or layer, not an animation frame'}
        thumb=output.copy();thumb.thumbnail((132,130),Image.Resampling.LANCZOS);montage.paste(thumb,(col*160+(160-thumb.width)//2,row*160+(136-thumb.height)//2),thumb);draw.text((col*160+6,row*160+140),name,fill='#d7b66a')
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');montage.save(args.source.parent/'extracted_preview.jpg')
    print('Extracted 24 VFX textures with soft alpha, individual aspect ratios and stable names.')
if __name__=='__main__':main()
