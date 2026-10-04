# Player base construction — first pass

Implemented in dev October 4. Open **Base → Settlement → Floors, props & walls**.
Production was not deployed by this pass. This is player-owned camp decoration,
not the dev Battle Lab or a replacement for existing functional facilities.

## Workflow

Choose Floors & terrain, Props, Walls, Select / move, or Erase. Search filters
that layer's asset library. Drag an asset from the library into the map, or drag
on the map using the current brush. **Release inside the map to place it.**
Releasing outside the visible map viewport cancels the entire operation,
including a painted floor stroke or moving an existing object. Escape cancels
an active drag; otherwise it requests closing the editor. Losing window focus
also cancels the preview. Floor strokes interpolate skipped cells.

R rotates the brush, selected object, or object being dragged. It works with a
button, slider or closed dropdown focused; typing in text/number fields remains
normal. Arrow keys shift prop art 5% of a cell, Shift+Arrows shift it 1%, and Home
centers it. For walls, arrows choose the corresponding cell edge and Home chooses
center. Invalid boundary adjustments are rejected. Select / move allows dragging
an existing object, or editing its cell coordinates. Clicking empty ground
clears selection. Undo/redo buttons and Ctrl+Z/Ctrl+Shift+Z restore edits; a drag
or slider gesture is one undo entry. Zoom runs from 50% to 200% with scrolling.
The layout also displays on the normal settlement plan after saving/reloading.

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

Walls have named directional assets rather than a separate post setting:

- Full horizontal plain, left-post, right-post and both-post walls.
- Full vertical plain, top-post, bottom-post and both-post walls.
- Four corners, each with **two full-cell-length arms** along cell edges.
- Gates. T and + junctions have been removed from the active kit.
- Opposite facing variants of straight walls and gates, so future artwork can
  have its own front/shadow instead of being mirrored.
- Timber, rough stone, polished stone and iron placeholder materials.

`construction-wall-pieces.json` is the shared client/server definition of geometry,
explicit posts and clockwise successor assets. R changes facing within horizontal/vertical families and selects a mirrored
corner orientation;
new directional walls save rotation 0. Matching ports snap to exact half-cell
coordinates. Full segments are split into graph edges at midpoints, so T branches
and crosses connect correctly. Post assets retain their chosen end posts even
when another wall connects; plain assets have no automatic posts. Asset previews
show their actual placeholder geometry and posts. Arrows translate the entire
piece to the selected anchor; they do not shorten its arms or change its facing.

Old saved walls without a `piece` identifier remain readable and editable with
the original arm/rotation/post rules. They are not silently resized or deleted.
Choose a new wall asset in the inspector to replace a legacy piece. Half-arm
corners, half walls, T junctions and + junctions are no longer offered in the
library. Previously saved junctions still render and save, but their rotation
control is disabled; their definitions live in the legacy piece file. Boundary validation
applies to every new and legacy segment. Existing combat wall art is unchanged.

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
wall asset IDs/shapes/anchors/materials, unique safe object IDs, and camp bounds. Saves use
the player lock and a compare-and-swap against the original JSON state; revision
mismatches reject stale windows instead of replacing another edit or unrelated
player changes. Only construction layers are changed. Existing buildings, roster,
inventory, resources and production are preserved.

Client construction-geometry.js and construction-render.js are independent of
the dialog and usable by a later dev map editor. Backend construction.py reads
the shared directional piece definitions and owns validation; legacy arm rules
remain compatible. A later combat adapter must
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

## Responsiveness and validation

The committed SVG scene stays intact during pointer movement. A separate preview
layer updates at most once per animation frame and skips unchanged previews;
pointer events change local preview data without API calls or whole-plan cloning.
Undo snapshots and committing a draft occur on drop. Nudging/rotating a selected
prop or native wall replaces only that object's SVG, retaining the ground and
facilities. Legacy automatic-post walls need a scene redraw for neighbor caps.
Full redraws still occur when committing a placement, switching tools, restoring
history or saving. There is no permanent animation loop while idle.

Nine backend construction tests plus economy/onboarding regressions (26 checks)
pass, including native/legacy save round trips, bounds, unknown asset IDs and
player/server isolation. Seven geometry/render tests cover full-arm corners,
post orientation through a full rotation cycle, junction ports and nudges. All
151 frontend tests and the production build pass. Isolated browser QA covers
native palette drag, preview-only painting, outside-drop cancellation for paint,
props, movement and erase, dropdown-focus R, arrow positioning, rotation during
movement, undo/redo and save/reopen. At 1440/800/430px the dialog stays within the
viewport. During 80 pointer updates, a MutationObserver verified zero changes to
the committed scene. Selected-object nudging also retained the original ground
node. Desktop capture was visually inspected. This is a behavior/DOM check, not
a guarantee of frame rate on every device. Production and real player saves were
not used for these tests. No bitmap art was generated in this refinement.

