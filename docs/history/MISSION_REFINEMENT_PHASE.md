# Mission Refinement Phase

## October 4: Combat ability foundation

Implemented versioned snapshots, independent cooldowns/charges, ordered effects and validated conditions using existing combat primitives. Precision Shot/Arc Bolt/Field Care are cooldown pilots; all other existing gear techniques keep individual one-use limits. Polling never starts activations. Legacy battle rules preserved. Removed new-battle twenty-round loss; auto step limit pauses. Twelve Jobs/loadouts/summons remain deferred. Added backend/frontend coverage and isolated browser review; all 45 authored gear definitions validated. Auto pathfinding wall stalls in two older maps recorded in backlog. Production and real saves untouched.

## October 4: Starting Job and skill design — proposal only

Inspected current starter equipment, capture formula, combat and design references.
Recorded twelve-Job roster, matching starter gear, eight proposed learnable skills
per Job (three starter/five later), full equipped-gear ability access, and proposed
summon/device/form/control timing and UI. Champion authoring remains deferred.
Updated INDEX and backlog; this is design work, not an implemented feature.
No gameplay code, saves, generated art or production changes; no tests claimed.

## October 4: Adjustable table spacing

Seats now have a saved Table spacing slider: 60% tuck through a 60% seat-size
gap, retaining the nearby table and side. Shared overlap allowance accommodates
the deeper tuck with table draw priority; unrelated collisions still reject.
Fixed selection of visible chair edges and repeated inspector edits after Save.
Full map audit with calibrated toolkit recorded as pending in FEATURE_BACKLOG.
182 frontend and 25 backend tests, build and browser spacing/save/reopen checks
passed with in-memory saves only. Production unchanged.

## October 3: Final male installation and female Troll replacement

Imported ten approved male batch 004 sheets, verified all 600 assets and role fallback, inspected installed montage. Installed user-provided f_troll.png, f_troll_shaman.png and f_troll_chieftain.png as 4×4 regular/magic/special pools, sixteen active images each. Regular IDs 001–016 replaced; 017–020 remain compatibility copies excluded from new selection and Lab browsing. Backed up old sources, pool, manifest, appearance metadata and shared framing; cleared stale replaced-image tags/defaults. Existing personal overrides preserved.

Boss portrait selection now requests special art where available; checked eight female Troll bosses use chieftain pool. Fifteen focused framing/importer/race tests passed; regular pool measured-crop validation has no problems. Lab now 2,072 active images. Per-image appearance analysis/tagging has not been performed for these imports and remains outstanding. No production changes.

## October 3: Final male generation and female-only race rules

Generated ten fresh sheets: Astral Elf/Voidsent/Dark Elf/Foxkin/Fairy magic, Homunculus/Merfolk healer, Automaton worker, roleless Slimefolk/Werewolf. Saved 200 portraits and exact prompts under staging-portraits/MALE_BATCH_004.md; all files decode at 1254×1254 and grid evidence recorded. Inspected outputs and documented edge/face/anatomy concerns. New sheets remain staged.

Skipped Banshee/Dryad males at user request and enforced female-only new generic recruits and contract combat enemies through a shared race gender rule; other profile restrictions retained. Existing saved identities unaffected. Installed the previously approved Aasimar male healer sheet, verified all sixty assets and role fallback; Lab now 1,844 portraits. Fourteen focused tests passed covering race generation, portrait framing and importer behavior. No production changes.

## October 3: Approved male batches 002 and 003 consumed

Imported all sixteen approved race sheets into dev through the stable append-only importer. Twenty IDs per pool, separate original images, square 768px full and 192px thumbs; canonical sources copied into portraits and staging retained. Verified all 960 assets decode, runtime exact/alternate role fallback, and all 320 additions in Portrait Lab (1,824 total). Inspected installed montage at data/portrait_audit/male_batch_002_003_install/installed.jpg. Existing identities and production unchanged. Recorded user interest in a selective female quality pass after male rollout.

## October 3: Third common-role male batch staged

Generated eight fresh sheets using the full approved production male template and specific race anatomy: Revenant/Vampire/Ogre/Troll melee, Alien ranged, Undead/Manaforged/Dreamkin magic. Saved all images and exact prompts under staging-portraits/MALE_BATCH_003.md. All eight decode at 1254×1254; grid boundary evidence recorded in data/portrait_audit/male_batch_003/manifest.json. Inspected every output and documented recurring Alien structures, edge clearance concerns and preserved humanoid Undead design. No imports, identity rerolls or production changes.

## October 3: Second common-role male batch staged

Generated eight fresh beast-race male sheets using the full production male prompt and explicit species anatomy: Bugbear/Lizardfolk/Minotaur/Dragonkin melee, Harpy/Centaur/Faun/Catfolk ranged. Saved all sheets and exact prompts under staging-portraits with MALE_BATCH_002.md. All eight decode at 1254×1254; 5×4 boundary evidence recorded in data/portrait_audit/male_batch_002/manifest.json. Inspected outputs, with tight horn/ear clearance, ambiguous close-cropped Harpy wings and smaller Centaur faces noted for review. No runtime imports, existing identity changes or production changes.

## October 3: Approved male batch 001 consumed

Following user approval, imported all eight batch 001 male sheets into their matching pools. Copied canonical source sheets into portraits while retaining staging references and exact prompts. Each pool received twenty IDs (001–020) with square full/thumb images and separate uncropped originals. Verified all 480 assets decode at expected preview sizes, runtime role/fallback matching works, and Portrait Lab lists all 160 additions (1,504 total portraits). Inspected installed montage at data/portrait_audit/male_batch_001/installed.jpg. Existing character portrait assignments are preserved; production unchanged.

## October 3: First eight common-role male sheets

Generated eight new 5×4 male race sheets using the built-in image tool, full production male prompt, authoritative style reference and male presentation reference. Saved all requested images and exact prompts in staging-portraits, with batch index and grid/size report. Halfling required a fresh second pass for adult proportions; first attempt retained. Inspected complete outputs; all decode at 1254×1254 with twenty slots. Some face repetition, youthful small-race faces and tight Tiefling horn clearance remain visual-review concerns. No live portraits, character assignments or production assets changed.

## October 3: Approved male Goblin portrait installation

Installed the approved ranged sheet and earlier approved melee style test, twenty images per pool. Preserved staging references and copied canonical sheets into portraits. Verified all 120 full/thumb/original files decode, exact role selection chooses its matching pool, and Portrait Lab lists all forty additions. Inspected the installed thumbnail montage at data/portrait_audit/goblin_male_install/installed.jpg. Existing assigned portraits are not rerolled; production is unchanged.

## October 3: Safe default framing and one male portrait test

Replaced immediate recommended-frame reset with a preview-only Reset to default button. Saving clears the appropriate individual/shared override; cancelling sends no mutation. Browser QA verified reset preview makes zero writes, cancel makes zero writes, and save sends exactly one reset. Eleven framing/importer tests and frontend build passed. Generated a single new male Goblin ranged 5×4 sheet with the built-in image tool, approved art reference and male presentation reference. Saved image/prompt in staging-portraits; not imported. Some narrower jaws remain a visual-review concern before further male generations.

## October 3: Refreshed portrait cache and retained geometry

Checked the five reported Aasimar healer images: current square full/thumb files have no side padding and their resolved default circles remain inside the image. Added file versions to generic portrait URLs without changing canonical IDs or manual frame keys. Existing character normalization and battle views refresh versions too. Retained battle DOM patches reapply image geometry so cached images do not lose computed positioning. Regression tests cover version changes and preserved framing identity.

## October 3: Square portraits and separate originals

Restored square generic previews and square thumbnails for new uploads; recovered all 1,080 uncropped generic cells into separate original folders without changing IDs. Reimported the padded Aasimar sheet as square previews with uncropped originals and a backup. Both editors offer Original/Square source selection and default to Original for manual editing; source choice persists with framing. Automatic recommendations remain inside square bounds. Ten framing/importer tests and frontend build passed. Browser QA confirmed original-source selection and saved source-aware frames with no script errors.

## October 3: Portrait framing and Portrait Lab

Added a saved per-character circle editor and searchable dev art browser for all 1,304 installed generic/Champion portraits. Drag/resize previews preserve image proportions. Library defaults are stored separately from automatic estimates, individual overrides take priority, and production access is explicitly blocked. Updated the Aasimar healer sheet with stable IDs and backups; future imports preserve full rectangular cells with padding. Nine framing/importer tests passed; production frontend build passed. Headless Chrome checked 60-card pagination, Aasimar filtering, editor preview and save payload with no browser errors. Review captures live under data/portrait_audit/lab_preview. Automatic face recommendations are not a guarantee of perfect framing and cannot restore pixels missing from original sources.

## October 3: Roadblocks and military compounds

Implemented the first four mission families from the location review, including all six prisoner-rival/former rank copies. Added four roadblock layouts, four small-post footprints, four compound perimeters and a separate barracks; the same compound plans support timber command/redoubt and rough-stone/metal vanguard sites. Preserved gate mechanics, rank budgets, rewards, active saved maps and production isolation. Existing approved art sufficed. Verified 39 focused backend tests, 20 rendered layout cases and 201-preview/14,615-reference asset audit. Current authored/generic coverage: 31/30 encounter IDs. Remaining specialized sites stay documented as proposals.

## October 3: Map art cleanup

Moved 54 obsolete art/cache targets (about 799.5 MiB logical size) outside dev and compressed the archive, including the earlier rejected polished trials. Permanent deletion was rejected by automatic approval review; originals remain recoverable in fortcamp-art-archive. Active source atlases/user parts and all map templates remain. Verified all 171 registered runtime asset hashes and the complete 145-preview/7,877-reference asset audit. Updated the old installer shortcut to detect the active sources across versions. The cleanup manifest records exact paths and measured allocated-space recovery.

## October 3: Approved buildings expanded into contract settings

Added sixteen thematic chapel/armory/cache/checkpoint templates from the eight existing footprints, plus Salvage Court workshop routing. Current authored coverage is 17 contract encounter IDs; 44 remain generic, including repeated prison ranks. Added independent deterministic dressing choices and distributed small patrols across twin buildings. Battle Lab derives four named seeds per setting from the actual generator. Material art, collision rules, objectives, budgets, rewards, production and saves remain unchanged. Reviewed actual renderer screenshots across new settings; remaining specialized sites and proposed batches are documented in AUTHORED_BATTLE_LOCATIONS.md and the generated BATTLE_LOCATION_AUDIT.md.

Validation: 35 focused backend tests; 20 furnished browser layout checks (50 prop URLs); full art audit of 145 previews and 7,877 references, no missing files or assignments. Representative enlarged renders reviewed. Tactical difficulty remains subject to player feedback despite preserved rank budgets.

## October 3: Restore previous side-facing T

User preferred the previous map detail 2 T junction. Reverted only the part-17 side-T trial to the earlier part-20/part-19 artwork, reinstalled assets and refreshed their cache version. Part 20 true inward corners and other wall changes remain intact.

## October 3: Part 17 restored specifically for side-facing Ts

Used the user's dedicated three-arm part 17 for map 2's side-facing divider join, with its opposite facing reflected from the same source. The shared installer now applies this choice to every polished map; part 20 remains exclusive to inward corners. Original corner, remaining T and perimeter T rules are retained. Refreshed and reviewed map detail 2; four furnished browser renders, asset loading checks, 32 wall-rendering tests and frontend build pass. No map footprints or collision changes.

## October 3: Authored part 20 for inward polished joins

The user supplied part_20.png and clarified the requested inward corner was in map detail 3, then accepted the shared pass. Replaced the previously adjusted inward-corner artwork with the supplied silhouette at the kit?s common scale, remeasured its horizontal/vertical anchors and fitted its surviving vertical arm. All four mirrored inward-corner facings derive from this source. Side-facing interior Ts also use its corner-shaped arm plus the existing part-19 upright upper continuation, preserving all three connections. These shared rules apply throughout the polished kit, not by mission-specific exceptions. Source overrides are recorded in installed.json and restored on reimport; the original source file is not modified.

Reviewed enlarged map details 2 and 3; four furnished browser renders and asset loading checks pass. Doors, map footprints, collision and logical connection ports remain unchanged. Other material profiles, rough-stone assets, production and saves unchanged. Canonical installer: tools/install_polished_building_kit.py. Artwork still requires normal subjective live review.


## October 3: Apply sample placement rules to every polished-stone map

Used the user?s `staging-terrain/building-toolset-v10-polished/SAMPLE-detail3.png` as a placement/painted-face reference. Polished convex corners (including damaged corners) now use reflected facings instead of quarter-turning horizontal paint into vertical paint: native NE, vertical reflection SE, both reflections SW, horizontal reflection NW. Each facing carries its measured reflected anchor; displayed artwork rotation is separate from the unchanged logical wall rotation. Lower T pieces use a vertical reflection of the native T; crosses preserve the original horizontal/upright painted faces in every orientation.

Concave corners preserve the existing L-shaped collision and arm geometry. Their horizontal and vertical arm faces are reflected locally and remeasured so they meet the outside-facing wall runs around a courtyard; the original joint stays in place. Part 1 horizontal / part 19 upright straight rules remain. The installer exports these variants from existing art and records them in the shared polished geometry profile; renderer selects by piece/orientation and inward-corner offset. There are no map-3-specific placement overrides: every dev map using this polished kit follows the same rules. Door/gate placements, furniture, layouts, interaction edges and movement/sight rules remain unchanged. Rough stone, timber, metal, production and saves unchanged.

Reviewed the four complete furnished layouts, particularly the annex?s inset join and outer corners. Small painted seams remain subject to live review. Browser checks confirm current assets load; rendering tests verify reflected art does not alter connection ports or logical rotation. Canonical implementation: tools/install_polished_building_kit.py and frontend/src/building-joins.js.


## October 2: Original joints restored; part 19 supplies matching upright runs

Disabled the part 17/18 overrides and restored original part 2 corners, part 3 interior Ts and part 15 perimeter Ts. Part 1 remains the horizontal straight wall. The alpha silhouette of part 19 is installed as a dedicated upright straight: its thickness uses the same scale as native vertical arms, its length fits one full wall span, and it is counter-rotated on export so existing whole-building rotation and face-mirroring rules still work. The renderer selects it for vertical straight runs; collision, movement edges, IDs and connection ports are unchanged. This addresses the painted-face mismatch when joining the vertical arms of parts 2, 3, 4, 14 and 15. The original damaged corner's surviving stem is also fitted to its neighboring run without filling the broken area.

Installer records only the active part 19 override; parts 17/18 remain as inactive source files. Reviewed all four furnished layouts and checked asset loading. Wall rendering tests cover all four orientations and verify unchanged face/port rules. Source and screenshots: staging-terrain/building-toolset-v10-polished. Rough stone, timber, metal, production and saves remain unchanged. Painted joins are still subject to live visual review.


## October 2: User-authored polished T and corner replacements

Installed `staging-terrain/building-toolset-v10-polished/part_17.png` for both centered and perimeter T walls, and `part_18.png` for intact corners. Original atlas remains unchanged. The dedicated polished installer reapplies these overrides, records filenames in installed.json, measures the new horizontal/vertical anchors and fits their stems to the adjoining tile. Existing straight-wall boundary offset is preserved; rotations carry calibrated anchors to each corner and T orientation. Native artwork is retained, without assembled corner overlays. Damaged corner, cross, doors and other pieces remain from the existing kit. Asset cache version changed so refreshed clients load the replacement sprites.

Reviewed enlarged browser captures of all four furnished polished buildings; browser loading/native-junction checks pass. Rough stone, timber, metal, production and saves unchanged. Small painted seams remain subject to live visual review.


