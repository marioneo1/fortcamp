# Resource, contract and building progression proposal

Status: first implementation, September 30, 2026. The implemented rules below supersede conflicting draft language later in this document. Later sections preserve earlier brainstorming, not promises that every proposal exists.

## Implemented rules

- Solo start remains. Public claims need no team and move into Private Contracts with a 24-hour start window. Assignment happens on start. Roll missions resolve immediately; decisions and battles remain playable. Abandoning does not refund points.
- Each half-hour pool has two one-minute waves, five Contract Points each without rollover. Wave two reveals the second half after 60 seconds; free-for-all begins at 120 seconds with a separate three-point budget. Five Guild Hall allowance upgrades increase only that final budget, to eight. Rank costs: E/D 1, C 2, B 3, A 4, S 5.
- Pool scaling uses game players active in the last seven days: sixteen E and eight D per player. C rolls five candidates at 60%, B three at 35%, A two at 12%, S three at 1%. No guaranteed rare ranks. Added 46 ordinary templates: ordinary catalogue totals E 28, D 16, C 14, B 6, A 4, S 3, plus existing event/story templates. Some gathering contracts offer an optional fight; new E fights are solo-feasible.
- Idle player gathering supplies Wood, Stone, Scrap, Food, Medicine. Focused hourly rates before bonuses: 18,16,10,12,3; balanced splits time equally. Expeditions pause work. Assigned idle workers add yields; relevant proficiencies add 15% per level. Production buildings add 30% per level, with three levels and up to three slots. Offline storage: twelve hours plus six per Storage Shed. Settle time before transfers/upgrades.
- Cloth balances migrate once to Stone. Construction and mission material rewards use Stone. Unrelated missions lose resource bundles, while relevant gathering and special chain windfalls remain. Guild Hall costs 30 Wood, 12 Stone, 8 Scrap; opens D, then paid upgrades progress through C/B/A/S. Foundational production/kitchen/workshop blueprints are dependable. Barracks, Alchemy Lab and Arcane Sanctuary also have paid research routes.
- Base expands 12x8 -> 16x8 -> 16x12 -> 20x12 without moving buildings. Ordinary hires cost 30 Gold, rising by 20 per hire. No free starter recruit. Housing limits remain deferred.
- Relevant work and successful expeditions build proficiency practice: Basic 12, Skilled 60, Expert 180, Master 480. Training is optional acceleration. Basic may use a local instructor for eight Gold; higher levels require an idle teacher with that target level and the existing manual/tome/codex. Natural work advancement does not require those items. Combat proficiency remains separate from production work.
- Optional lasting meals: Trail (four Food, +1 Survival for one expedition), Study (five Food, +8 noncombat practice), Rest (six Food, injury reduced 30 minutes). No starvation or automatic roster food drain. Solo E critical failure still incapacitates, but beginner rest takes two minutes; later recovery uses existing medical/tent rules.
- Three faction shops have relationship gates 0/15/35/65, earning three relationship on relevant success, five on critical success. Gold cannot bypass gates. Faction stock replenishes daily. Personal merchant: independent 45% daily arrival roll, three limited-stock offers, 12% chance of replacing one with a merchant-exclusive rare ring. Stock is saved and deterministic per player/day; reloads do not reroll. Visits have a 24-hour browsing window from discovery; some players get no visit. Basic Food/Medicine purchases do not require a merchant.
- Twelve E/D/C contract-exclusive items offer real Guard, Pathfinder, Scout, Engineer, Graveward, resistance or other existing effects. Each belongs to one contract at 3% success / 5% critical-success drop chance; battle-specific loot requires finishing its encounter. Excluded from general, higher-rank and shop pools. Existing icons are reused; no new socket/card system.

## Follow-up

Track real solo time to Guild Hall, gold vs hire costs, rare-drop returns and allowance usage before finalizing balance. Housing, refinement/crafting, richer recipes, teacher selection UI, faction private-contract unlocks and merchant sales remain pending. New combat contracts reuse coherent existing map templates and props; no new art was required.


Confirmed user constraint: the player starts SOLO, with no helper or free starting recruit. All early progression must work with the player character alone. Recruited workers improve production later; no foundational service may require extra characters to function.

