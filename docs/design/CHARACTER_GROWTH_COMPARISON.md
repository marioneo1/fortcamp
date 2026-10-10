# Character growth comparison

October 9, 2026. Offline proposal: no live stats, saves, ranks or equipment changed.

## Encounter formula comparison

Current opponents use authored combat stats. These projections retain their unranked recruit allocation and apply Adventurer Rank once before deriving stats. Growth stage is deliberately unassigned: a stat total cannot prove a completed advancement.

All values below are **HP / Attack / Armor**. Projections include current racial HP/Armor, but exclude gear, training, perks and Job bonuses. They use STR for melee and DEX for Ranger. Thus they are body probes, not complete reconstructed enemy kits. Current encounters retain all their existing modifiers.

A uses current player bases: HP = 24 + 4×VIT; Attack = 5 + scaling attribute÷2, rounded down. B is an **unapproved global experiment** with bases 12 and 2; it is not an enemy-only discount.

| Mission / role | Race / Rank | Base allocation STR/DEX/AGI/VIT/INT/LUK | Budget | Current encounter | A | B |
| --- | --- | --- | --- | --- | --- | --- |
| roadside_toll: Road Enforcer | Human / E | 6/5/4/5/4/4 | 28 | 28 / 5 / 1 | 44 / 8 / 1 | 32 / 5 / 1 |
| roadside_toll: Road Cutpurse | Human / E | 4/5/6/4/4/4 | 27 | 22 / 4 / 0 | 40 / 7 / 1 | 28 / 4 / 1 |
| goblin_pickpockets: Goblin Cutpurse | Goblin / E | 4/5/6/4/4/4 | 27 | 24 / 4 / 0 | 28 / 7 / 1 | 20 / 4 / 1 |
| goblin_pickpockets: Goblin Lookout | Goblin / E | 4/6/6/4/4/4 | 28 | 24 / 4 / 0 | 28 / 8 / 1 | 20 / 5 / 1 |
| highway_ambush: Bandit Enforcer | Human / D | 6/5/4/5/4/4 | 28 | 36 / 6 / 0 | 52 / 9 / 2 | 40 / 6 / 2 |
| highway_ambush: Bandit Trapper | Human / D | 4/5/6/4/4/4 | 27 | 30 / 5 / 0 | 44 / 7 / 1 | 32 / 4 / 1 |
| highway_ambush: Highway Lookout | Human / D | 4/6/4/4/4/4 | 26 | 30 / 5 / 0 | 44 / 9 / 1 | 32 / 6 / 1 |
| bone_patrol: Relic Warden | Undead / D | 6/5/4/5/4/4 | 28 | 40 / 7 / 1 | 58 / 9 / 3 | 45 / 6 / 3 |
| bone_patrol: Bone Shieldbearer | Undead / D | 6/5/4/5/4/4 | 28 | 40 / 7 / 3 | 58 / 9 / 3 | 45 / 6 / 3 |
| bone_patrol: Chapel Archer | Undead / D | 4/6/4/4/4/4 | 26 | 34 / 5 / 1 | 49 / 9 / 2 | 36 / 6 / 2 |
| goblin_boar_riders: Boar Vanguard | Goblin / D | 6/5/6/5/4/4 | 30 | 36 / 7 / 1 | 36 / 9 / 2 | 28 / 6 / 2 |
| goblin_boar_riders: Mounted Skirmisher | Goblin / D | 4/5/6/4/4/4 | 27 | 31 / 5 / 0 | 31 / 7 / 1 | 22 / 4 / 1 |
| goblin_boar_riders: Rider Slinger | Goblin / D | 4/6/6/4/4/4 | 28 | 31 / 6 / 0 | 31 / 9 / 1 | 22 / 6 / 1 |

### What this means

- Current player formulas have a Human HP floor of 28 at VIT 1, and an untrained/unarmed Attack floor of 5. Allocation and Growth labels alone cannot reproduce the lighter enemies below those floors.
- B moves enemies closer to current encounters, but also weakens players: an all-6 Human goes from 48 HP / 8 Attack to 36 HP / 5 Attack at E. At S it goes from 84 / 12 to 72 / 9. Gear and training add afterward; these are not final player builds.
- Neither formula preserves the original 1.3× combat outputs at D. Attribute-first scaling intentionally scales only attribute contributions; fixed bases and weapon power do not receive that multiplier.
- Keep current encounters until a shared formula and player baseline are approved. Then rebuild coherent allocations and equipment together, preserve kits/range/movement identity, and run all-layout fights. Do not hide residual mismatches in unexplained encounter multipliers.

## Allocation costs at S rank

Five E→S Growth advances of +4–6 yield budgets 56–66 from the starting 36; 61 is the average, not a cap. These examples use current player bases, Human race, no gear/training/perks, and S rank ×2.5 applied once. No existing creator ceiling is imposed: raising it would be part of a future implementation.

