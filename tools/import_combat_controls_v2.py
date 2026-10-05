"""Extract six evenly spaced cells from the approved painted command atlas."""
import argparse
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['ranged', 'magic', 'pointer', 'loading', 'unavailable', 'chain_hook']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('atlas', type=Path)
    args = parser.parse_args()
    staging = ROOT / 'staging-ui/combat-controls-v2'
    destination = ROOT / 'frontend/public/assets/combat-controls-v2'
    staging.mkdir(parents=True, exist_ok=True)
    destination.mkdir(parents=True, exist_ok=True)
    if args.atlas.resolve() != (staging / 'atlas.png').resolve():
        shutil.copy2(args.atlas, staging / 'atlas.png')
    atlas = Image.open(args.atlas).convert('RGBA')
    records = []
    for index, name in enumerate(NAMES):
        col, row = index % 3, index // 3
        bounds = (round(col * atlas.width / 3), round(row * atlas.height / 2),
                  round((col + 1) * atlas.width / 3), round((row + 1) * atlas.height / 2))
        cell = atlas.crop(bounds)
        # Crop transparent padding only; preserve the supplied artwork and alpha.
        bbox = cell.getchannel('A').point(lambda a: 255 if a > 12 else 0).getbbox()
        if not bbox:
            raise ValueError(f'Empty atlas cell: {name}')
        cropped = cell.crop(bbox)
        for size, suffix in [(256, ''), (32, '_cursor')]:
            art = cropped.copy()
            art.thumbnail((size - 4, size - 4), Image.Resampling.LANCZOS)
            square = Image.new('RGBA', (size, size))
            square.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
            square.save(destination / f'{name}{suffix}.png')
        records.append({'name': name, 'cell': bounds, 'alpha_bounds': bbox})
    (staging / 'crop_manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(f'Imported {len(records)} painted assets into {destination}')


if __name__ == '__main__':
    main()
