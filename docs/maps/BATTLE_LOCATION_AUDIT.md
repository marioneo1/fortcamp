# Combat location coverage audit

Generated from runtime content with `.venv\Scripts\python.exe tools/audit_battle_locations.py`.
This inventories existing tactical encounters, including combat branches of roll/story missions. It does not propose converting roll-only contracts to combat.

31 contract encounter IDs use authored locations; 30 still use generic road/camp/ruin/court layouts. Prison rank copies are grouped below. Generic maps have seeded dressing but no named, mission-specific building plans.

## Authored contract locations

| Mission | Rank | Setting | Named layouts |
| --- | --- | --- | --- |
| A Road Wide Enough for Everyone | C | toll_post | 4 |
| A Watchman’s Dispute | D | toll_post | 4 |
| Bandit Outpost | C | raider_cache | 4 |
| Bone Collectors | D | graveyard | 2 |
| Bone Patrol | D | cemetery_road | 2 |
| Break the Rival Warband | A | road_blockade | 4 |
| Break the Rival Warband | B | road_blockade | 4 |
| Break the Rival Warband | C | road_blockade | 4 |
| Break the Rival Warband | D | road_blockade | 4 |
| Break the Rival Warband | E | road_blockade | 4 |
| Break the Rival Warband | S | road_blockade | 4 |
| Chieftain's Redoubt | B | timber_redoubt | 4 |
| End the Old Command | A | command_camp | 4 |
| End the Old Command | B | command_camp | 4 |
| End the Old Command | C | command_camp | 4 |
| End the Old Command | D | command_post | 4 |
| End the Old Command | E | command_post | 4 |
| End the Old Command | S | command_camp | 4 |
| Intruders at the Workshop | D | repair_yard | 4 |
| The Chapel Gatekeepers | C | chapel_approach | 4 |
| The Chapel Patrol | D | chapel_approach | 4 |
| The Ford Enforcers | C | toll_post | 4 |
| The Hidden Goblin Armory | C | open_armory | 4 |
| The Ironcap Vanguard | B | vanguard_camp | 4 |
| The Locked Tool Shed | E | tool_shed | 4 |
| The Narrow Bridge Gang | D | toll_bridge | 2 |
| The Road Raiders’ Cache | D | raider_cache | 4 |
| The Salvage Yard Court | C | salvage_court | 4 |
| The Unwanted Toll | E | toll_post | 4 |
| Timber Across the Creek | E | broken_creek_bridge | 2 |
| Who Collects the Second Toll? | B | toll_post | 4 |

## Generic contract locations still needing review

| Mission | Ranks | Current fallback |
| --- | --- | --- |
| A Light on This Side | B | camp |
| A Promise Proven in Battle | E / D / C / B / A / S | camp |
| Boar-Rider Patrol | D | road |
| Court of the Empty Crown | A | court |
| Goblin Warren Purge | C | ruin |
| Herbs Behind the Wall | E | road |
| Highway Ambush | D | road |
| Knight without a Grave | B | ruin |
| Movement at the Old Well | E | ruin |
| Rats in the Storehouse | E | camp |
| The Caravan’s False Account | D | road |
| The Custodian Who Would Not Stop | B | camp |
| The Goblin Pickpockets | E | road |
| The Last Collection Order | C | road |
| The Meridian Calibration | C | camp |
| The Missing Governor | C | camp |
| The Names Left on the Road | C | road |
| The Patrol That Did Not Return | C | road |
| The Small Supply Watch | E | road |
| The Tithe Convoy | B | road |
| The Wagon on the Wrong Road | C | road |
| Three Horns, One Road | B | road |
| Wards at the Waystation | C | ruin |
| Where the Spare Current Goes | B | camp |
| Wolves at the Fence | E | road |

## Separate authored scenarios

Goblin Warcamp, The Captive Cart, Smoke on the Hedgerow investigation ambush and Hedgerow Watch defense have separate scenario generators. They are not counted as generic contracts above. They still need a separate review of named layout coverage; existing seeded dressing and defense deployment should be preserved.

Story-only locations such as The Bell Beneath the Mud are not standalone tactical maps just because their story names a location. Their current combat complications can route to another contract. Giving them their own battle site requires changing that encounter routing deliberately.

See [authored locations](../design/AUTHORED_BATTLE_LOCATIONS.md) for implemented rollout and proposed next batches.
