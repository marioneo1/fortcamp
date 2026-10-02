# Fortcamp feature backlog

## Completed October 2: Remaining active mission props

Added twelve overhead sprites and wired missing dispatch satchel, loose wagon wheel and marked farm chart. Prison wagon now has dedicated intact/wrecked art; prepared traps have armed/spent variants and generic contract walls use the existing overhead stone-wall sprite. Shared state resolver supports older saved encounters without changing gameplay. Current registry: 55 sprites. Audit: 65 encounter setups, 888 references, no missing prop assignments/files. Validation: 301 backend and 103 frontend tests, browser encounter checks and frontend build passed. No production deployment. Remaining: subjective live review, unused legacy-library objects and future props needed by new mission forms.

## Completed October 2: Expanded overhead props installed

Generated three additional twelve-sprite packs and installed 43 selected overhead assets across nature, defenses and containers. The left pine, lower-right bramble and alarm bell now render in the actual Warcamp; bell active/disabled art and human-readable labels match. Stable IDs and old saves remain compatible, gameplay unchanged, original art preserved. Sources/prompts/gallery/screenshots: staging-terrain/overhead-props-v2. Manifest and reproducible import procedure: docs/art/MAP_ASSET_LAYERING.md. Remaining: subjective live review, unmapped specialist props and further camera refinement where tall structures still show frontal surfaces. Validation: 301 backend tests, frontend build and actual-browser asset/state checks passed. Production not deployed.

## Completed October 2: Prop grounding and camera pilot

Live painted props now preserve aspect ratio when enlarged and use short silhouette shadows. Generated and safely extracted a twelve-object overhead study with terrain comparisons and actual Warcamp old/new toggle; existing runtime art remains intact. See docs/art/MAP_ASSET_LAYERING.md and staging-terrain/overhead-props-v1/PROMPT.md. Two catalogue crop tests, production build and browser study/Warcamp checks passed. Remaining: user visual review, steeper overhead palisades and coherent open/closed pairs before expanding or replacing the full prop pack. Do not describe the pilot as a completed art replacement.

## Completed October 2: vendor, hire pricing and social workspaces

Implemented: always-available starter gear for gold; contact-grade hiring fees multiplied by actual contract rank; compact prisoner selection/details with warden readiness and explicit full-cell swaps; portrait-based conversation workspace with eight session exchanges, readable topics, meal quantities/preferences/cooldown and duplicate-click protection. Canonical rules: docs/design/FACTIONS_AND_ROTATING_TRADE.md, MERCENARIES.md, PRISON_RECRUITMENT.md and CHARACTER_RELATIONSHIPS.md. Validation: 301 backend tests, 101 frontend tests, production build and isolated mercenary/social/trade browser checks passed. No production deployment. Remaining: real multiplayer price feedback, more authored conversation/Champion voices, and persistent conversation history if later requested. Current dialogue remains curated, not an LLM service.

Use this file for pending work and GAMEPLAY_VISION.md for standing design rules. Update statuses when implementing a feature; record validation in docs/history/MISSION_REFINEMENT_PHASE.md. Requests here do not authorize paid generation or publication beyond the user's current instructions.

## October 2 ? capture weapons and starter roles

- Implemented in dev: Fighter, Ranger, Mage, Captor, Medic and Engineer starting roles with matching poor-quality gear, one perk and Basic proficiency. Starting roles do not restrict later builds; existing characters keep their gear.
- Implemented: dedicated capture weapons replace Attack with Subdue, including the A hotkey, target menu and previews. The server rejects Attack for these weapons. Repeatable STR/DEX/INT probability checks drive Subdue. Failed attempts do no damage; success leaves a living captive. Manual/automatic/personality combat, previews, boss resistance, control setup and legacy battles use the new rules.
- Implemented: nine capture weapons with rank-gated general/event sources and two rare mission exclusives; existing restraint tools converted. Ordinary blunt/unarmed capture and the glove loophole retired. Blackwatch Cudgel gets its own 5% killing-blow knockout effect.
- Deferred/design recorded: levels, persistent XP, bounded specialization choices and fixed enemy levels; no automatic attribute inflation or player-scaled encounters. Respecialization and dedicated starter/capture art still need a pass.
- Canonical reference: docs/design/CAPTURE_AND_STARTING_ROLES.md. Existing gear art reused; no new image generation or production deployment.


