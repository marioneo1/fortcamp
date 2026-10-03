# Overhead garden props and crop edging

Implemented in dev, October 3, across all four herb-garden and training-yard layouts, plus suitable reuse in farm, well, supply and camp sites. New battles receive it;
saved encounters keep their existing furniture and scenery.

## Art pack

Built-in imagegen created a new transparent **6x4 prop-only atlas** at
1536x1024. The approved camp atlas supplied the painted style; the new ground
atlas supplied palette context. The prompt specified a strict overhead camera,
equal square cells and separated complete silhouettes. Ground and furniture
were not combined in the atlas. Source and exact prompt:
`staging-terrain/garden-toolkit-v2/garden_toolkit_24.png` and `PROMPT.md`.

The 24 source props include full/half/damaged rails, a corner, T and cross
junction, end post, closed/open gate, scarecrow, hand pump, round stool/table,
potting bench, watering can, wheelbarrow, tool crate, soil sack, clay pots,
seedling tray, herb basket, compost bin, drying screen and hose coil.

The importer preserves complete silhouettes, including detached pots and open
gate parts, by grouping connected alpha components around their cell centres.
It removes neighboring components instead of cutting blindly along grid lines.
Transparent crops are proportionally fitted into 384x384 canvases; the two-cell workbench, wheelbarrow and drying screen use 384x192 canvases so their square transparent padding does not shrink them inside a wide footprint. The source
is retained. `extraction.json` records complete source bounds; the gallery is
`staging-terrain/garden-toolkit-v2/extracted-gallery.jpg`.

A 25th runtime sprite takes the middle painted rail from the full fence and
normalizes it to a continuous one-cell-long, thin overhead strip. The complete
original full fence remains available. Removing terminal posts from connected
rails avoids doubled posts at every join. Runtime is
`frontend/public/assets/combat-terrain/props/garden-toolkit-v2`; stable IDs use
`horticulture_`, distinct from the rejected user atlas's retired IDs.

## Placement and gameplay

Garden planting patches have low timber edging overlaid above ground art.
Rails sit at half-cell offsets on the crop boundaries, rotate for vertical
edges, and meet under small circular corner stakes. They are **step-over crop
borders**, not walls or interactive gates: movement and sight are unchanged.
Their decorative anchors do not remove otherwise clear enemy deployment cells.
This pass uses the joined rail and end-post art for rectangular borders. Native
corner/T/cross and gate sprites are retained for future layouts; no new gate
operation, breakable fencing or fence construction mechanics are claimed.

The garden now has a two-cell potting bench, adjacent small stool, tools and
spare pots; a compact hand pump beside water storage and a watering can; a
scarecrow among herbs; compost, soil and a two-cell herb drying screen along the
south edge; and a round rest table with a stool and cut-herb basket. A two-cell
wheelbarrow sits outside the entrance. Placement offsets remain visual;
collision follows each solid object's complete footprint. Small tools/pots use
smaller calibrated silhouettes than the tables and benches.

The training yard receives equipment-repair tools, spare target straw, water and
a rest stool in its existing equipment corner. Its sparring court and archery
lanes remain open. Approved walls retain their existing connection geometry. All four activity layouts now use the kit, with distinct arrangements for each footprint.

## Tool

From the dev project:

```powershell
.venv\Scripts\python.exe tools/install_garden_toolkit.py
.venv\Scripts\python.exe tools/audit_prop_sizes.py --write-profiles
```

The installer rebuilds only this kit's sprites/registry entries from its retained
source. The audit refreshes shared size profiles and their frontend mirror.
Neither changes saves or reinstalls the rejected atlas. Review through fresh
Battle Lab layouts 1?4 of Herbs Behind the Wall or A Promise Proven in Battle;
actual-render screenshots use the existing `--activity-sites` review command.

## Validation

Nine backend prop/beginner tests pass, including 400-map reachability, unique
crop-stake identities and walking across low crop borders. The frontend build
passes. Browser checks cover eight activity layouts, 28 beginner layouts and
20 command/camp layouts, with no runtime exceptions or missing loaded assets.
All six newly dressed activity variations and representative farm, well and camp
renders were visually inspected. Full coverage checks 249 encounters and 20,330
prop references with no missing art. Shared profiles cover 131 non-modular sprites.
Production and player saves were untouched.

## Current variation rollout

| Layout | Herb garden | Training yard |
| --- | --- | --- |
| 1 | Approved cross-path and four plots; potting, watering, drying and rest corners | Approved sparring court and two archery lanes |
| 2 | Broad northern plots; compost/drying and a sheltered rest area in the annex | Compact sparring court, long side range and annex equipment/rest corner |
| 3 | Nursery and flowering plots separated by the existing divider; gate approach clear | Separate sparring and archery courts with their own equipment stations |
| 4 | Long western plot, northern flowers and a southern wash court; side-gate route clear | Deep sparring court, eastern archery lanes and southern equipment/rest area |

The new crops and borders follow each building footprint; these are distinct
compositions, not rotations of the first layout. Reuse adds a scarecrow/tools
and water can to farm clearings, a hand pump/pots/can to old village well yards,
repair tools beside provision/supply stores, and herbs/stools/tools/water cans
around camp cooking, repair and water stations. Camp placement retains reserved
spawn lanes, door staging cells and complete footprints. This affects 36 authored
layout variants across nine settings. No new farming, pump or training mechanics
are implied. Saved battles retain their existing scenery.
