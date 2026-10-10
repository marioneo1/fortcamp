# Fortcamp documentation map

[Technical stack brief for GPT](design/TECH_STACK_GPT_BRIEF.md): copy-paste
architecture/dependencies, combat, assets, tooling and deployment snapshot.

[Day/night lighting tester and proposal](design/DAY_NIGHT_LIGHTING_PROPOSAL.md):
saved arrival phases, elapsed light movement on return, blue scenery grading,
stylized directional shadows and lighting controls within Battle Lab.
Includes roofed-room contact shadows, art-only cart filtering and stable preview sizing.
Full phase progression during missions remains deferred.

[Mission resource reward preview](design/MISSION_RESOURCE_REWARD_PREVIEW.md): proposed
four-outcome resource comparison; awaiting UI discussion, not implemented.

[Animal mounts](design/ANIMAL_MOUNTS.md): implemented Rider/boar rules, targeting,
turn timing, art and deferred animal capture. [Short rider guide](player-reference/RIDERS.md).


[Shared combat stats](design/SHARED_COMBAT_STATS.md): implemented formulas,
attribute-first rank, enemy reconstruction, capture parity and deferred work.
[Migration audit](design/SHARED_COMBAT_STATS_AUDIT.md): 396 fresh E/D fights.

[Character growth proposal](design/CHARACTER_GROWTH_PROPOSAL.md): brainstorming
for Adventurer Rank, Growth budgets, respec/rebirth and transparent stat Details;
documents the former formula mismatch and remaining growth decisions.
The shared 12 HP / 2 Attack migration is now implemented separately above.
Its deferred race section records possible racial innate HP/base Attack differences.

[Growth comparison](design/CHARACTER_GROWTH_COMPARISON.md): reproducible offline
comparison of 13 E/D enemy bodies and S-stage builds, recorded before the shared
baseline was selected. [Short progression checkpoint](player-reference/CHARACTER_GROWTH_NEXT_STEPS.md)
summarizes implementation and deferred decisions.

[Shared-stat combat trial](design/CHARACTER_GROWTH_TRIAL.md): 216 isolated paired
fights, opening damage and survival data, [per-fight results](design/CHARACTER_GROWTH_TRIAL.csv).
Historical pre-migration trial; lower bases were subsequently implemented with reconstruction.

[D-rank combat audit](design/D_RANK_COMBAT_AUDIT.md): E-relative rank multipliers
and the first twelve layouts for Highway Ambush, Bone Patrol and Boar-Rider Patrol.

[Defense preparation](design/DEFENSE_PREPARATION.md): rebuilt point defenses,
free equipped Engineer/Rogue deployments, pit escape and proximity explosions.

[Personality audit](player-reference/PERSONALITY_AUDIT.md): 12 implemented
personalities, 16 proposed anime/ordinary additions, and the separate voice/AI scope.

[E-rank combat audit](design/E_RANK_COMBAT_AUDIT.md): all 14 missions in the current
audit scope now covered, including four defense and four E-rank rescue layouts.

[Player reference folder](player-reference/README.md): short readable summaries
of enemy specialties, implemented recruit perks, proposals and voice progress.

[Voice progress](player-reference/VOICE_PROGRESS.md): animal/specialty sounds and
the installed 144 wordless Human/Goblin combat clips by gender and personality.
[Vocal implementation](art/ENEMY_VOCALS_V1.md) records assets, event timing,
recruit persistence, preloading and listening limitations.
[Voice tester](../frontend/public/assets/sfx/voice-tester/preview.html):
all installed Human/Goblin clips with playback, saved ratings and feedback export.

[General quirks](player-reference/GENERAL_PERKS.md): implemented positive/negative
quirks, conflict groups and rarity; generated from runtime definitions. Naturally
Gifted is an independent bonus compatible with redistribution and luck traits.

[General perk audit](player-reference/GENERAL_PERK_AUDIT.md): historical design
review and deferred event-based ideas.

[Recruit perk options](player-reference/RECRUIT_PERK_OPTIONS.md): player-readable
historical alternatives; approved implementations are in RECRUIT_PERKS.md.

