# Combat status presentation

## October 9: readable Unit Details stat help

Pinned stat tooltips now use one or two plain-English sentences, followed by a
visually separated numeric formula. Attack/Armor use “÷ 2/3, rounded down” rather
than programming operators. Shared source formatting covers both players and
ordinary NPCs, rank and equipment, while saved formulas get a read-only notation
cleanup. No stats or save values are recalculated by this presentation pass.

Armor explains flat subtraction and percentage-DoT bypass; accuracy explains
target-specific chance and Parry, Evasion explains the attack-type factors, and
Rat/form/capture equipment exceptions use their real rules. Hover-following cards
still have no stat help. Pinned tooltips escape text and avoid rebuilding identical
content on every mouse movement. Backend/renderer checks and browser build recorded
in WORK_STATE; exact live crash cause remains a separate diagnostic issue.

October 6 Mage surface update: elemental Frozen covers the actual portrait with translucent painted ice, four stable patterns and contact-timed spreading/shattering or thawing. The old Freeze binding-tether flash is removed. Status badge placement and gameplay remain unchanged. Dedicated sheet, import and limitations: [Mage surfaces V2](../art/MAGE_SURFACES_V2.md).

October 6 Ranger additions: owner-specific Quarry badges identify the owner and guaranteed accuracy; Poison shows stack counts and target-end percentage damage; see [Combat DoTs](COMBAT_DOTS.md). Pestilence, Poison Imbue and Sharpshooter have painted status art. Longshot critical feedback is labelled Critical; Rupture has its own damage label. See [Ranger rules](RANGER_REWORK_REVIEW.md) and [Ranger art](../art/RANGER_V1.md). Existing badge sizes/layout are unchanged.

October 5 spacing refinement: attached map badges use wrapping flex rows with a 3px column gap (previously 6px) and unchanged 6px row gap. Removing fixed 36px grid tracks also removes unused column space around 27px passive-readiness badges. Icon sizes, attached position and the dock/inspection displays are unchanged. Verified in the browser with two readiness badges; transformed visual gap is 3.45px at 115% token scale, corresponding to 3px CSS spacing. Twenty-one related UI tests and the frontend build pass; the existing large-bundle warning remains.

Implemented in dev, October 5, 2026. Reference: the player supplied
`question/dota 2 buff and debuff.png`. Its useful principle is readable square
art with distinct positive/negative framing, adapted for a turn-based map.

## Current display

- The acting character has a full-width status strip in the bottom command dock.
  Green-framed Buffs, red-framed Debuffs and blue-framed Other effects are
  separated and named. Icons are 48 px, with short names underneath.
- Map units show all compact effects as 36 px square art. The first row begins
  slightly inside the unit upper-left (8% from the top, 4% from the left), with
  further rows wrapping downward. The row is a child of the moving NPC token,
  never a separate cell overlay. It no longer stacks upward into the cell above.
  Control statuses take priority, then damage over time. Hover the unit to see
  every effect; hovering a specific icon gives that effect's description.
- Unit inspection lists every effect in its group with 36 px art, name,
  plain-English description, remaining activations/ticks and source when known.
  The dock icons support both mouse hover and keyboard focus.
- The badge number means remaining rounds/activations/ticks; the hover explains
  the clock. Barrier instead shows its remaining absorption amount. One-use
  bonuses show `1x` (rendered with the multiplication sign). Real-time countdown
  rings would misrepresent these turn-based rules, so they are not used.
- Ordinary Guard is included even though it is stored as a flag. Marks from
  different owners remain separate. Unknown effects remain visible with a
  neutral fallback. Defeated, extracted or carried units do not show active
  status badges. No hidden enemy data is exposed.

Artwork is reused from the existing painted ability atlas. Some conditions
share a relevant image; names, colored grouping and hover text identify their
actual rules. A dedicated status-icon pack can refine those distinctions later.
This status layout uses existing art; the accompanying command/cursor atlas
is documented in `docs/art/COMBAT_CONTROLS_V2_PROMPT.md`. Status mechanics are unchanged.

