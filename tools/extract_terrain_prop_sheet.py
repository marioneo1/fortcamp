"""Extract the stable cells from the painted terrain-prop master sheet."""

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

    image = Image.open(args.sheet).convert("RGBA")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    columns = int(manifest["columns"])
    rows = int(manifest["rows"])
    names = manifest["reading_order"]
    if len(names) != columns * rows:
        raise ValueError(f"Manifest has {len(names)} names for a {columns}x{rows} sheet")

    args.output.mkdir(parents=True, exist_ok=True)
    index: dict[str, dict[str, int | str]] = {}
    for index_number, name in enumerate(names):
        row, column = divmod(index_number, columns)
        left = round(column * image.width / columns)
        right = round((column + 1) * image.width / columns)
        top = round(row * image.height / rows)
        bottom = round((row + 1) * image.height / rows)
        destination = args.output / f"{name}.png"
        image.crop((left, top, right, bottom)).save(destination, optimize=True)
        index[name] = {
            "file": destination.name,
            "row": row,
            "column": column,
            "width": right - left,
            "height": bottom - top,
        }

    (args.output / "index.json").write_text(
        json.dumps({"source": args.sheet.name, "columns": columns, "rows": rows, "sprites": index}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Extracted {len(names)} terrain props to {args.output}")


if __name__ == "__main__":
    main()
