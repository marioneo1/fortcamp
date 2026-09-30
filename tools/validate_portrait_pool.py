"""Validate and preview one live generic portrait pool against its source sheet."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from portrait_import_core import (
    POOL_ROOT, ROOT, _render_cells, normalized_sheet,
    read_manifest, refresh_entry, staging_root,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--pool", required=True)
    args = parser.parse_args()
    manifest = read_manifest()
    entry = refresh_entry(args.sheet, args.pool, manifest)
    if entry is None:
        raise SystemExit("No unique prior import matches this sheet and pool")
    columns, rows = int(entry["columns"]), int(entry["rows"])
    inset, names = float(entry["inset"]), list(entry["files"])
    sheet = normalized_sheet(args.sheet)
    problems: list[str] = []
    tiles: list[Image.Image] = []
    stage_root = staging_root()
    stage_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pool-validation-", dir=stage_root) as temporary:
        staging = Path(temporary)
        x_bounds, y_bounds, _ = _render_cells(sheet, names, staging, columns, rows, inset)
        if entry.get("grid_bounds") != {"x": x_bounds, "y": y_bounds}:
            problems.append("manifest grid bounds do not match the measured source sheet")
        for index, name in enumerate(names):
            full_path = POOL_ROOT / args.pool / "full" / name
            thumb_path = POOL_ROOT / args.pool / "thumb" / name
            expected_full = staging / f"full-{name}"
            expected_thumb = staging / f"thumb-{name}"
            if not full_path.is_file() or full_path.read_bytes() != expected_full.read_bytes():
                problems.append(f"{name}: full portrait does not match its measured source crop")
                continue
            if not thumb_path.is_file() or thumb_path.read_bytes() != expected_thumb.read_bytes():
                problems.append(f"{name}: thumbnail does not match its measured source crop")
            with Image.open(full_path) as opened:
                tile = ImageOps.fit(opened.convert("RGB"), (190, 190), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (190, 216), "#111111")
            canvas.paste(tile, (0, 0))
            ImageDraw.Draw(canvas).text((5, 196), f"{index + 1:02d}  {Path(name).stem[-3:]}", fill="#f3e6c9")
            tiles.append(canvas)

    montage = Image.new("RGB", (columns * 190, rows * 216), "#080808")
    for index, tile in enumerate(tiles):
        montage.paste(tile, ((index % columns) * 190, (index // columns) * 216))
    output = ROOT / "data" / "portrait_audit" / "validation" / f"pool_{args.pool}_live.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)
    montage.save(output, quality=94)
    print(json.dumps({
        "pool": args.pool, "portraits": len(names), "problems": problems,
        "montage": str(output.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
