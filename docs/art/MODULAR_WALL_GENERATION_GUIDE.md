# Modular wall art — current dev strategy

## October 2: Fit candidate stone corners and lengths to actual building boundaries

Restored the template's edge-wall collision convention. Candidate perimeter bands now sit 0.38 tile from cell centre; the generated corner's bend sits at the rotated boundary intersection rather than the tile centre. Concave joins retain their template seating. Full bands span one unit, half bands half a unit; corner arms and perimeter T stems extend 0.88 units to meet the neighbouring boundary/divider ports. Centre T/cross arms reach half-unit ports. Dedicated authored corner/T/cross centres remain intact. Only outer arms use uncapped cropped sections of the matching straight/vertical material from the SAME generation; sections repeat at unchanged pixel scale. No image stretching, foreign wall art, centre patches, synthetic overlapping junction bands or extra posts. Added a separate perimeter-T export. Sprites use shared 1024px canvases and port-based anchors.

Reinstallation now calls tools/fit_boxed_wall_ports.py automatically from tools/install_boxed_wall_trial.py; raw recovery is internal, so reimport does not undo calibration. The frontend's native connection ports use these exact arm lengths. Cache stamp updated. Timber/metal and all old stone profiles remain unchanged. Review screenshots of all four complete buildings show boundary corners and continuous wall runs; subtle texture/stone-course transitions still exist and visual approval is not claimed. Verification: four backend material tests, 31 frontend wall tests including corner-to-band/perimeter-T coincidence, frontend build, and four actual-renderer browser maps with loading assets and no procedural junction connectors. The browser screenshots are in staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production unchanged.

## October 2: Replace isolated wall displays with full building comparisons

User rejected the candidate's isolated pieces/rotated sample rows as insufficient. The same dev material now rebuilds the four established furnished building plans: gatehouse, divided hall, breached annex and twin stores, using material-layout-1 through material-layout-4. Former boxed-walls-1..4 seeds remain aliases. Stone shells, partitions and authored junctions use the new generated six-piece art at one shared scale; all room floors and original furniture remain. Doors/gates deliberately use working timber leaves, because no matching door art was generated; broken sections use traversable gaps with common stone-debris props. Removed unsupported pillar/stair/brace sample decorations rather than pretending they came from the new atlas. Native masonry occupies its cell; enemy spawn candidates are recalculated to avoid occupied walls. No old stone wall textures are mixed into the new shell.

Verified four complete-building renders and reviewed screenshots of every layout; four backend material tests pass, including full-plan/floor/furniture preservation, working gate pairs, reachable exits and save/owner isolation. Generated thickness/span inconsistencies remain visible and are not called solved. Screenshots: staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production and normal mission defaults unchanged. This supersedes the previous individual-piece Battle Lab layouts.

## October 2: Boxed six-piece kit available in dev Battle Lab

Installed the v9 candidate additively as **Polished stone (Boxed six-piece trial)** in Building material tests. Four seeds: boxed-walls-1 (individual pieces), boxed-walls-2 (connected runs), boxed-walls-3 (90-degree connected runs), boxed-walls-4 (180-degree connected runs). Six source silhouettes are exported on shared 640px canvases at unchanged scale; measured intersection anchors seat them on the grid. Removed broad soft-alpha background halos using silhouette ownership with a two-pixel fringe. No texture stretching or independent piece rescaling. The new native_pieces profile draws generated corner/T/cross directly, without procedural connectors, cap overlays or face mirroring. Old material profiles/default maps remain unchanged.

This is an in-game comparison, not an even or seamless kit: generated full/T/cross spans are 397/443/412px, and half width is 218px. Gates, breaches and other parts were not generated and are not substituted from another kit. The dedicated test maps use ordinary destructible blocking walls, owner-scoped temporary Battle Lab parties and reachable exits. Verification: three material tests (all seven material families), 30 wall-renderer tests, frontend build and all four isolated browser renders with every candidate asset loading and zero procedural connector elements. Connected-run screenshot inspected; joins remain subject to visual review. Rebuild tool: tools/install_boxed_wall_trial.py. Browser check: tools/boxed_wall_browser_qa.mjs. Media excluded from Git; stored locally in structures/building-v9-boxed and staging-terrain/building-toolset-v9-boxed-reference.

## October 2: Explicit boxed generation reference

Added a visible 3x2 diagram of six equal 512px square cells, with labels, dimensioned full/half silhouettes and matching axes. Saved under staging-terrain/building-toolset-v9-boxed-reference/six_equal_cells_reference.png. Generated all six matching parts together using that guide and the painted style reference. The generator still varied bar spans and added soft alpha halos; source/report preserved, not installed or approved. Future generation references must show clear equal cell boundaries and declared piece dimensions, rather than relying on invisible cell positions. Even boxes do not alone prove compatible asset geometry.