## October 2: Complete painted polished-stone kit installed

The active dev `limestone` family now uses one 4x4, 16-piece atlas in `staging-terrain/building-toolset-v10-polished`. References: successful timber/metal sheets, the user?s `question/better style.png`, and a visible diagram of sixteen equal square cells. Full walls, half ends, native corner/T/cross/perimeter-T joints, window, breach, matching open/closed doors and gates, pillar, stairs, damaged corner and brace were generated together. Exact prompt, original atlas, crop bounds and in-game screenshots are preserved beside the source.

`tools/install_polished_building_kit.py` extracts complete alpha components at one shared scale. Door/gate states retain fixed jamb anchors; joint arms are calibrated to the tile axes. Only the straight longitudinal stems beyond corner/T joints are fitted to their adjoining tile boundary; wall thickness and the authored joint are retained. The renderer displays native polished junction art directly rather than assembling overlapping straight-wall bands. This is a painted, partly overhead camera matching existing timber/metal, not the rejected flat plan-view style.

Battle Lab ? Building material tests ? **Polished stone building kit** has four furnished layouts: gatehouse, divided hall, breached annex and twin stores (`material-layout-1` through `material-layout-4`). All sixteen parts occur across the layouts. Doors, gates and collision retain normal interactions. Checked actual browser renders at enlarged scale; automated checks cover asset loading, native joints, reproducible layouts, reachable exits and save isolation. Remaining tiny painted seams and subjective style should be reviewed live; this is not a claim of mathematically seamless artwork.

Retired the unused polished plan-view and boxed-trial selectors, geometry, registry entries and their installation/preview tools. Obsolete polished assets/trials are archived outside the project at `E:/Other Games/Fortcamp/fortcamp-art-archive/polished-trials-20261002` after bulk deletion was rejected by automatic approval review. Historical entries below document retired experiments, not current options. The preferred v4 style source remains available as reference. The general material importer delegates polished installation to the current dedicated installer, and the overhead importer handles rough stone only. Rough stone (including its overhead variant), timber, metal, production, credentials and saves are unchanged. Generated media remain local and excluded from Git.


## October 2: Fit candidate stone corners and lengths to actual building boundaries

Restored the template's edge-wall collision convention. Candidate perimeter bands now sit 0.38 tile from cell centre; the generated corner's bend sits at the rotated boundary intersection rather than the tile centre. Concave joins retain their template seating. Full bands span one unit, half bands half a unit; corner arms and perimeter T stems extend 0.88 units to meet the neighbouring boundary/divider ports. Centre T/cross arms reach half-unit ports. Dedicated authored corner/T/cross centres remain intact. Only outer arms use uncapped cropped sections of the matching straight/vertical material from the SAME generation; sections repeat at unchanged pixel scale. No image stretching, foreign wall art, centre patches, synthetic overlapping junction bands or extra posts. Added a separate perimeter-T export. Sprites use shared 1024px canvases and port-based anchors.

Reinstallation now calls tools/fit_boxed_wall_ports.py automatically from tools/install_boxed_wall_trial.py; raw recovery is internal, so reimport does not undo calibration. The frontend's native connection ports use these exact arm lengths. Cache stamp updated. Timber/metal and all old stone profiles remain unchanged. Review screenshots of all four complete buildings show boundary corners and continuous wall runs; subtle texture/stone-course transitions still exist and visual approval is not claimed. Verification: four backend material tests, 31 frontend wall tests including corner-to-band/perimeter-T coincidence, frontend build, and four actual-renderer browser maps with loading assets and no procedural junction connectors. The browser screenshots are in staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production unchanged.

## October 2: Replace isolated wall displays with full building comparisons

User rejected the candidate's isolated pieces/rotated sample rows as insufficient. The same dev material now rebuilds the four established furnished building plans: gatehouse, divided hall, breached annex and twin stores, using material-layout-1 through material-layout-4. Former boxed-walls-1..4 seeds remain aliases. Stone shells, partitions and authored junctions use the new generated six-piece art at one shared scale; all room floors and original furniture remain. Doors/gates deliberately use working timber leaves, because no matching door art was generated; broken sections use traversable gaps with common stone-debris props. Removed unsupported pillar/stair/brace sample decorations rather than pretending they came from the new atlas. Native masonry occupies its cell; enemy spawn candidates are recalculated to avoid occupied walls. No old stone wall textures are mixed into the new shell.

Verified four complete-building renders and reviewed screenshots of every layout; four backend material tests pass, including full-plan/floor/furniture preservation, working gate pairs, reachable exits and save/owner isolation. Generated thickness/span inconsistencies remain visible and are not called solved. Screenshots: staging-terrain/building-toolset-v9-boxed-reference/in-game-1..4.png. Production and normal mission defaults unchanged. This supersedes the previous individual-piece Battle Lab layouts.

## October 2: Boxed six-piece kit available in dev Battle Lab

Installed the v9 candidate additively as **Polished stone (Boxed six-piece trial)** in Building material tests. Four seeds: boxed-walls-1 (individual pieces), boxed-walls-2 (connected runs), boxed-walls-3 (90-degree connected runs), boxed-walls-4 (180-degree connected runs). Six source silhouettes are exported on shared 640px canvases at unchanged scale; measured intersection anchors seat them on the grid. Removed broad soft-alpha background halos using silhouette ownership with a two-pixel fringe. No texture stretching or independent piece rescaling. The new native_pieces profile draws generated corner/T/cross directly, without procedural connectors, cap overlays or face mirroring. Old material profiles/default maps remain unchanged.

This is an in-game comparison, not an even or seamless kit: generated full/T/cross spans are 397/443/412px, and half width is 218px. Gates, breaches and other parts were not generated and are not substituted from another kit. The dedicated test maps use ordinary destructible blocking walls, owner-scoped temporary Battle Lab parties and reachable exits. Verification: three material tests (all seven material families), 30 wall-renderer tests, frontend build and all four isolated browser renders with every candidate asset loading and zero procedural connector elements. Connected-run screenshot inspected; joins remain subject to visual review. Rebuild tool: tools/install_boxed_wall_trial.py. Browser check: tools/boxed_wall_browser_qa.mjs. Media excluded from Git; stored locally in structures/building-v9-boxed and staging-terrain/building-toolset-v9-boxed-reference.

## October 2: Explicit boxed generation reference

Added a visible 3x2 diagram of six equal 512px square cells, with labels, dimensioned full/half silhouettes and matching axes. Saved under staging-terrain/building-toolset-v9-boxed-reference/six_equal_cells_reference.png. Generated all six matching parts together using that guide and the painted style reference. The generator still varied bar spans and added soft alpha halos; source/report preserved, not installed or approved. Future generation references must show clear equal cell boundaries and declared piece dimensions, rather than relying on invisible cell positions. Even boxes do not alone prove compatible asset geometry.

## October 2: Complete material kits must be generated together

Generate each material's straight bands and authored junctions in the SAME atlas generation. Do not generate only junctions and later generate their straight walls separately: this omits essential parts and risks different style/stone scale. Minimum matched trial: full horizontal, half horizontal, full vertical, corner, T and cross. Measure before installation; sharing a generation does not guarantee compatible lengths.

Saved six-piece one-generation limestone candidate in staging-terrain/building-toolset-v8-matched-walls, with exact prompt, geometry reference, intact atlas and complete region crops at unchanged scale. Full horizontal/T solid widths 446/448px; cross 397px; half 235px. Not approved or installed; modular fit and generated shadow alpha need correction/review. Prior materials retained.

## 2026-10-02: Reject patched junction assembly and test dedicated generated pieces

User explicitly rejected the procedural overlap approach. Generated actual complete corner/T/cross artwork in two built-in imagegen calls, referencing a measured silhouette guide and existing painted limestone. Preserved prompts/source outputs and recovered each whole silhouette through alpha-component extraction without warping or patch assembly. Inspection found dimensional inconsistencies in both trials, plus a stepped corner in the second. Saved measured reports and candid rejection notes under staging-terrain/building-toolset-v7-junctions. Neither trial was installed. Updated canonical guidance to require authored junction artwork and explicitly supersede the rejected assembly direction. Game art, runtime, production and saves unchanged; no gameplay tests needed for staging media/docs.

## 2026-10-02: Demonstrate fixed-unit junction construction

User asked to see the promised corner/T/cross assembly and questioned excluding dedicated guided junction artwork. Confirmed dedicated generation is a valid option. Built a standalone staging canvas renderer using existing v6 painted bands, fixed 128px corner arms, 256/128px T and 256px cross spans, with 48px top thickness. Combined top footprints before projecting their shaded sides so internal connections have no dark face crossing their stem. Camera direction remains constant across quarter turns. Matching local top patches cover intersections without raised columns.

Rendered the three shapes on a plain backing and actual map paving; interactive controls provide four rotations, four source textures and grid toggle. Browser QA checked all 16 configurations, loaded terrain and no runtime exceptions, then exported four comparison images. Inspected every rotation. Mortar transitions still show assembly; the preview is not a claim of finished join artwork or combat integration. Original assets/runtime/production/saves unchanged. Stored reproducible tools and updated art guidance; user review pending.

## 2026-10-02: Reject independently sized wall illustrations; restore painted-map priority

User correctly criticized the new polished style and wasteful long L/cross silhouettes, emphasizing full/half grid lengths and consistent band widths. User withdrew strict overhead as the primary target. Preserved all active materials. Created a geometry reference and generated a new painted limestone material sheet referencing the existing v4 wall and actual map cobbles. Inspection/measurement showed it still failed the exact 2:1 ratio (276-281px full vs 171-174px half), despite a closer painted appearance. Explicitly rejected the independent half/join/door rows rather than presenting them as correct.

Recovered the four full material bands and cropped exact 256px full / 128px half strips plus 48px joint patches, all sharing an 84px painted cross-section. No scaling/warping; terminal rim removal gives flush band ends. Saved twelve usable source parts, exact prompt/source, geometry report and an on-paving full/full/half/half preview under staging-terrain/building-toolset-v6-gridfit. Reviewed these visually and verified dimensions. No runtime changes or active asset replacements; door/gate generation and a grid-defined connection prototype remain pending. This is a material-source trial, not a completed corner/gate integration. Media remain excluded from Git.

## 2026-10-02: Install new overhead stones alongside original materials

User requested playable comparisons, keeping old limestone. Added independent limestone_plan and fieldstone_plan profiles, 32 building-v5-topdown sprites and two named Pure overhead entries to dev Battle Lab. Reused all four showcase plans/layout seeds for direct comparisons. Implemented a dedicated additive installer with complete alpha extraction, shared scale, jamb-based state-pair anchors and separate joint/damage/end calibration. Planar sprites rotate without side-face flips or old column overlays. Original registry/geometry entries were programmatically compared with HEAD and confirmed unchanged; original material reinstallation retains additive profiles.

Validation: 132 frontend tests and build, eight backend boundary/showcase tests (including identical comparison footprints/spawns and owner/save isolation), plus all 24 material layouts in the isolated real-renderer browser fixture. Enlarged/direct screenshot review covers new overhead maps; user art approval remains pending. Production and player saves untouched. Generated media remain local and require separate backup.

## 2026-10-02: Separate pure top-down stone generation trial

User requested new pure-overhead polished/rough stone building sets while retaining the current art and leaving wood/metal intact. Generated separate packs with explicit architectural plan-view constraints. The first polished draft still showed upright door fronts, so it was rejected and regenerated with thin top-edge door leaves. Selected polished/rough outputs are 1254px square 4x4 packs, not the requested 2048px. Saved exact prompts and sources in staging-terrain/building-toolset-v5-topdown, recovered all 32 complete silhouettes with existing alpha-component extraction, normalized without warping and created a portable preview gallery. Inspected source sheets and extracted corner/door/gate examples.

Active registry, geometry, building-v4 art, wood/metal, production and saves remain untouched. Candidate visual approval and optional in-map calibration are pending; subtle border shading remains. No game tests were required for staging-only media/docs; extraction verified transparency and 16 populated cells per sheet. Media need separate backup because Git excludes them.

## 2026-10-02: Correct missed limestone face mismatch and corner overlap

User correctly identified that the preceding corner replacement still faced opposite to adjoining wall bands. Inspected the source art and enlarged actual-CSS renders instead of treating alignment tests as visual acceptance. Added a material-specific outward perimeter convention, including T bars and exposed caps. Rejected perpendicular wall inset because it created stepped edges. Extended matching bands 0.035 tile into existing corner columns and clipped the supplied directional image to its foreground column, eliminating protruding source arm tips without introducing separate pillars or changing source images. Preserved logical connections, collision, destruction and saves.

Reviewed all four enlarged limestone directions plus full gatehouse/divided-hall layouts. 131 frontend tests, build, seven targeted backend tests, four-material/four-rotation enlarged QA and all 16 Battle Lab material layouts pass. Production untouched; user visual approval remains pending. Legacy damaged-corner arm shading remains a separate art limitation.

## 2026-10-02: Revert strategic posts and select directional limestone corners

User rejected c8dd76e's strategic pillars. Reverted that pass and inspected the supplied four limestone_wall_* directional corner PNGs, located in frontend/dist. Preserved them in frontend/public plus a staging backup before rebuilding. Calibrated horizontal/vertical arm anchors independently, selected one unrotated image for each logical corner direction and preserved connection ports/translation/destruction. Installer now detects complete optional directional sets without overwriting their source files. Earlier exposed caps, layer order, mirroring and native T remain; rough stone keeps previous corners. 128 frontend tests, build, seven targeted backend checks and all 16 Battle Lab layouts pass. Production/saves unchanged; subjective approval pending.

## 2026-10-02: Foreground stone posts

The latest polished/rough-stone snips showed the exposed branch-end post below the gate covered by its adjoining band and facing the wrong way. Assigned caps an explicit layer above bands but below tokens and matched stone post mirroring to the attached face, including terminal posts. Updated both active/preparation rendering and the enlarged preview. 127 frontend tests, build and 16-layout browser checks pass, with explicit foreground/mirror assertions for both stone divided halls. Also made horizontal bands cover vertical bands at corners and branches, and selected the calibrated dedicated v4 stone T for the left-facing join above the gate. Other orientations retain face-correct assembly. Documented the reusable construction rules; production and saves unchanged.

## 2026-10-02: Finish stone T and cross orientation

Reviewed refreshed polished/rough-stone screenshots. Rotated junction arms still reversed their painted face relative to ordinary divider runs. Normalized each interior arm separately; retained inward-facing perimeter bars and unchanged attachment geometry. Centered half-turn walls/terminal bands share the convention. Added rotation and bottom-perimeter-T regression checks. 124 frontend tests, build, seven targeted backend tests and all 16 actual Battle Lab material layouts pass. No asset generation, backend changes, save changes or production deployment.

## 2026-10-02: Match wall faces to corners

Reviewed the updated metal corner and polished/rough-stone snips. Opposite perimeter bands shared grid rotations, making their painted face inconsistent with the adjoining corners. Added boundary-normal texture mirroring separately from movement geometry, preserved centered divider orientation, reversed concave corner faces and mirrored breach alignment corrections. Replaced metal corner overlap with complementary diagonal texture cuts without stretching the source or generating new art.

Validated 122 frontend tests, frontend build, seven targeted backend boundary/showcase tests, enlarged previews for all materials/rotations and all 16 full Battle Lab layouts. Previous full backend baseline remains 325 tests. Updated canonical art/boundary docs and backlog. Existing dev battles receive the presentation fix on refresh; production and saves untouched. User subjective review remains pending.

## 2026-10-02: New stone art and exposed-end cap rules

