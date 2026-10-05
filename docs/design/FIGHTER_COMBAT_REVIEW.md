# Fighter combat and battle UI review

Updated October 5, 2026. Layout A and the Fighter disruption redesign below are
implemented in dev. Production and player saves are unchanged.

## Current playable Fighter and Layout A

Layout A is the real battle workspace: compact mission/objective/turn header,
proportionate map, bottom actor/skill/action dock, and a separate field inspector.
Hovering a character updates the inspector; it starts with the acting character.
Move, Attack, Throw, Guard, Actions and End Turn keep painted icons and boxed
shortcuts. End Turn now has a painted hourglass/shield icon. C/Escape cancels
skill targeting. All gear skills remain available with ten per hotbar page.
Auto One Turn and Auto Resolve Battle remain visible in the sidebar alongside
Leave Map and confirmed Retreat All. Map options and supplies are in a named
drawer; history/passives remain expandable. Wheel zoom, right-drag panning,
movement previews and preparation mode continue to work. Fit reserves space for
the command dock instead of clipping the bottom of the map.

| Skill | Current behavior | Cost / counterplay |
|---|---|---|
| Driving Strike | Existing single-target melee hit and one-cell push | 2 owner activations; accuracy, walls and resistance apply |
| Chain Snare (formerly Cover) | Weapon-power hit; clear three-cell reach in any direction (square range). Pull up to two cells along the dominant cardinal direction, stopping beside the caster. On hit, Hobbled halves movement, rounded down with minimum 1, for two target activations | 3 owner activations. Miss prevents both pull and Hobbled. Displacement resistance can stop the pull; ordinary accuracy/elevation, walls and existing status resistance apply |
| Earthbreaker (formerly Break Formation) | Ground-targeted leap up to three Manhattan cells after any legal walking approach. Weapon-power physical landing hit against enemies in a two-cell square radius. Inner ring pushes two cells; outer ring one. Damage resolves first for all targets; pushes then resolve inner-first so bodies can collide | 5 owner activations. Each enemy has its own accuracy roll. Resistance stops movement, not the landing hit. Open landing only, clear sight and no crossed wall; at most two levels of height change. Can leap over a gap, but cannot land in water/pits, carry payloads, or leap while movement is disabled. Area impact is not an interceptable direct strike and does not trigger a melee counter |
| Hold Together | Self-targeted rally removes Fear from self and every living ally within a two-cell square radius and line of sight. No Barrier or healing | 3 owner activations. No valid cast when nobody in the area has Fear. Walls block the rally |
| Intercept | Existing adjacent ally protection | One shared reaction |
| Riposte | Existing survived-melee counter at half attack | Competes with Intercept for the shared reaction |

Earthbreaker uses existing half-hit collision rules: solid/person collisions
add half the resolved landing damage, including friendly fire against a bystander.
Existing authored pit/fall rules and knockback resistance remain in force. The
rings are snapshotted before movement. Dead bodies do not become solid obstacles.
Capture weapons cannot use the two damaging techniques; Hold Together remains
available. Automatic play chooses a useful legal leap for groups, avoids nearby
allies and protected capture targets, and uses rally when Fear can be removed.

Stable learned/equipped IDs are retained (`cover`, `pull`, `rally`); new battles
receive the new definitions. Existing active battle snapshots finish with their
original skills. Restart Battle Lab / start a new encounter to test this pass.
Unlock thresholds and five regular slots are unchanged.

The new equal-square painted pack is recorded in
[the art prompt](../art/FIGHTER_V3_PROMPT.md). Chain contact, leap flight,
landing wave and rally ripple are timed effects; floating damage remains above
all of them. The expansion uses independent translation so its centre stays at
the landing cell. This does not approve the previously rejected Mage ground/
barrier artwork; that broader pass remains pending.

Verification: 105 related backend tests, 205 frontend tests and frontend build.
Isolated browser checks covered icons/keycaps, both auto controls, a 900px-high
workspace, exact 9-cell inner/16-cell outer previews, self-rally area, chain
contact/status feedback, landing impact, collision and C cancellation. No live
saves were used. Final visual quality/balance still needs player review.

## Historical October 4 audit

The sections below describe the previous skills and rejected visual proposals.
The current implementation above supersedes Cover, Break Formation, Hold
Together and the Layout A proposal.

## Problems found and repaired

Moving/attacking/hit tokens use z-index 44–46, above the previous 42 damage layer
and 35 hit art. A dedicated non-interactive feedback layer at 100 now contains
numbers, hit sprites and particles. Projectile/death effects sit at 90. Existing
menu/map DOM updates preserve that layer; changing modes does not remove or
replay an in-flight hit. Overlapping hit/collision labels spread horizontally
instead of covering each other's numbers.

