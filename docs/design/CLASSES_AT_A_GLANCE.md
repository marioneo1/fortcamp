# Classes at a glance

Defense preparation: Engineers can place their equipped machines/explosives free,
sharing turret caps with combat (one Engineer mine in defense); Rogues can place
equipped Caltrops free. These are preparation benefits, not additional Job skills.

October 9 final E-rank batch: Hedgerow Watch and Bring the Captive Home now use
recruitable Goblin guard, snarer, cutpurse, ringleader and lookout kits from the
existing Fighter/Rogue/Ranger families. Watch Raider, Wagon Guard, Light Raider,
Light Escort and Escort/Raider Lookout are role labels, not additional Jobs;
captured recruits keep their specialty skills and normal Job starter pool.

Current implemented catalogue, October 9, 2026. This is the short reference;
the original [design draft](STARTING_JOBS_AND_SKILLS_V1.md) contains historical
proposals, and individual rework documents explain the full rules.

## The 12 selectable classes

| Class | What it does | Signature tools |
| --- | --- | --- |
| [Fighter](FIGHTER_COMBAT_REVIEW.md) | Reliable melee fighter who protects allies and controls positioning. | Intercept, Earthbreaker, Second Wind |
| [Barbarian](MARTIAL_JOBS_REWORK.md) | Builds Fury from enemy damage and spends it on powerful attacks and control. | Skullbreaker, Groundbreaker, Bloodthirst |
| [Monk](MONK_REWORK_REVIEW.md) | Mobile melee damage through openers, follow-ups and a finisher. | Rapid Palm, Sweeping Dash, Heaven-Piercing Strike |
| [Rogue](ROGUE_REWORK_REVIEW.md) | Fragile burst fighter who exploits positioning, debuffs and traps. | Cheap Shot, Exploit Weakness, Caltrops |
| [Ranger](RANGER_REWORK_REVIEW.md) | Ranged damage through marked targets, distance and Poison buildup. | Mark Quarry, Longshot, Rupturing Blow |
| [Mage](MAGE_REWORK_REVIEW.md) | Fragile elemental caster who reshapes terrain and combines elemental effects. | Flash Freeze, Chain Lightning, Meteor |
| [Bard](BARD_REWORK_REVIEW.md) | Performs stationary Songs that change nearby combat rules and supports allies. | Cue the Strike, Quickening Chorus, Song of Peace |
| [Cleric](CLERIC_REWORK_REVIEW.md) | Manages limited healing charges, or trades allied healing for personal holy combat. | Rest, Holy Light, Battle Priest |
| [Druid](DRUID_REWORK_REVIEW.md) | Switches animal forms for different roles; uses nature magic in humanoid form. | Prowler/Bulwark/Rat Forms, Living Armor, Bramble Wall |
| [Summoner](SUMMONER_REWORK_REVIEW.md) | Creates autonomous creatures and manages their orders, survival and sacrifice. | Bound Companion, Wisp Swarm, Spirit Projection |
| [Engineer](ENGINEER_REWORK_REVIEW.md) | Turns preparation time into turrets, mines and explosive firepower. | Heavy Emplacement, Overclock, Dynamite |
| [Captor](CAPTOR_REWORK_REVIEW.md) | Takes targets alive by damaging Resolve, isolating them and maintaining restraint. | Bola, Abduct, Restraining Hold |

Fighter has **9** learnable skills; the other classes have **8** each: **97 total**.
Normal characters equip five skills, including slotted passives. Basic commands,
racial traits and innate mechanics are separate. Battle Priest, Marksman and
other build names are choices within a class, not additional selectable classes.

## Extra humanoid enemy kits

These are authored loadouts of existing classes, not new starter classes.
Their learned/equipped skills and specialization survive capture and recruitment.

