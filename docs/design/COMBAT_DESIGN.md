# Fortcamp Tactical Battle Design

> This document combines implemented combat foundations with future design proposals. The live game now uses painted terrain and props, reusable scenario maps, defense preparation, and authored decision encounters. Later release proposals below are historical planning, not a statement that only one mission exists.

## Implemented vertical slice

Goblin Warcamp now implements the 8×8 persistent battle, portrait tokens, provisional movement, weighted elevation, manual commands and hotkeys, server-authored contextual actions, ranged and magic weapon skills, terrain blocking and line of sight, shallow water, flight-only pits, destructible palisades and rubble, visible status definitions, lethal and nonlethal defeat, unconscious units and corpses, carrying and dropping bodies, Strength-and-weight-based throwing of bodies and portable objects, free body handoff at exits, individual extraction, Retreat All pathing, boss-triggered panic and pursuit choices, automatic secured-field recovery, corpse-scaled equipment and coin, captives, alarm reinforcements, three auto-battle tactics, instant resolution, battle reports, and normal mission reward integration described below. The remaining sections guide expansion to later encounters.

## Feasibility

A top-down grid battle layer is a medium-to-large feature, but it fits the current FastAPI and browser client architecture. Rendering an 8×8 grid and portrait tokens is the easy portion. The main work is a deterministic combat engine, enemy behavior, encounter data, skill definitions, save recovery, and enough encounter variety that positioning matters.

The first release should be a vertical slice attached to one mission, preferably Goblin Warcamp. The existing mission resolver remains available for missions without combat and as an auto-resolve option where appropriate.

## Combat promise

Combat should answer a tactical question rather than repeat a power comparison. Every battle needs at least two of these:

- terrain that changes movement or line of sight;
- an objective besides eliminating every enemy;
- a time or reinforcement pressure;
- interactable objects;
- a retreat or negotiation route;
- enemies with behavior the player can exploit;
- a party composition that changes the available plan.

An encounter that cannot meet this standard should remain a narrative mission.

## Board and tokens

- Use an 8×8 square grid for the first implementation. It remains readable on desktop and can scroll or scale on smaller screens.
- Character tokens use the existing 192×192 portrait thumbnails, cropped with `object-fit: cover` inside a circular or rounded-square frame.
- The frame carries team color, health, status icons, facing or intent, and a small role marker. The portrait remains the identity layer.
- Clicking a token opens the full portrait and combat sheet without replacing the battlefield.
- Terrain tiles are code-rendered CSS or SVG layers. Bespoke battle art is optional.

## Turn structure

Use alternating activations rather than an entire player phase followed by an enemy phase. Initiative is derived from AGI with bounded equipment and perk modifiers. A unit receives:

- movement points;
- one main action;
- one quick action when granted by a skill or item;
- one reaction per round;
- an optional facing-independent guard zone.

Alternating turns prevent a fast team from deleting the opposition before it acts and make enemy intent meaningful.

## Small skill loadouts

Each deployed character brings a compact loadout:

- one weapon action;
- two equipped active skills;
- one reaction;
- one passive;
- race, Champion, Celestial, or story-perk interactions.

Skills come from equipment, perks, race, and individual identity. Characters do not learn a growing list of strictly stronger copies. Changing a weapon or perk changes the available decisions.

Examples:

- a spear attacks two tiles away and can Brace against movement;
- a shield grants Interpose but lowers movement;
- a bow gains damage from clear lines and elevation;
- a grimoire changes spells according to nearby terrain;
- Bannerbreaker can reveal a raider officer's command radius;
- Titan Speaker can turn a beast neutral instead of damaging it;
- Riftwalker can exchange positions through unstable tiles.

## Attributes without linear progression

Attributes describe strengths and unlock mechanics:

- STR: force, heavy weapons, knockback, carrying, armor break;
- DEX: precision, ranged weapons, traps, delicate interactions;
- AGI: movement, initiative, disengagement, reactions;
- VIT: health, guard, resistance to displacement and attrition;
- INT: spell shaping, constructs, analysis, area control;
- LUK: risky effects, unusual drops, event manipulation, recovery from bad states.

Use soft scaling. Most direct bonuses should flatten after the useful range rather than multiply forever. A high attribute unlocks reliability and special interactions; it should not make every lower-stat character obsolete.

