"""Shared image and metadata helpers for Champion portrait import tools."""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CHAMPION_ROOT = ROOT / "data" / "champion_portraits"
MANIFEST_PATH = CHAMPION_ROOT / "manifest.json"
SLUG_PATTERN = re.compile(r"[a-z0-9_]+")


def validate_slug(value: str, label: str) -> str:
    if not SLUG_PATTERN.fullmatch(value):
        raise ValueError(f"{label} may contain only lowercase letters, numbers, and underscores")
    return value


def variant_directory(champion_id: str, variant: str) -> Path:
    validate_slug(champion_id, "Champion ID")
    validate_slug(variant, "Variant")
    base = CHAMPION_ROOT / champion_id
    return base / "default" if variant == "default" else base / "expressions" / variant


def save_variant(image: Image.Image, champion_id: str, variant: str, replace: bool = False) -> tuple[Path, Path]:
    destination = variant_directory(champion_id, variant)
    full_path, thumb_path = destination / "full.webp", destination / "thumb.webp"
    if not replace and (full_path.exists() or thumb_path.exists()):
        raise FileExistsError(f"Portrait already exists for {champion_id}:{variant}; pass --replace to update it")
    destination.mkdir(parents=True, exist_ok=True)
    source = ImageOps.exif_transpose(image).convert("RGB")
    full = ImageOps.fit(source, (768, 768), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    thumb = ImageOps.fit(source, (192, 192), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    full_tmp, thumb_tmp = destination / ".full.tmp", destination / ".thumb.tmp"
    full.save(full_tmp, "WEBP", quality=90, method=6)
    thumb.save(thumb_tmp, "WEBP", quality=84, method=6)
    full_tmp.replace(full_path)
    thumb_tmp.replace(thumb_path)
    return full_path, thumb_path


def read_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        return {"version": 1, "champions": {}}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def write_manifest(manifest: dict) -> None:
    CHAMPION_ROOT.mkdir(parents=True, exist_ok=True)
    temporary = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(MANIFEST_PATH)


def record_variant(manifest: dict, champion_id: str, variant: str, **metadata: object) -> None:
    champions = manifest.setdefault("champions", {})
    record = champions.setdefault(champion_id, {})
    record.update({key: value for key, value in metadata.items() if value is not None})
    variants = set(record.get("variants", []))
    variants.add(variant)
    record["variants"] = sorted(variants, key=lambda value: (value != "default", value))


def available_variants(champion_id: str) -> list[str]:
    validate_slug(champion_id, "Champion ID")
    variants = []
    if (variant_directory(champion_id, "default") / "full.webp").is_file():
        variants.append("default")
    expressions = CHAMPION_ROOT / champion_id / "expressions"
    if expressions.is_dir():
        variants.extend(sorted(
            path.name for path in expressions.iterdir()
            if path.is_dir() and SLUG_PATTERN.fullmatch(path.name) and (path / "full.webp").is_file()
        ))
    return variants


def remove_variant(champion_id: str, variant: str) -> bool:
    """Delete one known variant and remove it from the central manifest."""
    destination = variant_directory(champion_id, variant)
    removed = False
    for filename in ("full.webp", "thumb.webp", ".full.tmp", ".thumb.tmp"):
        path = destination / filename
        if path.is_file():
            path.unlink()
            removed = True
    if destination.is_dir() and not any(destination.iterdir()):
        destination.rmdir()
    expressions = CHAMPION_ROOT / champion_id / "expressions"
    if expressions.is_dir() and not any(expressions.iterdir()):
        expressions.rmdir()

    manifest = read_manifest()
    record = manifest.get("champions", {}).get(champion_id)
    if record:
        record["variants"] = [name for name in record.get("variants", []) if name != variant]
        write_manifest(manifest)
    return removed
