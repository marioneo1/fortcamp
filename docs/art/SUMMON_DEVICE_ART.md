# Summon and device art

October 4, 2026. Generated with the built-in imagegen tool.

Source: `staging-terrain/summons-devices-v1/atlas.png`.
Exact prompt: `staging-terrain/summons-devices-v1/PROMPT.md`.
Style reference: `staging-terrain/furniture-training-v1/atlas.png`.
Requested 2048 square; actual source is 1280 square, with transparency and a 4x4
layout. Do not crop using the requested pixel dimensions. No source overwrite.

Row-major contents:

1. Scrap crossbow turret; repeater turret; guard automaton; repair drone.
2. Bonded wolf; grove sprite; blue wisp; amber wisp.
3. Stone bulwark; wooden guardian; spectral hound; astral guardian.
4. Destroyed scrap turret; broken automaton; rune beacon; component cache.

Status: staged reference, not runtime art. The wolf/spectral glow sits close to
row boundaries, so simple equal-cell extraction needs silhouette review before
installation. There is no claim that all sprites are extracted/normalized yet.

User direction after generation: mobile units should retain character portrait
circles and existing movement/impact animations. Do not install overhead mobile
sprites as their main character presentation. Later generate mobile summon
portraits in coherent portrait packs using the established portrait style.

Stationary devices can use map sprites. Plan coherent packs containing idle,
optional winding/launch preparation, firing, projectile and destroyed artwork.
All states need consistent visible scale and anchor. Current sheet provides only
base designs and two broken designs; it is not a complete animation-state pack.

All future image-generation artwork should use equal cells, complete contained
silhouettes, consistent perspective/light, no drawn separators, retained originals
and stable ordered manifests. Terrain and prop/entity packs remain separate.
