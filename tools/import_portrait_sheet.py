"""Split a generated portrait contact sheet into Fortcamp full/thumbnail assets."""
from __future__ import annotations

import argparse
from pathlib import Path

from portrait_import_core import import_sheet

ROOT = Path(__file__).resolve().parents[1]
POOL_ROOT = ROOT / "data" / "portrait_pools"

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path, help="Generated contact-sheet image")
    parser.add_argument("pool", help="Target folder name, such as goblin_female_melee")
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--inset", type=float, default=0.025, help="Fraction trimmed from every cell edge")
    args = parser.parse_args()
    result = import_sheet(
        args.sheet, args.pool, columns=args.columns, rows=args.rows, inset=args.inset,
    )
    if result["status"] == "duplicate":
        print(f"Skipped exact duplicate sheet for {args.pool}")
    else:
        print(f"Imported {len(result['written'])} portraits into {args.pool}")
        print(f"Full: {POOL_ROOT / args.pool / 'full'}")
        print(f"Thumb: {POOL_ROOT / args.pool / 'thumb'}")


if __name__ == "__main__":
    main()
