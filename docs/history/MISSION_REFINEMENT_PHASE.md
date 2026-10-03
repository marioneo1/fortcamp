# Mission Refinement Phase

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