User identified repeated baked columns as the underlying source problem and requested regenerated stone plus connection-aware column removal. Built-in image generation produced separate rough-fieldstone/polished-limestone v4 atlases. Preserved sources/exact prompts in staging-terrain/building-toolset-v4 and selected complete extracted silhouettes under stable IDs. Old source/runtime packs remain retained.

Added map-space endpoint matching and an indexed per-render lookup. Stone uses plain bands and separate exposed-end caps; metal clips/reuses its post-free center and retains source posts at exposed ends. Doors count as connections when open or closed, parallel walls do not, removing neighbors exposes caps, and damaged centers remain broken. New stone terminals use half-cell geometry. Excluded resolved texture sections from recursive assembly after visual QA exposed that issue. Physics, saves and production unchanged. 325 backend tests, 117 frontend tests, build and enlarged/full-map browser checks passed; 99 previews / 3,465 references have no missing art. User visual approval and a future stricter overhead door camera pass remain open.

## 2026-10-02: Repair joins using actual screenshot evidence

Reviewed all eight snips in question: rough-stone general/corner alignment, polished-stone corner/T/end/damaged joins and timber/metal T/end/damaged joins. Generated whole silhouettes and short sleeves still failed to establish reliable attachment lengths. Changed intact corners/Ts/crosses to CSS assembly from clipped matching painted straight-wall textures, preserving thickness/proportions. Added directional short-end anchoring, separate damaged-corner calibration and surviving-arm extensions without replacing rubble. Kept old source/runtime art, boundaries, IDs, targeting, destruction and live saves.

Expanded isolated comparison to six types and quarter-turn selection; refreshed all material test screenshots. 109 frontend tests, build, seven targeted backend tests, enlarged four-material checks and all 16 Battle Lab layout checks passed. Previous full backend baseline: 325. Production unchanged. Subjective live approval remains for the user.

## 2026-10-02: Replace rough stone and expose all material parts

User rejected the visible repeated stone caps in the earlier repair. Generated a fresh 16-piece rough-fieldstone atlas using built-in image generation, with continuous overhead masonry and no oversized cap blocks; installed as v3 while retaining v2 originals. Timber broken-wall placement now uses surviving beam alignment. Common reference scale prevents small supporting pieces from being inflated; shared geometry remains reproducible.

Added owner-scoped diagnostic Battle Lab entries for timber, rough stone, polished stone and metal. Each offers four distinct reusable building footprints with fixed seeds, collectively using all 16 parts. The toolbar lists actual pieces present and distinguishes material tests from normal missions. Stairs/braces remain scenery; no new public contracts, rewards, save migration or physics changes. 325 backend tests, 107 frontend tests, build and all 16 material browser tests passed. Coverage expanded to 99 previews / 3,465 references with no missing art. Sources/prompts/screenshots in staging-terrain/building-toolset-v3. Production unchanged.

## 2026-10-02: Repair visible T and corner gaps

User screenshots exposed shortened T stems, unequal corner arms and averaged-axis drift in the new generated structural pack. Added independent corner offsets to the reproducible material installer and synchronized backend/frontend geometry. The renderer now uses clipped sections of each material's existing straight wall beneath connection ends; no raster stretching/regeneration, health/collision changes or save migration. Sleeves rotate with parents and disappear when destroyed. Enlarged comparison screenshots confirm connected timber and forge stone joins; all four materials use the same repair. 106 frontend tests, frontend build, all authored-layout browser checks and enlarged real-CSS checks passed. Production untouched.

## 2026-10-02: Edge walls, T-junctions and four complete material atlases

Replaced full-tile collision for newly authored perimeter walls with bidirectional edge boundaries. Corners keep usable interior floors; centered dividers still occupy their tiles. Both divided buildings now connect their partitions to the shell with T pieces. Movement, melee/ranged sight, gate use, enemy pursuit and panic routes agree on boundaries; existing saved battles retain legacy collision. Direct wall-floor clicks move while body context menus remain available.

Built-in image generation produced separate timber, rough stone, polished stone and metal packs, 16 structures each. Sources/prompts/extraction are preserved in staging-terrain/building-toolset-v2; complete silhouettes are fit proportionally, open/closed posts stay anchored, and corner/T offsets are calibrated per material. Old installers preserve/delegate current art. 323 backend tests and 103 frontend tests, build and actual-browser layout/edge-floor checks pass; 83 encounters / 2,169 art references have no missing files. No production or live-save changes.

## 2026-10-02: Mission evidence art and encounter-wide coverage

Generated a twelve-sprite mission-object atlas in the approved overhead style using built-in image_gen. Preserved source/prompt and recovered complete isolated silhouettes; installed selection grows to 55. Added missing satchel/wheel/chart images, dedicated prison wagon/wreck art, distinct armed/spent trap states and stone-wall fallback. Shared frontend art resolution covers existing saved missions and preparation/live battle, while new mission data explicitly assigns evidence/wagon sprites.

Validated 65 isolated encounter setups against the actual resolver: 888 references, no missing images or assignments. Browser QA confirmed visible Captive Cart satchel/wheel/prison wagon, investigation chart, and both defense trap states with working assets and narrow layouts. All 301 backend tests and 103 frontend tests passed; frontend build passed. No production files or live saves touched. Future unused-library art is not claimed as converted.

## 2026-10-02: Three more overhead packs and live map assignments

Generated 36 new sprites across vegetation, defenses/alarm and paired containers using approved overhead props plus terrain palette references. Recovered complete silhouettes and installed 43 selected sprites in versioned runtime folders with a stable registry; original files stay intact. Filled missing Warcamp pine/bramble, replaced alarm placeholder with active/disabled bell art, and aligned objectives/context/log/story labels while retaining legacy alarm_horn IDs and rules. Saved battle presentation remains compatible. Added a manifest-driven audit/install tool and a 43-image ground gallery, plus actual Warcamp loading/state browser checks.

Validation: frontend build and isolated actual-browser checks passed for all 43 gallery sprites, map asset loading, pine/bramble/bell/cage assignments and bell sprite changes. All 301 backend regression tests passed. No live saves or production files changed. Some tall structure sprites still expose frontal faces; further camera polish remains optional rather than hidden as finished work.

## 2026-10-02: Grounded props and overhead pilot

Corrected independent width/height enlargement of legacy painted props to preserve aspect ratio, shortened drop shadows and removed hover glow while retaining the selection outline. Generated one new transparent twelve-object atlas with the terrain sheet as the only style reference; old art was not modified. Connected-silhouette extraction recovered tent/tree crossing nominal cell edges and removed neighboring fragments. Added a comparison across three ground materials and an isolated actual Warcamp preview with old/new toggle. Atlas, exact prompt, extracted sprites and screenshots stay in staging-terrain/overhead-props-v1.

Validation: two catalogue crop tests, frontend production build and real-browser checks passed. Browser checks verify all twelve comparison pairs and three material assets load, real Warcamp toggle changes only the preview art, and legacy enlargement uses automatic height. Palisades remain too frontal for the intended overhead direction; the full production pack is not replaced. No live saves or production files changed.

## 2026-10-02: Starter vendor, contract-priced hires and social UI

Added ten always-available starter gear offers at 4-6 gold with server-side purchases, distinct unequipped copies and prices above resale value. Raised contact-grade base fees and added contract-rank multipliers; planner quotes, analysis and acceptance agree, while browsing preserves contacts. Redesigned prison as list/detail with visible capacity, assigned warden/readiness, stockade warnings and explicit full-cell swaps. Redesigned Conversation with portrait, loyalty, transcript, topic explanations and meal drawer. Retained reading position, topic/drawer selection and bounded session history through polling; guarded duplicate clicks and late responses.

Validation: all 301 backend tests and 101 frontend tests passed; frontend production build passed. Isolated real-browser checks covered rank-priced multiple hires/bodyguards, conversation state and duplicate-click protection, prisoner selection/swap controls, ten starter offers and responsive layouts at 1440/800/430 pixels. Fixtures and screenshot previews are development tools, not launchers. No player databases, credentials or production files changed. Further dialogue authorship, persistent transcripts and multiplayer economy tuning remain separate work.

## 2026-09-30: Continuous fire and soft wood crackle

Changed all authored flame layers to infinite emission with finite particle lifetimes, removing the all-out gaps between bursts. The controller no longer schedules delayed restarts. Generated and installed one 24-second wood-fire loop: subdued dry crackles and embers, without roaring flames. It fades with board visibility and uses the existing Master/Ambient channels; occasional goblin ambience remains separate. Added targeted generation support without replacing preserved originals, and documented the source, processing and playback in docs/audio/WOOD_FIRE_AMBIENCE.md.

Validation: 59 frontend tests and production build passed. A real browser sustained three native emitters for 30 seconds without restarting or reaching the 512-instance cap. One actual audio layer decoded and played through its 24-second wrap, then faded out when its context ended. Screenshot and sampled diagnostics are in staging-ui/effekseer-fire-trial. User listening review remains pending.

## 2026-09-30: Foreground flame tips

Replaced the isolated visible-fire composition with the user's close-camera direction: enlarged, overlapping flames rooted below the frame, showing only their upper tongues. Widened the authored particle growth, extended particle life and shortened its final fade to keep the cropped tips bright. Runtime width and height are independent, seeded ages differ, and slow height variation avoids synchronized border motion. Smoke/embers use broad lower spawn regions above the unseen fire bed. Resize immediately seeds a fresh composition. Preserved the previous project locally and revisioned the binary URL for cache refresh.

Validation: 57 frontend tests, production build and actual board-browser QA passed, including active Effekseer particles, the 512-instance cap, reduced-motion freeze, event switching and narrow layout. Desktop/mobile screenshots are preserved in staging-ui/effekseer-fire-trial. Live Discord visual approval remains separate.

## 2026-09-30: Burning scene, tactical gear, loot and equipment browser

Distributed larger Effekseer fires across the background and paired their positions with rising Pixi smoke and sparks. Added 28 items (108 total), real equipment-granted abilities, explicit scaling/elevation behavior, elemental affinity checks and deterministic Burn/Poison procs. Damage-over-time ticks once per activation, expires and respects nonlethal safety. Added low-tier event gear, nine authored mission caches and five follow-up-only chain relic checks (14% success, 22% critical). Ordinary pools cannot award those relics.

Roster Equipment now provides paged/searchable inventory cards, duplicate stacks, slot/rarity filters, sorting, equipped ownership, named transfers, comparisons and quick equip/unequip. Removed the discarded legacy dropdown construction. Tiered training is labelled Proficiencies; distinctive traits remain Perks. Saved progress and instance IDs stay compatible. Generated and installed 108 item icons and 42 race emblems with stable manifest mappings and preserved original sheets; generated media remains outside public Git. Item icons also appear in aftermath. Backlog and design/pipeline documents record remaining scope.

Validation: 147 backend tests and 57 frontend tests passed; production build passed. Real browser checks covered active bounded Effekseer fire, reduced motion, theme changes, stable board controls, inventory paging, icon loading, skill-search focus, injured equip/unequip, duplicate stacks and narrow-screen overflow. Screenshots are in staging-ui/equipment-icons-v1. Further visual approval and balancing require real play; this pass does not claim all 118 mission pools or every named status mechanic is finished.

Latest visual follow-up (2026-09-30): [actual Effekseer fire trial](../art/EFFEKSEER_FIRE_TRIAL.md) replaces Goblin Pixi flame meshes. The authored effect uses a supplied CC-0 Pierre flame texture, warm tint/alpha blending and a pinned MIT WebGL/WASM runtime. It shares the board canvas/context/clock, supports reduced-motion stills and cleanup, and loads only for Goblin events. One Python rebuild tool was added, no BAT/global installation. Validation: 55 frontend tests, production build and browser checks passed, including real native particles, allocation caps, event switching and clock freeze. Headless CPU submission comparison averaged 0.32 ms without fire and 0.64 ms with fire; live Discord/GPU performance and visual approval remain separate.

This file records the rules for expanding Fortcamp's missions without turning their results into mechanical reports.

## Story rules

- Results should read as short scenes. Use concrete actions, setbacks, decisions, and consequences.
- Keep the useful invented connective moments that make a mission feel lived in.
- Never print internal condition names such as `event race or relic affinity`, rule IDs, score formulas, or hidden team requirements in story text.
- Put exact kills, captures, recovered objects, and combat statistics in the separate tactical report. The scene can use those facts, but it should turn them into narrative rather than list them.
- Appearance is optional context. Do not force a hair, eye, race, weapon, or clothing description into a paragraph merely because metadata exists.
- Content remains SFW. Fork of Chains may be studied for pacing and result structure, but its prose is not copied and unsuitable material is excluded.

## Mission identity

- Ordinary quest NPCs receive stable names generated from the mission seed. Replaying or reopening the same mission preserves those identities; a new mission produces new people.
- Champions and Celestials are authored limited characters. Their identity is persistent and globally unique rather than regenerated per mission.
- Internal unit IDs remain stable so saves and battle rules do not depend on a displayed name.

## Mission forms

The board should mix several forms rather than treating every contract as combat:

- expedition and profession rolls;
- dialogue and negotiation choices with clear information;
- tactical combat;
- rescue, extraction, capture, defense, pursuit, and escape objectives;
- consequence missions that appear on a later board because of an earlier outcome;
- private mission chains belonging to the player who started them.

## Rewards

- Give every mission a reason for its rewards. Logging and mining contracts may provide bulk materials; a prisoner rescue should not produce arbitrary lumber or stone.
- Maintain a useful baseline reward, then add mission-specific discoveries, equipment, perks, recruits, intelligence, or story items.
- Some rewards require behavior rather than a better roll. Capturing a named target alive, recovering evidence, protecting a witness, or leaving an enemy alive can each unlock distinct loot.
- Failure gives little or nothing. Critical failure may also cause injuries or new hostile consequences.
- Event rewards should carry the event's identity through their name, use, perks, or later mission access.

## Prison foundation

Captured unconscious enemies now become persistent prisoner records. Each record keeps the person's generated identity, portrait, race, weapon, capture mission, and whether they are a priority target. A Prison Cell holds four captives securely and accepts one character assignment as its Warden.

Overflow captives enter the temporary stockade with one hour before removal. The allowance belongs to the prisoner: moving them into a cell pauses it, and moving them back resumes the remaining time rather than resetting it. Players can swap prisoners between the cell and stockade or sell any captive for gold. Recruitment, negotiation, release, and ransom remain locked until their rules and costs are authored. Later work should add Warden effects, escape risk, treatment, loyalty, and consequences for holding important prisoners.

## Planned content passes

1. Audit every existing mission for clear stakes, mission form, outcome scenes, sensible baseline rewards, critical requirements, secret routes, and consequence hooks.
2. Build race gameplay identities: meaningful strengths, weaknesses, movement traits, resistances, profession affinities, and rare drawbacks such as loyalty limits. Elements should be added only alongside readable combat interactions and counters.
3. Author Champion acquisition chains around places and conflicts that fit each character's source lore. A Champion can be acquired once, and discovery should result from a memorable route rather than a generic reward roll.
4. Expand prisoner play with recruitment, exchange, ransom, release, and faction consequences.

The proposed goblin diplomacy route belongs in the Champion pass: bringing a goblin chieftain changes an assault into negotiation, opens goblin-only follow-ups, and a disastrous village raid can cause Goblin Slayer to enter the chain. Exact hidden requirements remain concealed until the player's selected party can trigger a clue.

## Current first pass

- Goblin Warcamp and The Captive Cart use generated mission identities and authored tactical aftermath scenes.
- Captured enemies persist in the roster's Prisoners collection.
- Capturing a warcamp chieftain alive unlocks a roll for the Chieftain's Command Horn. Securing the battlefield improves the chance from 20% to 35%.
- Capturing a cartmaster alive unlocks a roll for the Cartmaster's Route Book. Recovering the dispatch satchel improves the chance from 35% to 55%.
- Internal trigger labels no longer appear in result prose; invented character moments remain available.

