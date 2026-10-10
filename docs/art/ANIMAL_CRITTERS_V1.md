# Animal art and audio handoff

October 8, 2026. Dev only; no prod/save changes.

**User requirement: future image batches use the usual 5 columns x 4 rows.**
Do not generate portraits individually. All ten individual requests were already
queued before the correction and completed; no generation remains running.
Reuse these outputs; do not regenerate them to make a sheet.

Originals and exact prompts: `staging-portraits/animal-critters-v1/`.
[Source manifest](ANIMAL_CRITTERS_V1_SOURCES.json) retains original generator paths
and prompts. Runtime copies: `frontend/public/assets/animals-v1/`, 512 pixels.
Preview: `/assets/animals-v1/preview.html`; combined preview: `preview.jpg`.
Combining these existing outputs uses no image generation.

Ten portraits: rat, rat swarm, rat boss, wolf, wolf boss, bear, bear boss, boar,
bat, giant spider. Current audited E-rank rats/wolves use the art; other portraits
are future assets only. Style reference: `reference/portrait-art-reference.png`,
the authoritative reference used for male/female portraits. Built-in imagegen;
no LinkAPI helper. Visual/circular-crop inspection remains pending.

27 ElevenLabs clips: three variants each of rat attack voice, bite, hurt, death,
swarm gathering; wolf attack voice, bite, hurt, death. Originals, exact prompts
and technical/billing report: `staging-sfx/animal-combat-v1/`. Runtime WAVs:
`frontend/public/assets/sfx/`. Listening preview:
`/assets/sfx/preview-animal-combat-v1.html`.
All 27 are nonempty mono 48 kHz with no clipped output samples. One source
had one clipped sample. API-reported character cost: 234. Listening approval
is pending; technical checks cannot judge sound quality.

`combat-audio.js` uses stable species identity and animation events for timing;
never infers death timing from final unit condition. Rat/wolf attacks get animal
voices and bites instead of weapon swings. Three-rat contacts: 100/280/460 ms.
Hurt requires actual direct damage; defeat events trigger death (knockout uses
hurt). Merge gets gathering audio. Voices are quieter than contacts. Variants
vary across activations. Human weapon contacts are retained.
Merge snapshots preserve old/new portraits and update the map image at merge
completion. Image warmup includes animal and swarm art.

Checks before interruption: 409 frontend tests and 22 encounter tests passed;
frontend build passed with existing large-chunk warning. Backend portrait
snapshot assertions also passed on rerun (22 encounter tests). Frontend rebuilt
after art installation, so dist now contains the portraits and sounds. Manual browser/audio/visual review remains.

Reimport without generation:
`.venv/Scripts/python.exe tools/import_animal_portraits.py staging-portraits/animal-critters-v1`.
Sound generator reruns reuse sources:
`.venv/Scripts/python.exe tools/generate_sfx_pack.py --pack animal-combat-v1`.

## Boar combat vocals (October 9)

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