## Simplified art plan (agreed; not generated yet)

The future kit excludes half walls, T junctions and + junctions: 24 selectable
variants from 9 original images per material. Originals are horizontal plain,
vertical plain, horizontal one-post, vertical one-post, horizontal both-post,
vertical both-post, corner, horizontal gate and vertical gate. Permitted mirrors
supply other facings, post positions and corners; horizontal artwork is never
rotated into vertical artwork. Full-length corner arms remain. R cycles through native horizontal and vertical variants (see the October 4 refinement below). A nine-original plain-wood atlas is now available in the
isolated debug Wall Kit Lab; permanent player art selection remains deferred.
See docs/art/CONSTRUCTION_PLAIN_WOOD_KIT.md for generation, mapping and validation. Rectangle fill/repeated-footprint
placement and separate Remove / Remove floors tools also remain pending from the
interaction discussion. No art was generated in this simplification.

## Debug wall artwork trial

Mission Board debug controls include Wall Kit Lab, an isolated sample layout.
A single dropdown switches all test walls between geometry placeholders and the
new painted plain-wood kit. It never saves to a camp and is denied in production
or without debug/admin access. Normal construction keeps its existing save UI
and has no trial dropdown. Canonical art reference:
[Plain wood trial](../art/CONSTRUCTION_PLAIN_WOOD_KIT.md).

## October 4 rotation and library refinement

R now cycles horizontal -> vertical -> opposite-facing horizontal ->
opposite-facing vertical, returning to the starting piece after four turns.
Each step selects its native source or a reflection; no H bitmap is quarter-turned
to make a V bitmap. This supersedes the earlier family-limited R behavior.
Facing duplicates no longer have separate library icons/options, and corners
have one rotatable entry. Direct horizontal/vertical choices and explicit
left/right/top/bottom post choices remain. All 24 saved variant IDs stay valid.
Center [Home] beside Rotate resets prop offsets to zero or wall anchor to center;
the Home hotkey does the same. Text/number editing retains its normal keys.

Rotating an edge-anchored wall carries its position clockwise: top -> right ->
bottom -> left. Center remains center. The library has 11 entries, representing
all 24 saved orientation/post variants without duplicate facing icons.

## October 4 position-aware construction rules

Placement and save validation use world-coordinate wall segments, independent of
which cell owns a wall. A bottom-edge horizontal wall in one cell and a top-edge
wall in the cell below occupy the same segment: the second placement is rejected.
Material, facing and posts do not permit duplicates. End-to-end connections and
perpendicular joins remain allowed; partially overlapping collinear segments do
not. Existing untouched conflicts in old saves are grandfathered by the save API;
new or moved conflicts are rejected. No player data is rewritten.

Props cannot overlap walls, including open gates and broken-wall objects. The
check uses the shifted, rotated prop image viewport (92% of its footprint), plus
0.08 cell clearance for wall thickness. This is a conservative rectangle, not
pixel-perfect silhouette detection: nudging a small prop away can make it fit.
The same rule applies when placing/moving either the wall or the prop. Floors
remain placeable under walls. Invalid placements show a reason and do not commit;
rotations, arrow adjustments and inspector edits respect the same checks.

Shared JavaScript/Python movement helpers distinguish walls crossing a cell's
interior from walls lying along its edges. Interior segments make that cell
unwalkable; edge segments only block crossing that edge. Full corners occupying
two boundaries leave the cell interior walkable. Open gates/broken walls permit
movement; reserved prop footprints block their cells. The base currently has no
walking-character simulation, so these helpers are tested foundations for a
future playable base/map adapter, not a new live base movement feature. Existing
combat continues using its existing edge-wall pathfinding.

Validation: 161 frontend tests, 15 construction backend tests and build pass.
Browser checks cover 11 library entries, native four-step R, rotating edge anchors,
Home/Center, a duplicate shared edge, a perpendicular connection, a rejected
prop and successful offset adjustment. The wall save check indexes half-cell
segments rather than comparing every pair of walls. Pointer error labels only
change when their message changes. No production deployment or real saves used.
