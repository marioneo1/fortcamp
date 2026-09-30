"""Check transparent padding around assets in a proportional sheet grid."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--columns", type=int, required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--minimum-margin", type=float, default=0.15)
    parser.add_argument("--alpha-threshold", type=int, default=8)
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGBA")
    alpha = image.getchannel("A")
    width, height = image.size
    failures: list[str] = []
    minimum_seen = 1.0

    for row in range(args.rows):
        top = round(row * height / args.rows)
        bottom = round((row + 1) * height / args.rows)
        for column in range(args.columns):
            left = round(column * width / args.columns)
            right = round((column + 1) * width / args.columns)
            cell = alpha.crop((left, top, right, bottom))
            mask = cell.point(lambda value: 255 if value > args.alpha_threshold else 0)
            bounds = mask.getbbox()
            if bounds is None:
                failures.append(f"r{row + 1}c{column + 1}: empty")
                continue
            x0, y0, x1, y1 = bounds
            cell_width, cell_height = cell.size
            margins = (x0 / cell_width, (cell_width - x1) / cell_width,
                       y0 / cell_height, (cell_height - y1) / cell_height)
            minimum_seen = min(minimum_seen, *margins)
            if min(margins) < args.minimum_margin:
                failures.append(
                    f"r{row + 1}c{column + 1}: margins "
                    f"L{margins[0]:.1%} R{margins[1]:.1%} "
                    f"T{margins[2]:.1%} B{margins[3]:.1%}"
                )

    print(f"image={width}x{height}; grid={args.columns}x{args.rows}")
    print(f"minimum observed cell-edge transparency={minimum_seen:.1%}")
    if failures:
        print(f"FAIL: {len(failures)} of {args.columns * args.rows} cells violate the requirement")
        print("\n".join(failures))
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