## Catalog audit completed

- All 116 current templates now carry an audited mission form and a plain-language objective. The forms distinguish recovery, rescue, escort, defense, hunt, containment, investigation, infiltration, and broader operations.
- The mission board shows that form on each card and shows the objective in mission details before party selection.
- Generic event outcomes now use short scene structures appropriate to the mission form. Mission results still include useful invented character moments, but those moments use concrete actions rather than repeating a character's stat or specialty.
- Event material bundles now follow the work performed. Combat sites favor captured provisions and equipment, building sites yield usable structure material, medical and magical sites produce their relevant supplies, and survival expeditions return plausible field resources.
- Event keepsakes use rank-scaled drop chances. Critical caches, critical recruits, Champion encounters, permanent boons, transformations, consequence relics, and consequence perks all make visible seeded rolls rather than being silently guaranteed.
- Story finales still guarantee their permanent world outcome. Their trophy relic and personal perk roll separately, so completing an arc matters even when its rare equipment does not drop.
- Consequence chapters continue to unlock through board-followup rolls, while their special discovery items have their own drop chances.

The encounter architecture and first race gameplay identity pass are now recorded in `MISSION_ENCOUNTER_ARCHITECTURE.md`. Mission purpose is separate from current resolution, intended encounter mode, and combat disclosure. The next implementation pass is the first branching investigation with bodyguard selection, followed by the Private Contracts foundation and authored Champion acquisition chains. Champion chains should replace unrelated random Champion appearances as their authored routes are completed.
# September 30: immediate private leads, combat routing, roster usability

Earned follow-up rolls now create owner-only Private Contracts immediately. Discovery chances stay unchanged; a discovered contract lasts 24 hours from the source mission's completion. Guild Hall visibility gates the shared pool, not a lead the player already earned. Existing unexpired leads are recovered from completed missions without resetting their deadline. Older public consequence copies are moved into private ownership when still unclaimed. Result screens link directly to ready contracts, and the Private Contracts tab shows an available count.

Eleven explicitly hostile contracts now launch tactical battles: Highway Ambush, Bandit Outpost, Goblin Warren, Goblin Chieftain, Goblin Boar Riders, Hobgoblin Vanguard, Bone Patrol, Undead Bone Collectors, Undead Death Knight, The Tithe Convoy, and Court of the Empty Crown. Road, camp, ruin, and court blueprints reserve deployment cells and open routes. Enemy counts and strength scale by rank; racial health, movement, armor, evasion, and resistances apply. Loot remains rolled. A living commander capture plus a secured field and standing party is the critical objective for living factions; undead encounters require a secured field and standing party. Peaceful missions and deserted checkpoints remain roll-driven. These are the first reusable encounter layouts; advanced escort, stealth, and dungeon progression remain separate future passes.

Roster management has search, race/status/type filters, CON/DPS sorting, 24-character pages, independent list scrolling, and separate Overview / Equipment / Appearance tabs. Collection and prisoner browsing sits below the roster. Equipment slots have search fields; appearance drafts persist during redraws and character switches. Polling does not replace focused roster inputs, textareas, or selectors. Browser fixtures exercise 300 characters at desktop and narrow widths.

## September 30: consequential choices, perk mechanics, and layered loot

Four contracts have authored decision scenes, and twelve tactical contracts offer direct attack, a checked ambush, or an Engineer/trained-builder blockade. Optional failure can remove a discovery without ending the contract; other failures end the job or launch a fight. Exceptional investigation failures can bring a stronger named officer with a separately rolled, recovery-dependent trophy. Three timed contracts can transition from critical failure into a playable recovery encounter without prematurely applying terminal rewards or injuries. Bodyguards do not improve primary mission checks. Saved node revisions reject repeated choices.

General and faction caches now select rank-weighted rarities. Eight new exclusive equipment pieces have separate drop checks and never enter broad pools. Fifty-eight core perks have bounded shared mechanics, including equipment-granted effects; all forty-two racial identities disclose their implemented modifiers in the roster. The larger Champion perk catalog remains an authored follow-up, rather than being declared complete.

The standing design requirements and remaining scope are recorded in GAMEPLAY_VISION.md. Night approaches, full stealth, larger deployments, and continuing a decision scene after its battle require later passes. Verification: 138 Python tests, seven JavaScript tests, production frontend build, and browser previews of decisions and racial effects passed.

## September 30: immediate decisions, aftermath layout, and audio controls

Contract acceptance now includes the first saved choice scene in the same response. The client renders it immediately, clears the planner, resets scroll and focuses the first available choice. Closing still preserves server-side progress. Other expeditions completing in the background do not replace an open mission screen.

Aftermath shows the outcome first, gives the story and recovered rewards separate columns, and collapses mechanical checks and loot rolls. Device-local audio controls expose Master, Music, Interface & Mission Sounds, and Battle Effects, plus mute, defaults, and previews. Interface clicks and all four mission outcomes share one channel as requested; playing file-based effects respond immediately to changes.

FEATURE_BACKLOG.md now collects pending UI, performance, and gameplay work. MUSIC_GENERATION_GUIDE.md proposes a warm, restrained fantasy palette without piercing high leads. No paid music generation has occurred. Music playback awaits approved tracks. Equipment/inventory redesign, board art/VFX, and measured responsiveness work remain deferred.

Verification: 139 Python tests and eleven JavaScript tests passed, including acceptance-response and immediate-opening regressions; production frontend build passed. Browser previews verified four audio channels and the aftermath layout. A local Git baseline covers source, tests, docs, and configuration; secrets, player data, generated assets, and builds are excluded. No remote is configured.

## September 30: four guild-board music auditions

At the user's request, generated Lanternlight, Guildhall Shuffle, Roads Waiting, and Mapmaker's Clock as four distinct 120-second instrumental guild-board candidates. Exact requests and immutable originals are retained under staging-music/guild-board-candidates-v1. Listening copies use two-pass integrated-loudness matching around -20 LUFS; true peaks are below -5 dBFS. Each has a separate end-to-start cyclic-crossfade trial. Musical continuity, melody, fatigue, and subjective treble comfort await user listening.

LISTEN.html and listen_music_candidates_windows.bat open the four-track comparison. Only one audition player runs at once; the page provides a common volume control, original repetition, loop trials, and downloads. A hosted copy is linked from Sound settings. No track is selected as gameplay background music yet, and all candidates remain available. The generation utility reuses saved originals and blocks automatic retries of uncertain paid requests.

## September 30: music rotation, transitions and launcher inventory

Approved all four guild tracks, applied gentle three-second endings to playback copies, and preserved source downloads. Generated three additional 120-second location themes: Hearth & Camp, Roads Under Pressure, and Goblin Warcamp. A seven-track listening library replaces the standalone music batch shortcut. Runtime music rotates board tracks and selects base/general/goblinoid battle themes, crossfades over three seconds, unlocks after a user gesture, follows the Master/Music mix, and pauses when hidden. Normal redraws do not restart the music.

WINDOWS_TOOLS.md distinguishes source/dependency checks from actual launcher operation. Start/setup working directory handling was corrected; the development backend uses the project's venv explicitly. Install, stop, crop mutation, GUI launch and public-tunnel actions were not exercised against the live game. Remaining investigation, undead, siege, boss and Starfall prompts are in MUREKA_MUSIC_PROMPTS.md for the user's website subscription; no additional ElevenLabs generations were made after that request.


## September 30: Mureka imports, popup-safe transitions, documentation and GitHub

Installed eight distinct corrected Mureka uploads: Boss 1/2, Defense 1/2, Investigate 1/2, and Undead 1/2. Originals are archived without overwriting; the importer records source hashes, matches loudness and applies gentle fades without network/API requests. The local and hosted listening library now contains 15 tracks, with context filters and loop trials.

Runtime playlists distinguish major bosses, defense, undead, goblins, ordinary combat, and sustained interactive investigations. Short popups leave background music alone. Investigations wait eight seconds, ordinary tab switches 700 ms, and return from encounters five seconds. Three-second crossfades and remembered playback positions prevent abrupt restarts. Tests cover delayed switching, cancellation, return position, fade reversal, and encounter precedence.

Organized design, art, audio, reference, and historical documents under docs. Root DOCUMENTATION.md provides the index; existing portrait and SFX tool-dependent guide locations remain unchanged. Legacy portrait prompts and the original README are preserved. Corrected prison backlog status to reflect implemented selling, swaps, and individual stockade clocks. Regional prompts cover all five actual events, including hostile Starfall impacts.

Validation: all 20 frontend tests and the production build passed; import and library scripts compile. Markdown links and Git history were checked before public publication. The user authorized uploading code to marioneo1/fortcamp; secrets, player data, generated media, and build outputs remain excluded. No new paid generation requests were made.


## September 30: regional playlists and sparse ambience

Imported ten Mureka regional uploads, two per event, with preserved originals and source hashes. Regional browsing now chooses the actual event playlist; base, interactive investigations, and encounter-specific battle music retain precedence. The 25-track listening library includes regional filters.

Generated seven environmental accents (64 requested seconds; API receipts total 640 credits): goblin chatter/camp, ash procession, arcane disturbance, beast call/passage, and damaged alien machinery. Stored originals and exact prompts separately. Runtime uses one clip at a time, delayed initial play, randomized 45?80-second gaps, variant alternation, context fades, hidden-page suspension, missing-file suppression, and a separate Ambient Sounds channel. No continuous ambience bed is used. Auditions are linked in Sound settings. Technical level checks passed; subjective listening review remains necessary.

Validation: 26 frontend tests passed, including ambience gesture/sparsity/alternation, fade cancellation, mute/background behavior, missing-file suppression, regional playlist priority, and settings migration. Production build and source-script compilation passed. Music imports make no API calls; new sound-effect generation was limited to the seven requested accents.

## Guild ambience and proposed board redesign

Generated one 16-second guild chatter clip (API receipt: 160 credits) and wired it exclusively to the ordinary Mission Board. Regional or combat ambience takes precedence; other general guild-music tabs do not play chatter. Preserved the source and reused it after correcting very quiet source gain before loudness normalization; no repeat generation was made. Current ambience pack has eight clips. A separate mission-board plan describes a 24-icon shared sheet, stronger card hierarchy, stable navigation/refresh state, and restrained event animation. No board rebuild or UI image generation occurred before proposal review.


## September 30: painted contract board and stable refreshes

Following user approval, generated one 6x4 transparent painted icon atlas using existing prop and combat UI artwork as style references. Extracted six rank seals, eight mission forms, five event emblems, and five utilities. Removed small disconnected row-border flecks, retained alpha, and normalized without aspect distortion. Original source, exact prompt, extraction preview, and board screenshots are preserved.

Public and private work now share the Contracts destination with inner navigation and saved-expedition access. Cards separate premise, duration/party, role recommendations, possible reward previews, requirements, and explicit inspection. Rank groups retain unlock concealment and collapsed state. Filter controls remain reachable on desktop, active chips remove filters, and unchanged polling keeps the existing DOM and focus. Countdowns update independently. Event headers use generated emblems, regional colors and bounded motion; the old full-screen particle pattern is removed. Hidden-page and reduced-motion rules apply.

Verification: all 33 frontend tests and the production build passed. Local browser checks verified 24 loading assets, no script errors, hidden locked names, focus and collapse retention through refresh, combined filtering, public/private navigation and Inspect buttons, reduced motion, and a one-column 390-pixel layout without overflow. The actual board renderer was used with representative safe fixtures; no live user game state was modified. Discord-specific network performance remains a later measured pass.


## September 30: full-board event atmosphere

The user clarified that leaves, ash, arcane pulses and alien light should appear in the board background, not just its emblem. Added a dedicated canvas behind public/private contract views, with distinct event particles/light motion and stronger banner scenes. Cards and controls remain above it. Motion uses at most 24 draws per second, bounded resolution and particle count, and retains state during polling. Battles, unrelated tabs, general events and hidden pages stop the effect. Reduced motion renders a static frame with no animation loop.

Verification: all 36 frontend tests and production build passed. Browser pixel comparisons confirmed active background motion for all five events and a frozen frame under reduced motion; the ordinary board hides the effect. Existing navigation, focus, filtering, stacking, locked-content and narrow-layout checks still pass. No new image or sound generations were made in this pass.

## 2026-09-30: Painted board background effects

Generated one new transparent 6x4 effects atlas with the built-in image tool and extracted 24 padded PNGs without flattening soft alpha. Public/private regional backgrounds now use painted leaf variation, ash and mist, green/orange embers, rotating cyan/violet glyphs, alien ribbons/motes and an occasional comet. A shared lazy loader caches images and failures once, preserves aspect ratios, and makes the pack available for later weather/skills without implementing those systems now. Existing motion limits, visibility suspension, fallback shapes and reduced-motion still rendering remain. Exact prompt and asset guide are documented; source media stays local and excluded from public Git.

Validation: 38 frontend tests and production build passed; browser checks confirmed all board textures loaded, every event animated, reduced motion stayed static, ordinary boards hid the backdrop, mobile had no overflow, and polling preserved focus/collapse state. Inspected extracted preview and the rendered Beast Tide board.

## 2026-09-30: Pixi particle motion pass

Replaced the board's repeated position formulas with PixiJS Particle Emitter V3 presets using the existing painted textures. Leaves have near/far layers, individual wind/sway and rotation, seeds and petals; camp sparks rise/shrink/fade with low smoke; ash falls over slow expanding mist. Arcane/alien themes retain painted glyph/comet accents with emitter-driven motes/haze. Rain and snow presets are usable in the local preview, without adding combat weather rules. Pixi modules are pinned, lazily bundled (about 88 KB gzip), and governed by one loop with desktop/narrow draw limits, particle caps, visibility suspension and reduced-motion still rendering. The earlier 2D canvas is retained as an initialization fallback. Vite now serves the local fixture preview so npm imports resolve; the old Python command delegates to it. No new art generation, launcher BAT or paid request was required.

Validation: 46 frontend tests (including real emitter finite-position/visibility checks), production build and browser checks passed. Browser verification checks active Pixi rendering, pixel changes for all five events and rain/snow, bounded particles, static reduced motion, ordinary-board hiding, stable controls and narrow layout. Live Discord playtesting remains the user's final visual check.

## 2026-09-30: Full-board atmosphere and shooting-star correction

The initial Pixi pass animated existing smoke/mist art and retained large glyph/comet sprites. In response to the user's visual feedback, smoke and vapor now use four new soft noise-based textures created in code. Arcane Convergence has three continually deforming mesh currents, fireflies and glimmers rather than oversized glyph stamps. Starfall uses a fast light point with a separately positioned tapered trail, replacing the slowly translated/faded comet image. Event particle layers are brighter and denser within an 80-particle overall ceiling; board presets cap at 62. Restrained translucent panel surfaces reveal atmosphere through the board while the canvas stays behind text/controls. Removed the redundant emblem-only CSS scene from active regional backgrounds. Original generated art is preserved and no paid generation was performed.

Validation: 48 frontend tests and production build passed. Browser verification confirms active Pixi effects, three arcane currents with no glyph ornaments, actual shooting-star launch, motion in every event and both weather presets, reduced-motion stills, texture loads, stable controls and no narrow-screen overflow. The fixture preview rebuilds its isolated Vite dependency cache to avoid stale relocated metadata.

## 2026-09-30: Starfall gravity, campfire and arcane circles

