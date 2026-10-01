# Item and race icons

108 item icons and 42 race emblems are installed in `frontend/public/assets/catalogue/items/` and `races/`, respectively. PNGs are 192×192 with transparency. They are original generated game art, not extracted commercial game assets.

Sources are preserved in `staging-ui/equipment-icons-v1/`: `items_batch_001.png` through `003.png` (6 columns × 6 rows), and `races_batch_001.png` (7 columns × 6 rows). Prompts and a browser preview live beside them. Equal cells have no drawn separators. Extraction now isolates complete silhouettes on the transparent source, including artwork that crosses a nominal cell edge, and preserves aspect ratio inside 192px output with padding. Unexpected connected/ambiguous silhouettes stop import for manual review rather than silently clipping art.

`docs/art/equipment_icon_manifest.json` stores permanent IDs, sheet numbers, zero-based cells and filenames. Entries append; existing items never shift when the catalogue grows. Removing an item does not recycle its old cell. Same IDs keep the same file paths. New generations should preserve internal margins, common brushwork, lighting and visual weight while varying each object's design.

From the project root:

```powershell
# Write the next requested prompt and update assignments without generating or paying for anything.
.venv\Scripts\python.exe tools/build_gear_icon_catalogue.py --batch 4
# Race prompts use their own 7×6 layout.
.venv\Scripts\python.exe tools/build_gear_icon_catalogue.py --kind races --batch 2
# Extract an approved sheet into its assigned item IDs.
.venv\Scripts\python.exe tools/build_gear_icon_catalogue.py --batch 4 --extract staging-ui/equipment-icons-v1/items_batch_004.png
```

There are currently no batch 4 items or batch 2 races, so those prompt requests will report no entries until new catalogue entries are added. The extractor refuses all existing target files before writing anything. Deliberate replacement requires preserving the old corresponding files first; never renumber the manifest to repair an image.

Generated media remains outside public Git, as requested. Back up the `frontend/public/assets/catalogue` and source sheets separately; a code-only Git checkout will not contain those images. The tracked manifest, source scripts and prompts/design documentation retain mappings. No new BAT launcher was added.

October 1 crop repair: 43 item icons and 41 race emblems were replaced from their original sheets; 66 good crops were untouched. Stable IDs, mappings and filenames did not change. A generous source crop plus a silhouette mask recovers the full object and removes neighboring fragments. Original live icons, replacement hashes and crop coordinates are preserved in `data/catalogue-crop-audit/backups/` and `repairs.json`. Review contact sheets are `data/catalogue-crop-audit/items_001_after.png` through `003` and `races_001_after.png`. Repaired icons use a new URL cache revision in the equipment/roster UI.

`tools/audit_catalogue_crops.py` audits original source sheets without modifying live images. `--apply` deliberately backs up and replaces the reported faulty grid crops. The report measures the original grid failure; rerunning it after repair still reports the same source crossings, so inspect the current icons/report before applying again. This tool does not generate new artwork or change the source sheets.

Preview: run `tools/build_equipment_preview.py`, then the existing `node tools/serve_board_preview.mjs`; open `http://127.0.0.1:8766/staging-ui/equipment-icons-v1/equipment-preview.html`. This fixture does not touch the player database. `tools/equipment_browser_qa.mjs` uses the same local Chrome debug setup as board QA and checks paging, icon loading, search focus, injured equip/unequip, duplicate stacks and narrow-screen overflow.
