"""Install the reviewed 6x4 overhead furniture/training atlas with full silhouettes."""
import argparse
import json
from pathlib import Path
from PIL import Image
from audit_catalogue_crops import source_icons, recovered_icon

ROOT=Path(__file__).resolve().parents[1]
IDS=['timber_chair','iron_chair','stone_chair','wicker_chair','upholstered_chair','tribal_chair',
     'wooden_armchair','royal_chair','round_wooden_stool','square_wooden_stool','training_bench','folding_camp_stool',
     'straw_training_dummy','armored_training_dummy','archery_target','hay_archery_butt','practice_weapon_rack','training_shield_rack',
     'floor_training_target','padded_sparring_post','practice_spear_bundle','practice_sword_bundle','archery_quiver','training_helmet_crate']

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atlas',type=Path,required=True)
    args=parser.parse_args()
    source=Image.open(args.atlas).convert('RGBA')
    anchors,parts,labels=source_icons(source,6,4)
    stage=ROOT/'staging-terrain/furniture-training-v1'
    stage.mkdir(parents=True,exist_ok=True)
    source.save(stage/'atlas.png')
    registry_path=ROOT/'frontend/src/map-prop-art.json'
    registry=json.loads(registry_path.read_text())
    sizes=json.loads((ROOT/'frontend/src/map-prop-sizes.json').read_text())
    sizing_path=ROOT/'frontend/src/construction-prop-sizing.json'
    sizing=json.loads(sizing_path.read_text())
    furniture_path=ROOT/'frontend/src/construction-furniture.json'
    furniture=json.loads(furniture_path.read_text())
    report=[]
    output=ROOT/'frontend/public/assets/combat-terrain/props/furniture-training-v1'
    output.mkdir(parents=True,exist_ok=True)
    for index,(ident,anchor) in enumerate(zip(IDS,anchors)):
        l,t,r,b=anchor['box']
        if min(l,t,source.width-r,source.height-b)<3:
            raise ValueError(f'{ident}: silhouette at canvas edge')
        icon=recovered_icon(source,anchor,parts,labels,size=384,padding=20)
        icon.save(output/f'{ident}.png',optimize=True)
        is_seat=index<12
        footprint=[2,1] if ident=='training_bench' else [1,1]
        fill=.35 if 'stool' in ident else .5 if is_seat else .75
        if ident=='training_bench': fill=.75
        if ident in ('practice_spear_bundle','practice_sword_bundle','archery_quiver'):fill=.35
        if ident=='training_helmet_crate':fill=.6
        sizing[ident]={'footprint':footprint,'fill':fill,'category':'seat' if is_seat else 'training equipment'}
        old_file=registry.get(ident)
        registry[ident]=f'props/furniture-training-v1/{ident}.png'
        if is_seat and ident not in furniture['seats']:furniture['seats'].append(ident)
        solid=icon.getchannel('A').point(lambda a:255 if a>=40 else 0).getbbox()
        fraction=max((solid[2]-solid[0])/384,(solid[3]-solid[1])/384)
        # Battle retains its existing declared footprint and fill for replacement IDs.
        profile=sizes.get(ident,{'footprint':footprint,'fill':fill,'category':sizing[ident]['category']})
        profile['scale']=round(profile['fill']/fraction,4)
        sizes[ident]=profile
        report.append({'id':ident,'cell':index,'source_bounds':anchor['box'],'installed':registry[ident],'previous_file_retained':old_file})
    for path,value in [(registry_path,registry),(sizing_path,sizing),(furniture_path,furniture),
                       (ROOT/'frontend/src/map-prop-sizes.json',sizes),(ROOT/'backend/map_prop_sizes.json',sizes)]:
        path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    (stage/'installation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Installed {len(report)} sprites; previous source artwork retained.')

if __name__=='__main__':main()