[Starting race audit](design/STARTING_RACE_AUDIT.md): implemented 14 starting
choices, 26 discovery races and two special acquisitions; existing characters preserved.

[Classes at a glance](design/CLASSES_AT_A_GLANCE.md): short current reference for
all 12 selectable classes, extra humanoid kits, animals, summons and machines.

[Animal art/audio handoff](art/ANIMAL_CRITTERS_V1.md): preserved portraits,
rat/wolf sounds, playback changes and required 5x4 future image batches.

[Current work and parked threads](WORK_STATE.md) is the session/pivot checkpoint;
read it first to resume unfinished work and preserve accepted decisions.

[Race-name upload brief](content/RACE_NAMES_GPT_BRIEF.md) covers all 42 current
races in seven GPT batches; [workflow](content/RACE_NAMES_WORKFLOW.md) records
the output folder, naming-source guidance and implemented dev integration.

Current skill click audit: [Skill targeting](design/SKILL_TARGETING_AUDIT.md)
records the 12-Job/77-active-skill routing review, direct approach execution,
invalid-target fallback fix, retained placement flows and test coverage.

Character life / personal-story planning: [design proposal](design/CHARACTER_STORIES_PROPOSAL.md),
[short character overview](content/CHARACTER_LIFE_OVERVIEW.md),
[content index and maintenance rules](content/CHARACTER_STORY_CONTENT_INDEX.md),
[GPT bulk authoring prompt](content/CHARACTER_STORY_AUTHORING_PROMPT.md) and
[draft v0.2 content contract](content/character-story-contract-v0.2.json).
[Upload-ready GPT brief](content/CHARACTER_LIFE_GPT_BRIEF.md) includes the
conversation-led character-blueprint pilot and contract in one file.
[Authoring workflow](content/CHARACTER_LIFE_WORKFLOW.md) defines the fresh-chat,
single-upload process, offline checks and separate design/approval gates; the
current bundle requests revision 3 with its source draft and review attached.
Proposal only: persistent hidden backgrounds, conditional voices, novelty selection,
optional personal objectives and explicitly once-per-player stories are not implemented yet.
The refinement also proposes early disclosed loyalty conflicts, bounded personal
chains, earned personality variations, core-arc closure and story-matched rewards.

Current mobile battle pass: [Combat controls](design/COMBAT_CONTROLS.md) describes compact touch tabs, swipeable action rows, mobile Battle Lab setup, pan/pinch, long-press inspection and Safari validation limits. Desktop geometry remains separate; other game screens still need a mobile pass.

Current E-rank audit: [Batch audit](design/E_RANK_COMBAT_AUDIT.md) records three completed batches: rats/toll/wolves, pickpockets/well/supply, and timber/tool shed/herb garden. It includes all layouts, recruitable enemy kits, material checks and simulation limits. [Combat capability reference](design/COMBAT_CAPABILITY_REFERENCE.md) indexes implemented mechanics and must be maintained with combat changes.

Current floating battle HUD trial: [Combat controls](design/COMBAT_CONTROLS.md) documents draggable groups, snapping guides, saved local layouts, proportional resizing for four groups, foremost Edit Layout tools and effects overflow. Implemented in dev; production unchanged.

Implemented Captor: [Captor and Resolve](design/CAPTOR_REWORK_REVIEW.md) documents separate Attack/Subdue, Resolve, eight skills, Hold ticks and unconscious recovery; [Captor art/audio](art/CAPTOR_V1.md) records generated packs and foley.

Implemented Summoner: [Summoner rework](design/SUMMONER_REWORK_REVIEW.md) documents eight skills, autonomous owner-linked turns, innate one/all commands, chosen placement, group replacement cooldowns, capacity, sacrifice/empowerment, migration and AI limits. [Summoner art/audio](art/SUMMONER_V1.md) records the packed portrait/icon/effect atlas and six generated sounds. Start a fresh Battle Lab encounter to try the new kit.

Current navigation polish: [Combat controls](design/COMBAT_CONTROLS.md) documents final-path hazard warnings and custom map cursors; [Painted navigation atlas](art/COMBAT_NAVIGATION_V1.md) records the six-icon generation and importer.

