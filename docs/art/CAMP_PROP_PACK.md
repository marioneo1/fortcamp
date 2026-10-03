# Camp prop pack

Implemented in dev, October 3. Built-in imagegen generated one transparent 8x4 atlas using the approved mission-object and location-prop atlases as style references. No portraits, floors or wall pieces were included. Original image: `staging-terrain/camp-props-v1/camp_props_32.png`. Exact generation prompt: `staging-terrain/camp-props-v1/PROMPT.md`. Review sheet: `extracted-gallery.jpg`; measured silhouettes: `extraction.json` in the same folder.

The canvas is 1774x887. The nominal cells are equal, but some silhouettes extend beyond the nominal row boundary. Installation therefore orders the 32 measured connected silhouettes by row/column and masks neighboring components rather than cutting at fixed grid lines. The source-edge check rejects clipped silhouettes; the current pack passes. Output is transparent 384x384 PNG, with proportional fitting and padding. This preserves the source outlines; it does not invent missing detail or guarantee future generations are even.

Reinstall with `.venv\Scripts\python.exe tools\install_camp_props.py`. This updates only its 32 stable IDs in `frontend/src/map-prop-art.json` and `frontend/public/assets/combat-terrain/props/camp-v1`, retaining other libraries. Generated media remains local and is excluded from the public code repo. Keep the source and runtime assets available for local dev/release packaging.

| Row | Contents, left to right |
| --- | --- |
| 1 | Straw dummy, armored dummy, round archery target, hay archery target, practice weapon rack, training shield rack, arrows, war drum. |
| 2 | Sleeping bag, straw bed, canvas cot, wooden bed, stone bed, luxurious bed, tribal hide bed, reed mat. |
| 3 | Cooking pot, food preparation table, grain sacks, water trough, wash tub, mess bench, herb planter, village well. |
| 4 | Loaded ballista, empty ballista, oil cauldron, tipped cauldron, ballista bolts, dropped purse, blanket chest, trophy pole. |

Current maps use a subset. Luxury/stone/wood beds and siege cauldron states are available for later places. Active camp beds occupy 1x2 tiles; ballistas 2x2. Siege props are not usable weapons yet. Future operation needs crew access, aim/direction, ammunition, friendly-fire rules and appropriate fixed damage budgets; pouring oil also needs elevated mounting, a gate approach and a limited hazard duration. Ordinary training props are obstacles/scenery, not a second base-training system.

For review, run `tools/build_prop_coverage_preview.py`, the existing preview server, then `node tools/location_rollout_browser_qa.mjs --beginner-sites` or `--command-camps` with the isolated Chrome session described by that script. Screenshots are in `staging-terrain/beginner-locations-v1` and `command-locations-v1`. These tools never read or write live player saves.
