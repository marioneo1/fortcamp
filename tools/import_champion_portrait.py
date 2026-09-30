"""Add or replace one Champion's default portrait or expression variant."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from champion_portrait_io import read_manifest, record_variant, save_variant, validate_slug, write_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("champion_id")
    parser.add_argument("--variant", default="default", help="default, happy, angry, injured, victory, etc.")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    champion_id = validate_slug(args.champion_id, "Champion ID")
    variant = validate_slug(args.variant, "Variant")
    if not args.image.is_file():
        raise SystemExit(f"Image not found: {args.image}")
    with Image.open(args.image) as opened:
        full_path, thumb_path = save_variant(opened.copy(), champion_id, variant, replace=args.replace)
    manifest = read_manifest()
    record_variant(manifest, champion_id, variant)
    write_manifest(manifest)
    print(f"Imported {champion_id}:{variant}")
    print(f"Full: {full_path}")
    print(f"Thumb: {thumb_path}")


if __name__ == "__main__":
    main()

