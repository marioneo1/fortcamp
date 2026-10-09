"""Install retained animal portraits at a bounded runtime size; no generation/API calls."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('rat', 'rat_swarm', 'rat_boss', 'wolf', 'wolf_boss', 'bear',
         'bear_boss', 'boar', 'bat', 'giant_spider')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    output = ROOT / 'frontend/public/assets/animals-v1'
    # Validate all inputs before installing anything.
    for name in NAMES:
        with Image.open(args.source / f'{name}.png') as image:
            image.verify()
    output.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (5 * 256, 2 * 284), '#20231e')
    draw = ImageDraw.Draw(sheet)
    manifest = {}
    for index, name in enumerate(NAMES):
        with Image.open(args.source / f'{name}.png') as source:
            image = source.convert('RGB')
            image.thumbnail((512, 512), Image.Resampling.LANCZOS)
            image.save(output / f'{name}.png', optimize=True)
            manifest[name] = {'source': str(args.source / f'{name}.png'),
                              'runtime': f'/assets/animals-v1/{name}.png',
                              'size': list(image.size)}
            image.thumbnail((256, 256), Image.Resampling.LANCZOS)
            x, y = index % 5 * 256, index // 5 * 284
            sheet.paste(image, (x, y))
            draw.text((x + 10, y + 264), name.replace('_', ' ').title(), fill='white')
    sheet.save(output / 'preview.jpg', quality=90)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    cards = ''.join(f'<figure><img src="{n}.png"><figcaption>{n.replace("_", " ").title()}</figcaption></figure>' for n in NAMES)
    (output / 'preview.html').write_text('<!doctype html><meta charset="utf-8"><title>Fortcamp animal portraits</title>'
        '<style>body{background:#20231e;color:#eee;font:16px system-ui}main{display:flex;flex-wrap:wrap}'
        'figure{margin:12px}img{width:240px;height:240px;border-radius:50%}figcaption{text-align:center}</style>'
        '<h1>Animal portraits</h1><p>Rat, swarm and wolf are used in the audited E-rank encounters; others are future assets.</p><main>' + cards + '</main>', encoding='utf-8')
    print(f'Installed {len(NAMES)} portraits and circular-crop preview at {output}')


if __name__ == '__main__':
    main()
