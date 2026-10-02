# Map Asset Layering

## October 2: Mission evidence, prison wagon and coverage audit

Added a fourth expansion pack with 12 sprites: intact/wrecked prison wagon, dispatch satchel, wagon wheel, marked farm chart, armed/spent spike traps, armed/spent iron-jaw traps, handcart, cold campfire and wooden table. The registry now installs 55 sprites. This supersedes the earlier 43-sprite count below. Exact built-in image_gen prompt/source are preserved in staging-terrain/overhead-props-v2/mission_objects_PROMPT.md and mission_objects_12.png. Reference roles and extraction method remain as documented below.

Fixed missing assignments in Captive Cart and Smoke over the Hedgerows; contract walls now use stone-wall art. map-object-art.js is the shared state resolver for preparation and active combat. New encounters declare mission-object sprite IDs explicitly; legacy encounters without them use stable object/kind fallbacks. Spent traps and broken prison wagons use their own images. Custom explicit art remains authoritative. No interaction, damage, collision, footprint or mission reward rules changed.

Build isolated current encounters with `.venv\Scripts\python.exe tools/build_prop_coverage_preview.py`, then run `node tools/audit_battle_prop_art.mjs`. This pass checked 65 encounter setups and 888 intact/destroyed/object/decorative references with no missing assignments or runtime files. Shallow water intentionally uses ground; the existing deep pit remains a terrain asset. This audits sampled generated maps and all current tactical contract definitions, not every possible random layout or unused art-library entry. The browser fixture at /staging-terrain/overhead-props-v2/encounter-preview.html has an encounter selector; tools/prop_coverage_browser_qa.mjs checks actual Captive Cart, investigation and defense rendering. All fixtures are isolated from saves.

## October 2: Installed overhead packs and alarm bell

The earlier pilot-only status below is historical. Dev now selects 43 versioned overhead sprites: seven retained from the approved pilot plus 36 from three new twelve-image packs. Nature includes the missing pine and thorny bramble, other trees/shrubs, stump, branches, stones, hay and paired barrels. Defenses include palisades/gates/breached art, platform, rescue cage states, barricade, stone wall/rubble and alarm bell states. Containers include crate, silver/gold chests, coffer, reliquary and lever states. Palisades still show some front surfaces; the pack is a consistent improvement, not a claim of perfectly vertical projection.

Runtime registry: frontend/src/map-prop-art.json, resolved by map-prop-art.js. Stable gameplay sprite IDs select props/overhead-v2 or structures/overhead-v2; original libraries remain untouched and cover unmapped art. Selected sprites use 100% sizing with preserved aspect ratio; footprints, collision, rotation, objectives and gameplay rules are unchanged. Reusing an existing sprite ID updates scenery in saved battles too. The old alarm_horn ID intentionally remains compatible with saves and commands, while current labels, logs and story text call it Alarm Bell. Active/disabled sprites replace the placeholder symbol; the disabled bell has a cut rope and fallen clapper.

Sources and exact built-in image_gen prompts are in staging-terrain/overhead-props-v2, with the approved pilot as the object-style reference and mega terrain v4 as the palette reference. Art is new generation, not modification. All originals and crops are retained; media remain ignored by Git and need separate backup. The tracked source/order selection is docs/art/overhead_prop_manifest.json.

Run `.venv\Scripts\python.exe tools/install_overhead_props.py` to recover silhouettes and audit/build the gallery. Add `--install` to write the validated versioned runtime assets and registry. All source packs are checked before runtime writes; ambiguous connected silhouettes reject extraction. This tool does not create new art, change gameplay data or edit legacy files. Selected crops are normalized to 384x384 with at least 32px transparent margins. Run tools/build_gear_battle_preview.py for an isolated current Warcamp preview and tools/installed_prop_browser_qa.mjs with the local fixture server/Chrome for gallery, asset loading and bell-state checks. These are development tools, not game launchers.

## October 2: Grounding and overhead study

Live renderer preserves image aspect ratio when enlarging one-cell structures and interactables: horizontal size plus automatic height replaces independent width/height stretching. Short silhouette shadows replace the longer floating-looking drop shadow; hover retains the outline without a large glow. Multi-cell footprints and rotation remain unchanged. No gameplay collision or map placement changes.

Generated a separate 12-object steep-overhead pilot using the painted terrain atlas as the sole style reference. Source, exact prompt, crops, comparison and real Warcamp toggle preview are in staging-terrain/overhead-props-v1. Existing art is preserved and the pilot does not automatically replace the live prop library. Crates/barrel/canopy/campfire show the overhead direction better; palisades still expose excessive front faces and need another pass. A global camera direction is not complete yet.

