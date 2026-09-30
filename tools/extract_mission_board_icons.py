"""Extract the fixed 6x4 guild icon sheet using actual image dimensions, preserving alpha."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
from extract_combat_ui_rows import normalize,remove_tiny_islands
ROOT=Path(__file__).resolve().parents[1]
NAMES=['rank_e','rank_d','rank_c','rank_b','rank_a','rank_s','form_recovery','form_rescue','form_defense','form_hunt','form_containment','form_investigation','form_infiltration','form_operation','event_goblin_warhost','event_ashen_procession','event_arcane_convergence','event_great_beast_tide','event_starfall_omen','utility_public','utility_private','utility_reward','utility_clock','utility_party']
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=ROOT/'staging-ui/mission-board-v1/guild_icons_6x4.png');args=parser.parse_args()
    destination=ROOT/'frontend/public/assets/mission-board-v1';destination.mkdir(parents=True,exist_ok=True)
    sheet=Image.open(args.source).convert('RGBA');manifest={'source':args.source.name,'dimensions':sheet.size,'columns':6,'rows':4,'icons':{}}
    montage=Image.new('RGB',(960,640),'#1a211b');draw=ImageDraw.Draw(montage)
    for index,name in enumerate(NAMES):
        row,column=divmod(index,6);bounds=(round(column*sheet.width/6),round(row*sheet.height/4),round((column+1)*sheet.width/6),round((row+1)*sheet.height/4));cell=sheet.crop(bounds)
        cell=remove_tiny_islands(cell,minimum_ratio=.02)
        icon=normalize(cell,name,256);icon.save(destination/(name+'.png'))
        thumbnail=icon.resize((132,132));montage.paste(thumbnail,(column*160+14,row*160+4),thumbnail);draw.text((column*160+8,row*160+141),name,fill='#d7b66a')
        manifest['icons'][name]={'crop':bounds,'file':name+'.png','size':256}
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2));montage.save(args.source.parent/'extracted_preview.jpg')
    print('Extracted 24 icons with transparency and uniform aspect-preserving scale.')
if __name__=='__main__':main()
