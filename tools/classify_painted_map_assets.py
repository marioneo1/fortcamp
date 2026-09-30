"""Move painted map art into mutually exclusive runtime layers."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAINTED = ROOT / "frontend" / "public" / "assets" / "combat-terrain"
PROPS = PAINTED / "props"
TERRAIN = PAINTED / "mega-terrain-tiles"
STRUCTURES = PAINTED / "structures"

PROP_STRUCTURES = {
    "palisade_breached", "palisade_corner", "palisade_end", "palisade_gate_closed",
    "palisade_gate_open", "palisade_straight", "palisade_t_junction", "stake_barrier",
    "stone_archway", "stone_gate_closed", "stone_gate_open", "stone_pillar",
    "stone_wall_breached", "stone_wall_corner", "stone_wall_end", "stone_wall_straight",
    "stone_wall_t_junction", "wall_rubble", "wooden_barricade", "wooden_ladder",
    "wooden_watch_platform",
}

TERRAIN_STRUCTURES = {
    "castle_arch_open", "castle_battlement", "castle_door_closed", "castle_door_open",
    "castle_pillar_square", "castle_portcullis_closed", "castle_wall_corner",
    "castle_wall_cross", "castle_wall_end", "castle_wall_straight", "castle_wall_t",
    "prison_bars_corner", "prison_bars_end", "prison_bars_straight", "prison_bars_t",
    "prison_cell_door_closed", "prison_cell_door_open", "prison_pen_corner",
    "prison_pen_end", "prison_pen_gate_closed", "prison_pen_gate_open",
    "prison_pen_straight", "prison_pen_t",
}


def load_index(folder: Path) -> dict:
    path = folder / "index.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"sprites": {}}


def main() -> None:
    for folder in (PROPS, TERRAIN, STRUCTURES):
        folder.resolve().relative_to(ROOT.resolve())
    STRUCTURES.mkdir(parents=True, exist_ok=True)

    prop_index = load_index(PROPS)
    terrain_index = load_index(TERRAIN)
    structure_entries: dict[str, dict] = {}

    for source, names, index, source_label in (
        (PROPS, PROP_STRUCTURES, prop_index, "environment_props_master_60"),
        (TERRAIN, TERRAIN_STRUCTURES, terrain_index, "terrain_only_mega_96"),
    ):
        for name in sorted(names):
            source_file = source / f"{name}.png"
            destination = STRUCTURES / source_file.name
            if source_file.exists():
                if destination.exists():
                    raise FileExistsError(f"Refusing to overwrite {destination}")
                source_file.replace(destination)
            entry = index.get("sprites", {}).pop(name, {"file": destination.name})
            entry["source_library"] = source_label
            structure_entries[name] = entry

    prop_index["runtime_layer"] = "props"
    terrain_index["runtime_layer"] = "terrain"
    prop_index["sprites"] = dict(sorted(prop_index.get("sprites", {}).items()))
    terrain_index["sprites"] = dict(sorted(terrain_index.get("sprites", {}).items()))
    (PROPS / "index.json").write_text(json.dumps(prop_index, indent=2) + "\n", encoding="utf-8")
    (TERRAIN / "index.json").write_text(json.dumps(terrain_index, indent=2) + "\n", encoding="utf-8")
    (STRUCTURES / "index.json").write_text(json.dumps({
        "runtime_layer": "structures",
        "behavior": "Rendered above terrain; may block movement or sight and carry state such as HP, open, closed, breached, or destroyed.",
        "sprites": dict(sorted(structure_entries.items())),
    }, indent=2) + "\n", encoding="utf-8")

    print(f"terrain={len(terrain_index['sprites'])} structures={len(structure_entries)} props={len(prop_index['sprites'])}")


if __name__ == "__main__":
    main()