## Current pass — September 30, 2026

- Goblin flames now emit continuously instead of ending together between bursts. Added a 24-second soft wood-fire loop with gentle context fades and Master/Ambient controls. Sources and listening previews are preserved; user listening approval remains pending. See docs/audio/WOOD_FIRE_AMBIENCE.md.

- Goblin fire composition revised after user feedback: large overlapping flames originate below the camera, with only broad tongues rising from the bottom. The effect itself keeps its upper flames wide and bright; smoke/embers emerge from the same unseen blaze. No buildings or random visible campfire bases. Independent timing and scale changes avoid a uniform fire border. Desktop/mobile browser previews, reduced motion and allocation checks passed; live visual review remains open.

- Implemented: accepting a choice-driven contract includes its first decision in the acceptance response. Open immediately, scroll to the top, allow closing, and resume saved choices. Background completions must not replace an open mission screen.
- Implemented: aftermath places readable story beside recovered rewards; expedition checks and loot rolls are expandable.
- Implemented: device-local Master, Music, Interface & Mission Sounds, and Battle Effects volume settings, mute, reset, and sound previews. Existing effects retain their individual mix levels inside those channels. Music playback now rotates approved guild tracks and switches to base/general/goblin themes with fades.
- All four guild tracks approved; three base/combat themes and eight distinct Mureka tracks installed (two each for investigation, defense, undead, and bosses). Originals are preserved; the listening library contains 15 tracks. docs/audio/MUSIC_GENERATION_GUIDE.md records the shared palette and four arrangements. ELEVENLABS_MUSIC_IMAGE_KEY remains server/tool-only.

## Next priorities

- Browser play implemented: Discord OAuth, server picker restricted to user membership and this instance's installed bot, registration gating, server switching and sign-out. Website/Activity share server-scoped saves. Dev/release sessions bind to environment/application/database; cookies and caches are separated. Alpha signing secret is independent. Launchers block conflicting simultaneous bot application IDs; release preparation preserves production credentials rather than copying dev env. Portal redirects and a separate dev Discord application remain manual setup; pinned release unchanged. See docs/WEB_PLAY.md.

- October 1 gear/content pass implemented: 180 items total, 56 additions across all eight slots, 18 new mission-exclusive/capture/event discoveries, and six existing utility upgrades. Low-rank exclusives remain relevant; new long-chain pieces and Starfall relic retain independent drop rates. Equipment techniques are selectable with one shared battle use. Carrying, throwing, breaching, guarding, terrain mobility, elemental protection and survival rules are bounded and shown in gear descriptions. See docs/gameplay/ITEM_CATALOGUE_AUDIT.md and GEAR_LOOT_DESIGN.md. All 180 local icons installed; new sheets append existing assignments.
- Follow-up item design: actual player drop-rate/progression feedback, additional authored branch rewards, party support/healing skills and consumable actions. Do not label unimplemented granted-perk effects as working mechanics. Loadouts/shared armory and deeper gear comparison remain separate UX work.

- October 1 onboarding: catalogue-backed race dropdown with racial effect preview, clearly separated starting Perk and Basic Proficiency, optional background/portrait settings. Exactly one roster character grants +10 Contract Points per pool in free-for-all only; waves remain five points and spent points do not reset when roster size changes. Camp hiring removed from UI and API; keep mission recruitment and author future prisoner recruitment/trader acquisition separately.
- Building functionality audit: see docs/design/BUILDING_FUNCTIONAL_AUDIT.md. Watchpost has no implemented defense effect; Barracks beds do not enforce housing capacity; Campfire staff has no working bonus. Decide whether to retire/defer those construction offers or give them meaningful systems. Do not silently delete placed buildings or existing recruits. Correct stale claims about equipment repair and inventory capacity.
- Loyalty remains partial: combat reads it and low-loyalty endangered allies may panic; missing values default to 100. Recruit starting values, loyalty gains/losses, visible obedience chances and independent commands remain unimplemented. Preserve the proposed curve in COMBAT_DESIGN.md for a dedicated gameplay pass.
- Catalogue art crop repair: 43 items and 41 race emblems recovered from complete source silhouettes, good crops preserved, importer upgraded to prevent nominal-grid cuts, backups/report under data/catalogue-crop-audit. No new artwork generated.

