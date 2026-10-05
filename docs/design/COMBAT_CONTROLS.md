# Combat controls and targeting

Implemented in dev, October 4, 2026.

## Movement and finishing turns

Provisional movement remains reversible until the character uses an action or
ends the turn. Returning to the original tile restores the original position
and movement budget. The return route respects contact discovery rather than
teleporting through unseen enemies. Position changes never award extra actions.

Space ends the activation. If the main action is unused, the character guards
automatically, including after movement. G is an explicit shortcut to the same
defensive finish. No free Guard after attacking or using another action. Guard
reduces the next direct damaging hit by 25%, consumed by that hit and cleared
at the character's next activation. Damage uses integer rounding; damage-over-
time and environmental falls bypass Guard. Existing guard equipment effects
use the same finish. This changes the prior 50% rule.

## Skills and targeting

The map hotbar replaces the ability dropdown and duplicate selected-skill button.
Job actives appear first, then all equipment/proficiency techniques. Number keys
1-9 and 0 select ten skills on the current page; C or Escape cancels skill
targeting and returns to Move. Artwork fills each 64px button; names sit below. Arrows expose further pages
without restricting gear abilities. Hover/focus explains source, range, target,
description and availability. Passives remain inspectable in the sidebar.

Pure zone skills can target actual ground, including empty cells. Other attacks,
status spells and support spells retain unit targets. No new arbitrary area
damage or ground-target damage semantics are implied. Valid cast cells, exact
clipped area, crosshair, approach path and casting destination are shown.
Terrain/void/water exclusions use the engine's actual zone-cell rules. Pure
self forms/deployments outline the caster. The active summon still chooses its
existing legal adjacent placement; this is not a new deployment placement UI.

Offensive, allied support and ground casts can include a server-validated move
within the provisional movement budget. Preview and execution use the same
range/sight/target rules. Mute, availability and useful ally-target checks still
apply. Discovery during movement interrupts the approach before casting.
A combined cast submits skill ID, target or cell, and optional destination; the
client never supplies range, effects, area cells or movement allowance.

Hold the right mouse button to drag/pan the map. Wheel zoom and existing Fit
remain; releasing or cancelling the pointer ends the drag. Hovering/focusing
a visible unit opens a viewport-clamped status card with HP, armor, movement,
status explanations and remaining durations. Hidden enemies are still omitted.
Vulnerable explicitly means the next direct hit ignores three armor.

Movement, melee, projectile and death animations reserve their place in the
existing timeline. The following enemy animation waits rather than starting
during a preceding projectile or death effect. This changes presentation, not
the deterministic server turn rules. Polling/skill changes do not spend turns.

## Design reference and verification

Larian's [skill creation documentation](https://docs.larian.game/Skill_creation)
distinguishes area radius, valid unit targets, ground targeting and trajectory
preview. Fortcamp applies that distinction to its existing square grid and
authored effect vocabulary, rather than importing another game's skill system.

78 related backend tests and 192 frontend tests pass, plus the frontend build
(existing bundle-size warning). Additional backend cases verify ground area
preview versus actual cast, combined allied support, return-to-origin and 25%
Guard. Isolated browser checks verify number keys, overflow pages, unit status
cards, right dragging, exact area highlights, self markers, destination markers
and enemy movement/projectile ordering. Fixtures do not modify real saves.
Production has not been deployed. Further authored AoE shapes and art remain
future work; fixed tactical icons are used for this pass.

Subsequent impact pass: COMBAT_IMPACT.md documents typed damage feedback, shield
capacity/halos, half-hit collisions and knockback beginning at the melee impact.

## October 5: Layout A and Fighter targeting

Implemented map-first layout with a bottom actor/skills/actions dock and field
inspector. Primary actions retain painted icons and boxed shortcuts; End Turn
adds hourglass artwork. Auto One Turn and Auto Resolve Battle remain visible.
Map options/supplies are expandable; right-drag, wheel zoom and skill paging
are retained. Fit subtracts dock height. Earthbreaker previews a landing,
walking approach where required, nine inner cells and sixteen outer cells
(clipped by map/sight), with amber rings. Hold Together highlights its self
marker and two-cell rally area. Chain Snare uses three-cell square reach.

## October 5: larger controls and readable Layout A

The six primary commands now live in a two-column right-hand panel, with 40px
artwork, boxed hotkeys and 64px button height. The bottom dock contains the
acting character (76px portrait) and 88px square skills (80px at narrower desktop
widths). The title, horizontally scrollable enlarged turn order and objectives
share one header row on wide screens. Smaller screens wrap rather than squeeze
these sections. Action Preview stays directly under the command panel at 15px
with generous line spacing; button hover and keyboard focus preview descriptions,
and leaving restores the selected action. Other right-hand labels and status
text are larger. The sidebar height follows its actual screen position and
scrolls independently; map fit still reserves the dock. Existing combat bindings,
auto controls, targeting, hotkeys and rules are unchanged.

Validation: frontend build, 205 frontend tests and isolated browser inspection
at 1440x1100 and 1440x900. All six command buttons retain icons/keycaps; skill
art fills the enlarged squares; Fighter previews/contact/C cancellation still
work. Production and saves are unchanged.

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


### October 5 hotbar readability
Cooldowns appear as a large centered remaining-turn number over faded art.
Unlimited ready skills have no Ready badge. Limited-use counts remain visible;
hover help and accessible button names retain the reason a skill is unavailable.
The countdown remains visible after using the main action. Bottom Layout A
command descriptions use 18 px text.


### October 5 status readability
The bottom command dock separates Buffs/Debuffs with 40 px square painted icons,
short names and duration/absorption/one-use badges. Map units show two priority
24 px icons plus an overflow count; unit hover shows every effect. Hover/focus
on a status opens its own readable description. See
[Status presentation](COMBAT_STATUS_PRESENTATION.md) for the current rules and
persistent Stun orbit. Existing ability targeting and combat rules are retained.
