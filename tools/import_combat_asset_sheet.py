"""Import an exact edge-to-edge prop sheet into the permanent combat libraries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "frontend" / "public" / "assets" / "combat-terrain"


def rebuild_index(folder: Path, additions: dict[str, dict], source: str) -> None:
    index_path = folder / "index.json"
    existing = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    old_sprites = existing.get("sprites", {})
    sprites: dict[str, dict] = {}
    for image_path in sorted(folder.glob("*.png")):
        name = image_path.stem
        if name in additions:
            sprites[name] = additions[name]
        elif name in old_sprites:
            sprites[name] = old_sprites[name]
        else:
            with Image.open(image_path) as image:
                sprites[name] = {"file": image_path.name, "width": image.width, "height": image.height}
    payload = {key: value for key, value in existing.items() if key not in {"source", "columns", "rows", "sprites"}}
    payload["sources"] = sorted(set(existing.get("sources", [existing.get("source")]) + [source]) - {None})
    payload["sprites"] = sprites
    index_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    image = Image.open(args.sheet).convert("RGBA")
    columns, rows = int(manifest["columns"]), int(manifest["rows"])
    entries = manifest["entries"]
    output_size = int(manifest.get("output_size", 160))
    expected = (int(manifest["width"]), int(manifest["height"]))
    if image.size != expected:
        raise ValueError(f"Expected {expected[0]}x{expected[1]}; got {image.width}x{image.height}")
    if len(entries) != columns * rows:
        raise ValueError(f"Expected {columns * rows} entries; got {len(entries)}")

    additions: dict[str, dict[str, dict]] = {"props": {}, "structures": {}}
    for position, entry in enumerate(entries):
        row, column = divmod(position, columns)
        left = column * image.width // columns
        right = (column + 1) * image.width // columns
        top = row * image.height // rows
        bottom = (row + 1) * image.height // rows
        tile = image.crop((left, top, right, bottom))
        alpha = tile.getchannel("A").point(lambda value: 0 if value <= 8 else value)
        tile.putalpha(alpha)
        tile = tile.resize((output_size, output_size), Image.Resampling.LANCZOS)
        category, name = entry["category"], entry["name"]
        if category not in additions:
            raise ValueError(f"Unsupported category: {category}")
        destination = LIBRARY / category / f"{name}.png"
        destination.parent.mkdir(parents=True, exist_ok=True)
        tile.save(destination, optimize=True)
        additions[category][name] = {
            "file": destination.name,
            "row": row,
            "column": column,
            "width": output_size,
            "height": output_size,
            "source_library": args.sheet.stem,
        }

    for category, records in additions.items():
        rebuild_index(LIBRARY / category, records, args.sheet.name)
    print(f"Imported {len(entries)} combat assets at {output_size}x{output_size}")


if __name__ == "__main__":
    main()