- October 1 friend-trial pass: explicit per-server `/register` and `/unregister` participation; unregister preserves saves. Pinned local releases and separate stable/dev databases and ports; see docs/FRIEND_TRIAL.md. Base workshop/search/management cleanup, immediate contract mutation updates, live phase countdown and deadline refresh. Broader Base artwork and real multiplayer balance/soak testing remain future work.

1. **Music pilot:** 25 tracks are installed with context playlists, three-second crossfades, brief-popup protection, and resuming prior background tracks. All five regional events now have two Mureka tracks each. Seven occasional ambience clips are installed with a separate Ambient Sounds channel; subjective listening refinement remains open. Keep one musical identity across arrangements. Verify actual loop boundaries and perceived loudness, not just file peaks.
2. **Selection responsiveness — first pass implemented October 1:** battle/preparation updates retain map cells, tokens and decoded portraits; interrupted walking continues from its actual displayed position. Rapid movement input keeps only the latest pending destination for the same activation. Hidden Base/Roster panels defer polling redraws; visible roster cards, base cells and resource counters retain their elements. Local software-rendered browser profiling removed the observed 128 ms long task and reduced the maximum sampled frame gap from 217 to 67 ms. Actual Discord/device profiling, large parties/maps and selection performance remain follow-ups; this does not eliminate network latency.
3. **Equipment and inventory UX — first pass implemented:** paged/searchable item stacks, slot/rarity filters, equipped ownership, transfers, injured-character equip/unequip and remembered hide-equipped preference. Granted effects now show bounded utility rules; battle exposes all equipped techniques. Shared armory, loadouts and deeper comparisons remain pending.
4. **Mission-board visual direction — catalogued, deferred:** consider consistent generated icons, restrained backgrounds and event VFX. Preserve readability, navigation, rank grouping, private leads, and reduced-motion behavior; decorative work must not worsen performance.
5. **Aftermath follow-up:** review the new format with real long stories, prisoners, discoveries, and large reward lists. Prefer story and consequence over a wall of mechanical recap; expose checks on demand.

## Gameplay and content pipeline

- Economy/building discussion (not implemented): starter production, Stone replacing Cloth as a general construction resource, expanded E-rank content, public wave/free-for-all allowances, and base expansion. See docs/design/RESOURCE_PROGRESSION_PROPOSAL.md; numerical proposals and tentative buildings require validation.
- Faction trade: gold purchases increasingly varied/rare/faction-specific goods as relationships improve. Visiting merchants can offer rare or merchant-exclusive stock; persist offers and avoid reload rerolls or compulsory frequent checking. Preserve mission-exclusive acquisition rules.
- Food/cooking proposal: simple foraging and passive farm production, hunting/provision missions and trade fallback; optional batch-cooked meals. Defer detailed crop simulation and avoid offline starvation or collection-size upkeep penalties.
- Confirmed starting constraint: player begins SOLO. Withdraw starter-helper proposal; production, basic cooking, construction, recovery and early contracts must work without recruited staff. Workers improve these systems later. See the resource progression draft for proposed idle Camp Work and recovery safeguards.
- Faction diplomacy and trust that open relevant Private Contracts.
- Decision scenes continuing after combat, with route-specific endings.
- Broader authored decision coverage: optional setbacks, mission loss, ordinary fights, exceptional bosses; pure-roll missions remain plentiful.
- Defense preparation and readable objective placement; traps/Engineer constructions develop in stages.
- Adventure floors, transitions, rescue/escort objectives, and scenario-specific maps. Reuse docs/art/BATTLE_MAP_AUTHORING.md and docs/art/MAP_ASSET_LAYERING.md; add props only for meaningful interactions.
- Full stealth/detection and night/sleep approaches; larger squads only after scaling and deployment UI support them.
- Individually authored Champion acquisition chains and signature perk mechanics; maintain uniqueness and lore-relevant discovery.
- Continue perk/race balancing and show only implemented effects. Do not claim the entire perk catalogue is finished.
- Prison foundation already supports capture storage, selling, secured/stockade swaps, and a one-hour stockade budget preserved per prisoner. Recruitment, exchanges, and meaningful warden mechanics remain deferred until resumed explicitly.
- Remaining male portrait pass: deferred. Preserve current female/male generation guides and legacy prompts.