Replaced Starfall floating alien cutouts with tiny procedural starlight, falling dust, darker nebula and two gently deforming gravity arcs. Sparse fast shooting stars stay. Goblin background now emphasizes smoke with restrained sparks and three intermittent flame tongues with yellow cores and warm orange edges. Arcane retains its three flowing currents and restores the liked two counter-rotating circles on the far right of the banner, separate from the emblem. Geometry animates continuously; no additional paid image generation, emitter ticker or launcher was added. The fallback removes Starfall cutouts too. Original art stays intact.

Validation: 51 frontend tests, production build and local browser checks passed, including bounded particles, active gravity/flame meshes, visible Arcane circles, shooting-star launch, reduced-motion freezing, stable controls and mobile layout. Live Discord visual review remains separate.

## 2026-09-30: Rank-row repairs and meteor showers

Re-extracted all six rank seals from the user-cleaned 1536 x 268 row, keeping full independent row height and equal horizontal cells. Removed tiny neighboring flecks and normalized uniformly without stretching. Backed up previous assets, kept runtime names, recorded per-icon crop sources and added a rank URL revision for Discord cache refresh. Row-only importer updates no other icons; full atlas extraction honors the corrected row when present. Starfall now emits clusters of 6-10 varied meteors with up to four concurrent flights and quiet gaps. Goblin flames are still Pixi meshes; no Effekseer effect/runtime integration is claimed.

Validation: crop bounds, transparency and source metadata checked for all six ranks; 52 frontend tests, production build and local browser checks passed, including several live shower flights, reduced-motion freezing and no script errors. Live Discord appearance remains separate.


## September 30 ? solo economy and contract progression

Implemented the connected progression pass documented in RESOURCE_PROGRESSION_PROPOSAL.md. Existing saves retain balances and placement, with a pre-migration SQLite backup; Cloth converts to Stone once. Public reservations require no team; private expedition rolls resolve immediately. Added 46 contracts, twelve isolated lower-rank exclusives, personal merchants/faction trade, production, expansion and natural proficiency growth with optional teacher acceleration.

Validation: 160 Python tests, 59 JavaScript tests and production Vite build. Browser checks run in isolated progression_qa.db with bot disabled; Base controls and Trade dialog render without runtime errors. Verified public claim without a planner/team, private assignment, immediate aftermath display, persistent merchant stock, and no page overflow at desktop and 390px mobile widths. Housing, crafting and extended faction quest unlocks remain pending; numeric balance needs real sessions.


## September 30 ? public claim gateway and UI follow-up

The public domain returned 502 for configuration and claim requests while backend port 8000 was healthy; frontend port 5173 had no listener. Restored the Vite frontend and confirmed public configuration returns 200 and unauthenticated claim reaches backend authentication (401). Reproduced authenticated claiming successfully on an isolated copy of the current save; no live player claims were changed during diagnosis.

Replaced the bare claim text with a responsive contract brief, rank seal, objective, rolled reward previews, point allowance/cost and a 24-hour start explanation. Successful reservations offer Assign team now or Keep browsing. One bounded retry handles 502/503/504 only; existing owned reservations are idempotent. Budget/authentication failures are never auto-retried; failed board refresh after saving cannot turn a successful claim into a second reservation attempt.

Validation: 63 frontend tests and production build pass. Browser check covers desktop/mobile layout, private reservation, immediate assignment and aftermath, with no runtime exceptions. QA used a separate save and bot was disabled.


## October 1 ? inventory filter and approach attacks

Roster inventory defaults to hiding equipped instances while leaving spare copies available and equipped slots visible. The checkbox preference persists in browser storage per guild/player, shared between that player's character inventories. Opting out reveals ownership and transfer controls; inaccessible storage falls back safely to the default.

Used Attack/Subdue/Skill/Throw and completed activations return targeting to Move; deliberate carry-to-throw remains available. Targets inside movement plus attack range have server-generated approach previews with path costs and destination-based accuracy. Hover highlights the path; selecting the target offers an explicit Move & Attack/Subdue/Skill confirmation. In-range actions remain direct. Destructible terrain uses the same approach system. The server revalidates terrain costs, occupancy, climb limits, line of sight and the original uncommitted movement budget before moving and using the action. Invalid approaches do not reposition a unit. Walking and impact animations run sequentially; delayed attack effects no longer override the walking transform before their start.

Validation: 168 Python tests (including eight approach cases), 67 frontend tests, production build. Browser QA in a separate save confirms spare visibility, persisted opt-out after reload, two-tile hover preview, explicit approach command over HTTP, movement before impact and return to Move. Walking transform progresses between sampled frames; no runtime exceptions. No live player inventory/battle was altered during QA.

## October 1: movement and redraw performance

Repeated battle clicks replaced the entire modal contents, discarding the map, decoded portrait elements and active animations. Requests also ignored movement input while an earlier move was pending. Battle and defense preparation now reconcile existing keyed elements; visible roster cards, collections, base cells/buildings and idle portraits retain their elements too. Resource counters update in place and regional theme classes only change when needed. Polling keeps data current but defers hidden Base/Roster redraws, including while combat or a decision is open.

Rapid movement keeps one latest pending destination, scoped to the same mission, actor and round. It does not queue attacks or moves across activations. Retargeted walking starts from the token's actual displayed position. Finished effects release their animation objects; delayed cancellation of an older animation cannot clear a replacement's state. Closing a battle discards pending movement and ignores late responses.

Validation: 73 frontend tests and production build pass. Isolated browser checks with 120 ms simulated latency verify only first/latest movement commands are sent, final position is correct, viewport/cells/tokens retain identity, animation objects release, hidden panels receive zero mutations during a changed-save poll, roster collection state persists and base selections retain tiles/buildings/portraits. Existing move-and-attack confirmation, walking-before-impact, inventory preference and return-to-Move checks pass without runtime exceptions. No backend rules or live player saves were changed.

Local headless Chrome with software rendering, same map and 2.2-second repeated-click workload: observed 128 ms long task disappears; frame interval p95 changes from 200.2 ms to 16.8 ms and maximum from 216.8 ms to 66.7 ms. Map identity is retained. Request p95 remains about 25 ms. These are local samples, not a guarantee of Discord frame rate or elimination of network delay; larger-map/device profiling remains in the backlog.

## October 1: immediate movement response

Follow-up user testing found that retaining map elements removed frame drops but movement still waited for request acknowledgements. The server now exports a compact parent/cost tree for reachable tiles. Each valid movement click immediately previews the destination and starts or redirects walking from the actual displayed position, using only that validated tree. Preview movement uses constant-speed interpolation rather than restarting an eased acceleration after each click. Earlier acknowledgements cannot undo a newer queued destination. Commands remain serialized, only the newest pending move is sent, and the server still validates all movement. Failed requests discard queued movement and reload the authoritative position. No client preview changes server gameplay state or rolls.

Validation: 169 backend tests, 77 frontend tests and production build pass. Isolated browser QA with 400 ms simulated latency confirms an active walking animation toward the fourth clicked destination before the first response, no rollback on the older acknowledgement, first/latest commands only, correct final server position, and recovery after an intentionally failed move. Map/token identity, released animations, hidden-panel deferral, roster/base retention and move-and-attack sequencing still pass with no runtime exceptions. Repeated-click profiling retains a 16.8 ms p95 frame interval and no long tasks in the local software-rendered sample; this is not a Discord frame-rate guarantee.

## October 1: friend trial, opt-in registration and Base cleanup

Reset the sole saved player, Grimm, and 168 owned contracts after a consistent local SQLite backup; shared contracts/guild configuration and all art were preserved. Added a targeted local reset tool. Set safe .env defaults for Discord authentication, disabled debug and normal time scale; cleared the single test-guild command-sync restriction. Credentials and tunnel settings are unchanged and remain untracked.

Added per-server /register and /unregister. Registration determines mission pool scaling independently of server member count or character creation. Unregister preserves the save, excludes participation in future pools and blocks new contract starts; re-register resumes progress. Legacy accounts are registered once without reactivating deliberately inactive registrations. No privileged member-list intent is required.

The trial runs pinned committed backend code, built frontend, and copied generic/Champion art on existing port 5173. Development uses workspace reload on 8001/5174 with its bot disabled. Stable/dev saves and uploaded portraits are separate and persistent outside release folders. Updating prepares the next release and never replaces a running version or save. Python dependencies remain shared; that limitation is documented. Source/secret/media Git exclusions remain intact.

Contract mutation responses update local lists immediately; outdated overlapping poll responses are discarded and mutation refreshes fetch again after an earlier poll completes. Phase labels tick from absolute timestamps on the live clock, refresh at deadlines, and show a waiting state during the boundary request. Base now has a consistent workshop/map/management layout, searchable blueprints, selected-building controls first, dynamic settlement dimensions, compact building labels, responsive forms and retained map/portrait/control elements.

Validation: 174 backend tests, 80 frontend tests and production build pass. Isolated desktop/mobile browser QA verifies searchable plans, selected building management, no page overflow, phase ticks 59/58/57, immediate reservation removal and assignment opening without runtime exceptions. Registration tests cover opt-in count without a save, save-preserving pause/rejoin, and inactive-preserving migration; profile tests cover forced safe trial settings, distinct stores/ports and release-path containment. Discord guild installation/App Tester setup and actual multiplayer balance remain user-side checks; instructions and official references are in docs/FRIEND_TRIAL.md.

## October 1: independent sibling release copies

Replaced internal-snapshot launch guidance with the user's requested separate development/release directories. New release-copy builder publishes tested committed source to GitHub's release branch using fast-forward-only updates, clones a versioned sibling folder, installs a separate Python environment from a 36-package lock, copies built frontend/runtime media, and keeps an independent untracked env file. Version tags and existing folders cannot be overwritten. The existing dev folder stays on main with its own local saves and bot disabled by its launcher.

Production saves/uploaded portraits live in fortcamp-release-data beside the code folders and are initialized only if absent. Future release versions use that same production data; creating a release cannot replace progress. Launcher verifies its prepared Git commit, rejects edited/unrebuilt code, requires contained data paths, disables debug/auth bypass and uses existing public port 5173. Old snapshot folders are retained as legacy. New create_release_windows.bat and run_release_windows.bat distinguish publishing from running; old stable entry points provide compatibility guidance.

Profile tests cover independent credentials/code/data settings, unsafe version rejection and runtime path containment. docs/FRIEND_TRIAL.md now describes exact folders, Discord installation/App Tester steps, local dev and safe version-to-version switching. Secrets, saves and generated media remain excluded from GitHub.


## October 1 ? onboarding, mission acquisition and catalogue crop repairs

Character creation uses the current race catalogue (limited Celestials excluded), previews real racial combat/mission modifiers, separates standalone Perks from Basic Proficiencies and collapses optional background/portrait inputs. New-game API rejects unknown or limited races. Exactly one roster character grants +10 free-for-all Contract Points per pool, stacks with purchased allowance, and never changes five-point opening waves. Removing/adding recruits does not reset points already spent. Camp hiring UI/API removed; existing recruits are preserved. Workers must be acquired through missions, with later prisoner recruitment/trader encounters tracked separately.

Audited building purposes in docs/design/BUILDING_FUNCTIONAL_AUDIT.md: Watchpost defense, Barracks housing enforcement and Campfire staff bonuses remain absent; functional production/recovery/training/board buildings retained. Corrected storage and workshop descriptions. Loyalty is still partial (combat field and panic threshold only), with progression/disobedience left as a dedicated design pass.

Recovered 43 item and 41 race icons from original alpha silhouettes rather than clipping equal grid cells. Stable paths and assignments retained; 66 good icons untouched. Existing faulty live icons backed up under data/catalogue-crop-audit/backups, with exact coordinates and before/after hashes in repairs.json. Reviewed all four after contact sheets visually. Importer now isolates full silhouettes, refuses ambiguous sheets and preserves overwrite protection. URL cache revision refreshes repaired art in the equipment/roster views. No image generation or paid API calls used.

Validation: 183 backend tests and 81 frontend tests passed; frontend production build passed. Crop tests cover preserving an object crossing a nominal boundary, excluding neighbor pixels, preserving aspect ratio and rejecting merged silhouettes. Solo tests cover phase boundaries, upgrade stacking, post-recruit bonus removal, exhaustion and ledger persistence. Changes are in development; the pinned friend release remains untouched.

## October 1: equipment identities and mission discoveries

Audited the live 124-item baseline rather than the outdated 108-item documentation. Added 56 pieces across all eight slots, bringing the catalogue to 180: 51 weapons, 10 heads, 14 bodies, 11 hands, 9 legs, 12 feet, 18 offhands, 42 accessories and 13 nonequipment items. The live audit lists every item by category, implemented effects and mission/cache sources. Primary categories: 84 stat/capability focused, 30 active techniques, 8 attack enchantments, 38 tactical rules, 7 conditional combat perks and 13 nonequipment items.

Added bounded carrying/throwing/breaching rules, opening Guard, defensive recovery, water/rubble movement, capture gloves, conditional wounded/boss damage, equipment elemental/status protection and one-use survival safeguards. Six old pieces gained real utility. Equipped techniques from weapons and other slots are selectable; authoritative previews and command validation honor the chosen technique. All techniques share one battle charge. Preview calculation with four equipped techniques averaged 4.49 ms over 100 local runs (maximum 4.72 ms); this is a local fixture measurement, not a claim about all maps/devices.

Eighteen new exclusive discoveries retain real independent drop rates: six E-rank reasons to revisit, four other authored mission rewards, five completed-chain armor/utility rewards, two live-capture rewards and a Starfall tomb pendant. New chain rewards roll 4% / 6% critical alongside existing 14% / 22% weapon relics. Second-Chance Button rolls 1% / 2% in the storehouse; Deadstar Orbit Pendant rolls 2% / 4% in the Starfall tomb. Capture checks require a living recovered target and successful mission. All 43 restricted items are excluded from ordinary cache pools.

Generated two new 6×6 transparent icon sheets using the original item atlas as style reference. Recovered all 72 complete silhouettes into stable 192px filenames: 16 missing old item icons and 56 additions. Existing 108 files/assignments stayed unchanged. Preserved originals/prompts, appended manifest entries and source hashes, reviewed the new-equipment contact sheet and installed local runtime art. Generated media remains excluded from public Git.

Objective auto-battle also closes to a valid nonlethal range when a live target must be captured, rather than firing a lethal bow because a longer-range weapon is equipped. If no capture option remains, it holds fire. Manual control and aggressive tactics retain player choice.

Validation: 196 backend tests and 83 frontend tests pass, including new drop misses/wins, chain gates, capture requirements, pool exclusion across ranks/events, bounded rules, nonlethal gloves, shared technique use, survival behavior, climb costs, throwing/breaching, conditional damage and objective auto-capture. Production build passes. Desktop/narrow browser fixture verifies all visible icons load, pagination/search/focus, injured-character equip, quick unequip and duplicate stacks without script errors or horizontal overflow. An additional fixture runs the actual battle renderer: offhand technique selection updates the action, persists across refresh, sends its correct server command ID, and leaves preparation rendering functional. Development updated; pinned friend release untouched. Multiplayer reward pacing still needs trial feedback.

## October 1: browser play and environment isolation

Added browser Discord OAuth and an authenticated server picker alongside the Activity. Picker intersects the user's server snapshot with this instance's live bot guilds; selecting rechecks current membership and game registration. Website and Activity reuse the existing server/user save keys. Header supports changing servers and signing out; development carries a persistent DEV badge. Startup restores cached sessions without new authorization, preserves cache on transient failures and requests prompt=none for already-approved Discord scopes.

