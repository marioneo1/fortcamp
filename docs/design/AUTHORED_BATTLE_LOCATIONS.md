# Authored battle locations

## October 3: Finished materials rolled into mission locations

Implemented in dev. New battles use the approved timber, rough-stone, polished-stone and metal kits through the same shared connection/orientation rules as the material tests. No art regeneration or material geometry changes in this pass.

| Setting | Missions using it | Material and identity | Layouts |
| --- | --- | --- | --- |
| Chapel approach | The Chapel Patrol; The Chapel Gatekeepers | Polished stone, cracked chapel paving, altar, pews, fallen bell and memorial stone. | Nave; divided vestry; burial annex; twin chapels with memorial court. |
| Toll post | The Unwanted Toll; The Ford Enforcers; A Watchman's Dispute; A Road Wide Enough for Everyone; Who Collects the Second Toll? | Rough stone, toll cobbles, ledger desk, inspection crates, guard equipment and operable gates. Existing story/roll routes remain unchanged; this applies when their tactical encounter starts. | Toll court; through-road customs hall; inspection wing; paired posts. |
| Raider cache | The Road Raiders' Cache; Bandit Outpost | Timber storehouses, stolen crates/barrels, sorting table and escape breach. | Storehouse; divided hideout; annex yard; twin stores. |
| Goblin armory | The Hidden Goblin Armory | Reinforced metal magazines, racks, ammunition and supply coffer. Replaces the two legacy timber enclosures. | Weapon store; divided magazine; loading yard; twin magazines. |
| Salvage court | The Salvage Yard Court | Approved rough-stone workshop buildings with existing forge/repair vocabulary. | Uses the four existing workshop footprints. |

Sixteen mission-specific building definitions reuse the eight approved footprints. Reuse is intentional, rather than claiming each skin is new geometry. Doors, breaches, furniture and enemy positions belong to the building template; mission rewards, rank budgets and objectives remain unchanged. Small patrols in twin buildings now occupy both buildings instead of putting every enemy in the first room.

All building locations, including the existing shed/workshop, also have four seeded dressing choices independent of their four layout choices. Solid furniture swaps among authored slots; loose scenery may relocate to free floor. Doors, walls, spawn cells and other props are excluded. Choices reproduce from the encounter seed and stay stored in an active battle. Chests/coffers used as scenery do not gain a loot-opening interaction in this pass.

Battle Lab automatically lists verified seeds and names for all four layouts on these missions and on story choices that lead to them. Start a new test/battle to see changes; existing saved encounters are not regenerated. Screenshots: `staging-terrain/location-rollout-v1`. The actual renderer QA tool is `tools/location_rollout_browser_qa.mjs`; `tools/audit_battle_locations.py` refreshes the [complete coverage audit](../maps/BATTLE_LOCATION_AUDIT.md).

### Proposed next batches

The [complete remaining-location review](../maps/GENERIC_CONTRACT_LOCATION_REVIEW.md) supersedes broad setting assumptions below. In particular, Knight without a Grave's own premise places it on the royal road; crypt/chapel settings should follow the origin of its reused story encounters. The review contains brief proposed maps for every remaining generic mission title and records additional bridge/chapel placement issues.

These are pending design work, not implemented by this rollout:

1. **Roadblocks and command camps:** Break the Rival Warband, End the Old Command, Chieftain's Redoubt and The Ironcap Vanguard need actual fortified positions, guard lanes and supply/command areas. Add a reusable road-spanning blockade piece and camp perimeter, rather than another storehouse skin. Reuse current gates, timber/stone walls, tents and alarm bell.
2. **Beginner sites and sparring yards:** Rats in the Storehouse, Wolves at the Fence, Herbs Behind the Wall and A Promise Proven in Battle need smaller sites and more direct routes. Sparring yards need training-dummy art; gardens need planted beds. Keep early fights compact instead of copying a large fort.
3. **Tunnels and burial interiors:** Goblin Warren Purge, Knight without a Grave and Court of the Empty Crown need branching tunnels/crypts or ruined halls with their own chokepoints. Tunnel terrain, stairs and larger chamber pieces should be separate terrain/structure packs.
4. **Convoys, investigation sites and the flooded bell:** The Tithe Convoy, missing patrol/wagon jobs and The Bell Beneath the Mud need road bends, wagon staging, waterlogged approaches or a submerged chapel/bell. The bell currently routes combat complications to existing undead encounters; a dedicated bell map requires deliberate story-routing changes. Preserve the existing bridge ground-layer approach.
5. **Separate scenarios:** Goblin Warcamp, Captive Cart, investigation ambush and defense have authored generators already, but should receive a separate layout-variation review. Preserve their rescue objects, alarm logic, extraction rules and defense preparation.

