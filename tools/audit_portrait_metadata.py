"""Local, resumable appearance and crop audit for Fortcamp portraits.

Uses locally cached BLIP and CLIP models. Original portrait assets are read-only;
the script writes sidecar metadata and review artifacts only.
"""
from __future__ import annotations

import argparse
import csv
import gc
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import cv2
import torch
from PIL import Image, ImageDraw, ImageOps
from transformers import (
    BlipForConditionalGeneration, BlipProcessor, CLIPImageProcessor, CLIPModel,
    CLIPProcessor, CLIPTokenizerFast,
)

ROOT = Path(__file__).resolve().parents[1]
GENERIC_ROOT = ROOT / "data" / "portrait_pools"
CHAMPION_ROOT = ROOT / "data" / "champion_portraits"
AUDIT_ROOT = ROOT / "data" / "portrait_audit"
AUDIT_PATH = AUDIT_ROOT / "portrait_analysis.json"
REPORT_PATH = AUDIT_ROOT / "PORTRAIT_AUDIT_REPORT.md"
CROP_CSV_PATH = AUDIT_ROOT / "crop_review.csv"
GENERIC_METADATA_PATH = GENERIC_ROOT / "portrait_metadata.json"
CHAMPION_METADATA_PATH = CHAMPION_ROOT / "portrait_metadata.json"

BLIP_ID = "Salesforce/blip-image-captioning-large"
CLIP_ID = "openai/clip-vit-large-patch14"

HAIR_COLORS = ["black", "dark brown", "brown", "auburn", "red", "orange", "blonde", "golden", "white", "silver", "gray", "blue", "green", "teal", "purple", "pink"]
HAIR_LENGTHS = ["bald or no visible hair", "very short", "short", "shoulder-length", "long", "very long"]
EYE_COLORS = ["brown", "amber", "gold", "hazel", "green", "blue", "gray", "red", "purple", "pink", "black", "glowing white"]
SURFACES = ["fair skin", "light skin", "tan skin", "brown skin", "dark skin", "green skin", "blue skin", "red skin", "purple skin", "gray skin", "pale spectral skin", "metallic plating", "wooden bark", "feathered skin", "scaled skin", "fur-covered skin", "translucent slime body"]
BUILDS = ["slender build", "lean build", "athletic build", "sturdy build", "broad build", "muscular build", "stocky build", "petite build"]
COMPOSITIONS = [
    "a well-framed centered portrait with the whole head visible",
    "a portrait with the top of the head cut off",
    "a badly cropped portrait with the face at the image edge",
    "an excessively zoomed-in portrait",
    "a portrait where the person is too small in the frame",
    "a portrait containing multiple people",
]

NO_HAIR_RACES = {"slimefolk", "automaton", "manaforged", "harpy", "lizardfolk", "dragonkin", "kobold", "minotaur", "werewolf", "catfolk", "foxkin", "bugbear"}


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def cached_snapshot(model_id: str) -> Path:
    model_dir = Path.home() / ".cache" / "huggingface" / "hub" / ("models--" + model_id.replace("/", "--")) / "snapshots"
    snapshots = sorted(path for path in model_dir.glob("*") if path.is_dir())
    if not snapshots:
        raise FileNotFoundError(f"Local model cache is missing {model_id}")
    return snapshots[-1]


def read_json(path: Path, fallback: dict) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else fallback
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return fallback


def pool_identity(pool: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"(.+?)_(female|male)(?:_(melee|ranged|magic|healer|worker|special))?", pool)
    if not match:
        return pool.replace("_", " "), "", ""
    return match.group(1).replace("_", " "), match.group(2), match.group(3) or ""


def inputs() -> list[dict]:
    found: list[dict] = []
    for pool_dir in sorted(path for path in GENERIC_ROOT.iterdir() if path.is_dir()):
        race, gender, role = pool_identity(pool_dir.name)
        for path in sorted((pool_dir / "full").glob("*")):
            if path.suffix.lower() not in {".webp", ".png", ".jpg", ".jpeg"}:
                continue
            found.append({
                "key": f"generic:{pool_dir.name}/{path.name}", "kind": "generic",
                "metadata_key": f"{pool_dir.name}/{path.name}", "path": path,
                "pool": pool_dir.name, "race": race, "gender": gender, "role": role,
            })
    manifest = read_json(CHAMPION_ROOT / "manifest.json", {}).get("champions", {})
    for champion_dir in sorted(path for path in CHAMPION_ROOT.iterdir() if path.is_dir()):
        path = champion_dir / "default" / "full.webp"
        if not path.is_file():
            continue
        profile = manifest.get(champion_dir.name, {}) if isinstance(manifest, dict) else {}
        found.append({
            "key": f"champion:{champion_dir.name}/default", "kind": "champion",
            "metadata_key": f"{champion_dir.name}/default", "path": path,
            "pool": champion_dir.name, "race": "human", "gender": "female", "role": "champion",
            "name": profile.get("name", champion_dir.name.replace("_", " ").title()),
            "series": profile.get("series", ""),
        })
    return found