## Development workflow

Use local Git for code, tests, documentation, and build configuration. Keep secrets, player databases, generated art/audio, and build outputs outside the baseline. Asset source folders need their own backups; Git exclusions do not delete files. The origin remote is https://github.com/marioneo1/fortcamp.git; the user authorized public code publication. Generated media and player data are excluded.

## Regional audio follow-up

All ten regional uploads are installed, bringing the listening library to 25 tracks. Seven sparse ambience accents are generated and installed. Review their listening comfort in real play; do not add a continuous bed or more clips until the current mix has been heard. Ambient volume is separate from music and battle feedback.

## Mission Board art proposal and guild ambience

The user approved the board proposal; the first art/layout pass is implemented. docs/design/MISSION_BOARD_UI_PLAN.md preserves the plan and docs/art/MISSION_BOARD_ASSETS.md records extraction and browser verification. Guild chatter is installed now as an eighth ambience clip, restricted to the ordinary Mission Board and governed by the existing Ambient Sounds slider.

Regional visual effects now include actual full-board backgrounds behind public/private cards, alongside the event emblem scene. Motion is bounded and suspended when hidden or outside the board. Further tuning should follow real Discord play rather than adding more layers blindly.

The board backgrounds now use PixiJS Particle Emitter with the generated painted effects pack: layered windblown leaves, sparks that fade/burn out, expanding smoke/mist, ash and magical motes. Shared lazy loading preserves stable asset names. Rain/snow presets are implemented and available in the local effects preview; actual battle weather and skill integrations remain deferred. See docs/art/ENVIRONMENT_VFX_ASSETS.md.

Visual follow-up replaces repeated painted smoke curls with new procedural density textures, large arcane glyphs with deforming viewport currents/glimmers, and the slowly dragged Starfall image with a fast head and tapered trail. More visible particle layers and restrained panel transparency let the atmosphere read across the board. The old emblem-only CSS scene is suppressed; original art assets remain preserved.

Implemented the next visual review: Starfall uses tiny procedural starlight, falling cosmic dust, darker nebula and two deforming gravity trails alongside sparse fast shooting stars. Goblin atmosphere favors smoke, fewer green sparks and three intermittent flame sources. Arcane keeps its flowing currents and restores the two counter-rotating circles on the far right of the banner, separate from the emblem. Original art remains preserved. Effekseer is now integrated for Goblin fire; authored spells/portals/impacts remain future work.

Starfall follow-up: meteor showers use staggered 6-10-meteor clusters, four concurrent flights maximum, varied paths/scales and quiet gaps. Mission Board rank crops use the cleaned full-height row with stable filenames and a cache revision. Goblin fire now has an enabled Effekseer trial replacing the rejected Pixi flames; live Discord visual approval remains pending. See docs/art/EFFEKSEER_FIRE_TRIAL.md.

Effekseer Goblin fire is authored, compiled and browser-tested using the real WASM engine on the shared board canvas. Other regional effects remain Pixi. Allocation caps, reduced-motion freeze and cleanup are implemented; source, provenance, license and rebuild instructions are recorded. Further fire art/tuning should follow the user's live visual review.

## Equipment, loot and burning scene - September 30, 2026