The audit currently identifies 17 authored contract encounter IDs and 44 generic ones, including six rank copies for each prisoner agreement route. Finish these in focused batches; do not turn roll-only missions into fights merely to give every mission a map.

Validation: 35 focused backend tests pass (location routes/spawns over 40 seeds, material maps, normal battle maps, Battle Lab catalogue and save isolation). Actual browser checks render 20 new setting/layout combinations with no runtime errors; 50 distinct prop URLs load. Reviewed representative enlarged chapel/toll/armory/cache images. The complete art audit checks 145 isolated encounter previews and 7,877 references with no missing assignments/files. Long-term tactical pacing and player feedback remain follow-up work; identical enemy budgets do not guarantee identical difficulty after changing a map.

## Current wall rules and art (October 2)

New building/enclosure perimeters now block crossing edges while leaving interior floor tiles usable. Centered dividers still occupy their tile; actual T-junctions connect them to the outer shell. Doors, attacks, enemy pursuit and escape use the same boundaries. Four complete material-specific structure packs supersede the mixed-material art below; original sources remain legacy. See WALL_BOUNDARIES.md and BUILDING_TEMPLATES.md. Existing saved maps are not regenerated.

## Current: coordinated building toolset and eight reusable plans

Shed and workshop selection now uses four distinct building footprints each, assembled independently of the map. This supersedes the flipped shed and three earlier workshop choices below. Matching fieldstone straight/corner art replaces the mixed libraries. Small doors and gates have coordinated overhead state pairs. See BUILDING_TEMPLATES.md for the eight plans, 40-part structural toolset, source prompts, calibrated joins, installation and validation. The old layouts are preserved in `docs/maps/archive/building_locations_v2.json`.

## October 2 follow-up: doors, building plans and crossing art

Current dev adds The Hidden Goblin Armory to the six locations below. Its two plans use north/south or east/west storage houses joined by an open, paved armory courtyard. Weapon racks, shields, armor and arrow storage identify the place. The existing mission objective, loot and rank budget are preserved.

Workshops now choose among three saved plans: the original enclosed repair yard, two workshops across a courtyard, and a forge house with open work bays. Shed plans mirror the damaged entrance between north and south. Bridges move between two crossing positions; the toll bridge also switches between wood and stone. Selection is deterministic from the encounter seed. `backend/location_templates.py` stores building rectangles, doors, furniture and safe spawns; the original authored baseline remains in `docs/maps/archive/location_layouts_v1.json`. Existing saved battles keep their map.

Enemy pursuit now compares a breach/detour with a door route, including the cost of spending an activation to open it. Units stop beside a closed door before opening it; they cannot walk through it. Panicked units use this same route comparison to escape enclosed rooms. A very close breach can still be the better route. Ordinary terrain, occupied cells and climb rules remain respected.

Lanterns render at one-third size, including existing saved lantern sprites. Straight perimeter walls and doors move 28% of a cell toward the outside edge to meet the corner pieces. Broken shed walls keep that alignment; destroyed walls retain their offset. This changes artwork placement, not collision cells. Corners remain anchored to their original cells.

Follow-up correction: the offset declaration initially lost to the later-loaded global stylesheet, so the intended positioning was not visible. The global sprite rule now applies offsets directly; the duplicate earlier declaration is removed. Browser checks assert the computed sprite position, rather than just checking that offset metadata exists, and screenshots confirm the straight/broken walls join the corners. Battle Lab now exposes named layouts with verified seeds; see BATTLE_LAB.md.

