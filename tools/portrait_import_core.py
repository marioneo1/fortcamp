"""Safe, stable import helpers for generic portrait contact sheets."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import struct
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps

try:
    from .portrait_grid import detect_grid_bounds
except ImportError:  # Direct execution from the tools directory.
    from portrait_grid import detect_grid_bounds

ROOT = Path(__file__).resolve().parents[1]
POOL_ROOT = ROOT / "data" / "portrait_pools"
MANIFEST_PATH = POOL_ROOT / "import_manifest.json"
METADATA_PATH = POOL_ROOT / "portrait_metadata.json"
BACKUP_ROOT = ROOT / "data" / "portrait_audit" / "crop_backups"
STAGING_ROOT = ROOT / ".portrait_staging"
AUDIT_PATH = ROOT / "data" / "portrait_audit" / "portrait_analysis.json"
POOL_PATTERN = re.compile(
    r"[a-z0-9_]+_(?:male|female)(?:_(?:melee|ranged|worker|healer|magic|special))?"
)


def validate_pool(pool: str) -> None:
    if not POOL_PATTERN.fullmatch(pool):
        raise ValueError(
            "Pool names must end in _male or _female, optionally followed by "
            "_melee, _ranged, _worker, _healer, _magic, or _special"
        )


def staging_root() -> Path:
    """Choose fast staging on the same volume as the current pool root."""
    if STAGING_ROOT.drive.casefold() == POOL_ROOT.drive.casefold():
        return STAGING_ROOT
    return POOL_ROOT.parent / ".portrait_staging"


def normalized_sheet(path: Path) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).convert("RGB")


def pixel_digest(path: Path) -> str:
    """Hash decoded pixels so metadata/compression changes do not affect dedupe."""
    sheet = normalized_sheet(path)
    digest = hashlib.sha256()
    digest.update(struct.pack(">II", sheet.width, sheet.height))
    digest.update(sheet.mode.encode("ascii"))
    digest.update(sheet.tobytes())
    return digest.hexdigest()


def read_manifest() -> dict:
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("imports"), list):
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {"version": 1, "imports": []}


def write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = MANIFEST_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, MANIFEST_PATH)


def _clean_appearance(value: object) -> dict[str, str]:
    source = value if isinstance(value, dict) else {}
    limits = {
        "hair_color": 48, "hair_length": 48, "eye_color": 48,
        "skin_tone": 64, "build": 64, "distinctive_features": 240,
        "summary": 360,
    }
    return {
        field: " ".join(str(source.get(field, "")).strip().split())[:limit]
        for field, limit in limits.items()
    }


def read_metadata_registry() -> dict:
    try:
        payload = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"version": 1, "portraits": {}}
    portraits = payload.get("portraits", {}) if isinstance(payload, dict) else {}
    return {"version": 1, "portraits": portraits if isinstance(portraits, dict) else {}}


def write_metadata_registry(registry: dict) -> None:
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = METADATA_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, METADATA_PATH)


def sheet_metadata(sheet_path: Path, expected: int) -> list[dict[str, str]] | None:
    """Read an optional row-major companion named ``<sheet>.metadata.json``."""
    companion = sheet_path.with_suffix(".metadata.json")
    if not companion.is_file():
        return None
    try:
        payload = json.loads(companion.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid portrait metadata JSON: {companion.name}") from exc
    rows = payload.get("portraits") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or len(rows) != expected:
        raise ValueError(f"{companion.name} must contain exactly {expected} portrait entries in row-major order")
    return [_clean_appearance(row) for row in rows]


def is_imported(pool: str, digest: str, manifest: dict | None = None) -> bool:
    manifest = manifest or read_manifest()
    return any(
        entry.get("pool") == pool and entry.get("pixel_sha256") == digest
        for entry in manifest.get("imports", [])
    )


def refresh_entry(sheet_path: Path, pool: str, manifest: dict | None = None) -> dict | None:
    """Find the stable manifest entry represented by a source sheet."""
    sheet_path = Path(sheet_path)
    manifest = manifest or read_manifest()
    digest = pixel_digest(sheet_path)
    entries = [entry for entry in manifest.get("imports", []) if entry.get("pool") == pool]
    exact = [entry for entry in entries if entry.get("pixel_sha256") == digest]
    if len(exact) == 1:
        return exact[0]
    same_name = [entry for entry in entries if entry.get("source_name") == sheet_path.name]
    return same_name[0] if len(same_name) == 1 else None


def _render_cells(
    sheet: Image.Image,
    names: list[str],
    staging: Path,
    columns: int,
    rows: int,
    inset: float,
) -> tuple[list[int], list[int], dict]:
    x_bounds, y_bounds, evidence = detect_grid_bounds(sheet, columns, rows)
    for index, name in enumerate(names):
        row, column = divmod(index, columns)
        left, right = x_bounds[column], x_bounds[column + 1]
        top, bottom = y_bounds[row], y_bounds[row + 1]
        dx, dy = (right - left) * inset, (bottom - top) * inset
        cell = sheet.crop((
            round(left + dx), round(top + dy), round(right - dx), round(bottom - dy),
        ))
        # Keep an uncropped source alongside square presentation images.
        original = cell.copy()
        original.thumbnail((1200,1200),Image.Resampling.LANCZOS)
        original.save(staging / f"original-{name}", "WEBP", quality=90, method=0)
        full = ImageOps.fit(cell, (768, 768), Image.Resampling.LANCZOS, centering=(.5,.35))
        thumb = ImageOps.fit(cell, (192, 192), Image.Resampling.LANCZOS, centering=(.5,.35))
        full.save(staging / f"full-{name}", "WEBP", quality=90, method=0)
        thumb.save(staging / f"thumb-{name}", "WEBP", quality=84, method=0)
    return x_bounds, y_bounds, evidence


def mark_repaired_audit_records(pool: str, names: list[str]) -> int:
    if not AUDIT_PATH.is_file():
        return 0
    try:
        audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0
    changed = 0
    for name in names:
        record = audit.get("records", {}).get(f"generic:{pool}/{name}")
        if not record or record.get("crop", {}).get("severity") != "bad":
            continue
        record["crop"].update({
            "severity": "good", "flags": [], "suggestion": "", "proposal": "",
            "source_geometry_flags": [], "applied_fix": True,
        })
        changed += 1
    if changed:
        temporary = AUDIT_PATH.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temporary, AUDIT_PATH)
    return changed


def refresh_sheet(sheet_path: Path, pool: str) -> dict:
    """Rebuild one prior import in place while preserving its portrait IDs."""
    sheet_path = Path(sheet_path)
    validate_pool(pool)
    manifest = read_manifest()
    entry = refresh_entry(sheet_path, pool, manifest)
    if entry is None:
        raise ValueError("No unique previous import matches this pool and source filename")
    columns, rows = int(entry.get("columns", 5)), int(entry.get("rows", 4))
    inset = float(entry.get("inset", 0.025))
    names = list(entry.get("files", []))
    if len(names) != columns * rows:
        raise ValueError(f"The previous import tracks {len(names)} files; expected {columns * rows}")
    full_dir, thumb_dir = POOL_ROOT / pool / "full", POOL_ROOT / pool / "thumb"
    original_dir = POOL_ROOT / pool / "original"
    original_dir.mkdir(parents=True,exist_ok=True)
    targets = [directory / name for name in names for directory in (full_dir, thumb_dir)]
    missing = [path.name for path in targets if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Cannot safely repair; {len(missing)} tracked portrait files are missing")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = BACKUP_ROOT / f"generic_{pool}_{stamp}"
    backup.mkdir(parents=True)
    shutil.copy2(MANIFEST_PATH, backup / "import_manifest.json")
    previous_registry = read_metadata_registry()
    if METADATA_PATH.is_file():
        shutil.copy2(METADATA_PATH, backup / "portrait_metadata.json")
    for name in names:
        for kind, directory in (("full", full_dir), ("thumb", thumb_dir), ("original", original_dir)):
            if not (directory / name).is_file():continue
            destination = backup / kind
            destination.mkdir(exist_ok=True)
            shutil.copy2(directory / name, destination / name)
    print(f"[{pool}] Backup complete: {backup}", flush=True)

    sheet = normalized_sheet(sheet_path)
    metadata_rows = sheet_metadata(sheet_path, len(names))
    replaced: list[tuple[str, str]] = []
    try:
        stage_root = staging_root()
        stage_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="portrait-refresh-", dir=stage_root) as temporary:
            staging = Path(temporary)
            x_bounds, y_bounds, evidence = _render_cells(
                sheet, names, staging, columns, rows, inset,
            )
            print(f"[{pool}] Rendered {len(names)} full portraits and thumbnails.", flush=True)
            for name in names:
                for prefix, directory in (("full", full_dir), ("thumb", thumb_dir), ("original", original_dir)):
                    with Image.open(staging / f"{prefix}-{name}") as check:
                        expected = (768, 768) if prefix == "full" else (192, 192)
                        if prefix != "original" and check.size != expected:
                            raise ValueError(f"Generated {prefix} image for {name} has size {check.size}")
                    os.replace(staging / f"{prefix}-{name}", directory / name)
                    replaced.append((prefix, name))
        print(f"[{pool}] Installed refreshed files; updating the manifest.", flush=True)

        old_digest = entry.get("pixel_sha256")
        entry.update({
            "pixel_sha256": pixel_digest(sheet_path),
            "source_name": sheet_path.name,
            "source_path": str(sheet_path.resolve()),
            "grid_bounds": {"x": x_bounds, "y": y_bounds},
            "measured_dividers": sum(item["accepted"] for axis in evidence.values() for item in axis),
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        })
        if old_digest and old_digest != entry["pixel_sha256"]:
            entry["previous_pixel_sha256"] = old_digest
        if metadata_rows is not None:
            registry = json.loads(json.dumps(previous_registry))
            for name, appearance in zip(names, metadata_rows):
                if any(appearance.values()):
                    registry["portraits"][f"{pool}/{name}"] = appearance
            write_metadata_registry(registry)
        write_manifest(manifest)
        marked_fixed = mark_repaired_audit_records(pool, names)
        print(f"[{pool}] Manifest update complete.", flush=True)
    except Exception:
        for kind, name in replaced:
            directory = {"full":full_dir,"thumb":thumb_dir,"original":original_dir}[kind]
            saved = backup / kind / name
            if saved.is_file():shutil.copy2(saved, directory / name)
            else:(directory / name).unlink(missing_ok=True)
        if replaced:
            shutil.copy2(backup / "import_manifest.json", MANIFEST_PATH)
            if (backup / "portrait_metadata.json").is_file():
                shutil.copy2(backup / "portrait_metadata.json", METADATA_PATH)
        raise

    try:
        backup_label = str(backup.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        backup_label = str(backup)
    repair_log = {
        "pool": pool, "source": str(sheet_path.resolve()), "files": names,
        "grid_bounds": {"x": x_bounds, "y": y_bounds},
        "measured_dividers": entry["measured_dividers"],
        "backup": backup_label,
        "audit_records_cleared": marked_fixed,
    }
    (backup / "repair.json").write_text(json.dumps(repair_log, indent=2) + "\n", encoding="utf-8")
    return {"status": "refreshed", **repair_log}


def pool_count(pool: str) -> int:
    validate_pool(pool)
    return sum(1 for path in (POOL_ROOT / pool / "full").glob("*") if path.is_file())


def next_index(full_dir: Path, thumb_dir: Path, pool: str) -> int:
    numbers: list[int] = []
    pattern = re.compile(rf"{re.escape(pool)}_(\d+)\.webp")
    for directory in (full_dir, thumb_dir):
        for path in directory.glob(f"{pool}_*.webp"):
            match = pattern.fullmatch(path.name)
            if match:
                numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def import_sheet(
    sheet_path: Path,
    pool: str,
    *,
    columns: int = 5,
    rows: int = 4,
    inset: float = 0.025,
) -> dict:
    """Append a sheet in row-major order without replacing an existing asset."""
    sheet_path = Path(sheet_path)
    validate_pool(pool)
    if columns < 1 or rows < 1 or not 0 <= inset < 0.2:
        raise ValueError("Invalid grid dimensions or inset")
    digest = pixel_digest(sheet_path)
    manifest = read_manifest()
    if is_imported(pool, digest, manifest):
        return {"status": "duplicate", "pool": pool, "written": [], "digest": digest}

    full_dir = POOL_ROOT / pool / "full"
    thumb_dir = POOL_ROOT / pool / "thumb"
    original_dir = POOL_ROOT / pool / "original"
    full_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir.mkdir(parents=True, exist_ok=True)
    original_dir.mkdir(parents=True,exist_ok=True)
    sequence = next_index(full_dir, thumb_dir, pool)
    sheet = normalized_sheet(sheet_path)
    names = [f"{pool}_{sequence + index:03d}.webp" for index in range(columns * rows)]
    metadata_rows = sheet_metadata(sheet_path, len(names))
    previous_registry = read_metadata_registry()

    moved: list[Path] = []
    try:
        stage_root = staging_root()
        stage_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="portrait-import-", dir=stage_root) as temporary:
            staging = Path(temporary)
            x_bounds, y_bounds, grid_evidence = _render_cells(
                sheet, names, staging, columns, rows, inset,
            )

            targets = [directory / name for name in names for directory in (full_dir, thumb_dir)]
            if any(path.exists() for path in targets):
                raise FileExistsError("A generated portrait filename already exists; no files were changed")
            for name in names:
                for prefix, directory in (("full", full_dir), ("thumb", thumb_dir), ("original", original_dir)):
                    target = directory / name
                    os.replace(staging / f"{prefix}-{name}", target)
                    moved.append(target)

        manifest["imports"].append({
            "pool": pool,
            "pixel_sha256": digest,
            "source_name": sheet_path.name,
            "source_path": str(sheet_path.resolve()),
            "columns": columns,
            "rows": rows,
            "inset": inset,
            "grid_bounds": {"x": x_bounds, "y": y_bounds},
            "measured_dividers": sum(
                item["accepted"] for axis in grid_evidence.values() for item in axis
            ),
            "files": names,
            "imported_at": datetime.now(timezone.utc).isoformat(),
            "metadata_source": sheet_path.with_suffix(".metadata.json").name if metadata_rows is not None else None,
        })
        if metadata_rows is not None:
            registry = json.loads(json.dumps(previous_registry))
            for name, appearance in zip(names, metadata_rows):
                if any(appearance.values()):
                    registry["portraits"][f"{pool}/{name}"] = appearance
            write_metadata_registry(registry)
        write_manifest(manifest)
    except Exception:
        for path in moved:
            path.unlink(missing_ok=True)
        if metadata_rows is not None:
            write_metadata_registry(previous_registry)
        raise
    return {
        "status": "imported", "pool": pool, "written": names, "digest": digest,
        "metadata_written": sum(any(row.values()) for row in metadata_rows or []),
    }
