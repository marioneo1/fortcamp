# Flesh and armor contacts V1

Implemented in dev, October 5, 2026. Extends the existing melee presentation; no additional renderer, runner or production changes.

## Selection and timing

Organic targets in cloth, leather or no body armor use six new contact sounds. Slash, hack, crush and stab use eight painted crimson/ivory contact/fade sprites; blunt and fist retain their bloodless art with dry body-contact sounds. Basic fist/blunt lethal hits keep their collapse but suppress the blood burst. Metal armor and Automatons retain the original family impacts. Golem, deathless and slime bodies retain their existing non-blood presentation.

The selection uses body armor material and anatomy, never numerical defense. Player body equipment derives material from explicit armor_material or its item name. Contract enemy material is authored: Hobgoblin Vanguard and Black Banner escort use chain, Black Banner captains use plate; archers use leather. The fallen knight uses plate but deathless anatomy remains bloodless. Other unspecified organic enemies default to flesh. Custom future equipment/encounters can set armor_material or body_material explicitly.

All normal melee contacts remain at 185ms. Misses do not play flesh impacts. A fully absorbed hit has barrier feedback without a flesh contact sound. Net restraint damage stays bloodless and uses the existing 320ms tightening marker.

## Artwork

Source: staging-ui/flesh-contact-v1/atlas.png. The first hazy generation is preserved separately as rejected-haze-reference.png. The alpha edit produced a transparent 1536x1024 atlas. Equal four-column/two-row crops preserve proportions on 256px canvases; no stretching or source trimming. Run python tools/import_melee_effects.py --flesh. Runtime art: frontend/public/assets/flesh-contact-v1. The cells are slash contact/fade, hack contact/fade, crush contact/fade, stab contact/fade.

Built-in imagegen generation prompt:

```
Create ONE transparent game VFX sprite atlas in the SAME warm painterly fantasy art style and brushwork as the attached ivory/gold slash impact. Requested canvas 1536x1024, EXACTLY four equal columns and two equal rows, no gaps, no separators, no labels. Each sprite wholly inside its cell with generous transparent margins, centred. 8 distinct reusable contact sprites in row-major order: top row sword slash contact, sword slash fade, axe chopping contact, axe chopping fade; bottom row hammer crushing contact, hammer crushing fade, spear/dagger puncture contact, spear/dagger puncture fade. These are SHORT ABSTRACT EFFECTS for hitting flesh or leather instead of metal: sharp warm ivory cut accent with dark crimson fine droplets for slash; broader heavier diagonal crimson burst with warm short chopping streak for axe; compact low heavy round crimson splash and dull ochre fragments for hammer; tight narrow pointed ivory stab and small crimson spray for spear. Fade counterpart of each is sparse dissipating droplets. Stylized modest blood, no gore, no bodies, no organs, no wounds or people, no weapons, no opaque background plates. Transparent alpha between fine droplets and through empty areas. No huge splashes that hide a portrait. Keep hues, painted texture and stroke quality consistent across all 8 cells. Do not crop any silhouette against a cell edge.
```

Alpha-correction prompt:

```
Edit this exact 4x2 atlas. REMOVE ALL background haze, brown and orange fog and the dark backdrop. Make the entire background fully transparent alpha, including all empty areas between the eight separate effects and gaps between individual droplets. Preserve all eight foreground effects exactly at their existing positions, sizes, orientations and equal cell spacing. Retain sharp painted ivory slash accents, ochre small fragments and crimson blood droplets. NO opaque color plates, gradients, lighting haze or ground. Keep foreground edges antialiased on transparency. Output a genuinely transparent PNG sprite atlas, same canvas and layout, not an image displayed on a dark backdrop.
```

## Audio and verification

Six dry contact clips use the existing ElevenLabs generator: python tools/generate_sfx_pack.py --pack flesh-contact-v1. Exact audio prompts are in SFX_GENERATION_GUIDE.md. Originals/reports remain in staging-sfx/flesh-contact-v1; normalized 48kHz mono WAVs install under frontend/public/assets/sfx. No final clipped samples; one source crush clip contained one clipped sample before normalization. Subjective listening review remains the player's decision.

Audition at /assets/sfx/preview-flesh-contact-v1.html. Technical checks are not a claim of human listening approval.

117 related backend tests, 247 frontend tests and build pass. Isolated browser checks exercise six flesh families, metal/Automaton contacts and net capture/escape/miss, with real damage labels and correctly selected assets. Screenshots: staging-ui/flesh-contact-v1/*-browser.png. The static fixture has no live backend/favicon; all combat assets load. Existing bundle-size warning remains. Ranged presentation is deferred.