Hotbar artwork now fills the 64 × 64 button. Names sit below and key/readiness
overlays stay small. C or Escape cancels active skill targeting and returns to
Move. C keeps its existing contextual shortcut when no skill is being targeted.

Corpse alignment differed from the living token's collapse destination. The
collapse now uses the final body's exact center, dimensions and rotation,
including cells with a body stacked under a living unit. The hidden final body's
CSS transition is disabled while measuring: otherwise its old transform is
sampled mid-transition. Browser review measured less than 0.001 px of center
difference once the collapse settled. The corpse appears after the ghost fades.

Moving collision travel now reaches contact at 220 ms and rebounds through
420 ms. Immediately blocked targets contact at 100 ms and rebound through
320 ms. Overshoot is 28% of a cell, with stronger compression and return motion.
Bystanders recoil at contact without changing legal occupancy. Collision sounds
use the newly generated `body_collision.wav` at the same timeline marker.

## All six Fighter skills

| Skill | Actual behavior | Presentation / finding |
|---|---|---|
| Driving Strike | Melee hit; attempts a one-cell push; solid collision adds half the resolved hit | Melee contact, hit number, displacement or resistance cue, collision rebound/number/audio. Tested directly against a wall. |
| Cover | 10 HP Barrier on an ally, one target activation | Barrier capacity/application feedback works. The current blue bubble is visually rejected; replacement proposal below. |
| Intercept | Redirects one attack on an adjacent ally when eligible; shares reaction allowance | Actual redirected recipient receives damage. Now announces Intercept before contact; passive icon reads as ally protection. |
| Riposte | Half-attack counter after surviving a reachable melee hit; shares reaction allowance | Separate counter attack packet, Counter cue, wind-up/contact/damage. Passive icon reads as damage. |
| Break Formation | Melee hit; attempts a one-cell pull | **Design flaw:** an adjacent target is pulled toward the Fighter's occupied cell, ordinarily colliding with the Fighter and hurting both. The melee event does exist; obscured hit art and overlapping numbers were real display problems. Mechanics intentionally remain unchanged pending redesign. |
| Hold Together | Removes Fear and grants a 12 HP Barrier for one target activation | Cleanse reports only actual removal; separate barrier capacity/application feedback. Same protection visual concern as Cover. |

Recommended Break Formation replacement: an explicitly ranged hook/drag that
pulls a distant enemy into an adjacent free cell and stops before the caster,
with clear range and destination preview. That needs a deliberate targeting/
collision-rule decision; do not silently exempt arbitrary pulls from collisions.
Alternatively author a different formation-breaking strike rather than retaining
an accidental self-damage skill. Neither replacement is implemented here.

## UI proposals

Local interactive comparison:
`staging-ui/combat-fighter-review/proposals.html` (open directly in a browser).
Screenshots: `layout-a.png`, `layout-b.png` in the same directory.
These are layout prototypes using actual map/icon art, not playable battle UI.

**A — recommended tactical workspace:** compact mission/turn header; majority
of space reserved for a full, proportionate map; bottom character/skill/action
dock; one sidebar for hovered target and selected-action preview. History,
supplies, automation, legend and retreat live in clearly named drawers. Keep
all equipment skills with paging; no gear skill limit is introduced. On narrower
screens, the inspector becomes a drawer without covering targeting cells.

**B — floating controls:** full map workspace with a bottom dock and floating
inspector. It gives more flexible space but can cover useful tiles and complicates
large maps. Avoid it as the default unless panels can be reliably placed outside
the active targeting region.

The current UI has weak hierarchy: repeated actor information, a large skill
section with much unused space, and primary/secondary controls competing with
the battlefield. An art border will not solve those layout problems.

## Barrier and ground-effect proposals

Fighter Cover/Hold Together should read as protection: restrained moving frame
light, clear capacity, short directional ripple on contact and a break on depletion.
No large glass bubble. The prototype includes an animated direction sketch with
a protection-hit button; it is not final artwork or an installed game effect.

Mage protection can use a different forcefield material with travelling highlights,
contact ripples and a depletion break. Common damage absorption mechanics should
remain shared, while the visual source distinguishes martial from magical skills.

Rejected ground art stretches a bright flat sheet over the whole footprint and
pulses decorative images. Replace it with three stages: cast impact, readable
persistent ground state, and a triggered response. Ember needs a darkened/scorched
floor and sparse rising embers, with ignition on cast and a flare on crossing.
Binding needs low tethers; sanctuary a quiet light boundary; thorns floor-integrated
growth. Preserve affected-cell clipping and gameplay rules. New texture/sprite
packs should serve those specific stages, not substitute a static image for motion.
This wider replacement is deferred until Fighter interaction/layout is reviewed.

