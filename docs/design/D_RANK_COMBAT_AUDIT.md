# D-rank combat audit

Implemented in dev October 9, 2026. First batch: Highway Ambush, Bone Patrol,
Boar-Rider Patrol. Four variations each; start a fresh battle to use them.

## Boar-Rider follow-up

Patrol riders now own real boars rather than a permanent movement flag. Both
bodies take 25% less damage while mounted; +1 movement. Mount loss rolls
25% hard (half mount max HP + Stun), 50% rough (quarter + Hobble), 25% safe;
control lasts one turn. Rider perk persists through recruitment.
Three layouts start mounted; fourth mixes mounted riders and adjacent boars.
16-HP boars (12 HP in the four-rider layout) have no separate mounted attack turn.
24 D-ranked all-6 Human duo smoke fights across six Jobs: 20 wins, 4 defeats,
no stalls/errors. These replace neither the historical audit nor player testing.
See [Animal mounts](ANIMAL_MOUNTS.md) for precise mechanics and art.

## Current rank rule — shared migration

Rank scales **allocated attributes once**, then bonuses apply and the shared
formulas derive ordinary HP/Attack/Armor. New captures retain raw allocations
plus Adventurer Rank; legacy captures are not inferred or ranked again. Role
movement/range, percentages, cooldowns and species exceptions remain.
[Canonical rules](SHARED_COMBAT_STATS.md); the [396-fight audit](SHARED_COMBAT_STATS_AUDIT.md)
includes all twelve D layouts with D-ranked Human sample parties. Every D layout
also has recruitment parity checks. Promotion/rebirth UI is not implemented.

## Historical authoring targets before shared migration

The following targets help reconstruct bodies; they are not an extra multiplier
on final combat stats. Exact old HP is not guaranteed.

| Rank | E-relative combat stats |
| --- | --- |
| E | 1.0× |
| D | 1.3× |
| C | 1.6× |
| B | 1.9× |
| A | 2.2× |
| S | 2.5× |

Scale HP, attack, armor and core attributes from the same E-relative role/race
baseline; round to nearest integer, with halves rounding upward. Never multiply
the previous rank. Movement, range, evasion, resistance percentages, initiative,
cooldowns and status durations remain role mechanics. Stats do not adapt to the
player's roster. Perks apply after scaling; capture retains the scaled attributes.

`backend/combat_pacing.py` supplies generic contract budgets (E commander 28 HP /
5 attack; escort 24 HP / 4 attack, then racial adjustments). This replaces the old
steeper rank jumps. The B-rank Redoubt's veteran commander now uses an E-relative
55-HP role baseline at 1.9× (105 HP), rather than a hardcoded 112 HP. This keeps
it above the existing D-rank Warcamp's 72-HP boss; patrol leaders use smaller roles.
Audited E encounters retain their authored kits. The three D encounters below
scale comparable authored E roles: normal 23–28 HP, light-group members 19 HP.
Goblin roles already include their audited racial durability; do not apply
fragility a second time. Undead adds its racial durability/armor before scaling.

This establishes a rank policy, not a completed audit of C–S or every remaining
D mission. Separate boss scenarios such as Goblin Warcamp retain bespoke boss
profiles pending their own audits. Swarms can trade individual stats for more
bodies. Existing saved battles are not retroactively rescaled.

## Twelve variations

| Mission | Variation | Opposition / activity |
| --- | --- | --- |
| Highway Ambush | Rock-cut crossfire | Enforcer, Trapper and Lookout watch two elevated banks. |
| Highway Ambush | Wagon choke and flank | Skirmisher, Enforcer and Lookout guard a blocked wagon lane and southern bypass. |
| Highway Ambush | Broken roadside relay | Trapper, Skirmisher and Enforcer hold the relay approach. |
| Highway Ambush | Raiders dividing the haul | Four lighter raiders sort stolen supplies across the road. |
| Bone Patrol | Funeral avenue | Relic Warden, Shieldbearer and Archer patrol between burial markers. |
| Bone Patrol | Chapel relic transfer | Shieldbearer, Warden and Archer guard relics outside the ruined chapel. |
| Bone Patrol | Graveyard switchback | Warden, Archer and Shieldbearer cover separated plots and collapsed tombs. |
| Bone Patrol | Scattered bone procession | Four lighter bone carriers/scouts spread across the route. |
| Boar-Rider Patrol | Messenger relay stop | Vanguard, mounted Skirmisher and Slinger pause outside the relay office. |
| Boar-Rider Patrol | Open cavalry bend | Skirmisher, Vanguard and Slinger cover a wider road bend. |
| Boar-Rider Patrol | Split weapons convoy | Ringleader, Vanguard and Slinger oversee a weapon cart and bypass. |
| Boar-Rider Patrol | Scattered young riders | Four lighter riders regroup around scattered supplies. |

