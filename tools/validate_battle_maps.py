"""Validate every authored tactical map. Run from the project root."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.battle_maps import BATTLE_MAPS, compile_battle_map, validate_battle_map


def main() -> int:
    failed = False
    for map_id in BATTLE_MAPS:
        problems = validate_battle_map(map_id)
        if problems:
            failed = True
            print(f"[FAIL] {map_id}")
            for problem in problems:
                print(f"  - {problem}")
            continue
        compiled = compile_battle_map(map_id)
        print(f"[OK] {map_id}: {compiled['width']}x{compiled['height']}, "
              f"{len(compiled['terrain'])} terrain props, {len(compiled['elevation'])} elevations")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