OAuth uses a fixed profile origin, signed expiring state tied to an HttpOnly cookie, matching token-exchange redirect and host-only browser-account cookie. The database stores a hash of the opaque account cookie, identity and server/admin snapshot with 12-hour expiration; OAuth access tokens are discarded after callback. Account sessions survive backend reloads. Selection/logout require the exact Origin. Vite now preserves public Host/Origin for OAuth validation.

Game sessions include an audience bound to environment, application and canonical database location. Browser/Activity caches and account-cookie names use that namespace; old unscoped tokens log in again. Found alpha and trial were configured with the same application and signing secret. Made alpha's signing secret independent without editing the release env. Profile launchers guard against concurrent shared application IDs and the dev runner rechecks during execution. A separate Dev application/token is still required for concurrent bots; setup is documented in docs/WEB_PLAY.md.

Release preparation now inherits the existing production env or an explicitly supplied private .env.release. It refuses silently copying alpha/dev credentials into a new release. Source changes and browser origins are configured in alpha; the existing pinned trial copy, production credentials and player saves are unchanged.

Validation: 208 backend tests, 87 frontend tests and production build pass. New tests cover state/cookie expiry and tampering, registered/shared/installed servers, membership removal, logout, persisted accounts after restart, separate guild saves, cross-environment JWT rejection even with shared secrets, duplicate-application guards and production env preservation. Real Vite proxy test verifies forwarded Host/Origin. Browser fixture runs actual frontend startup, picker selection, selected-guild token requests, development labels and narrow layouts without live player traffic. Actual Discord authorization remains untested until portal redirects and the separate dev application are configured; no claim of live end-to-end approval is made.


## October 1: rare critical outcomes with veteran progression

Removed automatic critical success from high totals and natural twenties. Rolled missions and dialogue use independent bounded confirmation with increasing chances for developed teams revisiting easy ranks. Authored criteria remain required. Scene finales use one confirmation rather than accumulating critical opportunities across nodes. Combat bonus objectives remain earned; normal rewards and independent exclusive loot rolls are preserved. See `docs/gameplay/CRITICAL_SUCCESS_BALANCE.md`.


## October 1: critical soft caps and diminishing returns

Replaced the previous hard critical ceilings with soft caps. Extreme E/D/C stat advantages can reach genuine 100%, including an explicit natural-one mastery exception. C requires vastly more advantage. Pure-stat B remains below 50%, A below 10%, S at most 5%; rare A/S reach their useful soft caps sooner. Added precise percentile confirmation and readable two-decimal UI odds. Criteria and independent loot rolls remain unchanged; future special limit-breaking effects remain a separate design pass. See `docs/gameplay/CRITICAL_SUCCESS_BALANCE.md` for curves and achievable-vs-long-term limits.


## October 1: loyalty, companion records and combat VFX trial

Implemented once-per-activation loyalty checks, stable tropes/shared independent AI policies, character-specific tastes and first roster conversation/meal-gift UI. Added forward-only service records and eight owned expedition memories, champion-specific behavior/voice override seam, and durable mission-result notice delivery for all completion paths. Dev save inspection found two completed Wolves at the Fence missions and no configured announcement channel; `/fortcamp_setup` remains required in the Dev server. No retrospective announcements were queued.

Native Effekseer 1.70e finite death splash and magic projectile compiled from source projects with procedural textures. Pre-hit token briefly flashes/fades before corpse marker. Existing sounds remain; native WebGL/actual roster browser fixture checks passed without runtime errors, with explicit fallback/reduced-motion behavior. Added docs/INDEX.md and repository AGENTS.md update rules. Future relationships, rivalries, awards and handbook remain documented design stages.

Validation: 224 backend tests and 92 frontend tests passed; production build passed. Isolated real-browser QA confirmed native Effekseer rendering mode, two effect events, idle cleanup, actual Conversation tab and food discovery, without runtime errors. Discord delivery was tested with mocks; live Dev channel setup is still required. Existing saves keep explicit loyalty and completed historical results; new counters do not backfill old encounters.

## Contract and roster QoL pass (2026-10-01)

Implemented outside-click contract dismissal, equipped gear effects, saved default-visible spare gear details, stat formula and readable perk help, separate Service Record tab, spoiler-aware server reward previews, and responsive Fit map with manual zoom. Browser fixtures use mocked APIs and no saves. Checked full maps at 1440?1000, 1280?720 and 800?700, plus actual detail preference, keyboard tooltips and backdrop dismissal. 226 backend/94 frontend tests and production build pass. Alpha/dev only; live Discord caching and release deployment were not exercised.

### Victory and equipment presentation follow-up

Fixed the camera grid cascade that wrapped zoom-in into a stretched row. Equipped effects now render directly instead of inside a disclosure. Objective completion uses a wide centered map overlay and a minimized finish bar during optional pursuit. Existing backend victory and extraction rules remain intact. 94 frontend tests and production build pass; mocked-API browser checks cover equal camera widths, visible equipped effects while spare details are hidden, centered banner and continue/reopen/minimize flow.

### Map wheel zoom and prison design

Added fine exponential wheel zoom centered on the pointer without a battle rerender. Documented the current prison gaps and proposed recruitment loop separately from live mechanics. Frontend unit tests, build and isolated browser wheel/control checks validate this UI pass.

## Prisoner allegiance first pass

Implemented fixed capture/migration profiles, eight personal requests, warden INT sessions shared across prisoners, once-only payment and recruitment, owner-only allegiance missions with linked success credit, and prisoner conversation UI. Initial boss pacing distinguishes negotiation from agreements and adds proof after payment for B/A/S bosses. Legacy NPC records use authored baselines because no original attribute snapshots exist. Rescue templates scale enemy strength but reuse the wagon map; temporary factions and deeper individual loyalty missions remain deferred. Validation: 235 backend tests, 95 frontend tests, production build and isolated browser conversation/payment/recruitment checks. No release saves changed.

## October 1, 2026 - Prisoner UI standardization

Agreement fulfillment and sales now use a themed in-game confirmation with exact costs and consequences. Prisoner cards have remembered conversation/profile tabs, readable terms, a warden resistance meter and separate custody actions. The shared confirmation also covers abandoning a reserved contract. Frontend build and 95 tests passed; browser fixture verifies cancellation, recruitment and tab preservation without altering live saves.

## October 1, 2026 - Base and inventory workspace pass

Reorganized Base into five task sections and moved prisoners into their own Base workspace with a Roster shortcut. Settlement has a facility browser, construction sidebar and explicit staffing controls. Development displays separate expansion, allowance and blueprint cards. Roster now separates Characters, Inventory and Collections. Non-wearable manuals/materials no longer enter Equipment; Inventory supports confirmed quantity sales of unequipped instances with server prices and replay/ownership checks. Production trial.2 remains pinned. See ../design/CAMP_INTERFACE.md for rules and verification.
## October 2, 2026 — quieter boards, starter kits, and hired swords (dev)

Reduced natural regional event candidates from 30% to 12%, with a quiet-board check preventing consecutive natural events. Added poor starter equipment for selected combat/magic/support perks, with creation preview and unchanged existing saves.

Added a persistent four-contact player-specific mercenary board to the private contract planner. Hires fill required and bodyguard slots, charge on acceptance, impose bounded roll penalties, build trust/discounts, and unlock rank-priced permanent service. Betrayal starts a separate playable road encounter and resumes the original contract when survived. Selective outdoor maps can very rarely reveal a fallen contact or a friendly/hostile arrival. Hostile arrivals fight both sides and must be stopped for victory; deaths remove known contacts immediately. See ../design/MERCENARIES.md for implemented mechanics and limitations. Production remains unchanged.

## October 2 - fixed dev/prod deployment

Renamed the editable workspace to `fortcamp-dev`, prepared the tested production commit in `fortcamp-prod`, and preserved the shared production database, uploads and credentials. Added a fixed-folder production updater with a pre-update SQLite backup, archived previous copies, rollback on build failure and refusal to replace a running host. Debug and authentication bypass remain off in production. See ../FRIEND_TRIAL.md for current paths, launchers and server registration instructions.


## October 2, 2026 ? opening ambush and goblin boss difficulty

Successful ambush approaches now create a three-round shared sleep window before enemy AI runs. Enemy-targeted attack attempts wake the group before accuracy resolution; thrown impacts share the alarm. Positioning and failed validation do not wake enemies. Status tooltips explain the rule and show remaining rounds. Warcamp chief: 72 HP, 3 armor, 12 attack; its escort is tougher as well. B-rank Redoubt chief: 112 HP, 4 armor, 17 attack. These are fixed encounter stats and apply to new battles only; production saves and already-running battles were not modified.

Added behavior tests including a legal two-person ambush victory with ordinary equipment. Existing gear/objective tests now isolate skill targeting and use veteran fixtures for objective-routing checks rather than assuming the old boss is trivial. Release-builder filesystem tests mock the port probe so a running production server does not affect isolated test results. World-outcome clarification: the Empty Hearse flag is currently a personal story completion marker without additional gameplay consequences.

Validation completed: 264 backend tests, 96 frontend tests, frontend production build and Git whitespace checks passed. Changes are in dev; no production deployment or save migration was performed.


## October 2, 2026 ? dedicated capture weapons and coherent starters

Implemented six clear starter roles with server-selected weak kits, matching Basic training and creator previews. Added nine capture weapons, converted three existing restraint tools, removed the ordinary blunt/unarmed and glove Subdue permissions, and made Capture the weapon's basic action. Balanced STR/DEX/INT, wounded HP, control setup and boss resistance drive the preview and deterministic repeated check. Capture failures do no damage or weapon procs; successful restraint creates a recoverable unconscious unit and credits subdue rather than damage or death. Saved battle permissions migrate; captor AI uses capture. Blackwatch Cudgel has a separate 5% killing-blow knockout. Chain Grips now offers support rather than a capture bypass. Two mission-exclusive capture tools retain low independent drop rates, with legitimate chain provenance required for the Starless Lens.

The level/XP/specialization proposal is documented separately from live mechanics in docs/design/CAPTURE_AND_STARTING_ROLES.md. Enemy/player level scaling was not introduced. Existing character equipment, identities and production saves remain untouched. Backend behavioral tests and the isolated actual-browser QA cover capture safety, gear/role choices, display, mobile width and matching training. Validation totals are recorded in the canonical document after the final checks.


October 2 clarification: capture weapons exclusively replace their basic Attack with Subdue. The UI shows Subdue [A], sends the subdue command, and omits Attack previews; the backend rejects Attack for capture weapons. Auto battle uses the same restraint check. Isolated browser QA covers the A shortcut and outgoing command, alongside backend coverage of rejected Attack without damage or movement.
# October 2 — development Battle Lab

Added the isolated in-game battle mission catalogue and approach/outcome tester described in docs/design/BATTLE_LAB.md. All 73 supported mission templates launch using the real engine, including investigation complications and defense preparation. Test sessions never write player/mission records or award rewards. Enlarged Captive Cart wagon and wreck artwork without changing collision routes; cleared old CSS wheels from painted multi-cell props. Validation: 309 backend and 103 frontend tests, frontend build and browser desktop/mobile workflow checks. No production deployment; balance changes remain a separate pass.
# October 2 — focused authored locations

Rebuilt six mission maps using actual shed/repair-yard/cemetery/river-crossing settings. Added reusable pieces, deterministic dressing variants, operable/destroyable gates with AI support, a separate twelve-prop pack and eight-structure pack. Existing terrain reused and original generic layout snapshots preserved. Full backend suite: 314 tests; six-map browser previews and 65-map/1,044-reference art audit passed, plus frontend build/tests. Remaining locations and balance review recorded in docs/design/AUTHORED_BATTLE_LOCATIONS.md. No production deployment.
# October 2 — building variants and door route planning

Dev-only follow-up adds meaningful saved workshop/shed/connected-armory layouts, varying bridge positions and wood/stone deck art, one-third lantern scale and perimeter artwork offsets that survive destruction. Enemy pursuit compares gate actions with breaches; panic escape can open gates. Separate terrain and prop atlases installed; chapel/bell tools prepared without claiming their maps are finished. Original authored map snapshots retained. Validation: 316 backend and 103 frontend tests, build and actual-browser previews. Canonical scope: docs/design/AUTHORED_BATTLE_LOCATIONS.md.
# October 2 — wall CSS correction and named test layouts

User screenshot exposed an offset CSS declaration being overridden by the later global stylesheet. Applied offsets in the actual global sprite rule and added computed-position browser assertions. Added per-encounter named layout seeds to Battle Lab, checked launches against the generator's actual template IDs, exposed preset selection/Custom/New seed behavior and displayed template names in the toolbar. Browser workflow tests launch all three workshop plans, keep each seed on return and retain mobile layout. Dev only; stacked body-marker design is documented as proposed, not implemented.
# October 2 — reusable buildings and matching architectural art

Replaced flipped-shed variation with four independent footprints and expanded workshops to four. Building definitions now use local room unions and an anchor/rotation stamp, separately from map settings; inner joins, explicit doors/breaches and furnishings/spawns travel together. Installed matching timber/fieldstone/limestone/iron structural families (40 pieces). Dedicated overhead door/gate generation replaces frontal drafts; extraction preserves complete silhouettes, paired anchors and calibrated wall joins. Previous building layouts archived, old media preserved, earlier installers keep new aliases. Battle Lab exposes all eight plan seeds. Validation: 318 backend tests, 103 frontend tests, build, browser workflows and 83-encounter/2,169-reference art audit. No production deployment. See docs/design/BUILDING_TEMPLATES.md.
# October 3 — compact locations and lived-in command camps

Added four layouts each for provision stores, fenced farms, herb gardens, purse roads, village wells, supply stops and occupied training grounds; the last serves all six prisoner-proof ranks. Added reusable store/activity-yard geometry, logical landmarks and separate-room enemy staging in twin stores. Existing mission choices, rank budgets and rewards retained.

Generated one transparent 8x4 camp atlas with built-in imagegen and approved map prop references. Installed 32 complete silhouettes, including seven requested beds, training/archery props, food/water supplies, well/herbs/purse, ballista states and oil cauldron states. Full command compounds now have activity-area clutter with reserved gates/spawns and full 1x2/2x2 collision footprints. Ballista remains stored scenery; oil hazards and siege operation are documented proposals. Previous wall materials/media, original small Goblin Warcamp and production unchanged.

Validation: 43 focused backend tests, including existing every-location route/spawn checks and fresh 400-map reachability; 28 beginner plus 20 command-camp browser renders; frontend build; 249-preview/19,555-reference art audit. Visual review corrected accidental wooden outdoor floors and confirmed whole-silhouette cropping. Sources/prompts/review sheets are in staging-terrain/camp-props-v1; canonical references are docs/art/CAMP_PROP_PACK.md and docs/design/AUTHORED_BATTLE_LOCATIONS.md. Coverage: 43 authored, 18 generic encounter IDs. Next: convoy/highway/watch settings.
# October 3 — prop size audit and supplied garden artwork

Paused new map rollout to audit 138 registered non-modular prop/state sprites across 249 preview encounters. Added shared alpha-calibrated size profiles and default footprints, while retaining wall join rules and saved occupancy. New wells and captive wagons reserve 2x2, carts/long furniture two cells, small clutter uses smaller silhouettes. Mature tree canopies span 2x2 visually without expanding trunk collision. Captive courier is outside the new wagon footprint.

Imported the user's 32-object garden atlas with complete-silhouette extraction. Four herb gardens now contain three/four large raised beds and potting/watering/compost areas around clear aisles, using the supplied mockup as reference. Larger beds are explicit size variants. Archived 34 replaced runtime copies outside dev; active images, style comparison files and prepared artwork retained. No new image generation, farming rewards or siege interactions. Canonical: docs/art/PROP_SIZE_STANDARDS.md and PROP_SIZE_AUDIT.md; cleanup manifest PROP_CLEANUP_20261003.json.

