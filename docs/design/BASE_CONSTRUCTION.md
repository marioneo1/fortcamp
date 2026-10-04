# Player base construction — first pass

Implemented in dev October 4. Open **Base → Settlement → Floors, props & walls**.
Production was not deployed by this pass. This is player-owned camp decoration,
not the dev Battle Lab or a replacement for existing functional facilities.

## Workflow

Choose Floors & terrain, Props, Walls, Select / move, or Erase. Search filters
the current asset library. Floors paint with click/drag, interpolating skipped
cells along a fast stroke. R rotates the brush or selected object. Select / move
allows dragging an object to a new cell, or editing its cell coordinates.
Clicking empty ground deselects it. Undo/redo buttons and Ctrl+Z/Ctrl+Shift+Z
restore edits. Slider gestures form one undo entry. Zoom runs from 50% to 200%;
the map scrolls within its viewport. The layout also displays on the normal
settlement plan after saving and reloading.

Changes stay in the local draft until **Save camp**. Closing an unsaved draft
uses the standard in-game confirmation. Export layout downloads only the camp
layout and size, not character data or credentials. Import and applying exported
layouts to combat maps are future work. Export is not a full-game save backup.

## Layers and geometry

One cell is one unit. Terrain/floors, props and walls are independent layers.
Ground is a cell-keyed asset/quarter-turn rotation map. Existing facilities are
shown as labeled footprints and retain their original management functions.
There are currently 112 installed ground textures and 124 supported props;
catalogue counts depend on locally installed artwork.

Props have stable IDs, cell coordinates, a 1–4-cell footprint on each axis,
quarter-turn rotation and independent horizontal/vertical offsets from -45% to
+45% of a cell. Rotation swaps a rectangular footprint's width/height. The SVG
image preserves source aspect ratio; resizing a footprint never stretches the
image. Offset changes the art position, not the reserved cells. Non-reserved
decorations can overlap for clutter. Reserve this footprint prevents placing a
future facility across it and cannot be enabled over an existing facility.
Reserved props do not currently define combat collision. Artwork shifted beyond
the map edge may be clipped in the normal camp view; keep edge decorations inside
the boundary when adjusting offsets.

Walls anchor at center, top, right, bottom or left of a cell. Snap chooses the
closest anchor to the pointer. Quarter-turn rotation changes the piece's arms
around that anchor. The wall tool includes:

- Full straight wall, half wall, corner, T, cross and gate.
- Timber, rough stone, polished stone and iron placeholder appearances.
- Automatic exposed-end posts, no posts, or manual piece-end posts.
- Open/closed gates and simple broken-center variations.

All connecting arms occupy exact half-cell segments. A top edge and the cell
above's bottom edge map to identical coordinates. Neighbor connections use
endpoint equality and deduplicated segments, not loosely matching sprite boxes.
Crossing full walls form a cross at their shared center. An additional branch
forms a T. Automatic posts appear at degree-one graph nodes only; they disappear
at joined ends. The line geometry renders continuous junctions with matching
thickness. Manual posts may deliberately remain at piece ends. Pieces are snapped
to a half-cell lattice, not arbitrarily shifted by pixels. Rotate a boundary piece
if its arms extend outside camp; server validation rejects out-of-bounds arms.

Gate openness and broken variants are stored and rendered, but they are not yet
doors operated by walking camp characters. The current camp has no walking actor
or raid simulation. Walls currently have no resource cost, HP or defense bonus.
Painted building artwork, economic costs, unlocks, construction time, damage and
functional camp pathfinding are separate follow-up passes. Chests, cages and other
decorations do not grant loot, capacity, prisoner slots or production. Functional
facilities still come from the existing Build menu.

## Persistence, ownership and reuse

state.construction is a versioned layout with a revision, ground map and object
lists. No SQL schema migration. GET/PUT /api/construction use authenticated player
and server identity; no target player/server can be supplied by the client.
PUT validates catalogue IDs, finite numbers, footprints, offsets, quarter turns,
wall shapes/anchors/materials, unique safe object IDs, and camp bounds. Saves use
the player lock and a compare-and-swap against the original JSON state; revision
mismatches reject stale windows instead of replacing another edit or unrelated
player changes. Only construction layers are changed. Existing buildings, roster,
inventory, resources and production are preserved.

Client construction-geometry.js and construction-render.js are independent of
the dialog and usable by a later dev map editor. Backend construction.py mirrors
the same coordinate/arm rules and owns validation. A later combat adapter must
translate wall segments and prop reservations into real movement/sight rules;
decoration data alone does not silently change combat maps. Existing authored
combat map generation and wall-boundary rules remain unchanged.

## Design references

[Godot terrain connection tools](https://docs.godotengine.org/en/4.5/tutorials/2d/using_tilemaps.html)
provide the neighbor-aware connection model. Fortcamp uses exact connection ports
rather than importing Godot or requiring its tile sets.
[Factorio blueprints](https://wiki.factorio.com/Blueprint) inform reusable layouts
and rotation; Fortcamp's layout export is a foundation, not yet blueprint import.
No new runtime library or generated bitmap assets were required.

## Validation

Eight backend construction tests cover layer data, edge-coordinate equivalence,
rotations, unknown assets/injected IDs/nonfinite inputs, bounds, reserved facility
footprints, real SQLite save/reload, revision conflicts, and player/server isolation.
With economy and onboarding regressions, 25 checks pass. Four geometry/render tests
cover exact joins, duplicate arms, snapping, proportional rotations and automatic
post removal. All 148 frontend tests pass. Isolated browser QA exercises actual
mouse placement, offsets, rotation, T joins, undo/redo, save/reopen and 1440/800/430px
dialog bounds. A desktop capture was visually inspected. Production build passes.
