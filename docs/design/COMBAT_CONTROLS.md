# Combat controls and targeting

## October 8: extend direct targeting to skills and Subdue

The shared unit handler now executes the selected skill or Subdue with its
validated approach, matching explicit basic Attack. No generic Move & Attack
menu appears just because the preview includes movement. Invalid explicit
targets cannot fall back to other skills/basic attacks, and occupied-floor
clicks filter actions to the selected mode. Move mode still offers contextual
choices. Dedicated AoE/self, placement, element, ally-command and Abduct flows
keep their relevant selection/confirmation steps. This branch is shared by
desktop and touch; mobile gesture code was not the cause.

See [skill targeting audit](SKILL_TARGETING_AUDIT.md) for all base-Job catalogue
entries, routing families, regression coverage and remaining manual checks.

## October 8: single-click Attack and door intent

Explicit Attack mode (A) now executes a valid enemy/obstacle click directly,
including the previewed approach if needed. It no longer opens a second Move &
Attack menu. Normal Move mode still exposes contextual choices; skills and Subdue
retain their existing targeting flow. Weapon range, walls and movement allowance
remain authoritative. This removes the extra click reported against Tarin Fen;
it does not expand weapon reach.

Clicking a distant door icon now means approach and perform the displayed Open or
Close action on arrival in the same request. Nearby approaches retain immediate
movement preview. Insufficient movement or discovery/hazard interruption stops
without operating; reaching the door consumes the normal main action. Stale Open
intent cannot accidentally close an already-open door. Both public request models
now retain gate ID and operation intent (previously unrecognized fields were
discarded). Plain floor navigation remains movement-only.

Validation: Chrome A/adjacent/distant attack and immediate door approach checks,
395 frontend tests, 26 focused backend tests including the real Battle Lab handler,
and build pass. Existing playback/input locking remains in place.

## October 8: target cursors and single doorway control

Valid/invalid target cursors now inherit through portraits, HP labels and other token children. Pressing A shows the weapon's attack cursor across the complete enemy token. Browser QA verifies that an adjacent legal enemy click sends Attack directly, while an out-of-range target still requires approach confirmation. The reported intermittent unnecessary approach while stationary has not been reproduced; no range or wall rules were weakened.

Each doorway has one permanent control centered on its physical boundary (or legacy gate footprint). Both inside and outside operating positions remain valid. A nearby approach uses the supplied legal movement graph and starts its normal optimistic walking preview before the server responds. If neither side is within the current movement allowance, the server chooses the nearest reachable operating side, with its existing shortest-route/open-entrance tie rules. Approaching does not automatically open/close or spend the main action. Opening/closing still requires server validation and normal action/animation sequencing.

Validation: isolated Chrome A/cursor/direct-attack/approach/door checks, 394 frontend tests, 19 focused backend tests and frontend build pass. The broader approach suite also exposes an existing obsolete Mage-zone fixture (`test_ground_spell_preview_and_move_cast_use_same_cells`), which fails to find a retired skill before exercising combat; it remains outside this UI fix.

## October 8: player layout adopted as default

New/reset layouts use the exported approximately 1216px centered, bottom-aligned Command/Skills/Effects bar, centered top turn order and Battle Lab at 21.9% vertical travel. The old standalone preview, commands and tools coordinates are obsolete because those controls are now grouped. Existing saved positions remain respected. Title, Objectives and map/battle tools now share one draggable card, with the icon row directly below Objectives. On smaller windows the bar clamps to fit, the unsaved character card moves above it if necessary, and long turn orders move below the title card. Map zoom and camera behavior are unchanged.

## October 8: close controls and drag interaction

Command and Skills now each reserve 12px before the next divider, in addition to the 12px inset after it; icon tracks and resize calculations include this spacing.

The shared placement-window drag handler now ignores interactive controls in its header, so clicking Close does not become a drag or lose its click through pointer capture. Turn Order and All Effects close reliably after dragging. Battle utilities, unit/effect inspectors, both HUD detail windows and the main battle-view Close button share 38px bordered square controls, hover/focus treatment and accessible labels. Closing the battle view does not order extraction; placement actions continue to use Cancel.