## Build diversity rules

1. Equipment tiers increase their option budget more than raw damage. A legendary item may offer two unusual actions and a drawback rather than twice the numbers.
2. Strong effects require positioning, setup, a cooldown, a resource, or exposure to counterplay.
3. Defense has different forms: armor, evasion, wards, interception, healing, concealment, and control resistance.
4. Damage builds differ through reach, burst, sustained pressure, area denial, reactions, summons, and status exploitation.
5. No universal best-in-slot item. Each powerful item should surrender something another build retains.
6. Enemy mechanics test different tools. A build that dominates packed goblins should not automatically dominate a mobile Voidsent or a titan.
7. Perks and equipment can open story actions during battle, keeping narrative and tactics connected.

## Auto-battle

Manual and auto-battle must use the same deterministic engine. Auto-battle is an AI controller, not a separate result formula.

Players choose a tactic for each character:

- Hold Ground;
- Protect Ally;
- Focus Target;
- Control Space;
- Support and Recover;
- Seek Objective;
- Avoid Risk.

They can also set retreat thresholds and skill priorities. The battle can run instantly, step quickly, or pause for manual control. Because the same commands and rules are used, an auto-battle replay can explain why a unit moved or selected a skill.

## Mission integration

Only templates with a `combat_encounter` definition open the tactical layer. Other missions continue through the narrative resolver.

A mission can contain pre-battle routes:

- diplomacy completes the objective without combat;
- scouting changes deployment or reveals enemies;
- an equipped item opens a secret interaction;
- an item can deliberately provoke a fight with different enemies or rewards;
- failure in negotiation can start combat with worse positioning;
- retreat can produce a partial narrative outcome instead of a generic loss.

Hidden route conditions remain server-side. The client receives only the actions currently available and enough text to understand what each choice risks.

## Example vertical slice: Goblin Warcamp

- 8×8 palisade map with a gate, watch platform, prisoner pen, cookfire, and alarm horn.
- Party deploys two characters outside the south wall.
- Tank and DPS remain useful roles, but stealth, goblin identity, explosives, ranged fire, and diplomacy create different plans.
- Objectives can be defeat the chieftain, free captives, steal the route map, or escape after sounding the alarm.
- Goblins use morale. Removing an officer, displaying a war token, or opening the prisoner pen can change their behavior.
- A Breaching Charge opens the wall quickly but calls reinforcements and can reveal a secret Black Banner supply route.
- Auto-battle tactics can prioritize captives, the horn, the officer, or survival.

## Technical shape

The server owns combat state and validates commands. A battle stores its seed, map, units, turn order, command log, and current snapshot. The combat engine is a pure deterministic module so the server, tests, replays, and auto-battle all receive identical results.

Suggested pieces:

- `combat_content.py`: skills, enemies, terrain, and encounters;
- `combat_engine.py`: movement, targeting, actions, status effects, and victory rules;
- `combat_ai.py`: tactic evaluation and auto-battle commands;
- `BattleInstance`: persisted active battle and replay log;
- battle API routes for start, command, auto-step, auto-resolve, and resume;
- a battlefield screen in the existing frontend.

The mission should be claimed before a battle starts. Completion rewards and story text still flow through the normal mission result system, with combat facts added to the aftermath.

## Recommended implementation order

1. Deterministic engine with movement, line of sight, basic attacks, cover, health, and objectives.
2. Goblin Warcamp map with three player actions and three enemy types.
3. Portrait-token battlefield and manual controls.
4. One auto-battle tactic per broad role plus replay explanations.
5. Mission outcome, injuries, rewards, and narrative integration.
6. Branching diplomacy, item-triggered fights, reinforcements, and secret objectives.
7. Additional encounters only after the first battle produces multiple viable strategies in tests and play.

## September 2026 combat expansion brief

This section records the intended direction after the Goblin Warcamp prototype. These mechanics should be implemented as reusable encounter rules rather than special cases tied to one map.

### Action language and interface

Every action must expose a short description on hover and selection, including its range, target type, commitment cost, and important status effects. Guard ends the activation and halves the next incoming hit; End Turn simply commits the current position without another benefit. Interact is a contextual action for adjacent objectives, terrain, doors, switches, bodies, and movable objects. The interface should only emphasize valid targets for the selected action.

