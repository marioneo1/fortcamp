"""Recover the authored overhead packs and optionally install their versioned runtime library.

Run without flags to extract/audit and build the gallery. --install publishes the
validated selection and renderer registry; legacy art and game saves are untouched.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
from audit_catalogue_crops import source_icons, recovered_icon

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'docs/art/overhead_prop_manifest.json'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    destination = ROOT/'staging-terrain/overhead-props-v2'
    sprites = destination/'sprites'
    sprites.mkdir(parents=True, exist_ok=True)
    registry, recovered, report = {}, {}, []
    for pack in manifest['packs']:
        source = Image.open(ROOT/pack['source']).convert('RGBA')
        ordered, parts, labels = source_icons(source, manifest['columns'], manifest['rows'])
        if len(pack['ids']) != len(ordered):
            raise ValueError('Manifest count differs from recovered silhouettes')
        for sprite, part in zip(pack['ids'], ordered):
            selected = sprite in pack.get('install', pack['ids'])
            output = recovered_icon(source, part, parts, labels, size=384, padding=32)
            bounds = output.getbbox()
            if not bounds or min(bounds[0], bounds[1]) < 30 or max(bounds[2], bounds[3]) > 354:
                raise ValueError(f'{sprite}: missing sprite or unsafe normalized border')
            layer, name = ('structures', sprite.split(':',1)[1]) if sprite.startswith('structure:') else ('props', sprite)
            filename = sprite.replace(':','_')+'.png'
            output.save(sprites/filename, optimize=True)
            report.append({'id': sprite, 'pack': pack['name'], 'selected': selected, 'source_box': part['box'], 'bounds': bounds})
            if selected:
                if sprite in registry:
                    raise ValueError(f'Duplicate selected ID: {sprite}')
                registry[sprite] = f'{layer}/{manifest["version"]}/{name}.png'
                recovered[sprite] = output
    # All sheets are validated before any runtime files are written.
    if args.install:
        for sprite, file in registry.items():
            target = ROOT/'frontend/public/assets/combat-terrain'/file
            target.parent.mkdir(parents=True, exist_ok=True)
            recovered[sprite].save(target, optimize=True)
        (ROOT/'frontend/src/map-prop-art.json').write_text(json.dumps(registry, indent=2)+'\n', encoding='utf-8')
    (destination/'extraction.json').write_text(json.dumps({'installed': args.install, 'selected_count': len(registry), 'sprites': report}, indent=2)+'\n', encoding='utf-8')
    cards = []
    for sprite in registry:
        filename = sprite.replace(':','_')+'.png'
        cards.append(f'<figure><div style="--sprite:url(\'sprites/{filename}\')"></div><figcaption>{sprite.replace("structure:", "").replace("_", " ")}</figcaption></figure>')
    page = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fortcamp overhead props</title><style>
    *{box-sizing:border-box}body{margin:0;padding:24px;background:#192019;color:#e7e3cb;font:15px system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px}figure{margin:0;background:#293125;border:1px solid #5b664e;border-radius:8px;padding:10px}figure>div{aspect-ratio:1;background:url('/assets/combat-terrain/mega-terrain-tiles/dirt_pale_dry.png') center/cover;position:relative}figure>div:before{content:"";position:absolute;inset:0;background:var(--sprite) center/contain no-repeat;filter:drop-shadow(1px 2px 1px #17201244)}figcaption{text-transform:capitalize;padding:8px 0;font-size:12px}p{line-height:1.5;max-width:850px;color:#b8c4ac}
    </style></head><body><h1>Overhead map props</h1><p>Installed selection from the approved pilot and authored expansion packs. Original assets remain intact. Open/closed variants share gameplay footprints; visual source proportions are preserved. The alarm bell has active and disabled art.</p><main>'''+''.join(cards)+'''</main></body></html>'''
    (destination/'gallery.html').write_text(page, encoding='utf-8')
    print(json.dumps({'sprites': len(registry), 'installed': args.install, 'gallery': str(destination/'gallery.html')}))

if __name__ == '__main__':
    main()
