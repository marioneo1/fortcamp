# Ranger rework — implemented in dev, October 6

Ranger is one Job with Marksman, Poison specialist and hybrid loadouts. It uses the existing five shared active/passive slots, practice unlocks, movement previews, activation clocks, Quick Actions, damage pipeline, resistance, Barrier, equipment procs and AI. No new resource or subclass system. Champions are unaffected.

## Kit and progression

| Skill | Unlock | Action | Cooldown | Rules |
| --- | --- | --- | --- | --- |
| Mark Quarry | Starter | Main | None | Range 5. One quarry per owner, three target turns. All that owner's attacks have 100% accuracy against it. Other Rangers may independently mark it. Walls, interception and inability to act still matter. |
| Longshot | Starter | Main | 2 | Requires own Quarry. Manhattan distance 1–2: 100% attack; 3: 150%; 4: 175%; 5+: 200%. Independent 20% critical roll doubles final direct damage before Barrier. |
| Poison Attack | Starter | Main | None | 150% attack, two Poison stacks or four against own Quarry. Also coats the next successfully damaging attack: one Poison stack per damaging hit. |
| Multi-Shot | 2 successful contracts | Main | 2 | Uniformly rolls 2, 3 or 4 arrows; each 75% attack, independently 50% base accuracy before ordinary modifiers. Own Quarry guarantees every arrow hits. |
| Rapid Fire | 5 | Quick | 4 | Choose an enemy. Uniformly select a legal, available equipped Ranger attack for that target; execute without spending its cooldown. Basic Attack fallback uses the weapon range. Locks normal walking, leaves main action available. |
| Sharpshooter | 9 | Slotted passive | — | After ending a full activation on the starting tile, +10% direct damage and +2 basic/Ranger technique range. Actual committed or forced movement ends it. Moving a preview away and back does not. |
| Pestilence Shot | 12 | Main | 4 | 100% attack. On hit, ATK −25% and all incoming damage +25% for three target turns. Selective authored Pestilence resistance applies. |
| Rupturing Blow | 16 | Main | 2 | 150% attack. A landed hit consumes all owners' Poison/Bleed and cashes out 50% of remaining base damage. Misses consume nothing. |

Cooldowns count personal activations using the existing engine. All seven techniques have five-cell base reach, increased by stationary Sharpshooter. The basic attack retains its weapon's range. A walking approach loses the stationary range bonus before targeting; forecasts use the same rule.

## Decisions and cross-Job interactions

- Mark is a main action. A free, cooldown-free mark would be mandatory bookkeeping instead of a setup decision. Ranger is vulnerable during setup; replacing a quarry has a cost.
- Each new Ranger Poison stack snapshots **8% of effective attack, rounded, minimum 1 HP per tick**, for two target-start ticks. This scales with later weapons instead of making DoT builds obsolete at higher stats. Existing nonstacked equipment Poison retains its original damage when converted to layers.
- Poison imbue is one attack, not one arrow. A fully missed/fully absorbed attack preserves it; a damaging volley spends it and applies one stack per damaging arrow. Poison Attack can consume an earlier coating and create a fresh one.
- Poison resistance applies per stack. Undead/Automaton immunity remains. Durations are independent; new stacks do not extend older ones. Views do not tick or roll anything.
- Generic on-hit equipment effects get one attempt on the first landed arrow; flat equipment/perk damage bonuses have one volley budget. Armor applies to each arrow; finite Barrier depletes across arrows. Hold Together's attack bonus and Iron Reversal's defensive form cover the whole volley, consistent with techniques.
- Pestilence's incoming modifier is additive with Monk direct-hit vulnerability, not multiplied repeatedly. It also amplifies Poison, Bleed, collision and other indirect damage. ATK reduction does not retroactively reduce snapshotted DoTs.
- Rupture uses each actual layer's remaining duration and tick damage. Existing Bleed only damages a victim that exerts itself: its remaining damage is **potential**, assuming future movement/physical actions. Future defensive-status changes cannot be predicted. Compute base potential, halve it once, then apply current damage modifiers once; do not double-amplify Pestilence.
- Longshot and Multi-Shot are alternative main attacks. They are never multiplied together. Critical doubling belongs to Longshot only; this pass does not silently add random crits to every Job.
- Rapid Fire cannot choose Mark, passives, itself, unusable/cooling-down attacks, unmarked Longshot or blocked targets. It does not choose arbitrary enemies behind the player's back. It may fire a technique again as the main action if that technique remains available. No Quick Action after the main action.

