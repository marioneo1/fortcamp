"""Back up, boundary-recrop, and validate one 4x4 Champion batch."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAMPION_ROOT = ROOT / "data" / "champion_portraits"
BACKUP_ROOT = ROOT / "data" / "portrait_audit" / "crop_backups"


def batch_entries(batch: str) -> list[tuple[str, dict]]:
    manifest = json.loads((CHAMPION_ROOT / "manifest.json").read_text(encoding="utf-8"))
    entries = [
        (champion_id, record) for champion_id, record in manifest.get("champions", {}).items()
        if str(record.get("source", {}).get("batch", "")) == batch
    ]
    entries.sort(key=lambda item: item[1].get("source", {}).get("cell", ""))
    return entries


def restore(entries: list[tuple[str, dict]], backup: Path) -> None:
    for champion_id, _ in entries:
        source = backup / champion_id
        destination = CHAMPION_ROOT / champion_id / "default"
        for filename in ("full.webp", "thumb.webp"):
            shutil.copy2(source / filename, destination / filename)
    shutil.copy2(backup / "manifest.json", CHAMPION_ROOT / "manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Three-digit Champion batch number")
    parser.add_argument("--dry-run", action="store_true", help="List the batch without changing files")
    args = parser.parse_args()
    batch = f"{int(args.batch):03d}"
    entries = batch_entries(batch)
    if len(entries) != 16:
        raise SystemExit(f"Batch {batch} has {len(entries)} tracked portraits; expected 16")
    print(f"Batch {batch}: " + ", ".join(record.get("name", champion_id) for champion_id, record in entries))
    if args.dry_run:
        print("Dry run only; no files changed.")
        return

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"batch_{batch}_{stamp}"
    backup.mkdir(parents=True)
    shutil.copy2(CHAMPION_ROOT / "manifest.json", backup / "manifest.json")
    for champion_id, _ in entries:
        source = CHAMPION_ROOT / champion_id / "default"
        destination = backup / champion_id
        destination.mkdir()
        for filename in ("full.webp", "thumb.webp"):
            shutil.copy2(source / filename, destination / filename)

    try:
        subprocess.run([
            sys.executable, str(ROOT / "tools" / "import_champion_sheets.py"),
            "--batch", batch, "--replace",
        ], cwd=ROOT, check=True)
        subprocess.run([
            sys.executable, str(ROOT / "tools" / "validate_champion_batch.py"),
            "--batch", batch,
        ], cwd=ROOT, check=True)
    except Exception:
        restore(entries, backup)
        print(f"Repair failed; the original Batch {batch} files were restored from {backup}")
        raise

    log = {
        "batch": batch,
        "applied_at": datetime.now().astimezone().isoformat(),
        "backup": str(backup.relative_to(ROOT)).replace("\\", "/"),
        "champions": [champion_id for champion_id, _ in entries],
        "validation_montage": f"data/portrait_audit/validation/champion_batch_{batch}_live.jpg",
    }
    (backup / "repair.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print(f"Batch {batch} repaired and validated. Backup: {backup}")


if __name__ == "__main__":
    main()
