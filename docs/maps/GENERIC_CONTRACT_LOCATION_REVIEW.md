# Generic contract location review

Status update October 3: roadblocks/command camps and the seven compact beginner/training settings below are implemented in dev. The original review is preserved; read AUTHORED_BATTLE_LOCATIONS.md for the final maps. Highway/convoy/watch, tunnels and later story locations remain proposed. Runtime audit currently lists 43 authored and 18 generic encounter IDs.

Current status: the first roadblock/command-position batch below is implemented in dev, with four variants per setting and compact E/D old-command posts. See ../design/AUTHORED_BATTLE_LOCATIONS.md for exact behavior and validation. All later batches below remain proposals. The original review counts and assessments are preserved as the planning baseline; BATTLE_LOCATION_AUDIT.md contains current coverage.

Reviewed October 3, 2026 against runtime mission premises, faction openings and the current `_contract_blueprint`. This is a proposed design pass; it changes no battle maps, mission outcomes or rewards. Coverage: all 29 distinct mission titles currently represented by 44 generic contract encounter IDs. Three prisoner agreement titles each have six rank copies.

The existing road/camp/ruin/court maps share a 12x9 rectangle, four central cover pieces, fixed spawns and one firing bank. Seed changes mostly affect boundary tree selection. They are functional fallbacks, but most do not contain the landmark or geography described by the mission. The table distinguishes an appropriate starting setting from a complete map.

## First batch: roads and command positions

| Mission | Current fit | Proposed map |
| --- | --- | --- |
| Break the Rival Warband | Camp misses the road they control. | Road-spanning timber blockade with a working gate, a roadside guard shelter and a supply yard. A rough flank trail gives an alternative to forcing the gate. |
| End the Old Command | Camp is the right setting but has no command position. | Occupied military camp with an enclosed command yard, barracks/store, supply tents and two usable entrances. The commander is behind a defensive line rather than standing beside the entrance. |
| Chieftain's Redoubt | Camp misses the explicitly layered timber redoubt. | Two timber defensive lines enclosing a chieftain's tent and stores. Offset gates prevent a straight charge; a damaged side approach offers a longer flank. Use grounded rises only where the movement/height rules remain fair. |
| The Ironcap Vanguard | Camp fits, but it does not read as an organized force. | Disciplined drill camp with a broad parade yard, weapon stores, command shelter and controlled gate. Keep room for formations and ranged support instead of filling it with clutter. |

Use the approved timber and rough-stone kits, existing tents, crates, weapon racks and alarm-bell art. The bell is scenery until a separate alarm mechanic is implemented for these encounters. Do not imply that destroying a decorative store disables enemy abilities.

Build four actual plan families: straight blockade, bent-road checkpoint, split supply/guard post and fortified command enclosure. Mission variants choose a fitting subset and use distinct perimeter/entrance/yard arrangements, not only reflections. Dressing can reuse an approved plan, moving supplies and tents between safe slots. Roadblock walls must actually meet the impassable boundary or provide an intentional flank; decorative cover across an otherwise open field is not a blockade.

Prisoner agreement rank copies should share their setting vocabulary. Early-rank jobs use a compact occupied post; later ranks can use deeper enclosures and multiple approaches. Keep fixed rank-based enemy budgets; do not scale enemies to the player's level. Racial/faction context can change the material/dressing without changing the premise. Rank alone should not make every map enormous.

## Compact early sites and reclaimed ground

| Mission | Current fit | Proposed map |
| --- | --- | --- |
| Rats in the Storehouse | Camp has no provision shed. | Small timber store with grain sacks/barrels around the walls, one door and a damaged delivery opening. Keep a short central aisle for a solo character. |
| Wolves at the Fence | Road has no fenced clearing. | Farm-edge pasture enclosed by timber fencing, with an open/broken gate and scattered brush. Wolves occupy the clearing; the approach stays readable. |
| Herbs Behind the Wall | Road omits the garden and gate. | Abandoned walled herb garden with accessible plants outside and a second patch behind the gate. The fight belongs around the access route; a separate harvest objective needs explicit implementation. |
| The Goblin Pickpockets | Road is suitable, but the dropped purse has no place. | Small roadside bend with a clear dropped-purse landmark between the goblins, a ditch and a little cover. Avoid a full fort for two thieves. |
| Movement at the Old Well | Ruin is plausible, but there is no well. | Abandoned village yard with a central well, a collapsed cottage edge and a few broken boundary sections. Keep two short approaches to the scavengers. |
| The Small Supply Watch | Road is suitable but lacks the provision stop. | Small roadside delivery yard with a shelter, barrels and a waiting handcart, plus a clear entry lane. Scavengers hold the approach rather than an unexplained wall maze. |
| A Promise Proven in Battle | Camp does not identify the ground being reclaimed. | Occupied training yard with a marked sparring area, dummies, racks and a small shelter. This is a real fight against the occupiers, not a harmless training duel. |

