# Plain wood construction trial - dev Wall Kit Lab

Implemented October 4, 2026. Open **Mission Board -> Debug controls -> Wall Kit
Lab**. The **Debug wall kit** dropdown switches the entire temporary layout
between Geometry placeholders and Plain wood - painted test kit. It defaults
to painted wood. The layout includes all 24 selectable variants and a connected
room with four corners, horizontal/vertical runs and a closed gate. Floors,
props, selection, dragging, arrows and export work in the temporary layout.
Preview only is disabled: there is no save write, mission or economic effect.
Closing drops the test draft; reopening restores the samples. Normal base
construction has no kit dropdown and keeps its existing saved-layout behavior.

## Access and ownership

The backend GET /api/debug/construction/wall-kits requires debug enabled, a
non-production environment, and server admin identity or dev authentication
bypass. Prod/production/release/stable return 404 even if debug was enabled by
mistake; unauthorized non-admins return 403. The frontend lab button is also
hidden outside development debug access. No player state is read or written by
the lab endpoint. Runtime kit IDs are offered only if all nine media files exist.
Production, combat materials and real player saves were not changed.

## The agreed kit

24 selectable pieces use 9 generated originals per material:

| Family | Selectable pieces | Originals |
|---|---:|---:|
| Plain horizontal | 2 | 1 |
| Plain vertical | 2 | 1 |
| Horizontal one post | 4 | 1 |
| Vertical one post | 4 | 1 |
| Horizontal both posts | 2 | 1 |
| Vertical both posts | 2 | 1 |
| Full-length corners | 4 | 1 |
| Horizontal gate | 2 | 1 |
| Vertical gate | 2 | 1 |
| Total | 24 | 9 |

Horizontal and vertical artwork are independently generated; there is never a
90-degree bitmap rotation between them. Horizontal mirroring moves left/right
posts, vertical mirroring changes horizontal facing. Vertical mirroring moves
top/bottom posts, horizontal mirroring changes vertical facing. Corner mirrors
supply the four corners without exchanging the horizontal and vertical arms.
R now changes facing only within a straight/gate orientation family; it cycles
corner positions through mirrors. Choose horizontal versus vertical in the asset
library. Half walls, T junctions and + junctions are excluded. Previously saved
retired junctions still use their compatible placeholder renderer.

## Generation and extraction

Used the built-in imagegen tool with the active v2 timber atlas as a style
reference, an actual creek map as context, and a purpose-drawn 3x3 equal-cell
layout guide. All nine objects were generated together, then the same atlas was
refined to correct the initially short vertical plain wall. The corrected sheet
is 1254x1254; extraction uses relative third boundaries, making nine 418px cells.
The requested output dimensions were guidance, not an assumed crop size.
No final atlas separators or labels were generated. Alpha is preserved.

Source directory: staging-terrain/construction-plain-wood-v1.
- plain-wood-atlas.png: final corrected full atlas.
- atlas-first-candidate.png: original before the vertical-length correction.
- GENERATION_PROMPT.md and REFINEMENT_PROMPT.md: exact prompts.
- nine-piece-layout-reference.png: generation diagram.
- original-cells/: untouched relative-grid extractions.
- installation.json: source bounds, silhouette bounds and normalized sizes.
- wall-kit-lab.png and connected-room.png: real renderer/browser captures.

Rebuild with the dev Python environment:
`.venv/Scripts/python.exe tools/install_construction_wall_kit.py`.
No new batch launcher was added. The installer requires the source atlas and
Pillow, and installs only this trial directory. It never overwrites combat kits.

Installed media: frontend/public/assets/combat-terrain/construction/plain-wood-v1.
Manifest: frontend/src/construction-wall-art.json. Native mapping and reflection
rules: frontend/src/construction-wall-art.js.

Canonical canvases are 512px square with 416px connection spans and approximately
64px beam cross-sections. Post centers, rather than outer cap tips, define joins.
The importer measures alpha and dominant beam thickness, fits middle grain bands
to the module span while retaining authored ends/posts, and fits the native
corner with its joint retained. This is measured raster normalization; it does
not assume the generator produced equal lengths or assemble corners from other
sprites. Middle grain is resampled when span fitting is needed. The renderer
keeps the square source aspect ratio, uses exact shared ports, and applies only
reflections. There are no extra procedural posts or connector patches over the
painted art. Texture seams and painterly differences remain subject to review.

This is an intact-wall/closed-gate visual trial. Open/broken painted artwork,
permanent player material selection, costs, functional camp collision and raids
are future passes. Choosing painted wood overrides test-wall material appearance;
material/broken/open controls are disabled for the painted trial. Choosing it
also resets broken/open flags in the temporary draft so the whole layout uses
the same complete kit.

## Validation

10 construction backend checks plus economy/onboarding regressions (27 total),
155 frontend checks and build pass. Tests cover all 24 mappings to 9 originals,
separate native upright images, mirror directions, family-limited R, unchanged
logical geometry, legacy compatibility, no database access in the lab, and
production/debug/admin access checks. Actual browser QA loads all nine 512px
sprites, switches all 44 sample/room walls together, exercises a reflected drag
preview, confirms no PUT/save, verifies normal construction has no kit picker,
and checks dialog bounds at 1440/800/430px. Full lab and 100% connected-room
captures were visually inspected. Generated media remains local and excluded
from Git according to the existing media policy; code/docs/manifests are tracked.

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


October 4 construction follow-up: 11 wall-library entries cover all 24 orientations;
R changes native H/V artwork and rotates edge anchors; Center [Home] resets position.
World-segment duplicate detection prevents two neighboring cells owning the same
wall span while allowing perpendicular/end connections. Prop collision respects
actual offsets and wall thickness, in preview, selected edits and server saves.
Untouched old conflicts remain saveable. Shared movement helpers distinguish
edge crossing from blocked interior cells; base character walking is still deferred.
Validation: 161 frontend tests, 15 construction backend tests, build and browser
rotation/collision checks pass. Dev only; production and player saves untouched.
See docs/design/BASE_CONSTRUCTION.md for implemented rules and limitations.
