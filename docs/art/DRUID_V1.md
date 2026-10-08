# Druid presentation assets — October 7, 2026

Two native-imagegen packs were generated and imported locally. No external
LinkAPI helper was used. Animal forms use circular portrait tokens, not walking
animal sprites. Originals are retained under `staging-ui/druid-v1/`.

`icons-atlas.png` is an equal 4×3 grid: eight ability icons, three animal
portraits, and the humanoid-return icon. Equal proportional cells were cropped
and resized to 384×384 with Pillow LANCZOS. Runtime directory:
`frontend/public/assets/druid-v1/`. Icons remain square with painterly forest,
emerald and gold art; portraits use complete centered animal heads.

`vines-atlas.png` is a transparent 4×2 grid. Top row: idle, ready, lash and settling
bramble frames. Bottom row: destroyed bramble, leaf transformation ring,
restoration motes and vine whip. Same proportional import and size. Idle and
destroyed props also live under `assets/combat-terrain/props/druid_bramble.png`
and `druid_bramble_broken.png` for existing terrain rendering. Three ground
segments share the gameplay HP pool. A short vine stretch and frame sequence
play on reactions; no continuously running particle engine was added.

Generated art follows existing ignored-asset policy: include these runtime files
when creating a later release. This pass does not deploy production.

## Native generation prompts

### Icons and animal portraits

Fortcamp fantasy tactical RPG hand painted asset atlas. Exactly 4 columns by 3 rows of equal square cells, perfectly even grid, each complete composition centered with safe margins, no labels no lettering no UI. Cohesive painterly detailed fantasy illustration matching warm gold/emerald RPG ability icons, dark charcoal backgrounds. First row four square ability icons: fierce black panther portrait with emerald eyes (Prowler), thick brown bear portrait (Bulwark), gray rat portrait (Rat), hands cradling a luminous green healing leaf (Rejuvenation). Second row icons: thorny intertwined green vines (Bramble Wall), armored shoulder encased in living leaves (Living Armor), ancient tree golden roots in emerald glow (Nature's Persistence), luminous paw print with three animal spirits (Wild Instinct). Third row: three FULL HEAD centered animal portraits on atmospheric forest background, black panther face forward, brown bear face forward, gray rat face forward, suitable for circular character tokens with ears and entire heads safely inside circle; final cell luminous druid humanoid silhouette encircled by green leaves for return to humanoid icon. Consistent professionally painted game art, crisp silhouettes readable small, no walking animal sprites. Every asset confined to equal cell, no crossing boundaries.

### Ground props and nature effects

Transparent fantasy tactical game sprite atlas, exact evenly divided 4 columns x 2 rows, eight equal square cells, all images safely inside their cell with generous padding. PURE VERTICAL TOP DOWN ORTHOGRAPHIC view, no horizon, no isometric. Hand painted Fortcamp emerald green woodland magic with brown thorny woody stems, readable silhouettes. First four cells across top are four animation frames of the SAME compact dense bramble wall segment, square occupancy, horizontal tangled thorn roots and small leaves: frame1 restful, frame2 branches raised slightly, frame3 vine whip reaching upward in a curved lash, frame4 settling back. Bottom row: frame1 broken dead thorn roots wreckage, frame2 luminous swirling green leaves transformation ring with clear transparent center, frame3 emerald restorative leaf motes around transparent empty center, frame4 a single long curved thorn vine whip striking with leaf trail, isolated prop/effect only. No ground, no tiles, no soil backgrounds, no animals, no characters, no icons, no text, no grid lines. Maintain exact same wall size across top frames and painterly art consistent throughout. Preserve full transparency between and around every prop.

## Sound

Five ElevenLabs clips, generated with the existing configured tool and prompts in
`SFX_GENERATION_GUIDE.md`: `druid_prowler`, `druid_bulwark`, `druid_rat`,
`druid_growth`, `druid_vine_lash`. Runtime WAVs are in `assets/sfx/`; retained
sources/report in `staging-sfx/druid-nature-v1/`. 48 kHz mono with automated
nonempty/clipping checks. They use short animal/rustle/growth/whip accents rather
than competing background music. Preview: `/assets/sfx/preview-druid-nature-v1.html`.

Generation resumed after an upstream 500 on growth; three successful sources were
reused, and the failed request was reported uncharged. Runtime playback uses the
shared timeline, with lash audio at 220 ms contact and form/growth audio at effect
start. Human listening/style review is still needed; automated audio checks do
not establish that the clips sound good. Existing flesh/armor melee families
provide animal contact sounds for this pass.