The battle view should use most of the screen, show the current and upcoming turn order, distinguish bosses with a crown and frame, and change targeting feedback by action. Skills and spells should live in a compact loadout panel rather than growing into a permanent list. A unit can eventually have a weapon action, two to four equipped skills or spells, contextual interactions, and universal actions such as Guard.

### Consciousness, defeat, and lethality

Health and consciousness are separate concepts. Reaching zero health normally produces one of three states chosen by the attack and target rules:

- **Unconscious:** alive, unable to act, can be stabilized, carried, captured, or extracted.
- **Dying:** alive but at risk of becoming a corpse after a countdown or further damage.
- **Dead:** becomes a corpse object and cannot be restored by ordinary medicine.

Weapons and skills carry a damage intent: lethal, nonlethal, or selectable. Blunt weapons, restraint tools, sleep magic, shock effects, choke techniques, and some unarmed attacks support nonlethal takedowns. Blades and destructive spells default to lethal unless the skill explicitly says otherwise. Bosses and unusual creatures may have resistance to knockout effects, but mission-critical targets should never rely on an unexplained immunity.

### Status-effect vocabulary

Statuses use visible icons with a hover card containing the exact rule and remaining activations. Application chance, duration, stacking, resistance tags, and removal conditions belong to the weapon or skill that applies the status. A stronger item should usually improve reliability, duration, area, or tactical setup rather than simply applying every condition.

- **Stun:** loses the next activation. Short and powerful; normally requires impact, setup, or a limited skill.
- **Sleep:** cannot act until damaged or cleansed. Excellent control but fragile and resisted by tireless creatures.
- **Poison:** armor-ignoring damage at activation start. Usually longer-lasting and weaker per tick than Burn.
- **Bleed:** physical damage after movement or physical exertion. Strong against mobile living targets; ineffective against constructs and most undead.
- **Charm:** temporarily changes allegiance relative to the source. Rare, resisted by discipline, and usually breaks on direct harm from the charmer.
- **Confuse:** offensive actions may redirect to another valid nearby target. It creates risk without guaranteeing a skipped turn.
- **Berserk:** must attack when possible and treats every nearby unit as hostile. It increases offensive pressure while removing control.
- **Freeze:** prevents movement and increases impact damage; fire removes it. It does not automatically remove the main action.
- **Burn:** damage at activation start, suppresses Regeneration, thaws Freeze, and can ignite tagged terrain.
- **Blind:** sharply reduces physical ranged accuracy and reaction range. Area attacks and explicitly sightless magic can ignore it.
- **Bind:** prevents movement until broken, removed, or expired. Unlike Freeze, it does not create impact vulnerability.
- **Slow:** reduces movement and delays initiative. It preserves actions, distinguishing it from Stun and Paralyze.
- **Paralyze:** checks separately for lost movement and lost main action at activation start. Unreliable but potentially severe.
- **Mute:** prevents spells with a verbal component. Every spell declares components, so physical techniques and silent magic remain usable.
- **Fear:** prevents voluntary movement toward the source and reduces accuracy against it.
- **Vulnerable:** the next damaging hit ignores some armor, then consumes the status.
- **Regeneration:** restores health at activation start and is suppressed by Burn or specific anti-healing effects.

Immunity should follow understandable tags such as mindless, construct, incorporeal, tireless, bloodless, or fire-formed. The UI must show an immunity when a target is inspected; it should never surprise the player only after an effect fails.

### Carrying, bodies, and extraction

An adjacent conscious unit can use a contextual **Carry** interaction on an unconscious ally, unconscious enemy, or corpse. Carrying occupies the unit's hands or a carry slot, may reduce movement, may prevent some skills, and can expose the carrier to reactions. Current carrying capacity is `max(1, floor(STR / 3))`; movement penalty is `clamp(0, 3, payload weight - capacity + 1)`. This lets a strong unit handle a goblin or stone freely while heavy bodies and crates burden weaker carriers.

Dropping currently uses the main action. Throwing is a dedicated main action with short range and collision damage to the target; an unconscious thrown body also takes collision damage. Throw range is `clamp(1, 5, 1 + floor(STR / 4) - max(0, weight - 2))`. Impact is the payload's base impact plus `floor(STR / 3)` and `floor(weight / 2)`, then the target's armor applies. Body base impact is `2 + weight`; portable objects declare their own weight, impact, carrying penalty, and whether they break when thrown. The Goblin Warcamp currently demonstrates this with a heavy breakable supply crate and a light reusable stone. Knockdown, explosive payloads, and grappling conscious targets remain later extensions.

