# Reusable building templates — implemented in dev

Building plans are separate from battlefield plans. `backend/building_templates.py` defines local rooms, doors, breaches, dividers, furniture, courtyard paving and enemy spawn candidates. `place_building(template_id, anchor, instance_id, rotation)` in `backend/location_maps.py` places a complete instance at any map anchor, with 0/90/180/270-degree rotation. It returns a fragment; it does not own mission rewards, enemy budgets, exits or victory conditions. Distinct instance prefixes prevent ID collisions when a future map places multiple buildings.

Rectangular room footprints form a union. Overlapping rooms lose shared internal walls; exposed edges select straight or convex corner pieces, and inward bends get concave joins. Explicit doors and breaches replace wall cells. Furniture and spawn candidates follow the same transform as the shell. Map dimensions accommodate the selected footprint rather than squeezing every building into the old rectangle. Ground is painted only under the building and its defined yard, preserving the outline.

## Current plans

| Mission | Building | Difference in layout |
| --- | --- | --- |
| The Locked Tool Shed | Long tool store | Wide single-room store, front door and rear breach. |
| The Locked Tool Shed | Divided tool house | Square store with internal divider, operable connecting door and rear breach. |
| The Locked Tool Shed | Side annex and yard | Joined L-shaped footprint with an outdoor carpenter work area. |
| The Locked Tool Shed | Twin sheds and loading court | Two independent sheds, multiple doors and a central/loading court. |
| Intruders at the Workshop | Enclosed forge yard | Broad stone perimeter and workshop gate, forge and repair bays. |
| Intruders at the Workshop | Courtyard pair | Independent north/south workshops facing a usable working courtyard. |
| Intruders at the Workshop | L-shaped forge | Joined forge and repair wing with two approaches and an outdoor work yard. |
| Intruders at the Workshop | Partitioned repair hall | Long hall, internal divider/door, front gate and rear delivery door. |

These eight footprints are distinct even under reflection and rotation. Flipping a building does not count as another plan. `backend/location_templates.py` selects a building and map anchor; the seed also varies its anchor slightly. Battle Lab exposes all four plans for each mission using seeds verified against the real generator. Original v2 maps are preserved in `docs/maps/archive/building_locations_v2.json`; older snapshots and art remain available. Active saved battles retain their map geometry.

## Coordinated structural art

Current runtime library: `frontend/public/assets/combat-terrain/structures/building-v2`. Four separate material atlases now contain 16 parts each: timber, rough fieldstone, polished limestone and iron. Walls, junctions, doors and gates for each material were generated together. Exact prompts/source sheets and extraction report are in `staging-terrain/building-toolset-v2`; old mixed-material `building-toolset-v1` sources and runtime files are preserved as legacy.

Install with `.venv\Scripts\python.exe tools\install_material_building_toolsets.py`. Complete silhouettes are recovered without stretching; open/closed doors share anchors and scale. `backend/building_art_geometry.json` calibrates corners and T-junctions. The old installer delegates to these packs when available. Generated media remain local and need separate backup.

## Wall occupancy and divider joins

New perimeter walls and corners leave their interior floor tile walkable and block crossing their outside edges. Centered dividers occupy the whole tile. The divided tool house and repair hall use T-junctions to connect their dividers to the shell. Gates, enemy routing and attack sight lines obey the same boundaries. Legacy saved geometry keeps its old collision behavior. See [Wall boundaries](WALL_BOUNDARIES.md) for exact rules and validation.

## Validation and remaining work

323 backend tests and 103 frontend tests pass; frontend build and browser checks pass. Forty seeds per location validate clear, unique spawns and actual movement routes through opened doors to exits. Building tests cover shell coverage, T connections, four distinct footprints per mission, independent instances and rotation. Art coverage: 83 encounters, 2,169 references, no missing files.

Further work: more map settings using these pieces; chapel/fort/prison-specific plans and stair destinations; richer courtyard dressing and player balance review. Production and live saves were not modified.