Current dev playtesting: [Development runner](design/DEVELOPMENT_RUNNER.md) serves source files with a CSS-only dev client, no automatic reload connection, and no startup build, retains debug tools/dev saves, offers opt-in live editing and preserves timestamped logs. Scorched V3 loops are slowed to 3.2?4.0 seconds following motion feedback.

Current DoT rules: [Combat DoTs](design/COMBAT_DOTS.md) defines Burn 2% and Bleed 5% maximum HP per damage stack, Poison 10% maximum HP per turn with duration stacks, target-end damage/one-stack decay, Burn entry hits and damage resistance. Current fire art: [Scorched V3](art/SCORCHED_V3.md), one sixteen-frame patch per cell, larger upper-left Meteor and impact-gated ground. Older surface notes below record preceding passes.


Current Mage surface art: [Frozen portraits and Scorched ground V2](art/MAGE_SURFACES_V2.md) records two dedicated 4×4 sheets, portrait frost/spread/shatter/thaw, connected feathered scorch, large central cinders and three to five independently phased small fires per cell, exact prompts and browser validation. Replaces the initial ice cage and explosion ground stamps.

Implemented Mage: [Mage rework](design/MAGE_REWORK_REVIEW.md) covers eight elemental skills, Wet/Blister, breakable ice, delayed Freeze, interruptible Meteor, chosen ally enchantments, Burn stack pools, four self/ally-hitting area spells, Scorched paths dangerous to everyone, migration and AI limitations. [Mage art/audio](art/MAGE_V1.md) records the single packed atlas, animated effects and five locally synthesized clips. Current catalogue: 85 executable definitions across twelve Jobs. Numeric playtesting remains open.

Implemented Ranger: [Ranger rework](design/RANGER_REWORK_REVIEW.md) covers eight skills, owner Quarry, Longshot crits, Rapid Fire, Poison stack pools, party-wide Pestilence, allied DoT cashout, stationary Sharpshooter, migration and AI. [Ranger art](art/RANGER_V1.md) documents the packed icons/projectiles and reviewed crop bounds. Numeric playtesting remains open.

Current painted combat props: [Tactical props pack](art/TACTICAL_PROPS_V1.md) covers grounded Caltrops, animated Scrap Turret/projectile/wreckage and reserved Engineer props. Both combat API schemas preserve Knife delivery/strip rotation; placing traps immediately affects occupants.

Implemented Rogue: [Rogue rework](design/ROGUE_REWORK_REVIEW.md) documents eight skills, multiple Quick Actions before one activation-ending main action, traps, positional/stack forecasts, chosen landings, migration and AI limitations. [Rogue art/audio](art/ROGUE_V1.md) records the packed atlas and four generated sounds. October 6: centred Rogue confirmation/attack selection, fixed Knife Exploit dispatch and fixed Caltrops previews with smaller pulsing steel art; see those same documents. Numerical/aesthetic playtesting remains open.

Implemented Monk: [Monk rework](design/MONK_REWORK_REVIEW.md) documents eight skills, full starter combo, technique budgets, readiness, AI and migration. [Monk art](art/MONK_V1.md) records the packed assets and import workflow. Numerical balance remains provisional. Map status columns use 3px gaps; see [Status presentation](design/COMBAT_STATUS_PRESENTATION.md).

Implemented Bard: [Bard rework](design/BARD_REWORK_REVIEW.md) documents planted Songs, lingering and NO LINGER timing, Jeering Verse, Cue the Strike, Song of Peace targeting, Maestro switching, audio cues and current AI/balance limits.

Current skill-bar layout and saved order: [Combat controls](design/COMBAT_CONTROLS.md) covers slotted passives, drag swaps, Arrange, innate/equipment Traits, horizontal acting card and passive readiness buffs. Bloodthirst healing is now 20% max HP per kill.

Current martial kit: [Fighter additions and Barbarian Fury](design/MARTIAL_JOBS_REWORK.md) records the five-slot choices, innate resource, exact costs, healing, death defiance and migration. [Martial art/audio](art/MARTIAL_JOBS_V1.md) records the 4?4 painted packs and eight physical sounds. Battle Lab practice tiers now extend through 20 successes.