## October 8: compact combined action bar and fixed character card

The latest floating HUD replaces separate Commands and Skills with one draggable Command | Skills | Effects panel. Fixed column tracks give command and skill buttons identical spacing and sizes; the effects section wraps across then down. The panel retains horizontal resizing in Edit layout. Old separate-command and preview positions are unused; Reset restores current defaults.

The acting character, Traits and action description share a fixed 400 by 260 pixel card (30 extra pixels while editing), with a divider above the description. Text stays at 16px with no scrollbar or automatic font/card resizing. Commands and all base-Job active skill summaries use one concise sentence; full mechanics remain in skill tooltips. Dynamic Battle Priest healing, humanoid return, Reclaim and machine exit/cancel summaries follow their current state.

Map tools are a single icon row with accessible labels and hover titles: Center map, Supplies, History, Battle options and Edit layout (plus Reset while editing). Zoomed maps now reserve at least 360px extra camera travel on either side, scaling with viewport height, so right-drag can pull edge cells clear of overlays. Fitted panning remains bounded to 120px each way. No combat rules or production data changed.

## October 8: unified skills, effects and command styling

The rightmost quarter of the skills container now holds Effects, separated by a vertical divider. Badges fill from left to right and wrap into rows; overflow opens the existing full-effects popup. Empty effects remain visible. Effects move with Skills rather than as a separate HUD group. The skills grid is five columns by two rows with no scrollbar; the existing skill-page controls handle more than ten abilities. Resizing the container scales skill and command tiles together (up to 88px) so ten skills remain reachable instead of forcing a third row. Commands now use the same filled square artwork, borders, top-left key badge and name underneath, with a matching header and panel height.

Objectives are directly beneath the round/title in the same draggable group. The centered map margin is now 96px; the battlefield allows overflow so bottom-edge HP/Resolve labels are not clipped at the map boundary. Fitted-map panning is now limited to 120px each way (three times the original adjustment); a deliberate pan can bring an edge closer to the viewport, and Center map restores full centered breathing room. Other saved group positions remain local and preserved.

## October 8: HUD sizing and bounded map adjustment

Skills now use 88px square buttons with 72px artwork, matching commands, with two rows in a panel the same height as Commands. Resizing skills changes the available columns; overflow remains reachable. Buffs/debuffs are a separate draggable group beneath skills, including an empty state so the group can always be positioned. Existing browser-local positions are retained; Reset applies the updated defaults.

Turn-order cards and portrait art are 50% larger (102px cards, 54px portraits). The HUD shows up to ten upcoming conscious, living, present units, fewer on narrow windows. Its scrollbar is removed; a non-interactive **+N more** label indicates overflow. Click the turn-order group (or Enter/Space while focused) to open one draggable full-order window. The full order refreshes as units die, become unconscious or leave. Effects and turn-order windows have dedicated styling so summon-placement cleanup cannot remove them.

Fit now reserves 80px around the map for edge names/markers. The aspect ratio remains unchanged. Right-drag can adjust a fitted/zoomed-out map by at most 40px each way; zoomed-in maps retain ordinary panning with edge margins. Camera adjustment survives action-selection redraws. **Center map**, immediately beside Supplies, explicitly restores the centered fitted view. The same padded camera works across square, wide and tall maps; no gameplay coordinates/pathfinding are changed.

## October 8: floating battle HUD (implemented in dev, experimental)

The active battle viewport fills the battle window; map fitting still preserves its aspect ratio. The previous full-width header and command dock are replaced by translucent independent groups: battle title, turn order, objectives, acting character with Traits, skills/Arrange with a smaller effects row, commands, action description, and map/Supplies/History/Battle options. Preparation UI is unchanged. Existing skill and command artwork/sizes and combat rules remain unchanged. Auto One Turn and Auto Resolve remain in Battle options.

