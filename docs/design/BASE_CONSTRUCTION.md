# Player base construction — first pass

Implemented in dev October 4. Open **Base → Settlement → Floors, props & walls**.
Production was not deployed by this pass. This is player-owned camp decoration,
not the dev Battle Lab or a replacement for existing functional facilities.

## Workflow

Choose Floors & terrain, Props, Walls, Select / move, or Remove. Search filters
that layer's asset library. Drag an asset from the library into the map, or drag
on the map using the current brush. **Release inside the map to place it.**
Releasing outside the visible map viewport cancels the entire operation,
including a painted floor stroke or moving an existing object. Escape cancels
an active drag; otherwise it requests closing the editor. Losing window focus
also cancels the preview. Floors fill the rectangle between the first and last
cells; walls extend a single row or column. See the drag refinement below.

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
quarter-turn rotation and independent horizontal/vertical offsets from -50% to
+50% of a cell. Rotation swaps a rectangular footprint's width/height. The SVG
image preserves source aspect ratio; resizing a footprint never stretches the
image. Offset changes the art position, not the reserved cells. Non-reserved
decorations can share cells when their visible bounds fit. Reserve this footprint prevents placing a
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
See docs/art/CONSTRUCTION_PLAIN_WOOD_KIT.md for generation, mapping and validation.
Rectangle floor fill and separate layer removal are implemented below; repeated
prop placement remains deferred. No art was generated in this simplification.

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
check uses the visible artwork bounds inside its aspect-preserving image viewport,
including footprint size, rotation and offsets, plus 0.08 cell wall clearance.
Transparent padding no longer reserves space. This is a conservative silhouette
bounding rectangle, not pixel-perfect detection; narrow gaps inside artwork
still count as occupied. Unknown artwork falls back to its image viewport.
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


## October 4 hotkeys, wheel zoom and optional snapping

| Key / gesture | Action |
|---|---|
| F / P / W / V | Floors / Props / Walls / Select and move |
| Delete | Switch to Remove; does not immediately delete an object |
| Shift held before a Remove drag | Remove floors as a rectangle, preserving props/walls |
| S | Toggle wall snapping; preference saved in this browser |
| R | Rotate; while snapped, keep joins and skip rotations that cannot fit |
| Arrows / Shift+arrows | Position / fine prop positioning |
| Home | Center the prop or wall |
| Wheel over map | Smooth zoom, 25-300%, keeping the cursor point when scroll bounds allow |
| Shift+wheel | Ordinary scrolling |
| Ctrl+Z / Ctrl+Shift+Z | Undo / redo |

Text/number inputs keep normal typing/Delete behavior. Ctrl/Meta wheel gestures
stay available; library/inspector scrolling does not zoom. Zoom buttons remain.

Snapping defaults on and searches nearby exact endpoint connections, checking
bounds, duplicate spans and prop overlap. Corners can change facing and anchor,
preferring connections at the bend. Straight/gate brushes retain their chosen
horizontal/vertical family until R. Green dots mark connections and a status
line confirms the join. R considers the other native orientations and nearby
positions to preserve all existing endpoint contacts. If none fit it leaves the
piece unchanged and explains that S permits free rotation. Distant walls cannot
attract the brush. Turn S off for fully manual positioning/rotation.

Snapping uses nearby world geometry, independent of artwork or material. It
changes only previews/local drafts; existing server validation remains. No new
network calls occur on pointer movement or zoom. Six new kits use the same
nine-original contract: see ../art/CONSTRUCTION_MATERIAL_KITS.md.

Validation: 168 frontend tests, 18 construction/extraction backend tests, build
and browser controls/material checks pass. Seven painted kits switch 44 sample
walls and load all 63 native sprites. Room captures visually inspected. Production
and real player saves untouched. Base character walking remains deferred.


## October 4: construction drag and removal refinement

Clicking a rotated snapped corner now commits the exact hovered orientation and
anchor. Starting a drag snapshots that preview instead of clearing its rotation
choice and snapping again.

