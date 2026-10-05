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
