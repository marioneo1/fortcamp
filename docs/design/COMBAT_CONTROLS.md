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

## October 5: painted commands and attached Chain Snare (implemented in dev)

Commands now have 44 px art and 15 px labels, with a wider unboxed section
at the right of the bottom dock. Narrow screens give commands their own row.
One painted atlas adds weapon-aware bow/magic attack art, a leather pointer,
animated hourglass, unavailable X and Chain Snare hook cursor. Playback hides
native map cursors while showing one hourglass; reduced motion keeps it still.
Map status icons are 36 px, wrap above the portrait and retain all compact effects.
Dock status icons are 48 px. Existing keybinds remain.

[Fighter review](FIGHTER_COMBAT_REVIEW.md) records attached chain movement,
collision forecasts, audio correction and browser verification. Atlas source,
prompt and import: `docs/art/COMBAT_CONTROLS_V2_PROMPT.md`.

## October 5 follow-up: target cursors and wider inspection

All weapon targeting cursors are 50% larger than their preceding sizes and face
upper-left: sword, subdue gauntlet, thrown object, bow, magic wand and chain hook.
The hook's actual effect still rotates toward its target; this direction rule is
for the cursor. Native PNGs are derived reproducibly by the existing atlas importer.
Cursor hotspots scale with the artwork; pointer/loading/unavailable cursors are
unchanged. No paid generation was needed.

Selected skills now determine their target cursor from the skill's own targeting
rule and effects: ballistic shots use the bow (including Poisoned Dart/Dust Shot),
magical targeting uses the wand, pulls use the hook, and support/deployment uses
the pointer. Basic attacks retain equipped-weapon selection. Invalid targets and
busy playback retain their respective X/hourglass rather than a weapon cursor.

The unit hover card is 680 px wide within screen bounds. Forecasts and compact
abbreviated stats sit beside effects; a unit without effects uses the full width.
ATK/ARM/MOV/RNG/ACC/EVA/INIT/LVL/ELEV retain full labels in abbreviation titles.
Narrow screens stack the columns. Status-only hover cards remain smaller.

Map status rows now start slightly inside the moving unit's upper-left and wrap
downward, keeping 36 px icons. Browser measured roughly 5 px top / 3 px left inset
at the tested zoom. See [Status presentation](COMBAT_STATUS_PRESENTATION.md).
Validation: 238 frontend tests, build and isolated browser inspection/targeting
checks; review capture `staging-ui/combat-fighter-review/target-card-v3.png`.


## October 5: Direct provisional repositioning

Fixed origin-tree backtracking in immediate movement previews and server movement/attack approaches. The shortest origin tree defines legal destinations and turn costs; it no longer defines the route between two provisional positions. The server exports at most four legal directed steps per reachable tile, respecting occupancy, edge walls, elevation and terrain cost. The immediate preview finds a weighted legal route from the displayed position. Server movement independently checks that route and still stops on concealed enemy discovery. Combined attack/support/ground approaches use the same direct routing.

Movement remains refundable until an action commits, with the original activation origin and budget preserved. Repeated clicks do not refill movement. The action preview shows the current position's cost against the effective movement allowance. The reported Goblin Warcamp screenshot has an empty adjacent destination outside a three-movement Fighter's origin range; direct routing does not expand that range. No unseen occupant was established by the screenshot.

Validation: 84 movement/approach, ground-zone, concealment, wall and Fighter presentation backend tests; 239 frontend tests; production frontend build. Regression checks cover adjacent movement between different origin-tree branches, wall-blocked direct steps and retained original budget. No production deployment or save changes.

## October 5: actions pressed during pending movement (implemented in dev)

Battle commands, including provisional moves, are server validated. The browser
immediately previews legal movement using the server's movement graph, coalesces
rapid clicks to the latest destination and ignores obsolete movement acknowledgements.
Modes and targeting selections are local. Movement remains server checked because
scouting can reveal concealed enemies and interrupt a route; committed paths also
feed ground hazards, carrying and exit rules.

Previously Guard or another action pressed while a move POST was pending was
silently discarded. The input handler now buffers one action, finishes the latest
chosen movement and then submits that action once. Further movement/action presses
cannot alter that buffered commitment. It is discarded on request failure, battle
closure, actor/round change or an interrupting playback lock. Enemy/action playback
still blocks inputs. Server acknowledgements are still required; this does not
remove network latency or let the client resolve combat outcomes.

The pool/private/active/state GET requests remain general five-second refreshes.
Visible-panel rendering already skips roster/base/board replacement during combat;
these requests do not submit combat actions. No polling change or measured claim
about Cloudflare latency is part of this fix.

Validation: 252 frontend tests and Vite build pass, including delayed-request tests
of the real command handler for rapid movement plus one Guard press, repeated
Guard presses, changed actor and failed movement recovery. No live-server network
latency benchmark was performed. Existing bundle-size warning remains.