Select **Edit layout**, then drag a group's labeled grip. Gold guides snap its edges/center to the window or another group's edges/center (8-pixel tolerance); hold Shift for free placement. Focused grips also support arrow keys (8 pixels, or 1 with Shift). Combat keyboard shortcuts pause while editing. Select **Done editing** to hide grips. Layout is saved automatically in this browser, shared across battles, using normalized positions and clamped after window resizing. **Reset** restores the starting edge layout. The skills group can be resized horizontally using its lower-right corner while editing; icons retain their size and the skill bar scrolls when necessary. Deliberate custom overlaps are allowed. Narrow windows stack central groups above commands by default.

Buffs, debuffs and other visible effects share the row beneath skills: up to six 30-pixel badges, fewer when the container is narrow. **+N more** (or **All effects**) opens one draggable, scrollable effects window with full descriptions. Its position is remembered, it closes on actor changes/battle close, and Escape closes it. The open window refreshes on battle redraw. Map badges and the existing right-click unit inspector are unchanged.

The BG3 reference informs edge placement and map space, while Fortcamp retains its own painted controls. No art generation or new assets are needed. Layout settings stay local to this browser; cross-device presets, per-resolution profiles and touch/mobile-specific HUD design are deferred.

Engineer uses centered Confirm/Cancel for machinery/hazard placement and mounting/
exit, with legal highlights and prop previews. C/Escape/right-click cancel. Attack
fires an occupied machine; Overclock leaves the first of two shots in the same
activation. Mine interruptions truncate committed routes and suppress the pending
offensive cast. [Full rules](ENGINEER_REWORK_REVIEW.md).

## October 5: Monk buffs and resistance inspection

See MONK_REWORK_REVIEW.md for the updated kit: capped per-punch exposure, advancement-gated stun, enemy-specific reversal evasion, three-turn hit healing and brief physical parry. Effects reuse existing clocks, feedback and packed icons. Direct damage amplifiers add together; damage-over-time/collision/environmental sources are excluded. Unit inspection groups individual status resistance, boss control-duration limits and push/pull resistance into one Innate resistances buff. Status chance for weapons, abilities, zones and collision stuns shares `combat_conditions.status_chance`; missing percentages do not imply universal boss resistance. Authored per-boss profiles override thematic defaults. Parry excludes magic and area attacks, with a distinct contact label. Fresh battle snapshots use the updated skills.

## October 5: Monk sequence presentation

The acting card shows Neutral, Follow-up Ready or Finisher Ready, with a three-stage meter and remaining personal turns. Setup becomes usable on the next activation. Locked skill tooltips explain the required stage. Eight square icons share one packed art set; existing saved drag ordering and five-slot loadouts remain unchanged. Slotted Perfect Rhythm/Flowing Footwork remain in the skill bar. Temporary Iron Reversal, Open Guard and Footwork have explicit status tooltips. Punch damage, sound and defeat use authored contact offsets; enemy actions wait for packet playback. Dash previews the route, landing, visible crossed enemies and committed ground damage. No extra click or separate resource meter is introduced.

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

## October 5: initial house-navigation latency (dev)

The Command Post reproduction already uses current edge-wall geometry (14x10,
30 terrain structures, 28 edge walls, `small_command_4`, seed `layout-0`). Its
initial navigation delay came mainly from repeated terrain footprint scans, not
outdated construction assets. Movement, repositioning and entrance searches now
build temporary terrain/ground lookups once per search. Movement-cost evaluation
also reuses its terrain lookup. Overlapping and rotated footprints preserve their
original rules and order. These indexes never enter saved battles or API views;
every search rebuilds from current door/structure state, avoiding stale blockers.

Eight isolated uncached navigation commands averaged 238ms before and 32ms after
on this PC (about 7.4x faster). This includes battle-view construction, excludes
network latency, and does not establish the cause of the earlier unrecorded server
exit. Existing server authority, explicit door opening, START movement budgets,
hazard handling and animation locks remain unchanged. No frontend changes.

