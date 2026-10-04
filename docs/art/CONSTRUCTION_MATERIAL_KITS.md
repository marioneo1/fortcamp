# Construction material kits — dev comparison

Implemented October 4, 2026. Open **Mission Board → Debug controls → Wall Kit
Lab** and switch **Debug wall kit**. The approved wood remains; six new kits are
available: Rough stone, Castle masonry, Church masonry, Iron fortifications,
Goblin camp and Raider camp.

Each has nine originals generated together in an equal 3×3 transparent atlas.
Horizontal/vertical art stays separate; mirrors supply 24 variants behind 11
library entries. No T/+ junctions or half walls. All materials use the same
ports, snapping, duplicate checks and prop clearance. Art never defines collision.

| Kit ID | Appearance | Runtime directory under combat-terrain |
|---|---|---|
| rough_stone_v1 | Weathered gray fieldstone, moss, timber gates | construction/rough-stone-v1 |
| castle_v1 | Cool dressed granite, oak and iron fittings | construction/castle-v1 |
| church_v1 | Ivory limestone, blue-gray bands, bronze fittings | construction/church-v1 |
| metal_v1 | Riveted dark iron, subdued bronze seams | construction/metal-v1 |
| goblin_camp_v1 | Olive-brown timber, rope, worn red ties | construction/goblin-camp-v1 |
| raider_camp_v1 | Brown timber, salvaged iron, burgundy bindings | construction/raider-camp-v1 |

These are intact-wall/closed-gate comparison kits. The dropdown remains debug-only
and cannot save. Normal construction retains its placeholder materials. Existing
combat art/maps are not replaced. Permanent material selection, open/broken
artwork, costs and map adoption remain separate work.

## Source and installation

The built-in imagegen tool made six new sheets using approved wood as the style
reference and its nine-piece diagram as geometry. No API key/new launcher needed.
`staging-terrain/construction-kits-v1/<kit_id>/` contains the unchanged `atlas.png`,
exact `GENERATION_PROMPT.md`, untouched `original-cells/`, measured
`installation.json` and actual browser `connected-room.png`.
The parent folder's `material-comparison.png` compares all six rooms.

Crop boundaries use thirds of actual dimensions (these sheets are 1254×1254),
not the requested output size. Rebuild, for example:

```powershell
.venv\Scripts\python.exe tools/install_construction_wall_kit.py --kit rough_stone_v1 --name "Rough stone" --atlas staging-terrain/construction-kits-v1/rough_stone_v1/atlas.png
```

The installer preserves other manifest entries and existing combat directories.
It removes small disconnected fragments touching crop boundaries only below
10% of the primary silhouette, handling neighboring art leaking across a grid
boundary. Source cells remain unchanged and removed regions are logged.

New canvases are 576px square, with the same 416px connection span and approximately
64px beam thickness as wood. Extra transparent margin accommodates posts/gates
without clipping or shrinking their in-game length. Middle bands are fitted while
retaining authored ends and joints. Normalization does not guarantee identical
texture details; seams and painterly differences remain subject to visual review.

`frontend/src/construction-wall-art.json` records native origins, spans and canvas
sizes. Future kits use this nine-source contract and installer without changing
snapping logic. Generated media stays local under existing Git exclusions.

## Validation

168 frontend tests, 18 construction/extraction backend tests and build pass.
Browser checks cover Delete/tool keys, wheel zoom, optional snapping, automatic
corner placement on a raised row, R retaining joins, text editing, prior collision
controls, seven painted kits, 63 native images, 44 walls per switch, no save writes
and dialog bounds at 1600/800/430px. Six connected-room captures were inspected.
Production and real player saves were not used.


## Drag controls follow-up

All seven kits share the same geometry-based rectangular floor fill, straight
wall runs and layer-specific Remove controls. Corner runs use one corner followed
by native plain H/V pieces; no atlas changes or bitmap quarter-turns are needed.
Rotated snapped previews retain their placement on click. See
[Base construction](../design/BASE_CONSTRUCTION.md) for controls and limitations.