Current armor-aware melee: [Flesh contact art/audio](art/FLESH_CONTACT_V1.md) distinguishes organic light armor from chain/plate and Automatons. [Capture rules](design/CAPTURE_AND_STARTING_ROLES.md) now include modest nonlethal damage and separate contact/capture outcomes.

Current melee weapon and net presentation: [Melee families and capture net](art/MELEE_WEAPON_PRESENTATION_V1.md) covers six deliveries, contact timing, matching audio/art and per-tester Battle Lab weapons.

Latest combat controls: [Painted control atlas](art/COMBAT_CONTROLS_V2_PROMPT.md)
records the six matching attack/cursor/hook assets and reproducible import.
[Combat controls](design/COMBAT_CONTROLS.md) and
[Fighter review](design/FIGHTER_COMBAT_REVIEW.md) cover attached Chain Snare,
pull/collision forecasts, wider commands, skill-aware enlarged targeting cursors,
horizontal hover cards, NPC-attached status placement, full collision recovery
and the corrected physical landing audio.

Current buff/debuff UI: [Status presentation](design/COMBAT_STATUS_PRESENTATION.md)
covers readable grouped icons, counts, cursor descriptions, the persistent Stun
star orbit, reduced motion and dry Earthbreaker landing audio. Mage now adds painted ice and Scorched ground; further Barrier redesign remains pending.

Current Fighter review: [Fighter combat and UI audit](design/FIGHTER_COMBAT_REVIEW.md)
records the current full-width map, bottom skills/three-by-two commands,
cursor-following stats, per-victim area forecasts, plus utility dialogs,
Fighter Chain Snare/Earthbreaker/area rally, 150%/200% attack power,
lethal body displacement/collision stun, START tile marking, two-turn armor
fracture and per-target shockwave contact,
contact/collision rules, continuous walking/attack poses, full push/wave recovery,
composed token motion, enemy-playback input lock,
melee structure attacks, boundary contact, one-use Hold Together bonuses,
one-cell/four-turn support tuning, large icon cooldown counters, larger action
descriptions, landing fade, distinct Fighter collision/landing audio and verification. The intermittent corner/door pathing
report is deferred to the rebuild. Prior audits remain historical.
[New Fighter art prompt](art/FIGHTER_V3_PROMPT.md) records the compact six-cell pack.
Mage ground art is implemented; further Barrier art review remains open.

Combat presentation rollout: [Presentation plan](design/COMBAT_PRESENTATION_PLAN.md)
records contact timing, collision bounce, painted ability icons, volumetric
barriers, coherent ground effects and deferred damage typography. The first rollout is implemented;
[Presentation V2](art/COMBAT_PRESENTATION_V2.md) records 72 icons, shared painted effects,
asset imports, verification and remaining manual review.

Current combat feel: [Impact and damage feedback](design/COMBAT_IMPACT.md)
covers collision damage, Ember crossings, typed damage numbers, visible shields,
shared hit/knockback/audio timing and the four new impact sounds.

Current combat controls: [Hotbar, targeting and map controls](design/COMBAT_CONTROLS.md)
covers 1-9/0 skills, ground area previews, combined movement/casting, automatic
25% Guard, status cards, right-drag panning and sequential enemy animations.

Current Job testing: [Battle Lab](design/BATTLE_LAB.md) supports temporary parties
of twelve starting Jobs, matching starter kits, practice presets and five-slot
loadouts without changing roster saves.

Current starting Jobs: [Jobs and character loadouts](design/JOB_LOADOUTS.md)
covers twelve creator choices, matching poor equipment, 72 implemented skills,
five shared slots, learned/equipped IDs and unlocks at 2/5/9 successful contracts.
[Capture and starter equipment](design/CAPTURE_AND_STARTING_ROLES.md) documents
capture rules and starter kits. [The larger design draft](design/STARTING_JOBS_AND_SKILLS_V1.md)
preserves the proposed 96-skill catalogue; unimplemented entries stay proposals.

