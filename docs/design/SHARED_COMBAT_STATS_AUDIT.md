# Shared combat stats: migration smoke audit

October 9, 2026. Fresh isolated battles; no database writes, saved-battle edits or server restart.

Two Human allies, legal all-6 allocations and actual starter equipment. Six damage-focused Jobs, every layout exposed for the audited E/D mission set. D bodies explicitly have Adventurer D; this does not promote real players. Defense uses its real preparation encounter with no defenses placed; rescue uses its actual objective encounter. Species mechanics remain authored. No radiant encounters injected.

| Mission | Wins / fights | Other completed | Stalls / errors | Mean rounds |
| --- | --- | --- | --- | --- |
| bone_patrol | 20/24 | 4 | 0 | 8.1 |
| frontier_watch_defense | 20/24 | 4 | 0 | 9.8 |
| goblin_boar_riders | 21/24 | 3 | 0 | 8.9 |
| goblin_pickpockets | 22/24 | 2 | 0 | 5.5 |
| herbs_wall | 23/24 | 1 | 0 | 9.5 |
| highway_ambush | 21/24 | 3 | 0 | 7.0 |
| prison_former_e | 24/24 | 0 | 0 | 7.6 |
| prison_proof_e | 24/24 | 0 | 0 | 8.2 |
| prison_rescue_e | 23/24 | 1 | 0 | 5.9 |
| prison_rival_e | 23/24 | 1 | 0 | 7.6 |
| rats_storehouse | 24/24 | 0 | 0 | 7.4 |
| roadside_toll | 24/24 | 0 | 0 | 8.1 |
| ruined_well | 23/24 | 1 | 0 | 7.8 |
| supply_watch | 24/24 | 0 | 0 | 7.5 |
| timber_creek | 11/12 | 1 | 0 | 8.1 |
| tool_shed | 24/24 | 0 | 0 | 8.5 |
| wolves_fence | 24/24 | 0 | 0 | 9.3 |

Total 396 trials; 0 errors; 0 stalls.

[Per-fight opening totals and outcomes](SHARED_COMBAT_STATS_AUDIT.csv).

Auto-play is a smoke check, not proof of human difficulty. Setup/support Jobs, other player races, optimized loadouts, progression UI and high-rank bosses are not represented. Objective/rescue/defense outcomes reflect current auto-play limitations as well as combat strength; avoid altering kits simply to improve this score. Manual map playtests remain necessary. Earlier trial reports retain their pre-migration data and must not be read as current-runtime results.