Validation: 140 distinct backend tests across map, prop, beginner and mission suites; 37 frontend map/size/wall tests; frontend build; art coverage 249 previews/19,603 references with no missing assets. Twenty-eight general beginner layouts and seven targeted size/garden renders checked in browser; targeted checks verify real cart/well 2-column spans and wait for 145 background-image URLs before capture. Existing saves and production untouched.


## October 3: Rejected gardening atlas retired; environment composition proposal

Removed the supplied 32-sprite garden kit from active runtime art, registry and shared size profiles. Retired its source, extraction outputs, importer and extra dressing module to the external `fortcamp-art-archive/rejected-garden-20261003` archive. Earlier camp-kit herb planters/wash tub are restored in all four garden layouts. Explicit retired-sprite aliases preserve saved encounter positions/occupancy while displaying approved replacements. Other prop standards, approved wall materials and production remain unchanged.

Proposed next pass, not implemented: coherent planting areas and worn paths instead of a checkerboard of dirt; true overhead herb ground detail; scuffed sparring areas and archery lanes; equipment clustered by activity, with visual offsets against walls/edges independent of logical collision. Review one garden and one training yard before generating more variations. Retained the user's separate layout mockup as a composition reference.

Validation: 8 backend tests, including 400-map reachability; 6 focused frontend tests; frontend build. Refreshed 249 encounter previews and 19,555 sprite references with no missing art. Seven isolated scenes rendered, 117 asset URLs loaded, no runtime exceptions; restored garden screenshot inspected. No player saves accessed or modified.


## October 3: First herb-garden and training-yard environment compositions

Implemented layout 1 of Herbs Behind the Wall and the prisoner-proof training
site (A Promise Proven in Battle). A newly generated 4x4 terrain-only atlas adds
overhead medicinal herbs, quiet soil, shallow irrigation, worn paths, scuffed
practice earth, straw and small footprints. Continuous 2x2 ground patches share
image fragments across cells rather than repeating a full texture on each tile.
Ground presentation remains independent of movement material and collision.

Garden plants now grow directly in the soil; a cross-path separates four patches
and a work/rest area uses approved existing equipment. The training yard has a
sparring court, two dummy stations, archery lanes and an equipment/rest corner.
Furniture has deliberate sub-cell visual offsets; approved wall joins are
unchanged. Visual review moved the bench onto clear ground and reduced footprint
texture size. Other three layouts remain for later composition review. No new
harvesting, training actions, loot or combat budgets were added.

Added a narrowly scoped atlas installer and --activity-sites to the existing
renderer QA tool. Fixed a Chrome teardown race in that tool. Source/prompt and
screenshots live in staging-terrain/environment-ground-v1. Canonical reference:
docs/art/ENVIRONMENT_DRESSING_V1.md.

Validation: 9 backend tests, including 400-map reachability, 8 focused frontend
tests and frontend build pass. Both real rendered layouts were inspected; 40
asset URLs load and no runtime exceptions occur. Full coverage: 249 encounters,
19,571 prop references, no missing art. Production and player saves untouched.


## October 3: Overhead garden toolkit and crop-edge props

Created a separate transparent 6x4 overhead garden atlas with the built-in
imagegen tool. Retained complete silhouettes for 24 props and added a separate
connected-rail texture from the full fence's middle section. Native corner,
T/cross, damaged rail and gate art are prepared for future layouts. Current
crop borders use thin continuous rails at cell boundaries with small corner
stakes; these are step-over scenery, not walls or new interactive gates.

The reviewed garden layout now has fencing above its crop ground, potting bench
with adjacent stool/tools, water pump, watering can, scarecrow, compost, potting
soil, drying screen, round table/stool, herb basket, spare pots and an external
wheelbarrow. The training yard gets repair tools, spare target straw, water and
a stool. Furniture uses shared size profiles and deliberate offsets; long
props use rectangular canvases to preserve scale without warping. Other layout
variants and approved building materials are retained. No gardening income,
training actions, gate actions or loot changes were introduced.

Source/prompt/extraction gallery are in staging-terrain/garden-toolkit-v2;
runtime has 25 new sprites. Added a scoped importer. Canonical documentation:
docs/art/GARDEN_TOOLKIT_V2.md. Updated backlog, doc index, authored-location and
prop-size references. Production and saves remain untouched.

Validation: 9 backend tests, including 400-map reachability and low edging
crossings; 9 focused frontend tests and frontend build pass. Two actual-render
layouts inspected, 55 asset URLs loaded, no runtime exceptions. Full coverage:
249 encounters, 19,705 prop references, zero missing art. Shared profiles cover
131 non-modular sprites. Rechecked profile mirrors after long-canvas correction.


## October 3: Activity variations and garden-kit reuse

Extended approved garden and training-yard dressing to all four building
layouts. Annex, divided and deep courtyards have their own planted areas,
paths, practice lanes, equipment and rest stations. Ground art follows actual
building floor unions. Low crop edging remains step-over scenery and does not
remove clear furniture or enemy deployment cells. Approved wall geometry and
first-layout compositions remain unchanged.

Reused suitable props in farm clearings, village well yards, provision/supply
stores and full command, timber-redoubt and vanguard camps. Tools, herbs, stools,
pumps and watering cans fit existing work stations; camp placement respects
reserved routes and full footprints. This affects 36 authored layouts across
nine settings. No farming, pump or training gameplay was added. Fresh battles
receive the dressing; saved encounters, production and player saves are untouched.
Canonical reference: docs/art/GARDEN_TOOLKIT_V2.md.

Validation: 9 backend tests including 400-map reachability; frontend build;
8 activity, 28 beginner and 20 command/camp real browser renders without runtime
exceptions. Visually inspected all six new activity arrangements and representative
farm, well and camp renders. Coverage rebuilt for 249 encounters: 20,330 prop
references, no missing art; 131 shared non-modular size profiles.


## October 3: Highway Ambush authored road layouts

Replaced this D-rank contract's generic road with four named, seed-persistent
16x11 plans: straight cut, descending bend, wooded-ridge fork and passing place.
Added reusable road-lane assembly in backend/road_locations.py, coherent painted
road ground, climbable height-1 banks, short muddy ditches, connecting flank
trails, authored vegetation cover pockets and stolen-supply pull-offs. One
ambusher starts on a bank. Eight reserved party/enemy candidate slots have no
prop overlap; the actual encounter still uses its original three enemies.
Supplies are scenery, not guaranteed loot. Enemy stats, mission choices,
objectives and reward/drop rules remain unchanged. Existing generic fallback
maps and active saved battles remain intact. No new art pack was necessary;
approved textures and shared-size props were reused.

Battle Lab exposes all four named layouts with verified seeds. Added scoped
--road-sites renderer review. Canonical: docs/design/AUTHORED_BATTLE_LOCATIONS.md;
updated index/backlog and runtime coverage audit (44 authored, 17 generic).
Final rendered captures are staged under staging-terrain/road-locations-v1.

Validation: 23 focused road/map/Battle Lab tests passed, including 40-seed routes
to both exits and preview save isolation. After final bank/route refinements,
the three road tests passed again. All four final renderer captures were
visually inspected; 10 ground/prop URLs load with no runtime exceptions. Full
asset coverage checks 253 encounters and 20,441 references with no missing art;
131 non-modular size profiles remain unchanged. Different approaches can change
tactical difficulty despite fixed enemy stats; player balance feedback remains
follow-up work. Production, credentials and player saves were untouched.

Next focused maps: Boar-Rider Patrol (open road/courier fork) and The Tithe Convoy
(guarded tribute-wagon stopping yard). Do not mix terrain and props in any
additional asset packs.


## October 3 ? standalone local portrait tagging

Cloud tagging paused without an API key. Built sibling character-tagger with WD EVA02-Large v3, independent Windows environment, real CUDA/CPU health checks, structured normalization, known pool/catalogue race and gender, SQLite immutable detector runs/manual edit history, resume, JSON/CSV export, local review and searchable attributes. All 2,072 installed portraits processed; main GPU pass took 237 seconds for 2,059 new portraits with 13 pilot records skipped. Full resume skipped all images. Eighteen automated tests, Windows setup launcher and isolated desktop/mobile browser QA passed. Nine Champion and twelve original portraits visually checked with five separate field corrections; no samples marked fully reviewed. Existing game registries, production and character overrides unchanged. Reviewed-data integration and a benchmarked optional visual second pass remain deferred. Canonical: docs/art/LOCAL_PORTRAIT_TAGGER.md; standalone README has setup/configuration/schema details.


## October 3 ? Aasimar healer original crop repair

Trimmed 17 bottom rows from uncropped IDs 011?015 after visual inspection showed separator/next-row contamination. Remaining pixels retained losslessly. Square/thumb image bytes, both appearance registries, shared framing and standalone tagging DB/normalized export verified unchanged by hashes. No tagging run. Image URL versions refreshed via timestamps, backups and before/after captures retained. Canonical: docs/art/PORTRAIT_FRAMING.md.


## October 3: production update packaging

Release updates now include shared portrait framing defaults alongside portrait assets, exclude the obsolete macOS/Linux dev shortcut, and require clean tracked source while leaving unrelated untracked notes alone. Production launch continues to force debug and authentication bypass off; production credentials, player saves and uploads stay separate. The standalone portrait tagging tool remains separate from game runtime metadata.

Validation: 142 frontend checks passed. Full backend run passed 355/356; the remaining special-Goblin portrait test depended on an optional uninstalled male art pool. Isolated that test with both special pools supplied explicitly; production fallback behavior remains unchanged.


## October 3: bush concealment and roadside ambushes

Implemented persistent first sightings for enemies in walkable bush cover. Spot within two tiles with clear sight, or reveal on leaving cover/attacking; bodies are visible. Server views omit unseen units, initiative, targets and animations; direct targeting is rejected. Provisional movement pauses on discovery without spending the main action. Auto/independent party AI uses spotted enemies and searches brush. Two Highway Ambush presets put two escorts in brush with waiting AI; other two presets and rank budgets stay intact. No new art or dependencies. Production remains unchanged. Full stealth, friendly concealment and re-hiding remain deferred. Canonical: docs/design/BUSH_CONCEALMENT.md.

Bush pass validation: 150 targeted backend checks passed; final 56-check command/approach pass includes 11 concealment cases. All 142 frontend checks and build pass. Strong-party auto smoke completes all four road layouts. Player saves and prod unchanged.


## Bush ambush refinement

Supersedes the two-tile proximity reveal: nearby enemies remain concealed until attacking, leaving cover or physical contact with their occupied cell. Names remain absent from initiative. Authored road kill zones, actual reachable attacks, isolated/wounded target preference and a shared spring signal govern ambushers. Two waiting activations maximum, then normal pursuit; hidden last survivors pursue immediately. An unfinished-fight hint covers the case with no visible targets. No extra damage or free attacks. Fatigue is a separate pacing proposal, not implemented. See docs/design/BUSH_CONCEALMENT.md and docs/design/FATIGUE_PACING_PROPOSAL.md.

Refined ambush validation: 70 targeted combat checks; final 20 concealment/road checks; 142 frontend checks and build pass. All four strong-party road auto checks complete. Fatigue simulation confirms S starts at 0s/9s/909s with 200 recovery, versus 0s/18s with 100 recovery in a 30-minute pool. All fatigue changes remain proposals.


## October 3: stamina recovery and reward pacing review

Proposal only: retain the user's 200-point recovery per 30-minute pool as the initial candidate so borrowed S-rank stamina can recover in approximately one pool. Recovery is elapsed-time based, not a reset refill; late deployments cannot guarantee full points at the next boundary. Current ordinary E?B reward scaling does not justify the earlier B20 suggestion on generic payouts alone. Keep B10 as the initial candidate and review whole-party cost, risk, rarity, unique effects and mission-specific rewards before increasing it. Optional healer/exploration/personal-contract recovery unlocks and modest additive improvements are documented, not implemented. Canonical: docs/design/FATIGUE_PACING_PROPOSAL.md. Validation: compared backend/content.py scaling and backend/services.py pool timing; calculated expected independent loot rolls and recovery durations. No runtime, save, drop-table or production changes.


## October 4: expedition stamina (dev)

Implemented 100 maximum stamina, 100 recovery per 30 minutes, E1/D3/C5/B10/A50/S100 deployment costs, and borrowing from at least 1 whole point. Bodyguards and mercenaries pay; saved hiring contacts retain debt. Recovery is computed from timestamps, including offline, without per-character timers or recovery writes. Reservation, base work, Battle Lab and forced debug completion do not spend points; scene/battle transitions within a contract do not recharge. Existing saves start full. Assignment and roster/hiring UI show points, recovery times and borrowing; suggestions omit tired candidates and eligibility returns without reopening the planner. Capacity/recovery quest upgrades remain deferred. Production and live player saves were not touched. Canonical: docs/gameplay/STAMINA.md.

Validation: nine stamina backend tests plus mercenary/private-contract regressions (27 total) passed; 144 frontend checks and build passed. Isolated browser QA passed candidate filtering, suggestions, recovery boundary and desktop/mobile readout sizing. Another 38 backend checks covering stamina, economy, solo onboarding, Battle Lab save isolation and notifications passed. Python compilation and diff whitespace checks passed.


## October 4: square roster and prisoner portrait containers

Fixed rectangular prisoner list/detail and roster Conversation header frames, plus the Conversation companion card at desktop/tablet/mobile sizes. Portrait flex items cannot shrink under long names. The existing framing renderer now receives square containers so image proportions remain intact; original images, square thumbnails, tags and personal framing are untouched. Dev only. Validation: isolated browser measurements at 1440/800/430px verified five affected contexts remain square and a non-square source retains its original aspect ratio; all 144 frontend checks and production build passed.


## October 4: player base construction foundation (dev)

Implemented Base ? Settlement ? Floors, props & walls: searchable installed terrain/prop catalogue, drag floor painting, adjustable/multi-cell/rotatable props, center/edge-snapped wall arms with corners/T/cross/half/gates, automatic exposed posts, broken/open placeholders, selection/moving, undo/redo, zoom, saved layout display and JSON layout export. Authenticated player/server ownership, server validation and revision/CAS conflicts protect persistence. Existing facilities and economy stay functional; decoration is currently free and grants no loot, capacity or defense. Generic geometry/render modules are reusable for a later dev map editor; import, combat adapters, costs/unlocks, functional camp gates/raids and painted wall art remain deferred. Canonical: docs/design/BASE_CONSTRUCTION.md. Validation: 25 backend construction/economy/onboarding checks, all 148 frontend checks, actual browser placement/joins/undo/save/reopen and 1440/800/430px bounds, visually inspected desktop capture, production build. Production and real player saves unchanged by validation.


## October 4: construction interaction and wall asset refinement (dev)

Implemented drag previews with drop-to-commit and outside/Escape/focus-loss
cancellation, reliable R outside text entry, arrow-key prop offsets (Shift fine)
and directional wall anchors, Home centering, full-cell corner arms, and named
horizontal/vertical/post/corner/T/cross/gate assets. Opposite facings have their
own IDs for later painted artwork. Post choice is part of the asset; the separate
post dropdown and half-arm pieces are removed from the library. Legacy saved
walls retain their geometry and can be replaced explicitly. Construction preview
updates use a separate SVG layer, animation-frame coalescing and unchanged-preview
skips; selected-object nudges replace only that SVG, avoiding whole-map rebuilds.
Art generation and functional construction economy/collision remain deferred.
Canonical: docs/design/BASE_CONSTRUCTION.md. Validation: 26 backend regressions,
151 frontend checks, build, actual browser drag/cancel/hotkey/move/undo/save flows,
1440/800/430px bounds, stable scene during 80 pointer updates, stable ground during
selected prop adjustment, and visually reviewed capture. Dev only; no real save
or production changes.