## Agreed direction and open numbers

- Claiming public missions moves them to Private Contracts without assigning a team. Assignment happens when starting them.
- Proposed opening: five allowance units in the first wave, another five after one minute, then free-for-all with a separate per-pool allowance. Only that final allowance is increased by building upgrades. Rank-dependent allowance pricing is under discussion, not implemented. The duration of wave two and rollover rules remain to be settled.
- Increase E-rank supply substantially; the current first-cohort 12 plus one per additional player is inadequate relative to D's seven per player. Expand actual E templates alongside instance count.
- Routine construction resources should predominantly come from base work. Resource-specific missions, especially E-ranks, remain worthwhile sources; unrelated quests should not hand out bundles of wood, scrap, cloth, medicine and food.
- Equipment, plausible gold payment, recruits, blueprints and story/faction opportunities are important mission rewards. Keep separate drop checks; an ordinary success does not guarantee special loot.

## Proposed resource roles

Wood and Stone are primary construction inputs. Salvage (existing Scrap, potentially relabelled) supports tools, engineering and equipment work. Gold pays for relevant services and purchases. Food supports cooking/expedition preparation. Medicine supports recovery and medical items. Remove Cloth as a top-level construction currency; fabric can later exist as a specific crafting item if it has a useful purpose.

Stone is a new economic role, not a text replacement for every cloth occurrence. A future migration must preserve player value and separately review construction recipes, mission rewards, saves and UI. Existing item references to clothes remain valid.

## Proposed starter production

- Accessible logging clearing -> blueprint/unlock for Lumber Mill.
- Accessible stone outcrop -> blueprint/unlock for Quarry.
- Accessible salvage patch -> Salvage Yard.
- Accessible foraging patch -> Garden or other food production upgrade.

Basic sites require no rare blueprint. The player starts solo; the earlier starter-helper suggestion is withdrawn. Proposed baseline is an idle Camp Work setting: balanced gathering of available basic resources, or focus on a chosen resource. The player performs that work during elapsed idle/offline time. Expeditions pause their contribution; resolve accrued work before departure and restore the chosen setting when available again. No invisible extra workers or simultaneous use of the player in an expedition and production. Balance rates and starter supplies around this single-character constraint.

Production accumulates while offline and is collected automatically on return/ordinary state updates. No repeatedly clicking a gather button. Initial offline-storage proposal is about 12 hours, expandable through storage, with no offline starvation or punishment. Settlement must account for time under the old assignment/rate before worker transfers or upgrades, preventing retroactive production exploits. Active missions and building work cannot use the same unit simultaneously; claiming does not occupy units. Camp Work is a baseline scheduling setting, not a new occupied worker slot that must be manually cleared before each mission.

Upgrades first improve output and then staffing capacity (e.g. 1 -> 2 -> 3 slots). Specialists and relevant gear give bounded production advantages. Do not reward arbitrarily large rosters with unlimited resource growth. Gold purchases can bridge specific shortages but should not outperform all local production or allow resale profit loops.

Solo safeguards: player-operated basic cooking and construction; slow rest recovery requiring no purchased medicine; safe early earning/resource contracts alongside solo-feasible combat; no early mandatory two-person party or staffed service. Recovery cannot create a deadlock where medicine is required to recover and the only character must be healthy to obtain medicine. Basic recruitment should have a dependable later route (such as an affordable hire or authored introduction), while special recruit drops remain probabilistic. These acquisition options are proposals and do not award a starting companion.

## Proposed reward policy

- Logging/salvage/foraging: appropriate resources, optional tools or production leads.
- Paid protection/delivery/bounties: gold, optional relevant equipment.
- Bandits/goblin fights: carried equipment, coin where plausible, captures, relevant faction loot; supplies only when an actual supply cache is recovered.
- Hunts: food or creature materials when appropriate, optional trophies.
- Ruins: relics, equipment, knowledge or blueprint opportunities.
- Medical work: medical supplies where physically recovered, payment where commissioned, relevant training/recruits.

Resource expeditions supplement production or accelerate a chosen project. Higher-rank missions primarily broaden equipment, character and story opportunities rather than becoming giant universal construction-resource payouts. Basic progression blueprints must have a reliable acquisition route (authored personal introduction, research or purchase); advanced/exotic ones can remain rare drops. Duplicate blueprints need a useful treatment, proposed research/trade value, without gold arbitrage.

