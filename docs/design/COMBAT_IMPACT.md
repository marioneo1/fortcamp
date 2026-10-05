# Combat impact and damage feedback

Implemented in development on October 4, 2026.

## Collision rules

A damaging push/pull that stops against a solid wall, blocking object or active
person adds collision damage: half the preceding resolved hit, rounded down with
a minimum of one. The hit has already considered armor, Guard and Barrier. The
collision bypasses armor and Guard so these are not applied twice; a remaining
Barrier can absorb it. A fully absorbed original hit causes no collision damage.

When the obstacle is a person, both take that amount. Allies can be hit. The
second person is not displaced; there is no chain reaction. A wall in front of a
person prevents hitting that person. Resisted movement, map boundaries and
impassable height alone do not deal this extra damage. Damage-free pulls stay
damage-free. Authored pit rules still apply separately. Friendly damage does not
grant player damage/kill credit.

## Burning ground

**Scorch** applies Burn to a unit; it does not burn the floor or deal an immediate
hit. **Ember Ground** creates an Ember Patch. A hostile committed crossing deals
3 damage and applies Burn once per activation, even when the route ends outside
the patch. Forced movement also checks crossed cells. Standing in it at activation
start applies Burn; the normal Burn tick deals 2–5 damage based on maximum HP.
That start does not also apply the 3-point entry hit. Allies are safe.

Overlapping patches and repeated crossings do not multiply entry damage during
the same activation. Provisional movement/target previews do not trigger damage.
Barriers absorb zone damage. Water can remove Burn through existing entry rules.

## Presentation

The server sends resolved presentation facts alongside existing animation events.
Floating numbers show actual HP lost, not overkill; absorbed damage has a separate
shield annotation. Capture displays Subdued rather than the internal capture
damage number. Healing, barriers, statuses, misses, physical/magic/elemental
hits, Burn, Poison, Bleed, thorns, collisions and falls have readable labels.

Colors are accompanied by words and distinct symbols. Painted hit sprites and
short particles provide impact without obscuring the portrait. Barrier has a persistent blue
shell and visible remaining capacity; Guard has a separate dashed gold outline.
Existing hover cards still give complete status explanations.

Melee impact lands at 185 ms. Associated knockback starts at that moment and
normally lasts 220 ms. Solid collisions use a 420 ms bounce, with feedback at
220 ms contact; immediately blocked targets contact at 100 ms during a 320 ms bounce. Attack
coordinates are captured before displacement so the lunge aims at the original
position. A lethal collision carries the living portrait into the collapse.
Subsequent enemy animations wait for the current action/death to finish. Floating
labels can linger without delaying turns. Sounds use the same timeline.

Effects use resolution-independent DOM/CSS/Web Animations and existing projectile/
death effects. Presentation V2 adds painted icon/effect atlases. Reduced-motion mode keeps text but
omits rings/particles. Timers and temporary nodes are cleared when leaving battle.

Four ElevenLabs one-shots were generated as `combat-impact-v1`: Burn tick, Poison
tick, Barrier absorption and collision. They use the existing Battle volume
channel at restrained gain. WAVs were checked for nonempty 48 kHz mono output and
zero clipped samples. Automated audio checks do not judge aesthetic quality;
the audition page is `/assets/sfx/preview-combat-impact-v1.html`.

## Verification and limits

96 related backend tests and 203 frontend tests pass. New checks cover solid/
person/friendly collisions, barriers, resistance, boundaries, crossing hazards,
overkill numbers, event order, shared sound/visual timing and visible protection.
The frontend builds with the existing large-chunk warning. An isolated real UI
fixture verifies floating labels, shield capacity and particles without touching
player saves. Production is unchanged.

There is no general physics engine, obstacle collision damage, knockback chain,
screen shake, or new status stacking rule in this pass. See ../art/COMBAT_PRESENTATION_V2.md for the delivered icon/effect art and
remaining bespoke presentation work.

Design reference: [Xbox Accessibility Guideline 103](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/103)
recommends conveying essential information through more than color alone.

Fighter-first follow-up: see FIGHTER_COMBAT_REVIEW.md for overlay ordering,
separated overlapping numbers, exact corpse handoff, stronger rebound and new
body collision sound. Shared AOE/barrier art is not an approved final direction.

## October 5: Fighter disruption

Earthbreaker first resolves physical impact against every enemy in its landing
area, then attempts knockback in snapshotted inner-before-outer order. This
preserves enemy-body collision opportunities and existing half-hit/pit rules.
Its 420ms leap precedes the shared landing packet; individual collision contact
markers follow displacement. Chain Snare stops before the caster's occupied
cell, explicitly preventing accidental caster collisions. Other pull skills
retain their existing rules. Generated chain/earth-impact components, animated
chain links and a short rally wave are in combat-fighter-v3. Damage overlays stay
in front. The broader rejected persistent-ground/Barrier redesign is deferred.

## October 5: Fighter power and wave contact

Driving Strike now uses 150% attack power and stuns surviving solid-collision
participants for one activation. Chain Snare adds nonstacking 30% armor loss for
two target activations. Earthbreaker uses 200% attack power, with per-target
contact markers following the expanding wave after landing. Existing cooldowns
and defensive rules remain. See [Fighter review](FIGHTER_COMBAT_REVIEW.md) for
exact rules, balance proposals and validation. Fresh battles use these changes;
existing snapshots and production are unchanged.

## October 5: animation ordering and input lock

