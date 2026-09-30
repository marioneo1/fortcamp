"""Split the approved 4x4 combat UI sheet into stable transparent assets."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


ASSET_NAMES = [
    "action_attack", "action_subdue", "action_throw", "action_move",
    "action_guard", "action_skill", "action_interact", "action_exit",
    "target_hostile", "target_throw", "target_friendly", "target_reachable",
    "frame_normal", "frame_active", "frame_boss", "frame_unconscious",
]


def split_sheet(source: Path, destination: Path, output_size: int = 512) -> list[Path]:
    image = Image.open(source).convert("RGBA")
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, name in enumerate(ASSET_NAMES):
        row, column = divmod(index, 4)
        left, right = round(column * image.width / 4), round((column + 1) * image.width / 4)
        top, bottom = round(row * image.height / 4), round((row + 1) * image.height / 4)
        cell = image.crop((left, top, right, bottom))
        # The generator left a few sparks just across horizontal cell edges.
        # They are outside the useful silhouette and would otherwise expand a
        # crop or leave a sliver from the following row.
        clean_bottom = round(cell.height * (.82 if row == 2 else .925 if row < 2 else 1))
        if clean_bottom < cell.height:
            cell.paste((0, 0, 0, 0), (0, clean_bottom, cell.width, cell.height))
        alpha = cell.getchannel("A")
        bounds = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
        if not bounds:
            raise ValueError(f"Cell {index + 1} ({name}) is empty")
        content = cell.crop(bounds)
        usable = round(output_size * .88)
        content.thumbnail((usable, usable), Image.Resampling.LANCZOS)
        output = Image.new("RGBA", (output_size, output_size), (0, 0, 0, 0))
        output.alpha_composite(content, ((output_size - content.width) // 2, (output_size - content.height) // 2))
        path = destination / f"{name}.png"
        output.save(path, optimize=True)
        written.append(path)
    for action in ("attack", "subdue", "throw"):
        source_icon = Image.open(destination / f"action_{action}.png").convert("RGBA")
        bounds = source_icon.getchannel("A").getbbox()
        cursor_icon = source_icon.crop(bounds) if bounds else source_icon
        cursor_icon.thumbnail((58, 58), Image.Resampling.LANCZOS)
        cursor = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        cursor.alpha_composite(cursor_icon, ((64 - cursor_icon.width) // 2, (64 - cursor_icon.height) // 2))
        cursor_path = destination / f"cursor_{action}.png"
        cursor.save(cursor_path, optimize=True)
        written.append(cursor_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    for path in split_sheet(args.source, args.destination):
        print(path)


if __name__ == "__main__":
    main()
