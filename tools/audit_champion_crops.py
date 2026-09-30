"""Measure Champion source-grid boundaries and propose corrected stable crops."""
from __future__ import annotations

import json
import os
from pathlib import Path

from PIL import Image, ImageOps

from portrait_grid import detect_grid_bounds

ROOT = Path(__file__).resolve().parents[1]
CHAMPION_ROOT = ROOT / "data" / "champion_portraits"
AUDIT_PATH = ROOT / "data" / "portrait_audit" / "portrait_analysis.json"
GEOMETRY_PATH = ROOT / "data" / "portrait_audit" / "champion_crop_geometry.json"
PROPOSAL_ROOT = ROOT / "data" / "portrait_audit" / "proposed_champion_recrops"


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def save_proposal(sheet: Image.Image, bounds_x: list[int], bounds_y: list[int], row: int, column: int, champion_id: str) -> tuple[Path, Path]:
    left, right = bounds_x[column - 1], bounds_x[column]
    top, bottom = bounds_y[row - 1], bounds_y[row]
    dx, dy = (right - left) * 0.015, (bottom - top) * 0.015
    cell = sheet.crop((round(left + dx), round(top + dy), round(right - dx), round(bottom - dy)))
    full = ImageOps.fit(cell, (768, 768), Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    thumb = ImageOps.fit(cell, (192, 192), Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    destination = PROPOSAL_ROOT / champion_id
    destination.mkdir(parents=True, exist_ok=True)
    full_path, thumb_path = destination / "full.webp", destination / "thumb.webp"
    full.save(full_path, "WEBP", quality=90, method=6)
    thumb.save(thumb_path, "WEBP", quality=84, method=6)
    return full_path, thumb_path


def main() -> None:
    manifest = json.loads((CHAMPION_ROOT / "manifest.json").read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    geometry = {"version": 1, "batches": {}, "affected": {}, "fixed": {}}
    sheets: dict[str, tuple[Image.Image, list[int], list[int]]] = {}

    for record in manifest.get("champions", {}).values():
        source = record.get("source", {})
        filename = source.get("sheet")
        if not filename or filename in sheets:
            continue
        path = ROOT / "champions" / filename
        image = Image.open(path).convert("RGB")
        bounds_x, bounds_y, evidence = detect_grid_bounds(image, 4, 4)
        x_evidence, y_evidence = evidence["x"], evidence["y"]
        sheets[filename] = (image, bounds_x, bounds_y)
        geometry["batches"][filename] = {
            "width": image.width, "height": image.height,
            "x_bounds": bounds_x, "y_bounds": bounds_y,
            "x_evidence": x_evidence, "y_evidence": y_evidence,
        }

    affected = 0
    for champion_id, manifest_record in manifest.get("champions", {}).items():
        source = manifest_record.get("source", {})
        filename, cell = source.get("sheet"), source.get("cell", "")
        if filename not in sheets or not cell.startswith("R"):
            continue
        row, column = int(cell[1]), int(cell[3])
        image, bounds_x, bounds_y = sheets[filename]
        equal_height = image.height / 4
        importer_top = (row - 1) * equal_height + equal_height * 0.015
        importer_bottom = row * equal_height - equal_height * 0.015
        actual_top, actual_bottom = bounds_y[row - 1], bounds_y[row]
        flags: list[str] = []
        lost_top = max(0, round(importer_top - (actual_top + (actual_bottom - actual_top) * 0.015)))
        divider_inside = row < 4 and actual_bottom - 1 < importer_bottom - 2
        if divider_inside:
            flags.extend(["source_grid_boundary_bleed", "neighboring_cell_visible"])
        if row == 4 and lost_top >= 6:
            flags.extend(["wrong_source_row_bounds", "head_area_lost"])
        if not flags:
            continue
        stored_bounds = source.get("grid_bounds", {})
        if stored_bounds.get("x") == bounds_x and stored_bounds.get("y") == bounds_y:
            key = f"champion:{champion_id}/default"
            audit_record = audit.get("records", {}).get(key)
            if audit_record:
                audit_record["crop"].update({
                    "severity": "good", "flags": [], "suggestion": "", "proposal": "",
                    "source_geometry_flags": [], "applied_fix": True,
                })
            geometry["fixed"][champion_id] = {
                "batch": source.get("batch"), "sheet": filename, "cell": cell,
                "grid_bounds": stored_bounds,
            }
            continue
        full_path, _ = save_proposal(image, bounds_x, bounds_y, row, column, champion_id)
        proposal = str(full_path.relative_to(ROOT)).replace("\\", "/")
        key = f"champion:{champion_id}/default"
        audit_record = audit.get("records", {}).get(key)
        if audit_record:
            audit_record["crop"].update({
                "severity": "bad", "flags": flags,
                "suggestion": "Use the boundary-aware source-sheet recrop; it removes neighboring-cell bleed and restores the intended cell framing.",
                "proposal": proposal, "source_geometry_flags": flags, "applied_fix": False,
            })
        geometry["affected"][champion_id] = {
            "batch": source.get("batch"), "sheet": filename, "cell": cell,
            "flags": flags, "lost_top_pixels": lost_top,
            "current_import_y": [round(importer_top), round(importer_bottom)],
            "detected_source_y": [actual_top, actual_bottom], "proposal": proposal,
        }
        affected += 1

    for image, _, _ in sheets.values():
        image.close()
    atomic_json(AUDIT_PATH, audit)
    atomic_json(GEOMETRY_PATH, geometry)
    print(f"Measured {len(sheets)} Champion sheets; created {affected} boundary-aware recrop proposals.")


if __name__ == "__main__":
    main()
