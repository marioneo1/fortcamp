# Animal mounts

Implemented in dev October 9, 2026. Start a fresh Boar-Rider Patrol to test.

## October 9: zoom, facing and lethal shockwave follow-up

Implemented: map effect badges scale with cell width (22%, capped at 36 px),
including smaller counts; no fixed minimum row width. HUD/detail icons unchanged.
Stationary mount redraws preserve the continuous visual angle when the saved
facing is unchanged; playback only resets facing for the mount's own walk/attack.
Mounted deaths persist `mounted_death`: overhead corpse only if mounted at defeat;
free/dismounted animals retain their portrait corpse. Corpse layers remain beneath
living units, including hover and motion styles. Existing unflagged corpses use
portrait presentation; a fresh fight exercises both death contexts.

Earthbreaker and Groundbreaker still damage both mounted bodies, but displace a
surviving linked pair once per shockwave. Lethal AoE bodies with separate routes
animate independently. Mount fall/release waits for its packet's displacement;
collision feedback cannot overwrite an ongoing paired push. Browser QA exposed
and fixed overlapping collision/movement frames that previously caused an invalid
Web Animation timeline. No general animation framework or skill balance changes.

Validation: 65 targeted backend tests (mounts, Fighter presentation, D-rank),
438 frontend tests and build pass. Isolated browser fixture uses real lethal
Earthbreaker events: body remains at source before contact, then pushes/collapses;
checks paired motion, corpse layer, zoom badge sizing and continuous facing redraw.
QA processes stopped. No dev restart or release push.

## Player rules

- **Rider** is a persistent perk on all patrol riders and their captured recruits.
  It adds innate **Mount / Dismount** buttons without using a Job skill slot.
- Mounting an adjacent, conscious allied boar is a Quick Action. Dismount targets
  yourself and uses the first legal adjacent exit, clockwise from north. Once
  per activation; no cooldown. Walls, occupied exits and restraints are respected.
- Mounted riders gain **+1 movement**. Mounted rider and boar take **25% less
  damage**, including DoTs, through normal damage calculations and rounding.
- Rider and boar have separate HP and are independently targetable. An aimed
  hit damages the selected body; AoE/hazards can reach both. No damage sharing
  or automatic interception was added. The optional 60/40 sharing suggestion
  remains unselected and is not an implemented rule.
- A lost mount rolls once: **25% hard fall** (50% mount maximum HP damage and
  one-turn Stun), **50% rough landing** (25% mount maximum HP damage and
  one-turn Hobble), or **25% clean landing** (no damage/control). Damage rounds
  up and can kill; normal Barrier/incoming modifiers apply after mounted
  protection ends. Overkill does not change the penalty; save/load cannot reroll it.
- Mounted boars have no extra autonomous attack activation. Their statuses
  begin/end with the rider's activation; DoT damage and stack decay occur once.
  A free boar can take its own normal turn. Incapacitated mounts stop riding
  movement; changing bodies does not erase spent movement.
- Both bodies share committed movement, forced displacement and hazard entry.
  Rider defeat releases the surviving boar. Extraction takes the mount along.

## Patrol and balance

First three layouts start mounted. Fourth includes two riders with adjacent
free boars; their AI mounts when legal before continuing its ordinary action.
Boars have **16 HP**, or **12 HP** in the four-rider variation, and 3 Attack when
unmounted. These are explicit species profiles, not a second rank multiplier.
Original humanoid allocations, Job kits, capture parity and rewards are retained;
the old unconditional mounted movement bonus is replaced by actual mounting.

Rider chooses either body as a target; portrait center selects rider and the
exposed animal selects boar. Separate HP badges and a Mounted effect explain
the protection and fall risk. Mounted art is overhead; free boars retain their
ordinary portrait. The atlas contains facings, walking frames, corpse and button icons from
from one transparent 5×4 atlas in staging-art/boar-mount-v1. Runtime slices are
in frontend/public/assets/boar-mount-v1. The rider's identity image is reused.
Death/release presentation waits for attack contact rather than showing final
mount state before the enemy attack plays.