Validation: 77 backend tests pass, including all Battle Lab catalogue starts and
persistence checks, covering indexed/unindexed route equivalence,
rotated/overlapping footprints, fresh searches after door/footprint mutations,
absence of indexes from saved/public state, navigation API, approach movement,
wall boundaries, committed ground hazards and combat tactics.

## October 5: persistent doorway controls (dev)

Every intact door now has a small painted-hand control on each approach side,
always visible instead of requiring a hover or a navigation attempt. The label
and plus/minus badge switch between Open and Close with the actual gate state.
Controls are anchored to the doorway boundary (all four edge orientations) or
the footprint of older centered gates. Off-map approach sides are omitted.
Clicking while directly inside/outside operates the same door without stepping
through it. From farther away the button approaches its selected side using
existing navigation, leaving opening/closing as an explicit action. Closed-door
routing can stop at the near side rather than pass through a closed door.

Door operation still costs the character?s action. During an enemy activation,
a spent action or animation playback the controls remain visible but unavailable.
Occupied older centered gates explain why closure is blocked. Broken doors have
no button. Each control has its own click handler, accessible action label and
hover explanation; clicks do not bubble into movement/attack targeting. Existing
context actions and navigation prompts in the API remain compatible.

Validation: 25 backend tests (door geometry/operation, all edge directions,
rotated legacy footprints, occupied gates, bounds, navigation API and routing),
266 frontend tests, and Vite build pass. An isolated Chrome fixture using the
actual Command Post battle UI rendered all six controls and confirmed a side
button sends its corresponding approach command. Production and saves unchanged.
Existing bundle-size warning remains. Network multiplayer latency was not tested.

Doorway-size follow-up: doubled the painted-hand buttons from 22px to 44px.
Each side shifts outward by 12px so the enlarged pair remains separate at the
normal battle view. Door anchoring, commands and action costs are unchanged.
Verified targeted frontend tests and Vite build; production unchanged.


## October 5: Fury and self-targeted martial skills

Barbarian has five Fury segments below its map token and a numbered meter below
HP in the acting card and cursor inspection. Hovering includes its innate Job
rule; attack inspection uses Bloodied Strength's effective attack. Skills report
Fury costs/unavailability, existing cooldown numbers and remaining charges.
Brace, Second Wind and Groundbreaker target the caster, not another ally.
Groundbreaker previews all eight neighboring cells and individual enemy damage.
New physical effects finish before the next actor moves; damage text remains
above the effect layer. Reduced motion disables aura breathing and sprite growth.


## October 5: equipped passives and saved skill order

Equipped Job passives occupy visible slots beside actives in the bottom bar.
Their P label and tooltip identify automatic behavior; clicking or pressing a
number never casts a passive. Slotted passives are excluded from the Traits
panel. Traits sits beside the horizontal acting card, before the skills, and
lists racial/innate and equipment effects with readable full descriptions.

Drag one skill onto another to exchange their positions. Order saves immediately
on the device and, for roster characters, through the authenticated skill-order
endpoint in their existing player save. No turn/action, Fury, cooldown or equipped
skill changes. Saves serialize so rapid swaps cannot arrive out of order. Storage
keys include environment, player, server and save creation. Battle Lab orders are
separate local preferences; testers never write to the real roster. Arrange opens
all skills together so swaps can cross hotbar pages. Dropping elsewhere cancels.
Actives on cooldown remain draggable, while their cast is unavailable.

Passive cooldown/once-use/reaction state appears with the actual skill icon in
map buffs and the acting effects tray. A number counts owner turns until ready;
used once-per-battle passives show ?. Hover explains Ready, Active now or Used.
Bloodthirst's same-turn multi-kill window remains active before its cooldown.
These are derived view indicators, not extra statuses influencing combat. Map
polls therefore do not advance or alter their state. Equipped-passive tooltips
also show their readiness. Bloodthirst now heals 20% maximum HP per lethal kill.