- Implemented: three larger burning sources spread across desktop backgrounds, two on narrow screens. Smoke and sparks use the same source positions as actual Effekseer fire; restart as each effect finishes. Reduced motion, hidden-tab suspension and allocation caps remain. Further visual tuning follows live play.
- Implemented: 28 new items, bringing the catalogue to 108. Ordinary capture weapons, elemental weapons, armor-piercing abilities and five chain-exclusive relic weapons. Gear skills work in manual and auto combat, use explicit STR/DEX/INT scaling and explicit elevation rules, and consume one action once per battle.
- Implemented: Fire, Ice, Lightning, Holy and Void enchantments check matching racial affinities. Existing Burn/Freeze/Radiant affinities map to Fire/Ice/Holy. Burn and Poison weapon procs tick once per activation, expire, do not stack, and cannot be applied by nonlethal attacks. Poison-resistant Deathless/constructs are immune; other status mechanics remain separate backlog work.
- Implemented: Common and Uncommon additions for all five event caches; nine authored mission cache pools mix with ordinary gear. Rarity rolls remain gated by rank, after a separate chance to obtain any loot. Mission-exclusive relics never enter random caches. Five chain-final relic checks require follow-up provenance: 14% success / 22% critical success; failure yields none. No guaranteed relic or automatic pity reward.
- Implemented: 108 generated item icons (three 6x6 sheets) and 42 race emblems (one 7x6 sheet), installed with stable item/race filenames. Item icons appear in equipment and aftermath; race emblems appear in roster racial identity. Original sheets are preserved under staging-ui/equipment-icons-v1. Manifest assignments append rather than reorder; extractor refuses overwrites and preserves aspect ratio. Generated media remains excluded from public Git.
- Implemented: tiered Basic to Master tracks are called **Proficiencies** in roster/training. Distinctive traits remain **Perks**. Saved field/API names remain compatible; existing progress is unchanged.
- Next balancing pass: mission loot across all 118 templates, branch/capture-specific rewards, skill diversity beyond a single equipped action, elemental enemy variety, rare non-weapon active gear and crafting/consumable uses for keepsakes. Do not display unimplemented skills as functional.
- Next UI pass: full shared inventory view and loadouts; existing roster Equipment browser is functional now. Broader combat-status mechanics, stealth, dungeon floors, prisoner recruitment and male portraits retain their previous scope.

See docs/gameplay/GEAR_LOOT_DESIGN.md and docs/art/EQUIPMENT_ICON_PIPELINE.md for the rules and asset workflow.

- October 1 responsiveness follow-up: valid movement clicks now immediately redirect local walking using server-validated routes, without waiting for network replies. Older replies cannot undo newer input; failed moves restore the authoritative position. Tested with 400 ms simulated latency. Continue actual Discord/device review.


## October 1 relationship / combat-effects foundation

Implemented: loyalty-based independent-turn chance, stable personalities (12 tropes / seven shared policies), individual meal tastes, roster conversations and service records, eight factual memories, prepared-meal gifts with six-hour cooldown, Effekseer death splash and magic projectile. docs/INDEX.md and AGENTS.md upkeep rules added. Durable completion notices with reconnect retry; Dev still needs `/fortcamp_setup` in its own channel.

Deferred: deeper debriefs and Champion voices, item/trinket gifts and crafter recipes, relationship events/rivalries, adult SFW family/relationship design, award ceremonies and in-game handbook. See docs/design/CHARACTER_RELATIONSHIPS.md. No free-form conversational AI or retrospective statistics.

## Completed: contract, equipment and map QoL (2026-10-01)

- Click outside the contract dialog to close it without abandoning a saved mission.
- Equipped gear effects; spare item effects visible by default; independently saved Hide gear details setting.
- Viewport-clamped perk/attribute formula help; Service Record moved out of Conversation.
- Fit map camera for combat and preparation; preserve proportions and manual scrolling at larger zooms.
- Hidden unique rewards no longer advertised by name or numerical drop chance unless the briefing discloses them.
- Validation: 226 backend tests, 94 frontend tests, production build; isolated real-browser checks for fit, zoom, gear preferences, tooltips, record placement and outside dismissal. No release/save changes.