## Validation and remaining work

Targeted tests cover separate damage, once-only fall, mounting action economy,
save round-trip, status timing, shared movement and recruit perk preservation.
Frontend tests cover asset existence, mount-state playback and button art.
Isolated browser fixture verifies both loaded portraits/art and independent
hit targets. D-rank all-6 Human duos: 24 autonomous smoke fights, no stalls or
errors, 20 successes / 4 defeats; layouts won 4/6, 5/6, 5/6, 6/6 respectively.
This is a smoke check, not a substitute for tactical player testing.

Deferred: animal capture/roster persistence, other rideable species, detailed
mount personality behavior, mount-specific voice generation and chosen-tile
dismount UX. No story histories, dialogue triggers, race or quest IDs were added.
Existing saves are not supplied new boars. No release deployment/server restart.

Regression note: the full 1,132-test backend run found one old contract assertion
that assumed every enemy shares the humanoid race; updated it to recognize Beast
mounts and reran that contract check. Eleven other failures remain in ambush,
legacy capture/zone fixtures and the old 120-second recovery expectation.
All eleven reproduce with every mount hook disabled (5 failures, 6 errors).
They are recorded separately rather than changing unrelated systems here.
All 433 frontend tests pass; build succeeds with the existing bundle-size warning.

## October 9 follow-up: rider-owned Boar Charge

Rider now describes allied mounts, with species bonuses/techniques. Only boars
are currently available. Mounting a boar adds `innate:rider:boar_charge` to the
rider without consuming an equipped slot; dismount or mount loss removes it.
Boar Charge uses a main action, three-activation cooldown and a clear cardinal
line. Starting target distance 1/2/3/4 gives 1.25/1.5/1.75/2.0 times rider attack
power, stopping adjacent. Only a landed four-cell hit attempts one-turn Stun;
normal Stun resistance applies. Approach hazards resolve on both bodies and
can stop the charge. This is dedicated skill movement, not a normal movement
refill. Existing walking/strike presentation is reused. AI chooses a legal
straight charge before its ordinary attack; no new animal AI framework.
Targeted mount/D-rank checks cover tiers, shared movement, blockers, miss,
immunity, dismount, save/fall outcomes and hazard interruption.

## Mounted presentation refinement (October 9)

Rider portrait is 75% of the normal token size. One fixed overhead boar pose
sits underneath; no stride/facing image swaps during actions. Shared motion
pairs walking bounce, live movement previews, attacks, hit recoil and forced
movement, using the mount link at each event's playback time. Delayed fall/
release ends pairing only when that event plays. Corpse keeps the living boar's
96%-cell footprint rather than inheriting the smaller humanoid corpse layout.

One effects row is drawn on the rider. Identical status badges are deduplicated;
different status values/owners remain inspectable with their actual body owner.
Rider and boar HP, targeting and combat statuses remain independent; this is
visual grouping, not shared status propagation. No balance/race/story changes.
Validation: all 436 frontend tests, 25 mount/D-rank backend tests and build pass.
Browser QA exercises actual animation code through knockback, attack and later
walking, checking both token centers stay aligned throughout; exposed mount and
rider remain independently targetable. Existing build chunk warning remains.

## Facing and sprite-boundary correction (October 9)

The fixed live image now rotates smoothly toward each movement step or attack
while the rider portrait stays upright. Turns use the shortest angle (140 ms);
forced knockback preserves facing. Direction changes are scheduled at their
playback event, not applied from the final server position before the action.
Reduced-motion preferences disable the turning transition. No stride swaps.

The original grid slicer cut the right-facing snout and included neighboring
feet in the death image. Explicit subject bounds now import both complete
silhouettes from the approved source sheet, including transparent margins;
no new generation. Importer and source manifest record the corrected bounds.
Asset version query prevents old browser-cached crops. Corpse keeps full size.