Open battle dialogs survive live rendering, including a swap in Arrange. Hotbar
DOM nodes are keyed by skill ID so a swap moves the correct button/tooltip.


Layout follow-up: desktop places the horizontal character card, Traits, skill bar
and commands in one row, followed by a full-width buffs/effects row and action
help. This recovers vertical room for the map. At narrower widths commands wrap
below, and phone-sized views wrap skills as well. Only passive readiness badges
on map tokens shrink from 36px to 27px (75%); tray/tooltip icons and ordinary
buff/debuff sizes are unchanged. Unit hover/active scaling still applies normally.

## Rogue targeting (October 5, implemented in dev)

Quick Actions are labelled in the hotbar/tooltips. Shadowstep: choose enemy, choose highlighted adjacent landing, Confirm. Backflip: choose legal cardinal landing, Confirm. Caltrops: preview a 1x3 strip, R rotates, Confirm places; release an outside-map drag to clear placement. C cancels without cost. Invalid cells are red. Knife: choose Basic Attack/Cheap Shot/Exploit (only equipped compatible skills), choose enemy beyond melee range, Confirm. Attack selection and Confirm/Cancel appear centred on the visible map. Rotation and targeting instructions remain in the action-preview area. Forecasts explain positional power and negative-stack totals; map Bleed/Hobble badges show stack count and hover text explains independent expiry. Main attacks end the activation; chain Quick Actions first. Animation playback still blocks all confirmed combat inputs until contact/movement/collapse resolves.


## October 6: Rogue confirmation and trap visibility fixes (implemented in dev)

Rogue attack selection and Confirm/Cancel now appear in the centre of the visible map viewport. R rotation stays in the bottom action-preview area. A selected Caltrops strip stays fixed while confirming; pointer motion only moves the unconfirmed hover preview. Invalid placement cannot commit; cancelling is free. Knife attack selection refreshes the selected attack forecast.

Fixed Throwing Knife + Exploit Weakness: the command sender now preserves an explicit skill ID instead of replacing it with the selected Knife utility. The underlying selected main attack and Knife cooldown resolve together; the main attack still ends activation. Multiple Quick Actions remain allowed before it.

Caltrops now use three small opaque steel spike silhouettes per tile, with a subtle glow and scale pulse, above terrain and props. Combat feedback and interaction controls keep their own foreground layers. Reduced motion disables the pulse. Prior atlas imagery is retained; it is no longer the persistent trap visual.

Validation: 24 Rogue backend tests, all 291 frontend tests and frontend build pass (existing bundle-size warning). Actual Chrome UI fixture checks centred prompts, rotation/cancellation, and the confirmed Exploit/Knife command IDs. Screenshot review covers the confirmation panel and trap layer. No production deployment or player-save changes.

## October 6: Painted tactical props and Rogue API fixes (implemented in dev)

Replaced the temporary steel-vector Caltrops with three seeded, pure top-down painted scatter props. They keep transparent gutters, contact shading, a small footprint, and the established subtle pulse/glow above terrain/props. New equal 4x4 atlas also supplies anchored Scrap Turret ready/fire/recoil/destroyed frames and its north-oriented bolt. The existing stationary Engineer turret now renders as a prop, aims toward its target, animates firing/recoil, launches a bolt to the shared 220 ms contact, and uses wreckage when destroyed. HP/hover controls and automatic targeting remain. Heavy turret variants, tools, spare bolts and bear traps are imported for later use; no new equipment or deployment rules are implied.

Fixed both Battle Lab and normal combat API schemas dropping `knife_skill_id` and Caltrops `rotation`. Knife delivery now reaches the engine for Basic Attack, Cheap Shot and Exploit Weakness. Vertical strips remain vertical after confirmation. Caltrops immediately attempt one Bleed/Hobble stack on occupants of newly placed tiles (including allies); resistance and Trap Expert apply. This triggers only the new strip, marks the current tile, and does not charge an extra entry for standing still. Later committed movement and push/pull continue adding stacks per entered tile.

