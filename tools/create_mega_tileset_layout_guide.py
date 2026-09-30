"""Create an exact 12x8 edge-to-edge layout guide without separators."""

from pathlib import Path

from PIL import Image, ImageDraw


COLUMNS = 12
ROWS = 8
CELL = 128


def main() -> None:
    output = Path("staging-terrain/mega_tileset_12x8_layout_guide.png")
    backup = output.with_name("mega_tileset_12x8_magenta_separator_backup.png")
    if output.exists() and not backup.exists():
        backup.write_bytes(output.read_bytes())

    image = Image.new("RGB", (COLUMNS * CELL, ROWS * CELL))
    draw = ImageDraw.Draw(image)
    colors = ((34, 35, 40), (43, 44, 49))
    for row in range(ROWS):
        for column in range(COLUMNS):
            left, top = column * CELL, row * CELL
            draw.rectangle(
                (left, top, left + CELL - 1, top + CELL - 1),
                fill=colors[(row + column) % 2],
            )

    image.save(output, optimize=True)
    print(f"Wrote edge-to-edge guide: {output} ({image.width}x{image.height})")
    print(f"Grid: {COLUMNS}x{ROWS}; cells: {CELL}x{CELL}; gaps: 0px")
    print(f"Preserved the separator experiment: {backup}")


if __name__ == "__main__":
    main()