## Proposed early pacing

Starter session: use base jobs, complete safe contracts and a short fight, obtain useful gear, choose an early camp investment, and reach Guild Hall construction through ordinary play. Guild Hall versus production/housing should be a meaningful choice rather than an obligatory click order.

Next sessions: specialize staffing, improve production and housing, develop a second build, and approach C-rank access. Later ranks need demonstrated capability/relevant accomplishments plus affordable construction inputs, rather than increasingly long passive waiting alone. These are pacing goals, not promises about current cost curves.

Model at least short occasional sessions and frequent sessions, counting passive input, failed missions, claim-point costs, optional paths, building spend, medical demand and loot variance. Treat the 30-minute refresh and five-plus-five opening as potential high throughput; do not tune costs around perfect attendance or spending every claim.

## Proposed E-rank content batch

Expand toward 24-30 distinct templates initially, approximately 45% pure roll, 25% branching with possible combat, 30% deliberate short combat. This is a proposed content mix, not a constraint on every refresh.

Examples:

- Rats in the Storehouse: short known combat; protect food sacks, retrieve intact provisions, chance of useful pest-control equipment.
- Roadside Toll: short known fight with ordinary bandits; bounty/payment, recovered gear and possible capture.
- Wolves at the Fence: defend a worker or enclosure; drive off or defeat attackers, retrieve appropriate creature loot.
- Timber Across the Creek: roll for a small load; an optional larger load enters a dangerous section, with a possible short fight.
- The Locked Tool Shed: salvage roll with an optional risky route, tools and resources matching the scene.
- Herbs Behind the Wall: safe collection versus a harder route toward medical supplies, possibly involving creatures.
- Market Errand / Survey the Outcrop / Camp Repairs: plentiful pure-roll work with relevant payment, local relationships or modest materials.

Use authored encounter families (storehouse, roadside, forest clearing, salvage yard) with coherent terrain and objective-specific props. Early encounters must be feasible for starter parties, allow retreat and support existing capture/loot mechanics. Do not label a mission pure-roll if it can secretly force combat; the board's general warning and optional bodyguards still apply to appropriate investigation/branching forms. Avoid pretending unimplemented trap, stealth or dungeon mechanics already work.

## Implementation order

1. Agree economic roles and acquisition rules; simulate candidate costs/rates.
2. Add Stone, recipe/save migration and starter production with safe settlement.
3. Implement public ownership separate from expedition start, wave budgets and free-for-all accounting.
4. Expand E templates, accessible supply and short encounter maps; revise actual reward blocks alongside their displayed text.
5. Playtest early sessions, then tune higher-rank access, staffing and claim upgrades.

## Building review: proposals, not requirements

The user explicitly confirms BUILDINGS_DESIGN_WIP.md is a collection of tentative ideas, open to rejection, merger and redesign. No listed system should be implemented merely because it appears in that file.

- Guild Hall: mission rank visibility and separate free-for-all allowance upgrades. Avoid making it the only worthwhile first building.
- Housing: retain meaningful capacity/rest benefits, but do not delete or permanently deny rare recruits because beds are full. Consider temporary guest accommodations with transparent disadvantages; exact capacity rules remain open.
- Starter work sites/production upgrades: priority foundation for the new resource economy, with no rare-blueprint bootstrap dependency.
- Medical Ward: recovery, preserving slower baseline recovery without it. Keep an accessible medical supply source.
- Workshop: engineering/tools and eventual salvage/refining. Blacksmith may initially be a workshop specialization instead of another compulsory small structure.
- Training Grounds: bounded, targeted training. Blanket passive gains for every undeployed character risk rewarding roster hoarding and eliminating choices; evaluate assigned trainees instead. Existing proficiency items remain useful.
- Kitchen and Dining Hall: combine into one cooking building initially. Expand with a dining upgrade if it provides meaningful later choices.
- Storage: expand offline accumulation capacity; do not turn every resource into mandatory frequent collection.
- Prison: existing storage foundation; deeper recruitment/warden behavior remains deferred as previously requested.
- Watchtower, raids and Treasure Room: later systems. Avoid involuntary loss of scarce loot while offline or an accelerating rare-reward loop available only to established players.
- Beast facilities, arena and deep crafting: defer until their underlying gameplay exists.
- Private Contracts: distinguish ordinary local repeatable jobs from valuable earned faction/story chains. The latter should not be broadly weaker than public contracts just because they are private. Avoid unlimited instant repeatable gold/resource loops outside public allowances.

