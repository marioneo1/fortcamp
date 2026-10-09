"""Stable icon sheet assignments; add IDs without shifting existing cells."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.content import ITEMS
from backend.races import RACE_CATALOG


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract", type=Path, help="Extract an approved evenly divided sheet")
    parser.add_argument("--kind", choices=["items", "races"], default="items")
    parser.add_argument("--batch", type=int, default=1)
    args = parser.parse_args()
    folder = ROOT / "staging-ui" / "equipment-icons-v1"
    folder.mkdir(parents=True, exist_ok=True)
    path = ROOT / "docs" / "art" / "equipment_icon_manifest.json"
    manifest = json.loads(path.read_text()) if path.exists() else {"columns": 6, "rows": 6, "items": [], "races": []}
    manifest["layouts"] = {"items": [6, 6], "races": [7, 6]}
    for kind, ids in [("items", ITEMS), ("races", RACE_CATALOG)]:
        existing = {row["id"] for row in manifest[kind]}
        # The newer 5x4 sheet has its own stable assignments; never schedule its
        # installed items again into the legacy 6x6 sheets.
        external = ROOT / 'docs/art/FIELD_GEAR_V1_MANIFEST.json'
        if kind == 'items' and external.exists():
            existing.update(row['id'] for row in json.loads(external.read_text())['items'])
        for iid in ids:
            if iid not in existing:
                index = len(manifest[kind])
                slug = iid.lower().replace("-", "_").replace(" ", "_").replace("'", "")
                cols, rows = manifest["layouts"][kind]
                count = cols * rows
                manifest[kind].append({"id": iid, "batch": index // count + 1, "cell": index % count, "file": f"{slug}.png"})
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    rows = [row for row in manifest[args.kind] if row["batch"] == args.batch]
    columns, row_count = manifest["layouts"][args.kind]
    if not rows:
        raise SystemExit("No entries in this batch")
    if args.extract:
        from PIL import Image
        source = Image.open(args.extract).convert("RGBA")
        out = ROOT / "frontend" / "public" / "assets" / "catalogue" / args.kind
        out.mkdir(parents=True, exist_ok=True)
        conflicts = [out / row["file"] for row in rows if (out / row["file"]).exists()]
        if conflicts:
            raise SystemExit(f"Refusing to overwrite {conflicts[0]}; preserve existing icons before explicitly replacing a sheet")
        from tools.audit_catalogue_crops import source_icons,recovered_icon
        silhouettes,parts,labels=source_icons(source,columns,row_count,len(rows))
        for row in rows:
            target = out / row["file"]
            recovered_icon(source,silhouettes[row['cell']],parts,labels).save(target)
        print(f"Extracted {len(rows)} {args.kind} icons")
    else:
        specs = []
        for row in rows:
            item = ITEMS[row["id"]] if args.kind == "items" else {}
            specs.append(f"{row['cell'] + 1}. {item.get('name', row['id'])}: {item.get('description', 'distinctive race emblem, a recognizable species head or defining motif')}" )
        prompt = (f"Use case: stylized-concept. Asset type: fantasy RPG {args.kind} icon atlas. Create a NEW {columns * 256}x{row_count * 256} image, EXACTLY {columns} columns by {row_count} rows, {columns * row_count} equal square cells, read left to right then top to bottom. "
                  "Each object entirely contained inside its own mathematically equal cell, centered, with a 14% internal safety margin on every edge. No gaps, no lines, no separators, no labels, no lettering, no decorative frames. Actual transparent background. "
                  "Consistent hand-painted fantasy game item art, softly shaded dimensional objects, crisp silhouettes, warm restrained highlights, aged metal, rich cloth and wood, moderate detail readable at 64px, Ragnarok/Tree-of-Savior modern illustrated fantasy feeling without copying existing assets. "
                  "All icons have the SAME lighting, brushwork, scale and visual weight. One object per cell. Weapons diagonal bottom-left to top-right; accessory and armor objects centered. Do not show characters, hands or scenery. "
                  "Draw every entry in this EXACT cell order. Ignore functional descriptions except to inform the object design. Empty unused final cells remain fully transparent.\n" + "\n".join(specs))
        (folder / f"{args.kind}_batch_{args.batch:03d}_prompt.txt").write_text(prompt, encoding="utf-8")
        print(json.dumps({"prompt": prompt, "destination": str(folder / f"{args.kind}_batch_{args.batch:03d}.png")}))


if __name__ == "__main__":
    main()