Mount layering follow-up: generic walking/attack/hit styles gave both bodies
the same raised layer, letting the later DOM boar cover the portrait. Explicit
ordered layers now keep rider above mount during idle, hover and every motion.
Browser playback checks both aligned centers and rider-above-boar layers.
Facing/crop update passes all 437 frontend tests and browser checks; build passes.

Overhead-pose correction: rotate the top-left north-facing overhead boar, not
the side-biased east pose. Isolate its full silhouette with corrected crop
bounds (remove neighboring artifact). Keep existing 96%-cell mount container
and 75% rider; no extra shrink requested. No walking sprites. Death sprite
uses a -90-degree basis correction to share the overhead facing convention.

Boar scale correction: tightening source crops removed transparent padding and
made the animal appear larger. Render its artwork at 80% of the mount container
(10% inset per side), for both living and dead poses; keep rider at 75% standard
size. Hit targets, paired motion, facing and combat mechanics are unchanged.

Boar head/rear clipping root cause: generic `.battle-token img` used cover and
overrode the earlier mount contain rule at equal specificity. Mount image now
uses an explicit scoped `object-fit: contain !important`; size remains unchanged.
Browser fixture loads generic character CSS after mount CSS to reproduce actual
cascade, checking computed contain/no clipping as well as motion/layering.

Final containment/proportion correction: remove the temporary 10%-per-side
art inset now that cover clipping is fixed. Full contained overhead silhouette
uses the original 96%-cell footprint, extending beyond the 75% rider frame.
Keep explicit contain, clean crop, shared motion and ordered layers.

Mounted readability: target reticle stays within the rider frame instead of
covering the animal outline; animal art sits 12% lower beneath the portrait.
This constant art offset does not alter paired token motion or unit coordinates.

Current mounted presentation: boar artwork is centered again (remove downward
offset) and 25% larger than its previous contained image, behind the unchanged
75% rider. Attack facing now persists on the actual mount, so redraws after an
unrelated player action do not revert it to a prior walking direction. Forced
displacement preserves facing. Own walking/attacks still deliberately turn it.
No walking sprites or combat balance changes.

## Boar combat vocals (October 9)

Target readability: mounted boars use the standard hostile/throw target reticle
at 147.2% of the animal token footprint (23.6% outset; 15% larger than the initial marker), with slightly stronger
opacity. Rider targets keep the smaller portrait marker. Animal reticle does
not appear on dead mount artwork or during ally-support targeting. Markers are
visual only and do not enlarge hit targets or change targeting legality.

Presentation follow-up: living mounted animal artwork receives a sun-direction
shadow on a nonrotating wrapper, leaving rider labels and the portrait unfiltered.
Dismounted circular animal portraits do not receive this additional shadow.
Parting Cut's backward skid preserves attack-facing instead of turning the mount
to face its retreat; ordinary deliberate walking still changes facing.

Nine generated ElevenLabs clips: attack / hurt / death, three variants each.
Runtime assets: `assets/sfx/boar_{attack,hurt,death}_{1,2,3}.wav`.
Sources and per-clip prompts/metrics: `staging-sfx/boar-combat-v1/manifest.json`;
reruns of `tools/generate_boar_sfx.py` reuse original MP3s without rebilling.
Listening page: `/assets/sfx/preview-boar-combat-v1.html`.

Saddle-boar species uses stable animal identity. Free boars vocalize on attacks
alongside normal contact foley; mounted rider attacks do not add boar cries.
Actual damage to either free or mounted boars can trigger hurt (including DoTs);
healing/status application/zero damage cannot. Lethal packets use death instead
of an additional hurt cue, scheduled at collapse rather than final saved state.
All nine outputs are nonempty mono 48kHz with zero clipped output samples.
Listening approval remains unclaimed; generated audio installed in dev.
