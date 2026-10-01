# Effekseer Goblin fire trial

This is an actual Effekseer WebGL/WASM effect in the Mission Board. It replaces the rejected Pixi flame meshes for Goblin events; Pixi still renders smoke, sparks and other regional effects. Reopening the Activity and triggering Green Warhost shows it immediately. Live Discord visual approval remains pending.

## Source and runtime

Authored project: `docs/art/effekseer/campfire.efkproj`. Three layers vary scale, growth, lifetime and emission for a short campfire. Warm runtime tint and normal alpha blending avoid the initial white additive pile-up. This uses a supplied flame texture, not a new AI-generated image. Texture: Effekseer 1.70e `Sample/01_Pierre01/Texture/Fire.png` (Pierre). The sample readme declares CC-0. Attribution: Effekseer Project and Pierre.

Runtime: `frontend/public/vendor/effekseer-1.70e/effekseer.js` and `.wasm`, pinned to upstream commit `e8c3ce076644789918695b0cba0031461c817890`. MIT license and hashes are alongside them. Script/WASM total about 1.4 MB uncompressed, fetched once on the first Goblin event. Compiled effect and texture: `frontend/public/assets/effekseer/campfire-v1/`. Exported media remains excluded from public Git; the source project, runtime code and rebuild tool are tracked.

The engine shares Pixi's canvas and WebGL context. Drawing after Pixi resets cached GL state and uses the existing board clock; no second canvas or animation loop. The approved direction is now a foreground blaze below the camera: three overlapping broad sources on desktop, two on narrow screens, with every root below the visible bottom. Only their upper tongues rise into view. Independent width/height scales, unequal seeded ages and gentle height changes prevent a regular fire border. The authored effect keeps flames broad as they rise and uses longer lives with a shorter final fade, so the cropped tips stay bright rather than becoming faint strands. Smoke and sparks emerge across the same unseen fire bed. Native emission is continuous: each layer emits indefinitely while individual particles keep their finite lives. This removes the synchronized gaps caused by restarting finite bursts. Handles restart only if unexpectedly lost. Allocation remains capped at 512 instances/quads. Reduced motion uses a seeded still; hidden pages and unrelated tabs/battles suspend the controller. Resizing reuses the context and immediately seeds the new composition. Failed initialization leaves smoke/sparks working. Abandoned loads are cancelled; cleanup is idempotent.

Foreground screenshots: `staging-ui/effekseer-fire-trial/foreground-blaze-desktop.png` and `foreground-blaze-mobile.png`. The prior project is preserved locally as `campfire-before-foreground.efkproj` in that staging folder. The binary URL includes a revision to avoid showing the cached small-fire export after reopening Discord.

## Rebuild and preview

Run `.venv\Scripts\python.exe tools/build_effekseer_campfire.py` from the project root. It uses the local portable 1.70e editor; on a new machine it downloads the official approximately 32 MB release into staging. It copies the tracked source and supplied texture, then exports with `-cui -in ... -e ...`. No BAT file or global installation is required. Optional `--editor` accepts an existing compatible executable.

Use the existing board preview: `.venv\Scripts\python.exe tools/build_mission_board_preview.py`, then `node tools/serve_board_preview.mjs`, and choose Goblin in the effects selector. The game uses the same renderer. Screenshots and measured browser results are in `staging-ui/effekseer-fire-trial`.

Latest validation: 59 frontend tests and production build passed. Actual browser checks confirm Effekseer is active, instances spawn, old flame meshes are absent, allocation stays bounded, reduced motion freezes its clock, event changes disable it, other themes animate and no script errors occur. A 90-frame headless software-WebGL comparison at 1440 x 1100 measured average JavaScript update/draw submission of 0.32 ms without fire and 0.64 ms with fire (p90 0.60 / 0.90 ms). This is CPU submission timing, not GPU frame time or a Discord FPS guarantee. Live Discord visual/performance approval remains separate.

Official references: https://github.com/effekseer/EffekseerForWebGL and https://effekseer.github.io/Helps/17x/Tool/en/ToolReference/index.html.
