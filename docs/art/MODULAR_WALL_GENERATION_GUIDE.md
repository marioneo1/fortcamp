# Modular wall art — current dev strategy

## October 2: Painted grid-unit direction supersedes the pure-overhead experiment

User rejected the planar polished material style and inconsistent generated lengths, and explicitly withdrew pure-top-down as the main requirement. PRIORITY: match existing painted terrain/props. Preserve all original and comparison materials. Do not interpret the prior overhead trial as the new art standard.

Construction assets must be designed around one declared unit and its exact half, with one material cross-section and one stone scale. Do not request long independent L-corner sprites or full T/cross illustrations when the renderer uses straight bands. Corner/junction art covers only the local join; attached full/half segments supply arms. An atlas cell is packaging, not permission to inflate small parts to its size. Never normalize a half wall or small joint independently to full-wall width.

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