Build the study with `.venv\Scripts\python.exe tools/build_overhead_prop_preview.py`, then serve using `node tools/serve_board_preview.mjs`. Open http://127.0.0.1:8766/staging-terrain/overhead-props-v1/preview.html for Grass/Dirt/Stone comparisons or battle-preview.html for the actual Warcamp toggle. These are isolated development fixtures, not launchers. Crop extraction uses connected silhouettes and removes neighboring artwork; it recovered two nominal-grid cuts (tent and tree). Scattered fragments are retained only near their owning silhouette; merged or ambiguous sheets reject extraction for review. Complete source art must exist to recover it; cropped-away details cannot be invented. All twelve crops preserve transparency and natural proportions.

Fortcamp maps use three mutually exclusive runtime art layers.

## Terrain

Terrain is the ground itself. It includes grass, dirt, floors, water, pits, cliffs, slopes, stairs, ground transitions, and integrated surface rubble. Terrain controls movement cost and elevation and remains after movable or destructible entities are removed.

Runtime assets: `frontend/public/assets/combat-terrain/mega-terrain-tiles`

## Structures

Structures sit above terrain and own gameplay state. Walls, palisades, barricades, gates, doors, prison bars, prison-pen fences, pillars, archways, ladders, and watch platforms belong here. Structures may block movement or sight, receive attacks, carry HP and armor, open, close, become breached, or leave rubble when destroyed.

Runtime assets: `frontend/public/assets/combat-terrain/structures`

## Props

Props also sit above terrain but are independent objects rather than map boundaries. Trees, rocks, crates, barrels, carts, furniture, tents, traps, campfires, and similar clutter belong here. A prop may be decorative, portable, throwable, interactable, or blocking according to its game data.

Runtime assets: `frontend/public/assets/combat-terrain/props`

Stateful interactables use paired sprites at the same scale and orientation. Current pairs include bronze, silver, and gold treasure chests; an ancient reliquary; a military supply coffer; an arcane crystal; and a floor lever.

Rescue cages, prisoner stocks, sarcophagi, and ritual altars live in the structure layer because they occupy and block a map cell. The current prisoner-rescue objective uses the wooden rescue cage pair. Dead and unconscious units remain character tokens with state styling so their identity and portrait remain visible.

Large map entities remain single sprites. A `footprint: [width, height]` reserves every covered grid cell, while `rotation` accepts 0, 90, 180, or 270 degrees and swaps rectangular footprints when needed. The renderer spans the entity across the grid and rotates the art as one piece, avoiding seams from splitting a structure into separate images. Both cage types default to 2×2; sarcophagi and prisoner stocks default to 2×1. The warcamp prisoner cage currently demonstrates the system. Larger future maps can place 2×2 tents without constricting this encounter's established routes.

Each asset identifier belongs to exactly one runtime library. A source generation sheet may contain multiple families for visual consistency, but extraction must classify every exported file into one layer before it can be used by a map.

New generation packs keep terrain, props and structures separate. The first authored-location pass adds `props/location-v1` (12 work/grave/riverbank props) and `structures/location-v1` (8 shed-wall/door/yard-gate/corner pieces). Its bridges are floor cells across a continuous river; gates are attackable, operable terrain entities above the floor, never duplicated as tiles. Existing ground textures are reused. See docs/design/AUTHORED_BATTLE_LOCATIONS.md for scope and tools.

October 2: the Captive Cart's prison wagon artwork renders at twice its previous width and height, preserving aspect ratio. `art_scale: 2` enlarges its intact/wrecked sprite independently of collision footprint; the existing road and courier placement remain usable. Older saved `cart_body` objects receive the same visual scale without rewriting saves. Multi-cell painted art clears the legacy CSS wagon wheels so those circles cannot appear behind the enlarged sprite. Use Battle Lab to review the map at different zoom levels.
# October 2 follow-up — building alignment and bridge/armory libraries

`art_offset: [x,y]` shifts artwork by fractions of a cell without changing occupancy; perimeter straight walls, gates and broken walls share outward offsets, while corner pieces retain their anchor. `art_scale` supports shrinking as well as enlargement; lanterns use one-third scale and retain their aspect ratio. Offsets use world-grid axes, independently of sprite rotation.

The separate `bridge-v1` ground library contains 12 terrain textures. `props/armory-v1` contains eight transparent props; chapel assets are prepared for future locations. Installer: `tools/install_bridge_armory_art.py`. Terrain is cropped from a gapless equal-cell 4×3 atlas; props are recovered from 4×2 cell ownership and connected components. No structure sprites were added to the terrain pack, and existing libraries were not overwritten.
