# Combat status presentation

Implemented in dev, October 5, 2026. Reference: the player supplied
`question/dota 2 buff and debuff.png`. Its useful principle is readable square
art with distinct positive/negative framing, adapted for a turn-based map.

## Current display

- The acting character has a full-width status strip in the bottom command dock.
  Green-framed Buffs, red-framed Debuffs and blue-framed Other effects are
  separated and named. Icons are 48 px, with short names underneath.
- Map units show all compact effects as 36 px square art, arranged above the
  portrait from the upper-left of its enclosing box, wrapping into further rows.
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
