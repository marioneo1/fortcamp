# Painted combat controls v2

Generated with the built-in imagegen tool, October 5, 2026. Style references:
`frontend/public/assets/combat-ui/action_attack.png` and `action_subdue.png`.
The six assets share one generation for consistent materials and proportions.

Source: `staging-ui/combat-controls-v2/atlas.png`, actual 1536 x 1024 RGBA.
Layout: three columns, two rows, equal 512 x 512 cells. Source and measured
alpha bounds remain in staging. Runtime assets: `frontend/public/assets/combat-controls-v2/`.

Reimport without paid generation:

```powershell
.venv\Scripts\python.exe tools\import_combat_controls_v2.py staging-ui\combat-controls-v2\atlas.png
```

Extraction uses image-relative cell boundaries, trims transparent padding and
resizes proportionally into 256 px squares and 32 px native cursor versions.
It does not repaint or modify the generated artwork. Hourglass animation and
steel chain links are rendered in code; the hook is painted sprite art.
Generated media is excluded from the public code repository by existing policy.

## Exact generation prompt

Create a production game UI asset atlas, 1536x1024, EXACT uniform 3 columns x 2 rows of six equal 512x512 square cells, no gutters, no visible grid, no text. Each asset centered INSIDE its own square, at least 48 pixel transparent safety margin on EVERY side, absolutely no crossing cell borders. Genuine transparent background. Match provided painted fantasy command icons: hand-painted semi-realistic steel, brown leather, restrained warm gold bevels, detailed readable silhouettes, NOT flat vector, not realistic photo, no square background or UI frames. SIX ASSETS IN EXACT ROW ORDER. Row1 col1: elegant wooden recurve bow with steel arrow angled up-right, restrained red motion accent, recognizably ranged basic attack. Row1 col2: weathered wand with a brilliant violet-blue projectile at its tip angled up-right, recognizably magic basic attack. Row1 col3: natural LEATHER GLOVED pointing index finger cursor, finger points diagonally up-left, ONE clearly extended finger, remaining fingers curled, no gauntlet punching. Row2 col1: ornate bronze and steel small hourglass cursor, upright, bright golden sand, clean silhouette; this will be animated by code, one complete base object no baked motion blur. Row2 col2: bold thick metallic red X cursor with dark steel edge and gold highlights, no circle or background. Row2 col3: forged steel grappling chain hook, THREE visible hooked prongs, dark leather collar at base, hook head points straight to the RIGHT, exactly horizontal so code can rotate it toward the target, no long dangling chain, no background, no magic glow. Keep icon sizes consistent, use each full cell generously but NEVER touch the margins. Reference images are STYLE references only, do not copy the sword or fist subjects. Save the generated atlas to a local file and return its path for installation.

## Target cursor rendering revision

The importer now also derives sword, subdue and throw cursors from their existing
approved native cursor files, preserving their transparent margins and enlarging
them exactly 1.5 times. Bow/magic cursors mirror to upper-left; the hook rotates
135 degrees from its right-facing source. These three occupy 48 px canvases with
42 px content bounds, versus the preceding 32 px / 28 px. Their 256 px command
and animated-effect source art remains unchanged. Reimport applies transformations
from original sources rather than repeatedly transforming the generated cursors.