## Stun visual

Three lit gold stars orbit an elliptical ring above the unit's portrait. It is
built from lightweight SVG/CSS with depth implied by scale, height and opacity.
The effect follows the token while walking or being pushed and remains only
while a conscious, living unit has Stun. New Stun starts visually at its existing
status-contact time on the shared attack/collision timeline. Existing Stun shows
immediately. Recovery or defeat removes it. Reduced motion shows static stars.
Stun application no longer displays the unrelated binding-tether sprite.
Poison's current cloud and particles are unchanged.

## Earthbreaker landing audio

The dry 220 ms landing edit remains. The continuing shrill tail was actually
an extra `magic_cast` emitted by the generic non-attack fallback after the area
attack. Area attacks now use their own impact audio without that extra spell cue.
Landing gain is 0.65; a new low crater boom is layered at the same landing contact
at 0.38. The generated 573 ms mono 48 kHz boom has no clipped samples. Original
sources and generation receipt are retained. Final aesthetic listening review
remains with the player; automated metrics cannot judge the sound's character.

## Verification and remaining work

236 frontend tests, 112 relevant backend tests and frontend build passed.
Isolated browser checks verified 48 px dock / 36 px map icons, uncropped square
art, all effects instead of an overflow counter, grouped poison hover duration,
three animated stars, static reduced motion and removal after recovery.
Review capture: `staging-ui/combat-fighter-review/controls-status-review.png`.
Fixtures do not use live player saves. Production was not changed.

Dedicated distinct status artwork and richer Barrier/Burn/Freeze presentation
remain deferred. Large numbers of effects can occupy several map rows; the full
inspection and dock strip remain available. Unknown statuses use a neutral badge.

## Rogue stacks (October 5)

Bleed and Hobble show their layer count rather than a misleading single duration number. Bleed hover details explain percentage damage and one-stack target-end decay; Hobble retains independent expiry and halves normal movement only once. Rogue skill artwork supplies the badges. Each real Caltrop tile-entry application produces status feedback on the movement route; discarded path previews produce none. Main/Quick action labels and stack-powered damage forecasts live in the existing dock/inspection UI.


### October 6: status badges follow playback

Implemented: status-application feedback carries an independent snapshot of the affected unit's statuses at that event. The map starts with the prior snapshot and updates badges and status hover details at the shared contact markers, including Meteor impact and later Burn applications during movement. The final stack counts/removals reconcile when action playback ends. This changes presentation only, not damage, AI turns or status timing. Older recordings without snapshots retain prior badges until playback ends. HP bars and other non-status HUD fields still use the resolved battle snapshot; exact intermediate decay/removal timing is not emitted as a separate event.


October 6: Frozen portrait visuals now consume intermediate status snapshots, not only previous/final state differences. This preserves short boss Freeze effects even when the boss has already skipped its activation and thawed before the API returns. Natural transient ice gets a minimum readable 500 ms from application before thaw starts; direct damage still shatters at contact. Pending ice timers are scoped to the token playback generation and cannot restore an old shell over a newer animation.


## October 7 unit inspection

Innate resistances now share one Buff entry: selective status resistances, push/pull resistance and boss hard-control duration limit. No separate resistance/recovery panel or duplicate Footing entry is added to the hover card. Control recovery immunity is removed; controls may chain. Frozen tooltip describes Wet without obsolete recovery text. Right-click inspection pins a draggable details window with stat explanations; regular hover remains cursor-following and temporary. See COMBAT_CONTROLS.md for exact formulas and controls.


## October 7: bounded horizontal hover summary

Unit hover uses a 740px-wide, 350px-high card on desktop, bounded by the viewport on smaller screens. Identity/HP sit above two compact columns: stats/forecast and effects. Buff/debuff rows show the icon, count, name and one-line summary; the effects column scrolls independently, without growing the card. Nothing is dropped when effects overflow. Full Job/passive prose and full status details remain in the persistent right-click inspector. Hovering a specific attached effect still opens its full description. A footer says "Right-click to inspect stats and effects."

