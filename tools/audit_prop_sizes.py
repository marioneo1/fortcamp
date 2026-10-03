"""Audit all registered map objects and encounter use; write shared size rules.

--write-profiles updates calibrated presentation data; it does not rewrite saves.
Without it, regenerates the report from current profiles and fixture encounters.
"""
import argparse
import json
import hashlib
import shutil
from collections import Counter,defaultdict
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'frontend/public/assets/combat-terrain'

def profile(sprite):
    name=sprite.removeprefix('structure:')
    footprint=[1,1];fill=.85;category='ordinary prop'
    if name in {'prison_wagon','prison_wagon_broken','canvas_tent','ballista_loaded','ballista_empty','village_well'} or 'rescue_cage' in name:
        footprint=[2,2];fill=.9;category='large object'
    elif name in {'sleeping_bag','straw_bed','canvas_cot','wooden_bed','stone_bed','luxurious_bed','tribal_hide_bed','reed_sleeping_mat','bedroll'}:
        footprint=[1,2];fill=.92;category='bedding'
    elif name=='wooden_handcart' or name.startswith(('stone_sarcophagus','prisoner_stocks')):
        footprint=[2,1];fill=.88;category='long object'
    if any(term in name for term in ('satchel','purse','pruning_basket','bucket','watering_can','empty_pots','garden_stool','garden_tool_caddy','arrow_bundle','ballista_bolts')):
        fill=.45;category='small clutter'
    if name=='camp_lantern':fill=.38;category='small clutter'
    if name=='wagon_wheel':fill=.65
    if name=='marked_farm_chart':fill=.6
    result={'footprint':footprint,'fill':fill,'category':category}
    if name in {'oak_tree','pine_tree','birch_tree'}:
        result.update(category='tree canopy',art_span=[2,2])
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-profiles',action='store_true');parser.add_argument('--retire-legacy',action='store_true');args=parser.parse_args()
    registry=json.loads((ROOT/'frontend/src/map-prop-art.json').read_text())
    fixture=json.loads((ROOT/'staging-terrain/overhead-props-v2/coverage-input.json').read_text())
    usage=Counter();examples=defaultdict(list)
    objects={'prisoner_pen':'structure:wooden_rescue_cage_closed','iron_rescue_cage':'structure:iron_rescue_cage_closed',
             'wooden_rescue_cage':'structure:wooden_rescue_cage_closed','alarm_horn':'alarm_bell_active',
             'dispatch_satchel':'dispatch_satchel','loose_wheel':'wagon_wheel','signal_chart':'marked_farm_chart',
             'supply_crate':'crate_closed','loose_stone':'scattered_stones'}
    for scene,board in fixture.items():
        entries=board.get('terrain',[])+board.get('decorations',[])+list(board.get('objects',{}).values())
        for item in entries:
            sprite=item.get('sprite') or objects.get(item.get('id'))
            if not sprite:continue
            usage[sprite]+=1
            example={'scene':scene,'id':item['id'],'footprint':item.get('footprint',[1,1]),'art_scale':item.get('art_scale',1)}
            if example['footprint'] not in [x['footprint'] for x in examples[sprite]]:examples[sprite].append(example)
    coverage=ROOT/'staging-terrain/overhead-props-v2/coverage-audit.json'
    resolved=json.loads(coverage.read_text()).get('records',[]) if coverage.exists() else []
    if resolved:
        # Use the renderer's actual alias/state resolution, including cages,
        # chests, optional interactions and destroyed appearances.
        usage.clear();examples.clear()
        for record in resolved:
            sprite=record['sprite'];usage[sprite]+=1
            board=fixture[record['encounter']]
            entries=board.get('terrain',[])+board.get('decorations',[])+list(board.get('objects',{}).values())
            item=next((entry for entry in entries if entry['id']==record['id']),{})
            example={'scene':record['encounter'],'id':record['id'],'footprint':item.get('footprint',[1,1]),
                     'art_scale':item.get('art_scale',1),'size_variant':item.get('size_variant')}
            if (example['footprint'],example['size_variant']) not in [(e['footprint'],e.get('size_variant')) for e in examples[sprite]]:examples[sprite].append(example)
    profiles={};records=[]
    for sprite,path in registry.items():
        # Architectural parts have calibrated join geometry, not prop scales.
        if path.startswith('structures/building-'):continue
        im=Image.open(ASSETS/path).convert('RGBA');box=im.getbbox()
        alpha=im.getchannel('A');solid=alpha.point(lambda value:255 if value>=40 else 0).getbbox()
        bounds=solid or box;fraction=max((bounds[2]-bounds[0])/im.width,(bounds[3]-bounds[1])/im.height)
        settings=profile(sprite);settings['scale']=round(settings['fill']/fraction,4)
        # State pairs use the same nominal size. Both keep their own complete
        # silhouette; larger open lids/door leaves are not squeezed to fit.
        profiles[sprite]=settings
        records.append({'id':sprite,'file':path,'canvas':list(im.size),'alpha_box':list(bounds),
                        'uses':usage[sprite],'examples':examples[sprite],**settings})
    if args.write_profiles:
        for name in ['backend/map_prop_sizes.json','frontend/src/map-prop-sizes.json']:
            (ROOT/name).write_text(json.dumps(profiles,indent=2)+'\n')
    else:
        saved=json.loads((ROOT/'backend/map_prop_sizes.json').read_text())
        for record in records:record.update(saved[record['id']])
    folder=ROOT/'staging-terrain/prop-size-audit';folder.mkdir(parents=True,exist_ok=True)
    (folder/'audit.json').write_text(json.dumps({'scenes':len(fixture),'objects':records},indent=2)+'\n')
    lines=['# Map prop size audit','',f'Checked {len(records)} registered non-modular sprites across {len(fixture)} isolated encounter previews. Architectural wall kits keep their existing joint calibration.','',
           'Footprints reserve logical cells. Fill is the maximum visible silhouette fraction within its art box; it does not stretch the PNG. Prepared/unseen assets are retained rather than deleted merely for zero fixture use.','',
           '| Sprite | Standard footprint | Visible fill | Preview references (incl. states) | Observed footprints |','| --- | --- | --- | --- | --- |']
    for r in records:
        observed=', '.join('x'.join(map(str,e['footprint']))+(' ('+e['size_variant']+')' if e.get('size_variant') else '') for e in r['examples']) or 'prepared / state art'
        lines.append(f"| {r['id']} | {'x'.join(map(str,r['footprint']))} | {r['fill']:.0%} | {r['uses']} | {observed} |")
    (ROOT/'docs/art/PROP_SIZE_AUDIT.md').write_text('\n'.join(lines)+'\n')
    # Honest grid preview: each card has metre/tile-like squares and the sprite
    # spans its declared footprint, so differing physical categories are visible.
    tile=48;cardw,cardh=240,210
    sheet=Image.new('RGB',(cardw*6,cardh*((len(records)+5)//6)),'#263129');draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(records):
        ox,oy=i%6*cardw,i//6*cardh
        for y in range(3):
            for x in range(4):draw.rectangle((ox+16+x*tile,oy+12+y*tile,ox+16+(x+1)*tile,oy+12+(y+1)*tile),outline='#55634d')
        w,h=r.get('art_span',r['footprint']);im=Image.open(ASSETS/r['file']).convert('RGBA')
        scale=min(w*tile/im.width,h*tile/im.height)*r['scale']
        im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)
        px,py=ox+16+(4*tile-im.width)//2,oy+12+(3*tile-im.height)//2
        sheet.paste(im,(px,py),im);draw.text((ox+8,oy+166),r['id'],fill='white')
        draw.text((ox+8,oy+184),f"{w}x{h} / {r['category']}",fill='#bccbb0')
    sheet.save(folder/'standard-size-gallery.jpg',quality=92)
    if args.retire_legacy:
        # Only root-level copies with a registered replacement are candidates.
        # Pilot comparison references and their open/closed partners stay live.
        keep={'treasure_chest_bronze_closed','treasure_chest_bronze_open','crate_closed','crate_open',
              'bound_barrels','campfire_lit','cut_log_pile','mossy_boulder','canvas_tent',
              'wooden_rescue_cage_closed','wooden_rescue_cage_open','palisade_straight','palisade_corner','oak_tree'}
        text_files=list((ROOT/'staging-terrain').rglob('*.html'))+list((ROOT/'staging-terrain').rglob('*.js'))
        references='\n'.join(f.read_text(encoding='utf-8',errors='ignore') for f in text_files)
        active_hashes={path:hashlib.sha256((ASSETS/path).read_bytes()).hexdigest() for path in set(registry.values())}
        archive=ROOT.parent/'fortcamp-art-archive/prop-audit-20261003'
        archive=archive.resolve()
        if not archive.is_relative_to(ROOT.parent.resolve()) or archive.is_relative_to(ROOT.resolve()):raise ValueError('Unsafe archive path')
        retired=[]
        for layer in ('props','structures'):
            for old in (ASSETS/layer).glob('*.png'):
                key=('structure:' if layer=='structures' else '')+old.stem
                replacement=registry.get(key)
                if not replacement or replacement==old.relative_to(ASSETS).as_posix() or old.stem in keep:continue
                url='/assets/combat-terrain/'+old.relative_to(ASSETS).as_posix()
                if url in references:continue
                target=archive/old.relative_to(ASSETS)
                if target.exists():raise ValueError(f'Archive already exists: {target}')
                target.parent.mkdir(parents=True,exist_ok=True)
                retired.append({'from':str(old.relative_to(ROOT)),'to':str(target),'bytes':old.stat().st_size,'replacement':replacement})
                shutil.move(str(old),str(target))
        for path,digest in active_hashes.items():
            if hashlib.sha256((ASSETS/path).read_bytes()).hexdigest()!=digest:raise ValueError(f'Active asset changed: {path}')
        if retired:
            (ROOT/'docs/art/PROP_CLEANUP_20261003.json').write_text(json.dumps({'archive':str(archive),'retired':retired,'style_reference_names_kept':sorted(keep)},indent=2)+'\n')
        print(f'Retired {len(retired)} obsolete runtime copies to {archive}; active sprites/style references retained.')
    print(f'Audited {len(records)} prop/state sprites across {len(fixture)} encounters.')

if __name__=='__main__':main()
