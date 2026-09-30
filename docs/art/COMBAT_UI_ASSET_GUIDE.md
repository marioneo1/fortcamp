# Combat UI Asset Guide

The approved extraction masters are four independently cropped rows. Their
heights may differ. Each row contains four equal-width assets from left to
right. Runtime assets live in `frontend/public/assets/combat-ui`.

Regenerate the individual files without changing their stable names:

```powershell
.\.venv\Scripts\python.exe tools\extract_combat_ui_rows.py `
  staging-ui\top_crop.png staging-ui\2nd_row_from_top_crop.png `
  staging-ui\2nd_row_from_bottom_crop.png staging-ui\bottom_crop.png `
  frontend\public\assets\combat-ui
```

The original `staging-ui/combat_ui_sheet_v1.png` remains archived as the
generation source. It is not the extraction master because artwork crossed
its nominal row boundaries.

The extractor uses a four-column, four-row layout:

1. Attack, Subdue, Throw, Move
2. Guard, Skill, Interact, Exit
3. Hostile target, Throw target, Friendly target, Reachable tile
4. Normal frame, Active frame, Boss frame, Unconscious frame

The row extractor divides each supplied row independently, trims transparent
padding, removes microscopic disconnected crop flecks, and derives 64px
cursor files from Attack, Subdue, and Throw. Existing filenames are
intentional API contracts with the combat CSS.

## Generation prompt

```text
Use case: stylized-concept
Asset type: transparent game UI sprite sheet for a top-down fantasy tactical RPG
Primary request: Create a cohesive 4 by 4 grid containing exactly sixteen separate combat UI assets. Row 1: attack icon (single forward sword), subdue icon (gauntleted fist with a small sleep star), throw icon (small stone following a curved motion arc), movement icon (boot with directional arrow). Row 2: guard icon (shield), skill icon (small magical burst), interact icon (open hand), exit icon (doorway with outward arrow). Row 3: hostile target reticle in red, throwable target reticle in amber, friendly selection reticle in teal, reachable-tile marker in pale green. Row 4: circular normal character portrait frame, circular active-turn character portrait frame with restrained gold glow, circular boss portrait frame with a crown integrated into the top edge, circular unconscious-unit portrait frame with a subdued gray-blue treatment.
Style/medium: polished hand-painted fantasy game UI, clean readable silhouettes, slightly weathered dark iron and warm bronze, subtle leather details, restrained highlights, consistent rendering and line weight across all assets
Composition/framing: exact 4 columns by 4 rows; every asset centered within its own equal square cell; generous identical internal padding; no dividers; no overlaps; no asset touches a cell edge; all circular frames have identical inner opening diameter and outer diameter
Color palette: charcoal iron, warm bronze, parchment ivory, muted crimson, amber, teal, pale green; strong contrast at small sizes
Constraints: transparent background; isolated assets only; no words, letters, numbers, portraits, faces, characters, scenery, shadows extending outside a cell, watermark, or border around the full sheet; each icon must remain legible when reduced to 32 pixels; frame centers must be fully transparent so a portrait can show through
```