These should be compact enough that reaching the opponent is not the main challenge. Reuse sheds, existing fences/gates and supplies; training dummies, planted herb beds and a well need purpose-built art if suitable assets are absent. Keep terrain, props and structures in separate packs. No decoration becomes loot or a mission objective automatically.

## Road encounters, convoys and collection sites

| Mission | Current fit | Proposed map |
| --- | --- | --- |
| Highway Ambush | Road is right; the narrow highway cut is absent. | Sunken highway between low banks, with ambushers on the shoulders and stolen supplies at a pull-off. Provide a main lane and one longer shoulder route; avoid unanswerable elevated archers. |
| Boar-Rider Patrol | Road fits, but the layout does not support cavalry. | Broad dirt road with a branching courier track, sparse trees and open verge for fast movement. Avoid tight indoor corridors and excessive blocking props. |
| The Tithe Convoy | Road is right; the tribute convoy is absent. | Guarded tribute wagons at a road bend or stopping yard, with escorts occupying both ends and cover along the shoulders. Wagons start as stationary scenery; moving-convoy rules would be a separate mechanic. |
| The Patrol That Did Not Return | Road fits, but the watch post/evidence trail is absent. | Empty watch shelter linked by a woodland track to an occupied roadside position. Use abandoned watch supplies and a clear signal landmark to connect the two areas. |
| Three Horns, One Road | Road omits the copied signal network. | Road fork with three visible signal positions, a command shelter and connected side paths. Horns are landmarks until disabling signals has real mechanics. |
| The Wagon on the Wrong Road | Road is right, but the opening names a makeshift toll camp. | Diverted wagon caught at a temporary timber toll barrier beside a false-route sign, with a guarded dispatch table and a back trail. Reuse the blockade piece and wagon staging. |
| The Names Left on the Road | Road fits, but neither the hearse route nor collectors are visible. | Old hearse stopping place beside memorial markers, with a collector's table and boxes of burial tags. Preserve a recognizable roadside setting rather than using a generic dungeon. |
| The Last Collection Order | Road is right, but the collection point is absent. | Occupied village-road collection post with a records table, tribute crates and a small escort shelter. It should look like the remnants of the fallen court, not a new major fortress. |
| The Caravan's False Account | Road is too generic for confronting a supplier. | Caravan accounting stop with a clerk's booth, weigh station, sacks and parked handcart. Used for the combat complication; normal receipt/dialogue choices stay available. |

Road templates can share bends, forks, banks and pull-offs. Their layout should preserve the setting-specific landmark and offer an intentional tactical choice. Signposts/horns/weighing gear may need one small prop pack; current wagons, tables, dispatch satchels and crates cover much of the dressing. Do not label decorative records as recoverable until interaction and outcome logic support it.

## Ruins, tunnels and the royal court

| Mission | Current fit | Proposed map |
| --- | --- | --- |
| Goblin Warren Purge | Open ruin is wrong for a tunnel network beneath hills. | Connected underground chambers with branching passages, a storage alcove and a main guard chamber. At least two routes reconnect, preventing one endless corridor. Dark ground/rock walls must clearly separate walkable tunnels from solid hillside. |
| Knight without a Grave | Ruin is misleading: its premise names the old king's road. | Cracked royal causeway with fallen milestones, a ruined roadside monument and space for the knight's challenge. The ruin vocabulary belongs beside the road, not in a default crypt. |
| Court of the Empty Crown | Court is the right category but currently only a stone rectangle. | Roofless royal audience court with a raised dais, broken columns, side galleries and multiple door approaches. Captains occupy meaningful positions around the court; masonry cover should follow the architecture. |