Floors preview an inclusive rectangle between the start and current cells. Moving
back toward the start shrinks it; skipped cells are filled automatically. Walls
preview one row or column along the dominant drag direction, never a room fill.
Straight walls select matching native H/V artwork. A corner appears once at the
start, followed by plain walls extending its appropriate arm. All pieces retain
the material and facing. Some offset corner arms cannot extend with the current
five anchors: the UI asks to center the corner. Invalid runs place nothing.

Remove [Del] targets only props/walls under the pointer. Hold Shift before starting
a drag to remove a floor rectangle instead; its layer stays fixed until release.
Hover enlarges an object by 10%, dims its original and adds a warm red outline;
floors receive cell outlines. This identifies the layer without removing it early.

Every drag stays in the preview layer until release inside the map. Release
outside cancels the entire operation. Each completed drag is one undo entry.
Library-to-map dragging follows the same rules, starting at the first entered
map cell. Pointer updates do not write saves or rebuild the committed scene.

Validation: 173 frontend tests and production build pass. Isolated browser checks
cover rectangular fill/shrinking, straight runs, rotated corner commit, invalid
run rejection, layer-specific removal over shared cells, magnification, undo,
palette dragging and outside cancellations. Saves used an in-memory fixture;
production and real player data were untouched. No artwork changed.


## October 4: props sharing wall cells and default wall anchors

Wall ownership of a cell does not reserve its interior. Collision now measures
visible artwork (alpha at least 32/255) after the same aspect-preserving sizing,
rotation and offset as the renderer. A small prop can fit inside top/bottom/side
walls; larger props still cannot cross a wall. Frontend previews and backend save
validation share construction-prop-bounds.json. Existing placements and artwork
are unchanged. Wall clearance remains 0.08 cell. Bounds are conservative boxes:
transparent holes inside a silhouette are not usable gaps.

New horizontal brushes default to the top edge; native vertical brushes default
to the left edge. Corners default to center so their full arms follow cell edges.
Choosing another piece resets its default anchor; arrows/Home and smart snapping
can still change it. Existing saved wall positions are preserved.

Rebuild measurements after replacing/adding artwork with:
`.venv\Scripts\python.exe tools\measure_construction_props.py`.
The tool reads sources without modifying them; unmeasured assets use the previous
viewport fallback. 237 existing sprites measured. Validation: 175 frontend tests,
16 backend construction tests and build pass, including three-sided enclosure,
center collision, shifted collisions, multicell size and rotated art bounds.
Production and player saves were not changed.


## October 4: shared-cell furniture and seat docking

Props do not reserve an entire cell for placement. Their measured, shifted,
rotated artwork boxes are checked against other props. Separate silhouettes can
share one cell; overlapping boxes reject new placements/moves. Bounds remain
conservative: transparent gaps inside the silhouette are not detected. Unchanged
old overlaps remain saveable, but moving either object rechecks the pair.

Tables and seats have an explicit, editable exception in construction-furniture.json.
Supported tables: wooden table, round garden table and food-prep table. Supported
seats: round garden stool and mess bench. Up to 30% of the seat's visible box may
tuck under a table; full overlap is rejected. Table art draws after seats regardless
of placement order. Nearby seats dock at one of four table sides within 0.3 cell,
using the existing optional Snapping [S] control. Preview shows the tabletop over
the tucked seat. Other props do not snap to tables. Arrows/Shift+arrows provide
manual positioning; turn off S to prevent automatic docking while dragging.

Both the frontend and save API enforce these rules. The backend sweeps horizontal
bounds to avoid testing distant prop pairs. No source artwork, player saves or
production files changed. Validation: 178 frontend tests, 18 backend construction
tests, build and real browser seat-preview/drop/save/draw-order QA pass. Browser
saves were an in-memory fixture. Pixel-perfect silhouette collision and additional
furniture pairing rules remain deferred.


## October 4: calibrated prop audit and placement outlines

