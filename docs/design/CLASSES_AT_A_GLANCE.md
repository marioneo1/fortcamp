# Classes at a glance

Current implemented catalogue, October 8, 2026. This is the short reference;
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
| Road Enforcer | Fighter | Driving Strike and Intercept; protective frontline. | Unwanted Toll |
| Road Cutpurse | Rogue | Standard starter Rogue kit; opportunistic melee. | Unwanted Toll |
| Road Trapper | Rogue, mixed kit | Cheap Shot, Road Bola and Exploit Weakness. | Unwanted Toll |
| Goblin Cutpurse | Rogue | Cheap Shot and Crippling Cut; mobile Goblin profile. | Goblin Pickpockets |
| Goblin Snarer / Scavenger Snarer | Rogue, mixed kit | Road Bola and Cheap Shot. | Pickpockets / Old Well / Supply Watch |
| Goblin Lookout / Sling Scout / Supply Lookout | Ranger | Mark Quarry and Longshot with a sling. | Pickpockets / Old Well / Supply Watch |
| Salvage Guard / Supply Raider | Fighter | Driving Strike and Intercept. | Old Well / Supply Watch |
| Supply Pilferer | Rogue | Cheap Shot and Crippling Cut; weaker body in larger groups. | Supply Watch |

**Road Bola** is our extra recruitable technique: a ranged half-power attack
that applies Hobble. It is distinct from Captor's Resolve-damaging Bola.
That makes **98 skill definitions** including the 97 player-class skills.

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