The pointer can move from a unit into its hover card to scroll; a short 120ms crossing allowance prevents the card closing across the gap. Leaving both closes it. Right-clicking the card also opens the associated unit inspector. Wheel gestures inside the card scroll its content instead of zooming the map. The tooltip remains a temporary summary, while the inspector is the place to read calculations and longer explanations.

Corrupted display separators/multipliers in Rogue forecasts, status explanations and action-cost text are replaced with plain punctuation and x multipliers. Poison badges count remaining turns, and help explains its constant 10% maximum-HP base tick. Burn/Bleed still show damage stacks. See COMBAT_DOTS.md.


## October 7: full-width Unit details and pinned effect inspection

Implemented in dev. The persistent Unit details window uses identity/HP and a full-width stat strip above its effects. Buffs, debuffs and other effects use two-column cards within a bounded 340px scroll area (one column and 260px on narrow screens). A lone card fills the row. Long effects no longer stretch a narrow right column beside empty stats. Traits/passives remain collapsed below; stat calculations remain available on hover/focus. Scroll position and expanded traits survive battle redraws.

Cards show compact mechanical summaries, meaningful remaining time/stack counts and source names. Poison is duration, Burn/Bleed are damage stacks, Hobble layers expire independently, regeneration counts healing ticks, and NO LINGER Songs do not advertise a misleading turn count. The description audit preserves damage scope: War Anthem excludes DoTs, Pestilence includes them, Quarry accuracy belongs to its Ranger, and weapon enchantment help describes only the selected element. Legacy non-elemental Freeze is described by its actual movement/damage rules. No combat mechanics changed in this pass.

Hovering a map status badge still shows its full explanation. Right-clicking a map/dock badge, its hover explanation, or an effect card opens one separate draggable Effect details window. Subsequent effect inspection replaces that window's contents, never the Unit details window; duplicate windows cannot accumulate. It can close independently. It refreshes with battle snapshots; an expired effect is labelled no longer active while retaining its last explanation. Hidden/missing units and exiting battle remove the related window. Opening a pinned inspector hides the temporary hover until the pointer moves again.

Validation: all 351 frontend tests and frontend build pass. Isolated Chrome checks cover the fourteen-effect card, bounded scrolling, full badge hover, singleton replacement, independent dragging/closing, map right-click, narrow viewport and existing Druid controls. Captures: staging-ui/druid-v1/details-crowded.png and effect-pinned.png. Dedicated status artwork and later map-badge crowding improvements remain deferred; this pass changes reading/inspection rather than token badge placement.


### October 7: inspector redraw performance

Unchanged Unit details and Effect details markup is now retained instead of assigned through innerHTML on every battle redraw. Battle references still update, changed content still refreshes, and changing the selected effect invalidates its cached presentation. Scroll/expanded traits remain stable. Isolated browser regression checks assert DOM identity for unchanged windows, correct changed effects, and zero API requests from History.

Measured local fixture with both windows open: median redraw about 5.6ms before and 2.5ms after; History about 9ms before and 4ms after. These are diagnostic samples, not a performance guarantee. A stress fixture of 576 cells, 74 tokens and 2,000 history entries measured about 58ms initial render and 32ms History layout. The user's recurrent broader loading regression was not reproduced or established as fixed. No startup, caching, proxy, animation timing or dev runner settings changed.


### October 7: hover scheduling and layout reads

Unit/map-effect hover and acting-character status hover now coalesce pointer events into at most one update per animation frame. Unit hover no longer serializes every status or reads token/card dimensions on every mousemove. It caches content by unit, presentation-status snapshot, action/forecast and selected effect; unchanged battle-control redraws retain that content. Card size is measured when content or viewport size changes, with token geometry read only for keyboard/no-pointer positioning. A new playback status snapshot still invalidates the explanation.

