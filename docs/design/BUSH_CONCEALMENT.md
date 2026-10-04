# Bush concealment

Implemented in development October 3, 2026. Production remains on its separately prepared release.

## Rules

An enemy who starts unseen in a bush is omitted from the map, initiative strip,
target previews, context actions and battle response. The server rejects attacks,
techniques, capture attempts and throws at unseen targets, including guessed IDs.

Proximity and line of sight alone do **not** reveal an enemy, even from an
adjacent cell. Moving out of bush cover or attacking (even a miss) reveals them.
Trying to enter their occupied cell creates physical contact, reveals them and
stops movement before an overlap. Dead and unconscious enemies are visible for
body interactions. Once revealed, a character stays visible throughout this
battle; stepping into another bush does not hide them again.

Unseen enemy tiles appear open in movement previews, avoiding an occupancy hint.
Movement checks each step and pauses on physical contact with a hidden occupant.
The player retains their main action. A combined move and attack likewise pauses
without spending the attack. Sightings persist in saved battle state, including
after provisional movement is changed. Merely walking beside brush does not
trigger a free enemy reaction or give the player a free reveal; surprise attacks
use the enemy's ordinary activation.

Auto battle and independent party behavior target spotted opponents only.
When none are visible, auto battle checks unsearched brush instead of selecting
an unseen enemy's coordinates. Hidden enemies still count toward objectives and
prevent premature battlefield clearance, victory and automatic loot.

This is first-sighting concealment, not a complete stealth system. It does not
hide friendly units from enemy AI, add sneak damage, permit re-hiding, or add
perception rolls. It no longer uses the previous two-tile proximity reveal. Enemy stat budgets, loot tables and ordinary ambush sleep rules
are unchanged. Already-progressed older saves preserve their presented enemies.

## Map authoring and testing

Use a walkable terrain/decorative entry with `conceals_units: true` or `kind:
"bush"`. Existing `dense_shrub` and `thorny_bramble` sprites also count as brush.
Footprints cover all occupied cells. Destroyed or carried entries do not conceal.
Plant beds, trees and unrelated clutter are not automatically concealment.

Highway Ambush now has two deliberate brush layouts, alongside its two open-road
layouts. Both brush layouts have two escorts in walkable roadside pockets and
leave deployment cells, road passages and exits usable. `bush_ambusher: true`
lets an unseen enemy wait for a clear shot from cover or an actually reachable
move-and-strike into the authored road kill zone. It favors direct shots, isolated
targets and wounded opponents. The first attacker signals the rest to spring the
ambush. There are no extra attacks or damage bonuses. Panic, sleep and control
statuses retain priority.

Ambushers wait at most two eligible activations; on the third they abandon the
plan and use normal pursuit AI, including existing gate operation. If no spotted
enemies are left, concealed survivors pursue immediately instead of keeping the
player in an apparently empty fight. The UI says to check brush or end the turn
when opponents remain but none are visible. Ordinary victory checks still count
all living enemies. Physically checked brush cells guide auto battle's search;
looking at a bush does not mark it cleared.

Open Battle Lab in dev, choose Highway Ambush, then choose either preset whose
label starts with **Brush ambush**. Launch a fresh preview. Approach roadside
brush or end turns to see enemies wait and spring their ambush. No new image pack
is required: this pass reuses the installed painted bush props.

## Validation

Dedicated tests cover response/initiative/log/animation filtering, guessed-target
rejection, hidden occupancy previews, stepwise discovery, persistent sightings,
blocked ambush shots, attack/cover-exit/body reveals, waiting AI, auto searching and
all four real road presets. Combat movement, weighted elevation/water costs,
wall boundaries, ordinary ambush sleep and mission resolution are checked with
the existing regression tests.

Validation completed: 150 targeted backend checks passed, followed by 56 checks after the final command-authorization adjustment (including 11 concealment cases). All 142 frontend tests and the production frontend build pass. With a deliberately strong test character, auto battle completed all four road variants; this checks completion, not rank balance. No real player saves were used.

October 4 refinement supersedes proximity-based spotting: adjacency stays hidden, actual attack opportunities drive coordinated ambushes, and bounded waiting/last-survivor pursuit prevent concealment-only stalls. Tests include blocked shots, adjacency surprise attacks and both pursuit safeguards.

Refinement validation: 70 targeted combat/mission checks passed; final concealment/road pass has 20 passing tests, including authored kill-zone attacks and the shared spring signal. All 142 frontend checks and build pass. Strong-party auto checks finish all four road layouts.
