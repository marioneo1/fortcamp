# Summoner portrait, icon and effect atlas

Generated with the built-in imagegen tool, October 7, 2026. Original and exact
prompt: `staging-ui/summoner-v1/atlas.png`, `prompt.txt`; crop manifest alongside.
Importer: `tools/import_summoner_art.py ATLAS_PATH`.

Runtime: `frontend/public/assets/summoner-v1/`, sixteen 256px PNGs.
Four-by-four atlas, no labels/separators:

| Row | Cells left to right |
|---|---|
| 1 | Fire fox portrait, Earth golem portrait, Grass spirit portrait, Wisp portrait |
| 2 | Transposition, Bound Companion, Wisp Swarm, Spirit Projection |
| 3 | Sacrifice, Overload, Life Pact, Rapid Conjuration |
| 4 | Conjure portal, spirit projectile, spirit explosion, nature burst ring |

Inspected full atlas before cropping. Equal-cell bounds with three-pixel insets
prevent sampling neighboring icons. Last row retains original alpha. Portraits
use the standard battle circles; these are not animated animal map sprites.
Portal/burst/explosion animation uses scale, rotation and fade with reduced-motion
support. Current Projection uses the shared magic projectile for moving bolts;
the generated projectile cell supplies its cast accent.

Six generated audio clips live in `frontend/public/assets/sfx/summoner_*.wav`.
Exact prompts/originals/checks: `staging-sfx/summoner-spirit-v1/`; generation guide
section **Summoner spirit pack**. Run `tools/generate_sfx_pack.py --pack
summoner-spirit-v1` to reuse retained originals and reprocess them. All six are
nonempty mono 48 kHz WAVs with no final clipped samples. Listening review remains
open. Preview: `/assets/sfx/preview-summoner-spirit-v1.html`.

Isolated UI screenshots: `staging-ui/summoner-v1/companion-placement.png`,
`group-orders.png`, `projection-preview.png`, `sacrifice-playback.png`.
Browser QA never reads live saves.