New separate atlases: 12 terrain cells in `staging-terrain/bridge-terrain-v1/bridge_terrain_12.png`, and eight transparent props in `staging-terrain/armory-props-v1/armory_props_8.png`. Reinstall both with `.venv\Scripts\python.exe tools\install_bridge_armory_art.py`. The terrain pack is a gapless 4×3 grid cropped relative to actual source dimensions. Prop silhouettes use connected components within a 4×2 grid, including disconnected details; normalization preserves aspect ratio. Old libraries are preserved.

Live terrain: wood/stone bridge edges, damaged plank crossing, toll cobbles and soot-stained workshop paving. Live props: weapon/shield racks, armor stand, arrow crate and toll ledger desk. Chapel paving, altar, pew and fallen bell are prepared assets for the next focused chapel/bell map pass; those missions have not been redesigned yet. Bridge edge strips are part of decking, not a second wall entity.

Validation: 316 backend tests, 103 frontend tests and production frontend build passed. Template checks cover 40 seeds per location, valid spawns, reachable exits, deterministic selection, door-vs-breach pursuit, fleeing through doors and offsets after destruction. Browser checks cover all seven locations and both new armory/three workshop plans. No production deployment or save changes.

## First focused pass (preserved history)

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

`MISSION_LOCATIONS` attaches a named setting to each selected mission without changing its encounter ID. Compiled maps report `location_id`, `map_variation` and now `template_id`. The first pass had two dressing variants per setting; the follow-up above adds actual building and crossing plans.

Closed gates block movement and sight. Adjacent characters can open or close them through Actions or the gate tile menu, using their main action. An occupied gate cannot close. Gates can also be attacked and destroyed. AI and automatic combat can open an adjacent closed gate toward an opponent. Gates occupy the structure layer exactly once; they are not duplicated as a ground tile or object. Healthy obstacle HP labels show on hover/targeting in these maps to reduce visual clutter.

## Assets and preservation

New art: 12 props in `staging-terrain/location-props-v1/location_props_12.png`, and 8 structures in `staging-terrain/location-structures-v1/location_structures_8.png`. Prompts and extraction reports sit beside each source. Runtime folders: `props/location-v1` and `structures/location-v1` under `frontend/public/assets/combat-terrain`. Transparent silhouettes are extracted and normalized without stretching; detached bone details and open gate leaves are retained. None of the previous assets were overwritten.

Terrain comes from the existing approved `mega-terrain-tiles` library: timber floor, repair cobbles, dark soil, shaded woodland, mossy paving and deep water. No new terrain generation was necessary for this pass. Terrain, props and structures are separate packs. Bridges are ground tiles; their bank abutments are structures.

The original four generic layouts remain in `_contract_blueprint` as fallback templates. Their reproducible baseline snapshots are preserved in `docs/maps/archive/contract_layouts_v1.json`. Existing map templates were not deleted.

Reinstall new assets with `.venv\Scripts\python.exe tools\install_location_props.py` and `tools\install_location_structures.py`. Reinstalling the older overhead pack preserves these other libraries. Sources must remain available locally; generated media is excluded from the public code repository.

## Validation and remaining work

Five new backend tests cover repeatability, both variants, valid/non-overlapping spawns, routes to exits, continuous deep water, ground-based bridges, full perimeters, gate opening/closing/occupied closure/destruction and saved-map stability. Full suite: 314 backend tests passed. Browser previews checked all six maps, actual floor textures and every assigned sprite. Art coverage audit: 65 encounter setups and 1,044 references, no missing assignments/files. Frontend build and existing frontend tests passed.

Next focused designs: chapel exterior/gatehouse; toll ford and watch dispute; fortified command camp/road blockade; tunnels and armory; riverside submerged bell; raider cache; reclaimed sparring yard for A Promise Proven in Battle. The latter currently describes defeating occupying fighters, so it should read as reclaimed training ground, not a harmless practice match. Map objectives for collecting timber/tools and noncombat story routes can receive a separate refinement; this pass does not introduce new resource-interaction or reward rules.
