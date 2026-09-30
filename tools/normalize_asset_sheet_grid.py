"""Repack a transparent generated sprite sheet onto an exact uniform grid."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def runs(values: list[int], minimum: int, minimum_width: int) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(values + [0]):
        if value >= minimum and start is None:
            start = index
        elif value < minimum and start is not None:
            if index - start >= minimum_width:
                found.append((start, index))
            start = None
    return found


def axis_counts(alpha: Image.Image, axis: str, threshold: int) -> list[int]:
    width, height = alpha.size
    if axis == "rows":
        return [sum(alpha.crop((0, y, width, y + 1)).histogram()[threshold + 1:]) for y in range(height)]
    return [sum(alpha.crop((x, 0, x + 1, height)).histogram()[threshold + 1:]) for x in range(width)]


def normalize(source_path: Path, output_path: Path, columns: int, rows: int,
              cell_size: int, object_ratio: float, alpha_threshold: int) -> None:
    source = Image.open(source_path).convert("RGBA")
    alpha = source.getchannel("A")
    source_width, source_height = source.size

    row_bands = runs(axis_counts(alpha, "rows", alpha_threshold), minimum=4, minimum_width=3)
    if len(row_bands) != rows:
        raise ValueError(f"Expected {rows} row bands, found {len(row_bands)}: {row_bands}")

    output = Image.new("RGBA", (columns * cell_size, rows * cell_size), (0, 0, 0, 0))
    target_longest = round(cell_size * object_ratio)
    report: list[str] = []

    for row_index, (top, bottom) in enumerate(row_bands):
        row_alpha = alpha.crop((0, top, source_width, bottom))
        fragments = runs(axis_counts(row_alpha, "columns", alpha_threshold), minimum=2, minimum_width=2)
        grouped: list[list[tuple[int, int]]] = [[] for _ in range(columns)]
        for left, right in fragments:
            center = (left + right) / 2
            slot = min(columns - 1, max(0, round(center / source_width * columns - 0.5)))
            grouped[slot].append((left, right))

        if any(not group for group in grouped):
            raise ValueError(f"Could not identify all {columns} sprites in row {row_index + 1}: {grouped}")

        for column_index, group in enumerate(grouped):
            left = min(part[0] for part in group)
            right = max(part[1] for part in group)
            candidate = source.crop((left, top, right, bottom))
            bounds = candidate.getchannel("A").getbbox()
            if bounds is None:
                raise ValueError(f"Empty sprite at row {row_index + 1}, column {column_index + 1}")
            sprite = candidate.crop(bounds)
            scale = target_longest / max(sprite.size)
            resized = sprite.resize(
                (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))),
                Image.Resampling.LANCZOS,
            )
            destination_x = column_index * cell_size + (cell_size - resized.width) // 2
            destination_y = row_index * cell_size + (cell_size - resized.height) // 2
            output.alpha_composite(resized, (destination_x, destination_y))
            report.append(
                f"r{row_index + 1:02}c{column_index + 1:02} "
                f"source=({left},{top})-({right},{bottom}) output={resized.width}x{resized.height}"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.save(output_path)
    report_path = output_path.with_suffix(".normalization.txt")
    report_path.write_text(
        f"source={source_path}\nsource_size={source_width}x{source_height}\n"
        f"output_size={output.width}x{output.height}\ngrid={columns}x{rows}\n"
        f"cell={cell_size}x{cell_size}\nfixed_longest_dimension={target_longest}\n\n" +
        "\n".join(report) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")
    print(f"Wrote {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--columns", type=int, required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--cell-size", type=int, default=160)
    parser.add_argument("--object-ratio", type=float, default=0.65)
    parser.add_argument("--alpha-threshold", type=int, default=8)
    args = parser.parse_args()
    normalize(args.source, args.output, args.columns, args.rows, args.cell_size,
              args.object_ratio, args.alpha_threshold)


if __name__ == "__main__":
    main()
