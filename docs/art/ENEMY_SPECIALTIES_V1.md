# Enemy specialty art and audio

October 9 Tripline refinement: the full three-cell strip uses one continuous
painted rope with two end stakes, not a repeated prop per cell. SVG cropping
excludes the stray gold atlas edge without modifying the source PNG; the separate
zone boundary is omitted for Tripline. Horizontal/vertical browser fixture:
staging-sfx/archive/superseded-files-20261009/staging-ui/tripline-v2
(preview.html and preview.png, archived after approval). Placement/trigger rules stay
unchanged: the first qualifying crossing snaps the whole strip.

Implemented in dev October 9, 2026. One packed 5-column by 4-row sheet, generated
with the built-in image tool using the existing Rogue atlas as style reference.
No external LinkAPI image helper and no single-icon generation calls.

Source: staging-ui/enemy-specialties-v1/atlas.png. Exact crop coordinates and
asset names: crop-manifest.json in that folder; reproducible importer:
tools/import_enemy_specialty_atlas.py. Eight painted skill icons and twelve
transparent props/impacts live in frontend/public/assets/enemy-specialties-v1.
Effects include rope set/snap, wet physical strikes, retreat, sling stone,
Tag Team crossing, Cornered Fury and Heel Cut. Browser Web Animations handles
projectile travel and short fade/grow impact timing; no new Effekseer runtime.

Nine ElevenLabs sound effects generated with retained sources by
tools/generate_enemy_specialty_sfx.py; that script contains the exact prompts,
duration targets and reuse policy. Runtime WAV files are in
frontend/public/assets/sfx: specialty_tripline_set/snap, shakedown, parting_cut,
ankle_bite, goliath_shot, tag_team, heel_cut and cornered_fury. Sounds are physical
foley, not bespoke humanoid race/gender/personality voices. The source helper's
single generation_report.json only retains the last clip's metrics; prompts for
all nine remain in the script and original source clips are retained.

Frontend tests verify all eight icon paths, all nine valid installed WAVs,
specialty-status art lookup and three-cell horizontal/vertical rope artwork.
Full live aesthetic review is still needed; generated assets and passing tests
do not establish subjective visual/audio quality.