## Builds, costs and counterplay

**Marksman:** Quarry / Longshot / Multi-Shot / Rapid Fire / Sharpshooter. Spend a setup action, hold clear firing lanes, punish distance, and use Rapid Fire for occasional extra pressure. Cover, interception, forcing relocation and close pursuit deny its strongest position. Guaranteed accuracy does not ignore armor or Barrier; multi-arrow attacks are less efficient against armor.

**Poison:** Quarry / Poison Attack / Pestilence Shot / Rupturing Blow / Multi-Shot. Build independent Poison layers, amplify party damage, spread an imbue across a volley, or detonate allied Caltrops Bleed. Committing Rupture sacrifices future damage for immediate pressure. Poison immunity, cleansing and forcing an early cashout interfere; direct shots remain usable.

**Hybrid:** Quarry / Longshot / Poison Attack / Rupturing Blow / Sharpshooter. Retains distance burst and DoT cashout, gives up Rapid Fire and party-wide Pestilence. No role restrictions.

## Presentation, saves and AI

Eight painted icons plus eight shared projectile/contact/marker assets: see [Ranger art](../art/RANGER_V1.md). Arrow flight, impact, damage, sound and critical label share existing attack packets. A volley is serialized before subsequent enemy movement. Tooltips identify the mark's owner; Poison stack counts, Pestilence and Sharpshooter appear in the existing status UI. Forecasts explain 2–4-arrow totals, critical damage, Rapid Fire's pool and base DoT cashout.

Old Ranger choices migrate: Track Quarry → Mark Quarry; Snaring Ground → Multi-Shot; Footwork/Steady Position → Sharpshooter; Poisoned Dart → Poison Attack; Dust Shot → Pestilence Shot. Duplicates collapse. Learned choices, practice and saved ordering remain; three starters are learned, not forcibly inserted into a full five-slot loadout. Existing in-progress battle snapshots are not rewritten.

AI uses one movement tree and a bounded target/skill scan. It values setup on durable targets, usable ranged damage, Poison immunity and existing Pestilence. After Rapid Fire it recomputes legal stationary choices; stale walking approaches are discarded. This is a practical heuristic, not a full future-DoT planner. Hidden enemies are not revealed by forecasting.

## Validation and remaining work

Backend regression suite covers Jobs, Battle Lab, combat abilities/conditions, movement, deployments, martial/Monk/Rogue, audio and impact. Ranger-specific tests cover ownership/expiry, range, crit/Barrier order, multi-hit budgets, independent stack ticks, immunity, allied cashout, party/DoT vulnerability, Quick Action sequencing, stationary movement, pure views, AI and migration. Frontend tests and a real Chrome fixture check both five-slot builds, art/status loading, serialized projectile contact and cleanup. Art crops were visually reviewed; custom gutters avoid adjacent effect-row contamination.

Numerical playtesting across ranks remains necessary. Poison stacking, Pestilence and Rapid Fire deliberately allow strong team setup. No production rollout, save reset or new Champion kit is part of this pass.

Validation results: 235 combined backend regression tests passed, followed by all 36 Ranger-specific checks after the final fallback-range refinement; all 297 frontend tests passed. The frontend build and real Chrome Ranger fixtures passed. The existing bundle-size warning remains.