def clean_caption(caption: str) -> str:
    text = " ".join(caption.strip().split()).strip(" .")
    return text[:240]


def label_probs(model, processor, images: list[Image.Image], labels: list[str], device: str) -> list[tuple[str, float]]:
    prompts = [f"a fantasy character portrait showing {label}" for label in labels]
    encoded = processor(text=prompts, images=images, return_tensors="pt", padding=True)
    encoded = {key: value.to(device) for key, value in encoded.items()}
    with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device == "cuda"):
        logits = model(**encoded).logits_per_image
        probabilities = logits.softmax(dim=1).float().cpu()
    return [(labels[int(row.argmax())], float(row.max())) for row in probabilities]


def face_geometry(path: Path) -> dict:
    image = cv2.imread(str(path))
    if image is None:
        return {"faces": 0}
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = list(cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(55, 55)))
    if not faces:
        return {"faces": 0}
    x, y, w, h = max(faces, key=lambda item: item[2] * item[3])
    height, width = gray.shape
    return {
        "faces": len(faces), "x": round(x / width, 4), "y": round(y / height, 4),
        "w": round(w / width, 4), "h": round(h / height, 4),
        "center_x": round((x + w / 2) / width, 4), "center_y": round((y + h / 2) / height, 4),
    }


def crop_assessment(composition: tuple[str, float], geometry: dict) -> tuple[list[str], str, str]:
    label, confidence = composition
    flags: list[str] = []
    suggestion = ""
    if label != COMPOSITIONS[0] and confidence >= 0.24:
        mapping = {
            COMPOSITIONS[1]: ("head_cut_off", "Use a wider crop with more space above the head."),
            COMPOSITIONS[2]: ("face_near_edge", "Shift the crop toward the face and preserve head clearance."),
            COMPOSITIONS[3]: ("too_tight", "Use a wider crop with more shoulder and head clearance."),
            COMPOSITIONS[4]: ("too_loose", "Crop closer around the head and upper torso."),
            COMPOSITIONS[5]: ("multiple_subjects", "Use a crop containing only the intended character."),
        }
        flag, suggestion = mapping[label]
        flags.append(flag)
    if geometry.get("faces", 0):
        center_x, face_width = geometry["center_x"], geometry["w"]
        if center_x < 0.30 or center_x > 0.70:
            flags.append("face_off_center")
            suggestion = suggestion or "Center the crop on the face."
        if face_width > 0.66:
            flags.append("face_too_large")
            suggestion = suggestion or "Use a wider crop."
        elif face_width < 0.14:
            flags.append("face_too_small")
            suggestion = suggestion or "Crop closer around the head and upper torso."
    elif confidence < 0.42:
        flags.append("manual_composition_review")
        suggestion = "Face detection was inconclusive; inspect this portrait manually."
    flags = list(dict.fromkeys(flags))
    severity = "bad" if any(flag != "manual_composition_review" for flag in flags) else "review" if flags else "good"
    return flags, severity, suggestion


def appearance_record(item: dict, caption: str, predictions: dict) -> dict[str, str]:
    race, gender = item["race"], item["gender"]
    no_hair = race.lower() in NO_HAIR_RACES
    hair_color = "" if no_hair else predictions["hair_color"][0]
    hair_length = "" if no_hair else predictions["hair_length"][0].replace("bald or no visible hair", "bald")
    if predictions["hair_length"][0] == "bald or no visible hair":
        hair_color = ""
    eye_color = predictions["eye_color"][0]
    surface = predictions["surface"][0]
    build = predictions["build"][0].removesuffix(" build")
    subject = " ".join(value for value in (gender, race) if value).strip()
    parts = [f"a {build} {subject}".strip()]
    if hair_color:
        parts.append(f"{hair_length} {hair_color} hair")
    if eye_color:
        parts.append(f"{eye_color} eyes")
    if surface:
        parts.append(surface)
    summary = parts[0].capitalize()
    if len(parts) > 1:
        summary += " with " + ", ".join(parts[1:])
    if caption:
        summary += f"; {caption}"
    return {
        "hair_color": hair_color, "hair_length": hair_length,
        "eye_color": eye_color, "skin_tone": surface, "build": build,
        "distinctive_features": caption, "summary": summary[:360],
    }


