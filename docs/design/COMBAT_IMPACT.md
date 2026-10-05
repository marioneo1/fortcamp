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

Colors are accompanied by words and distinct symbols. Short rings and particles
provide impact without obscuring the portrait. Barrier has a persistent blue
shell and visible remaining capacity; Guard has a separate dashed gold outline.
Existing hover cards still give complete status explanations.

Melee impact lands at 185 ms. Associated knockback starts at that moment and
lasts 220 ms; collision feedback arrives at the end of that movement. Attack
coordinates are captured before displacement so the lunge aims at the original
position. A lethal collision carries the living portrait into the collapse.
Subsequent enemy animations wait for the current action/death to finish. Floating
labels can linger without delaying turns. Sounds use the same timeline.

Effects use resolution-independent DOM/CSS/Web Animations and existing projectile/
death effects. No new sprite atlas is needed. Reduced-motion mode keeps text but
omits rings/particles. Timers and temporary nodes are cleared when leaving battle.

Four ElevenLabs one-shots were generated as `combat-impact-v1`: Burn tick, Poison
tick, Barrier absorption and collision. They use the existing Battle volume
channel at restrained gain. WAVs were checked for nonempty 48 kHz mono output and
zero clipped samples. Automated audio checks do not judge aesthetic quality;
the audition page is `/assets/sfx/preview-combat-impact-v1.html`.

## Verification and limits

88 related backend tests and 197 frontend tests pass. New checks cover solid/
person/friendly collisions, barriers, resistance, boundaries, crossing hazards,
overkill numbers, event order, shared sound/visual timing and visible protection.
The frontend builds with the existing large-chunk warning. An isolated real UI
fixture verifies floating labels, shield capacity and particles without touching
player saves. Production is unchanged.

There is no general physics engine, obstacle collision damage, knockback chain,
screen shake, or new status stacking rule in this pass. More distinct skill art
can be added to this event system later without changing damage resolution.

Design reference: [Xbox Accessibility Guideline 103](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/103)
recommends conveying essential information through more than color alone.