Construction now has its own audited size profiles in construction-prop-sizing.json.
The previous generic 92% image viewport was inconsistent: transparent margins
made furniture too small while charts and small clutter used furniture-sized boxes.
All 142 installed construction props have measured art bounds and calibrated fill.
Visible silhouettes are centered, sized by object category, and keep their source
aspect ratio. Chart 0.30 cell, lantern 0.25, ordinary containers about 0.75, chairs
0.50, stools 0.35. Large wells/cages/wagons/tents default 2x2; beds 1x2; workbenches,
pews and benches 2x1. This supersedes the earlier generic viewport sizing above.

Saved coordinates and footprints are not rewritten. Select an existing prop and
use Standard size to adopt the current default dimensions while retaining its
position/rotation; collision validation and undo still apply. Offsets now cover
-50% to +50% so docking has no gap between adjacent cells' supported positions.

Placement boxes are enabled by default in the editor, with a browser-persistent
checkbox. They tightly bound the visible alpha rectangle after sizing, rotation
and offsets, ignoring transparent image margins. Wall boxes show the existing
0.08-cell placement clearance around segments. Invalid prop previews remain visible
with red outlines and cannot commit. Boxes are noninteractive and do not appear
in the normal settlement view. They do not change character pathfinding, combat
movement, or the existing independent Reserve this footprint setting. Empty gaps
inside a silhouette's rectangle remain conservative occupied space.

Prop selection uses these tight rectangles as well, so transparent PNG margins
do not intercept neighboring objects. Painted walls use a narrow segment hit
area rather than their square bitmap canvas. Faint alpha outside the measured
silhouette is ignored for placement. These are editor hit areas, not gameplay
movement collision shapes.

A new 6x4 atlas supplies 24 overhead furniture/training props, including eight
chairs, three stools, a bench, six replacement training sprites and six new props.
All seats use the existing optional S table docking and tabletop draw priority.
Old sources remain. Combat replacement art resolves through the same stable IDs;
existing battle footprints and logic remain unchanged. Battle sprite calibration
is refreshed for the replacement images, separately from construction geometry.

Audit: docs/art/CONSTRUCTION_PROP_SIZE_AUDIT.md; six galleries and JSON under
staging-terrain/construction-prop-audit. Rebuild with:
`.venv\Scripts\python.exe tools\measure_construction_props.py`
then `.venv\Scripts\python.exe -m tools.audit_construction_props`.
New-pack source/prompt/extraction log: staging-terrain/furniture-training-v1.

Validation: 181 frontend tests, 24 backend construction/shared-size tests, build
and isolated browser checks pass. Browser verifies calibrated chart/chair/well
sizes, prop/wall boxes and toggle, red invalid preview/no commit, Standard size,
save and table docking/occlusion. Screenshots inspected. Saves were in-memory
fixtures; production and real player saves are untouched.

### Adjustable table spacing — October 4

Select a supported chair/seat and adjust **Table spacing**: left tucks it under
the tabletop, right pulls it away. Range: 60% tuck through a gap of 60% of the
seat's size along that side; default docking retains its 20% tuck. Adjustment
keeps the nearby table and current side, transferring position between cells
when needed. The preference saves per seat. Ordinary offset controls remain.
Walls, other props and map edges still constrain placement. Table art draws
above the seat; shared overlap allowance is 65% for rounding tolerance, and
fully enclosed seats are rejected.

Prop picking uses calibrated bounds in draw order, avoiding transparent table
margins intercepting visible chairs. Inspector edits resolve the current object
after Save, so repeated adjustments continue to persist.

Validation: 182 frontend tests, 25 backend construction/shared-size tests, build
and isolated browser checks: exposed-chair selection, deep tuck, pull-out, same
side, repeated saves and reopen persistence. In-memory saves only; prod untouched.

Deferred: full map audit using this calibrated toolkit. Review active locations
and variations for scale, clutter, wall connections, appropriate layouts,
objectives and traversable routes. Automatic base-to-map export is separate work.