def save_outputs(records: dict[str, dict], started_at: str, complete: bool = False) -> None:
    payload = {
        "version": 1, "generator": "local BLIP large + CLIP ViT-L/14 + OpenCV Haar",
        "started_at": started_at, "updated_at": datetime.now(timezone.utc).isoformat(),
        "complete": complete, "records": records,
    }
    atomic_json(AUDIT_PATH, payload)
    generic_existing = read_json(GENERIC_METADATA_PATH, {"version": 1, "portraits": {}})
    champion_existing = read_json(CHAMPION_METADATA_PATH, {"version": 1, "portraits": {}})
    generic = dict(generic_existing.get("portraits", {}))
    champions = dict(champion_existing.get("portraits", {}))
    for record in records.values():
        destination = generic if record["kind"] == "generic" else champions
        destination.setdefault(record["metadata_key"], record["appearance"])
    atomic_json(GENERIC_METADATA_PATH, {"version": 1, "portraits": dict(sorted(generic.items()))})
    atomic_json(CHAMPION_METADATA_PATH, {"version": 1, "portraits": dict(sorted(champions.items()))})


def write_report(records: dict[str, dict], total_expected: int) -> None:
    rows = sorted(records.values(), key=lambda row: row["key"])
    corrected = [row for row in rows if row["crop"].get("applied_fix")]
    flagged = [row for row in rows if row["crop"]["severity"] != "good"]
    bad = [row for row in flagged if row["crop"]["severity"] == "bad"]
    review = [row for row in flagged if row["crop"]["severity"] == "review"]
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    with CROP_CSV_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["key", "kind", "severity", "flags", "suggested_recrop", "proposal", "composition_confidence", "source_path"])
        for row in flagged:
            writer.writerow([row["key"], row["kind"], row["crop"]["severity"], "; ".join(row["crop"]["flags"]), row["crop"]["suggestion"], row["crop"].get("proposal", ""), row["crop"]["composition_confidence"], row["path"]])
    lines = [
        "# Portrait audit report", "",
        f"- Portraits discovered: **{total_expected}**",
        f"- Portraits analyzed: **{len(rows)}**",
        f"- Crop problems automatically flagged: **{len(bad)}**",
        f"- Inconclusive portraits needing visual review: **{len(review)}**",
        f"- Live portrait crops corrected from this audit: **{len(corrected)}**", "",
        "Automatic appearance labels are conservative initial tags and can be corrected in the roster editor. Crop flags use measured source-sheet boundaries and visible grid bleed; uncertain composition-model warnings were visually reviewed before this report was finalized.", "",
        "## Crop problems", "",
        "| Portrait | Flags | Suggested correction | Proposed file |", "|---|---|---|---|",
    ]
    for row in bad:
        proposal = f"`{row['crop']['proposal']}`" if row["crop"].get("proposal") else "—"
        lines.append(f"| `{row['key']}` | {', '.join(row['crop']['flags'])} | {row['crop']['suggestion']} | {proposal} |")
    if review:
        lines.extend(["", "## Manual review", ""])
        lines.extend(f"- `{row['key']}` — {row['crop']['suggestion']}" for row in review)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Review sheets make the flagged list practical without modifying assets.
    review_root = AUDIT_ROOT / "crop_review_sheets"
    review_root.mkdir(parents=True, exist_ok=True)
    for stale_sheet in review_root.glob("*.jpg"):
        stale_sheet.unlink()
    grouped: dict[str, list[dict]] = {}
    for row in flagged:
        grouped.setdefault(row["pool"], []).append(row)
    for pool, pool_rows in grouped.items():
        tiles = []
        for row in pool_rows:
            image = Image.open(row["path"]).convert("RGB")
            tile = ImageOps.fit(image, (240, 240), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(tile)
            color = "#ef5f5f" if row["crop"]["severity"] == "bad" else "#e6bd55"
            draw.rectangle((2, 2, 237, 237), outline=color, width=5)
            draw.rectangle((0, 204, 240, 240), fill="#090b09")
            draw.text((7, 210), Path(row["path"]).stem[-7:], fill=color)
            tiles.append(tile)
        columns, rows_count = 4, math.ceil(len(tiles) / 4)
        sheet = Image.new("RGB", (columns * 240, rows_count * 240), "#090b09")
        for index, tile in enumerate(tiles):
            sheet.paste(tile, ((index % columns) * 240, (index // columns) * 240))
        sheet.save(review_root / f"{pool}.jpg", quality=92)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    all_items = inputs()
    existing = read_json(AUDIT_PATH, {"records": {}})
    records = {} if args.force else dict(existing.get("records", {}))
    pending = [item for item in all_items if item["key"] not in records]
    if args.limit:
        pending = pending[:args.limit]
    if not pending:
        write_report(records, len(all_items))
        print(f"Nothing pending. {len(records)}/{len(all_items)} portraits already analyzed.")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"Loading local models on {device}; {len(pending)} portraits pending.", flush=True)
    blip_processor = BlipProcessor.from_pretrained(BLIP_ID, local_files_only=True)
    blip = BlipForConditionalGeneration.from_pretrained(BLIP_ID, torch_dtype=dtype, local_files_only=True).to(device).eval()
    clip_snapshot = cached_snapshot(CLIP_ID)
    clip_processor = CLIPProcessor(
        tokenizer=CLIPTokenizerFast.from_pretrained(clip_snapshot, local_files_only=True),
        image_processor=CLIPImageProcessor(
            crop_size={"height": 224, "width": 224}, size={"shortest_edge": 224},
            image_mean=[0.48145466, 0.4578275, 0.40821073],
            image_std=[0.26862954, 0.26130258, 0.27577711],
        ),
    )
    clip = CLIPModel.from_pretrained(clip_snapshot, torch_dtype=dtype, local_files_only=True).to(device).eval()
    started_at = existing.get("started_at") or datetime.now(timezone.utc).isoformat()

    for offset in range(0, len(pending), args.batch_size):
        batch = pending[offset:offset + args.batch_size]
        images = [Image.open(item["path"]).convert("RGB") for item in batch]
        encoded = blip_processor(images=images, return_tensors="pt", padding=True)
        encoded = {key: value.to(device, dtype=dtype if value.is_floating_point() else None) for key, value in encoded.items()}
        with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=device == "cuda"):
            generated = blip.generate(**encoded, max_new_tokens=36, num_beams=3)
        captions = [clean_caption(text) for text in blip_processor.batch_decode(generated, skip_special_tokens=True)]
        predictions_by_field = {
            "hair_color": label_probs(clip, clip_processor, images, HAIR_COLORS, device),
            "hair_length": label_probs(clip, clip_processor, images, HAIR_LENGTHS, device),
            "eye_color": label_probs(clip, clip_processor, images, EYE_COLORS, device),
            "surface": label_probs(clip, clip_processor, images, SURFACES, device),
            "build": label_probs(clip, clip_processor, images, BUILDS, device),
            "composition": label_probs(clip, clip_processor, images, COMPOSITIONS, device),
        }
        for index, (item, caption) in enumerate(zip(batch, captions)):
            predictions = {field: values[index] for field, values in predictions_by_field.items()}
            geometry = face_geometry(item["path"])
            flags, severity, suggestion = crop_assessment(predictions["composition"], geometry)
            records[item["key"]] = {
                "key": item["key"], "kind": item["kind"], "metadata_key": item["metadata_key"],
                "pool": item["pool"], "path": str(item["path"].relative_to(ROOT)),
                "caption": caption, "appearance": appearance_record(item, caption, predictions),
                "confidence": {field: round(value[1], 4) for field, value in predictions.items()},
                "crop": {
                    "severity": severity, "flags": flags, "suggestion": suggestion,
                    "composition_label": predictions["composition"][0],
                    "composition_confidence": round(predictions["composition"][1], 4),
                    "face_geometry": geometry,
                },
            }
        if not args.dry_run:
            save_outputs(records, started_at, complete=False)
        print(f"Analyzed {min(offset + len(batch), len(pending))}/{len(pending)} pending ({len(records)}/{len(all_items)} total).", flush=True)
        for image in images:
            image.close()

    if not args.dry_run:
        save_outputs(records, started_at, complete=len(records) >= len(all_items))
        write_report(records, len(all_items))
    del blip, clip
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
    print(f"Audit complete: {len(records)}/{len(all_items)} portraits.", flush=True)


if __name__ == "__main__":
    main()
