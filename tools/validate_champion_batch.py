"""Validate live Champion assets from one tracked contact-sheet batch."""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps

from portrait_grid import detect_grid_bounds

ROOT = Path(__file__).resolve().parents[1]
CHAMPION_ROOT = ROOT / "data" / "champion_portraits"
OUTPUT_ROOT = ROOT / "data" / "portrait_audit" / "validation"


def encoded_round_trip(image: Image.Image, size: tuple[int, int], quality: int) -> Image.Image:
    fitted = ImageOps.fit(image, size, Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    buffer = io.BytesIO()
    fitted.save(buffer, "WEBP", quality=quality, method=6)
    buffer.seek(0)
    with Image.open(buffer) as opened:
        return opened.convert("RGB")


def images_match(actual: Image.Image, expected: Image.Image) -> bool:
    return actual.size == expected.size and ImageChops.difference(actual, expected).getbbox() is None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Three-digit tracked batch number")
    args = parser.parse_args()
    batch = f"{int(args.batch):03d}"
    manifest = json.loads((CHAMPION_ROOT / "manifest.json").read_text(encoding="utf-8"))
    entries = [
        (champion_id, record) for champion_id, record in manifest.get("champions", {}).items()
        if str(record.get("source", {}).get("batch", "")) == batch
    ]
    entries.sort(key=lambda item: item[1].get("source", {}).get("cell", ""))
    if len(entries) != 16:
        raise SystemExit(f"Batch {batch} has {len(entries)} manifest entries; expected 16")

    problems: list[str] = []
    tiles: list[Image.Image] = []
    sheets: dict[str, tuple[Image.Image, list[int], list[int]]] = {}
    for champion_id, record in entries:
        directory = CHAMPION_ROOT / champion_id / "default"
        full_path, thumb_path = directory / "full.webp", directory / "thumb.webp"
        try:
            with Image.open(full_path) as opened:
                full = opened.convert("RGB")
            with Image.open(thumb_path) as opened:
                thumb_size = opened.size
        except (FileNotFoundError, OSError) as exc:
            problems.append(f"{champion_id}: unreadable asset ({exc})")
            continue
        if full.size != (768, 768):
            problems.append(f"{champion_id}: full size is {full.size}")
        if thumb_size != (192, 192):
            problems.append(f"{champion_id}: thumbnail size is {thumb_size}")

        source = record.get("source", {})
        sheet_name, cell = source.get("sheet"), source.get("cell", "")
        if sheet_name not in sheets:
            with Image.open(ROOT / "champions" / sheet_name) as opened:
                sheet = ImageOps.exif_transpose(opened).convert("RGB")
            x_bounds, y_bounds, _ = detect_grid_bounds(sheet, 4, 4)
            sheets[sheet_name] = (sheet, x_bounds, y_bounds)
        sheet, x_bounds, y_bounds = sheets[sheet_name]
        if source.get("grid_bounds") != {"x": x_bounds, "y": y_bounds}:
            problems.append(f"{champion_id}: manifest does not contain the measured grid bounds")
        row, column = int(cell[1]), int(cell[3])
        left, right = x_bounds[column - 1], x_bounds[column]
        top, bottom = y_bounds[row - 1], y_bounds[row]
        dx, dy = (right - left) * 0.015, (bottom - top) * 0.015
        source_cell = sheet.crop((
            round(left + dx), round(top + dy), round(right - dx), round(bottom - dy),
        ))
        expected_full = encoded_round_trip(source_cell, (768, 768), 90)
        expected_thumb = encoded_round_trip(source_cell, (192, 192), 84)
        with Image.open(thumb_path) as opened:
            thumb = opened.convert("RGB")
        if not images_match(full, expected_full):
            problems.append(f"{champion_id}: full portrait does not match the measured source crop")
        if not images_match(thumb, expected_thumb):
            problems.append(f"{champion_id}: thumbnail does not match the measured source crop")

        tile = ImageOps.fit(full, (240, 240), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (240, 270), "#111111")
        canvas.paste(tile, (0, 0))
        draw = ImageDraw.Draw(canvas)
        label = f"{record['source']['cell']}  {record.get('name', champion_id)}"
        draw.text((6, 247), label[:35], fill="#f3e6c9")
        tiles.append(canvas)

    montage = Image.new("RGB", (960, 1080), "#080808")
    for index, tile in enumerate(tiles):
        montage.paste(tile, ((index % 4) * 240, (index // 4) * 270))
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    montage_path = OUTPUT_ROOT / f"champion_batch_{batch}_live.jpg"
    montage.save(montage_path, quality=94)
    print(json.dumps({
        "batch": batch,
        "portraits": len(entries),
        "problems": problems,
        "montage": str(montage_path.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
