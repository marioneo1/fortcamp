# Bush concealment

Implemented in development October 3, 2026. Production remains on its separately prepared release.

## Rules

An enemy who starts unseen in a bush is omitted from the map, initiative strip,
target previews, context actions and battle response. The server rejects attacks,
techniques, capture attempts and throws at unseen targets, including guessed IDs.

A conscious, unextracted party member spots enemies within two Manhattan tiles
when there is clear line of sight. Walls, closed gates and high terrain still
block sight using the existing combat trace. Moving out of bush cover or making
an attack (even a miss) also reveals an enemy. Dead and unconscious enemies remain
visible for body interactions. Once spotted, a character stays visible throughout
this battle; stepping into another bush does not hide them again.

Unseen enemy tiles appear open in movement previews, avoiding an occupancy hint. Actual movement checks each step and pauses at the first new sighting.
The player retains their main action and can change their plan. A combined move
and attack is likewise interrupted by newly discovered opposition without
spending the attack. Units cannot overlap a hidden enemy. Sighting persists in
saved battle state, including after provisional movement is changed.

Auto battle and independent party behavior target spotted opponents only.
When none are visible, auto battle checks unsearched brush instead of selecting
an unseen enemy's coordinates. Hidden enemies still count toward objectives and
prevent premature battlefield clearance, victory and automatic loot.

This is first-sighting concealment, not a complete stealth system. It does not
hide friendly units from enemy AI, add sneak damage, permit re-hiding, or add
perception rolls. Enemy stat budgets, loot tables and ordinary ambush sleep rules
are unchanged. Already-progressed older saves preserve their presented enemies.

## Map authoring and testing

Use a walkable terrain/decorative entry with `conceals_units: true` or `kind:
"bush"`. Existing `dense_shrub` and `thorny_bramble` sprites also count as brush.
Footprints cover all occupied cells. Destroyed or carried entries do not conceal.
Plant beds, trees and unrelated clutter are not automatically concealment.

Highway Ambush now has two deliberate brush layouts, alongside its two open-road
layouts. Both brush layouts have two escorts in walkable roadside pockets and
leave deployment cells, road passages and exits usable. `bush_ambusher: true`
lets an unseen enemy wait in cover until a target is within movement plus weapon
range. It then uses ordinary movement/attacks, rather than teleporting or receiving
a free attack. Panic, sleeping-camp rules and control statuses retain priority.

Open Battle Lab in dev, choose Highway Ambush, then choose either preset whose
label starts with **Brush ambush**. Launch a fresh preview. Approach roadside
brush or end turns to see enemies wait and spring their ambush. No new image pack
is required: this pass reuses the installed painted bush props.

## Validation

Dedicated tests cover response/initiative/log/animation filtering, guessed-target
rejection, hidden occupancy previews, stepwise discovery, persistent sightings,
wall obstruction, attack/cover-exit/body reveals, waiting AI, auto searching and
all four real road presets. Combat movement, weighted elevation/water costs,
wall boundaries, ordinary ambush sleep and mission resolution are checked with
the existing regression tests.

Validation completed: 150 targeted backend checks passed, followed by 56 checks after the final command-authorization adjustment (including 11 concealment cases). All 142 frontend tests and the production frontend build pass. With a deliberately strong test character, auto battle completed all four road variants; this checks completion, not rank balance. No real player saves were used.
