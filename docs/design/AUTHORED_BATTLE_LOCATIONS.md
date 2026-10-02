# Authored battle locations — first focused pass

Implemented in dev, October 2. The first pass fixes six missions using shared location pieces and separate art libraries. Other missions retain their current layouts for later review; this is not a complete map redesign.

| Mission | Location and tactical identity |
| --- | --- |
| The Locked Tool Shed | Plank-floored, roofless shed with continuous timber walls, an operable door, tools, workbench, sawhorse, stored boards and a collapsed southern wall section as an alternative entrance. |
| Intruders at the Workshop | Cobbled repair enclosure with stone boundary, iron gate, forge/anvil bay, repair benches, loose wheel and handcart. Withdrawal uses the entrance or a breached wall, not an exit through an intact perimeter. |
| Bone Collectors | Shaded cemetery with grave rows, headstones, crosses, fallen markers, disturbed bones, an old paved path, dead trees and a broken boundary wall. |
| Bone Patrol | The same cemetery-road vocabulary, with a worn dirt patrol track through the paving. |
| Timber Across the Creek | Continuous deep river, damaged plank bridge with one remaining crossing lane, near-bank timber, far-bank planks and repair sawhorse. |
| The Narrow Bridge Gang | Intact bridge crossing with bank cover, toll barricades and collected goods on the gang's bank. |

These are 14×11 maps. Current enemy budgets, loot tables and victory objectives are preserved; longer routes and constrained approaches change tactics and need later player balancing feedback. Existing active battles keep their saved map. Restart/create a Battle Lab session to see the new design.

## Reusable pieces and variations

`backend/location_maps.py` owns `enclosure`, `work_bay`, `grave_plots` and `river_crossing`. Enclosures create a continuous perimeter, correct corner rotations and one gate. Work bays arrange benches/storage or anvil/forge combinations. Grave rows include burial earth and associated markers. River crossings paint water and bridge floor, with all deep-water cells marked impassable on foot. Flying units can cross deep water through existing flight rules; no swimming or drowning system was added.

`MISSION_LOCATIONS` attaches a named setting to each selected mission without changing its encounter ID. Compiled maps report `location_id` and `map_variation`. Each setting has two deterministic dressing variants selected by seed; tree/lantern/rock placement changes while the location, bridge and entrances stay recognizable. These are modest variations, not a claim of procedurally unique buildings. The components can be reused or expanded into larger authored variations later.

Closed gates block movement and sight. Adjacent characters can open or close them through Actions or the gate tile menu, using their main action. An occupied gate cannot close. Gates can also be attacked and destroyed. AI and automatic combat can open an adjacent closed gate toward an opponent. Gates occupy the structure layer exactly once; they are not duplicated as a ground tile or object. Healthy obstacle HP labels show on hover/targeting in these maps to reduce visual clutter.

## Assets and preservation

New art: 12 props in `staging-terrain/location-props-v1/location_props_12.png`, and 8 structures in `staging-terrain/location-structures-v1/location_structures_8.png`. Prompts and extraction reports sit beside each source. Runtime folders: `props/location-v1` and `structures/location-v1` under `frontend/public/assets/combat-terrain`. Transparent silhouettes are extracted and normalized without stretching; detached bone details and open gate leaves are retained. None of the previous assets were overwritten.

Terrain comes from the existing approved `mega-terrain-tiles` library: timber floor, repair cobbles, dark soil, shaded woodland, mossy paving and deep water. No new terrain generation was necessary for this pass. Terrain, props and structures are separate packs. Bridges are ground tiles; their bank abutments are structures.

The original four generic layouts remain in `_contract_blueprint` as fallback templates. Their reproducible baseline snapshots are preserved in `docs/maps/archive/contract_layouts_v1.json`. Existing map templates were not deleted.

Reinstall new assets with `.venv\Scripts\python.exe tools\install_location_props.py` and `tools\install_location_structures.py`. Reinstalling the older overhead pack preserves these other libraries. Sources must remain available locally; generated media is excluded from the public code repository.

## Validation and remaining work

Five new backend tests cover repeatability, both variants, valid/non-overlapping spawns, routes to exits, continuous deep water, ground-based bridges, full perimeters, gate opening/closing/occupied closure/destruction and saved-map stability. Full suite: 314 backend tests passed. Browser previews checked all six maps, actual floor textures and every assigned sprite. Art coverage audit: 65 encounter setups and 1,044 references, no missing assignments/files. Frontend build and existing frontend tests passed.

Next focused designs: chapel exterior/gatehouse; toll ford and watch dispute; fortified command camp/road blockade; tunnels and armory; riverside submerged bell; raider cache; reclaimed sparring yard for A Promise Proven in Battle. The latter currently describes defeating occupying fighters, so it should read as reclaimed training ground, not a harmless practice match. Map objectives for collecting timber/tools and noncombat story routes can receive a separate refinement; this pass does not introduce new resource-interaction or reward rules.