Leaving combat happens through extraction tiles rather than a global retreat button. Each encounter defines one or more extraction regions: an outdoor map may use part of an edge, a dungeon may use a doorway or staircase, and a surrounded encounter may initially have none. A unit on an extraction tile can leave alone or carry another unit out. The mission evaluates who and what escaped, allowing partial success, rescue, capture, corpse recovery, or abandonment.

### Retrieval and capture missions

Retrieval encounters do not require eliminating every enemy. Examples include:

- extract a named unconscious prisoner;
- subdue and capture a target alive;
- recover a fallen guild member or Champion;
- steal an object and escape before reinforcements arrive;
- retrieve a corpse for burial, identification, resurrection, or proof;
- rescue several civilians while deciding how many risks to take.

Mission resolution should read extracted entities and objectives directly from combat state. A living rescue, unconscious capture, corpse recovery, and empty-handed escape produce different narrative outcomes and rewards.

Corpses can retain a controlled loot manifest. Humanoid equipment may become recoverable gear; beasts may yield food, hide, reagents, trophies, or quest materials. If hostile resistance remains, recovering a specific body or prisoner requires extraction. Once the enemy force is defeated or entirely panicked, the battlefield is secure and all eligible bodies and unconscious prisoners are gathered automatically. This avoids post-victory cleanup while still making the number and type of fallen enemies matter to rewards.

### Terrain vocabulary

Maps are rectangular and data-driven. They may be square, narrow, irregular through void tiles, or several times larger than the prototype. Large maps need camera pan and zoom, a minimap, and tile culling so the DOM does not scale directly with every off-screen tile.

Tiles carry reusable properties:

- ground material such as grass, soil, stone, timber, metal, snow, or sand;
- movement cost and whether the tile can be entered;
- elevation level and ramp, stair, ladder, or climb connections;
- cover and line-of-sight height;
- liquid depth, current, burning, poison, ice, or other hazards;
- destructibility, health, armor, and replacement tile;
- support rules for pits, ledges, bridges, roofs, and collapses.

Elevation should be discrete and readable. Use height shading, raised tile faces, edge lines, small elevation labels while targeting, and shadows cast toward a consistent screen direction. Ranged attacks gain a modest line-of-sight or range advantage from height rather than a universal damage multiplier. Falling, forced movement, and collapsing support create situational damage.

Physical ballistic attacks use elevation directly. Attacking upward loses 12 percentage points of accuracy per level, capped at a 40-point penalty. Attacking downward gains 8 points of accuracy and one damage per level, capped at 20 accuracy and three damage. Extreme elevation can block line of sight.

Uphill movement costs two movement points per elevation level gained. A single step can climb at most two levels, so ground cannot connect directly to elevation three or four. Elevation four requires a traversable elevation-two approach and costs eight movement in total: four to climb from zero to two, then four to climb from two to four. Descending currently costs one point per tile but cannot drop more than two levels in one step; falling, jumping, ladders, flight, and controlled descent will add explicit exceptions later. An `impassable` terrain flag remains available for sheer surfaces that cannot be climbed regardless of nearby height.

Magic never inherits the physical ballistic rule automatically. Every spell declares an elevation rule such as `ignore`, `ballistic`, `line_of_effect`, `grounded`, `arcing`, or a spell-specific resolver. Arc Bolt currently declares `ignore`; future lightning, falling-projectile, ground-wave, and teleport spells can therefore behave differently without exceptions hidden in the engine.

Water can slow ordinary movement, block fire, conduct some magic, carry floating objects, and require swimming in deep sections. Pits and void tiles cannot be entered without flight, jumping, bridges, or forced movement. Barricades are targetable terrain objects with health, armor, material tags, and a destroyed replacement state. Doors, walls, trees, and cover use the same destructible-object interface.

### Visual target

An Elin-like readable tile presentation is feasible without a dedicated artist. The practical route is a small original tileset rather than generated full battle scenes. Start with a consistent top-down or shallow three-quarter projection and create modular 64–128 px assets for ground, edges, walls, water animation, props, elevation faces, hazards, and objective markers. CSS can continue to provide selection, path, range, faction, and status overlays above those textures.