Current summon/device foundation: [Owner-linked deployments](design/COMBAT_DEPLOYMENTS.md)
documents action/resource rules, profiles, commanded auto attacks and remaining
placement/AI work. [Artwork plan](art/SUMMON_DEVICE_ART.md) records staged art and
portrait-circle presentation for mobile units.

Current tactical foundation: [Abilities](design/COMBAT_ABILITIES.md) and
[zones/forms](design/COMBAT_SPACES.md) cover ordered effects, cooldowns, statuses,
reactions, displacement, zones and reversible forms. Champion kits remain deferred.

Construction sizing: [142-prop audit](art/CONSTRUCTION_PROP_SIZE_AUDIT.md), [overhead chairs and training pack](art/FURNITURE_TRAINING_OVERHEAD_V1.md), and [construction controls](design/BASE_CONSTRUCTION.md) cover calibrated visual sizes, placement-only boxes and preserved movement rules.

Portrait tagging: [Local structured tagger](art/LOCAL_PORTRAIT_TAGGER.md) covers the standalone WD tool, existing race/gender assignments, review, search, exports and deferred game integration. Cloud tagging is paused.

Male portrait rollout: [Batch progress and remaining targets](art/MALE_PORTRAIT_ROLLOUT.md) tracks installed males, staged sheets, generation prompts and visual-review concerns.

Portrait review: [Portrait framing and Portrait Lab](art/PORTRAIT_FRAMING.md) covers the dev art browser, saved circle adjustments, automatic recommendations and per-character overrides.

Current highway rollout: [Authored locations](design/AUTHORED_BATTLE_LOCATIONS.md) describes four Highway Ambush layouts, bank/flank rules and review captures. [Coverage audit](maps/BATTLE_LOCATION_AUDIT.md) lists the remaining generic encounters.

Current garden props: [Overhead garden toolkit](art/GARDEN_TOOLKIT_V2.md) covers crop edging, clutter, shared sizes, the atlas importer and prepared versus active pieces.

Current activity environments: [Garden and training yard dressing](art/ENVIRONMENT_DRESSING_V1.md) records the new overhead ground atlas, all four layout compositions, placement rules and review tools.

Current prop sizes and environment dressing: [Prop size standards](art/PROP_SIZE_STANDARDS.md), [complete prop audit](art/PROP_SIZE_AUDIT.md) and [retired-copy manifest](art/PROP_CLEANUP_20261003.json) cover shared scaling, actual footprints, retirement of the rejected gardening atlas, proposed ground dressing and retained references.

Camp/training/bedding and siege artwork: [Camp prop pack](art/CAMP_PROP_PACK.md) records the new 32-sprite atlas, installation, silhouette recovery and prepared versus functional assets. [Authored locations](design/AUTHORED_BATTLE_LOCATIONS.md) records seven new compact settings and full-camp clutter.

Current map rollout and remaining coverage: [Combat location audit](maps/BATTLE_LOCATION_AUDIT.md) lists authored and generic contract encounters from runtime content; [authored locations](design/AUTHORED_BATTLE_LOCATIONS.md) records the chapel/toll/cache/armory rollout and proposed next batches.

Map review: [Generic contract location review](maps/GENERIC_CONTRACT_LOCATION_REVIEW.md) preserves the original 29-title review, proposed variations, asset gaps and story-origin routing. Roadblocks/command camps and compact beginner sites are now implemented; the remaining sections are proposals.

Current wall generation/connection strategy: [Modular wall art](art/MODULAR_WALL_GENERATION_GUIDE.md) documents the active sixteen-part painted polished-stone kit, equal-cell generation guide, native junction calibration and four full-building comparisons. Rejected polished trials have been retired and archived. Rough stone, timber and metal remain unchanged.

Current building collision/art: [Wall boundaries](design/WALL_BOUNDARIES.md) explains walkable edge-wall floors, blocked crossing/sight, gates and T-junctions; [Building templates](design/BUILDING_TEMPLATES.md) lists the eight reusable plans and four material-specific art kits.

