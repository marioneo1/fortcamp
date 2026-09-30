"""Extract the evenly spaced cells from a guided painted mega tileset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    image = Image.open(args.sheet).convert("RGBA")
    columns, rows = int(manifest["columns"]), int(manifest["rows"])
    names = manifest["reading_order"]
    inset = int(manifest.get("crop_inset", 0))
    if image.size != (int(manifest["width"]), int(manifest["height"])):
        raise ValueError(f"Expected {manifest['width']}x{manifest['height']}; got {image.size}")
    if len(names) != columns * rows:
        raise ValueError(f"Expected {columns * rows} names; got {len(names)}")

    args.output.mkdir(parents=True, exist_ok=True)
    index: dict[str, dict[str, int | str]] = {}
    for position, name in enumerate(names):
        row, column = divmod(position, columns)
        cell_left = round(column * image.width / columns)
        cell_right = round((column + 1) * image.width / columns)
        cell_top = round(row * image.height / rows)
        cell_bottom = round((row + 1) * image.height / rows)
        box = (cell_left + inset, cell_top + inset, cell_right - inset, cell_bottom - inset)
        tile = image.crop(box)
        destination = args.output / f"{name}.png"
        tile.save(destination, optimize=True)
        index[name] = {"file": destination.name, "row": row, "column": column,
                       "width": tile.width, "height": tile.height}

    (args.output / "index.json").write_text(
        json.dumps({"source": args.sheet.name, "crop_inset": inset, "sprites": index}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Extracted {len(names)} tiles to {args.output}; each is {tile.width}x{tile.height}")


if __name__ == "__main__":
    main()