Generated art can help produce source material, but it needs an asset pipeline: fixed camera angle, fixed light direction, transparent background, strict tile dimensions, seamless edge requirements, palette control, and manual approval before inclusion. Code-generated noise, gradients, masks, and autotiling can supply variation so a dozen approved base tiles produce many combinations. Portrait tokens can remain above the environment until full-body unit sprites are worth the cost.

Recommended visual milestones:

1. Replace flat prototype colors with an original grass, dirt, timber, stone, water, and cliff tile kit.
2. Add autotiled borders, animated water, props, shadows, and elevation faces.
3. Add camera pan, zoom, minimap, and rendering for maps larger than the viewport.
4. Add destructible-object states and hazard animation.
5. Consider directional unit sprites only after the tactical language is stable; portraits remain a valid long-term identity layer.

### Implementation order for the expansion

1. Extraction regions and map-based Leave action; remove the global retreat shortcut after this works.
2. Unconscious, dying, corpse, and nonlethal attack rules.
3. Carry, drop, rescue, and capture objectives.
4. Contextual action menu replacing the single-purpose Interact button. **Implemented for objectives, bodies, carried units, and extraction. Destructible terrain uses the standard Attack mode.**
5. Data-driven rectangular maps, void tiles, camera pan and zoom. **Engine and browser viewport foundations implemented.**
6. Terrain costs, water, pits, destructible barricades, and elevation. **Initial rules and Goblin Warcamp demonstration implemented: weighted water and rubble, Burn removal in water, flight-only pits, Attack-targetable barricades with health/armor/destruction, line-of-sight changes, and elevation.**
7. Throwable objects and bodies after carrying and collision rules are stable. **Initial implementation complete: portable-object pickup/drop, body and object payloads, STR-versus-weight range and impact, landing tiles, breakable payloads, `[T] Throw` targeting, and combat explanations.**
8. First retrieval mission and first live-capture mission. **Implemented in The Captive Cart: extract wounded Courier Lysa to secure the primary objective, optionally subdue and extract Cartmaster Vrak alive, and carry out the stolen dispatch satchel. Extracting Lysa opens the leave-or-continue decision; securing the battlefield gathers eligible objectives automatically; recovering all three produces Critical Success; losing Lysa produces Critical Failure.**
9. Original modular environment tileset and map-authoring tools. **Initial foundation implemented: six code-native ground materials with deterministic variation and automatic borders, animated water and fire, rectangular square-tile rendering, map themes and an in-battle legend. Encounters now consume validated declarative blueprints with painted rectangles or individual tiles, terrain props, elevations, voids, and exits. `tools/validate_battle_maps.py` validates every authored map; `BATTLE_MAP_AUTHORING.md` documents the format. Future art assets can replace individual material renderers without rewriting maps or combat rules.**

### Loyalty and independent action

Every non-player recruit eventually receives Loyalty from 0 to 100. The player character has no Loyalty score because the player directly embodies that character. Loyalty 100 guarantees obedience; lower Loyalty creates a bounded chance that the unit replaces a command with a personality-consistent independent action.

Use a curved base chance rather than a linear punishment:

`independent_action_chance = 20% × ((100 - loyalty) / 100)²`

This produces approximately 20% at Loyalty 0, 11.25% at 25, 5% at 50, 1.25% at 75, 0.2% at 90, and exactly 0% at 100. Ordinary recruits should enter around 60–80 unless their story says otherwise, keeping disobedience unusual. Mission context can modify the result slightly: ordering a unit to abandon a loved one, attack its faction, enter certain death, or violate a defining perk raises resistance; rescue, shared history, fulfilled promises, compatible leadership, and relevant perks reduce it.

Independent behavior should remain intelligible rather than randomly malicious. A cautious unit may Guard or seek cover, a compassionate unit may rescue an ally, an ambitious unit may pursue a valuable objective, and a hostile captive may attempt extraction. Before confirming a command, the UI should show the current obedience percentage and any visible reason for unusual resistance. Charm, Confuse, Berserk, Fear, and enemy control remain separate status mechanics and never masquerade as Loyalty.