Validation: 70 focused backend/Battle Lab tests and all 293 frontend tests, frontend build, real Chrome UI checks for Knife confirmation/strip rotation, painted prop display, turret fire/recoil/bolt cleanup and destroyed art. Existing bundle-size warning remains. No production rollout or save reset. Restart the dev server and refresh the browser for the changed request schemas. Art source/import details: docs/art/TACTICAL_PROPS_V1.md via docs/INDEX.md.


### October 6: targeting cancellation and occupied AoE cells

Implemented: a stationary right-click in the map cancels targeting/placement and returns to Move without issuing a command. Right-drag still pans (five-pixel gesture threshold); interrupted gestures do not cancel. Rogue confirmation and Mage enchantment prompts also accept right-click cancellation. Playback remains protected against player commands.

Ground-targeted spells use their legal ground-cell preview for occupied targets, rather than the unit-only attack check. A valid occupied cell shows the acting unit's weapon attack cursor. Friendly-fire forecasts use warm red text and explicit You/Ally labels; enemy forecasts retain the ordinary palette.


### October 6: movement hazard warnings and painted navigation

Implemented: hovering a reachable destination in Move shows the consequences of its final path from START. Hazardous path cells gain an orange outline; the map overlay separates immediate HP damage from Burn/Bleed/Poison stacks and delayed turn-end damage. The chosen path warning remains when the pointer leaves the map. Discarded positioning previews remain free. Resistant status applications are labelled as attempts/up to a stack count; fatal routes say lethal risk. Forecasts reuse zone eligibility and damage/barrier calculations on an isolated character copy, account for overlapping patches and Trap Expert, and require no hover API calls. This is an entry-hazard estimate, not a prediction of later enemy attacks, reactive survival passives or delayed Meteor/Freeze impacts.

Open/close doorway buttons use distinct painted doors; extraction cells retain a boots-and-threshold EXIT/HOLD marker even when movement path numbers are present. Panning uses a painted four-way compass cursor. Map surfaces, props, blocked ground and interactions use Fortcamp cursors instead of browser arrows/hands. Generated art and exact prompt: [Navigation atlas](../art/COMBAT_NAVIGATION_V1.md).


## October 7: inspect units and allow chained control

Right-click a visible ally or enemy to open a persistent, draggable Unit details window. Drag its header; close with its X or Escape while focused. Right-drag still pans, including when begun over a unit. Right-click empty map space still cancels targeting and selects Move. Inspection sends no combat command. The window refreshes from current presentation snapshots, closes if its unit disappears, and is removed when the battle closes. Hidden enemies remain unavailable.

Hover or keyboard-focus HP, ATK, ARM, MOV, RNG, ACC, EVA, INIT and LVL for calculations/explanations. New player battle snapshots retain their actual initial stat ingredients; old battles and authored enemies use their existing battle/profile values without invented origin data. ATK includes Pestilence/Bloodied Strength; skill multipliers and target-dependent mitigation belong to attack forecasts. Evasion is weighted by attack type (ballistic 100%, melee 60%, magic 30%), not an independent dodge roll. Rat overrides ordinary aimed contact chance to 10%.

Armor is flat subtraction: max(1, attack power + bonuses - effective armor after piercing), before outgoing/incoming multipliers and Barrier. Armor Fracture subtracts ceil(30% of armor), without stacking. Armor 10 becomes 7; incoming power 20 becomes 13 before other modifiers. Current magic hits also use armor before magic mitigation. Percentage Burn/Poison/Bleed bypass armor. Do not advertise a fixed armor damage-reduction percentage: it varies with incoming power.

Innate resistance appears under Buffs, combining status application resistance, Burn damage resistance, knockback resistance and boss control-duration limits. Unlisted statuses have no innate resistance. The former blanket active-control exclusion and post-control recovery immunity are removed, including legacy saved immunity flags. Controls can overlap, refresh and be reapplied. Selective authored/racial resistance and boss/chieftain one-target-turn hard-control limits remain. Repeated Frost enchant hits may break and reapply Freeze; Lightning enchant still retains its deliberate once-per-target/application restriction.

