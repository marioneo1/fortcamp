# Fortcamp feature backlog

Use this file for pending work and GAMEPLAY_VISION.md for standing design rules. Update statuses when implementing a feature; record validation in docs/history/MISSION_REFINEMENT_PHASE.md. Requests here do not authorize paid generation or publication beyond the user's current instructions.

## Current pass — September 30, 2026

- Goblin flames now emit continuously instead of ending together between bursts. Added a 24-second soft wood-fire loop with gentle context fades and Master/Ambient controls. Sources and listening previews are preserved; user listening approval remains pending. See docs/audio/WOOD_FIRE_AMBIENCE.md.

- Goblin fire composition revised after user feedback: large overlapping flames originate below the camera, with only broad tongues rising from the bottom. The effect itself keeps its upper flames wide and bright; smoke/embers emerge from the same unseen blaze. No buildings or random visible campfire bases. Independent timing and scale changes avoid a uniform fire border. Desktop/mobile browser previews, reduced motion and allocation checks passed; live visual review remains open.

- Implemented: accepting a choice-driven contract includes its first decision in the acceptance response. Open immediately, scroll to the top, allow closing, and resume saved choices. Background completions must not replace an open mission screen.
- Implemented: aftermath places readable story beside recovered rewards; expedition checks and loot rolls are expandable.
- Implemented: device-local Master, Music, Interface & Mission Sounds, and Battle Effects volume settings, mute, reset, and sound previews. Existing effects retain their individual mix levels inside those channels. Music playback now rotates approved guild tracks and switches to base/general/goblin themes with fades.
- All four guild tracks approved; three base/combat themes and eight distinct Mureka tracks installed (two each for investigation, defense, undead, and bosses). Originals are preserved; the listening library contains 15 tracks. docs/audio/MUSIC_GENERATION_GUIDE.md records the shared palette and four arrangements. ELEVENLABS_MUSIC_IMAGE_KEY remains server/tool-only.

## Next priorities

1. **Music pilot:** 25 tracks are installed with context playlists, three-second crossfades, brief-popup protection, and resuming prior background tracks. All five regional events now have two Mureka tracks each. Seven occasional ambience clips are installed with a separate Ambient Sounds channel; subjective listening refinement remains open. Keep one musical identity across arrangements. Verify actual loop boundaries and perceived loudness, not just file peaks.
2. **Selection responsiveness:** profile the actual Discord activity and browser, including party selection, defense deployment, redraws, polling, image decoding, and request latency. Measure before choosing a fix. Avoid rebuilding unchanged panels and losing input state. User reports perceived frame drops even outside combat.
3. **Equipment and inventory UX — catalogued, deferred:** support large inventories, search/filter/sort, clear equipped state and compatible slots, readable comparisons and granted effects, quick equip/unequip, consistent scrolling and focus. Do not redesign as part of the current audio pass.
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
