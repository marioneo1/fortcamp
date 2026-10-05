# Combat status presentation

Implemented in dev, October 5, 2026. Reference: the player supplied
`question/dota 2 buff and debuff.png`. Its useful principle is readable square
art with distinct positive/negative framing, adapted for a turn-based map.

## Current display

- The acting character has a full-width status strip in the bottom command dock.
  Green-framed Buffs, red-framed Debuffs and blue-framed Other effects are
  separated and named. Icons are 40 px, with short names underneath.
- Map units show two priority effects as 24 px square art, plus a count for any
  remaining effects. Control statuses take priority, then damage over time.
  This avoids covering portraits with an unbounded row. Hover the unit to see
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
No new image generations, new status mechanics or gameplay balance changes were
made in this pass.

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

The previous 520 ms faded recording still had an unwanted late accent. The
importer now keeps only the first 220 ms, filters out treble above roughly
1 kHz using two low-pass stages, and uses a 12 ms edit edge to prevent a click.
The later recording is discarded entirely, rather than faded underneath.
Initial loudness gain is retained; there are no clipped samples. The original
MP3 remains intact and rebuilding derives this edit from the original. No paid
request was made. The game uses a new landing asset version after refresh.

## Verification and remaining work

232 frontend tests and frontend build passed. Tests cover grouping, ordering,
finite absorption versus duration versus one-use counts, per-owner Marks,
installed icon files, overflow, defeat/recovery and Stun contact timing.
Isolated browser checks verified 40 px dock / 24 px map icons, uncropped square
art, both groups, poison hover duration, three animated stars, static reduced
motion and removal after recovery. Review capture:
`staging-ui/combat-fighter-review/status-review.png`. Fixtures do not use live
player saves. Production was not changed.

Player listening/visual feedback remains the final quality check. Next focused
visual passes: Burn, Freeze, Barrier; then remaining control effects and
condition-specific icon artwork. These are pending, not implemented.