Pending updates cancel on pointer exit, blur, scroll or rebinding so a stale popup cannot appear after leaving. The existing 120ms pointer-crossing allowance, cursor-relative placement, bounded effect scrolling, full individual-effect explanations and pinned inspector controls remain. The subsequent unit-switch pass below adds a narrowly scoped hover intent delay. No new API request, loading-mode change or animation-timeline change is involved.

Validation: 353 frontend tests and build pass. Real Chrome checks send 100 pointer moves over an unchanged card with zero card-size/token-geometry reads and zero content mutations; they also check cancelled fast-exit display, retained content across control redraw, refreshed playback-status snapshots, scrolling/dismissal and independent right-click inspection. This removes confirmed unnecessary hover work; subjective smoothness still needs live playtesting.


### October 7: switching inspected units

Map hover keeps a bounded 48-entry cache of actual card nodes per battle, keyed by unit, action and selected effect. Returning to a unit reuses its card and decoded images. Changed unit/status/forecast snapshots refresh the content; unchanged markup preserves the existing nodes across control redraws. Pointer movement within a card still does no repeated content generation or size reads.

Only switching to another unit in Move mode waits 90ms (HOVER_SWITCH_DELAY_MS in combat-hover.js). The first card, movement within the same unit, keyboard focus, attack/skill/throw forecasts and right-click inspection bypass this intent delay. The old unit card hides immediately during a switch. Repeated mousemove events do not restart the same-unit timer. Exit, scroll, rebind and opening an inspector cancel pending display. Existing pointer crossing grace remains.

Validation: 356 frontend tests, build and isolated Chrome checks pass, including a three-unit sweep, cached return, pending exit and right-click cancellation, zero repeated geometry reads/content mutations, refreshed status snapshots and bounded effects. The user will assess the 90ms switch delay during play; shorten or remove it if it feels hesitant. No combat command, loader or animation changes.


### October 7: plain hover summary (current behavior)

Supersedes the preceding 90ms switch-intent/scrollable-hover presentation. Removed the unit-switch timer entirely: hover updates at the next animation frame, matching the original frame-coalesced behavior. Cached card reuse and cancellation still apply.

The cursor-following unit summary contains plain stat labels/values, including HP: no calculation tooltip markup, focus targets, hover-help styling or native abbreviation titles. The persistent right-click Unit details window retains its calculation tooltips and keyboard-focus help.

The hover effect column shows at most three compact rows. If more effects exist, it displays '+N more effects - Right-click for all'. This column has no scrolling; all effects and independent effect inspection remain available in right-click details. Individual map effect-badge descriptions remain unchanged. Browser checks verify fourteen effects become three rows plus an eleven-effect overflow hint without scrolling; pinned details still contain all fourteen. This is a presentation refinement, not proof that all live hover stutter is resolved.

Validation: all 356 frontend tests, build, hover browser checks and pinned-details browser checks pass. Unit switches display the latest target on the next frame, pinned stat calculations still open, cached cards survive return/redraw, and unchanged pointer bursts perform no repeated geometry reads or DOM replacements.


### October 7: hover movement rendering (current)

The transient card now moves using translate3d, anchored at left/top zero, with layout/paint containment and a compositor hint. It no longer toggles display off merely to switch units; the next animation frame replaces the content. Both map-unit and dock-status hover use this positioning. Pinned Unit/Effect details and stat tooltips retain their independent placement and interaction.

Transient hover is now pointer-transparent. It cannot steal pointer entry from units beneath it. The previous 120ms crossing grace and hover-card right-click interaction are removed because the summary no longer needs scrolling or interactive stat help. Leaving a unit dismisses immediately; right-click the actual unit/status badge to inspect. Cached content and full individual status-badge explanations remain.

Validation: 356 frontend tests, build and isolated Chrome hover/details checks pass. Added combat_hover_performance_qa.mjs: an isolated 90-frame movement comparison recorded 89 layout passes for left/top versus zero for translate3d; this isolates positioning, not full combat frame time. The actual three-unit sweep still performs layout for changing content (59 passes in one local sample). These results do not establish that all live stutter is fixed; user playtesting remains required.
