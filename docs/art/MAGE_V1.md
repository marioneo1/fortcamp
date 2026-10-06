# Mage V1 packed art and local audio

Current Meteor: 6.75-cell falling sprite, upper-left-facing, with new ground revealed at impact. Current fire art: [Scorched V3](SCORCHED_V3.md).


Surface update: [Mage surfaces V2](MAGE_SURFACES_V2.md) replaces the initial `ice_shell` and `scorched_tile` rendering with two dedicated 4×4 sheets. Other V1 icons/projectile/contact art and audio remain current. The initial sheet is retained as a reference; its old surface assets are no longer the active presentation.

Implemented in dev October 6, 2026. One transparent 4×4 atlas supplies eight consistent square ability icons and eight reusable isolated spell assets. It follows existing painted fantasy maps and gold-framed skill icons. No Effekseer dependency or animation runtime was added: browser sprite motion uses the existing contact clock and Web Animations, with static/fading reduced-motion alternatives.

## Assets and import

`frontend/public/assets/mage-v1/` contains 256px icons: `chain_lightning`, `flash_freeze`, `singularity`, `meteor`, `fireball`, `enchant_weapon`, `typhoon`, `debuffer`.

384px transparent effects: `lightning_arc`, `ice_shell`, `frost_ground`, `gravity_vortex`, `meteor_rock`, `fire_contact`, `scorched_tile`, `wind_ring`.

Generated source is retained at ignored `staging-mage/mage-atlas.png`; the reviewed contact sheet is `staging-mage/review.png`. The image generator returned `exec-75902e73-9523-47fe-8e7e-65ab1a2bff51.png`. Runtime crops are committed; large generated references are not shipped.

Reimport the SAME reviewed 1254×1254 atlas with:

```powershell
.\.venv\Scripts\python.exe tools/import_mage_atlas.py
# Or supply the atlas path as the first argument.
```

The importer uses custom reviewed gutters, x boundaries 0/314/628/942/1254 and row boundaries 0/307/600/900/1254. Lightning's bottom is trimmed at 880 to remove an adjacent Meteor fragment. Each crop trims transparent alpha, preserves aspect ratio and centres into its output square with padding. These bounds describe this atlas, not arbitrary future generations. Visually inspect any replacement atlas before importing.

### Generation brief for a replacement/reference pack

Use one evenly partitioned 4×4 sheet with transparent background and ample empty gutters. Match the established hand-painted fantasy tactical-game art and ornate square gold-framed skill icons. No labels, letters, numbers or mockup scenery. Top two rows: Chain Lightning (violet branching electricity), Flash Freeze (blue ice around a silhouette), Singularity (purple gravity well), Meteor (burning rock), Fireball (orange flame sphere), Enchant Weapon (blade with three elemental colours), Typhoon (cyan wind spiral), Debuffer (violet weakening spell). Bottom rows: isolated horizontal lightning bolt, hollow ice cage/ring that leaves a portrait face visible, top-down frost burst, top-down purple gravity vortex, isolated falling burning rock, orange fiery contact burst, purely top-down charred cracked ground tile, top-down cyan wind ring. Keep effect silhouettes separate, no frames around the effect cells, no assets touching adjacent cells. Fill the pack with these usable pieces; do not spend cells on redundant backgrounds.

## Playback

Lightning links each previous victim to the next; 120ms bounce offsets share damage timing. Fireball travels from the caster then bursts; Meteor now uses a 4.5-cell falling sprite (previously 2.5), then impacts at the same 420ms contact. The existing seven-cell impact burst and gameplay radius remain. Gravity/wind expand and rotate; ice persists around a Frozen token. Scorched terrain uses the dedicated surface kit described above, now with large central cinders and independently phased smaller fires. Damage feedback remains above spell art. Transient effects remove themselves on finish/cancel, skip hidden/disconnected fields and respect reduced motion.

## Audio

Five short stereo PCM clips at `frontend/public/assets/sfx/`: `mage_lightning.wav`, `mage_freeze.wav`, `mage_gravity.wav`, `mage_fireball.wav`, `mage_typhoon.wav`.

They are deterministic procedural sounds authored locally with Python's standard library, **not ElevenLabs outputs**; no cloud-audio tool was available for this pass. Reproduce with `tools/generate_mage_sfx.py`. Clips use layered noise/tones, short envelopes, bounded peaks and quiet stereo spread; duration approximately 0.34–0.65 seconds, no clipping in sample checks. Existing audio settings/mute/gesture handling remain.

Meteor uses approved dry `earthbreaker_land` + `earthbreaker_crater` with quiet Mage fire at impact, rather than the shrill generic cast tail. Mage spell contacts use their dedicated clips; preparation/enchantment retains a quiet magical cast cue. Human listening and in-game mix tuning remain necessary; numerical waveform checks are not a listening test.

## Reproducible visual QA

`tools/build_mage_preview.py` constructs isolated in-memory gameplay fixtures and never reads/writes player saves. Serve through the existing `tools/serve_board_preview.mjs`; `tools/mage_browser_qa.mjs` connects to a separately launched local Chrome debug session on port 9229. It checks icons, the centred enchant dialog, cancellation/selected element, ice, channel warnings, transient impact effects and cleanup. Captures are stored in ignored `staging-ui/mage-v1/`. It is development tooling, not a production endpoint.
