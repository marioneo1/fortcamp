"""Split tracked 4x4 Champion sheets into stable default portrait assets."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageOps

from champion_portrait_io import ROOT, read_manifest, record_variant, save_variant, write_manifest
from portrait_grid import detect_grid_bounds


TRACKER = ROOT / "CHAMPION_PORTRAIT_TRACKER.md"
HEADING = re.compile(r"^#{2,3} Batch (\d{3}) — `([^`]+)`$", re.MULTILINE)
ROW = re.compile(r"\| (R([1-4])C([1-4])) \| `([a-z0-9_]+)` \| (.*?) \| (.*?) \|")


def tracked_batches() -> list[dict]:
    text = TRACKER.read_text(encoding="utf-8")
    headings = list(HEADING.finditer(text))
    batches = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.end():end]
        cells = []
        for row in ROW.finditer(section):
            cell, row_number, column_number, champion_id, name, series = row.groups()
            cells.append({
                "cell": cell, "row": int(row_number), "column": int(column_number),
                "id": champion_id, "name": name, "series": series.replace("\\|", "|"),
            })
        if len(cells) != 16:
            raise ValueError(f"Batch {heading.group(1)} has {len(cells)} tracked cells; expected 16")
        batches.append({"number": heading.group(1), "filename": heading.group(2), "cells": cells})
    return batches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", action="append", help="Import only this three-digit batch number; repeat as needed")
    parser.add_argument("--inset", type=float, default=0.015, help="Fraction trimmed from every cell edge")
    parser.add_argument("--replace", action="store_true", help="Replace existing default portraits")
    args = parser.parse_args()
    if not 0 <= args.inset < 0.2:
        raise SystemExit("Inset must be between 0 and 0.2")
    selected = {f"{int(value):03d}" for value in args.batch} if args.batch else None
    batches = [batch for batch in tracked_batches() if selected is None or batch["number"] in selected]
    if selected and selected != {batch["number"] for batch in batches}:
        raise SystemExit("One or more requested batches were not found in the tracker")

    manifest = read_manifest()
    imported = 0
    for batch in batches:
        sheet_path = ROOT / "champions" / batch["filename"]
        if not sheet_path.is_file():
            raise FileNotFoundError(f"Missing Champion sheet: {sheet_path}")
        with Image.open(sheet_path) as opened:
            sheet = ImageOps.exif_transpose(opened).convert("RGB")
        x_bounds, y_bounds, grid_evidence = detect_grid_bounds(sheet, 4, 4)
        for entry in batch["cells"]:
            left, right = x_bounds[entry["column"] - 1], x_bounds[entry["column"]]
            top, bottom = y_bounds[entry["row"] - 1], y_bounds[entry["row"]]
            cell_width, cell_height = right - left, bottom - top
            dx, dy = cell_width * args.inset, cell_height * args.inset
            crop = sheet.crop((
                round(left + dx), round(top + dy),
                round(right - dx), round(bottom - dy),
            ))
            save_variant(crop, entry["id"], "default", replace=args.replace)
            record_variant(
                manifest, entry["id"], "default", name=entry["name"], series=entry["series"],
                source={
                    "batch": batch["number"], "sheet": batch["filename"], "cell": entry["cell"],
                    "grid_bounds": {"x": x_bounds, "y": y_bounds},
                },
            )
            imported += 1
        measured = sum(item["accepted"] for axis in grid_evidence.values() for item in axis)
        print(f"Imported Batch {batch['number']}: {len(batch['cells'])} portraits ({measured}/6 measured dividers)")
    write_manifest(manifest)
    print(f"Imported {imported} Champion portraits into {ROOT / 'data' / 'champion_portraits'}")


if __name__ == "__main__":
    main()