## Proposed base expansion

Current base grid is 12 x 8. Preserve existing placed structures and coordinate origins. A first expansion could add an adjacent strip (example 16 x 8); a later one adds depth (example 16 x 12). Sizes and costs are illustrative. Validate client layout, bounds and stored coordinates before any implementation; combat map sizing is a separate system.

Purchase a plot/clear land using reasonable wood/stone/gold costs and an appropriate camp milestone. Optional authored clearing expeditions can grant a discount or an alternative route, never requiring a random blueprint to escape lack of space. Buying space should be a choice between a wider base and improved existing facilities, not an arbitrary long construction wait.

Distinguish population capacity (housing), building staffing (available characters) and physical room (plots). Avoid forcing all three upgrades simultaneously for the same early milestone. Upgrade existing structures within their footprint first, allowing dense and spacious base layouts. Keep relocation forgiving so layout experimentation does not destroy invested resources.

Do not charge upkeep per unused tile. Do not introduce raids simply because the base grew. Decorative paths/gardens can be supported later, without silently competing with essential production. Base role and plot expansion should be readable in one management screen; UI work comes after the economy and persistence model are settled.

## Faction trade and visiting merchants

User-requested direction, not implemented: gold purchases faction goods, with better relationships unlocking a broader and potentially rarer selection, including faction-specific goods. Improving relationships should reveal new equipment techniques, recipes, blueprints and useful consumables, rather than merely bigger stat bonuses or discounts. Gold pays for eligible offers; spending gold alone does not bypass relationship requirements. Baseline trade remains useful before high reputation.

User-requested direction, not implemented: a merchant may visit an individual player with ordinary goods and a chance of rare or merchant-exclusive offers. Proposed safeguards: persistent player-specific inventory/prices, no reroll on reload, limited stock and bounded replenishment, and no buy/sell profit loops. A visit triggered during absence should be presented on return with a reasonable browsing window, rather than requiring constant checking. Exact visit frequency, duration and rarity probabilities remain open.

Faction and merchant exclusives must have explicitly authored pools. Do not leak mission-chain relics, capture-only loot or unique Champions/Celestials into a generic shop. Most basic supplies should have dependable access; randomness is for interesting extras. Shopping, selling and faction offers should share one readable Trade interface, with unavailable reputation tiers previewed clearly. Stronger relationships need not guarantee a rare roll on every shop refresh.

## Food and cooking without a farming chore loop

Food sources proposed for the first version: starter foraging, a passive Garden/Farm upgrade, hunting contracts, recovered provisions where appropriate, and ordinary merchant/faction purchases as a fallback. Farming is a production building, not a separate field-by-field simulation. Staffing and upgrades improve output/capacity; no manual sow/water/harvest schedule, crop death while offline, fertilizer/weather bookkeeping or mandatory livestock systems initially.

Keep one generic Food resource for routine cooking. Hunting can sometimes award distinct creature ingredients; recipes using rare ingredients can be optional later content rather than requirements for every meal. Do not make routine food preparation require several new resource currencies.

Kitchen converts Food into optional consumable meals, with a small initial recipe set and limited preparation bonuses. Proposed identities include training support, expedition endurance/recovery support and specialist-check support. Exact bonuses need simulation; do not stack unlimited meals or make meals compulsory for normal mission odds. Meals should persist until use rather than expire while players are absent. Cooking in batches and optional recurring production with a visible Food reserve prevent repetitive clicking and accidental depletion.

Do not implement starvation, offline deaths or automatic roster-wide food drain in this first pass. A large collection must not become an escalating punishment for recruiting characters. Additional farm depth can be considered only if players enjoy this simple layer and want more management.

Reference for iterative economy design: https://www.gdcvault.com/play/1028982/Building-Sustainable-Game-Economies-The.