### Completed follow-up: equipped effects and victory banner

- Equipped slot effects are permanently visible; spare-card detail preference remains separate.
- Camera buttons share one row with equal widths.
- Centered wide objective-secured banner minimizes after Continue for optional objectives and can be reopened through Finish operation.
- Validation: 94 frontend tests, production build, isolated browser checks of camera layout at three sizes, always-visible equipped effects and victory minimize/reopen. Gameplay rules and release saves unchanged.

### Precise zoom and prison planning (2026-10-01)

Implemented smooth pointer-anchored map wheel zoom, retaining modified-wheel scrolling, camera buttons and middle-click behavior. Proposed prison recruitment design documented in docs/design/PRISON_RECRUITMENT_PROPOSAL.md: warden attention, resistance versus loyalty, individual concerns and allegiance contracts for exceptional captives. Recruitment/warden effects remain pending; no prisoner data altered.

## Completed: first playable prisoner allegiance loop (2026-10-01)

Stable capture terms and recruit profiles; eight initial concerns; shared INT-based warden negotiation; story-backed gold/wood/medicine/item sinks; 24 owner-only tactical allegiance templates; explicit one-time recruit conversion and starting loyalty. B/A/S officers with payments also require proof. Roster prisoner conversations and Private Contracts now connect. See docs/design/PRISON_RECRUITMENT.md for live rules, migration and limitations. Temporary faction politics, deeper authored chains, security incidents and personal loyalty follow-ups remain pending.

### Completed October 1: prisoner UI standardization
- Replaced native browser confirmations with a shared in-game dialog for agreement payments, prisoner sales and contract abandonment.
- Organized prisoner cards into conversation/terms, recruit profile, warden resistance, and separate custody actions. Payment costs and follow-up requirements are explicit; tabs remain selected across refreshes.

### October 1: friend trial.2 release preparation
- Prepare an independent production clone from current tested main, preserving production credentials, database and media; force debug/auth bypass off in release env and launcher.
- Alpha and production still share a Discord application ID: simultaneous local dev is supported; concurrent Discord dev requires separate application credentials.
- Host startup and friend-server installation remain operator steps documented in docs/FRIEND_TRIAL.md.

### Completed October 1: camp, roster and inventory navigation (dev only)
- Base task sections: Settlement, Supplies, Development, Kitchen and Prisoners; facility list/inspector and construction sidebar; explicit staffing controls alongside drag/drop.
- Prisoners have their own Base workspace with Roster shortcut, search and secure/stockade filters. Collections are a separate Roster view.
- Party Inventory separates manuals/materials from wearable equipment and allows confirmed quantity sales of unequipped copies; server prevents equipped/duplicate/missing sales and publishes resale quotes.
- See docs/design/CAMP_INTERFACE.md. Existing production trial.2 is unchanged; further sale-price tuning, buyback and material use remain future work.
## Mercenary and early pacing pass — October 2, 2026

Implemented in alpha/dev: four persistent player-specific mercenary contacts; private-contract hiring after assigning an own crew member; multiple hires/bodyguards, rank-scaled fees, −1 check penalty per hire (maximum −4), shared betrayal encounter with occasional loyal holdout, trust discounts and permanent recruitment. Original contracts resume after surviving turncoats. Low-frequency outdoor corpse/friendly/hostile encounters, a central notice, hostile victory gating, and removal of dead contacts are implemented. Missing contacts refill on opening the hiring board. Starter perk kits and quieter natural regional events are included. See docs/design/MERCENARIES.md for numbers and validation.

Follow-ups: real multiplayer balance/soak testing; broader racial/named mercenary content; full pre-contract injury/consumable carryover into adventure encounters; dedicated worn starter-gear art if useful. Permanent companions remain the better long-term option. No release deployment in this pass.

## October 2 production workflow

Implemented fixed sibling `fortcamp-dev` and `fortcamp-prod` folders, a one-step `update_prod_windows.bat`, production-only launch guards, credential-preserving updates with database backups and failed-build rollback. `fortcamp-release-data` remains the production store for every installed server; registrations persist. Separate Discord dev application and actual multiplayer soak testing remain follow-ups. See docs/FRIEND_TRIAL.md.


