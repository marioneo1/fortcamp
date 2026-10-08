# Painted combat navigation atlas V1

Generated with the built-in imagegen tool, October 6, 2026. Style reference: `staging-ui/combat-controls-v2/atlas.png` (reference only; no edits to the original).

Source: `staging-ui/combat-navigation-v1/atlas.png`, 1536 by 1024 RGBA. Six equal 512-square cells in three columns/two rows. Runtime: `frontend/public/assets/combat-navigation-v1/`, six 256-square sprites and six 40-square native cursor derivatives. Crop manifest and contact-sheet QA remain in staging. Art preserves aspect ratio and alpha. The importer uses substantial alpha components to avoid isolated neighbouring-cell spill, including a stray fragment on the interaction cell; substantial detached icon pieces remain included.

Reimport:

```powershell
.venv\Scripts\python.exe tools/import_combat_navigation.py staging-ui/combat-navigation-v1/atlas.png
```

Implemented uses: door_open/door_close permanent doorway controls and their cursors; retreat EXIT/HOLD markers; pan four-way map cursor; interact object/menu cursor; hazard route-cost overlay. Existing pointer/attack/unavailable/loading assets remain in use. The atlas is UI art, not a world-prop replacement. Generated media follows the repository's existing ignored-asset policy.

## Exact generation prompt

Create ONE production fantasy game command-icon atlas. Reference image is STYLE ONLY: match hand-painted semi-realistic weathered brown leather, dark steel and warm brass/gold bevels, crisp readable silhouettes and restrained highlights. A genuinely TRANSPARENT background, no coloured ground, no panels, no lettering, no grid lines. Uniform 3 columns by 2 rows, SIX EXACTLY EQUAL SQUARE cells, each isolated object centered with generous transparent margins (15% of cell), nothing crosses boundaries. TOP ROW: 1) OPEN DOOR: stout timber door in dark steel/brass frame visibly swung open, small pale mint curved outward arrow, readable doorway opening. 2) CLOSE DOOR: matching door almost shut with prominent brass latch and small warm gold inward curved arrow, visibly distinct from open. 3) RETREAT/EXIT: pair of brown leather boots walking away through a simple stone threshold with bold gold outward arrow, instantly legible retreat. BOTTOM ROW: 4) MAP PAN: four-headed brass compass-like movement arrow with tiny leather centre grip, no closed fist, beautiful readable horizontal and vertical arrows. 5) INTERACT: brown leather gloved open hand reaching gently toward a small brass lever/ring, extended index/thumb, not a Windows white hand, not punching, points upper-left and clean silhouette. 6) HAZARD WARNING: three overlapping small sharp steel caltrops beside a low red-orange flame framed by a broken brass warning triangle, readable danger pictogram. All six painted in one consistent set; no excessive sparks or shadows outside object silhouettes. These are UI sprites, not map props. Use full available sheet with six equal square cells, keep all details inside safe margins.
