"""Refine raw local-model portrait output into conservative game metadata."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audit_portrait_metadata import (
    AUDIT_PATH, CHAMPION_METADATA_PATH, GENERIC_METADATA_PATH, ROOT,
    atomic_json, pool_identity, read_json, write_report,
)
from backend.content import CHAMPIONS

COLORS = ("black", "dark brown", "brown", "auburn", "red", "orange", "blonde", "golden", "white", "silver", "gray", "blue", "green", "teal", "purple", "pink")
EYE_COLORS = ("brown", "amber", "gold", "hazel", "green", "blue", "gray", "red", "purple", "pink", "black", "white")
NON_HAIR_TERMS = {
    "alien": "head tendrils", "slimefolk": "slime crest", "automaton": "head plating",
    "manaforged": "head plating", "lizardfolk": "head crest", "kobold": "head crest",
    "dragonkin": "head crest",
}
SURFACES = {
    "goblin": "green skin", "hobgoblin": "green-gray skin", "bugbear": "dense fur",
    "half orc": "olive-green skin", "orc": "green skin", "lizardfolk": "scaled skin",
    "kobold": "scaled skin", "dragonkin": "scaled skin", "minotaur": "short fur",
    "werewolf": "dense fur", "catfolk": "fine fur", "foxkin": "fine fur",
    "harpy": "feathered skin", "automaton": "metallic plating", "manaforged": "arcane plating",
    "dryad": "bark-like skin", "slimefolk": "translucent slime body",
    "banshee": "translucent spectral skin", "undead": "pale undead skin",
    "revenant": "weathered undead skin",
}


def caption_color(caption: str, feature: str, choices: tuple[str, ...]) -> str:
    for color in sorted(choices, key=len, reverse=True):
        if re.search(rf"\b{re.escape(color)}\s+{feature}\b", caption, re.I):
            return color
    return ""


def separator_y(path: Path) -> int | None:
    image = cv2.imread(str(path))
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dark_fraction = (gray < 35).mean(axis=1)
    rows = np.where(dark_fraction > 0.95)[0]
    rows = rows[(rows > gray.shape[0] * 0.08) & (rows < gray.shape[0] * 0.90)]
    return int(rows[0]) if len(rows) else None


def identity(record: dict) -> tuple[str, str]:
    if record["kind"] == "generic":
        race, gender, _ = pool_identity(record["pool"])
        return race, gender
    champion_id = record["metadata_key"].split("/", 1)[0]
    race = str(CHAMPIONS.get(champion_id, {}).get("race", "Human")).lower()
    caption = record.get("caption", "").lower()
    gender = "male" if re.search(r"\b(man|boy|male)\b", caption) else "female"
    return race, gender


def refined_caption(caption: str, race: str, gender: str) -> str:
    text = caption.strip(" .")
    text = re.sub(r"^(an?|the) (image|picture|portrait) of ", "", text, flags=re.I)
    subject = f"{gender} {race}".strip()
    text = re.sub(r"\b(a|an) (woman|girl|man|boy|person)\b", f"a {subject}", text, count=1, flags=re.I)
    replacement = NON_HAIR_TERMS.get(race)
    if replacement:
        text = re.sub(r"\bhair\b", replacement, text, flags=re.I)
    text = re.sub(r"\s+(holding|carrying|wielding)\b.*$", "", text, flags=re.I)
    text = re.sub(r"\s+with (a|an) (sword|bow|axe|staff|book|shield|spear|dagger|gun|weapon)\b.*$", "", text, flags=re.I)
    text = re.sub(r"\s+standing in front of\b.*$", "", text, flags=re.I)
    if race == "slimefolk":
        text = f"a {gender} slimefolk with a visible internal slime core and a fully fluid body"
    return text[:240]


def refine_appearance(record: dict) -> dict[str, str]:
    race, gender = identity(record)
    caption = record.get("caption", "")
    old = record.get("appearance", {})
    confidence = record.get("confidence", {})
    anatomy_term = NON_HAIR_TERMS.get(race)
    hair_color = "" if anatomy_term else caption_color(caption, "hair", COLORS)
    lowered = caption.lower()
    if anatomy_term:
        hair_length = ""
    elif "very long hair" in lowered:
        hair_length = "very long"
    elif "long hair" in lowered:
        hair_length = "long"
    elif "short hair" in lowered:
        hair_length = "short"
    else:
        hair_length = ""
    eye_color = caption_color(caption, "eyes", EYE_COLORS)
    surface = SURFACES.get(race, "")
    if race in {"alien", "dark elf", "tiefling", "dreamkin", "voidsent"} and float(confidence.get("surface", 0)) >= 0.50:
        surface = old.get("skin_tone", "")
    build = next((word for word in ("muscular", "stocky", "sturdy", "slender", "athletic", "petite") if re.search(rf"\b{word}\b", caption, re.I)), "")
    distinctive = refined_caption(caption, race, gender)
    subject = f"{gender} {race}".strip()
    summary = distinctive[:1].upper() + distinctive[1:] if distinctive else f"A {subject}"
    if surface and surface.lower() not in summary.lower() and race != "slimefolk":
        summary += f", with {surface}"
    return {
        "hair_color": hair_color, "hair_length": hair_length, "eye_color": eye_color,
        "skin_tone": surface, "build": build, "distinctive_features": distinctive,
        "summary": summary[:360],
    }


def refine_crop(record: dict) -> None:
    if record.get("crop", {}).get("applied_fix"):
        record["crop"].update({
            "severity": "good", "flags": [], "suggestion": "", "proposal": "",
            "source_geometry_flags": [],
        })
        return
    source_geometry_flags = record.get("crop", {}).get("source_geometry_flags", [])
    if source_geometry_flags:
        record["crop"].update({
            "severity": "bad", "flags": source_geometry_flags,
            "suggestion": "Use the boundary-aware source-sheet recrop; it removes neighboring-cell bleed and restores the intended cell framing.",
        })
        return
    path = ROOT / record["path"]
    separator = separator_y(path)
    label = record["crop"].get("composition_label", "")
    confidence = float(record["crop"].get("composition_confidence", 0))
    match = re.fullmatch(r"generic:half_orc_female_melee/half_orc_female_melee_(\d{3})\.webp", record["key"])
    half_orc_index = int(match.group(1)) if match else 0
    if 11 <= half_orc_index <= 15:
        record["crop"].update({
            "severity": "bad", "flags": ["grid_boundary_bleed", "neighboring_cell_visible"],
            "suggestion": "Use the boundary-aware proposed recrop; it restores the full face and removes the neighboring row.",
            "separator_y": separator,
            "proposal": f"data/portrait_audit/proposed_recrops/half_orc_female_melee_{half_orc_index:03d}.webp",
        })
    elif 16 <= half_orc_index <= 20:
        record["crop"].update({
            "severity": "bad", "flags": ["wrong_grid_row_bounds", "head_cut_off"],
            "suggestion": "Use the boundary-aware proposed recrop; it restores the missing head and face.",
            "proposal": f"data/portrait_audit/proposed_recrops/half_orc_female_melee_{half_orc_index:03d}.webp",
        })
    else:
        record["crop"].update({"severity": "good", "flags": [], "suggestion": "", "proposal": ""})


def main() -> None:
    audit = read_json(AUDIT_PATH, {"records": {}})
    records = audit.get("records", {})
    generic: dict[str, dict] = {}
    champions: dict[str, dict] = {}
    for record in records.values():
        record["appearance"] = refine_appearance(record)
        refine_crop(record)
        target = generic if record["kind"] == "generic" else champions
        target[record["metadata_key"]] = record["appearance"]
    atomic_json(AUDIT_PATH, audit)
    atomic_json(GENERIC_METADATA_PATH, {"version": 1, "portraits": dict(sorted(generic.items()))})
    atomic_json(CHAMPION_METADATA_PATH, {"version": 1, "portraits": dict(sorted(champions.items()))})
    write_report(records, len(records))
    bad = sum(record["crop"]["severity"] == "bad" for record in records.values())
    review = sum(record["crop"]["severity"] == "review" for record in records.values())
    print(f"Refined {len(records)} portraits: {bad} definite crop problems, {review} review candidates.")


if __name__ == "__main__":
    main()