## October 5: combined movement/action submission (implemented in dev)

Local reposition previews remain immediate. Movement-only requests now coalesce
behind a 100ms quiet interval. An action during that interval cancels the movement
POST and submits the final position with the action in one command. If a movement
request is already running, one action waits for it; its final position is included
without another movement POST. Earlier replies cannot rewind the local preview.
A reply whose actual position differs from the requested destination is treated as
a scouting interruption: discard queued inputs and show the revealed map.

The backend shares the existing movement validation/scouting implementation for
standalone and combined commands. Final positions retain START movement budgets,
carried-body updates and per-tile committed ground damage. A discovery that stops
the route does not execute the following action. This is request coalescing plus
combined submission, not completely offline movement; isolated movement pauses
still check scouting with the server.

Committed requests immediately disable combat inputs and show the existing
resolving indicator. The enemy/attack/forced movement playback lock remains in
place after the response; subsequent turns cannot bypass knockback/collision
playback. No server latency benchmark or new live browser measurement is claimed.
Validation: 256 frontend tests, 83 related backend tests and Vite build.

## October 5: persistent movement intent and doorway navigation (dev)

The latest chosen destination now survives consuming the request queue. Guard
and other committing commands attach that position even when the debounce already
sent it. Server acknowledgements update confirmed movement without overwriting a
newer chosen destination; a genuine scouting interruption still cancels intent.
A confirmed destination is not resent merely because it was queued again. Errors,
battle closure and forced/enemy playback clear pending intent as before.

Rapid reversal near a destination can round the visible position to that same
cell. Such previews now contain a real fractional-position-to-destination segment,
instead of one keyframe that holds until a jump. Walking hop/tilt and forced-motion
playback retain their existing tuning.

Clicking floor beyond current reach now plans a route toward it, including closed
doors. The server compares walking cost first and number of closed doors second,
so equal-distance open entrances win. Closed-door shortcuts are also marked in
the view when a longer open detour happens to fit the movement budget. This uses
existing walls, terrain costs, elevation and occupancy. The route stops at the
last legal reachable tile or beside its first closed door. It never opens doors
automatically or grants extra movement. Door operation remains a main action.
A painted-hand Open Door button appears by a closed door when it can be operated.
Opening it removes the prompt. Multi-turn navigation is not an automatic order;
the player chooses again on the next activation.

Route data uses one bounded graph search per player view only when a closed door
exists; routes are not recomputed separately for every possible destination.
Enemy door AI retains its existing opening-action policy.

Validation: 260 frontend tests, 94 related backend tests and Vite build. Regression
cases include 200 alternating inputs plus Guard, a destination already consumed
by the debounce, and a fractional mid-step reversal. In an isolated real browser,
60 alternating inputs with 180ms artificial responses followed by Guard finish
at the chosen cell, with under .02px portrait-centre error and no stuck walking
animation. The real prompt renders and sends the explicit interact command.
Backend cases cover open entrance ties, a closed shortcut versus an in-range open
detour, insufficient movement, sealed walls and edge-mounted doors. Existing
bundle warning remains. No live Cloudflare latency benchmark; production/saves
unchanged.

## October 5: occupied doorways and real API validation (dev)

Corrected both normal combat and Battle Lab request models: they now retain the
combined `position` field instead of silently discarding it during Pydantic input
validation. Earlier engine-only/delayed-fetch tests did not cover this request
model boundary; new tests exercise the actual Lab handler and both models.

Entrance intent planning looks past unit occupancy so a standing NPC inside a
closed door does not hide the entrance. Actual movement still uses the unchanged
occupied movement tree, stopping before the NPC and never overlapping it. Door
operation remains explicit and requires a legal adjacent/inside approach.

The browser suppresses repeated unchanged entrance requests. Changes in the
activation, units, door/structure state or props permit a new request; temporary
network/server errors permit retry. Unchanged invalid destination requests are
also suppressed after their 400 response. Battle Lab reuses an unchanged validated
navigation response only while the same battle object and activation remain.
Its command handler now uses the view already produced by the engine, avoiding
a second expensive battle-view construction. GET views share that bounded
per-session cache; other commands replace the battle and invalidate it.

An isolated 14x10 Command Post reproduction took 4.541s for 20 uncached engine
navigation commands. After duplicate handling, 100 repeated actual Lab-handler
commands took .227s total on this PC, with one engine computation. These measure
local CPU/request work, not Cloudflare latency, and do not prove the cause of an
unrecorded server process exit. Regression tests cover an NPC in the doorway,
25 repeated engine clicks, 100 repeated actual handler calls and cache invalidation.
See [Development runner](DEVELOPMENT_RUNNER.md) for persistent failure logs.

Validation for this pass: 263 frontend tests, 99 backend tests (including all Battle Lab catalogue starts, API/persistence and runner isolation tests), and Vite build pass. Existing bundle-size warning remains. No new browser animation benchmark in this pass.
