# Overhead furniture and training pack

Installed in dev October 4. One built-in imagegen call produced a 1536x1024 RGBA
atlas with 24 sprites, six columns/four rows. Reference: the approved garden kit's
painted materials. Source, exact prompt and extraction log remain in
`staging-terrain/furniture-training-v1`. Previous training sprites remain intact
in their old folder. Production was not deployed.

| Row | Sprites, left to right |
|---|---|
| 1 | Timber chair, iron chair, stone chair, wicker chair, upholstered chair, tribal chair |
| 2 | Wooden armchair, royal chair, round wooden stool, square wooden stool, training bench, folding camp stool |
| 3 | Straw training dummy, armored training dummy, upright archery target, upright straw archery butt, practice weapon rack, training shield rack |
| 4 | Flat floor target pad, padded sparring post, practice spear bundle, practice sword bundle, archery quiver, training helmet crate |

Chairs show seats and backrest tops. Dummies show helmet/head crowns and arm tops
rather than faces. Upright archery targets show their top edge and supports; the
flat fabric target pad shows rings. This is consistent with the requested overhead
camera rather than artificially presenting an upright target face from above.

Connected-component extraction identified all 24 complete silhouettes. Nearest
detached details are retained; neighboring sprites are masked away. Extracted
images use transparent 384px canvases. Runtime versions live in
`frontend/public/assets/combat-terrain/props/furniture-training-v1`.

The six training IDs replace registered artwork without changing saved identities,
encounter logic or combat footprints. The other eighteen sprites are new library
assets; they are not automatically scattered across authored maps. All twelve
seating assets support the existing limited table tuck, optional docking and
tabletop draw priority. Added props are scenery, with no new training interactions.

Construction profiles set chairs to half a cell visually and stools to 0.35 cell;
the long bench defaults to two cells. Combat profiles are separately alpha-calibrated
and preserve old replacement IDs' footprints. Images are never stretched.

Installer: `tools/install_furniture_training_props.py --atlas <path>`. Then rebuild
shared bounds with `tools/measure_construction_props.py` and the scale gallery with
`python -m tools.audit_construction_props`. Current dimensions are listed in
[the construction audit](CONSTRUCTION_PROP_SIZE_AUDIT.md).

Validation includes all source silhouettes, installed measurements, shared battle
profile equality, all 181 frontend tests, 24 backend tests, build, and real browser
placement/docking checks. Atlas and editor screenshots were visually inspected.
Generated media is local and excluded from public Git; manifests/code/docs are tracked.
