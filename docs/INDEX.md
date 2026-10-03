# Fortcamp documentation map

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
- [Relationships](design/CHARACTER_RELATIONSHIPS.md): loyalty, personality, records, conversations and staged roadmap.
- [Prison recruitment proposal](design/PRISON_RECRUITMENT_PROPOSAL.md): original warden, conversation and boss pacing proposals; see the implemented reference below.
- [Prison recruitment](design/PRISON_RECRUITMENT.md): implemented first pass; the proposal above retains deferred ideas.
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
