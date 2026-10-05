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
1-9 and 0 select ten skills on the current page; arrows expose further pages
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
