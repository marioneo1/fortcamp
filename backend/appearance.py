"""Character appearance fields and stable portrait sidecar metadata."""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
PORTRAIT_METADATA_PATH = ROOT / "data" / "portrait_pools" / "portrait_metadata.json"
CHAMPION_METADATA_PATH = ROOT / "data" / "champion_portraits" / "portrait_metadata.json"

APPEARANCE_FIELDS = (
    "hair_color", "hair_length", "eye_color", "skin_tone", "build",
    "distinctive_features", "summary",
)
FIELD_LIMITS = {
    "hair_color": 48, "hair_length": 48, "eye_color": 48,
    "skin_tone": 64, "build": 64, "distinctive_features": 240,
    "summary": 360,
}


def sanitize_appearance(value: object) -> dict[str, str]:
    source = value if isinstance(value, dict) else {}
    clean: dict[str, str] = {}
    for field in APPEARANCE_FIELDS:
        text = " ".join(str(source.get(field, "")).strip().split())
        clean[field] = text[:FIELD_LIMITS[field]]
    return clean


def has_appearance(value: object) -> bool:
    return any(sanitize_appearance(value).values())


def _read_metadata(path: Path) -> dict[str, dict[str, str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    entries = payload.get("portraits", payload) if isinstance(payload, dict) else {}
    if not isinstance(entries, dict):
        return {}
    return {
        str(key): sanitize_appearance(value)
        for key, value in entries.items()
        if isinstance(key, str) and has_appearance(value)
    }


def read_portrait_metadata() -> dict[str, dict[str, str]]:
    return _read_metadata(PORTRAIT_METADATA_PATH)


def write_portrait_metadata(entries: dict[str, dict[str, str]]) -> None:
    PORTRAIT_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "portraits": {
            key: sanitize_appearance(value)
            for key, value in sorted(entries.items())
            if has_appearance(value)
        },
    }
    temporary = PORTRAIT_METADATA_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, PORTRAIT_METADATA_PATH)


def portrait_metadata(pool: str, filename: str) -> dict[str, str]:
    if not pool or not filename:
        return sanitize_appearance({})
    return sanitize_appearance(read_portrait_metadata().get(f"{pool}/{filename}", {}))


def champion_metadata(champion_id: str, variant: str = "default") -> dict[str, str]:
    if not champion_id:
        return sanitize_appearance({})
    entries = _read_metadata(CHAMPION_METADATA_PATH)
    return sanitize_appearance(entries.get(f"{champion_id}/{variant}", entries.get(f"{champion_id}/default", {})))


def portrait_identity(character: dict) -> tuple[str, str] | None:
    pool = str(character.get("portrait_pool", "")).strip()
    portrait = str(character.get("portrait", "")).strip()
    if not pool or not portrait:
        return None
    path = unquote(urlparse(portrait).path)
    marker = f"/api/portrait-pools/{pool}/full/"
    if marker not in path:
        return None
    filename = path.rsplit("/", 1)[-1]
    return (pool, filename) if filename else None


def tagged_appearance(character: dict) -> dict[str, str]:
    if character.get("source_kind") in {"champion", "celestial"} and character.get("portrait_source") != "override":
        source_id = str(character.get("source_id", "")).removeprefix("celestial:")
        return champion_metadata(source_id, str(character.get("portrait_variant", "default")))
    identity = portrait_identity(character)
    return portrait_metadata(*identity) if identity else sanitize_appearance({})


def appearance_phrase(character: dict) -> str:
    appearance = sanitize_appearance(character.get("appearance", {}))
    if appearance["summary"]:
        return appearance["summary"].rstrip(".")
    details: list[str] = []
    hair = " ".join(x for x in (appearance["hair_length"], appearance["hair_color"], "hair") if x)
    if hair != "hair":
        details.append(hair)
    if appearance["eye_color"]:
        details.append(f"{appearance['eye_color']} eyes")
    if appearance["skin_tone"]:
        details.append(f"{appearance['skin_tone']} skin")
    if appearance["build"]:
        details.append(appearance["build"])
    if appearance["distinctive_features"]:
        details.append(appearance["distinctive_features"])
    return ", ".join(details)