Important routing issue: the death-knight encounter also appears as the bell oathkeeper or in grave-related story complications. Its own mission should use the royal road, while those branches may need a chapel/crypt context override. Changing the encounter's one default map cannot make every origin correct. Add explicit originating-location context later rather than choosing a crypt or road randomly.

Tunnels need a dedicated ground/rock-wall vocabulary and chamber templates. The court can reuse polished stone plus columns/stairs, with new dais/monument art only where existing assets fail. Stair scenery does not imply floor traversal; adventure-mode floors remain a separate feature.

## Meridian facilities, waystations and the treaty crossing

| Mission | Current fit | Proposed map |
| --- | --- | --- |
| The Missing Governor | Camp misses the opening's guarded salvage yard. | Fenced machinery salvage yard containing stripped pump parts, sorting benches and a guarded component store. The governor is a pump component, not a person to rescue. |
| The Custodian Who Would Not Stop | Camp lacks the workshop/control room. | Workshop floor with machine bays, a separated control room and two approaches around dangerous-looking equipment. The opening describes armed scavengers holding the controls; do not assume every opponent is a robot. |
| Where the Spare Current Goes | Camp omits the unrecorded overflow workshop. | Small outlying power workshop with a regulator platform, discharge channels and a side maintenance entrance. Electrical hazards require real rules before their art suggests tiles cause damage. |
| Wards at the Waystation | Ruin omits the inhabited traveler shelter. | Weathered waystation with a protected waiting yard, ward posts around its boundary and a damaged maintenance room. Leave the travelers' space identifiable even if NPCs are not present in the battle. |
| The Meridian Calibration | Camp is wrong for calibrating a survey instrument. | Survey terrace or measurement yard with an instrument plinth, marked reference points and a repair shelter. Keep open sight lines between measurement points; this is not a foundry by default. |
| A Light on This Side | Camp omits the treaty crossing and missing beacon lens. | Quiet crossing approach with a beacon platform, alien-scarred ground and a small arrival shelter. Keep the agreed route clear; the treaty means this is not automatically an alien invasion. |

These can use rough stone/metal workshop structures, but need distinct machine/control/ward/beacon landmarks. Existing levers, workbenches and charts help; do not substitute an anvil for every specialized device. Generate a focused machinery/ward prop pack once these layouts are designed. Crossings and power channels need terrain separate from the prop pack.

## Variations and validation contract

- Use named structural variants with different routes, entrance placement, room connections or cover distribution. Mirroring and furniture swaps are useful extra dressing, but do not count as distinct structural plans.
- Keep seeded selection persistent in saved battles. Battle Lab must expose verified layout seeds for every implemented family.
- Preserve existing mission choices, objectives, reward rolls, encounter identity and rank budgets unless a separate gameplay change is expressly recorded.
- Check blocked boundary crossings, operable doors, sensible sight lines, clear spawns and paths to exits. Check rendered maps at normal game zoom, not only data validation.
- Keep exits believable: road ends for highways, entrances/breaches for enclosures, cave mouths for tunnels. Changing extraction tiles must remain compatible with the existing wait-on-exit and carried-body rules.

## Adjacent issues found in already-authored locations

These are additional proposed corrections, not changes made by this review:

- **A Road Wide Enough for Everyone:** its story opening specifies a gate at a narrow bridge. The new toll building alone is not enough; combine it with the ground-layer river/bridge piece.
- **The Chapel Patrol:** its premise says the dead stop mourners outside the chapel. Its next placement pass should stage the patrol on the approach, with the chapel as a landmark, rather than putting every opponent inside.
- **Story-origin combat:** an encounter reused by several quest branches needs an appropriate origin setting. Preserve one enemy/reward definition while selecting the map from explicit scene context.

Recommended implementation order: roadblocks/command camps; compact beginner sites; convoy/watch/collection roads; tunnels/royal court; machinery/wards/treaty crossing. Art generation follows the layouts and asset-gap check, rather than generating a large unrelated pack first.