Loyalty changes through consequential events, not repetitive gifts: surviving missions together, rescue, fair reward, personal quests, compatible decisions, abandonment, friendly fire, broken promises, faction conflict, and mistreatment. Gains and losses should be capped per mission to prevent instant farming or a single incidental action permanently ruining a character.

## Map camera QoL (2026-10-01)

Battles and defense preparation open in Fit map mode: preserve the map aspect ratio and choose the largest size that fits both the available width and remaining screen height. A narrower sidebar gives the field more room. Fit map responds to window resizing. Zoom buttons leave fit mode and enlarge or shrink the actual current map size; the 50% view button restores the old fixed tile scale. Larger zooms remain scrollable. Small windows stack the sidebar below the map. This changes presentation only, not tile movement or targeting.

## Victory presentation follow-up (2026-10-01)

Securing the primary objective displays a wide banner centered over the visible map viewport, without changing the map size or scrolling its content. Continue for optional objectives retains the existing pursuit action and minimizes the banner to an Objective secured bar. Finish operation reopens the completion choice; continuing again minimizes it locally without consuming an action. The bar follows the current battle?s victory state, including resumed pursuits. Camera controls have a separate heading row and four equally sized buttons, fixing the wrapped/stretched zoom-in control.

### Precise wheel zoom

Wheel over the map smoothly zooms around the pointer without redrawing units or sending game commands. Shift+wheel keeps ordinary scrolling; Ctrl/Meta+wheel remains available for browser zoom. Fit and fixed zoom buttons remain available in combat and preparation. Zoom is bounded at 25?300%.
Mercenary integration (October 2 dev pass): private-contract hires deploy as temporary controllable party/bodyguard units. Betrayal is a separate road encounter that preserves the original contract on survival. Rare appropriate outdoor maps can contain a fallen known contact, an automatic friendly helper, or a hostile mercenary who attacks both sides and blocks victory. See [Mercenaries](MERCENARIES.md) for availability, rates, death handling, notification, and limitations.


## Opening ambush and goblin commanders (October 2, 2026)

Implemented in dev. A successful Scout an ambush position decision gives players the first activations and puts every initial enemy under Sleeping camp for rounds 1?3. Sleeping enemies skip movement and actions; the camp wakes together at the start of round 4. A committed attack against any enemy wakes the whole camp before its hit roll, including a miss, skill or nonlethal takedown. Thrown impacts also wake everyone. Moving, guarding, inspecting targets, attacking terrain and rejected out-of-range commands do not trigger the shared alarm. Normal weapon-induced Sleep remains separate. Status hover text explains the shared rule and shows remaining rounds. Direct and alerted encounters remain awake.

Goblin Warcamp is a fixed D-rank boss encounter: chief 72 HP / 3 armor / 12 attack / 4 movement, raider 28 HP / 2 armor / 8 attack, archer 24 HP / 1 armor / 7 attack, horncaller 24 HP / 1 armor / 7 attack. Goblin evasion and racial identity remain; boss durability is authored rather than derived from ordinary recruit HP penalties. The B-rank Chieftain's Redoubt commander has 112 HP / 4 armor / 17 attack, with 40-HP escorts at 2 armor / 10 attack. A critical-failure commander complication still applies its existing +25% HP and +2 attack. Enemies never scale to the player's roster. Other rookie fights and unrelated encounters are unchanged. Already-created battles keep their saved stats; start a new encounter to test these values.

Pacing target: Warcamp expects two armed characters, not a naked solo starter. Use the quiet approach to cross the palisade lanes and position damage dealers before waking the camp; focus the chief to trigger the existing rout/leave decision. The alarm still brings reinforcements in round 5. Capturing the stronger chief takes more preparation than defeating them. Automatic tactics do not currently reserve the three-round window for coordinated positioning; improving that planning is deferred.

Validation: a deterministic real-command test uses three preparation rounds and two characters with STR/DEX/VIT 9, Knight's Blade and Short Bow to secure the chief and finish successfully. An exploratory ten-seed manual opening won 4/10 with attributes 7 and 8/10 with attributes 9; those small scripted samples demonstrate feasibility, not general win-rate guarantees. Rushed auto tactics lost these samples. Dedicated tests cover expiry, no sleeping movement/damage, miss-triggered shared waking, thrown impacts, ordinary Sleep preservation, invalid commands, awake direct openings and fixed boss stats.
