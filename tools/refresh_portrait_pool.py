"""Repair one prior generic portrait-pool import without changing its IDs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from portrait_import_core import refresh_sheet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path, help="Original or edited 5x4 contact sheet")
    parser.add_argument("--pool", required=True, help="Existing canonical portrait pool name")
    args = parser.parse_args()
    print(json.dumps(refresh_sheet(args.sheet, args.pool), indent=2))


if __name__ == "__main__":
    main()
