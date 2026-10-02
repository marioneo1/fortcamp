"""Extract an overhead pilot atlas and compare it on real game terrain; no saves touched."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from PIL import Image
from audit_catalogue_crops import source_icons, recovered_icon

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['treasure_chest_bronze_closed', 'treasure_chest_bronze_open',
         'crate_closed', 'bound_barrels', 'campfire_lit', 'cut_log_pile',
         'mossy_boulder', 'canvas_tent', 'structure:wooden_rescue_cage_closed',
         'structure:palisade_straight', 'structure:palisade_corner', 'oak_tree']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet', type=Path, default=ROOT / 'staging-terrain/overhead-props-v1/overhead_props_12_v1.png')
    args = parser.parse_args()
    source = Image.open(args.sheet).convert('RGBA')
    folder = ROOT / 'staging-terrain/overhead-props-v1'
    extracted = folder / 'sprites'
    extracted.mkdir(parents=True, exist_ok=True)
    ordered, parts, labels = source_icons(source, 4, 3)
    records, problems = [], []
    for i, name in enumerate(NAMES):
        row, col = divmod(i, 4)
        box = (round(col*source.width/4), round(row*source.height/3),
               round((col+1)*source.width/4), round((row+1)*source.height/3))
        cell = source.crop(box)
        # Ignore near-invisible alpha noise for boundary validation only. Preserve original pixels.
        alpha = cell.getchannel('A').point(lambda value: 255 if value >= 32 else 0)
        bounds = alpha.getbbox()
        if not bounds or bounds[0] <= 1 or bounds[1] <= 1 or bounds[2] >= cell.width-1 or bounds[3] >= cell.height-1:
            problems.append(name)
        filename = name.replace(':', '_')+'.png'
        recovered_icon(source, ordered[i], parts, labels, size=384, padding=32).save(extracted / filename, optimize=True)
        records.append({'id': name, 'file': filename, 'cell': list(box), 'visible_bounds': bounds,
                        'recovered_silhouette': ordered[i]['box']})
    (folder / 'extraction.json').write_text(json.dumps({'source': str(args.sheet), 'size': source.size,
        'columns': 4, 'rows': 3, 'sprites': records, 'boundary_warnings': problems}, indent=2)+'\n', encoding='utf-8')
    figures = []
    for record in records:
        name = record['id']
        layer, asset = ('structures', name.split(':')[1]) if ':' in name else ('props', name)
        old = f'/assets/combat-terrain/{layer}/{asset}.png'
        new = '/staging-terrain/overhead-props-v1/sprites/'+record['file']
        figures.append(f'<article><h3>{asset.replace("_", " ")}</h3><div class="pair"><figure><div class="sample old" style="--sprite:url(\'{old}\')"></div><figcaption>Existing</figcaption></figure><figure><div class="sample new" style="--sprite:url(\'{new}\')"></div><figcaption>Overhead pilot</figcaption></figure></div></article>')
    page = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Fortcamp overhead prop study</title><style>
    *{box-sizing:border-box}body{margin:0;background:#171d17;color:#e5e2cf;font:15px system-ui;padding:24px}h1{margin:0}p{color:#b4beac;max-width:850px;line-height:1.6}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px}article{background:#232b21;border:1px solid #4e5c43;border-radius:10px;padding:16px}h3{font-size:14px;text-transform:capitalize;margin:0 0 12px}.pair{display:flex;justify-content:center;gap:12px}figure{margin:0;flex:1;max-width:144px}figcaption{font-size:12px;text-align:center;padding:8px}.sample{aspect-ratio:1;position:relative;background-image:var(--ground);background-size:cover;border:1px solid #66734c}.sample:before{content:"";position:absolute;inset:0;background-image:var(--sprite);background-repeat:no-repeat;background-position:center;background-size:contain}.old:before{filter:drop-shadow(2px 4px 3px #0007)}.new:before{filter:drop-shadow(1px 1px .6px #141a1233)}nav{display:flex;gap:8px;margin:20px 0}button{padding:9px 18px;border:1px solid #7d9165;background:#303e29;color:#eee;cursor:pointer;border-radius:6px}button[aria-pressed=true]{background:#596e40}body{--ground:url('/assets/combat-terrain/mega-terrain-tiles/grass_short.png')}@media(max-width:500px){body{padding:12px}}
    </style></head><body><h1>Overhead props / world placement study</h1><p>The same painted ground beneath both versions. The pilot uses a steep overhead camera and short contact shadows. Original assets remain intact. The barrel study is one barrel; existing art is a pair. Palisades need a steeper camera in a later pass.</p><nav><button data-ground="grass" aria-pressed="true">Grass</button><button data-ground="dirt" aria-pressed="false">Dirt</button><button data-ground="stone" aria-pressed="false">Stone</button></nav><main>'''+''.join(figures)+'''</main><script>const grounds={grass:'grass_short',dirt:'dirt_pale_dry',stone:'castle_flagstone_varied'};document.querySelectorAll('button').forEach(b=>b.onclick=()=>{document.body.style.setProperty('--ground',`url('/assets/combat-terrain/mega-terrain-tiles/${grounds[b.dataset.ground]}.png')`);document.querySelectorAll('button').forEach(other=>other.setAttribute('aria-pressed',String(other===b)))})</script></body></html>'''
    (folder / 'preview.html').write_text(page, encoding='utf-8')
    subprocess.run([sys.executable, str(ROOT/'tools/build_gear_battle_preview.py')], check=True)
    battle_source = (ROOT/'staging-ui/equipment-icons-v1/battle-preview.js').read_text(encoding='utf-8')
    urls = {record['id']: '/staging-terrain/overhead-props-v1/sprites/'+record['file'] for record in records}
    battle_source += '\nconst overheadPilotURLs='+json.dumps(urls)+';\n'+'''
const originalPropStyle=paintedPropStyle;
window.propOverheadPreview=()=>{paintedPropStyle=sprite=>overheadPilotURLs[sprite]?`--battle-prop:url('${overheadPilotURLs[sprite]}');--prop-scale:100%;`:originalPropStyle(sprite);window.gearRender()};
window.propLegacyPreview=()=>{paintedPropStyle=originalPropStyle;window.gearRender()};
const studyControls=document.createElement('div');studyControls.style.cssText='position:fixed;left:24px;bottom:14px;z-index:999;display:flex;gap:8px;padding:10px;background:#182318;border:1px solid #8c9564;border-radius:8px';
studyControls.innerHTML='<button>Existing props</button><button>Overhead pilot</button><a href="preview.html" style="color:#dce9c3">Side-by-side study</a>';
studyControls.children[0].onclick=window.propLegacyPreview;studyControls.children[1].onclick=window.propOverheadPreview;document.body.append(studyControls);
window.propOverheadPreview();
'''
    (folder/'battle-preview.js').write_text(battle_source, encoding='utf-8')
    battle_page=(ROOT/'staging-ui/equipment-icons-v1/battle-preview.html').read_text(encoding='utf-8').replace('/staging-ui/equipment-icons-v1/battle-preview.js','/staging-terrain/overhead-props-v1/battle-preview.js')
    (folder/'battle-preview.html').write_text(battle_page, encoding='utf-8')
    print(json.dumps({'preview': str(folder / 'preview.html'), 'sprites': len(records), 'grid_cuts_recovered': problems}))

if __name__ == '__main__':
    main()
