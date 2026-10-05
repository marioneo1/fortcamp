# Fighter disruption art pack

Generated October 5, 2026 with the built-in image generation tool. Style reference:
`staging-ui/combat-presentation-v2/job-icons-01.png` (style only).

Source: `staging-ui/combat-fighter-v3/fighter-atlas.png`, actual 1536 × 1024,
three columns by two rows, equal 512 × 512 source cells. Import with
`.venv\Scripts\python.exe tools\import_fighter_art.py`.
Runtime: `frontend/public/assets/combat-fighter-v3/`.
Three replacement skill icons and End Turn are 128 × 128; chain/impact components
are 256 × 256. Sources are preserved. The original 72-icon pack remains for
other Jobs and old art references. `ability-icons.js` overrides only three stable
Fighter IDs. Effects use brief additive/masked artwork, not permanent ground tiles.

## Exact prompt

Create one compact game UI ability icon atlas, exactly 3 columns by 2 rows, six equal square cells with NO gaps NO separators NO text, entire canvas 1536x1024 landscape. Reference image is ONLY painted fantasy RPG icon style reference: textured rich painterly materials, readable strong silhouettes, deep charcoal backgrounds, warm gold steel details, restrained magical color. Every icon fills its own square with safe 8% inset, nothing crossing cell boundary. Row1 left: iron chain hook whipping out from armored gauntlet, teal motion arc, for damaging pulling attack Chain Snare. Row1 middle: armored warrior boot slamming cracked earth with radial amber shockwave, for leap landing Earthbreaker. Row1 right: golden rallying battle standard surrounded by three small relieved soldier silhouettes, courage dispels purple fear wisps, Hold Together. Row2 left: polished bronze hourglass beside a round shield, quiet silver blue accents, End Turn action. Row2 middle: heavy iron chain and curved hook closeup on dark background, readable tension for Chain Snare effect art. Row2 right: rough concentric golden cracked-earth impact ring viewed from straight above on dark background, Earthbreaker impact art. All six belong to SAME professional painted game icon set, no anime faces, no letters, no frames around icons, no transparent background.
