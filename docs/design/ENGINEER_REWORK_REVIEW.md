# Engineer — implemented in dev, October 7, 2026

Engineer converts preparation time into stationary machinery and route denial.
This replaces its Components/shared-output-budget Job kit. Legacy gear deployments
retain their rules; Summoner remains the mobile creature Job. Five character slots
still apply. Multiple Quick Actions may precede the main action, which ends the turn.

| Skill | Unlock | Action / cooldown | Behavior |
|---|---|---|---|
| Sentry Turret | Starter | Main / none | Two further full working activations after starting; three active slots. |
| Dynamite | Starter | Main / 1 after explosion | Range three, next owner turn fuse; one-cell square blast, 200% ATK, push one, 75% Stun; failed Stun attempts Hobble. Friendly fire. |
| Rapid Assembly | Starter | Quick / 5 when consumed | Next turret build this activation completes instantly. Walking remains available; unused preparation expires freely. |
| Man the Guns | 2 successes | Quick / none | Mount adjacent owned machinery with clear approach; changes to Exit Emplacement. Both lock further walking that activation. |
| Heavy Emplacement | 5 successes | Main / none | Three further full working activations after starting; one active per owner. |
| Proximity Charge | 9 successes | Main / 4 | Empty ground within two cells, maximum two. Any team's entry within one square cell triggers, including forced movement. |
| Overclock | 12 successes | Quick / 5 after failure | Two shots this activation and next; no exit. Breaks at second following activation start; early destruction starts cooldown too. |
| Scuttle Protocol | 16 successes | Main / 4 | Destroy a selected owned machine; two-cell square blast for 50% owner max HP before mitigation, ignoring armor. Own blast leaves 1 HP; ejection/collision/hazards can kill. |

## Construction and machinery

Choose empty legal ground within two cells and sight. Construction locks walking
and other actions except Guard/end turn or deliberate cancellation via a build skill.
Damage does not cancel; hard control pauses work; displacement cancels. An unfinished machine immediately reserves the tile and can be attacked; completion preserves its remaining HP. The start action is preparation, not one
of the following working activations. Accelerando affects spell channeling, not builds.
Unfinished machines have the same HP/armor as completed machines and cannot fire or be mounted. Their destruction cancels construction and immediately frees the slot. Battle completion discards unfinished work.

Sentry: 2 HP, armor max(30, twice owner ATK), range four, 75% owner ATK automatic
bolt each owner turn. Normal flat armor/minimum damage applies; comparable hits
typically deal 1, but overwhelming damage, piercing and DoTs can destroy it faster.
Heavy: ceil(50% owner max HP), owner armor, range seven, 150% ATK primary hit with
half-power cardinal splash hitting either team with sight, every second owner turn.
Automatic fire starts next owner turn after completion. Machines cannot be displaced,
have independent firing cycles, and release their active slot when destroyed.

Manual Attack fires Sentry at 125% owner ATK/range seven or Heavy at 200%/range seven
without loading. Occupied machines never also fire automatically. Overclock supports
four shots across two activations. Engineer portrait occupies the generated seat;
the separate token is hidden. Aimed weapon hits route to machinery; area, status,
environmental and collision damage can reach the operator. Exit chooses a legal
cardinal tile. Destruction restores the Engineer profile and selects an emergency
adjacent exit, falling back to the former machine tile. Nonblocking wrecks begin fading next battlefield round and disappear the following round. Scuttle ejects toward the entry side up to three cells through normal
collision/entry resolution, ignoring displacement resistance, stopping at obstacles.

## Hazards, interface and persistence

Mines cannot be placed where their trigger area touches an enemy. Damaging AoEs detonate mines; aimed ranged attacks cannot select them. Mines trigger on real entry, not stationary checks. Trap Expert bypasses triggering.
Guaranteed mine Stun bypasses partial chance resistance but respects full immunity.
Immune victims still stop and cannot initiate damaging actions for that activation;
utility remains legal. Mine removal precedes blast resolution to avoid duplicates.
Routes truncate at interruption; offensive spells stop before casting after a mine
interrupts committed movement. Known mines appear in route forecasts, hidden enemy
mines do not. Forecast damage excludes later tiles beyond the first known mine.
Dynamite's dead-owner fallback detonates at a later round's activation start.

Turret placement has legal highlights, unfinished art, and a draggable window whose position is remembered; E confirms and C/Escape/right-click cancel. Invalid cells use the X cursor. Dynamite, mines, mounting/exit, Rapid Assembly and Scuttle use direct map targeting without confirmation windows. AoE previews show damage and friendly fire; mine previews show the trigger footprint. Scuttle can target an owned machine without mounting; only a mounted operator is ejected. Statuses explain builds,
occupancy and Overclock; active slots and shots remaining are visible. Generated
ready/fire/recoil/wreck art uses existing turret playback and upright operator portraits.

Old Engineer skill IDs migrate idempotently, preserving order, learning and practice.
No schema change/save reset. Battle snapshots retain their kit; use a fresh Lab
encounter. Starter is Sentry/Dynamite/Rapid Assembly; Lab loadouts expose all eight.

AI is conservative: lowest-HP visible turret targeting, construction/Guard, legal
manual fire, and Dynamite only without allies in the planned blast. Personality,
advanced placement/mine tactics/mounting priorities remain deferred. Heavy targeting
does not yet score the friendly-fire splash tradeoff.

## Validation

424 relevant backend tests and 373 frontend tests pass; frontend build passes.
Isolated browser QA checks remembered dragging/E confirmation, direct targeting, unfinished machinery, delayed wrecks and mine explosion timing; Summoner placement remains covered.
The broader discovery run terminated natively during map-variant reachability and
is not reported as a full-suite pass. Live saves and production were untouched.
Heavy shots use a dynamite-tipped bolt, cross-shaped explosion and dedicated ElevenLabs impact. Skill hotbar icons use the v2 packed artwork; combat descriptions are one sentence, with full definitions retained separately.

Art/audio provenance: [Engineer art](../art/ENGINEER_V1.md).

## Rapid Assembly feedback and Dynamite recovery

Rapid Assembly now emits a brief amber gear/check/spark cue, a dedicated mechanical preparation sound and Instant build ready text, with a visible preparation buff until consumed or activation end. Movement and main action remain available; its existing cooldown still begins only on a successful instant build.

Dynamite has one recovery turn starting when it explodes: thrown on turn N, explodes on N+1 and cannot be thrown that turn, ready again on N+2. This prevents an uninterrupted throw/explosion loop with one Engineer. The wider cooldown convention is unchanged.

Dynamite presentation: throws emit an explicit hazard snapshot and origin. The Engineer winds up for 180 ms, the bundle follows a 420 ms arc and lands at 600 ms; the 700 ms playback interval completes before following actions. A charge created and detonated in the same server response is reconstructed from its snapshot and remains visible from landing to explosion. Existing fuse and recovery rules are unchanged.
