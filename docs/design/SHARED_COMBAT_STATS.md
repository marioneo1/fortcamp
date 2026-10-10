# Shared ordinary-character combat stats

Implemented in dev October 9, 2026. Current reference; the original growth
comparison and paired trial are historical evidence, not live formulas.

## Calculation

1. Scale allocated STR/DEX/AGI/VIT/INT/LUK by Adventurer Rank, rounding halves up:
   E 1.0×, D 1.3×, C 1.6×, B 1.9×, A 2.2×, S 2.5×.
2. Add existing equipment, proficiency and perk attribute bonuses afterward.
   Battle-only random attribute rolls also apply afterward. Minimum attribute: 1.
3. Derive ordinary combat values:
   - HP: `12 + 4 × VIT`, then existing racial HP multiplier and flat bonuses.
   - Weapon Attack: `2 + floor(scaling attribute / 2) + weapon power + eligible training`.
   - Armor: `floor(VIT / 3) + racial Armor + equipment/perks/Job Armor`.

Existing minimum rules remain. Weapon power and fixed bonuses are not ranked;
completed combat stats are not multiplied again. STR/DEX/INT scaling depends on
the weapon. Capture equipment retains lethal Punch and separate Resolve/Subdue
power. Existing individual spell/status damage rules remain.

Neutral Human, VIT 6 / STR 6, without training or gear:

| Rank | Effective VIT / STR | HP | Unarmed Attack | Armor |
| --- | --- | --- | --- | --- |
| E | 6 | 36 | 5 | 2 |
| D | 8 | 44 | 6 | 2 |
| S | 15 | 72 | 9 | 5 |

Canonical code: `backend/combat_stats.py`, used by allied bodies, reconstructed
ordinary NPCs and equipment technique Attack. Frontend roster attributes use
the server's rank policy; combat stat explanations identify rank/contributions.
Unit Details uses short explanations followed by numeric formulas, with division
and rounding in plain language; source formatting is shared by both sides.
Roster mission DPS remains a **mission rating**, not battlefield Attack; its
existing help describes that separate purpose.

## Reconstruction and capture

Fresh contract humanoids and scripted Warcamp, captive-cart, rescue, Smoke Signals,
watch-defense and reinforcement opponents are reconstructed around authored
encounter HP/Attack/Armor targets. VIT and the weapon's scaling attribute are
allocated through the shared formulas. Existing racial rules, skills, perks and
role movement/range/initiative/evasion remain; those tactical role values are not
claimed to be fully attribute-derived.

The fitter balances close HP against excess Armor, weighting Armor more strongly
for bosses and retaining at least 80% of the HP target. Exact old HP is not promised:
the D Warcamp chief becomes 64 HP / 12 Attack / 6 Armor instead of 72 / 12 / 3.
Its prepared D-party regression passes. Higher-tier bosses still need manual audits.
Supply/worksite targets received small rounding adjustments to retain the existing
15% layout HP-budget band.

Additional encounter armor is explicit equipment. Worn weapons have zero power;
their scaling is recorded. Recruitment removes encounter gear, so losing a bow
can switch DEX scaling to unarmed STR. Equivalent gear produces equivalent stats.

New capture snapshots store **unranked allocations + Adventurer Rank**. Both sides
derive rank once; traits and identity persist. Legacy recruits without rank retain
their stored attributes at implicit E: never infer/unscale an old source rank.
Only fresh bodies are rebuilt; saved live battles and save data are not rewritten.

Species kits, protected scenario NPCs, temporary summons, machinery and form
exceptions retain their rules: rats/wolves, 1-HP Wisps, 2-HP Sentries and fixed
Rat-form damage are not rebuilt as ordinary humanoids.

## Validation and limitations

[Smoke audit](SHARED_COMBAT_STATS_AUDIT.md): 396 automated fights, every exposed
layout of 14 E and three D missions, six damage-focused Jobs, two Human allies.
D sample parties explicitly receive D rank; no real player promotion occurs.
Recruitment tests cover every audited humanoid layout, serialization, equivalent
equipment and rank parity. Separate checks cover legacy bodies and post-rank
bonuses. Focused frontend tests and browser build pass.

Auto-play is not proof of human difficulty. Support/setup Jobs, other races,
optimized builds and C–S bosses remain outside those fights. Broader-suite
concealment/legacy-fixture failures were reproduced under the old formulas;
task-specific validation is recorded in WORK_STATE.

## Deferred

- Player Adventurer Rank promotion/unlocks and Growth Grade UI/assignment.
- Rebirth, below-E catch-up, +4–6 growth rewards, allocation costs and paid respec.
- Racial innate HP/base Attack differences, saved for the race audit; no new
  racial modifiers were introduced here.
- Weapon overhaul, equipment requirements and further manual/race/boss balancing.

Explicit rank is supported; unlocking a guild tier does not automatically promote
the player. Restart dev, refresh the browser and create a fresh battle to test.
