# Map prop sizing and garden import

Implemented in dev, October 3. The audit in [PROP_SIZE_AUDIT.md](PROP_SIZE_AUDIT.md) covers all 138 registered non-modular prop/state sprites across 249 isolated encounter previews. Modular architectural parts retain their existing material-specific joint geometry. Ground art is not a prop. Runtime alias and destroyed/open state resolution comes from the actual frontend resolver, not filename guesses. Prepared assets are counted and retained even when no current map uses them.

## Shared sizes

`backend/map_prop_sizes.json` and its frontend copy `frontend/src/map-prop-sizes.json` define defaults, physical categories and alpha-calibrated visual fill. These are generated together by `tools/audit_prop_sizes.py --write-profiles`; tests require equality. Visible fill is measured from non-negligible alpha, not the square PNG canvas. `propArtScale` applies it in both preparation and battle. Art retains aspect ratio through `background-size:contain`; it is never stretched to fill a footprint. Structural wall scaling and intentional unregistered overrides remain separate.

| Category | Standard occupancy and treatment |
| --- | --- |
| Small carried clutter | One logical cell with a smaller visible silhouette: purse, satchel, tools/caddies, watering can, pots, arrows. These do not visually equal a well or crate. |
| Ordinary furniture/containers | Usually 1x1; most visible outlines fill about 85% of the art box. Small desks remain single-cell furniture. |
| Well, prison wagon, rescue cages, tent, ballista | 2x2. The whole footprint is used by movement/target distance; solid map furniture blocks every covered cell. Decorative art does not gain blocking or interactions merely by being large. |
| Handcart, sarcophagus, stocks, garden workbench/trough/drying rack | 2x1; quarter turns exchange width and height. |
| Bedding | 1x2; natural source proportions retained, including narrower sleeping bags versus heavier beds. The reserved area can exceed the visible mattress. |
| Mature trees | One trunk cell with a 2x2 visual canopy; art may overhang surrounding ground without making every leaf block movement. Saplings/shrubs remain smaller. |
| Garden planting | Ordinary boxes/pots are 1x1. Explicit `raised-bed` variants of four planted boxes occupy 2x2. Larger plant beds are a named size variant rather than an accidental scale discrepancy. |

Footprints describe reserved grid space, not exact real-world metres. Some authored objects intentionally represent smaller versions of their standard family; the audit lists observed footprints so these remain reviewable. Existing saved battles retain their authored coordinates and collision rather than expanding a wagon underneath a unit mid-fight. Presentation follows the common calibration; create a new battle to obtain updated occupancy.

`location_maps.prop` supplies standard footprints to newly generated scenery/furniture. Existing explicit map footprints still override these defaults. New Old Well scenes use 2x2 wells. New Captive Cart scenes use a 2x2 wagon instead of the former enlarged one-cell obstacle; the wounded courier now lies immediately outside its western side, preserving body pickup access. Closed/open rescue cages already reserve 2x2. Large objects are drawn once over their footprint, not as repeated PNG tiles.

## User gardening atlas

Supplied atlas: `staging-terrain/Gardening Props Asset Atlas.png`. The original remains untouched; imported source copy, extraction coordinates and normalized review gallery are in `staging-terrain/garden-props-v1`. `tools/install_garden_props.py` imports all 32 objects by complete connected silhouette, including nearby detached details, rather than clipping at nominal cell edges. Crops are transparent 384x384 PNGs with padding and proportional fitting. Runtime: `frontend/public/assets/combat-terrain/props/garden-v1`; stable IDs start with `garden_`. The supplied garden mockup `staging-terrain/herb_garden_design.png` remains a design reference, not a flattened game map.

The four Herbs Behind the Wall layouts now have three or four 2x2 planting beds, a potting bench, water barrel, stone trough, compost and small tools/pots, arranged around clear cross aisles. The annex layout omits one bed where its wall prevents a valid fit. An ordinary herb box remains outside the wall. Ground paving uses existing terrain assets; no plants were baked into a terrain sheet. Each prop has its own position/footprint. Combat spaces, gates and enemy deployment remain valid. This adds no harvesting, watering, farming income or automatic bonus loot.

## Cleanup and review

Archived 34 superseded root-level runtime PNGs with verified versioned replacements. Archive: `E:\Other Games\Fortcamp\fortcamp-art-archive\prop-audit-20261003`. Manifest and replacement paths: [PROP_CLEANUP_20261003.json](PROP_CLEANUP_20261003.json). Every registered active asset hash was verified unchanged. Pilot style-comparison images, their state partners, original atlases, prepared assets and approved architectural kits remain. This is reversible retirement, not permanent deletion. `--retire-legacy` only moves proven replaced copies and refuses overwrite; it does not delete merely unused sprites.

Audit workflow: build `tools/build_prop_coverage_preview.py`, run `node tools/audit_battle_prop_art.mjs`, then `.venv\Scripts\python.exe tools/audit_prop_sizes.py`. Detailed local measurements and scaled gallery: `staging-terrain/prop-size-audit/audit.json` and `standard-size-gallery.jpg`. `node tools/location_rollout_browser_qa.mjs --size-audit` uses the isolated renderer to check the real cart/well span two columns and render all four gardens; it waits for background image loading before snapshots. Screenshots and computed bounds: `staging-terrain/prop-size-audit/in-game`. Generated media remains local and excluded from public Git. Production and player saves are untouched.

Validation: 140 distinct backend map/prop/mission tests, 37 frontend map/size/wall tests and the frontend build pass. Full 40-seed location routes plus fresh 400-map reachability checks pass. Asset coverage: 249 encounters, 19,603 references, no missing files. General browser checks cover 28 beginner layouts; seven focused rendered scenes check actual large-object spans and all four gardens, with background image loading awaited. Visual references retain their limitations: imported garden art has a shallower viewing angle than an ideal pure overhead set, and the maps implement their own logical layout rather than duplicating the mockup.
