# Item and race icons

108 item icons and 42 race emblems are installed in `frontend/public/assets/catalogue/items/` and `races/`, respectively. PNGs are 192×192 with transparency. They are original generated game art, not extracted commercial game assets.

Sources are preserved in `staging-ui/equipment-icons-v1/`: `items_batch_001.png` through `003.png` (6 columns × 6 rows), and `races_batch_001.png` (7 columns × 6 rows). Prompts and a browser preview live beside them. Equal cells have no drawn separators; extraction uses actual source dimensions. The race sheet is resized into square output with aspect-preserving containment rather than stretching faces.

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

Preview: run `tools/build_equipment_preview.py`, then the existing `node tools/serve_board_preview.mjs`; open `http://127.0.0.1:8766/staging-ui/equipment-icons-v1/equipment-preview.html`. This fixture does not touch the player database. `tools/equipment_browser_qa.mjs` uses the same local Chrome debug setup as board QA and checks paging, icon loading, search focus, injured equip/unequip, duplicate stacks and narrow-screen overflow.
