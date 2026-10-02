# Combat tools and rank pacing

Implemented in dev, October 2, 2026. This supplements COMBAT_DESIGN.md. Existing saved encounters retain their stats; new battles receive the new budgets. Production and player saves were not reset.

## Fixed enemy budgets

Generated contract battles use authored rank budgets, rather than scaling to the party's strongest character. Values below are before racial modifiers:

| Rank | Commander HP / attack / armor | Escort HP / attack / armor |
| --- | --- | --- |
| E | 22 / 6 / 1 | 14 / 4 / 0 |
| D | 56 / 10 / 2 | 26 / 7 / 1 |
| C | 84 / 13 / 3 | 38 / 9 / 2 |
| B | 112 / 17 / 4 | 48 / 12 / 2 |
| A | 154 / 22 / 5 | 62 / 15 / 3 |
| S | 210 / 29 / 6 | 80 / 19 / 4 |

Ordinary units retain their racial HP modifier; commanders use a minimum 85% multiplier to represent veteran durability. Special rookie E fights keep their 10/7 HP, zero armor, attack 3. Named Warcamp and Redoubt budgets remain the separate authored values in COMBAT_DESIGN.md. This pass does not replace every custom encounter with the table. C+ armed contract enemies can inflict low-chance Bleed, Blind or Mute; Meridian faction fights can include an explicitly magical Lightning caster. Corpse coin scales with rank; creatures still do not carry gold.

Auto-battle uses the three opening ambush rounds to approach a clear attack position and guard, without waking the camp. The player may attack earlier manually. Ordinary auto tactics remain available after the preparation window; coordinated traps, elaborate formation planning and stealth remain future work.

## Treatment

Battle supplies are owned inventory copies. One conscious character spends their main action on a conscious ally within distance 1 and line of sight, including themselves. The whole party shares a maximum of three supply uses per battle. Healing caps at maximum HP; supplies cannot revive, cannot target enemies and are removed from inventory immediately. An inventory compare-and-update rejects a stale competing spend. Auto-battle never consumes supplies.

| Supply | Effect | Camp price |
| --- | --- | --- |
| Field Dressing | Restore 18 HP; remove Bleed | 8 gold |
| Restorative Tonic | Restore 32 HP | 18 gold |
| Cleansing Salts | Remove the listed negative conditions; no healing | 14 gold |

Dressing is in ordinary E+ loot; the other two begin at D. Their existing-art aliases preserve filenames and avoid blocking playable tools on an art generation pass.

Medic or Medicine proficiency grants Field Care (8 + half INT HP, remove Bleed, distance 1). Medic Coat gives a stronger 12 + half INT version. Garden Healer's Pin cures Poison and heals; Mourning Censer heals and clears Burn/Blind; Oathkeeper's Ward clears binding, Freeze, Mute, Charm and Confuse. New faction keepsakes offer ally Guard, discharge cleansing or physical Roadside Treatment. These are selectable techniques under the existing Skill action. All techniques on a unit share one use per battle, not one use per equipped item. Physical treatment works while muted; magical support does not. Auto tactics use support on badly hurt/afflicted allies before ordinary combat routing.

## Conditions

Status hover text describes the actual effect and remaining activations. Activation effects are stamped in the saved battle so movement clicks, UI mode changes and polling cannot reroll them or repeat healing. Reapplication refreshes the same status rather than stacking copies. New control applications last at most three activations; Stun/Sleep/Freeze/Paralyze last only one on bosses, followed by one recovery activation immune to those controls.

| Condition | Current rule |
| --- | --- |
| Stun / Sleep | Lose the activation; ordinary Sleep wakes on direct damage |
| Freeze | No movement; take 25% more direct damage; Fire removes Freeze |
| Paralyze | Seeded 30% chance to lose activation; otherwise no movement |
| Bind / Slow | No movement / movement reduced by 2, minimum 1 |
| Blind | Accuracy −35 points for ranged/magic, −15 for melee |
| Mute | Prevent magical basic attacks and spells; physical actions remain usable |
| Bleed | Physical attack or movement causes one 2–4 damage tick at activation end |
| Poison / Burn | Existing once-per-activation damage and expiry |
| Charm | AI temporarily treats the source's enemies as its targets; original team and prisoner identity remain unchanged |
| Confuse | Seeded 35% chance to redirect an attack to another in-range conscious unit, possibly an ally |
| Berserk | AI may attack either side; +3 direct damage and −10 accuracy |
| Fear | Cannot step closer to its source; −15 accuracy |
| Vulnerable | The next direct hit ignores 3 additional armor |
| Regeneration | Restore 5% maximum HP (minimum 2) once at activation start; Burn suppresses it |

Existing Winterglass Grimoire, Weighted Sling, Goblin Net Bow, Hunter's Bola, Goblin Notched Axe and Prism Tuning Fork now have distinct low-chance control/status hits. Nonlethal attacks do not apply damaging weapon procs. Not every listed condition has a new player-acquirable source in this pass; the rule and presentation exist for authored weapons/enemies/skills to use.

## Validation and limits

Tests cover capped healing, range/ownership/no revival, shared technique and supply budgets, immediate durable consumption, polling idempotence, boss control recovery, Charm ownership, Blind, Fire thawing, quiet auto preparation and roster-independent rank budgets. Existing strategic Warcamp validation remains separate from persistence tests. Broad player win-rate tuning, consumable carryover between adventure floors and adding sources for every condition remain follow-ups; current numbers are a first balancing baseline.
