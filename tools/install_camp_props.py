"""Install the 8x4 camp atlas using whole silhouettes, never blind grid cuts.

Run from the project: .venv/Scripts/python.exe tools/install_camp_props.py
Original atlas stays in staging-terrain/camp-props-v1; no older art is replaced.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
from audit_catalogue_crops import source_icons, recovered_icon

ROOT = Path(__file__).resolve().parents[1]
IDS = [
    'straw_training_dummy', 'armored_training_dummy', 'archery_target', 'hay_archery_butt',
    'practice_weapon_rack', 'training_shield_rack', 'arrow_bundle', 'war_drum',
    'sleeping_bag', 'straw_bed', 'canvas_cot', 'wooden_bed', 'stone_bed', 'luxurious_bed',
    'tribal_hide_bed', 'reed_sleeping_mat', 'camp_cooking_pot', 'food_prep_table',
    'grain_sacks', 'water_trough', 'wash_tub', 'mess_bench', 'herb_planter', 'village_well',
    'ballista_loaded', 'ballista_empty', 'oil_cauldron', 'oil_cauldron_tipped',
    'ballista_bolts', 'dropped_coin_purse', 'blanket_chest', 'tribal_trophy_pole',
]


def main():
    folder = ROOT/'staging-terrain/camp-props-v1'
    source = Image.open(folder/'camp_props_32.png').convert('RGBA')
    anchors, parts, labels = source_icons(source, 8, 4)
    destination = ROOT/'frontend/public/assets/combat-terrain/props/camp-v1'
    destination.mkdir(parents=True, exist_ok=True)
    registry_path = ROOT/'frontend/src/map-prop-art.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    gallery = Image.new('RGB', (8*192, 4*218), '#25302a')
    draw = ImageDraw.Draw(gallery)
    report = []
    for index, (ident, anchor) in enumerate(zip(IDS, anchors)):
        l,t,r,b = anchor['box']
        if min(l,t,source.width-r,source.height-b) < 3:
            raise ValueError(f'{ident}: source silhouette touches canvas edge; inspect before import')
        # The nominal equal grid is for ordering; component masking preserves
        # complete outlines even where a generated silhouette crosses that grid.
        icon = recovered_icon(source, anchor, parts, labels, size=384, padding=28)
        icon.save(destination/f'{ident}.png', optimize=True)
        registry[ident] = f'props/camp-v1/{ident}.png'
        preview = icon.resize((192,192), Image.Resampling.LANCZOS)
        x,y = (index%8)*192, (index//8)*218
        gallery.paste(preview,(x,y),preview)
        draw.text((x+4,y+195),ident,fill='white')
        report.append({'id':ident,'cell':index,'source_box':anchor['box'],
                       'output_box':icon.getbbox(),'source_edge_margin':min(l,t,source.width-r,source.height-b)})
    registry_path.write_text(json.dumps(registry,indent=2)+'\n',encoding='utf-8')
    (folder/'extraction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    gallery.save(folder/'extracted-gallery.jpg', quality=94)
    print('Installed 32 complete camp silhouettes; existing sprites preserved.')


if __name__ == '__main__':
    main()
