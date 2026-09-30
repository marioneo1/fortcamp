# Map Asset Layering

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
