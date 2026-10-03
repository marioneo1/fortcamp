# Modular wall art — current dev strategy

## Face orientation and corner matching ? implemented

The source horizontal band has its painted front face below its centerline. Outer corner arms establish the inward-facing convention: straight perimeter runs must match that face, including south and west walls. Use the rotated boundary normal to mirror the texture across its thickness independently of saved grid rotation. Do not rotate collision edges to fix an illustration. Centered dividers normalize half turns to keep horizontal faces down and vertical faces left. Each centered T/cross arm follows this convention independently; a perimeter T preserves its inward-facing boundary bar and normalizes only its divider stem. Translated concave corner arms reverse their painted side. Breach alignment corrections follow texture mirroring.

Metal corner bands meet along complementary diagonal clips, avoiding doubled rims at the inner corner. The clip is reflected before a texture mirror so its map-space attachment remains unchanged. Stone and timber keep their current corner join geometry. The enlarged review now saves every material at every quarter turn under staging-terrain/building-toolset-v4; full Battle Lab layouts verify opposite sides in context. No new source images were generated for this pass.

## Separate the wall band from its terminal column

A connecting wall is a continuous painted band with flat, uncapped mating ends. A cap/column is a separate sprite placed only at an exposed endpoint. Two connected walls consume their shared endpoint: neither adds a column there. Corners, Ts and crosses establish connectivity, rather than repeating the columns embedded in the source illustration. Deliberate architectural pillars remain separate placed props and do not follow this rule.

This is implemented for regenerated rough fieldstone and polished limestone (building-v4). Metal retains its v2 art: the renderer reuses only its post-free middle band for connected segments, and keeps an original terminal post at an exposed end. Timber keeps the previous rendering. It can adopt this scheme later if needed.

## Atlas specification

Generate one material per transparent, evenly spaced 4×4 atlas. Never mix terrain or furniture into it. Use the established painted medieval palette, strict overhead orthographic viewpoint and consistent wall thickness/stone scale. Connecting bands must have no enlarged caps or pillars at either end or junction. Keep the masonry continuous around turns; no larger intersection block. Door/gate state pairs must share their jamb positions, scale and camera direction. Damage must preserve the surviving bands' centerlines.

Row-major order: straight wall, top/right L corner, centered T (stem down), cross; half-wall terminal, horizontal breach, door closed/open; gate closed/open, window wall, separate small cap/pillar; stairs, broken top/right corner, perimeter T (top bar and center down stem), brace. Plain band endpoints, a separate cap, and equal square cells are more important than decorative posts. Exact v4 prompts and generated sources live in staging-terrain/building-toolset-v4. Originals are preserved; generated media are excluded from Git and require separate backup.

Image generation cannot guarantee pixel-exact mating points or a requested pixel size. Import complete silhouettes, preserve proportions, and calibrate the result. Current corners/Ts/crosses use the new band texture with deterministic clipping/positioning. New stone terminal pieces occupy exactly half a cell even when the generated terminal illustration is longer. This prevents generation drift from changing the map layout.

## Connection rules and review

Endpoints are compared in map space after rotation and edge placement. Adjacency alone is insufficient: parallel walls beside each other must keep their end caps. Door and gate jambs count as neighboring connections even when open. Destroying/removing a neighboring segment exposes a new cap. A damaged corner retains its broken center; its surviving outer endpoints still connect. Caps are visual only and add no health, collision, targets or objects to saves.

Connection lookup is indexed once per render; it does not search all walls for every beam. Already resolved texture sections never recursively produce more sections. Quarter turns and inward-corner offsets follow the parent structure. Saved edge walls use current material calibration without rewriting their map geometry.

Review in **Battle Lab → Source: Building material tests**: all four layouts per material. Also build the enlarged six-type/rotation comparison with tools/build_wall_join_preview.py. Check isolated walls, long runs, external/internal corners, Ts/crosses, half ends, closed/open doors and damaged neighbors, at both close zoom and normal map scale. Asset coverage and functional tests do not replace user visual approval.

Remaining art limitations: door/gate sprites in the new generated sheets still show more frontal surface than an ideal strict overhead kit. Their connectivity is implemented, but a later camera/style pass may replace them. Functional stairs and floor transitions remain deferred.