### October 2: ambush opening and goblin boss pacing ? implemented in dev
- Successful scouting: every initial enemy sleeps for three rounds; first attack against any enemy wakes all, even on a miss. Positioning remains safe. Status hover shows the shared rule and rounds remaining.
- Authored, roster-independent Goblin Warcamp chief and escort stats; stronger B-rank Redoubt commander. Existing saved battles retain their old values.
- Follow-up implemented below: quiet automatic opening positioning and generated-contract rank budgets. Coordinated formations and live friend-server balance review remain pending.
- Superseded by the following pass: the Story milestone label and five personal faction consequences are now implemented. These flags still do not alter server events.


## October 2: combat tools, authored branches and rotating faction trade ? dev

- Implemented fixed E?S enemy budgets for generated contract battles, preserving special rookie fights and authored Warcamp/Redoubt stats. No player-roster scaling. C+ enemies add restrained status threats; auto-battle positions quietly during ambush preparation.
- Implemented selectable ally healing/cleansing/Guard techniques, one shared technique use per character, three shared consumable uses per battle, three owned supplies and immediate durable inventory spending with stale-state rejection. Auto does not spend consumables. Status activation stamps prevent polling/repositioning from repeating effects; condition rules and boss control recovery are documented.
- Implemented nine relationship-gated private faction agreements plus five earned finale consequences. A contact request immediately opens the planner. Private ownership, rank gates, active-copy deduplication and completed-job protection are authoritative.
- Implemented four ordinary safe/risky investigation graphs and three beginner combat handovers. Winning a fight can return to an optional evidence choice; failed optional checks preserve victory, and final rewards/records/notices are issued only once at handover.
- Implemented one rotating faction trader per camp, 48-hour saved visits and stock, relationship discounts, permanent basic/treatment supplies, and the separate player-specific roaming merchant. Adding additional factions remains a later content pass.
- Implemented fourteen mission-exclusive agreement keepsakes with distinct support/defensive actions and independent drop rates. Existing loot exclusivity and low-rank discoveries remain. Initial icons reuse installed art; unique art is deferred rather than blocking play.
- Renamed aftermath World outcome to Story milestone. Five existing flags now unlock personal faction work, not server-wide event changes.
- Validation: 280 backend tests, 100 frontend tests, frontend production build; isolated actual-browser Trade and battle supply checks, responsive widths 1440/800/430, immediate planner opening, correct item command. Preview files are local only; tools never access game databases. Production was not deployed and player data was not wiped.
- Remaining: multiplayer balance/soak testing, more factions and merchant goods, more authored branches/long arcs and lore-based Champion acquisition, more explicit sources for the full status catalogue, formation AI, dungeon floors/stealth, adventure injury/supply carryover, and optional dedicated keepsake art. Existing relationship/portrait/handbook backlog remains.

Canonical references: docs/gameplay/COMBAT_TOOLS_AND_PACING.md and docs/design/FACTIONS_AND_ROTATING_TRADE.md. Local UI fixture: tools/build_faction_combat_preview.py; run with the existing tools/serve_board_preview.mjs and tools/faction_combat_browser_qa.mjs. These are developer QA tools, not new game launchers.


## October 2: unified launcher cleanup

Implemented one authenticated dev launcher for both website and Discord Activity, preserving debug tools and dev saves. Removed the duplicate Discord shortcut and obsolete title-based stop shortcut; Ctrl+C stops the owned process group. Release checkout filtering removes dev-only shortcuts without changing pinned production source, credentials, builds or saves, and persists in future release builds. Existing production received launcher filtering only, with no gameplay deployment or restart. README, WINDOWS_TOOLS, browser play and friend trial instructions updated. Validation: ten run-profile/release tests, including a real temporary Git checkout proving filtering preserves HEAD, source, generated runtime files and clean production status. Separate Discord application credentials remain necessary for concurrent authenticated dev/prod bots.
