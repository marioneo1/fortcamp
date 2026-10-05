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