## October 2: Complete material kits must be generated together

Generate each material's straight bands and authored junctions in the SAME atlas generation. Do not generate only junctions and later generate their straight walls separately: this omits essential parts and risks different style/stone scale. Minimum matched trial: full horizontal, half horizontal, full vertical, corner, T and cross. Measure before installation; sharing a generation does not guarantee compatible lengths.

Saved six-piece one-generation limestone candidate in staging-terrain/building-toolset-v8-matched-walls, with exact prompt, geometry reference, intact atlas and complete region crops at unchanged scale. Full horizontal/T solid widths 446/448px; cross 397px; half 235px. Not approved or installed; modular fit and generated shadow alpha need correction/review. Prior materials retained.

## October 2: Assembly rejected; dedicated generated junctions required

User rejected the v6 band-and-patch corner/T/cross assembly because of ugly overlaps. That prototype is rejected, not awaiting approval. Do not promote its renderer, overlays or center patches into combat. Generate complete authored corner, T and cross silhouettes with continuous masonry, matching painted-map art and shared full/half-unit geometry. Request the pieces the renderer actually needs; do not substitute intersecting straight sprites as the finished art solution.

Two guided built-in imagegen trials are saved in staging-terrain/building-toolset-v7-junctions with source images, exact prompts, a geometry diagram, alpha-extracted whole pieces and measured extraction reports. First trial has inconsistent arm lengths/cross-sections; second has inconsistent T/cross spans and a stepped corner. Neither is modularly approved or installed. Do not conceal mismatches with independent resizing, warping or patch overlays. Next pass must validate actual end ports, matching straight-band cross-sections and connection examples before installation. Existing materials remain active.

## October 2: Fixed-unit corner/T/cross preview available

Built a standalone assembly prototype from the v6 painted bands. Open staging-terrain/building-toolset-v6-gridfit/junction-preview.html, or review junctions-0/90/180/270.png. Controls choose quarter-turn rotation, one of four source textures and a tile grid. Each preview shows the three junctions enlarged and on actual smithy paving. Corner arms measure 128px each; T bar/stem 256/128px; cross spans 256/256px. All top bands are 48px thick. The 84px painted source cross-section is split into 48px top and 36px side material. No texture scaling or independently inflated half pieces.

This prototype combines the top footprint before projecting a 36px shaded side downward. That suppresses internal faces passing across a connecting stem and keeps camera direction stable through rotation. A 48px matching top patch covers the center; it is not a raised column. Brick/mortar transitions remain visibly assembled, so this is an art comparison rather than an approved replacement. The production combat renderer has not adopted this projection algorithm. Original materials remain active.

Guided dedicated junction generation is also valid: use these fixed-unit footprints as geometry references and preserve dimensions at import. The user does not prohibit actual corner/T/cross shapes; the rejected issue was oversized independently sized illustrations. tools/build_gridfit_join_preview.py reproduces the standalone page and tools/gridfit_join_browser_qa.mjs checks 16 rotation/texture combinations and exports the four comparison images. User rejected this assembly preview; retain it only as historical evidence of the failed approach.

## October 2: Painted grid-unit direction supersedes the pure-overhead experiment

User rejected the planar polished material style and inconsistent generated lengths, and explicitly withdrew pure-top-down as the main requirement. PRIORITY: match existing painted terrain/props. Preserve all original and comparison materials. Do not interpret the prior overhead trial as the new art standard.

Construction assets must be designed around one declared unit and its exact half, with one material cross-section and one stone scale. Generate dedicated corner, T and cross pieces with specified half-length arms and full-length bars, sharing one cross-section and compatible end ports with straight bands. Do not generate oversized long L legs or use intersecting bands as a substitute for authored junction masonry. An atlas cell is packaging, not permission to inflate small parts to its size. Never normalize a half wall or small joint independently to full-wall width.

New source trial: staging-terrain/building-toolset-v6-gridfit. References explicitly separate a measured geometry blueprint, existing v4 limestone wall style and actual smithy-cobble map style. The new generated sheet is closer to the painted direction but still failed dimensional constraints: full bands measured 276-281px, alleged halves 171-174px. Rejected its structural half/join/door rows. Do not claim the raw sheet is grid-correct.