## October 4: simplify player construction wall kit (dev)

Removed T and + junctions from the construction palette and wall-asset selector;
half walls were already absent. Saved junctions retain render/save compatibility
through separate legacy definitions, with rotation disabled. Future agreed kit:
24 selectable variants / 9 generated originals per material, with permitted
mirrors and separately generated horizontal/vertical art. Full-cell corners
remain. Rectangle fill and Remove / Remove floors, mirrored artwork and limiting
straight-wall rotation to its orientation family remain pending. Canonical:
docs/design/BASE_CONSTRUCTION.md. Production and player saves untouched.

Validation: 9 backend construction checks (including old/native retired junction
save/reload and active catalogue filtering), 8 frontend geometry/render checks,
production build and whitespace checks passed.


## October 4: plain-wood atlas and isolated Wall Kit Lab (dev)

Generated one matched 3x3 nine-original timber kit using active painted map art
and an equal-cell diagram; refined the short vertical plain wall in the same
atlas. Extracted relative equal cells, measured alpha/thickness/ports, retained
ends/posts/corner joint while fitting middle grain bands, and installed nine
normalized transparent sprites. All 24 variants use native H/V originals plus
mirrors; bitmap quarter-turns are never used. R stays within straight/gate
orientation families. No half, T or + assets. Added Mission Board debug Wall Kit
Lab with all variants and a connected room, a whole-layout kit dropdown, and no
save writes. Backend access denies production, debug-off and non-admin without
bypass; normal base construction has no trial picker. Combat kits and production
remain untouched. Canonical: docs/art/CONSTRUCTION_PLAIN_WOOD_KIT.md.

Validation: 27 backend construction/economy/onboarding checks, 155 frontend
checks and build; actual browser verifies 44 sample/room walls load nine sprites,
whole-layout switching, mirrored preview, no PUT/save, normal UI separation and
1440/800/430px bounds. Full/100%-zoom room captures visually inspected. Permanent
player wall art, open/broken sprites, rectangle fill/repeated placement and
separate Remove / Remove floors tools remain pending.


## October 4: construction palette and rotation QoL (dev)

Removed opposite-facing duplicate icons/options and collapsed rotated corners
to one Full-length corner entry. Kept direct horizontal/vertical choices and
explicit post positions. R now cycles four orientations H -> V -> opposite H
-> opposite V, selecting separately authored art plus mirrors without rotating
bitmap images. Post positions follow the turn and four turns restore the original.
Added Center [Home] beside Rotate: resets prop offsets or wall anchor to center.
Existing Home key remains. No art, player saves or production changes.


October 4 construction follow-up: 11 wall-library entries cover all 24 orientations;
R changes native H/V artwork and rotates edge anchors; Center [Home] resets position.
World-segment duplicate detection prevents two neighboring cells owning the same
wall span while allowing perpendicular/end connections. Prop collision respects
actual offsets and wall thickness, in preview, selected edits and server saves.
Untouched old conflicts remain saveable. Shared movement helpers distinguish
edge crossing from blocked interior cells; base character walking is still deferred.
Validation: 161 frontend tests, 15 construction backend tests, build and browser
rotation/collision checks pass. Dev only; production and player saves untouched.
See docs/design/BASE_CONSTRUCTION.md for implemented rules and limitations.


October 4: construction hotkeys, wheel camera, smart joins and six material kits.
Delete selects Erase, F/P/W/V switch tools and S toggles remembered snapping.
Wheel zoom preserves cursor anchoring where possible; Shift+wheel still scrolls.
Corners automatically find nearby endpoint/facing/anchor matches, preferring the
bend. R retains existing endpoint joins and skips invalid fits; manual mode stays
available. No pointer/zoom API traffic added.

Six new built-in imagegen calls each produced one nine-original equal 3x3 atlas:
rough stone, castle, church, iron, goblin camp, raider camp. Sources/prompts/crops
and real renderer screenshots saved under staging-terrain/construction-kits-v1.
Installer generalized to append a named kit, log disconnected neighbor-fragment
cleanup and retain endcaps; 576px canvases preserve the same 416px port span with
more margin. Existing wood and combat materials unchanged. Seven kits available
in read-only debug comparison; permanent painted player selection remains deferred.
168 frontend tests, 18 backend construction/extraction tests, build and browser
controls/collision/material checks pass. Six room comparisons inspected. No prod
changes or player save writes. Canonical reference: docs/art/CONSTRUCTION_MATERIAL_KITS.md.


## October 4: construction drag and removal refinement

Clicking a rotated snapped corner now commits the exact hovered orientation and
anchor. Starting a drag snapshots that preview instead of clearing its rotation
choice and snapping again.

Floors preview an inclusive rectangle between the start and current cells. Moving
back toward the start shrinks it; skipped cells are filled automatically. Walls
preview one row or column along the dominant drag direction, never a room fill.
Straight walls select matching native H/V artwork. A corner appears once at the
start, followed by plain walls extending its appropriate arm. All pieces retain
the material and facing. Some offset corner arms cannot extend with the current
five anchors: the UI asks to center the corner. Invalid runs place nothing.

Remove [Del] targets only props/walls under the pointer. Hold Shift before starting
a drag to remove a floor rectangle instead; its layer stays fixed until release.
Hover enlarges an object by 10%, dims its original and adds a warm red outline;
floors receive cell outlines. This identifies the layer without removing it early.

Every drag stays in the preview layer until release inside the map. Release
outside cancels the entire operation. Each completed drag is one undo entry.
Library-to-map dragging follows the same rules, starting at the first entered
map cell. Pointer updates do not write saves or rebuild the committed scene.

Validation: 173 frontend tests and production build pass. Isolated browser checks
cover rectangular fill/shrinking, straight runs, rotated corner commit, invalid
run rejection, layer-specific removal over shared cells, magnification, undo,
palette dragging and outside cancellations. Saves used an in-memory fixture;
production and real player data were untouched. No artwork changed.


## October 4: props sharing wall cells and default wall anchors

Wall ownership of a cell does not reserve its interior. Collision now measures
visible artwork (alpha at least 32/255) after the same aspect-preserving sizing,
rotation and offset as the renderer. A small prop can fit inside top/bottom/side
walls; larger props still cannot cross a wall. Frontend previews and backend save
validation share construction-prop-bounds.json. Existing placements and artwork
are unchanged. Wall clearance remains 0.08 cell. Bounds are conservative boxes:
transparent holes inside a silhouette are not usable gaps.

New horizontal brushes default to the top edge; native vertical brushes default
to the left edge. Corners default to center so their full arms follow cell edges.
Choosing another piece resets its default anchor; arrows/Home and smart snapping
can still change it. Existing saved wall positions are preserved.

Rebuild measurements after replacing/adding artwork with:
`.venv\Scripts\python.exe tools\measure_construction_props.py`.
The tool reads sources without modifying them; unmeasured assets use the previous
viewport fallback. 237 existing sprites measured. Validation: 175 frontend tests,
16 backend construction tests and build pass, including three-sided enclosure,
center collision, shifted collisions, multicell size and rotated art bounds.
Production and player saves were not changed.


## October 4: shared-cell furniture and seat docking

Props do not reserve an entire cell for placement. Their measured, shifted,
rotated artwork boxes are checked against other props. Separate silhouettes can
share one cell; overlapping boxes reject new placements/moves. Bounds remain
conservative: transparent gaps inside the silhouette are not detected. Unchanged
old overlaps remain saveable, but moving either object rechecks the pair.

Tables and seats have an explicit, editable exception in construction-furniture.json.
Supported tables: wooden table, round garden table and food-prep table. Supported
seats: round garden stool and mess bench. Up to 30% of the seat's visible box may
tuck under a table; full overlap is rejected. Table art draws after seats regardless
of placement order. Nearby seats dock at one of four table sides within 0.3 cell,
using the existing optional Snapping [S] control. Preview shows the tabletop over
the tucked seat. Other props do not snap to tables. Arrows/Shift+arrows provide
manual positioning; turn off S to prevent automatic docking while dragging.

Both the frontend and save API enforce these rules. The backend sweeps horizontal
bounds to avoid testing distant prop pairs. No source artwork, player saves or
production files changed. Validation: 178 frontend tests, 18 backend construction
tests, build and real browser seat-preview/drop/save/draw-order QA pass. Browser
saves were an in-memory fixture. Pixel-perfect silhouette collision and additional
furniture pairing rules remain deferred.


## October 4: calibrated prop audit and placement outlines

Construction now has its own audited size profiles in construction-prop-sizing.json.
The previous generic 92% image viewport was inconsistent: transparent margins
made furniture too small while charts and small clutter used furniture-sized boxes.
All 142 installed construction props have measured art bounds and calibrated fill.
Visible silhouettes are centered, sized by object category, and keep their source
aspect ratio. Chart 0.30 cell, lantern 0.25, ordinary containers about 0.75, chairs
0.50, stools 0.35. Large wells/cages/wagons/tents default 2x2; beds 1x2; workbenches,
pews and benches 2x1. This supersedes the earlier generic viewport sizing above.

Saved coordinates and footprints are not rewritten. Select an existing prop and
use Standard size to adopt the current default dimensions while retaining its
position/rotation; collision validation and undo still apply. Offsets now cover
-50% to +50% so docking has no gap between adjacent cells' supported positions.

Placement boxes are enabled by default in the editor, with a browser-persistent
checkbox. They tightly bound the visible alpha rectangle after sizing, rotation
and offsets, ignoring transparent image margins. Wall boxes show the existing
0.08-cell placement clearance around segments. Invalid prop previews remain visible
with red outlines and cannot commit. Boxes are noninteractive and do not appear
in the normal settlement view. They do not change character pathfinding, combat
movement, or the existing independent Reserve this footprint setting. Empty gaps
inside a silhouette's rectangle remain conservative occupied space.

A new 6x4 atlas supplies 24 overhead furniture/training props, including eight
chairs, three stools, a bench, six replacement training sprites and six new props.
All seats use the existing optional S table docking and tabletop draw priority.
Old sources remain. Combat replacement art resolves through the same stable IDs;
existing battle footprints and logic remain unchanged. Battle sprite calibration
is refreshed for the replacement images, separately from construction geometry.

Audit: docs/art/CONSTRUCTION_PROP_SIZE_AUDIT.md; six galleries and JSON under
staging-terrain/construction-prop-audit. Rebuild with:
`.venv\Scripts\python.exe tools\measure_construction_props.py`
then `.venv\Scripts\python.exe -m tools.audit_construction_props`.
New-pack source/prompt/extraction log: staging-terrain/furniture-training-v1.

Validation: 181 frontend tests, 24 backend construction/shared-size tests, build
and isolated browser checks pass. Browser verifies calibrated chart/chair/well
sizes, prop/wall boxes and toggle, red invalid preview/no commit, Standard size,
save and table docking/occlusion. Screenshots inspected. Saves were in-memory
fixtures; production and real player saves are untouched.

Validation: 420 backend tests and 183 frontend tests passed; Vite build passed (existing large-chunk warning). Isolated Chrome check confirmed cooldown labels, independent selection and action-button availability without JavaScript errors. No live API/database used for browser review.

## October 4 - tactical ability dependencies

Implemented finite Barrier, owned Mark, modern expiry/control recovery, one shared interception/counter reaction, straight displacement, resistance and opt-in shallow/deep/lethal pit resolution. Pilots use existing Tower Shield, Duelist Gloves, Precision Shot, Hook Thrust and Titan Thrust. Tooltips/previews explain actual rules; lost bodies do not become loot. No new Jobs, summons, forms, zones or maps published. Existing wall auto-pathfinding stalls remain tracked.

Validation: 432 full backend tests plus 74 final focused tests; 185 frontend tests; final build and isolated battle UI check pass. Production and live saves untouched. Canonical: docs/design/COMBAT_ABILITIES.md.

## October 4 - zones and reversible forms foundation

Added four bounded zone rules, owner activation expiry, same-kind per-target
activation limits, wall/ground clipping, committed route entry and owner-removal
cleanup. Zone casting is currently unit-anchored; no empty-tile casting UI yet.
Prowler/Bulwark replace each other and restore original profile fields exactly,
without healing, changing race or inheriting weapon attack procs. Capture tools
and payloads block changing form. Weapon techniques are unavailable in forms;
authored character abilities remain governed by their own rules.

Battle overlays preserve clicks and display zone ownership/duration. Form/status
tooltips and target preview descriptions use the same authored rules. Existing
starter kits, inventory and drops unchanged; this is engine dependency work,
not publication of Druid/Mage/Cleric or the twelve-Job roster. Summon/device
economy, ground-target UI and full form/zone AI scoring are still pending.

Validation: 207 related backend tests passed, followed by 40 focused checks for
final clipping/source-validation changes. All 186 frontend tests and Vite build
passed (existing large-chunk warning). Isolated actual battle UI confirmed zone
cells, tooltip ownership/timing, form tooltip and click-through overlay without
JavaScript errors; screenshot inspected. No real saves or production touched.
Canonical: docs/design/COMBAT_SPACES.md.

## October 4 - owner-linked summon/device foundation

Implemented seven fixed trial profiles in combat_entities.py and validated deploy
effects in the existing ability resolver. Finite encounter Components, concurrent
capacity/group identity, once-per-encounter history, delayed deployment timing,
owner-linked status clocks and shared automatic output persist through JSON.
Commanded movement preserves its own budget; attacks use the owner's main action.
Manual turret operation replaces automatic fire. No new initiative slots.
Physical devices work while muted; magical links do not. Enemy owners use the
same clock. Owner defeat/extraction dismisses units; temporary targets cannot
create prisoner/corpse loot or mission kill credit. Owner damage credit occurs once.

Context actions, resource readout and unit status tooltips are installed. No
existing starter kit, gear drop, vendor or Job catalogue grants the new profiles
yet. Dedicated placement/command UI, repair/reclaim/release and personality-aware
scoring remain pending before all twelve starting Jobs launch together.

Generated one transparent 4x4 painted atlas with the built-in imagegen tool,
retaining source, exact prompt and ordered manifest in summons-devices-v1. User
steered mobile units to portrait circles; atlas remains staged reference, not
runtime mobile sprites. Stationary idle/winding/firing/projectile/destroyed states
are documented for a later coherent pack. No source assets overwritten.

Validation: 221 related backend checks passed, then 55 focused checks covering
final enemy-clock/owner-validity changes. All 186 frontend tests and Vite build
passed; final tooltip tests passed. Isolated actual battle UI confirmed resources,
capacity, deployment tooltips/context controls and no extra turn chips or JS errors.
Production and real saves untouched. Canonical: COMBAT_DEPLOYMENTS.md and
SUMMON_DEVICE_ART.md.
# October 4, 2026 — Regular character loadouts

Added twelve initial opt-in Job toolboxes and the Roster Skills editor. Five
shared slots cover actives/passives; learned and equipped skills persist
separately. Job choice does not replace equipment/proficiencies, and Champions
remain outside generic Job migration. Battle snapshots now carry character
actives, real passive modifiers and reactions alongside every equipment ability.
Auto support understands legal/resource-bounded deployment and self forms.

Validated 230 related backend tests, 188 frontend tests, frontend build and an
isolated actual-browser fixture. Existing frontend chunk warning remains. Full
twelve-Job starter creation, progression and later skills are next; see
`docs/design/JOB_LOADOUTS.md`. No production deployment or player-save edits.
