"""Extract six evenly spaced cells from the approved painted command atlas."""
import argparse
import json
import shutil
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['ranged', 'magic', 'pointer', 'loading', 'unavailable', 'chain_hook']


def build_target_cursors(destination):
    """Normalize rendering direction and enlarge every existing target cursor 50%."""
    for name in ['attack', 'subdue', 'throw']:
        source = Image.open(ROOT / f'frontend/public/assets/combat-ui/cursor_{name}.png').convert('RGBA')
        source.resize((round(source.width*1.5), round(source.height*1.5)), Image.Resampling.LANCZOS).save(destination / f'{name}_cursor.png')
    for name in ['ranged', 'magic', 'chain_hook']:
        source = Image.open(destination / f'{name}.png').convert('RGBA')
        source = source.rotate(135, expand=True, resample=Image.Resampling.BICUBIC) if name == 'chain_hook' else ImageOps.mirror(source)
        source = source.crop(source.getchannel('A').point(lambda a: 255 if a > 12 else 0).getbbox())
        source.thumbnail((42, 42), Image.Resampling.LANCZOS)
        cursor = Image.new('RGBA', (48, 48))
        cursor.alpha_composite(source, ((48-source.width)//2, (48-source.height)//2))
        cursor.save(destination / f'{name}_cursor.png')


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
    build_target_cursors(destination)
    print(f'Imported {len(records)} painted assets into {destination}')


if __name__ == '__main__':
    main()
