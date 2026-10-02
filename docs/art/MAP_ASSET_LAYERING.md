# Map Asset Layering

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