## Verification and limits

96 related backend tests and 203 frontend tests pass. Five new tests exercise
all six Fighter skills using resolved backend events, including self-collision,
actual interception and separate counter packets. Browser checks use isolated
fixtures, not live player data: hit/collision labels above tokens, full-size skill
art, C cancellation without feedback replay, lethal collapse alignment and final
corpse reveal. A frontend test covers non-centered corpse destination geometry.

The frontend builds with its existing bundle-size warning. New audio is 48 kHz
mono, 0.922 seconds, peak -3 dBFS, with no clipped samples; aesthetic listening
approval remains pending. Audition:
`/assets/sfx/preview-fighter-contact-v1.html`. Generation prompt and model recipe
are in SFX_GENERATION_GUIDE.md / tools/generate_sfx_pack.py.

Passing tests validates these functional repairs, not production art quality.
AOE/barrier art is explicitly awaiting replacement, and neither full UI proposal
is installed. Keep further class rollout behind representative manual review.

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

## October 5: Fighter power and shockwave contact (implemented in dev)

Driving Strike uses 150% attack power before armor and other defenses. It still
pushes one cell, with half the actual hit as solid collision damage. Surviving
units involved in a wall/person collision receive one activation of Stun; a
person collision affects both people, including allies. No collision stun is
applied on resisted displacement, map edges, elevation limits or pits. Existing
control recovery immunity applies; racial stun resistance halves its chance.
Cooldown remains 2 owner activations.

Chain Snare retains its hit, three-cell square reach, pull and half movement.
On a hit it also applies Armor Fracture for two target activations: reduce armor
by 30%, rounding the reduction up, with a floor of zero. Reapplication refreshes
rather than stacks. The initial chain hit happens before the reduction. Base
armor remains intact; the unit inspector displays current effective armor.
Cooldown remains 3 owner activations.

Earthbreaker uses 200% attack power before defenses, retaining its five-owner-
activation cooldown and inner push 2 / outer push 1. The 420ms leap completes
before the ground burst. Each victim receives an independent impact packet,
delayed from landing by its distance along the expanding wave (400ms to a
three-cell radius). Damage text, push and subsequent collision contact follow
those markers; one victim's recoil cannot move another victim's impact marker.
Authoritative damage still resolves against the snapshotted area before pushes.
Earthbreaker does not gain Driving Strike's collision stun.

Design recommendation: retain the current six-skill Fighter pool and five-slot
choice. Chain Snare sets up a target; Driving Strike rewards obstacle placement;
Earthbreaker enters and breaks a group; Intercept, Riposte and Hold Together
provide protection, retaliation and Fear relief. Adding another attack now
would blur these uses. A future alternative passive could briefly brace the
Fighter after Earthbreaker, replacing another equipped choice rather than
adding free durability. That passive is a proposal, not implemented.

Existing active battles retain their saved skill snapshots. Start a fresh Battle
Lab encounter to test the new definitions. No production or player saves changed.

Validation: 107 related backend tests, 205 frontend tests and frontend build
passed. Tests cover pre-armor scaling, wall/person collision stun and immunity,
resisted push, nonstacking armor loss/restoration, ring packets and delayed
wave/impact/collision timing. The existing large-bundle build warning remains.

Browser validation: isolated real-UI fixtures at 1440x1100 and 1440x900 show
Earthbreaker hit/collision numbers over tokens after the landing burst, correctly
centered expanding shockwave, Chain Snare hit/Hobbled/Armor Fracture feedback,
area rally targeting and retained auto controls. No live save was used.

## October 5: rendered movement ordering repair (implemented in dev)

The previous wave-marker fix did not solve a second rendering bug: separate
Web Animations with backwards fill let a later enemy movement apply its starting
pose before an earlier push began. Damage/impact markers were correct while the
visible token was already displaced. Each token now receives one composed
transform timeline that holds its original position, plays the hit/push, holds
between segments, then plays its own enemy move. Melee lunges/recoils anchor to
the event's contact cell instead of the response's final cell. Overlapping
bystander collision recoil during its own push flashes without replacing that
push trajectory.

Player commands and combat hotkeys are blocked during resolved attacks and the
complete enemy animation sequence. Buttons show a Resolving turn notice and
restore their original availability when playback ends. Command entry points
also enforce the lock before optimistic movement or queued requests. Pure player
movement previews remain interruptible for fast repositioning. Lingering damage
labels do not extend the lock. Camera movement and unit hover remain available.

