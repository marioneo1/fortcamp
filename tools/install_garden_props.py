"""Import the supplied 8x4 gardening atlas as complete transparent silhouettes."""
import json
import shutil
from pathlib import Path
from PIL import Image,ImageDraw
from audit_catalogue_crops import source_icons,recovered_icon

ROOT=Path(__file__).resolve().parents[1]
IDS=['basil_pot','lavender_pot','empty_pots','mixed_herb_bowl','white_flower_box',
     'yellow_flower_box','lavender_barrel','herb_basket','watering_can','wooden_bucket',
     'water_barrel','stone_water_trough','soil_sack','compost_bin','herb_wheelbarrow',
     'potting_bench','shovel','rake','garden_fork','tool_caddy','mixed_herb_box',
     'cut_herb_box','garden_stool','seed_crate','white_flower_trellis','purple_flower_trellis',
     'herb_drying_rack','bundled_stakes','pruning_basket','stacked_empty_pots',
     'mixed_herb_barrel','supply_crate']

def main():
    source_path=ROOT/'staging-terrain/Gardening Props Asset Atlas.png'
    source=Image.open(source_path).convert('RGBA')
    anchors,parts,labels=source_icons(source,8,4)
    folder=ROOT/'staging-terrain/garden-props-v1';folder.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source_path,folder/'garden_props_32.png')
    destination=ROOT/'frontend/public/assets/combat-terrain/props/garden-v1'
    destination.mkdir(parents=True,exist_ok=True)
    registry_path=ROOT/'frontend/src/map-prop-art.json'
    registry=json.loads(registry_path.read_text())
    gallery=Image.new('RGB',(1536,872),'#25302a');draw=ImageDraw.Draw(gallery);report=[]
    for index,(name,anchor) in enumerate(zip(IDS,anchors)):
        ident='garden_'+name
        l,t,r,b=anchor['box']
        if min(l,t,source.width-r,source.height-b)<3:raise ValueError(f'{ident}: clipped source')
        icon=recovered_icon(source,anchor,parts,labels,size=384,padding=28)
        icon.save(destination/f'{ident}.png',optimize=True)
        registry[ident]=f'props/garden-v1/{ident}.png'
        preview=icon.resize((192,192),Image.Resampling.LANCZOS);x,y=index%8*192,index//8*218
        gallery.paste(preview,(x,y),preview);draw.text((x+3,y+196),name,fill='white')
        report.append({'id':ident,'source_box':anchor['box'],'output_box':icon.getbbox()})
    registry_path.write_text(json.dumps(registry,indent=2)+'\n')
    (folder/'extraction.json').write_text(json.dumps(report,indent=2)+'\n')
    gallery.save(folder/'extracted-gallery.jpg',quality=94)
    print('Installed 32 garden props; original atlas retained.')

if __name__=='__main__':main()
