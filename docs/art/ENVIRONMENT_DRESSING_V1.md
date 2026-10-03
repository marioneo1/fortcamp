# Herb garden and training yard visual prototypes

The garden now has additional overhead props and low crop edging; see [GARDEN_TOOLKIT_V2.md](GARDEN_TOOLKIT_V2.md). The first training-yard layout also has extra rest/repair clutter. This supersedes the initial furniture list below; ground composition and later-variant scope are unchanged.

Implemented in dev, October 3. Following approval of the first compositions, all four variants now have authored environment dressing; see GARDEN_TOOLKIT_V2.md for the current rollout. In Battle Lab, choose **Herbs
Behind the Wall → Walled herb beds** or **A Promise Proven in Battle ? Sparring yard and archery lane** (layout 1). Start a fresh session: saved
encounters retain their scenery and occupancy.

## Current composition

- Garden: four leaf/flower herb patches grow directly in the ground, separated
  by a cross-path, a narrow stepping-stone route and shallow irrigation grooves.
  The northern work area holds the herbalist's table, stored water and wash tub.
  A bench sits toward the south boundary. The older planter remains outside
  the entrance; there are no raised planter boxes inside this prototype.
- Training yard: worn sparring earth on the west, two dummy stations at its
  northern end, two targets with clear archery lanes on the east, straw around
  the practice stations, and a southern equipment/rest area. Centre and gate
  approaches remain usable.
- Furniture uses explicit visual offsets toward edges instead of every object
  sitting precisely in the cell centre. Its physical footprint stays unchanged.
  Approved modular walls retain their existing connection rules.

The ground detail is cosmetic and walkable. It introduces no harvesting,
training income, irrigation actions, firing-line restrictions or new loot.
Combat budgets and mission resolution remain unchanged. All four layouts of each setting now have their own adapted composition. The original layout-1 description above remains the starting point.

## Art and runtime

Created a new **terrain-only 4x4 atlas** with the built-in imagegen tool, using
the approved painted terrain and camp atlas as style references. The camera
request was orthographic 90-degree overhead. No furniture or structures were
included. The source and exact prompt are retained in
`staging-terrain/environment-ground-v1/environment_ground_16.png` and `PROMPT.md`.

The requested output was 2048x2048; actual output was 1254x1254. Extraction uses
relative equal-cell coordinates and a three-pixel inset to remove thin generated
seams, then saves 16 ground textures at 256x256. No prior terrain is overwritten.
Runtime art is `frontend/public/assets/combat-terrain/environment-ground-v1`;
names/order are recorded in `frontend/src/environment-ground-art.json` and the
source-folder `extraction.json`.

`backend/activity_dressing.py` assigns visual `ground_art` independently of the
existing movement material. A texture spans a continuous 2x2 patch through
background positioning, avoiding a separate full copy on each tile. The real
renderer uses this in battle and defense preparation. Older battles without
these visual overrides use their existing terrain.

## Tools

From the dev project:

```powershell
.venv\Scripts\python.exe tools/install_environment_ground.py
.venv\Scripts\python.exe tools/build_prop_coverage_preview.py
```

The installer rebuilds just these 16 textures from the retained source and its
registry. It does not generate art, change saves or reinstall the rejected garden kit.
For local renderer review, run `node tools/serve_board_preview.mjs`, use the
encounter preview, and select `herbs_wall_v1` / `prison_proof_d_v1`.
Automated screenshots use `node tools/location_rollout_browser_qa.mjs --activity-sites`
with the existing dedicated headless Chrome session. Results go to
`staging-terrain/environment-ground-v1/in-game`.

## Pending review

Review vegetation density, palette joins and equipment placement. This pack
does not guarantee seamless texture edges; broad patches and a consistent soil
palette reduce repetition, but actual screenshots must be checked. All four activity layouts now have adapted compositions; further specialised work props can follow as needed.

## Validation

Nine backend prop/beginner tests pass, including reachability over 400 generated
maps and preserving the other three variants. Eight focused frontend tests and
the frontend build pass. Actual renderer review captured both prototypes with
40 asset URLs loaded and no runtime exceptions; screenshots were visually
inspected. Full prop coverage checks 249 encounters and 19,571 references with
no missing sprite art. The activity review additionally checks authored ground
images, which are separate from the prop registry. Production and saves were
not modified.