Validation: 210 frontend tests and build pass. Five new tests cover composed
poses/holds, delayed wave contact followed by pursuit, contact-cell lunges,
playback deadlines and free player repositioning. Browser checks use actual UI
and backend fixtures containing a push followed by that same enemy's own turn:
Driving Strike at 80ms and Earthbreaker at 250ms show zero premature victim
movement on either axis. Map click, Space and direct move commands produce zero
requests while locked; controls unlock after the sequence. Existing two-victim
collision, chain/rally and 1440x900 layout browser checks also pass. No backend
rules, production or player saves changed. Existing build-size warning remains.

## October 5: map-first dock and hover cards (implemented in dev)

Removed the right rail. The map spans the battle workspace, with acting character,
large skill icons and a separate three-column/two-row command box in the bottom
dock. Action Preview is a readable strip beneath the dock contents rather than
a popup covering targets. Turn order uses compact framed portraits with clear
position numbers and current-turn emphasis; it scrolls horizontally when needed.

Hovering or keyboard-focusing any visible unit opens a 390px card beside it,
clamped to the viewport. It includes HP, current armor, attack, movement, range,
available accuracy/evasion/initiative/level, elevation, weapon, status explanations
and passives. Long cards scroll; the pointer can enter the card to read details.
During Attack/Subdue/targeted Skill selection it also shows the available attack
forecast, including approach movement and interception. No concealed enemy
identity is exposed by these cards.

Damage previews report HP damage on a successful direct hit and accuracy,
separately. They share the combat damage calculation: skill power, elevation,
armor/Armor Fracture/Vulnerable, racial/perk/gear bonuses, element effects, Guard
and current Barrier absorption. Previewing uses only a copied target and does
not consume guard, statuses, shields or rolls. Collision, reactions, finishing
safeguards and chance-based on-hit effects are not promised in this number.
Throw previews label their existing raw impact power explicitly. Ground-targeted
AOE per-victim forecasts were added in the later audit below.

A compact toolbar above the map opens Supplies, Passives, History and Battle
options in centered dialogs. Supply targeting, per-battle usage rules, both auto
buttons, tactic selection, exit and Retreat All confirmation are retained.
Dialogs close via X, Escape or an outside click. Mousewheel zoom/right-drag pan
remain; the redundant visible +/-/zoom buttons are removed. A small crosshair
button fits the whole map. These changes retain playback locking.

Validation: 109 related backend tests, 211 frontend tests and build pass. Browser
checks at 1440x900 confirm the command box is in the dock with three columns,
no right rail, a bounded hover card with live forecast/status data, working
Supplies/options dialogs and both auto buttons. 1000x800 has no horizontal
modal overflow; short screens can require vertical scrolling. Existing build
size warning remains. Dev only; no player saves or production changed.

## October 5: attack rubberband and area forecast audit (implemented in dev)

Walking segments now end at their own path destination, rather than the final
position of the entire response. A unit can walk, attack, react and walk again
without jumping between the later saved tile and the attack tile. An attack
interrupting an unfinished player preview first settles the short visible path.
Hit reactions start neutral instead of showing recoil before contact.

The resolving-turn notice is positioned outside layout flow: it no longer
resizes a fitted map halfway through pixel-based motion. Earthbreaker's complete
650 ms landing effect and every victim push, rebound and collapse finish before
the next unit begins movement. Per-victim wave contacts remain distance-based;
floating damage labels can linger without delaying the next turn. One composed
transform animation per token is retained, not a separate rules engine.

Unit stats follow the lower right of the cursor, clamped to the screen, and hide
immediately when the pointer leaves the unit. Cards do not intercept the pointer.
Ground previews show compact labels at each affected visible unit. Earthbreaker
forecasts include damage after armor/guard/barrier, accuracy, push and resistance;
zone labels distinguish future entry damage/control or activation healing from
an immediate hit. Adjacent labels stagger with connector lines. Forecasts do not
consume statuses, shields, RNG or mutate the battle. Hidden enemies are excluded.
Collision damage, reactions and random on-hit bonuses remain conditional, not
included in the direct-hit estimate. Large crowds and extreme zoom still warrant
manual visual review; this is not a claim of exhaustive visual verification.

Validation: 110 related backend tests, 218 frontend tests and build pass. Isolated
browser tests verify walk/attack/later-walk poses at four timeline samples, no
premature shift in Driving Strike/Earthbreaker, rejected commands during playback,
unlock afterward, collision feedback, cursor following/immediate hide, and two
nonoverlapping area forecasts. A two-enemy fixture averaged about 10 ms per
battle_view call over ten runs; this is not a large-map benchmark. Existing bundle
size warning remains. No live saves or production changed.