Linear: every raw attribute costs 1. Graduated: 1 through 10, 2 for 11–15, 3 above 15. All current legal creator builds retain their existing cost. Priorities are illustrative rather than optimized; exact distribution is reproducible in the tool.

| Build | Budget (spent) | Costs | Base STR/DEX/AGI/VIT/INT/LUK | HP / Attack / Armor | Move |
| --- | --- | --- | --- | --- | --- |
| Tank | 56 (56) | Linear | 10/7/7/18/7/7 | 204 / 17 / 15 | 4 |
| Tank | 56 (56) | Graduated | 9/7/7/15/7/6 | 176 / 16 / 12 | 4 |
| Tank | 61 (61) | Linear | 11/8/8/20/7/7 | 224 / 19 / 16 | 4 |
| Tank | 61 (60) | Graduated | 9/7/7/16/7/7 | 184 / 16 / 13 | 4 |
| Tank | 66 (66) | Linear | 12/8/8/22/8/8 | 244 / 20 / 18 | 4 |
| Tank | 66 (64) | Graduated | 10/7/7/17/7/7 | 196 / 17 / 14 | 4 |
| Melee DPS | 56 (56) | Linear | 17/7/9/9/7/7 | 116 / 26 / 7 | 4 |
| Melee DPS | 56 (56) | Graduated | 15/7/9/8/6/6 | 104 / 24 / 6 | 4 |
| Melee DPS | 61 (61) | Linear | 20/7/10/10/7/7 | 124 / 30 / 8 | 4 |
| Melee DPS | 61 (59) | Graduated | 15/7/9/9/7/7 | 116 / 24 / 7 | 4 |
| Melee DPS | 66 (66) | Linear | 20/8/11/11/8/8 | 136 / 30 / 9 | 4 |
| Melee DPS | 66 (66) | Graduated | 17/7/10/9/7/7 | 116 / 26 / 7 | 4 |
| Marksman | 56 (56) | Linear | 7/17/9/9/7/7 | 116 / 26 / 7 | 4 |
| Marksman | 56 (56) | Graduated | 7/15/9/8/6/6 | 104 / 24 / 6 | 4 |
| Marksman | 61 (61) | Linear | 8/19/10/10/7/7 | 124 / 29 / 8 | 4 |
| Marksman | 61 (59) | Graduated | 7/15/9/9/7/7 | 116 / 24 / 7 | 4 |
| Marksman | 66 (66) | Linear | 8/20/11/11/8/8 | 136 / 30 / 9 | 4 |
| Marksman | 66 (66) | Graduated | 7/17/10/9/7/7 | 116 / 26 / 7 | 4 |
| Caster | 56 (56) | Linear | 7/7/9/9/17/7 | 116 / 26 / 7 | 4 |
| Caster | 56 (56) | Graduated | 7/7/9/9/14/6 | 116 / 22 / 7 | 4 |
| Caster | 61 (61) | Linear | 8/7/10/10/19/7 | 124 / 29 / 8 | 4 |
| Caster | 61 (59) | Graduated | 7/7/9/9/15/7 | 116 / 24 / 7 | 4 |
| Caster | 66 (66) | Linear | 8/8/11/11/20/8 | 136 / 30 / 9 | 4 |
| Caster | 66 (66) | Graduated | 7/7/10/9/17/7 | 116 / 26 / 7 | 4 |

### Recommendation

Keep attribute-first rank scaling and trial the graduated costs. This leaves current creation intact while charging more for extreme specialization; +4–6 means allocation points, not guaranteed +4–6 raw attribute increases. Preserve actual rolled budgets, including totals above 61.

Do not assign Growth by looking up a point-total band. Generated characters need a declared completed stage plus an allocation allowance; below-E bodies need a recorded catch-up deficit. Existing enemies require an explicit reconstruction/migration record, not a guessed advancement history.

The consequential unresolved choice is the shared fixed bases. A preserves existing player formulas but raises light-enemy strength. B better approximates light enemies but reduces baseline player strength. Neither should be shipped automatically from this comparison. Recommend evaluating a small player-and-enemy trial together before selecting the final bases.

## Limits and next validation

This report samples the first authored variation of five humanoid missions, not every race, boss or layout. Caster Attack is a staff/INT weapon pool illustration, not a promise that every spell uses it. Armor is flat subtraction: actual durability depends on incoming damage, penetration, resistances and mitigation; it cannot be summarized as one universal reduction percentage.

Future trial must compare basic/technique damage through the real resolver, incoming attacks and survival turns, racial damage reduction, gear/perk modifiers, and full encounter action economy. No battle simulation or win-rate claim is made by this calculator. Movement/range percentages, cooldowns, statuses and species kits require independent review rather than rank multiplication.
