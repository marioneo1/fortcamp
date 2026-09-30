"""Extract combat UI assets from four independently cropped artwork rows."""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image


ASSET_NAMES = [
    "action_attack", "action_subdue", "action_throw", "action_move",
    "action_guard", "action_skill", "action_interact", "action_exit",
    "target_hostile", "target_throw", "target_friendly", "target_reachable",
    "frame_normal", "frame_active", "frame_boss", "frame_unconscious",
]


def remove_tiny_islands(image: Image.Image, threshold: int = 8) -> Image.Image:
    """Discard microscopic disconnected crop flecks while keeping real accents."""
    mask = image.getchannel("A").point(lambda value: 255 if value > threshold else 0)
    pixels = mask.load()
    width, height = mask.size
    seen = bytearray(width * height)
    components: list[list[tuple[int, int]]] = []
    for y in range(height):
        for x in range(width):
            offset = y * width + x
            if seen[offset] or not pixels[x, y]:
                continue
            seen[offset] = 1
            queue = deque([(x, y)])
            component: list[tuple[int, int]] = []
            while queue:
                current_x, current_y = queue.popleft()
                component.append((current_x, current_y))
                for next_y in range(max(0, current_y - 1), min(height, current_y + 2)):
                    for next_x in range(max(0, current_x - 1), min(width, current_x + 2)):
                        next_offset = next_y * width + next_x
                        if not seen[next_offset] and pixels[next_x, next_y]:
                            seen[next_offset] = 1
                            queue.append((next_x, next_y))
            components.append(component)
    if not components:
        return image
    minimum_area = max(12, round(max(map(len, components)) * .001))
    cleaned = image.copy()
    cleaned_pixels = cleaned.load()
    for component in components:
        if len(component) >= minimum_area:
            continue
        for x, y in component:
            red, green, blue, _ = cleaned_pixels[x, y]
            cleaned_pixels[x, y] = red, green, blue, 0
    return cleaned


def normalize(cell: Image.Image, name: str, output_size: int = 512) -> Image.Image:
    cell = remove_tiny_islands(cell.convert("RGBA"))
    bounds = cell.getchannel("A").point(lambda value: 255 if value > 8 else 0).getbbox()
    if not bounds:
        raise ValueError(f"Asset {name} is empty")
    content = cell.crop(bounds)
    # Image.thumbnail() never enlarges small source crops, which previously
    # left the artwork at roughly half the runtime canvas size.
    # Scale both axes by the same factor. Frames use the complete canvas while
    # action and target artwork retains a small amount of breathing room.
    usable = output_size if name.startswith("frame_") else round(output_size * .88)
    scale = min(usable / content.width, usable / content.height)
    content = content.resize(
        (max(1, round(content.width * scale)), max(1, round(content.height * scale))),
        Image.Resampling.LANCZOS,
    )
    output = Image.new("RGBA", (output_size, output_size), (0, 0, 0, 0))
    left = (output_size - content.width) // 2
    if name == "frame_active":
        left -= 7
    output.alpha_composite(content, (left, (output_size - content.height) // 2))
    return output


def split_rows(row_sources: list[Path], destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    index = 0
    for source in row_sources:
        row = Image.open(source).convert("RGBA")
        for column in range(4):
            left = round(column * row.width / 4)
            right = round((column + 1) * row.width / 4)
            name = ASSET_NAMES[index]
            path = destination / f"{name}.png"
            normalize(row.crop((left, 0, right, row.height)), name).save(path, optimize=True)
            written.append(path)
            index += 1
    for action in ("attack", "subdue", "throw"):
        icon = Image.open(destination / f"action_{action}.png").convert("RGBA")
        bounds = icon.getchannel("A").getbbox()
        icon = icon.crop(bounds) if bounds else icon
        icon = icon.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        # The sword silhouette reads much larger than the other two at the
        # same bounding-box size. Only it needs the deliberately small cursor.
        canvas_size, artwork_size = (40, 20) if action == "attack" else (64, 54)
        icon.thumbnail((artwork_size, artwork_size), Image.Resampling.LANCZOS)
        cursor = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        cursor.alpha_composite(icon, ((canvas_size - icon.width) // 2, (canvas_size - icon.height) // 2))
        path = destination / f"cursor_{action}.png"
        cursor.save(path, optimize=True)
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rows", nargs=4, type=Path, metavar="ROW")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    for path in split_rows(args.rows, args.destination):
        print(path)


if __name__ == "__main__":
    main()