| Enemy specialization | Underlying class | What distinguishes it | Found in |
| --- | --- | --- | --- |
| Road Enforcer | Fighter | Driving Strike, Intercept and Shakedown; protective frontline. | Unwanted Toll |
| Road Cutpurse | Rogue | Cheap Shot, Parting Cut and Crippling Cut; opportunistic melee. | Unwanted Toll |
| Road Trapper | Rogue, mixed kit | Cheap Shot, Road Bola, Tripline and Exploit Weakness. | Unwanted Toll |
| Goblin Cutpurse | Rogue | Cheap Shot and Ankle Bite; stronger beside allies. | Goblin Pickpockets |
| Goblin Snarer / Scavenger Snarer | Rogue, mixed kit | Road Bola and Cheap Shot. | Pickpockets / Old Well / Supply Watch |
| Goblin Lookout / Sling Scout / Supply Lookout | Ranger | Goblin Lookout uses Goliath Shot and Mark; Human slingers retain Mark/Longshot. | Pickpockets / Old Well / Supply Watch |
| Salvage Guard / Supply Raider | Fighter | Driving Strike and Intercept. | Old Well / Supply Watch |
| Supply Pilferer | Rogue | Cheap Shot and Crippling Cut; weaker body in larger groups. | Supply Watch |
| Goblin Salvage Guard | Fighter | Driving Strike and Intercept; guards recovered supplies. | Timber Creek / Tool Shed / Herb Garden |
| Tool Snatcher / Goblin Forager / Worksite Pilferer | Rogue | Cutpurses use Ankle Bite/Cheap Shot; lighter pilferers retain Crippling Cut. | Tool Shed / Herb Garden / Timber Creek |
| Garden Snarer / Worksite Snarer | Rogue, mixed kit | Road Bola and Cheap Shot; controls approaches. | Tool Shed / Herb Garden |
| Sling Scavenger / Worksite Lookout | Ranger | Goliath Shot and Mark Quarry; ranged cover for scavengers. | Timber Creek / Tool Shed / Herb Garden |
| Bandit Enforcer / Trapper / Skirmisher | Fighter / Rogue | Shakedown, Tripline/Bola, or Parting Cut/Cheap Shot. | Prisoner rival/former/proof missions |
| Warband Bruiser / Warden | Barbarian / Fighter | Reckless Blow/Cornered Fury, or Heel Cut/Intercept. | Prisoner former/proof missions |
| Goblin Ringleader | Fighter | Tag Team! and Intercept. | Goblin Pickpockets |
| Highway Enforcer / Trapper / Skirmisher / Lookout | Fighter / Rogue / Ranger | Shakedown, Tripline/Bola, Parting Cut, or Mark/Longshot; stronger D-rank road roles. | Highway Ambush |
| Relic Warden / Bone Shieldbearer / Chapel Archer | Fighter / Ranger | Heel Cut/Intercept, Driving Strike/Intercept, or Mark/Longshot; armored Undead patrol. | Bone Patrol |
| Boar Vanguard / Mounted Skirmisher / Rider Slinger / Ringleader | Fighter / Rogue / Ranger | Existing kits plus Rider: real boar HP, mounted protection and movement; Boar Charge gains damage with distance; mount loss risks Stun/Hobble or a safe landing. | Boar-Rider Patrol |
| Road Raider / Bone Carrier / Young Rider | Rogue, with Ranger scouts | Lighter bodies and smaller kits balance the four-member D-rank variations. | All three D-rank batch missions |

**Road Bola** is our extra recruitable technique: a ranged half-power attack
that applies Hobble. It is distinct from Captor's Resolve-damaging Bola.
Eight additional enemy definitions are implemented in dev: Tripline, Shakedown,
Parting Cut, Ankle Bite, Goliath Shot, Tag Team!, Cornered Fury and Heel Cut.
That makes **106 skill definitions** including the 97 player-class skills.
See the short [enemy specialty reference](../player-reference/ENEMY_SPECIALTIES.md)
for current kit rules. Recruitment
adds the underlying Job's starter skills as learned options without changing the
equipped five-slot loadout. [Background perks](../player-reference/RECRUIT_PERKS.md)
are separate Traits, not slotted techniques; some enemies have none.

Older maps also use generic Chieftain, Raider, Archer, Horncaller and Reinforcement
templates. Those are enemy roles, not five additional classes; they have not all
received the current encounter-by-encounter audit.

## Animal and created-unit profiles

| Profile | Simple identity |
| --- | --- |
| Store Rat / Rat Swarm | Wounded rats combine, up to three; bites apply stacking Gnawing Weakness. |
| Fence Wolf | Packs surround targets, gain stronger bites and can apply Bleed. |
| Foraging Bear | Independent wildlife that attacks either side during a rare same-map encounter. |
| Fire / Earth / Grass Companion | Summoner's offensive caster, durable disruptor or healer/support creature. |
| Wisp | Fragile flying ranged summon; deployed in groups of three. |
| Sentry Turret / Heavy Emplacement | Engineer's stationary automatic gun and slower artillery machine. |

Druid animal forms belong to Druid; they are not separate recruitable classes.
Bramble Wall is an obstacle with reactions, not another creature class.
Animal boss portraits alone do not mean dedicated boss kits are implemented.
Advanced classes and Champion-specific kits remain deferred.

Sources: `backend/job_loadouts.py`, `backend/combat_encounter_profiles.py`,
`backend/combat_radiant.py`, and the Summoner/Engineer runtime modules.
Update this reference whenever a class, enemy specialization or species kit changes.
Full encounter details: [E-rank audit](E_RANK_COMBAT_AUDIT.md).

## Character quirks
The 61 new general quirks and 16 selected backgrounds are innate perks, separate
from Jobs and skill slots. A recruit keeps its Job starter pool and any enemy
specialty skills. See ../player-reference/GENERAL_PERKS.md for the concise catalog.
