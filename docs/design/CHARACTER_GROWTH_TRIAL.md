# Shared-stat combat trial

Offline experiment, October 9, 2026. No game saves, runtime formulas, server or production changes.

## Method

Three missions × four authored layouts × six starter Jobs × three formula arms = 216 paired fights. Two Human allies use legal 36-point all-6 bodies and actual starter equipment/skills. Each arm clones the same opening and seed. No growth advancement is invented for these bodies.

- **live:** current player formulas and authored enemies; current players have no personal rank scaling.
- **shared24:** shared bases 24 HP / 5 Attack; allocate attributes then apply E/D rank once.
- **shared12:** shared bases 12 HP / 2 Attack; otherwise same as shared24.

Player attribute gear bonuses and flat gear/training/Job bonuses are retained after body rank scaling. Enemies use recorded pre-rank recruit bodies, with no invented weapon power or combat-training bonus; their existing skills, perks, statuses and resistances remain. Enemy Armor is derived anew, so authored role-specific armor overrides are removed in both shared arms. Enemy role movement/range remains authored. This tests the untouched allocations, not optimized reconstructions or final equipment assignments.

Cached skill Attack values receive the actor Attack delta; bespoke spell/heal/summon formulas are not rewritten. Full fights use existing targeting, hit rolls, AI, skill/status/damage resolution and termination rules. Opening damage columns call the real damage resolver on separate clones, bypassing hit/range checks; they mean damage **if the hit connects**, not expected DPS.

## Results

| Mission | Arm | Wins / fights | Failures | Stalls / errors | Mean rounds | Mean opening outgoing / incoming | Mean allies surviving |
| --- | --- | --- | --- | --- | --- | --- | --- |
| roadside_toll | live | 24/24 | 0 | 0 | 7.1 | 9.0 / 2.8 | 2.00 / 2 |
| roadside_toll | shared24 | 23/24 | 1 | 0 | 9.5 | 9.0 / 5.8 | 1.71 / 2 |
| roadside_toll | shared12 | 24/24 | 0 | 0 | 9.2 | 6.0 / 2.8 | 1.92 / 2 |
| highway_ambush | live | 24/24 | 0 | 0 | 5.8 | 10.0 / 2.8 | 2.00 / 2 |
| highway_ambush | shared24 | 18/24 | 6 | 0 | 7.1 | 9.8 / 4.1 | 1.42 / 2 |
| highway_ambush | shared12 | 20/24 | 4 | 0 | 8.0 | 6.8 / 1.2 | 1.67 / 2 |
| bone_patrol | live | 21/24 | 3 | 0 | 8.1 | 8.5 / 4.1 | 1.67 / 2 |
| bone_patrol | shared24 | 15/24 | 9 | 0 | 8.5 | 8.2 / 5.3 | 1.00 / 2 |
| bone_patrol | shared12 | 20/24 | 4 | 0 | 8.8 | 5.2 / 2.4 | 1.67 / 2 |

Per-fight opening stats, damage, outcomes, rounds and errors: [CSV](CHARACTER_GROWTH_TRIAL.csv).

## Limits

Auto-play measures these starter-loadout heuristics, not human balance or support effectiveness. Human-only, two-character parties; no bosses, Ogre/Fairy, advanced equipment, all Jobs, high Growth or S-rank encounters covered. One fixed seed per layout is a small paired sample. Opening damage is not a skill rotation or survival probability. Victory rates cannot determine a global formula alone.

Personal D-rank in shared arms is itself a new feature; live D players are still E-stat bodies. Consequently comparisons with live combine formula parity and proposed personal rank advancement. The two shared arms isolate the fixed-base choice. Before migration, reconstruct actual enemy gear/perks and role armor coherently, then rerun wider-race/manual trials.
