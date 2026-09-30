# Painted Mission Board assets and preview

The live board uses the 24-icon `mission-board-v1` pack. Its approved source is `staging-ui/mission-board-v1/guild_icons_6x4.png`, a 1536 x 1024 transparent atlas. References were the existing combat UI art and painted interactable props; character portraits were not used. The built-in image generator created one new atlas.

Exact generation prompt: [icon atlas prompt](mission-board-icons-v1-prompt.md). Source art, extraction preview, and browser screenshots remain under `staging-ui/mission-board-v1`; they are local asset backups, not tracked public media.

## Extraction and stable names

Run the project Python with `tools/extract_mission_board_icons.py`. The tool measures actual canvas dimensions and divides into six columns and four rows. It preserves transparency, discards small disconnected border flecks, and normalizes each icon uniformly within a 256-square canvas. Neither axis is stretched independently. Default behavior re-extracts the same approved pack; a future replacement should use a new versioned source and runtime directory rather than overwrite this approved source.

Runtime PNGs and crop manifest are in `frontend/public/assets/mission-board-v1`. The order is six rank seals, eight form icons, five event emblems, and five utility icons. Rank letters are rendered by the app over empty seal centers. Icons are decorative alongside readable labels and do not replace accessible action names.

## Browser preview and verification

`tools/build_mission_board_preview.py` builds representative safe fixture content using the actual board renderers and styles, with normal/event boards, roles, private leads, active missions, stacks, and locked ranks. The preview is `staging-ui/mission-board-v1/board-preview.html`. Serve it locally with `node tools/serve_board_preview.mjs` (port 8766; loopback only); `tools/serve_board_preview.py` delegates to the same Vite server. Vite resolves the new Pixi imports. The top selector previews events and future rain/snow presets. This preview does not run the game backend or access player data.

`tools/board_browser_qa.mjs` is a maintainer check requiring a separate Chrome debugging session on port 9229 and the local preview server. It checks locked information, stable DOM/focus and collapse state during refreshes, filtering, private/public inspection, reduced motion, and narrow layout. It writes screenshots beside the preview. This is not an everyday game launcher.

## Runtime behavior

Contracts is the primary destination for Public Board and Private Contracts; the inner navigation also jumps to saved expeditions. Cards prioritize a short premise, known resolution/choice labels, duration, party size, recommendations, possible rewards, and requirements. Detailed contract inspection and party assignment use the existing planner. Locked rank details stay concealed; pure roll missions and hidden encounters are not relabeled as guaranteed combat.

Search/filter controls remain reachable on desktop; active chips can remove individual filters. Unchanged renders retain their existing DOM, focus, and open rank sections rather than reconstructing them every five seconds. Real updates restore focused contract actions where possible. Countdown targets update independently.

Regional palettes apply to the new cards and header. Seven small particles, a halo and optional arcane orbit provide bounded visual effects around the event emblem. The legacy full-screen dotted overlay has been retired. Reduced motion disables ornament animation, and hidden-page state pauses it. No additional audio or paid generation occurs when switching views.


## Full-board regional backgrounds

Following clarification that effects should fill the background rather than only surround the emblem, `frontend/src/board-vfx.js` now renders a dedicated noninteractive canvas behind the public/private board. The backdrop uses irregularly positioned rising goblin motes, falling ash and mist, arcane rings/pulses, rotating windblown leaf silhouettes, and alien light fields/trails. Cards and controls stay in a higher layer. There is no repeating particle wallpaper.

The canvas renders at most 24 times per second, caps its width resolution at 1920 pixels and particle count at 38, and keeps animation state across unchanged polls. It stops on unrelated tabs, actual battle views, general events and hidden pages. Reduced motion uses a static frame and starts no animation loop. Event banners also have a more visible right-side scene and stronger emblem accents. No further image/audio generation was needed for these procedural effects.

Browser verification compares canvas pixels across time for every event, checks a static frame under reduced motion, and checks that the ordinary board hides the canvas. Unit tests verify frame scheduling, polling stability, suspension, event disablement, and motion-preference changes. All 36 frontend tests and the production build passed.

## Painted texture follow-up

The procedural pass above is preserved as history. The board now draws extracted painted leaves, ash, mist, embers, glyphs and alien light from the new shared effects pack. See [Painted environmental effects](ENVIRONMENT_VFX_ASSETS.md) for source, stable filenames, extraction and future reuse. All 38 frontend tests, production build and browser checks passed.
