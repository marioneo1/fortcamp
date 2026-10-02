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

Runtime library: `frontend/public/assets/combat-terrain/structures/building-v1`. Four material families: timber, rough fieldstone, dressed limestone for castles/chapels, and iron prison/security structures. Each has straight wall, corner, junction, terminal wall, breach, small door closed/open, gate closed/open and stairs: 40 pieces total.

Sources and complete prompts: `staging-terrain/building-toolset-v1`:

- `rustic_structures_20.png` and `RUSTIC_PROMPT.md`: matching timber and fieldstone parts.
- `civic_structures_20.png` and `CIVIC_PROMPT.md`: matching dressed stone and iron parts.
- `overhead_doors_gates_16.png` and `DOORS_PROMPT.md`: replacement paired doors/gates viewed from above. Frontal door drafts in the two initial sheets are not installed.
- `extraction.json`: source ownership, recovered bounds and shared door anchors.

Built-in image generation was used. These packs contain structures only; terrain textures and furniture props remain separate. Fieldstone walls and corners now come from the same sheet. Door/gate leaves use a separate coordinated overhead sheet to avoid the frontal doors in the draft. Stairs, junction/end pieces and castle/prison families are prepared tools; this pass does not add dungeon floors or stair interactions.

Install with `.venv\Scripts\python.exe tools\install_building_toolset.py`. The installer groups connected silhouettes by cell ownership and recovers complete bounds, including details extending beyond a nominal cell. It preserves aspect ratio and keeps paired door-post anchors/scale stable. Corner-arm measurements produce `backend/building_art_geometry.json`; walls and breaches use those family offsets so they meet the corners. Stable old sprite IDs point to the new matching families. Older pack installers preserve these overrides rather than reverting them. Source art is excluded from the public code repository and must remain locally available for reinstalling.

## Validation and remaining work

318 backend tests and 103 frontend tests pass; frontend build passes. Forty seeds per location validate clear, unique spawns and routes through doors to exits. Building tests cover all outer wall cells, intended openings, four unique footprints, independent instances and rotation of shell/furniture/spawns. Browser previews cover all eight plans plus other authored locations, actual sprite files and applied offsets. Coverage audit: 83 encounters, 2,169 references, no missing art.

Further work: more map-level settings using these building pieces; chapel/fort/prison-specific plans and stair destinations; richer courtyard dressing and map-by-map player balance review. Production and player saves were not modified.