October 7 hover refinement: unit summaries stay horizontal and bounded as effects accumulate; effects scroll independently. Hover advertises right-click inspection. A 120ms pointer crossing allowance permits scrolling the temporary card; leaving the card/unit closes it. Full calculations and effect details remain in the draggable inspector.


### October 7: independent effect inspection

Right-click an individual status badge on a unit or in the acting-character dock to pin that effect's explanation. Right-clicking its temporary hover or an effect card in Unit details does the same. There is one Effect details window: inspecting another effect updates it, and Unit details stays open. Drag the header to move; close with X or Escape while focused. Right-drag on a map badge continues to pan without opening a window. Inspection sends no command.

Unit details now places stats above a full-width, bounded effect grid. Effect overflow scrolls, with precise duration/stack labels and compact rules; traits/passives can expand below. Hovering individual map badges retains full rules. Existing stat calculation help remains available. No action, damage or resistance rules changed in this refinement.


### October 7: command tile consistency

The six primary commands use 88px square tiles, matching the desktop skill tile size, with 72px painted glyphs, consistent four-pixel corners, dark backgrounds, gold frames and selected/focus outlines. Hotkey/name labels sit below each tile. Desktop keeps three columns and two rows at the right of skills with a wider 324px allocation; existing responsive row layouts remain. Disabled commands desaturate. Controls and hotkeys are unchanged. Unit-switch intent and its targeting/right-click bypasses are documented in COMBAT_STATUS_PRESENTATION.md.


October 7 current hover behavior: no added unit-switch delay. The cursor-following summary has plain stats and at most three effect rows with an overflow count; its effect column does not scroll. Right-click Unit details retains stat calculation help, all effects and scrolling. Right-click map badges still opens the independent effect inspector.


October 7 rendering follow-up: transient unit/status hover is display-only and pointer-transparent, follows the cursor with transform positioning, and closes immediately on leaving its unit/badge. Use right-click on the actual unit or map/dock status badge for persistent details. The old hover-card pointer-crossing allowance is removed. Pinned windows remain draggable and interactive.

### Summoner placement and orders

Summoner skills open a centered map confirmation panel. Bound Companion first asks
for Fire, Earth or Grass, then an empty tile within two cells. Wisp Swarm selects
three distinct tiles before one confirmation. C, Escape or right-click cancels
without spending an action. The corresponding active skill becomes Quick Reclaim.

The numbered Summon Orders skill-bar tile opens a popup for Hold Position, Focus
Target, Follow Summoner, Stand Down or Clear Order, for one creature or all. Bound
Companions also offer Protect Ally: select a living ally on the map or from the popup target list, including the
Summoner, and confirm. Grass heals/supports them; Earth/Fire prioritize their
threats. No interception is granted. In All summons mode, Protect Ally changes
only the Companion's order, leaving Wisps unchanged. The skill tile can be
reordered and does not use an equipped skill slot. Orders persist and cost no
action. Creatures move and attack autonomously after their owner's activation,
beginning on the following owner activation after conjuring. They do not receive
manual turns. Transposition selects two owned bodies (the caster may be one),
then confirms a swap; it ends normal walking but leaves the main action available.
See SUMMONER_REWORK_REVIEW.md for lifecycle, creature profiles and AI limitations.

### Engineer/Summoner placement refinement — October 7

Placement windows drag by their header and remember separate positions. E confirms a valid selection; C/Escape/right-click cancels. Turret construction alone uses the Engineer window. Dynamite and mines use ground AoE targeting; mounting and Scuttle highlight owned legal machines; Rapid Assembly targets self. Invalid placement uses the X cursor. Engineer/Summoner battle descriptions are concise single sentences; extended reference text is retained for a later menu. Mines/wrecks now retain their presentation until resolved explosion/defeat events play.