Prepared four full bands, their exact halves and compact joining texture patches by crop only from the same four source bands: 256px full unit, 128px half, shared 84px painted cross-section including the side face, 48px-wide joining patch. Cut away terminal rim pixels for flush ends. No resizing/warping or long L arms. limestone_gridfit_12.png, individual sprites, geometry_report.json and full_and_half_on_map_floor.png record the usable trial. Exact prompt and source preserved. This is staging only; gate/door approval and a prototype with construction ports defined by the grid rather than generated silhouette dimensions remain pending. Do not feed the 12-piece pack to the old 16-piece installer.

## October 2: Overhead stone profiles installed additively for comparison

The two candidates below are now installed as separate limestone_plan and fieldstone_plan materials under structures/building-v5-topdown, with 32 new stable registry entries. No original registry entry, geometry profile, source image or default mission material was changed. Battle Lab > Building material tests exposes both Pure overhead entries alongside the four original kits, with the same four layout seeds.

The additive installer tools/install_topdown_stone_toolsets.py extracts complete silhouettes, shares source scale, anchors open/closed gate/door pairs to their measured jambs and writes independent join/breach/end metadata to both geometry manifests. Plan-view profiles disable painted-face mirroring and additional end columns; intact corners/Ts/crosses still assemble matching unclipped-thickness straight bands at deterministic boundaries. The original material installer now retains additive profiles. Remaining: user comparison/selection and a later decision about mission defaults. Previous staging-only status below records the generation phase.

## October 2: Pure overhead stone candidates (not active)

Preserved every active kit and generated new polished-limestone and rough-fieldstone packs from scratch using the built-in image generator. Separate 4x4 packs live in staging-terrain/building-toolset-v5-topdown. Their strict plan-view prompt rejects visible vertical faces, perspective, raised columns and external cast shadows. Closed/open doors and gates are thin top-edge leaves in the ground plane. Rejected the first limestone draft because it still illustrated door fronts; retained it under an explicit rejected filename.

Selected candidates, exact prompts, extraction report, 32 isolated sprites and a portable preview.html are saved in that folder. Requested 2048px output became 1254px; alpha-component extraction and relative cell positions recovered complete silhouettes. Current building-v4 selection, directional corners, registry, geometry, wood and metal remain unchanged. Visual review and optional in-map profile integration remain pending. These planar candidates must receive their own calibration; do not inherit v4's painted-side mirroring or corner-column assembly. Subtle border shading remains in the selected art, and generated mating points still require measurement.

## Supplied limestone corners: face and seating rules

The current limestone directional images shade outward. Use material metadata `perimeter_face: outward` for their adjoining perimeter bands, perimeter-T bars and exposed posts; other kits retain their existing inward convention. Match the source corner rather than assuming a universal inward face. Centered dividers still face horizontal-down/vertical-left.

Render the supplied corner's built-in column only, clipped in its original unrotated directional image on layer 4. Assemble its arms from matching straight bands on layers 3/2. Extend bands 0.035 tile under the column along their length, preserving thickness and aspect ratio. This removes unequal source arm tips and seats the bands inside the existing column without adding pillars or shifting the boundary sideways. Directional anchor offsets and collision ports are unchanged. Check all four corner directions enlarged as well as perimeter runs in a full map; passing geometry tests alone does not establish visual quality. Legacy damaged-corner art needs a separate matching-face pass.

## Directional limestone corners - current replacement

The strategic connector-pillar experiment was reverted. Intact limestone corners instead use the user's four limestone_wall_north_east/north_west/south_east/south_west.png images from building-v4. Their built-in corner detail remains part of the image; no separate strategic pillars are added. Logical quarter turns select a matching directional file; the image itself stays at zero rotation with no mirroring. Each horizontal/vertical arm has a measured alignment offset, preserving scale and logical ports.

Keep these custom files in frontend/public/assets/combat-terrain/structures/building-v4, not only frontend/dist, which builds replace. Originals are backed up in staging-terrain/building-toolset-v4/directional-limestone-corners. A complete optional directional set is detected and recalibrated by the material installer without re-extracting/overwriting it. Rough stone continues to use prior assembled corners. Visual approval is pending.

## Face orientation and corner matching ? implemented

The source horizontal band has its painted front face below its centerline. Outer corner arms establish the inward-facing convention: straight perimeter runs must match that face, including south and west walls. Use the rotated boundary normal to mirror the texture across its thickness independently of saved grid rotation. Do not rotate collision edges to fix an illustration. Centered dividers normalize half turns to keep horizontal faces down and vertical faces left. Each centered T/cross arm follows this convention independently; a perimeter T preserves its inward-facing boundary bar and normalizes only its divider stem. Translated concave corner arms reverse their painted side. Breach alignment corrections follow texture mirroring.

Metal corner bands meet along complementary diagonal clips, avoiding doubled rims at the inner corner. The clip is reflected before a texture mirror so its map-space attachment remains unchanged. Stone and timber keep their current corner join geometry. The enlarged review now saves every material at every quarter turn under staging-terrain/building-toolset-v4; full Battle Lab layouts verify opposite sides in context. No new source images were generated for this pass.