Each token has one composed motion timeline: original position, contact/push,
then later enemy movement. Later motions no longer prefill their positions.
Commands and hotkeys wait for resolved attacks and all enemy motion to finish;
a Resolving turn notice indicates the pause. Pure player movement previews
remain interruptible, and lingering damage text does not block input. See
[Fighter review](FIGHTER_COMBAT_REVIEW.md) for the bug and browser validation.

## October 5: bottom commands and hover forecasts

The full-width map now has commands beside skills in a three-by-two bottom box,
with action guidance below it. Unit stats/statuses and direct-hit forecasts are
in hover/focus cards. Supplies/passives/history/options open centered
dialogs. Wheel/right-drag camera controls remain, with one small map-fit button.
See [Fighter review](FIGHTER_COMBAT_REVIEW.md) for forecast limits and validation.

## October 5: motion continuity and cursor forecasts

Walking endpoints use each segment destination; interrupted previews settle before
attacks. The playback notice does not resize the map. Full landing waves and all
push/rebound/collapse motions conclude before subsequent turns. Stats follow the
cursor and vanish on leaving a unit. Area forecasts show affected visible units
with staggered labels; direct-hit forecasts use defenses without changing state.
See [Fighter audit](FIGHTER_COMBAT_REVIEW.md) for tested cases and limitations.

## October 5: lethal knockback and movement origin (implemented in dev)

Driving Strike and Earthbreaker retain their displacement when the impact kills
the target. A body can strike a solid object or living bystander; the surviving
bystander takes half the original impact damage and collision stun, subject to
existing immunity/resistance. Earthbreaker now declares collision stun as well.
Open-ground pushes do not stun. Corpse HP is not damaged a second time and no new
status is applied to a corpse. Bodies do not trigger ground damage/traps on their
forced route; lethal pits make pushed bodies unrecoverable. Death facts use the
final forced-movement cell, and presentation completes push/rebound before
collapse. Enemy playback continues afterward. Misses do not displace targets.

The provisional movement origin remains marked with a gold outline and START
label, including after choosing another destination. It resets when the movement
is committed or a new activation starts. Attack-sequence walking again has the
small 5 px hop, 2 degree tilt and scale change already used for free positioning;
forced movement remains a slide. This preserves the endpoint/rubberband repairs.

Validation: 114 related backend tests and 220 frontend tests pass. Isolated browser
checks confirm both lethal Fighter collisions finish motion before collapse,
restore the corpse marker, stun the living bystander without stunning the corpse,
and render the origin label. Tests cover open-ground lethal push, walls, a killed
bystander and stun immunity. Build passes with the existing bundle-size warning.
Use a new battle for the updated Earthbreaker skill definition; existing battles
retain skill snapshots. No production or live saves changed.

## October 5: melee attacks against structures (implemented in dev)

Standard melee attacks against weapon racks, walls, gates and other destructible
terrain now emit a real melee swing, sharing its contact packet with structure
hit/break sounds. The renderer can animate an attacker whose target is terrain,
including terrain destroyed by that hit; it no longer requires a character token
for the target. Magical structure attacks also emit their existing projectile.

Validation: 120 related backend tests, 220 frontend tests and build pass; the 46-test
location/wall/Fighter/audio subset also passes. An isolated browser test checks
the rack lunge at the 185 ms contact marker and the playback input lock. Tests
cover surviving and destroyed racks. Existing bundle-size warning remains.
Dev only; no production or live saves changed.

The screenshot-only pathing report near the lower corner/door was not reproduced
by the player or in fresh-map checks. Deferred to the planned map/pathing rebuild
at the player's request. No speculative collision changes or snapshot tool added.
Walking is unchanged in this pass: free movement and attack-sequence walking use
a 5 px midpoint hop, 2 degree tilt and 2.5% scale change; their keyframe phase is
not identical. Forced movement remains a slide. Preserve these approved amounts
and disclose future changes to their presentation.

## October 5: painted commands and attached Chain Snare (implemented in dev)

Chain Snare uses the shared contact timeline: hook reaches the target at
220 ms, follows its rendered position through forced movement/rebound and fades
after recovery. It receives the complete event batch even after the battle's
pending event list is consumed. Misses retract and play miss audio.

Preview and resolved movement share solid-contact geometry. Forecast collision
power is half of predicted post-Barrier direct damage; bystander Barrier is
shown separately. Map edges and height limits are not solid impacts. Hidden
bystander names are omitted. Forecasts remain conditional on hit, resistance,
survival and reactions.

Earthbreaker's area attack no longer falls through to generic `magic_cast`.
Its landing gain is 0.65 plus a new 0.38 crater layer at the same impact contact.
See [Fighter review](FIGHTER_COMBAT_REVIEW.md) for verification and limitations.

## October 5 follow-up: collision recovery before the next attack

Collisions retain their existing travel/contact times and distances, but hold
the compressed contact pose for 70 ms before rebounding. The struck bystander
has a 240 ms recoil with a visible compressed-pose hold. Shared packet recovery
now includes both the forced movement and collision recipient recoil. A 100 ms
settling interval precedes the next attack/move; collapse also waits for complete
packet recovery. Walking hop/tilt, basic melee timings and gameplay are unchanged.

A full backend command fixture pulls an enemy into an ally and immediately gives
that enemy its turn. Browser sampling verifies contact, both rebounds, neutral
settling, then the enemy lunge. Command input remains locked during playback.
Frontend regression tests check the same sequencing and lethal/stationary cases.
Fixture/review script: `staging-ui/combat-fighter-review/pull-followup-qa.mjs`.
