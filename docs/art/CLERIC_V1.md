# Cleric icons and presentation — October 7, 2026

Generated with the native imagegen tool in one eight-icon atlas. No external
LinkAPI helper was used. Original local source: `staging-ui/cleric-v1/atlas.png`.
Runtime icons: `frontend/public/assets/cleric-v1/`, with `mend`, `heal`,
`sanctuary`, `rest`, `smite`, `exorcist`, `holy_light`, `battle_priest` PNGs.
These generated asset directories follow the repository's existing ignored-art
policy; include the runtime assets when preparing a release copy.

The equal 4-column × 2-row cells were cropped at rounded proportional boundaries
and resized to 256×256 with Pillow LANCZOS. Icons remain square, with charcoal
backgrounds and coherent gold/emerald painterly art. No terrain is included.

## Generation prompt

Create a single square 4 by 2 asset atlas, exactly eight equal square cells, no
gutters, no text, no lettering, no border around entire atlas. Polished
hand-painted fantasy RPG ability icon art for Fortcamp, cohesive warm gold ivory
emerald teal palette, dark charcoal backgrounds, highly legible strong silhouettes
at small 80 pixel sizes, ornate restrained metal details, square ability icons.
Reading order top row: Mend (gentle luminous green-gold hands tending a small
wound); Heal (radiant golden chalice overflowing healing light); Sanctuary
(top-down circular consecrated stone rune with soft emerald restoration glow);
Rest (kneeling robed priest resting beside a staff with dim candle). Bottom row:
Smite (steel mace enveloped in a bright holy golden flame); Exorcist (holy seal
banishing a ghostly skull); Holy Light (brilliant golden cross of light extending
four cardinal rays, symmetrical top-down); Battle Priest (armored gauntlet
clutching a luminous sacred mace and prayer beads). Keep every icon composition
centered wholly within its own exact equal cell, no artwork crossing cell borders.
Consistent painterly game art, no UI labels, no photorealism, not a mockup.

## Effects and QA

Rest, Smite and Regeneration use the new icons for status presentation. Healing
and holy hits reuse existing painted restoration/force assets; Holy Light adds a
brief animated golden cross with reduced-motion support and automatic cleanup.
Physical and Smite damage feedback share the original attack packet so numbers
arrive on contact. Existing cast/guard sounds are reused. Dedicated Cleric sound
design and a more elaborate Sanctuary visual remain future polish.

`tools/build_mage_preview.py` builds the shared isolated fixture;
`tools/cleric_browser_qa.mjs` checks the Cleric states through Chrome CDP.
Screenshots: `staging-ui/cleric-v1/holy-preview.png` and `holy-impact.png`.
