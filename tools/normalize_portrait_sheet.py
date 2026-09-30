"""Rebuild an uneven tracked portrait sheet as a uniform contact grid."""
from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

from portrait_grid import detect_grid_bounds
from portrait_import_core import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--cell-size", type=int, default=512)
    parser.add_argument("--inset", type=float, default=0.025)
    parser.add_argument(
        "--preserve-canvas", action="store_true",
        help="Keep the source canvas size and distribute equal rectangular cells across it",
    )
    args = parser.parse_args()
    sheet_path = args.sheet.resolve()
    with Image.open(sheet_path) as opened:
        source = ImageOps.exif_transpose(opened).convert("RGB")
    x_bounds, y_bounds, evidence = detect_grid_bounds(source, args.columns, args.rows)
    accepted = sum(item["accepted"] for axis in evidence.values() for item in axis)
    expected = args.columns + args.rows - 2
    if accepted != expected:
        raise SystemExit(f"Detected {accepted}/{expected} dividers; refusing to normalize an uncertain sheet")

    separator = 1
    if args.preserve_canvas:
        width, height = source.size
        usable_width = width - (args.columns - 1) * separator
        usable_height = height - (args.rows - 1) * separator
        cell_widths = [usable_width // args.columns] * args.columns
        cell_heights = [usable_height // args.rows] * args.rows
        for index in range(usable_width % args.columns):
            cell_widths[index] += 1
        for index in range(usable_height % args.rows):
            cell_heights[index] += 1
    else:
        cell_widths = [args.cell_size] * args.columns
        cell_heights = [args.cell_size] * args.rows
        width = sum(cell_widths) + (args.columns - 1) * separator
        height = sum(cell_heights) + (args.rows - 1) * separator
    paste_x = [sum(cell_widths[:index]) + index * separator for index in range(args.columns)]
    paste_y = [sum(cell_heights[:index]) + index * separator for index in range(args.rows)]
    normalized = Image.new("RGB", (width, height), "black")
    for row in range(args.rows):
        for column in range(args.columns):
            left, right = x_bounds[column], x_bounds[column + 1]
            top, bottom = y_bounds[row], y_bounds[row + 1]
            dx, dy = (right - left) * args.inset, (bottom - top) * args.inset
            cell = source.crop((
                round(left + dx), round(top + dy), round(right - dx), round(bottom - dy),
            ))
            square = ImageOps.fit(
                cell, (cell_widths[column], cell_heights[row]),
                Image.Resampling.LANCZOS, centering=(0.5, 0.35),
            )
            normalized.paste(square, (paste_x[column], paste_y[row]))

    backup_root = sheet_path.parent / "source_backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_root / f"{sheet_path.stem}_{stamp}{sheet_path.suffix.lower()}"
    shutil.copy2(sheet_path, backup)
    temporary = sheet_path.with_suffix(sheet_path.suffix + ".tmp")
    normalized.save(temporary, "PNG", optimize=True)
    os.replace(temporary, sheet_path)

    print(json.dumps({
        "sheet": str(sheet_path),
        "backup": str(backup),
        "old_size": list(source.size),
        "new_size": list(normalized.size),
        "old_x_bounds": x_bounds,
        "old_y_bounds": y_bounds,
        "portraits": args.columns * args.rows,
    }, indent=2))


if __name__ == "__main__":
    main()
