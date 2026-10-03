# Map prop sizing and environment dressing

Implemented in dev, October 3. The audit in [PROP_SIZE_AUDIT.md](PROP_SIZE_AUDIT.md) covers all 106 registered non-modular prop/state sprites across 249 isolated encounter previews. Modular architectural parts retain their existing material-specific joint geometry. Ground art is not a prop. Runtime alias and destroyed/open state resolution comes from the actual frontend resolver, not filename guesses. Prepared assets are counted and retained even when no current map uses them.

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
| Herb planting | The approved camp kit herb planter remains 1x1. The rejected gardening atlas and its raised-bed variants are no longer generated. |

Footprints describe reserved grid space, not exact real-world metres. Some authored objects intentionally represent smaller versions of their standard family; the audit lists observed footprints so these remain reviewable. Existing saved battles retain their authored coordinates and collision rather than expanding a wagon underneath a unit mid-fight. Presentation follows the common calibration; create a new battle to obtain updated occupancy.

`location_maps.prop` supplies standard footprints to newly generated scenery/furniture. Existing explicit map footprints still override these defaults. New Old Well scenes use 2x2 wells. New Captive Cart scenes use a 2x2 wagon instead of the former enlarged one-cell obstacle; the wounded courier now lies immediately outside its western side, preserving body pickup access. Closed/open rescue cages already reserve 2x2. Large objects are drawn once over their footprint, not as repeated PNG tiles.

## Rejected gardening atlas: removed from use

The supplied gardening atlas was rejected after visual review. Its 32 runtime images, original source, extracted gallery and importer have been retired to `E:\Other Games\Fortcamp\fortcamp-art-archive\rejected-garden-20261003`. The garden dressing module is retired too. New garden maps again use the earlier approved `herb_planter` and `wash_tub` props. All other prop size standards remain active. Existing saved battles keep their positions and collision; frontend retired-sprite aliases show approved replacement artwork instead of missing images. The separate `herb_garden_design.png` mockup remains a composition reference.

## Proposed next visual pass (not implemented)

Improve a single herb garden and training yard before rolling out more variants. Separate ground dressing from solid furniture: garden herb patches, irrigation furrows and worn paths; training-yard scuffed sparring areas, archery lanes and straw near targets. Arrange equipment in work/rest clusters and preserve movement space. Ground plants should use a true overhead view with little or no visible front face; keep the established painted style. Produce terrain/ground details separately from prop packs.

Use existing `art_offset` support to place artwork toward cell edges where appropriate, rather than centering every object. Keep physical occupancy and wall boundaries independent of visual placement; large solid objects still reserve their full footprints. Workbench/rack silhouettes can sit against walls, while small tools cluster near the work area. Decorative shifts must not imply passable routes through solid objects. These are proposed composition changes, not new harvesting or training mechanics.

## Cleanup and review

Archived 34 superseded root-level runtime PNGs with verified versioned replacements. Archive: `E:\Other Games\Fortcamp\fortcamp-art-archive\prop-audit-20261003`. Manifest and replacement paths: [PROP_CLEANUP_20261003.json](PROP_CLEANUP_20261003.json). Every registered active asset hash was verified unchanged. Pilot style-comparison images, their state partners, original atlases, prepared assets and approved architectural kits remain. This is reversible retirement, not permanent deletion. `--retire-legacy` only moves proven replaced copies and refuses overwrite; it does not delete merely unused sprites.

Audit workflow: build `tools/build_prop_coverage_preview.py`, run `node tools/audit_battle_prop_art.mjs`, then `.venv\Scripts\python.exe tools/audit_prop_sizes.py`. Detailed local measurements and scaled gallery: `staging-terrain/prop-size-audit/audit.json` and `standard-size-gallery.jpg`. `node tools/location_rollout_browser_qa.mjs --size-audit` uses the isolated renderer to check the real cart/well span two columns and render all four gardens; it waits for background image loading before snapshots. Screenshots and computed bounds: `staging-terrain/prop-size-audit/in-game`. Generated media remains local and excluded from public Git. Production and player saves are untouched.

Validation: 140 distinct backend map/prop/mission tests, 37 frontend map/size/wall tests and the frontend build pass. Full 40-seed location routes plus fresh 400-map reachability checks pass. Asset coverage: 249 encounters, 19,603 references, no missing files. General browser checks cover 28 beginner layouts; seven focused rendered scenes check actual large-object spans and all four gardens, with background image loading awaited (before rejection of the supplied atlas). Visual references retain their limitations: imported garden art has a shallower viewing angle than an ideal pure overhead set, and the maps implement their own logical layout rather than duplicating the mockup.

Removal validation: 8 backend prop/beginner tests (including 400 generated-map route checks), 6 focused frontend tests and the frontend build pass. Refreshed asset audit: 249 encounters, 19,555 references, no missing files. Seven isolated scenes render with 117 asset URLs loaded and no runtime exceptions; the restored garden screenshot was inspected. Production remains untouched.