- [Capture and starting roles](design/CAPTURE_AND_STARTING_ROLES.md): live capture weapons, starter kits, balance rules, and the separate proposed level system.
- [Mercenaries and early pacing](design/MERCENARIES.md): persistent hiring, betrayal, rare encounters, starter kits, and quieter regional events.
- [Camp and roster UI](design/CAMP_INTERFACE.md): base sections, inventory, prisoner navigation and item selling.
- [Plain wood wall trial](art/CONSTRUCTION_PLAIN_WOOD_KIT.md): nine-original atlas, 24 mirrored variants, independent horizontal/vertical art, normalization and isolated debug Wall Kit Lab.
- [Construction material kits](art/CONSTRUCTION_MATERIAL_KITS.md): six new nine-original materials, shared snapping geometry, extraction reports and connected-room comparisons.
- [Player base construction](design/BASE_CONSTRUCTION.md): drag/drop terrain painting, arrow-key prop offsets, named directional wall/post/corner/gate assets (T/+ retired), preview optimization, undo/redo and player-owned saved layouts; reusable geometry for a later dev map editor.
- [Relationships](design/CHARACTER_RELATIONSHIPS.md): loyalty, personality, records, conversations and staged roadmap.
- [Prison recruitment proposal](design/PRISON_RECRUITMENT_PROPOSAL.md): original warden, conversation and boss pacing proposals; see the implemented reference below.
- [Prison recruitment](design/PRISON_RECRUITMENT.md): implemented first pass; the proposal above retains deferred ideas.
- [Expedition stamina](gameplay/STAMINA.md): implemented 100-point capacity, gradual recovery, borrowing, deployment costs and UI. [Earlier fatigue proposals](design/FATIGUE_PACING_PROPOSAL.md) retain alternative balance profiles and future quest unlock ideas.
- [Bush concealment](design/BUSH_CONCEALMENT.md): first sightings, roadside ambush presets and map authoring.
- [Combat](design/COMBAT_DESIGN.md): combat rules and outstanding mechanics.
- [Battle Lab](design/BATTLE_LAB.md): dev-only mission/map picker, real approach outcomes, repeatable seeds and isolated test parties.
- [Authored battle locations](design/AUTHORED_BATTLE_LOCATIONS.md): saved workshop/armory/shed plans, bridge variations, door-aware AI, wall alignment, separate art packs and remaining locations.
- [Building templates](design/BUILDING_TEMPLATES.md): eight independent shed/workshop buildings, room-union assembly, anchors/rotation, coordinated structure parts and installation.
- [Combat tools and rank pacing](gameplay/COMBAT_TOOLS_AND_PACING.md): treatment, condition rules, automatic ambush preparation and fixed enemy budgets.
- [Factions and rotating trade](design/FACTIONS_AND_ROTATING_TRADE.md): saved merchant visits, private agreements, ordinary mission choices and personal story consequences.
- [Critical outcomes](gameplay/CRITICAL_SUCCESS_BALANCE.md): current soft caps and stat curves.
- [Gear and loot](gameplay/GEAR_LOOT_DESIGN.md), [item audit](gameplay/ITEM_CATALOGUE_AUDIT.md): current equipment and discoveries.
- [Resource progression](design/RESOURCE_PROGRESSION_PROPOSAL.md), [building audit](design/BUILDING_FUNCTIONAL_AUDIT.md), [buildings WIP](design/BUILDINGS_DESIGN_WIP.md): implemented effects versus proposals.
- [Mission architecture](design/MISSION_ENCOUNTER_ARCHITECTURE.md): roll, dialogue and combat mission forms.
- [Races](reference/RACES.md): reference; runtime content remains authoritative.
- [Browser play](WEB_PLAY.md), [friend trial](FRIEND_TRIAL.md): hosting, login, registration and isolation.
- [Combat effects](art/COMBAT_EFFECTS.md), [map layers](art/MAP_ASSET_LAYERING.md), [item icons](art/EQUIPMENT_ICON_PIPELINE.md): art pipelines.
- [Music prompts](audio/MUREKA_MUSIC_PROMPTS.md), [fire ambience](audio/WOOD_FIRE_AMBIENCE.md): audio.
- [Backlog](../FEATURE_BACKLOG.md), [history](history/MISSION_REFINEMENT_PHASE.md), [repository instructions](../AGENTS.md): progress and documentation upkeep.

