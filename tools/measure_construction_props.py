"""Rebuild shared visible prop bounds; source artwork is never modified."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def main():
    assets = json.loads((ROOT / 'frontend/src/map-prop-art.json').read_text())
    bounds = {}
    for key, file in assets.items():
        path = ROOT / 'frontend/public/assets/combat-terrain' / file
        if not path.is_file():
            continue
        with Image.open(path) as source:
            image = source.convert('RGBA')
            box = image.getchannel('A').point(lambda alpha: 255 if alpha >= 32 else 0).getbbox()
            if box:
                bounds[key] = {'size': list(image.size), 'bounds': list(box)}
    target = ROOT / 'frontend/src/construction-prop-bounds.json'
    target.write_text(json.dumps(bounds, indent=2) + '\n', encoding='utf-8')
    print(f'Measured {len(bounds)} assets; wrote {target.name}')

if __name__ == '__main__':
    main()