## Separate the wall band from its terminal column

A connecting wall is a continuous painted band with flat, uncapped mating ends. A cap/column is a separate sprite placed only at an exposed endpoint. Two connected walls consume their shared endpoint: neither adds a column there. Corners, Ts and crosses establish connectivity, rather than repeating the columns embedded in the source illustration. Deliberate architectural pillars remain separate placed props and do not follow this rule.

This is implemented for regenerated rough fieldstone and polished limestone (building-v4). Metal retains its v2 art: the renderer reuses only its post-free middle band for connected segments, and keeps an original terminal post at an exposed end. Timber keeps the previous rendering. It can adopt this scheme later if needed.

## Required building assembly checklist

- Perimeter bands follow their kit's corner faces (outward for the supplied limestone corners, inward for the other kits); interior horizontal bands face down, vertical bands face left.
- T/cross arms normalize their face independently. A perimeter T follows the material's perimeter face for its bar and matches only its stem to the divider.
- Preserve thickness and proportions; clip lengths and metal corner mating planes instead of stretching art.
- Connected ports suppress terminal posts. Exposed posts match the attached face, including mirrored opposite endpoints.
- Vertical bands use layer 2, horizontal bands layer 3, and exposed posts layer 4 below character tokens (5). This makes horizontal bands cover vertical ones at corners and T/cross joins. Keep posts non-interactive and separate from collision.
- Mirroring must preserve attachment points, breach calibration and saved grid/boundary rotation.
- Review all four material layouts, both endpoint directions, rotated joins and open/damaged neighbors using the real renderer.

The dedicated v4 stone centered T is used for the left-branch orientation (90 degrees), where its painted faces match the divider convention. Its full bar/half stem are preserved at the existing scale, with a measured alpha-row anchor recorded in both geometry manifests by the installer. Other orientations retain assembly because rotating the whole source would reverse one of its faces.

These are implemented renderer rules, not instructions to manually flip individual maps. Reuse the structural layout/connector helpers for future buildings and previews.

## Atlas specification

Generate one material per transparent, evenly spaced 4×4 atlas. Never mix terrain or furniture into it. Use the established painted medieval palette, strict overhead orthographic viewpoint and consistent wall thickness/stone scale. Connecting bands must have no enlarged caps or pillars at either end or junction. Keep the masonry continuous around turns; no larger intersection block. Door/gate state pairs must share their jamb positions, scale and camera direction. Damage must preserve the surviving bands' centerlines.

Row-major order: straight wall, top/right L corner, centered T (stem down), cross; half-wall terminal, horizontal breach, door closed/open; gate closed/open, window wall, separate small cap/pillar; stairs, broken top/right corner, perimeter T (top bar and center down stem), brace. Plain band endpoints, a separate cap, and equal square cells are more important than decorative posts. Exact v4 prompts and generated sources live in staging-terrain/building-toolset-v4. Originals are preserved; generated media are excluded from Git and require separate backup.

Image generation cannot guarantee pixel-exact mating points or a requested pixel size. Import complete silhouettes, preserve proportions, and calibrate the result. Current corners/Ts/crosses use the new band texture with deterministic clipping/positioning. New stone terminal pieces occupy exactly half a cell even when the generated terminal illustration is longer. This prevents generation drift from changing the map layout.

## Connection rules and review

Endpoints are compared in map space after rotation and edge placement. Adjacency alone is insufficient: parallel walls beside each other must keep their end caps. Door and gate jambs count as neighboring connections even when open. Destroying/removing a neighboring segment exposes a new cap. A damaged corner retains its broken center; its surviving outer endpoints still connect. Caps are visual only and add no health, collision, targets or objects to saves.

Connection lookup is indexed once per render; it does not search all walls for every beam. Already resolved texture sections never recursively produce more sections. Quarter turns and inward-corner offsets follow the parent structure. Saved edge walls use current material calibration without rewriting their map geometry.

Review in **Battle Lab → Source: Building material tests**: all four layouts per material. Also build the enlarged six-type/rotation comparison with tools/build_wall_join_preview.py. Check isolated walls, long runs, external/internal corners, Ts/crosses, half ends, closed/open doors and damaged neighbors, at both close zoom and normal map scale. Asset coverage and functional tests do not replace user visual approval.

Remaining art limitations: door/gate sprites in the new generated sheets still show more frontal surface than an ideal strict overhead kit. Their connectivity is implemented, but a later camera/style pass may replace them. Functional stairs and floor transitions remain deferred.
