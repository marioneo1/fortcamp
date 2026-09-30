# Painted environmental effects v1

One new transparent 6-column × 4-row sheet was generated with the built-in image tool, using the painted interactable props and board icon sheet as style references. These are 24 separate static effects, not 24 frames of one animation. Code supplies drifting, rotation, pulsing and travel.

Source: `staging-ui/vfx-atlas-v1/environment_vfx_6x4.png` (1536 × 1024). Review: `staging-ui/vfx-atlas-v1/extracted_preview.jpg`. The exact prompt is preserved in [environment-vfx-v1-prompt.md](environment-vfx-v1-prompt.md).

Runtime: `frontend/public/assets/vfx/environment-v1/`. The manifest records stable filenames, original grid bounds, extracted dimensions, soft alpha and centered anchors. These generated media files remain local and are excluded from the public source repository.

| Background | Textures used |
| --- | --- |
| Great Beast Tide | Four distinct leaves, grass seeds, petal, soft wind curl |
| Ashen Procession | Ash flake/cluster, gray and violet mist |
| Goblin Warpath | Green embers with occasional orange embers, faint gold dust |
| Arcane Convergence | Cyan/violet glyphs, arcane ribbon; small procedural motes remain |
| Starfall | Alien ribbon, drifting mote, occasional traveling comet |
| Reserved for future use | Electric arc, violet impact, snowflake, rain streaks |

`frontend/src/vfx-textures.js` is a shared lazy texture library. Each file is fetched once as needed; failed files are cached as unavailable and existing geometry provides a fallback. Board rendering preserves each sprite's aspect ratio and places effects behind cards and controls. It does not stretch square images into long trails.

Animation retains the existing 38-particle maximum, 24 draws per second and 1920-pixel width limit. Unchanged polls do not restart it. Unrelated tabs, battles and hidden pages stop it. Reduced motion draws a still composition, including textures when their asynchronous loading completes. No weather or skill system is enabled by this pass.

To re-extract this approved source sheet, run `.venv\Scripts\python.exe tools\extract_environment_vfx.py` from the project root. This rebuilds this version's runtime files; it does not generate art. Extraction uses relative equal cells, then trims with padding while retaining faint alpha and disconnected sparks. It deliberately avoids solid thresholding or largest-island filtering, which would damage these effects. A different future sheet should receive a new pack/version rather than replacing these stable names.

Validation: visually inspected sheet/crops and browser background; 38 frontend tests and production build passed. Browser checks verify all board textures load, all five backgrounds animate, reduced motion freezes the canvas, ordinary boards hide it, controls retain focus across polling and mobile layout does not overflow.