These use road formations, elevated crossfire, graveyard processions and cavalry
staging rather than E-rank work-yard/storehouse variants. The new timber relay
office has two doors, a desk and supply storage; the chapel uses current boundary
walls/materials. Shared building/prop assets remain consistent with the map tool.
Riders use their mounted movement profile; no new boar-mounted portrait animation
is claimed. Undead use chain impacts and their racial resistances, not human voices.

## Kits and balance

Human roles reuse Shakedown, Tripline/Road Bola, Parting Cut and Mark/Longshot.
Undead Wardens use Heel Cut/Intercept; Shieldbearers use Driving Strike/Intercept;
Archers use Mark/Longshot. Goblin riders reuse Parting Cut, Goliath Shot, Tag Team
and existing frontline skills. Light groups use smaller Rogue/Ranger kits.
No new selectable Job or skill ID was added. Recruitable Humans/Goblins retain
their specialties, personality, perks, voice identity and normal Job starters.

Three-member groups face four lighter members in variation four. Total baseline
HP stays within 15% per mission; different action counts, armor and skills still
require actual combat checks. Most bodies have 25–40 HP before general perks,
instead of a roster of disposable 7–18 HP enemies. Perks can raise/lower this.
Bone Patrol should challenge fragile melee units more than the road raiders.

Scouting keeps the existing three-round ambush preparation mechanic. These
patrols are unaware, not literally sleeping; any attack alerts the whole patrol,
including a miss. Direct/alert/blockade branches, contract rewards and IDs remain.

## Validation and next pass

- Automated tests cover all twelve maps, repeatable seeds, clear/nonoverlapping
  spawns, access to both exits with gates opened, comparable HP budgets, rank
  rounding, preserved role rules and captured starter/specialty continuity.
- `tools/audit_d_rank_combat.py` runs 48 small paired starter martial samples;
  final sample: 46 wins / 2 losses, zero errors or stalls. The two losses are
  Barbarian pairs in Bone Patrol variations 1/2. This is a smoke check, not proof
  of balance for every loadout/support party; smarter mixed parties may differ.
- Regression checks cover mission/recruitment/defense/ambush behavior. Two older
  E-kit tests now account for approved background perks and Shakedown; Driving
  Strike is still verified while Shakedown is cooling. The B boss progression
  check caught and verified the veteran-baseline correction. Authoring brief and
  catalog check passes; map coverage inventory regenerated.
  Final focused run: 90 tests pass; the separate 24-test map/location run passes.
- Manual visual/difficulty review remains. The other D encounters, wider AI and
  personality expansion are subsequent work; avoid heavy solo-support tuning.

For another batch: select three missions, check their story/branches and shared
roles, author four layouts/rosters, validate routes and recruitment, run a small
combat sample, then record playtest feedback here before moving on.

## October 9 follow-up: rider-owned Boar Charge

Rider now describes allied mounts, with species bonuses/techniques. Only boars
are currently available. Mounting a boar adds `innate:rider:boar_charge` to the
rider without consuming an equipped slot; dismount or mount loss removes it.
Boar Charge uses a main action, three-activation cooldown and a clear cardinal
line. Starting target distance 1/2/3/4 gives 1.25/1.5/1.75/2.0 times rider attack
power, stopping adjacent. Only a landed four-cell hit attempts one-turn Stun;
normal Stun resistance applies. Approach hazards resolve on both bodies and
can stop the charge. This is dedicated skill movement, not a normal movement
refill. Existing walking/strike presentation is reused. AI chooses a legal
straight charge before its ordinary attack; no new animal AI framework.
Targeted mount/D-rank checks cover tiers, shared movement, blockers, miss,
immunity, dismount, save/fall outcomes and hazard interruption.

Boar-Rider visual/forced-movement follow-up: living linked bodies now receive one
Earthbreaker/Groundbreaker push per shockwave while both still receive damage.
Mounted corpse flags/layers and playback timing covered by mount/Fighter/browser
checks; no encounter stats, variations or rewards changed. See ANIMAL_MOUNTS.md.
