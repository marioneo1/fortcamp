"""Extract the fixed 6x4 guild icon sheet using actual image dimensions, preserving alpha."""
import argparse,json,shutil
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageDraw
from extract_combat_ui_rows import normalize,remove_tiny_islands
ROOT=Path(__file__).resolve().parents[1]
NAMES=['rank_e','rank_d','rank_c','rank_b','rank_a','rank_s','form_recovery','form_rescue','form_defense','form_hunt','form_containment','form_investigation','form_infiltration','form_operation','event_goblin_warhost','event_ashen_procession','event_arcane_convergence','event_great_beast_tide','event_starfall_omen','utility_public','utility_private','utility_reward','utility_clock','utility_party']
def refresh_rank_row(source,destination):
    """Use the whole cleaned row height; replace only the six stable rank files."""
    sheet=Image.open(source).convert('RGBA')
    manifest_path=destination/'manifest.json'
    manifest=json.loads(manifest_path.read_text())
    backup=source.parent/'crop_backups'/('ranks_'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    for name in NAMES[:6]:shutil.copy2(destination/(name+'.png'),backup/(name+'.png'))
    shutil.copy2(manifest_path,backup/'manifest.json')
    montage=Image.new('RGB',(960,180),'#1a211b');draw=ImageDraw.Draw(montage)
    for column,name in enumerate(NAMES[:6]):
        bounds=(round(column*sheet.width/6),0,round((column+1)*sheet.width/6),sheet.height)
        icon=normalize(remove_tiny_islands(sheet.crop(bounds),minimum_ratio=.02),name,256)
        icon.save(destination/(name+'.png'),optimize=True)
        thumb=icon.resize((144,144));montage.paste(thumb,(column*160+8,4),thumb);draw.text((column*160+8,152),name,fill='#d7b66a')
        manifest['icons'][name]={'source':source.name,'source_dimensions':list(sheet.size),'crop':bounds,'file':name+'.png','size':256}
    manifest_path.write_text(json.dumps(manifest,indent=2))
    montage.save(source.parent/'rank_row_extracted_preview.png')
    print(f'Refreshed six ranks from {sheet.width}x{sheet.height} row; other icons unchanged. Backup: {backup}')
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=ROOT/'staging-ui/mission-board-v1/guild_icons_6x4.png');parser.add_argument('--rank-row',type=Path,help='Refresh only rank E/D/C/B/A/S from a cleaned six-column row');args=parser.parse_args()
    destination=ROOT/'frontend/public/assets/mission-board-v1';destination.mkdir(parents=True,exist_ok=True)
    if args.rank_row:
        refresh_rank_row(args.rank_row,destination);return
    sheet=Image.open(args.source).convert('RGBA');manifest={'source':args.source.name,'dimensions':sheet.size,'columns':6,'rows':4,'icons':{}}
    rank_source=args.source.parent/'guild_icons_first_row.png'
    rank_sheet=Image.open(rank_source).convert('RGBA') if args.source.name=='guild_icons_6x4.png' and rank_source.exists() else None
    montage=Image.new('RGB',(960,640),'#1a211b');draw=ImageDraw.Draw(montage)
    for index,name in enumerate(NAMES):
        row,column=divmod(index,6);bounds=(round(column*sheet.width/6),round(row*sheet.height/4),round((column+1)*sheet.width/6),round((row+1)*sheet.height/4));cell=sheet.crop(bounds)
        if rank_sheet is not None and index<6:
            bounds=(round(column*rank_sheet.width/6),0,round((column+1)*rank_sheet.width/6),rank_sheet.height);cell=rank_sheet.crop(bounds)
        cell=remove_tiny_islands(cell,minimum_ratio=.02)
        icon=normalize(cell,name,256);icon.save(destination/(name+'.png'))
        thumbnail=icon.resize((132,132));montage.paste(thumbnail,(column*160+14,row*160+4),thumbnail);draw.text((column*160+8,row*160+141),name,fill='#d7b66a')
        manifest['icons'][name]={'crop':bounds,'file':name+'.png','size':256}
        if rank_sheet is not None and index<6:manifest['icons'][name].update(source=rank_source.name,source_dimensions=list(rank_sheet.size))
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2));montage.save(args.source.parent/'extracted_preview.jpg')
    print('Extracted 24 icons with transparency and uniform aspect-preserving scale.')
if __name__=='__main__':main()
