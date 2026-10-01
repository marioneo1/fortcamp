# Mission Refinement Phase

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