### Mobile Safari battle controls ? October 8 (first dev pass)

Touch screens up to 1100 CSS pixels use a separate battle layout; desktop mouse controls and saved desktop HUD positions are preserved. Portrait and landscape respect screen safe areas. Commands, Skills and Effects share a bottom panel with 44px action targets. Tap a tab to switch panels; Hide expands the map and Show restores controls. Goals expands objectives; Order opens the closeable turn-order window. The existing map-center icon recenters the view.

Tap a command/skill, then its target. Cancel abandons targeting and returns to Move. Drag the map with one finger; pinch to zoom around the gesture midpoint. Hold a unit for 450ms to open persistent Unit Details, or hold its status badge for Effect Details. Dragging, pinching and holding suppress the gesture's action click without delaying the next deliberate tap. Touch does not use the cursor-following hover card. Browser page zoom remains enabled. Mobile details/placement windows are constrained to the screen; long lists remain scrollable inside persistent windows.

Validation: 16 gesture/camera/HUD unit tests, isolated Chrome portrait/landscape touch-input checks (including no commands after pan/pinch/hold), persistent-details open/close, desktop-layout restoration, desktop HUD regression and frontend build. This is browser emulation, not actual iOS Safari validation. Real-device safe areas, browser chrome, performance, and the full collection of skill-specific multi-step placement flows still need playtesting. Non-battle screens, touch skill reordering and a complete mobile onboarding flow are outside this first pass. No deployment or combat-rule changes.


October 8 mobile space/setup follow-up: reduced the bottom controls from 206px to 138px and actor/description card from 120px to 82px. Commands and skills use one horizontally swipeable row, with labels retained and no visible scrollbar; Effects uses a compact row and the existing detail popup. Portrait map clearance increases by 110px at the same screen size. The Lab button exposes restart/map selection during a test. Battle Lab setup uses a full-height touch dialog, a single scrollable workspace, width-constrained fieldsets and 16px native select/input text. Job selection is tested reachable, uncovered and changeable in portrait/landscape. Desktop HUD regression and frontend build pass. Actual iPhone Safari feedback remains required.


## Withdrawal controls - October 8

Leave Map belongs to the Actions menu (I), not Battle Options. It appears only
when the acting character occupies an EXIT tile. During the initial HOLD it is
visible but disabled, with a short instruction to hold until the next turn.
When ready, Leave Map extracts that character using the existing rules. L selects
it while Actions is open; a disabled entry cannot be activated by click or key.

Retreat All belongs to the Commands group, with matching icon tile and R key
badge. It retains the existing second-click/second-R confirmation and is disabled
once withdrawal has begun. Order: Move, Attack, optional Subdue, Throw, Actions,
Guard, End Turn, Retreat All. Desktop commands use four columns/two rows; mobile
keeps its swipeable command row. Battle Options retains map help and auto-play,
without either withdrawal button. No retreat/extraction timing rules changed.

Validation: 15 backend tactical tests (including hidden/holding/ready/extract
behavior), 411 frontend tests and build pass. No manual browser acceptance claimed.


### Withdrawal layout correction

Guard's dedicated button is removed. The six standard commands are Move, Attack,
Throw, Actions, End Turn, Retreat All, in two rows of three. Subdue remains a
seventh command when capture equipment is available; that panel uses four
columns and still two rows. CSS now reads the same column count used for panel
width. Retreat All's legacy full-row span is overridden inside Commands; it was
causing the clipped third row reported by the player.

End Turn help explicitly states that an unused main action grants Guard, reducing
the next direct hit by 25%. Space ends the turn; G remains an alias for End Turn.
Retreat confirmation and the mobile swipe row remain. Isolated actual-browser
checks at 1440px/1000px confirm two rows, visible labels, optional Subdue, no Guard
button, the 25% description and held/ready Leave Map states. QA tool:
`tools/command_layout_browser_qa.mjs`; no game saves or live endpoints used.