## Shared vocabulary

**Loyalty**: command reliability from 0 to 100; independent-turn chance is 100 minus loyalty. **Personality**: independent behavior and broad dialogue voice, separate from combat specialty. **Taste**: an individual preference discovered through conversation or gifts. **Service record**: career counters beginning when tracking was introduced. **Memory**: bounded facts about expeditions the character joined. **Damage per turn**: credited actual damage divided by started combat activations; not real-time DPS. **Private Contracts**: contracts owned by one player. **Soft cap**: a point where further stats become less efficient. **Stat-only limit**: current critical-curve boundary; special overrides need explicit mechanics.

The planned in-game handbook should reuse player-facing definitions and exclude secret quest conditions.

October 5 movement correction: [Combat controls](design/COMBAT_CONTROLS.md) documents direct provisional routes, effective movement-use display and preserved turn range.


October 5 ground effects: [Combat zones](design/COMBAT_SPACES.md) defines committed per-cell damage; [Combat impact](design/COMBAT_IMPACT.md) covers crossing damage labels and animation timing.

October 5 battle input: [Combat controls](design/COMBAT_CONTROLS.md) documents server command validation, immediate movement previews and the buffered Guard/action fix for pending movement requests.

Combined battle submission: [Combat controls](design/COMBAT_CONTROLS.md) covers
100ms movement coalescing, atomic final-position/action commands and scouting
interruptions. [Flesh contacts](art/FLESH_CONTACT_V1.md) records reviewed crop masks,
sword sound layering and slash fade changes.

Movement/entrance refinement: [Combat controls](design/COMBAT_CONTROLS.md) documents
persistent destination intent, fractional reversal animation, nearest doorway
routing and explicit painted-hand door prompts.

Navigation hardening: [Combat controls](design/COMBAT_CONTROLS.md) covers occupied
doors, final-position API validation and repeated-request suppression.
[Development runner](design/DEVELOPMENT_RUNNER.md) explains retained logs and
visible abnormal exits.

Initial house-navigation performance and temporary spatial lookups: see
[Combat controls](design/COMBAT_CONTROLS.md), October 5 latency pass.

Permanent two-sided doorway buttons: [Combat controls](design/COMBAT_CONTROLS.md),
October 5 persistent doorway controls pass.

Job/build brainstorming catalogue: [Starting Jobs and Skills V1](design/STARTING_JOBS_AND_SKILLS_V1.md).
Implemented loadouts: [Jobs and character loadouts](design/JOB_LOADOUTS.md).

Cleric finite restoration and Battle Priest: [Cleric rework](design/CLERIC_REWORK_REVIEW.md). Native generated icons and shared effects: [Cleric art](art/CLERIC_V1.md).

Druid persistent animal forms, movement transitions, global Bleed and living terrain:
[Druid rework](design/DRUID_REWORK_REVIEW.md). Portraits, vine frames and sounds:
[Druid art](art/DRUID_V1.md).

Engineer construction, mounted machines, mines and delayed explosives:
[Engineer rework](design/ENGINEER_REWORK_REVIEW.md). Sprites/audio:
[Engineer art](art/ENGINEER_V1.md).

[Production preparation](design/RELEASE_PREPARATION.md) records dev/release targets, testing-tool exclusions, clean production initialization and the authorized launch reset.


Rat swarms, wolf flanking and personality-aware toll-bandit kits:
[E-rank audit](design/E_RANK_COMBAT_AUDIT.md) and
[combat capability reference](design/COMBAT_CAPABILITY_REFERENCE.md).


E-rank maintenance: [Encounter audit workflow](design/ENCOUNTER_AUDIT_WORKFLOW.md),
[same-map radiant events](design/RADIANT_ENCOUNTERS.md),
[field gear and bear audio](art/FIELD_GEAR_V1.md). Batch 2 is implemented in dev;
personal character-story proposals remain separate.
