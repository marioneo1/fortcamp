# Painted environmental effects v1

One new transparent 6-column × 4-row sheet was generated with the built-in image tool, using the painted interactable props and board icon sheet as style references. These are 24 separate static effects, not 24 frames of one animation. Code supplies drifting, rotation, pulsing and travel.

Source: `staging-ui/vfx-atlas-v1/environment_vfx_6x4.png` (1536 × 1024). Review: `staging-ui/vfx-atlas-v1/extracted_preview.jpg`. The exact prompt is preserved in [environment-vfx-v1-prompt.md](environment-vfx-v1-prompt.md).

Runtime: `frontend/public/assets/vfx/environment-v1/`. The manifest records stable filenames, original grid bounds, extracted dimensions, soft alpha and centered anchors. These generated media files remain local and are excluded from the public source repository.

| Background | Textures used |
| --- | --- |
| Great Beast Tide | Two depth layers of four distinct leaves, plus grass seeds/petals |
| Ashen Procession | Falling ash flake/cluster and fresh procedural gray/violet mist |
| Green Warhost | Rising green/orange embers and fresh procedural camp smoke |
| Arcane Convergence | Three deforming light currents, blue fireflies, violet glimmers and vapor; no large glyph stamps |
| Starfall | Alien haze/motes and an occasional fast light point with a tapered trailing streak |
| Weather previews | Falling rain streaks and two depth layers of drifting snow |
| Preserved for future use | Glyphs, painted mist/ribbons/comet, electric arc, violet impact, wind curl, gold dust |

`frontend/src/vfx-textures.js` is a shared lazy texture library. Each file is fetched once as needed; failed files are cached as unavailable. The board now uses PixiJS Particle Emitter with painted textures, independent particle lifetimes, gradual opacity envelopes and varied movement, size and rotation. Board rendering preserves each sprite's aspect ratio and places effects behind cards and controls. It does not stretch square images into long trails. The former canvas implementation is retained only as a fallback when WebGL/Pixi initialization fails.

Board presets cap live particles at 62 or fewer, with up to 60 draws per second on desktop and 30 on narrow screens for smoother motion. Rain caps at 80 and snow at 50. Arcane adds three lightweight mesh currents; Starfall adds one head/trail pair. The canvas retains a 1920-pixel width resolution limit. Pixi is a lazy separate bundle; no shared ticker or additional animation loop runs. Unchanged polls do not restart it. Unrelated tabs, battles and hidden pages stop it, and returning does not fast-forward the hidden interval. Reduced motion draws a seeded still composition. Weather presets are previewable and reusable; no battle weather selection or skill system is enabled by this pass.

To re-extract this approved source sheet, run `.venv\Scripts\python.exe tools\extract_environment_vfx.py` from the project root. This rebuilds this version's runtime files; it does not generate art. Extraction uses relative equal cells, then trims with padding while retaining faint alpha and disconnected sparks. It deliberately avoids solid thresholding or largest-island filtering, which would damage these effects. A different future sheet should receive a new pack/version rather than replacing these stable names.

## Particle authoring and preview

Configurations live in `frontend/src/particle-presets.js` and use the emitter's V3 behavior format directly. The older Pixi visual editor is not required. The official [emitter documentation](https://particle-emitter.pixijs.io/docs/) describes its lifecycle and behaviors. Versions are pinned to emitter 5.0.10 and compatible Pixi 7.4.3 modules. Core/display/sprite/extraction and lightweight mesh modules are bundled, rather than the entire Pixi application framework.

The first emitter pass reused the painted smoke/mist PNGs. Following visual feedback, `particle-textures.js` now makes four soft noise-based density textures and small light sources in code. These are new procedural source textures, not new AI-generated artwork. They are tinted, rotated, expanded and overlapped to form smoke/vapor without repeatedly displaying the same painted curl. The original sheet remains intact.

`particle-ribbons.js` uses [Pixi meshes](https://pixijs.download/v7.4.3/docs/PIXI.Mesh.html) to deform three feathered light currents across the actual viewport. Geometry changes with time; no large sigil image is slowly rotated. `particle-comets.js` launches a small bright head at roughly 1,000–1,800 pixels/second, with its separately positioned tapered trail behind the direction of travel. The tail dissipates after the head leaves; launches are sparse. This replaces the prior roughly four-second translation of a large painted comet.

Panel surfaces now allow restrained background motion through, while text/control layers stay above the canvas. The old small CSS particle/orbit/trail scene is hidden during regional backgrounds to avoid duplicated effects concentrated at the emblem. Particle visibility and density have increased across the viewport. Reduced motion freezes currents and particles and starts no shooting-star flights.

`WindBehavior` separates movement from rotation, so turning a leaf does not redirect it. It assigns random speed, sway phase, uniform size and rotation speed; smoke expands, sparks shrink, and all layers fade in/out. Rectangle spawn data uses the installed library's `w`/`h` fields. Relative texture widths are accounted for to avoid accidentally oversized particles. Every emitter has `autoUpdate: false`; the controller owns timing, suspension and cleanup.

Run `.venv\Scripts\python.exe tools\build_mission_board_preview.py`, then `node tools/serve_board_preview.mjs`. Open `http://127.0.0.1:8766/staging-ui/mission-board-v1/board-preview.html` and use the top **Local effects preview** selector, including rain/snow. Stop the server with Ctrl+C. The Python server command remains a compatibility wrapper for this same server. This is safe local fixture content, not the game backend. Vite resolves the npm imports; a plain static HTTP server is no longer sufficient.

Validation: 48 frontend tests and production build passed. Tests instantiate the actual emitter library to check finite positions and visible particles for every preset, plus lifecycle tests for lazy initialization, abandoned loads, disposal, fallback and reduced motion. Motion tests check deforming geometry and fast head/trail direction, clearance and launch gaps. Browser checks verify Pixi is actually active, all painted emitter textures load, the arcane scene has three currents and no large ornaments, Starfall actually launches its fast star, all five event backgrounds and both weather previews animate within their caps, reduced motion freezes the canvas, ordinary boards hide it, controls retain focus across polling and mobile layout does not overflow. Browser verification is separate from live Discord playtesting.
