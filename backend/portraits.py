from __future__ import annotations

import random
import re
from pathlib import Path
from urllib.parse import quote

from .appearance import champion_metadata, portrait_metadata

ROOT = Path(__file__).resolve().parents[1]
PORTRAIT_POOL_ROOT = ROOT / "data" / "portrait_pools"
CHAMPION_PORTRAIT_ROOT = ROOT / "data" / "champion_portraits"
SUPPORTED_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg"}

ARCHETYPE_ROLES = {
    "fighter": "melee",
    "scout": "ranged",
    "builder": "worker",
    "medic": "healer",
    "adept": "magic",
}

PORTRAIT_ROLES = ("melee", "ranged", "magic", "healer", "worker", "special")
ROLELESS_PORTRAIT_RACES = frozenset({"slimefolk", "werewolf"})


def portrait_pool_key(race: str, gender: str, archetype_id: str, special: bool = False) -> str:
    race_key = re.sub(r"[^a-z0-9]+", "_", (race or "human").lower()).strip("_") or "human"
    gender_key = gender if gender in {"male", "female"} else "male"
    if race_key in ROLELESS_PORTRAIT_RACES:
        return f"{race_key}_{gender_key}"
    role = "special" if special else ARCHETYPE_ROLES.get(archetype_id, "survivor")
    return f"{race_key}_{gender_key}_{role}"


def portrait_pool_candidates(pool_key: str) -> list[str]:
    """Return deterministic same-race/gender fallbacks for a requested pool.

    A roleless pool (for example ``slimefolk_female``) is preferred over a
    different role. This lets biologically general sheets serve every class
    while still allowing a dedicated role sheet to take priority later.
    """
    match = re.fullmatch(
        rf"(?P<base>[a-z0-9_]+_(?:male|female))(?:_(?P<role>{'|'.join(PORTRAIT_ROLES)}))?",
        pool_key,
    )
    if not match:
        return [pool_key]
    base = match.group("base")
    requested_role = match.group("role")
    candidates = [pool_key]
    if pool_key != base:
        candidates.append(base)
    for role in PORTRAIT_ROLES:
        candidate = f"{base}_{role}"
        if role != requested_role and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def choose_pool_portrait(pool_key: str, rng: random.Random) -> dict:
    if not re.fullmatch(r"[a-z0-9_]+", pool_key):
        return {"portrait": "", "portrait_thumbnail": "", "portrait_pool": pool_key}
    resolved_pool = pool_key
    portraits: list[Path] = []
    for candidate_pool in portrait_pool_candidates(pool_key):
        full_dir = PORTRAIT_POOL_ROOT / candidate_pool / "full"
        portraits = sorted(
            path for path in full_dir.glob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if portraits:
            resolved_pool = candidate_pool
            break
    if not portraits:
        return {"portrait": "", "portrait_thumbnail": "", "portrait_pool": pool_key}
    chosen = rng.choice(portraits)
    thumb = PORTRAIT_POOL_ROOT / resolved_pool / "thumb" / chosen.name
    base = f"/api/portrait-pools/{quote(resolved_pool)}/"
    appearance = portrait_metadata(resolved_pool, chosen.name)
    return {
        "portrait": base + "full/" + quote(chosen.name),
        "portrait_thumbnail": base + ("thumb/" if thumb.is_file() else "full/") + quote(chosen.name),
        "portrait_pool": resolved_pool,
        "appearance": appearance,
        "appearance_source": "portrait" if any(appearance.values()) else "none",
    }


def champion_portrait(champion_id: str, variant: str = "default") -> dict[str, str]:
    """Return stable URLs for a Champion portrait variant.

    Non-default variants live below ``expressions/<variant>``. Missing
    expressions fall back to the Champion's default portrait so story code can
    request an expression before art for it exists.
    """
    if not re.fullmatch(r"[a-z0-9_]+", champion_id):
        return {"portrait": "", "portrait_thumbnail": "", "portrait_variant": "default"}
    if not re.fullmatch(r"[a-z0-9_]+", variant):
        variant = "default"

    relative = Path("default") if variant == "default" else Path("expressions") / variant
    variant_dir = CHAMPION_PORTRAIT_ROOT / champion_id / relative
    full = variant_dir / "full.webp"
    thumb = variant_dir / "thumb.webp"
    resolved_variant = variant
    if not full.is_file() and variant != "default":
        variant_dir = CHAMPION_PORTRAIT_ROOT / champion_id / "default"
        full = variant_dir / "full.webp"
        thumb = variant_dir / "thumb.webp"
        resolved_variant = "default"
    if not full.is_file():
        return {"portrait": "", "portrait_thumbnail": "", "portrait_variant": "default"}

    relative_url = f"{quote(champion_id)}/"
    relative_url += "default/" if resolved_variant == "default" else f"expressions/{quote(resolved_variant)}/"
    version = full.stat().st_mtime_ns
    base = f"/api/champion-portraits/{relative_url}"
    appearance = champion_metadata(champion_id, resolved_variant)
    return {
        "portrait": f"{base}full.webp?v={version}",
        "portrait_thumbnail": f"{base}{'thumb.webp' if thumb.is_file() else 'full.webp'}?v={version}",
        "portrait_variant": resolved_variant,
        "appearance": appearance,
        "appearance_source": "portrait" if any(appearance.values()) else "none",
    }
