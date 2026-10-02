from __future__ import annotations

from .champions import CHAMPION_PERKS, EXPANDED_CHAMPIONS
from .champions_lower_tiers import LOWER_TIER_CHAMPIONS, LOWER_TIER_PERKS
from .celestials import CELESTIAL_CHAIN_STEPS, CELESTIAL_PERKS, CELESTIALS
from .races import (
    ADDITIONAL_RECRUIT_PROFILES, MISSION_RECRUIT_REGIONS, RACE_CATALOG,
    RACE_TRAIT_PERKS, REGIONAL_RECRUIT_TABLES, SECRET_RECRUIT_EVENTS,
)

STAT_NAMES = ["combat", "scavenging", "building", "medicine", "cooking", "survival", "magic"]
ATTRIBUTE_NAMES = ["str", "dex", "agi", "vit", "int", "luk"]
PERK_LEVELS = ["none", "basic", "skilled", "expert", "master"]
PERK_TRACKS = {
    "combat": {"name": "Combatant", "description": "Formal training in weapons, positioning, and fighting under pressure.", "attributes": ["str", "dex"], "facility": "training_ground", "attribute_bonus": "str"},
    "scavenging": {"name": "Scavenger", "description": "Practice finding useful material where other people see only wreckage.", "attributes": ["dex", "luk"], "facility": "training_ground", "attribute_bonus": "luk"},
    "building": {"name": "Constructor", "description": "Technical knowledge for structures, machinery, and safe demolition.", "attributes": ["str", "int"], "facility": "workshop", "attribute_bonus": "str"},
    "medicine": {"name": "Medic", "description": "Training in diagnosis, treatment, and recovering supplies safely.", "attributes": ["int", "dex"], "facility": "infirmary", "attribute_bonus": "int"},
    "survival": {"name": "Survivalist", "description": "Fieldcraft for hostile terrain, tracking, exposure, and long expeditions.", "attributes": ["vit", "agi"], "facility": "training_ground", "attribute_bonus": "vit"},
    "magic": {"name": "Arcanist", "description": "Controlled use and analysis of magical forces and artifacts.", "attributes": ["int", "luk"], "facility": "arcane_sanctum", "attribute_bonus": "int"},
    "alchemy": {"name": "Alchemist", "description": "Knowledge of reagents, transformations, compounds, and magical mixtures.", "attributes": ["int", "luk"], "facility": "alchemy_lab", "attribute_bonus": "int"},
}
PERK_TRAINING_ITEMS = {"skilled": "training_manual", "expert": "specialist_tome", "master": "mastery_codex"}
STANDALONE_PERKS = {
    "scout": {"name": "Scout", "description": "Comfortable moving ahead of a group and reading uncertain terrain.", "effect": "Can satisfy Scout-specific mission paths."},
    "engineer": {"name": "Engineer", "description": "Understands machinery and improvised technical solutions.", "effect": "Can trigger Engineer mission bonuses and special paths."},
    "medic": {"name": "Field Medic", "description": "Keeps a clear head when immediate treatment is needed.", "effect": "Can trigger Field Medic mission bonuses and special paths."},
    "fire_magic": {"name": "Fire Magic", "description": "Can create and control magical flame.", "effect": "Unlocks fire-based routes and Critical Success criteria."},
    "guard": {"name": "Guard", "description": "Experienced at protecting other people and holding dangerous ground.", "effect": "Can satisfy defensive and protection mission paths."},
    "goblin_hunter": {"name": "Goblin Hunter", "description": "Specialized knowledge of goblin habits, traps, and tactics.", "effect": "Unlocks powerful paths during The Green Warhost."},
    "tracker": {"name": "Tracker", "description": "Reads trails, spoor, disturbed ground, and evasive movement.", "effect": "Unlocks tracking-related mission criteria."},
    "pathfinder": {"name": "Pathfinder", "description": "Finds viable routes through unmapped or changing territory.", "effect": "Unlocks expedition and Beast Tide paths."},
    "undead_hunter": {"name": "Undead Hunter", "description": "Recognizes the patterns and weaknesses of the restless dead.", "effect": "Unlocks special paths during The Ashen Procession."},
    "exorcist": {"name": "Exorcist", "description": "Trained to identify and break spiritual corruption.", "effect": "Can satisfy possession and undead mission paths."},
    "divine_magic": {"name": "Divine Magic", "description": "Channels sacred power through rites and conviction.", "effect": "Unlocks divine and purification paths."},
    "priestess": {"name": "Priestess", "description": "Ordained in ritual practice and spiritual care.", "effect": "Can satisfy religious and ritual mission criteria."},
    "moon_sense": {"name": "Moon Sense", "description": "Feels unnatural changes tied to moonlight and bestial curses.", "effect": "Required for the Blood-Moon Den transformation path."},
    "lycanthrope": {"name": "Lycanthrope", "description": "Carries the controlled curse of the blood moon.", "effect": "Sets this character's race to Werewolf."},
    "heatproof": {"name": "Heatproof", "description": "Endures intense heat and smoke unusually well.", "effect": "Unlocks routes through fire and extreme heat."},
    "knight": {"name": "Knight", "description": "Bound to a martial code and trained for disciplined battle.", "effect": "Can satisfy knightly equipment and identity paths."},
    "swordsman": {"name": "Swordsman", "description": "Highly practiced with bladed weapons.", "effect": "Can satisfy sword-focused mission paths."},
    "magic_resistance": {"name": "Magic Resistance", "description": "Naturally resists hostile magical influence.", "effect": "Can bypass or reduce certain magical hazards."},
    "goblin_survivor": {"name": "Goblin Survivor", "description": "Has survived goblin captivity and understands their cruelty firsthand.", "effect": "Unlocks some Goblin Warhost story paths."},
    "warhost_veteran": {"name": "Warhost Veteran", "description": "Survived the Green Warhost and learned to read the rhythm of goblin armies.", "effect": "Can unlock veteran routes and advantages during goblin conflicts."},
    "graveward": {"name": "Graveward", "description": "Carries rites and instincts that resist the pull of restless dead.", "effect": "Can unlock protective paths during undead and spiritual missions."},
    "ley_touched": {"name": "Ley-Touched", "description": "Arcane convergence left a stable trace of living magic in this character.", "effect": "Can unlock unusual routes around unstable magic and ancient constructs."},
    "beast_bond": {"name": "Beast Bond", "description": "Understands the signals and territorial instincts of great beasts.", "effect": "Can unlock nonviolent or tracking paths during beast events."},
    "star_touched": {"name": "Star-Touched", "description": "Exposure to a fallen star changed this character in ways that are not fully understood.", "effect": "Can unlock rare Starfall paths and interactions with celestial relics."},
    "shield_wall": {"name": "Shield Wall", "description": "The equipment supports a disciplined, immovable defensive stance.", "effect": "Active while its granting item is equipped; satisfies Guard paths and defensive event routes."},
    "warhost_command": {"name": "Warhost Command", "description": "Carries the authority and battlefield signals of the Green Warhost.", "effect": "Active while its granting item is equipped; unlocks command and goblin-army routes."},
    "soul_anchor": {"name": "Soul Anchor", "description": "Fixes the wearer's spirit firmly to their body against deathly influence.", "effect": "Active while its granting item is equipped; unlocks resistance to possession and soul damage."},
    "stormbound": {"name": "Stormbound", "description": "Channels unstable weather and magical charge without immediately burning out.", "effect": "Active while its granting item is equipped; unlocks storm and raw-magic routes."},
    "gravity_walker": {"name": "Gravity Walker", "description": "Moves naturally when weight and direction stop obeying ordinary rules.", "effect": "Active while its granting item is equipped; unlocks gravity and aerial routes."},
    "apex_instinct": {"name": "Apex Instinct", "description": "Reads hostile movement with the certainty of a dominant predator.", "effect": "Active while its granting item is equipped; unlocks hunting and intimidation routes."},
    "titan_strength": {"name": "Titan Strength", "description": "The equipment carries a fraction of a colossal beast's physical force.", "effect": "Active while its granting item is equipped; unlocks feats of overwhelming strength."},
    "stellar_aegis": {"name": "Stellar Aegis", "description": "A thin celestial field turns aside hostile magic and impossible pressure.", "effect": "Active while its granting item is equipped; unlocks protection from Starfall hazards."},
    "void_sight": {"name": "Void Sight", "description": "Perceives shapes, paths, and movement in magical darkness and empty space.", "effect": "Active while its granting item is equipped; unlocks hidden Starfall and planar paths."},
    "masterwork": {"name": "Masterwork", "description": "Exceptional craftsmanship makes difficult physical work feel deliberate and precise.", "effect": "Active while its granting item is equipped; unlocks advanced construction and breaching routes."},
    "dwarven_resolve": {"name": "Dwarven Resolve", "description": "Dwarven endurance, craft tradition, and stubborn composure under pressure.", "effect": "A racial perk that unlocks endurance and master-craft routes."},
    "elven_senses": {"name": "Elven Senses", "description": "Exceptionally precise senses and awareness of subtle natural or magical changes.", "effect": "A racial perk that unlocks perception and arcane routes."},
    "orcish_might": {"name": "Orcish Might", "description": "Powerful build and a cultural respect for decisive action.", "effect": "A racial perk that unlocks strength and intimidation routes."},
    "hobgoblin_discipline": {"name": "Hobgoblin Discipline", "description": "Trained to maintain formation and follow complex battlefield signals.", "effect": "A racial perk that unlocks tactical Green Warhost routes."},
    "bugbear_ambush": {"name": "Bugbear Ambusher", "description": "Unexpectedly quiet and patient for such a large warrior.", "effect": "A racial perk that unlocks ambush and infiltration routes."},
    "kobold_trapsmith": {"name": "Kobold Trapsmith", "description": "Instinctively understands cramped structures, traps, and improvised mechanisms.", "effect": "A racial perk that unlocks trap and tunnel routes."},
    "deathless": {"name": "Deathless", "description": "No longer lives in an ordinary sense, but retains memory and purpose.", "effect": "A racial perk that resists undead hazards and changes some social routes."},
    "blood_sense": {"name": "Blood Sense", "description": "A vampire's awareness of life, injury, and predatory intent.", "effect": "A racial perk that unlocks tracking and medical-horror routes."},
    "mana_body": {"name": "Mana Body", "description": "Magic is part of this being's physical structure rather than merely a learned tool.", "effect": "A racial perk that unlocks raw-mana and construct routes."},
    "constructed": {"name": "Constructed", "description": "Built rather than born, with unusual resilience and repair needs.", "effect": "A racial perk that unlocks construct, repair, and hazard-immunity routes."},
    "dream_sense": {"name": "Dream Sense", "description": "Feels the edge between waking thought, illusion, and manifested dream.", "effect": "A racial perk that unlocks illusion and dream routes."},
    "scaled_hide": {"name": "Scaled Hide", "description": "Natural scales blunt injury and tolerate harsh climates.", "effect": "A racial perk that unlocks endurance and environmental routes."},
    "winged": {"name": "Winged", "description": "True flight changes how terrain, scouting, and pursuit can be approached.", "effect": "A racial perk that unlocks aerial routes."},
    "horned_guard": {"name": "Horned Guard", "description": "A minotaur's mass, balance, and instinct for holding contested ground.", "effect": "A racial perk that unlocks defensive and forceful routes."},
    "feral_agility": {"name": "Feral Agility", "description": "Animal-honed reflexes combine keen judgment with predatory speed.", "effect": "A racial perk that unlocks pursuit and evasion routes."},
    "astral_sense": {"name": "Astral Sense", "description": "Naturally perceives celestial currents and objects that do not belong to this world.", "effect": "A racial perk that unlocks Starfall navigation and relic routes."},
    "void_adapted": {"name": "Void Adapted", "description": "Endures silence, pressure, and spatial distortion that overwhelm ordinary bodies.", "effect": "A racial perk that unlocks void and planar-survival routes."},
    "living_constellation": {"name": "Living Constellation", "description": "Carries a shifting pattern of celestial light beneath the skin.", "effect": "A racial perk that unlocks rare celestial and prophecy routes."},
    "halfling_luck": {"name": "Halfling Luck", "description": "An improbable talent for being exactly where danger does not land.", "effect": "A racial perk that unlocks luck, escape, and overlooked-cache routes."},
    "infernal_legacy": {"name": "Infernal Legacy", "description": "A Tiefling heritage with an instinctive tolerance for heat and hostile magic.", "effect": "A racial perk that unlocks fire, pact, and magical-resistance routes."},
}
STANDALONE_PERKS.update(CHAMPION_PERKS)
STANDALONE_PERKS.update(LOWER_TIER_PERKS)
STANDALONE_PERKS.update(RACE_TRAIT_PERKS)
STANDALONE_PERKS.update(CELESTIAL_PERKS)
STANDALONE_PERKS.update({
    "bannerbreaker": {"name": "Bannerbreaker", "description": "Learned how the Black Banner communicates, collects tribute, and protects its officers.", "effect": "Unlocks anti-raider tactics, intimidation, and convoy-interception paths."},
    "keeper_of_last_rites": {"name": "Keeper of Last Rites", "description": "Carries part of the rite that can finally release the oath-bound dead of Lareth.", "effect": "Unlocks peaceful resolutions and powerful wards against the Ashen Procession."},
    "meridian_attunement": {"name": "Meridian Attunement", "description": "Can feel the surviving Meridian network and redirect a fraction of its power.", "effect": "Unlocks ancient-machine controls, ley routes, and dangerous overcharge options."},
    "titan_speaker": {"name": "Titan Speaker", "description": "Recognizes the calls, warnings, and migration customs of colossal beasts.", "effect": "Unlocks nonviolent titan routes and the ability to redirect great beasts."},
    "riftwalker": {"name": "Riftwalker", "description": "Has crossed a stable threshold between worlds and remembers how reality bends around it.", "effect": "Unlocks planar shortcuts, Voidsent negotiations, and controlled breach routes."},
})
EQUIPMENT_SLOTS = ["weapon", "offhand", "head", "body", "hands", "legs", "feet", "accessory"]
MISSION_RANKS = ["E", "D", "C", "B", "A", "S"]
GUILD_HALL_UPGRADES = {
    "C": {"wood": 30, "scrap": 25, "cloth": 10},
    "B": {"wood": 55, "scrap": 50, "cloth": 15, "medicine": 5},
    "A": {"wood": 90, "scrap": 90, "cloth": 25, "medicine": 12},
    "S": {"wood": 150, "scrap": 160, "cloth": 40, "medicine": 25},
}
MISSION_EVENTS = {
    "general": {"name": "Open Contracts", "splash": "The board carries the usual mix of local dangers, salvage leads, and unanswered requests.", "min_roll": 0, "theme": "general"},
    "goblin_warhost": {"name": "The Green Warhost", "splash": "War horns echo beyond the roads. Goblin bands are gathering beneath a single banner, and every contract points toward the coming war.", "min_roll": 700, "theme": "goblin"},
    "ashen_procession": {"name": "The Ashen Procession", "splash": "Cold ash falls without a fire. The dead are walking old roads again, and forgotten graves no longer stay quiet.", "min_roll": 850, "theme": "undead"},
    "arcane_convergence": {"name": "Arcane Convergence", "splash": "Ley lines flare across the region. Ruins awaken, impossible weather gathers, and magic leaves valuable scars behind.", "min_roll": 930, "theme": "arcane"},
    "great_beast_tide": {"name": "The Great Beast Tide", "splash": "Migrating monsters have broken every familiar boundary. Hunters, caravans, and settlements are all caught in their path.", "min_roll": 975, "theme": "beast"},
    "starfall_omen": {"name": "Starfall Omen", "splash": "The night split open in silent fire. Something ancient fell beyond the horizon, and the strongest guilds are already moving.", "min_roll": 994, "theme": "starfall"},
}

BUILDINGS = {
    "tent": {"name": "Tent", "w": 2, "h": 2, "workers": 0, "beds": 2, "cost": {}, "description": "Basic shelter for two people."},
    "campfire": {"name": "Campfire", "w": 1, "h": 1, "workers": 1, "cost": {}, "description": "Cooking, warmth, and the center of the first camp."},
    "storage_shed": {"name": "Storage Shed", "w": 2, "h": 2, "workers": 1, "cost": {"wood": 18, "scrap": 4}, "description": "Adds six hours to the camp's production catch-up allowance. The first shed increases it from 12 to 18 hours."},
    "workshop": {"name": "Workshop", "w": 3, "h": 2, "workers": 2, "cost": {"wood": 24, "scrap": 16}, "description": "Supports Constructor proficiency training. Higher tiers require a qualified teacher and the appropriate training item."},
    "infirmary": {"name": "Infirmary", "w": 3, "h": 2, "workers": 1, "cost": {"wood": 20, "scrap": 10, "cloth": 8, "medicine": 4}, "description": "Treats injured characters."},
    "barracks": {"name": "Barracks", "w": 3, "h": 3, "workers": 0, "beds": 6, "cost": {"wood": 36, "scrap": 14, "cloth": 10}, "description": "Additional living quarters for the camp."},
    "watchpost": {"name": "Watchpost", "w": 2, "h": 2, "workers": 2, "cost": {"wood": 20, "scrap": 12}, "description": "Guard assignment and future defense structure."},
    "guild_hall": {"name": "Guild Hall", "w": 3, "h": 3, "workers": 2, "cost": {"wood": 45, "scrap": 18, "cloth": 8}, "description": "Unlocks D-Rank missions when built and supports mission-board rank upgrades."},
    "training_ground": {"name": "Training Ground", "w": 3, "h": 2, "workers": 2, "cost": {"wood": 28, "scrap": 12}, "description": "Trains Combatant, Scavenger, and Survivalist proficiencies. Higher tiers require a qualified teacher and the appropriate training item."},
    "prison_cell": {"name": "Prison Cell", "w": 2, "h": 2, "workers": 1, "cells": 4, "cost": {"wood": 24, "scrap": 20}, "description": "Four secure prisoner slots and one Warden assignment. Overflow captives have one hour of total temporary-stockade time before they are removed."},
    "arcane_sanctum": {"name": "Arcane Sanctum", "w": 3, "h": 3, "workers": 2, "cost": {"wood": 32, "scrap": 24, "cloth": 12}, "description": "A facility for Arcanist proficiency training."},
    "alchemy_lab": {"name": "Alchemy Lab", "w": 3, "h": 2, "workers": 2, "cost": {"wood": 26, "scrap": 18, "medicine": 6}, "description": "A facility for Alchemist proficiency training."},
}

ITEMS = {
    "rusty_knife": {"name": "Rusty Knife", "slot": "weapon", "weapon_type": "blade", "weapon_scaling": "str", "power": 1, "tags": ["melee", "improvised"], "bonuses": {"combat": 1}, "rarity": "common"},
    "worn_jacket": {"name": "Worn Jacket", "slot": "body", "tags": ["clothing"], "bonuses": {"survival": 1}, "attribute_bonuses": {"vit": 1}, "rarity": "common"},
    "work_boots": {"name": "Work Boots", "slot": "feet", "tags": ["workwear"], "bonuses": {"scavenging": 1}, "attribute_bonuses": {"agi": 1}, "rarity": "common"},
    "scrap_hatchet": {"name": "Scrap Hatchet", "slot": "weapon", "weapon_type": "axe", "weapon_scaling": "str", "power": 2, "tags": ["melee", "breaching"], "bonuses": {"combat": 2, "building": 1}, "rarity": "uncommon"},
    "field_pack": {"name": "Field Pack", "slot": "accessory", "tags": ["pack", "scavenging_gear"], "bonuses": {"scavenging": 2}, "rarity": "uncommon"},
    "medic_coat": {"name": "Medic Coat", "slot": "body", "tags": ["medical_gear"], "bonuses": {"medicine": 2}, "rarity": "uncommon"},
    "hard_hat": {"name": "Hard Hat", "slot": "head", "tags": ["construction_gear"], "bonuses": {"building": 2}, "attribute_bonuses": {"vit": 1}, "rarity": "uncommon"},
    "work_gloves": {"name": "Work Gloves", "slot": "hands", "tags": ["construction_gear"], "bonuses": {"building": 1, "scavenging": 1}, "rarity": "common"},
    "cargo_pants": {"name": "Cargo Pants", "slot": "legs", "tags": ["clothing"], "bonuses": {"survival": 1}, "rarity": "common"},
    "short_bow": {"name": "Short Bow", "slot": "weapon", "weapon_type": "bow", "weapon_scaling": "dex", "power": 2, "tags": ["ranged"], "bonuses": {"combat": 2}, "rarity": "uncommon"},
    "breaching_charge": {"name": "Breaching Charge", "slot": "offhand", "tags": ["breaching", "explosive"], "bonuses": {"building": 1}, "rarity": "rare"},
    "ember_charm": {"name": "Ember Charm", "slot": "accessory", "tags": ["fire_focus", "magic_focus"], "bonuses": {"magic": 2}, "rarity": "rare"},
    "ember_staff": {"name": "Ember Staff", "slot": "weapon", "weapon_type": "staff", "weapon_scaling": "int", "power": 3, "tags": ["magic", "fire_focus", "magic_focus"], "bonuses": {"combat": 1, "magic": 2}, "rarity": "rare"},
    "knight_blade": {"name": "Knight's Blade", "slot": "weapon", "weapon_type": "sword", "weapon_scaling": "str", "power": 4, "tags": ["melee", "sword", "knightly"], "bonuses": {"combat": 3}, "rarity": "rare"},
    "training_manual": {"name": "Training Manual", "slot": None, "tags": ["training", "common_perk"], "bonuses": {}, "rarity": "common", "description": "Consumed to train a proficiency from Basic to Skilled."},
    "specialist_tome": {"name": "Specialist Tome", "slot": None, "tags": ["training", "rare_perk"], "bonuses": {}, "rarity": "rare", "description": "Consumed to train a proficiency from Skilled to Expert."},
    "mastery_codex": {"name": "Mastery Codex", "slot": None, "tags": ["training", "master_perk"], "bonuses": {}, "rarity": "mythic", "description": "Consumed to train a proficiency from Expert to Master."},
    "supply_satchel": {"name": "Reinforced Supply Satchel", "slot": "accessory", "tags": ["pack", "scavenging_gear"], "bonuses": {"scavenging": 1, "survival": 1}, "rarity": "common"},
    "warding_token": {"name": "Warding Token", "slot": "accessory", "tags": ["ward", "magic_focus"], "bonuses": {"magic": 1, "survival": 1}, "rarity": "uncommon"},
    "guildsteel_spear": {"name": "Guildsteel Spear", "slot": "weapon", "weapon_type": "spear", "weapon_scaling": "str", "power": 4, "tags": ["melee"], "bonuses": {"combat": 3, "survival": 1}, "rarity": "rare"},
    "salvager_goggles": {"name": "Salvager Goggles", "slot": "head", "tags": ["scavenging_gear"], "bonuses": {"scavenging": 2, "building": 1}, "attribute_bonuses": {"luk": 1}, "rarity": "uncommon"},
    "reinforced_vest": {"name": "Reinforced Vest", "slot": "body", "tags": ["armor"], "bonuses": {"combat": 1, "survival": 2}, "attribute_bonuses": {"vit": 1}, "rarity": "uncommon"},
    "ranger_cloak": {"name": "Ranger Cloak", "slot": "body", "tags": ["hunter", "scavenging_gear"], "bonuses": {"survival": 3, "scavenging": 2}, "attribute_bonuses": {"agi": 1}, "rarity": "rare"},
    "duelist_gloves": {"name": "Duelist Gloves", "slot": "hands", "tags": ["melee"], "bonuses": {"combat": 3}, "attribute_bonuses": {"dex": 1}, "rarity": "rare"},
    "trailblazer_boots": {"name": "Trailblazer Boots", "slot": "feet", "tags": ["scavenging_gear"], "bonuses": {"survival": 3, "scavenging": 1}, "attribute_bonuses": {"agi": 2}, "rarity": "rare"},
    "apothecary_belt": {"name": "Apothecary Belt", "slot": "accessory", "tags": ["medical_gear", "alchemy_gear"], "bonuses": {"medicine": 3, "alchemy": 3}, "attribute_bonuses": {"int": 1}, "rarity": "rare"},
    "engineers_bracers": {"name": "Engineer's Bracers", "slot": "hands", "tags": ["construction_gear", "breaching"], "bonuses": {"building": 4, "scavenging": 1}, "attribute_bonuses": {"str": 1, "int": 1}, "granted_perks": ["masterwork"], "rarity": "epic"},
    "tower_shield": {"name": "Guild Tower Shield", "slot": "offhand", "tags": ["shield", "knightly"], "bonuses": {"combat": 3, "survival": 2}, "attribute_bonuses": {"vit": 2}, "granted_perks": ["shield_wall", "guard"], "rarity": "epic"},
    "warhammer": {"name": "Siegebreaker Warhammer", "slot": "weapon", "weapon_type": "hammer", "weapon_scaling": "str", "power": 5, "tags": ["melee", "breaching"], "bonuses": {"combat": 4, "building": 2}, "attribute_bonuses": {"str": 1}, "granted_perks": ["masterwork"], "rarity": "epic"},
    "moonwood_longbow": {"name": "Moonwood Longbow", "slot": "weapon", "weapon_type": "bow", "weapon_scaling": "dex", "power": 5, "tags": ["ranged", "hunter"], "bonuses": {"combat": 4, "survival": 2}, "attribute_bonuses": {"dex": 1, "agi": 1}, "rarity": "epic"},
    "archmage_grimoire": {"name": "Archmage's Grimoire", "slot": "offhand", "tags": ["magic_focus"], "bonuses": {"magic": 5, "alchemy": 2}, "attribute_bonuses": {"int": 2}, "granted_perks": ["magic_resistance"], "rarity": "mythic"},
    "saints_censer": {"name": "Saint's Censer", "slot": "offhand", "tags": ["divine", "ward", "medical_gear"], "bonuses": {"medicine": 4, "magic": 4}, "attribute_bonuses": {"int": 1, "luk": 1}, "granted_perks": ["divine_magic", "soul_anchor"], "rarity": "mythic"},
    "goblin_war_token": {"name": "Goblin War Token", "slot": None, "tags": ["event", "goblin"], "bonuses": {}, "rarity": "event", "description": "A marked token recovered from the Green Warhost."},
    "chieftain_command_horn": {"name": "Chieftain's Command Horn", "slot": "accessory", "tags": ["goblin", "command", "capture_reward"], "bonuses": {"combat": 2, "survival": 2}, "attribute_bonuses": {"luk": 1}, "granted_perks": ["warhost_command"], "rarity": "epic", "description": "Taken intact from a captured warcamp chief. Its calls can redirect goblin patrols and open command routes."},
    "cartmaster_route_book": {"name": "Cartmaster's Route Book", "slot": "accessory", "tags": ["goblin", "raider", "intel", "capture_reward"], "bonuses": {"scavenging": 3, "survival": 1}, "attribute_bonuses": {"int": 1, "luk": 1}, "granted_perks": ["bannerbreaker"], "rarity": "rare", "description": "A coded road book surrendered during the live interrogation of a warhost cartmaster."},
    "ironcap_buckler": {"name": "Ironcap Buckler", "slot": "offhand", "tags": ["shield", "goblin"], "bonuses": {"combat": 3, "survival": 2}, "attribute_bonuses": {"vit": 2}, "granted_perks": ["shield_wall"], "rarity": "rare"},
    "crooked_shaman_staff": {"name": "Crooked Shaman Staff", "slot": "weapon", "weapon_type": "staff", "weapon_scaling": "int", "power": 5, "tags": ["magic", "goblin", "magic_focus"], "bonuses": {"magic": 5, "combat": 2}, "attribute_bonuses": {"int": 2}, "granted_perks": ["warhost_command"], "rarity": "epic"},
    "warlords_cleaver": {"name": "Warlord's Cleaver", "slot": "weapon", "weapon_type": "axe", "weapon_scaling": "str", "power": 6, "tags": ["melee", "goblin"], "bonuses": {"combat": 5}, "attribute_bonuses": {"str": 2, "vit": 1}, "granted_perks": ["warhost_command", "orcish_might"], "rarity": "mythic"},
    "warhost_banner": {"name": "Warhost Banner", "slot": "accessory", "tags": ["goblin", "command"], "bonuses": {"combat": 4, "survival": 3}, "attribute_bonuses": {"vit": 1, "luk": 1}, "granted_perks": ["warhost_command"], "rarity": "epic"},
    "grave_ash": {"name": "Consecrated Grave Ash", "slot": None, "tags": ["event", "undead"], "bonuses": {}, "rarity": "event", "description": "Ash gathered after quieting one of the restless dead."},
    "ashen_reliquary": {"name": "Ashen Reliquary", "slot": "accessory", "tags": ["ward", "undead", "magic_focus"], "bonuses": {"magic": 3, "medicine": 2}, "attribute_bonuses": {"luk": 1}, "granted_perks": ["soul_anchor"], "rarity": "rare"},
    "death_knight_helm": {"name": "Death Knight Helm", "slot": "head", "tags": ["armor", "undead"], "bonuses": {"combat": 5, "survival": 2}, "attribute_bonuses": {"vit": 2, "str": 1}, "granted_perks": ["undead_hunter", "soul_anchor"], "rarity": "epic"},
    "mourning_blade": {"name": "Mourning Blade", "slot": "weapon", "weapon_type": "sword", "weapon_scaling": "str", "power": 6, "tags": ["melee", "sword", "undead"], "bonuses": {"combat": 5, "magic": 2}, "attribute_bonuses": {"str": 1, "luk": 1}, "granted_perks": ["graveward", "soul_anchor"], "rarity": "mythic"},
    "corpse_lantern": {"name": "Corpse Lantern", "slot": "offhand", "tags": ["undead", "magic_focus"], "bonuses": {"magic": 4, "survival": 3}, "attribute_bonuses": {"int": 1}, "granted_perks": ["soul_anchor"], "rarity": "epic"},
    "mana_prism": {"name": "Raw Mana Prism", "slot": None, "tags": ["event", "arcane"], "bonuses": {}, "rarity": "event", "description": "A stable prism formed during an Arcane Convergence."},
    "spellglass_lens": {"name": "Spellglass Lens", "slot": "accessory", "tags": ["arcane", "magic_focus"], "bonuses": {"magic": 4, "scavenging": 2}, "attribute_bonuses": {"int": 1, "luk": 1}, "rarity": "rare"},
    "bottled_storm": {"name": "Bottled Storm", "slot": "offhand", "tags": ["arcane", "magic_focus"], "bonuses": {"magic": 5, "combat": 2}, "attribute_bonuses": {"int": 1, "luk": 2}, "granted_perks": ["stormbound"], "rarity": "epic"},
    "gravity_boots": {"name": "Gravity Boots", "slot": "feet", "tags": ["arcane"], "bonuses": {"magic": 3, "survival": 3}, "attribute_bonuses": {"agi": 2, "int": 1}, "granted_perks": ["gravity_walker"], "rarity": "epic"},
    "living_grimoire": {"name": "Living Grimoire", "slot": "offhand", "tags": ["arcane", "magic_focus"], "bonuses": {"magic": 6, "alchemy": 3}, "attribute_bonuses": {"int": 2, "luk": 1}, "granted_perks": ["ley_touched", "dream_sense"], "rarity": "mythic"},
    "beast_heart": {"name": "Great Beast Heartstone", "slot": None, "tags": ["event", "beast"], "bonuses": {}, "rarity": "event", "description": "A hardened core left by a creature of the Great Beast Tide."},
    "alpha_fang": {"name": "Alpha Fang", "slot": "accessory", "tags": ["beast", "hunter"], "bonuses": {"combat": 3, "survival": 3}, "attribute_bonuses": {"str": 1, "agi": 1}, "granted_perks": ["apex_instinct"], "rarity": "rare"},
    "thunderhide_coat": {"name": "Thunderhide Coat", "slot": "body", "tags": ["beast", "armor"], "bonuses": {"survival": 5, "combat": 2}, "attribute_bonuses": {"vit": 3}, "granted_perks": ["titan_strength"], "rarity": "epic"},
    "titanbone_spear": {"name": "Titanbone Spear", "slot": "weapon", "weapon_type": "spear", "weapon_scaling": "str", "power": 6, "tags": ["beast", "melee", "hunter"], "bonuses": {"combat": 5, "survival": 3}, "attribute_bonuses": {"str": 2}, "granted_perks": ["titan_strength"], "rarity": "mythic"},
    "razorwing_cloak": {"name": "Razorwing Cloak", "slot": "body", "tags": ["beast", "hunter"], "bonuses": {"survival": 4, "scavenging": 2}, "attribute_bonuses": {"agi": 2, "dex": 1}, "granted_perks": ["apex_instinct"], "rarity": "epic"},
    "starfall_shard": {"name": "Starfall Shard", "slot": None, "tags": ["event", "starfall"], "bonuses": {}, "rarity": "event", "description": "A warm fragment of matter that fell from beyond the sky."},
    "star_metal_blade": {"name": "Star-Metal Blade", "slot": "weapon", "weapon_type": "sword", "weapon_scaling": "str", "power": 7, "tags": ["melee", "sword", "starfall"], "bonuses": {"combat": 6, "magic": 2}, "attribute_bonuses": {"str": 2, "luk": 1}, "granted_perks": ["stellar_aegis"], "rarity": "epic"},
    "voidglass_mantle": {"name": "Voidglass Mantle", "slot": "body", "tags": ["starfall", "magic_resistance"], "bonuses": {"magic": 5, "survival": 4}, "attribute_bonuses": {"int": 2, "vit": 2}, "granted_perks": ["void_sight", "stellar_aegis"], "rarity": "mythic"},
    "starfall_core": {"name": "Starfall Core", "slot": "accessory", "tags": ["starfall", "magic_focus"], "bonuses": {"magic": 7, "combat": 3}, "attribute_bonuses": {"int": 3, "luk": 3}, "granted_perks": ["star_touched", "stellar_aegis", "void_sight"], "rarity": "mythic"},
    "comet_string_bow": {"name": "Comet-String Bow", "slot": "weapon", "weapon_type": "bow", "weapon_scaling": "dex", "power": 7, "tags": ["ranged", "starfall"], "bonuses": {"combat": 6, "scavenging": 2}, "attribute_bonuses": {"dex": 2, "agi": 1}, "granted_perks": ["gravity_walker"], "rarity": "mythic"},
    "celestial_halo": {"name": "Celestial Halo", "slot": "head", "tags": ["starfall", "magic_focus"], "bonuses": {"magic": 6, "medicine": 3}, "attribute_bonuses": {"int": 2, "luk": 2}, "granted_perks": ["stellar_aegis", "astral_sense"], "rarity": "mythic"},
}
ITEMS.update({
    "black_banner_cipher": {"name": "Black-Banner Cipher", "slot": None, "tags": ["story", "raider", "keepsake"], "bonuses": {}, "rarity": "story", "description": "A decoded strip of the raiders' tribute ledger. It proves the attacks were organized around old royal sites."},
    "empty_crown_standard": {"name": "Standard of the Empty Crown", "slot": "accessory", "tags": ["story", "command", "raider"], "bonuses": {"combat": 3, "scavenging": 3}, "attribute_bonuses": {"luk": 2}, "granted_perks": ["bannerbreaker", "warhost_command"], "rarity": "legendary", "description": "The standard under which Lareth's surviving raider captains tried to crown a new warlord."},
    "mudbound_clapper": {"name": "Mudbound Bell Clapper", "slot": None, "tags": ["story", "undead", "keepsake"], "bonuses": {}, "rarity": "story", "description": "The silenced heart of a chapel bell that once called Lareth's forgotten dead by name."},
    "bell_of_last_rites": {"name": "Bell of Last Rites", "slot": "offhand", "tags": ["story", "undead", "divine", "magic_focus"], "bonuses": {"magic": 4, "medicine": 4}, "attribute_bonuses": {"int": 1, "luk": 2}, "granted_perks": ["keeper_of_last_rites", "soul_anchor"], "rarity": "legendary", "description": "Its quiet note reminds oath-bound spirits that death was meant to have an ending."},
    "brass_foreman_key": {"name": "Brass Foreman's Key", "slot": None, "tags": ["story", "arcane", "keepsake"], "bonuses": {}, "rarity": "story", "description": "A command key carrying the three-ring seal of the Meridian Collegium."},
    "meridian_heart": {"name": "Heart of the Meridian", "slot": "accessory", "tags": ["story", "arcane", "machine", "magic_focus"], "bonuses": {"magic": 5, "building": 4}, "attribute_bonuses": {"int": 2, "luk": 1}, "granted_perks": ["meridian_attunement", "stormbound"], "rarity": "legendary", "description": "A regulated fragment of Lareth's surviving planar engine. It still seeks the rest of its network."},
    "colossus_heartblood": {"name": "Colossus Heartblood", "slot": None, "tags": ["story", "beast", "keepsake"], "bonuses": {}, "rarity": "story", "description": "A crystallized drop freely given by the wounded titan after its treatment."},
    "titan_shepherds_horn": {"name": "Titan Shepherd's Horn", "slot": "accessory", "tags": ["story", "beast", "command"], "bonuses": {"survival": 5, "combat": 2}, "attribute_bonuses": {"vit": 2, "luk": 1}, "granted_perks": ["titan_speaker", "beast_bond"], "rarity": "legendary", "description": "Its call can be felt through the oldest migration roads, even when it cannot be heard."},
    "echoing_starstone": {"name": "Echoing Starstone", "slot": None, "tags": ["story", "starfall", "keepsake"], "bonuses": {}, "rarity": "story", "description": "A hollow fragment that remembers the names of those who answered its signal."},
    "starless_gate_sigil": {"name": "Sigil of the Starless Gate", "slot": "accessory", "tags": ["story", "starfall", "void", "magic_focus"], "bonuses": {"magic": 6, "survival": 3}, "attribute_bonuses": {"int": 2, "luk": 2}, "granted_perks": ["riftwalker", "void_sight"], "rarity": "legendary", "description": "A treaty-mark and planar key recognized by the Voidsent houses beyond the dead stars."},
})

RANK_REWARD_SCALING = {
    "E": {"loot_rolls": 1, "loot_chance": 28, "authored_item_chance": 55, "gold": (4, 7)},
    "D": {"loot_rolls": 1, "loot_chance": 35, "authored_item_chance": 60, "gold": (8, 13)},
    "C": {"loot_rolls": 2, "loot_chance": 42, "authored_item_chance": 65, "gold": (15, 23)},
    "B": {"loot_rolls": 2, "loot_chance": 50, "authored_item_chance": 70, "gold": (28, 40)},
    "A": {"loot_rolls": 3, "loot_chance": 58, "authored_item_chance": 75, "gold": (55, 80)},
    "S": {"loot_rolls": 4, "loot_chance": 68, "authored_item_chance": 85, "gold": (100, 150)},
}
GENERAL_LOOT_TABLE = [
    ("training_manual", "E", 18), ("supply_satchel", "E", 14), ("work_gloves", "E", 12),
    ("cargo_pants", "E", 10), ("salvager_goggles", "D", 11), ("reinforced_vest", "D", 11),
    ("field_pack", "D", 10), ("short_bow", "D", 9), ("warding_token", "C", 8),
    ("breaching_charge", "C", 7), ("ranger_cloak", "C", 7), ("duelist_gloves", "C", 7),
    ("trailblazer_boots", "C", 7), ("apothecary_belt", "C", 6), ("specialist_tome", "B", 5),
    ("guildsteel_spear", "B", 5), ("engineers_bracers", "B", 3), ("tower_shield", "B", 3),
    ("warhammer", "A", 3), ("moonwood_longbow", "A", 3), ("archmage_grimoire", "S", 1),
    ("saints_censer", "S", 1), ("mastery_codex", "S", 1),
]
EVENT_REWARD_TABLES = {
    "goblin_warhost": {"keepsake": "goblin_war_token", "perk": "warhost_veteran", "loot": [("ironcap_buckler", "C", 9), ("warhost_banner", "B", 6), ("crooked_shaman_staff", "A", 4), ("warlords_cleaver", "S", 1)], "recruits": [("kobold", "D", 10), ("hobgoblin", "C", 8), ("orc", "B", 6), ("bugbear", "A", 4)]},
    "ashen_procession": {"keepsake": "grave_ash", "perk": "graveward", "loot": [("ashen_reliquary", "C", 9), ("corpse_lantern", "B", 6), ("death_knight_helm", "A", 4), ("mourning_blade", "S", 1)], "recruits": [("ashborn", "D", 10), ("dhampir", "C", 8), ("graveborn", "B", 6), ("revenant", "A", 4)]},
    "arcane_convergence": {"keepsake": "mana_prism", "perk": "ley_touched", "loot": [("spellglass_lens", "C", 9), ("gravity_boots", "B", 6), ("bottled_storm", "A", 4), ("living_grimoire", "S", 1)], "recruits": [("gnome", "D", 10), ("high_elf", "C", 8), ("homunculus", "B", 6), ("dreamkin", "A", 4), ("manaforged", "S", 2)]},
    "great_beast_tide": {"keepsake": "beast_heart", "perk": "beast_bond", "loot": [("alpha_fang", "C", 9), ("razorwing_cloak", "B", 6), ("thunderhide_coat", "A", 4), ("titanbone_spear", "S", 1)], "recruits": [("catfolk", "D", 10), ("faun", "D", 8), ("lizardfolk", "C", 8), ("harpy", "B", 6), ("centaur", "A", 4), ("minotaur", "S", 2)]},
    "starfall_omen": {"keepsake": "starfall_shard", "perk": "star_touched", "loot": [("star_metal_blade", "B", 8), ("voidglass_mantle", "A", 4), ("comet_string_bow", "A", 4), ("starfall_core", "S", 2), ("celestial_halo", "S", 1)], "recruits": [("cometkin", "C", 10), ("astral_elf", "B", 8), ("voidborn", "A", 6), ("starforged", "S", 4), ("celestine", "S", 2)]},
}

# Named authored characters are deliberately isolated here so they can later be removed or swapped
# without changing any mission/base engine code.
CHAMPIONS = {
    "saber": {
        "name": "Saber", "race": "Human", "series": "Fate/stay night", "source_kind": "champion",
        "traits": ["knight", "swordsman", "magic_resistance"],
        "stats": {"combat": 9, "scavenging": 3, "building": 2, "medicine": 2, "cooking": 2, "survival": 7, "magic": 6},
        "attributes": {"str": 9, "dex": 7, "agi": 8, "vit": 8, "int": 7, "luk": 7},
        "specialty": "Knight", "portrait": "",
    },
    "goblin_slayer": {
        "name": "Goblin Slayer", "race": "Human", "series": "Goblin Slayer", "source_kind": "champion",
        "traits": ["goblin_hunter", "tracker", "guard"],
        "stats": {"combat": 9, "scavenging": 6, "building": 4, "medicine": 3, "cooking": 2, "survival": 9, "magic": 1},
        "attributes": {"str": 8, "dex": 8, "agi": 7, "vit": 9, "int": 6, "luk": 3},
        "specialty": "Goblin Hunter", "portrait": "",
    },
    "sword_maiden": {
        "name": "Sword Maiden", "race": "Human", "series": "Goblin Slayer", "source_kind": "champion",
        "traits": ["priestess", "divine_magic", "goblin_survivor"],
        "stats": {"combat": 6, "scavenging": 3, "building": 2, "medicine": 9, "cooking": 4, "survival": 6, "magic": 9},
        "attributes": {"str": 4, "dex": 6, "agi": 5, "vit": 6, "int": 9, "luk": 7},
        "specialty": "Archbishop", "portrait": "",
    },
    "seraphine_vale": {
        "name": "Seraphine Vale", "race": "Human", "series": "Original", "source_kind": "champion",
        "traits": ["exorcist", "undead_hunter", "medic"],
        "stats": {"combat": 7, "scavenging": 3, "building": 2, "medicine": 8, "cooking": 3, "survival": 7, "magic": 9},
        "attributes": {"str": 4, "dex": 6, "agi": 6, "vit": 7, "int": 9, "luk": 6},
        "specialty": "Exorcist", "portrait": "",
    },
}
CHAMPIONS.update(EXPANDED_CHAMPIONS)
CHAMPIONS.update(LOWER_TIER_CHAMPIONS)

GENERIC_ARCHETYPES = {
    "scout": {"specialty": "Scout", "traits": ["scout"], "stats": {"combat": 4, "scavenging": 7, "building": 2, "medicine": 2, "cooking": 3, "survival": 6, "magic": 1}, "attributes": {"str": 4, "dex": 7, "agi": 8, "vit": 4, "int": 4, "luk": 6}},
    "builder": {"specialty": "Builder", "traits": ["engineer"], "stats": {"combat": 3, "scavenging": 4, "building": 8, "medicine": 2, "cooking": 2, "survival": 5, "magic": 1}, "attributes": {"str": 7, "dex": 4, "agi": 4, "vit": 7, "int": 5, "luk": 4}},
    "medic": {"specialty": "Medic", "traits": ["medic"], "stats": {"combat": 2, "scavenging": 4, "building": 2, "medicine": 8, "cooking": 3, "survival": 5, "magic": 1}, "attributes": {"str": 3, "dex": 5, "agi": 5, "vit": 5, "int": 8, "luk": 5}},
    "fighter": {"specialty": "Fighter", "traits": ["guard"], "stats": {"combat": 8, "scavenging": 3, "building": 3, "medicine": 1, "cooking": 2, "survival": 6, "magic": 1}, "attributes": {"str": 8, "dex": 5, "agi": 5, "vit": 8, "int": 3, "luk": 4}},
    "adept": {"specialty": "Adept", "traits": ["fire_magic"], "stats": {"combat": 5, "scavenging": 3, "building": 2, "medicine": 2, "cooking": 4, "survival": 5, "magic": 8}, "attributes": {"str": 3, "dex": 5, "agi": 5, "vit": 4, "int": 9, "luk": 6}},
}

GENERIC_FIRST_NAMES = ["Mara", "Tess", "Kael", "Rin", "Aya", "Niko", "Sera", "Vale", "Iris", "Rowan", "Mika", "Dane"]
GENERIC_LAST_NAMES = ["Quill", "Vale", "Rook", "Ember", "Stone", "Morrow", "Kestrel", "Ward", "Reyes", "Venn", "Cross", "Hale"]

MISSION_TEMPLATES = {
    "roadside_store": {
        "name": "Abandoned Roadside Store", "description": "A stripped roadside store still has a locked stockroom and a collapsed rear aisle.",
        "stat": "scavenging", "difficulty": 10, "party_size": 1, "durations": [60, 300], "pool_weight": 12,
        "claim_requirements": [],
        "visible_hints": ["High Scavenging helps.", "Fire magic can create a safer alternate route."],
        "modifiers": [{"kind": "trait", "value": "fire_magic", "bonus": 3, "label": "Fire magic burns through the jammed rear door"}, {"kind": "attribute", "attribute": "luk", "op": ">=", "value": 7, "bonus": 1, "label": "LUK 7+ uncovers an overlooked cache"}],
        "critical_any": [{"kind": "trait", "value": "fire_magic", "label": "Fire Magic"}, {"kind": "stat", "stat": "scavenging", "op": ">=", "value": 8, "label": "Scavenging 8+"}],
        "special_events": [],
        "rewards": {"materials": {"food": 8, "wood": 24, "scrap": 8, "cloth": 4}, "blueprint": "storage_shed"},
        "critical_rewards": {"materials": {"scrap": 8}, "item": "field_pack"},
        "reward_preview": ["Materials", "Storage blueprint", "Gear"],
    },
    "raider_checkpoint": {
        "name": "Abandoned Raider Checkpoint", "description": "A barricaded checkpoint has been deserted, but automated traps are still live.",
        "stat": "combat", "difficulty": 12, "party_size": 2, "durations": [300, 1800], "pool_weight": 10,
        "claim_requirements": [{"kind": "stat", "stat": "combat", "op": ">=", "value": 4, "label": "At least one Combat 4+"}],
        "visible_hints": ["Bring two capable fighters.", "Breaching equipment may expose the secured cache."],
        "modifiers": [{"kind": "item_tag", "value": "breaching", "bonus": 3, "label": "Breaching equipment bypasses the trapped door"}, {"kind": "attribute", "attribute": "dex", "op": ">=", "value": 7, "bonus": 1, "label": "DEX 7+ reacts quickly to the trap mechanisms"}],
        "critical_any": [{"kind": "weapon_type", "value": "sword", "label": "Sword equipped"}, {"kind": "stat", "stat": "combat", "op": ">=", "value": 9, "label": "Combat 9+"}],
        "special_events": [],
        "rewards": {"materials": {"scrap": 12, "food": 4}, "item": "scrap_hatchet"},
        "critical_rewards": {"item": "breaching_charge", "generic_recruit": "fighter"},
        "reward_preview": ["Weapons", "Materials", "Possible recruit"],
    },
    "industrial_yard": {
        "name": "Silent Industrial Yard", "description": "Tool lockers and a half-collapsed maintenance bay promise useful salvage.",
        "stat": "building", "difficulty": 13, "party_size": 2, "durations": [1800], "pool_weight": 9,
        "claim_requirements": [{"kind": "building", "value": "storage_shed", "label": "Storage Shed built"}],
        "visible_hints": ["Building skill matters.", "Engineers can identify intact machinery."],
        "modifiers": [{"kind": "trait", "value": "engineer", "bonus": 4, "label": "Engineer identifies intact machinery"}, {"kind": "item_tag", "value": "construction_gear", "bonus": 2, "label": "Construction gear"}],
        "critical_any": [{"kind": "stat", "stat": "building", "op": ">=", "value": 8, "label": "Building 8+"}],
        "special_events": [],
        "rewards": {"materials": {"scrap": 22, "wood": 16}, "blueprint": "workshop"},
        "critical_rewards": {"item": "hard_hat", "generic_recruit": "builder"},
        "reward_preview": ["Workshop blueprint", "Construction gear", "Possible builder"],
    },
    "field_clinic": {
        "name": "Ruined Field Clinic", "description": "An emergency clinic was abandoned in a hurry. Medicine remains behind unstable debris.",
        "stat": "medicine", "difficulty": 14, "party_size": 2, "durations": [1800], "pool_weight": 8,
        "claim_requirements": [{"kind": "stat", "stat": "medicine", "op": ">=", "value": 4, "label": "At least one Medicine 4+"}],
        "visible_hints": ["Medicine is the primary check.", "Medical gear can substantially improve the run."],
        "modifiers": [{"kind": "trait", "value": "medic", "bonus": 4, "label": "Medic recognizes salvageable supplies"}, {"kind": "item_tag", "value": "medical_gear", "bonus": 2, "label": "Medical equipment"}],
        "critical_any": [{"kind": "stat", "stat": "medicine", "op": ">=", "value": 8, "label": "Medicine 8+"}],
        "special_events": [],
        "rewards": {"materials": {"medicine": 10, "cloth": 10, "wood": 18, "scrap": 6}, "blueprint": "infirmary"},
        "critical_rewards": {"item": "medic_coat", "generic_recruit": "medic"},
        "reward_preview": ["Medicine", "Infirmary blueprint", "Possible medic"],
    },
    "ash_tunnel": {
        "name": "Ash Tunnel", "description": "A transit tunnel is choked with smoke and ash. Valuable cargo sits beyond the collapsed cars.",
        "stat": "survival", "difficulty": 15, "party_size": 3, "durations": [1800, 3600], "pool_weight": 7,
        "claim_requirements": [{"kind": "stat", "stat": "survival", "op": ">=", "value": 5, "label": "At least one Survival 5+"}],
        "visible_hints": ["Survival is crucial.", "Heat-resistant traits or fire magic can bypass hazards."],
        "modifiers": [{"kind": "trait", "value": "heatproof", "bonus": 4, "label": "Heatproof explorer"}, {"kind": "trait", "value": "fire_magic", "bonus": 2, "label": "Fire magic controls burning debris"}, {"kind": "attribute", "attribute": "vit", "op": ">=", "value": 7, "bonus": 2, "label": "VIT 7+ endures the smoke and heat"}],
        "critical_any": [{"kind": "trait", "value": "fire_magic", "label": "Fire Magic"}],
        "special_events": [],
        "rewards": {"materials": {"scrap": 20, "wood": 34, "cloth": 4, "food": 6}, "blueprint": "barracks"},
        "critical_rewards": {"item": "short_bow", "generic_recruit": "scout"},
        "reward_preview": ["Barracks blueprint", "Materials", "Possible scout"],
    },
    "old_armory": {
        "name": "Sealed Old Armory", "description": "A reinforced armory survived intact. Opening it safely requires both muscle and proper gear.",
        "stat": "combat", "difficulty": 16, "party_size": 3, "durations": [1800, 7200], "pool_weight": 5,
        "claim_requirements": [{"kind": "count", "min": 2, "condition": {"kind": "equipped_slot", "slot": "weapon"}, "label": "Two armed characters"}],
        "visible_hints": ["At least two characters must have weapons equipped.", "Breaching gear is especially valuable."],
        "modifiers": [{"kind": "item_tag", "value": "breaching", "bonus": 4, "label": "Breaching equipment"}],
        "critical_any": [{"kind": "weapon_type", "value": "sword", "label": "Sword user present"}],
        "special_events": [],
        "rewards": {"materials": {"scrap": 30}, "item": "knight_blade"},
        "critical_rewards": {"item": "breaching_charge"},
        "reward_preview": ["Rare weapons", "Breaching gear", "Scrap"],
    },
    "summoning_trace": {
        "name": "Impossible Summoning Trace", "description": "A strange magical signature has appeared beyond the camp's mapped territory.",
        "stat": "magic", "difficulty": 17, "party_size": 4, "durations": [3600, 14400], "pool_weight": 3,
        "claim_requirements": [{"kind": "stat", "stat": "magic", "op": ">=", "value": 5, "label": "At least one Magic 5+"}],
        "visible_hints": ["This is a difficult magical expedition.", "Certain series or magical equipment may trigger unusual events."],
        "modifiers": [{"kind": "item_tag", "value": "magic_focus", "bonus": 3, "label": "Magic focus equipped"}, {"kind": "trait", "value": "fire_magic", "bonus": 1, "label": "Elemental mage present"}, {"kind": "attribute", "attribute": "int", "op": ">=", "value": 8, "bonus": 2, "label": "INT 8+ stabilizes the summoning trace"}],
        "critical_any": [{"kind": "series", "value": "Fate/stay night", "label": "Fate-series resonance"}, {"kind": "stat", "stat": "magic", "op": ">=", "value": 9, "label": "Magic 9+"}],
        "special_events": [{"condition": {"kind": "series", "value": "Fate/stay night"}, "label": "A familiar magical signature answers the party."}],
        "rewards": {"materials": {"scrap": 18, "medicine": 4}, "item": "ember_staff"},
        "critical_rewards": {"champion": "saber"},
        "reward_preview": ["Rare gear", "Champion encounter", "Materials"],
    },
    "deep_expedition": {
        "name": "Deep Wilds Expedition", "description": "A long-range expedition beyond every safe route currently mapped by the settlement.",
        "stat": "survival", "difficulty": 18, "party_size": 4, "durations": [86400], "pool_weight": 1,
        "claim_requirements": [{"kind": "count", "min": 2, "condition": {"kind": "stat", "stat": "survival", "op": ">=", "value": 6}, "label": "Two characters with Survival 6+"}],
        "visible_hints": ["This mission takes a full day.", "A broad, well-equipped roster has the best odds."],
        "modifiers": [{"kind": "item_tag", "value": "pack", "bonus": 2, "label": "Field pack"}, {"kind": "trait", "value": "scout", "bonus": 2, "label": "Scout present"}, {"kind": "attribute", "attribute": "agi", "op": ">=", "value": 7, "bonus": 1, "label": "AGI 7+ keeps pace through difficult terrain"}],
        "critical_any": [{"kind": "stat", "stat": "survival", "op": ">=", "value": 10, "label": "Survival 10+"}],
        "special_events": [],
        "rewards": {"materials": {"food": 30, "wood": 50, "scrap": 35, "medicine": 8}, "blueprint": "watchpost"},
        "critical_rewards": {"generic_recruit": "scout", "item": "field_pack"},
        "reward_preview": ["Large material haul", "Watchpost blueprint", "Recruit"],
    },
}

# Contextual procedural recruitment profiles. These are data-only so missions/mod packs can
# add or swap recruit pools without changing the character-generation engine.
RECRUIT_PROFILES = {
    "survivor": {
        "race": "Human", "series": "Original",
        "archetypes": ["scout", "builder", "medic", "fighter", "adept"],
        "extra_traits": ["survivor"],
    },
    "raider_defector": {
        "race": "Human", "series": "Original",
        "archetypes": ["fighter", "scout"],
        "extra_traits": ["raider", "defector"],
    },
    "captive_survivor": {
        "race": "Human", "series": "Original",
        "archetypes": ["medic", "builder", "scout", "adept"],
        "extra_traits": ["former_captive"],
    },
    "industrial_worker": {
        "race": "Human", "series": "Original",
        "archetypes": ["builder", "scout"],
        "extra_traits": ["salvager"],
    },
    "clinic_survivor": {
        "race": "Human", "series": "Original",
        "archetypes": ["medic"],
        "extra_traits": ["field_medic"],
    },
    "tunnel_scout": {
        "race": "Human", "series": "Original",
        "archetypes": ["scout", "fighter"],
        "extra_traits": ["tunnel_runner"],
    },
    "wilds_explorer": {
        "race": "Human", "series": "Original",
        "archetypes": ["scout"],
        "extra_traits": ["pathfinder"],
    },
    "goblin": {
        "race": "Goblin", "series": "Original",
        "archetypes": ["fighter", "scout"],
        "extra_traits": ["goblin", "scrapper"],
        "first_names": ["Nikka", "Brik", "Vexa", "Mog", "Rikka", "Skiv", "Talla", "Grin"],
        "last_names": ["Rusttooth", "Ashnose", "Tin-Ear", "Quickhand", "Rattle", "Sootfoot", "Crookblade", "Mossback"],
    },
    "goblin_boss": {
        "race": "Goblin", "series": "Original",
        "archetypes": ["fighter"], "portrait_tier": "special",
        "extra_traits": ["goblin", "boss", "war_leader"],
        "first_names": ["Ghazra", "Morka", "Vrix", "Skarn", "Ruzza", "Krag"],
        "last_names": ["Iron-Ear", "Redknife", "Many-Teeth", "Banner-Breaker", "Blacktusk", "Chain-Cutter"],
    },
    "dwarf": {
        "race": "Dwarf", "series": "Original", "archetypes": ["builder", "fighter", "medic"],
        "extra_traits": ["dwarven_resolve", "engineer"], "attribute_bonuses": {"str": 1, "vit": 2},
        "first_names": ["Brom", "Dagna", "Kelda", "Orik", "Runa", "Thrain"], "last_names": ["Ironroot", "Deepdelve", "Coppervein", "Anvilward"],
    },
    "wood_elf": {
        "race": "Wood Elf", "series": "Original", "archetypes": ["scout", "medic", "adept"],
        "extra_traits": ["elven_senses", "tracker"], "attribute_bonuses": {"dex": 1, "agi": 2},
        "first_names": ["Faela", "Lethan", "Naeris", "Oryn", "Sylvi", "Talen"], "last_names": ["Fernwatch", "Rainleaf", "Greenpath", "Owlwood"],
    },
    "half_orc": {
        "race": "Half-Orc", "series": "Original", "archetypes": ["fighter", "builder", "scout"],
        "extra_traits": ["orcish_might"], "attribute_bonuses": {"str": 1, "vit": 1, "agi": 1},
        "first_names": ["Kara", "Dren", "Malk", "Sura", "Vek", "Yara"], "last_names": ["Greyhand", "Two-Roads", "Stonejaw", "Far-Blood"],
    },
    "halfling": {
        "race": "Halfling", "series": "Original", "archetypes": ["scout", "medic", "builder"],
        "extra_traits": ["halfling_luck"], "attribute_bonuses": {"dex": 1, "agi": 1, "luk": 2},
        "first_names": ["Pella", "Bram", "Cora", "Milo", "Nessa", "Tobin"], "last_names": ["Goodbarrel", "Quickstep", "Hearthlane", "Thistlewick"],
    },
    "tiefling": {
        "race": "Tiefling", "series": "Original", "archetypes": ["adept", "scout", "fighter"],
        "extra_traits": ["infernal_legacy", "heatproof"], "attribute_bonuses": {"int": 1, "luk": 1, "vit": 1},
        "first_names": ["Avaris", "Kallista", "Mordai", "Nyx", "Riven", "Zara"], "last_names": ["Ashhorn", "Cinder-Vow", "Redstar", "Emberveil"],
    },
    "hobgoblin": {
        "race": "Hobgoblin", "series": "Original", "archetypes": ["fighter", "builder"],
        "extra_traits": ["hobgoblin_discipline", "guard"], "attribute_bonuses": {"str": 1, "vit": 1},
        "first_names": ["Azhak", "Velka", "Drav", "Kezra", "Torv", "Mazha"], "last_names": ["Ironrank", "Redbanner", "Stoneheel", "Marchborn"],
    },
    "bugbear": {
        "race": "Bugbear", "series": "Original", "archetypes": ["fighter", "scout"],
        "extra_traits": ["bugbear_ambush", "tracker"], "attribute_bonuses": {"str": 2, "agi": 1},
        "first_names": ["Brum", "Harka", "Grol", "Vurna", "Mogg", "Thessa"], "last_names": ["Softstep", "Longarm", "Nightbrush", "Quietmaul"],
    },
    "kobold": {
        "race": "Kobold", "series": "Original", "archetypes": ["builder", "scout", "adept"],
        "extra_traits": ["kobold_trapsmith", "engineer"], "attribute_bonuses": {"dex": 1, "int": 1, "luk": 1},
        "first_names": ["Kip", "Snik", "Tizzi", "Rekk", "Pexa", "Nib"], "last_names": ["Copperclaw", "Wiretail", "Deepburrow", "Spark-Eye"],
    },
    "orc": {
        "race": "Orc", "series": "Original", "archetypes": ["fighter", "builder", "medic"],
        "extra_traits": ["orcish_might"], "attribute_bonuses": {"str": 2, "vit": 1},
        "first_names": ["Gara", "Drok", "Usha", "Korr", "Maraag", "Thok"], "last_names": ["Stoneblood", "Ashspear", "Broadhand", "Oathkeeper"],
    },
    "revenant": {
        "race": "Revenant", "series": "Original", "archetypes": ["fighter", "adept"],
        "extra_traits": ["deathless", "soul_anchor"], "attribute_bonuses": {"vit": 2, "int": 1},
        "first_names": ["Adel", "Corvin", "Mirelle", "Orren", "Sabine", "Vey"], "last_names": ["Returned", "Last-Vow", "Ashwake", "Unburied"],
    },
    "high_elf": {
        "race": "High Elf", "series": "Original", "archetypes": ["adept", "scout", "medic"],
        "extra_traits": ["elven_senses", "ley_touched"], "attribute_bonuses": {"dex": 1, "int": 2},
        "first_names": ["Aelira", "Caelen", "Ithil", "Liora", "Theren", "Vaelis"], "last_names": ["Silverbranch", "Dawnscript", "Stillwater", "Moonarchive"],
    },
    "gnome": {
        "race": "Gnome", "series": "Original", "archetypes": ["builder", "adept", "medic"],
        "extra_traits": ["engineer", "ley_touched"], "attribute_bonuses": {"int": 2, "luk": 1},
        "first_names": ["Pim", "Nella", "Orbi", "Fizz", "Tavi", "Wren"], "last_names": ["Coilwick", "Prismgear", "Brightsocket", "Tinkertide"],
    },
    "manaforged": {
        "race": "Manaforged", "series": "Original", "archetypes": ["fighter", "builder", "adept"],
        "extra_traits": ["mana_body", "constructed"], "attribute_bonuses": {"vit": 2, "int": 2},
        "first_names": ["Axiom", "Lumen", "Prism", "Cipher", "Echo", "Vector"], "last_names": ["Seven", "Blue-Core", "Concordant", "Unbound"],
    },
    "homunculus": {
        "race": "Homunculus", "series": "Original", "archetypes": ["medic", "adept", "scout"],
        "extra_traits": ["mana_body"], "attribute_bonuses": {"int": 2, "luk": 1, "agi": 1},
        "first_names": ["Ione", "Alba", "Mellis", "Quin", "Rho", "Saffra"], "last_names": ["Glassborn", "Vessel", "Red-Seal", "Ninth Batch"],
    },
    "dreamkin": {
        "race": "Dreamkin", "series": "Original", "archetypes": ["adept", "scout"],
        "extra_traits": ["dream_sense", "ley_touched"], "attribute_bonuses": {"int": 1, "luk": 2, "agi": 1},
        "first_names": ["Somna", "Reverie", "Nim", "Velum", "Mira", "Oneir"], "last_names": ["Soft-Bell", "Half-Awake", "Cloudstep", "Lucid"],
    },
    "lizardfolk": {
        "race": "Lizardfolk", "series": "Original", "archetypes": ["fighter", "scout", "medic"],
        "extra_traits": ["scaled_hide", "tracker"], "attribute_bonuses": {"vit": 2, "agi": 1},
        "first_names": ["Sszara", "Keth", "Vriss", "Takka", "Zhal", "Isska"], "last_names": ["Reed-Stalker", "Sunscale", "Marsh-Claw", "Warm-Stone"],
    },
    "harpy": {
        "race": "Harpy", "series": "Original", "archetypes": ["scout", "fighter"],
        "extra_traits": ["winged", "feral_agility"], "attribute_bonuses": {"agi": 2, "dex": 1},
        "first_names": ["Aerie", "Kiri", "Talon", "Scree", "Vela", "Rissa"], "last_names": ["Cloudcry", "Ridgewing", "Stormfeather", "High-Nest"],
    },
    "minotaur": {
        "race": "Minotaur", "series": "Original", "archetypes": ["fighter", "builder"],
        "extra_traits": ["horned_guard", "guard"], "attribute_bonuses": {"str": 2, "vit": 2},
        "first_names": ["Tauren", "Brakka", "Meros", "Dama", "Korun", "Istra"], "last_names": ["Stonehorn", "Gatekeeper", "Red-Maze", "Broadback"],
    },
    "centaur": {
        "race": "Centaur", "series": "Original", "archetypes": ["scout", "fighter", "medic"],
        "extra_traits": ["pathfinder", "feral_agility"], "attribute_bonuses": {"agi": 2, "vit": 1, "str": 1},
        "first_names": ["Thessa", "Orun", "Kalai", "Merek", "Vasha", "Pelor"], "last_names": ["Farstrider", "Grass-Sea", "Thunderhoof", "Open-Sky"],
    },
    "astral_elf": {
        "race": "Astral Elf", "series": "Original", "archetypes": ["adept", "scout"],
        "extra_traits": ["astral_sense", "elven_senses"], "attribute_bonuses": {"int": 2, "luk": 2},
        "first_names": ["Astrael", "Lyss", "Caelum", "Nimara", "Orion", "Veyra"], "last_names": ["Starwake", "Night-Orbit", "Far-Lantern", "Comet-Veil"],
    },
}
RECRUIT_PROFILES.update(ADDITIONAL_RECRUIT_PROFILES)
for _obsolete_profile in ("ashborn", "dhampir", "graveborn", "cometkin", "voidborn", "starforged", "celestine"):
    RECRUIT_PROFILES.pop(_obsolete_profile, None)

# Event geography controls both eligibility and relative rarity. A minimum rank
# prevents mythic peoples from appearing in routine contracts even on a lucky roll.
EVENT_REWARD_TABLES["goblin_warhost"]["recruits"].extend([
    ("ogre", "B", 3), ("troll", "S", 1),
])
EVENT_REWARD_TABLES["ashen_procession"]["recruits"] = [
    ("undead", "D", 10), ("vampire", "C", 7), ("banshee", "A", 3), ("revenant", "A", 2),
]
EVENT_REWARD_TABLES["arcane_convergence"]["recruits"].extend([
    ("slimefolk", "D", 9), ("dark_elf", "C", 7), ("foxkin", "B", 4),
    ("automaton", "A", 3), ("fairy", "S", 1),
])
EVENT_REWARD_TABLES["great_beast_tide"]["recruits"].extend([
    ("foxkin", "C", 6),
    ("dryad", "B", 4), ("dragonkin", "S", 1),
])
EVENT_REWARD_TABLES["starfall_omen"]["recruits"] = [
    ("alien", "C", 10), ("astral_elf", "B", 8), ("voidsent", "A", 5),
    ("automaton", "A", 3), ("aasimar", "S", 1),
]

GENERAL_RECRUIT_TABLE = [
    ("survivor", "D", 12), ("dwarf", "C", 8), ("wood_elf", "C", 8),
    ("half_orc", "B", 7), ("halfling", "B", 7), ("tiefling", "A", 5),
]

# Demonstration mission for context-sensitive recruitment: if this mission awards a recruit,
# the result is usually a goblin from the camp, but can instead be a captive recovered there.
MISSION_TEMPLATES["goblin_warcamp"] = {
    "name": "Goblin Warcamp",
    "description": "A rough palisade blocks an old service road. Goblin raiders use the camp as a staging point and keep a handful of prisoners behind the cookfires.",
    "stat": "combat", "difficulty": 13, "party_size": 2, "durations": [300, 1800], "pool_weight": 9,
    "roles": [
        {"id": "tank", "label": "Tank", "metric": "constitution", "recommended": 7, "description": "Holds the gate and absorbs the camp's first counterattack."},
        {"id": "dps", "label": "DPS", "metric": "dps", "recommended": 9, "description": "Breaks priority targets using the equipped weapon's scaling stat."},
    ],
    "claim_requirements": [{"kind": "stat", "stat": "combat", "op": ">=", "value": 4, "label": "At least one Combat 4+"}],
    "visible_hints": ["Combat is the main check.", "Scouts and goblins can identify weak points in the camp perimeter."],
    "modifiers": [
        {"kind": "trait", "value": "scout", "bonus": 2, "label": "Scout finds a quiet approach"},
        {"kind": "race", "value": "Goblin", "bonus": 3, "label": "Goblin knows camp habits"},
    ],
    "critical_any": [
        {"kind": "race", "value": "Goblin", "label": "Goblin present"},
        {"kind": "stat", "stat": "combat", "op": ">=", "value": 9, "label": "Combat 9+"},
    ],
    "special_events": [
        {"condition": {"kind": "race", "value": "Goblin"}, "label": "The party uses goblin camp signals to cross the outer ring without raising the whole camp."}
    ],
    "rewards": {},
    "critical_rewards": {
        "item": "short_bow",
        "procedural_recruit": [
            {"profile": "goblin", "weight": 75},
            {"profile": "captive_survivor", "weight": 25},
        ],
    },
    "reward_preview": ["Corpse-based equipment and coin", "Possible contextual recruit", "More defeated goblins means more loot"],
}

# Rank progression. Building the Guild Hall moves a settlement from E to D; its paid
# visibility upgrades then unlock C, B, A and S in order.
_EXISTING_MISSION_RANKS = {
    "roadside_store": "E", "raider_checkpoint": "D", "industrial_yard": "D",
    "goblin_warcamp": "D", "field_clinic": "C", "ash_tunnel": "B",
    "old_armory": "B", "summoning_trace": "A", "deep_expedition": "S",
}
for _mission_id, _rank in _EXISTING_MISSION_RANKS.items():
    MISSION_TEMPLATES[_mission_id]["rank"] = _rank


def _expanded_mission(
    name: str, description: str, rank: str, stat: str, difficulty: int, party_size: int,
    durations: list[int], rewards: dict, critical_rewards: dict, reward_preview: list[str],
    requirements: list[dict] | None = None, modifiers: list[dict] | None = None,
    critical_any: list[dict] | None = None, roles: list[dict] | None = None,
    event: str | None = None,
) -> dict:
    return {
        "name": name, "description": description, "rank": rank, "stat": stat,
        "difficulty": difficulty, "party_size": party_size, "durations": durations,
        "pool_weight": 10, "claim_requirements": requirements or [],
        "visible_hints": [f"{stat.title()} is the primary check.", f"Recommended for {rank}-Rank parties."],
        "modifiers": modifiers or [], "critical_any": critical_any or [], "special_events": [],
        "roles": roles or [], "rewards": rewards, "critical_rewards": critical_rewards,
        "event": event,
        "reward_preview": reward_preview,
        "narrative": {
            "approach": f"{{party}} set out for {name} with {{lead}} directing the approach. {description}",
            "critical_failure": "The operation unraveled faster than the party could contain it. They abandoned the objective and returned shaken, carrying only a clearer understanding of the danger.",
            "failure": "The party reached the objective but could not secure it without unacceptable risk. They withdrew in good order and left the main prize behind.",
            "success": "The plan held together. The party secured the useful supplies, checked the route home, and returned with a haul worthy of the mission's rank.",
            "critical_success": "Every part of the operation aligned. The party broke through the central obstacle, found the best of the hidden stores, and returned with an exceptional haul.",
        },
    }


MISSION_TEMPLATES.update(CELESTIAL_CHAIN_STEPS)


MISSION_TEMPLATES.update({
    "fallen_orchard": _expanded_mission("Fallen Orchard", "An abandoned orchard still bears hardy fruit around a collapsed storehouse.", "E", "scavenging", 8, 1, [60, 300], {"materials": {"food": 12, "wood": 10}}, {"materials": {"food": 6, "cloth": 3}}, ["Food", "Wood"]),
    "creekside_scrap": _expanded_mission("Creekside Scrap Run", "Floodwater exposed a line of old vehicles and washed loose salvage onto the bank.", "E", "scavenging", 9, 1, [60, 300], {"materials": {"scrap": 10, "cloth": 4}}, {"item": "work_gloves"}, ["Scrap", "Cloth", "Gear"]),
    "missing_trapper": _expanded_mission("Missing Trapper's Cache", "Trail signs lead toward an emergency cache left by a trapper who never returned.", "E", "survival", 10, 1, [300], {"materials": {"food": 8, "wood": 14}}, {"item": "field_pack"}, ["Food", "Wood", "Possible gear"]),
    "charcoal_camp": _expanded_mission("Cold Charcoal Camp", "A deserted charcoal camp contains dry timber, tools, and covered fuel pits.", "E", "building", 10, 1, [300], {"materials": {"wood": 20, "scrap": 5}}, {"item": "hard_hat"}, ["Large wood haul", "Scrap"]),
    "herb_meadow": _expanded_mission("Medicinal Herb Meadow", "A sheltered meadow contains useful plants if they can be identified and gathered safely.", "E", "medicine", 9, 1, [60, 300], {"materials": {"medicine": 4, "food": 6, "cloth": 2}}, {"materials": {"medicine": 4}}, ["Medicine", "Food"]),
    "flooded_underpass": _expanded_mission("Flooded Underpass", "Submerged maintenance rooms may hold supplies beyond unstable water and debris.", "D", "survival", 12, 2, [300, 1800], {"materials": {"scrap": 18, "wood": 14, "food": 8}}, {"item": "field_pack"}, ["Materials", "Gear"], [{"kind": "stat", "stat": "survival", "op": ">=", "value": 4, "label": "At least one Survival 4+"}]),
    "collapsed_workshop": _expanded_mission("Collapsed Workshop", "A machine shop has one accessible wing and a tool cage behind a fractured roof.", "D", "building", 12, 2, [300, 1800], {"materials": {"scrap": 22, "wood": 18}}, {"item": "work_gloves"}, ["Scrap", "Construction gear"], [{"kind": "stat", "stat": "building", "op": ">=", "value": 4, "label": "At least one Building 4+"}]),
    "highway_ambush": _expanded_mission("Highway Ambush", "Raiders have occupied a narrow highway cut and are carrying stolen camp supplies.", "D", "combat", 13, 2, [300, 1800], {"materials": {"food": 12, "scrap": 14}}, {"item": "scrap_hatchet"}, ["Recovered supplies", "Weapon"], [{"kind": "stat", "stat": "combat", "op": ">=", "value": 5, "label": "At least one Combat 5+"}]),
    "quarantine_house": _expanded_mission("Quarantine House", "A sealed relief station contains medicine alongside hazards left by its last occupants.", "C", "medicine", 14, 2, [1800, 3600], {"materials": {"medicine": 14, "cloth": 14, "food": 10}}, {"item": "medic_coat"}, ["Large medicine haul", "Medical gear"], [{"kind": "stat", "stat": "medicine", "op": ">=", "value": 6, "label": "At least one Medicine 6+"}]),
    "bandit_outpost": _expanded_mission("Bandit Outpost", "A fortified hill outpost controls several scavenging routes and stores seized cargo.", "C", "combat", 15, 3, [1800, 3600], {"materials": {"food": 18, "scrap": 28, "wood": 22}}, {"item": "breaching_charge", "procedural_recruit": [{"profile": "raider_defector", "weight": 100}]}, ["Large material haul", "Recruit chance", "Gear"], [{"kind": "count", "min": 2, "condition": {"kind": "equipped_slot", "slot": "weapon"}, "label": "Two armed characters"}]),
    "arcane_observatory": _expanded_mission("Ruined Arcane Observatory", "A broken observatory still pulses around a sealed instrument chamber.", "C", "magic", 15, 2, [1800, 3600], {"materials": {"scrap": 20, "medicine": 8}}, {"item": "ember_staff"}, ["Magic weapon", "Rare materials"], [{"kind": "stat", "stat": "magic", "op": ">=", "value": 6, "label": "At least one Magic 6+"}]),
    "iron_ogre_bridge": _expanded_mission("Iron Ogre Bridge", "An armored ogre has turned a reinforced bridge into a toll gate for every nearby route.", "B", "combat", 17, 3, [3600, 7200], {"materials": {"food": 22, "scrap": 42, "wood": 30}}, {"item": "knight_blade"}, ["Rare weapon", "Major materials"], roles=[{"id": "tank", "label": "Tank", "metric": "constitution", "recommended": 9, "description": "Holds the ogre's attention."}, {"id": "striker", "label": "Striker", "metric": "dps", "recommended": 12, "description": "Breaks its armor at close range."}, {"id": "ranged", "label": "Ranged DPS", "metric": "dps", "recommended": 11, "description": "Attacks from outside its reach."}]),
    "haunted_foundry": _expanded_mission("Haunted Foundry", "A dormant foundry has restarted itself around a hostile magical presence.", "B", "magic", 17, 3, [3600, 7200], {"materials": {"scrap": 48, "wood": 28, "medicine": 8}}, {"item": "ember_staff"}, ["Rare gear", "Major scrap haul"], [{"kind": "stat", "stat": "magic", "op": ">=", "value": 7, "label": "At least one Magic 7+"}]),
    "dragon_roost": _expanded_mission("Young Dragon's Roost", "A young dragon has claimed a quarry filled with ore, tools, and tribute.", "A", "combat", 19, 4, [7200, 14400], {"materials": {"scrap": 70, "wood": 55, "medicine": 15, "food": 30}}, {"item": "knight_blade"}, ["Exceptional materials", "Rare weapon"], [{"kind": "count", "min": 3, "condition": {"kind": "equipped_slot", "slot": "weapon"}, "label": "Three armed characters"}]),
    "planar_breach": _expanded_mission("Planar Breach", "A widening fracture is spilling hostile energy and impossible debris into the region.", "A", "magic", 20, 4, [7200, 14400], {"materials": {"scrap": 55, "medicine": 24, "cloth": 35}}, {"item": "ember_staff"}, ["Arcane gear", "Exceptional resources"], [{"kind": "stat", "stat": "magic", "op": ">=", "value": 8, "label": "At least one Magic 8+"}]),
    "fallen_star_citadel": _expanded_mission("Fallen-Star Citadel", "A citadel built around a fallen star has opened for the first time in generations.", "S", "combat", 22, 5, [14400, 86400], {"materials": {"food": 60, "wood": 100, "scrap": 150, "cloth": 60, "medicine": 35}}, {"item": "knight_blade", "procedural_recruit": [{"profile": "wilds_explorer", "weight": 100}]}, ["Massive resource haul", "Rare weapon", "Elite recruit"], [{"kind": "count", "min": 4, "condition": {"kind": "equipped_slot", "slot": "weapon"}, "label": "Four armed characters"}]),
})

# Event-exclusive contracts only enter the pool while their regional event is active.
MISSION_TEMPLATES.update({
    "goblin_tracks": _expanded_mission("Fresh Goblin Tracks", "Fresh tracks circle isolated farms where tools and livestock have gone missing.", "E", "survival", 10, 1, [60, 300], {"materials": {"food": 10, "wood": 12}}, {"item": "work_boots"}, ["Supplies", "Scout gear"], event="goblin_warhost"),
    "goblin_supply_carts": _expanded_mission("Goblin Supply Carts", "A guarded cart train is carrying stolen provisions toward the gathering warhost.", "D", "combat", 13, 2, [300, 1800], {"materials": {"food": 20, "scrap": 15}}, {"item": "short_bow"}, ["Recovered food", "Ranged weapon"], event="goblin_warhost"),
    "goblin_warren": _expanded_mission("Goblin Warren Purge", "A tunnel network beneath the hills is feeding fighters and weapons into the invasion.", "C", "combat", 15, 3, [1800, 3600], {"materials": {"food": 22, "scrap": 30, "wood": 24}}, {"item": "breaching_charge", "procedural_recruit": [{"profile": "goblin", "weight": 55}, {"profile": "captive_survivor", "weight": 45}]}, ["Major supplies", "Captive or goblin recruit"], critical_any=[{"kind": "trait", "value": "goblin_hunter", "label": "Goblin Hunter"}, {"kind": "stat", "stat": "combat", "op": ">=", "value": 9, "label": "Combat 9+"}], event="goblin_warhost"),
    "goblin_chieftain": _expanded_mission("Chieftain's Redoubt", "A goblin chieftain commands the road network from a layered timber redoubt.", "B", "combat", 17, 3, [3600, 7200], {"materials": {"food": 30, "scrap": 50, "wood": 45}}, {"item": "knight_blade"}, ["Rare weapon", "Warhost stores"], critical_any=[{"kind": "trait", "value": "goblin_hunter", "label": "Goblin Hunter"}, {"kind": "attribute", "attribute": "str", "op": ">=", "value": 9, "label": "STR 9+"}], event="goblin_warhost"),
    "goblin_kings_fortress": _expanded_mission("Fortress of the Goblin King", "The warhost's ruler has gathered veteran goblins, captives, and stolen relics behind a blackwood wall.", "A", "combat", 20, 4, [7200, 14400], {"materials": {"food": 45, "scrap": 85, "wood": 70, "medicine": 18}}, {"champion_pool": [{"champion": "goblin_slayer", "weight": 70}, {"champion": "sword_maiden", "weight": 30}], "item": "knight_blade"}, ["Event Champion chance", "Exceptional war spoils"], critical_any=[{"kind": "trait", "value": "goblin_hunter", "label": "Goblin Hunter"}, {"kind": "stat", "stat": "combat", "op": ">=", "value": 10, "label": "Combat 10"}], event="goblin_warhost"),

    "restless_graves": _expanded_mission("Restless Graves", "Freshly opened graves mark the path of the Ashen Procession.", "E", "magic", 10, 1, [60, 300], {"materials": {"medicine": 4, "cloth": 6}}, {"item": "ember_charm"}, ["Medicine", "Magic gear"], event="ashen_procession"),
    "bone_patrol": _expanded_mission("Bone Patrol", "Armored dead march the same road each night and carry relics from a ruined chapel.", "D", "combat", 13, 2, [300, 1800], {"materials": {"scrap": 20, "cloth": 12}}, {"item": "scrap_hatchet"}, ["Relics", "Weapon"], event="ashen_procession"),
    "sealed_crypt": _expanded_mission("The Sealed Crypt", "A broken seal beneath the cemetery is pouring dead things into the surrounding fields.", "C", "magic", 15, 3, [1800, 3600], {"materials": {"medicine": 16, "scrap": 28, "cloth": 20}}, {"item": "ember_staff"}, ["Arcane gear", "Relics"], critical_any=[{"kind": "trait", "value": "undead_hunter", "label": "Undead Hunter"}, {"kind": "stat", "stat": "magic", "op": ">=", "value": 9, "label": "Magic 9+"}], event="ashen_procession"),
    "ashen_necropolis": _expanded_mission("Ashen Necropolis", "The Procession ends at a buried city whose dead ruler is calling every grave in the region.", "A", "magic", 20, 4, [7200, 14400], {"materials": {"medicine": 28, "scrap": 70, "cloth": 45}}, {"champion_pool": [{"champion": "seraphine_vale", "weight": 100}], "item": "ember_staff"}, ["Event Champion chance", "Ancient relics"], critical_any=[{"kind": "trait", "value": "undead_hunter", "label": "Undead Hunter"}, {"kind": "attribute", "attribute": "int", "op": ">=", "value": 10, "label": "INT 10"}], event="ashen_procession"),

    "mana_squall": _expanded_mission("Mana Squall", "A roaming storm is crystallizing magic across exposed ruins.", "C", "magic", 15, 2, [1800, 3600], {"materials": {"scrap": 25, "medicine": 12}}, {"item": "ember_charm"}, ["Magic materials", "Focus gear"], event="arcane_convergence"),
    "mirror_labyrinth": _expanded_mission("Mirror Labyrinth", "A temporary maze of reflected corridors contains objects copied from distant places.", "B", "magic", 18, 3, [3600, 7200], {"materials": {"scrap": 48, "cloth": 30, "medicine": 16}}, {"item": "ember_staff"}, ["Rare magic gear", "Copied treasures"], critical_any=[{"kind": "item_tag", "value": "magic_focus", "label": "Magic Focus"}, {"kind": "attribute", "attribute": "luk", "op": ">=", "value": 9, "label": "LUK 9+"}], event="arcane_convergence"),
    "heart_of_leyline": _expanded_mission("Heart of the Leyline", "The convergence has exposed a living knot of magic beneath a floating ruin.", "S", "magic", 23, 5, [14400, 86400], {"materials": {"scrap": 120, "medicine": 50, "cloth": 70}}, {"item": "ember_staff"}, ["Mythic magical haul", "Rare gear"], critical_any=[{"kind": "stat", "stat": "magic", "op": ">=", "value": 10, "label": "Magic 10"}, {"kind": "series", "value": "Fate/stay night", "label": "Fate-series resonance"}], event="arcane_convergence"),

    "stampede_route": _expanded_mission("Stampede Route", "A pack of displaced monsters is about to cross a settled road.", "D", "survival", 13, 2, [300, 1800], {"materials": {"food": 20, "wood": 18}}, {"item": "short_bow"}, ["Food", "Hunter gear"], event="great_beast_tide"),
    "hunt_the_alpha": _expanded_mission("Hunt the Alpha", "One enormous predator is driving the Beast Tide toward inhabited ground.", "B", "combat", 18, 3, [3600, 7200], {"materials": {"food": 45, "medicine": 12, "scrap": 35}}, {"item": "knight_blade"}, ["Rare weapon", "Monster materials"], critical_any=[{"kind": "trait", "value": "tracker", "label": "Tracker"}, {"kind": "attribute", "attribute": "dex", "op": ">=", "value": 9, "label": "DEX 9+"}], event="great_beast_tide"),
    "titan_migration": _expanded_mission("Titan Migration", "A mountain-sized beast is crossing the region with an ecosystem moving in its wake.", "A", "survival", 20, 4, [7200, 14400], {"materials": {"food": 70, "wood": 80, "medicine": 25}}, {"item": "field_pack", "procedural_recruit": [{"profile": "wilds_explorer", "weight": 100}]}, ["Exceptional natural resources", "Elite explorer"], critical_any=[{"kind": "trait", "value": "pathfinder", "label": "Pathfinder"}, {"kind": "stat", "stat": "survival", "op": ">=", "value": 10, "label": "Survival 10"}], event="great_beast_tide"),

    "starfall_crater": _expanded_mission("Starfall Crater", "The fresh crater is surrounded by warped metal, glassed earth, and rival scavengers.", "A", "scavenging", 20, 4, [7200, 14400], {"materials": {"scrap": 100, "medicine": 20, "cloth": 30}}, {"item": "ember_staff"}, ["Star metal", "Rare magic weapon"], critical_any=[{"kind": "attribute", "attribute": "luk", "op": ">=", "value": 10, "label": "LUK 10"}, {"kind": "stat", "stat": "scavenging", "op": ">=", "value": 10, "label": "Scavenging 10"}], event="starfall_omen"),
    "tomb_beyond_sky": _expanded_mission("Tomb Beyond the Sky", "A doorway inside the fallen star opens onto a tomb untouched by the world's history.", "S", "magic", 24, 5, [14400, 86400], {"materials": {"scrap": 180, "medicine": 55, "cloth": 80, "wood": 100}}, {"item": "knight_blade"}, ["Mythic relics", "Massive resource haul"], critical_any=[{"kind": "stat", "stat": "magic", "op": ">=", "value": 10, "label": "Magic 10"}, {"kind": "attribute", "attribute": "int", "op": ">=", "value": 10, "label": "INT 10"}], event="starfall_omen"),
})

# Make the existing procedural recruit rewards context-sensitive too.
MISSION_TEMPLATES["raider_checkpoint"]["critical_rewards"] = {
    "item": "breaching_charge",
    "procedural_recruit": [
        {"profile": "raider_defector", "weight": 60},
        {"profile": "captive_survivor", "weight": 40},
    ],
}
MISSION_TEMPLATES["industrial_yard"]["critical_rewards"] = {"item": "hard_hat", "procedural_recruit": [{"profile": "industrial_worker", "weight": 100}]}
MISSION_TEMPLATES["field_clinic"]["critical_rewards"] = {"item": "medic_coat", "procedural_recruit": [{"profile": "clinic_survivor", "weight": 100}]}
MISSION_TEMPLATES["ash_tunnel"]["critical_rewards"] = {"item": "short_bow", "procedural_recruit": [{"profile": "tunnel_scout", "weight": 100}]}
MISSION_TEMPLATES["deep_expedition"]["critical_rewards"] = {"procedural_recruit": [{"profile": "wilds_explorer", "weight": 100}], "item": "field_pack"}

# Perks and facilities enter through ordinary play, while upper-tier training items
# remain attached to difficult or highly specific critical paths.
MISSION_TEMPLATES["herb_meadow"]["rewards"]["blueprint"] = "alchemy_lab"
MISSION_TEMPLATES["herb_meadow"]["stat"] = "alchemy"
MISSION_TEMPLATES["herb_meadow"]["visible_hints"] = ["Alchemy proficiency identifies safe and potent ingredients.", "A careful harvest can begin an Alchemist's training."]
MISSION_TEMPLATES["herb_meadow"]["critical_rewards"]["perk"] = {"track": "alchemy", "level": "basic"}
MISSION_TEMPLATES["arcane_observatory"]["rewards"]["blueprint"] = "arcane_sanctum"
MISSION_TEMPLATES["highway_ambush"]["critical_rewards"] = {"item": "training_manual", "perk": {"track": "combat", "level": "basic"}}
MISSION_TEMPLATES["field_clinic"]["critical_rewards"]["perk"] = {"track": "medicine", "level": "skilled"}
MISSION_TEMPLATES["herb_meadow"]["critical_rewards"]["procedural_recruit"] = [
    {"profile": "wood_elf", "weight": 70}, {"profile": "faun", "weight": 25},
    {"profile": "dryad", "weight": 5},
]
MISSION_TEMPLATES["flooded_underpass"]["critical_rewards"]["procedural_recruit"] = [
    {"profile": "captive_survivor", "weight": 55}, {"profile": "lizardfolk", "weight": 35},
    {"profile": "merfolk", "weight": 10},
]
MISSION_TEMPLATES["arcane_observatory"]["critical_rewards"]["procedural_recruit"] = [
    {"profile": "high_elf", "weight": 57}, {"profile": "slimefolk", "weight": 35},
    {"profile": "automaton", "weight": 8},
]
MISSION_TEMPLATES["iron_ogre_bridge"]["critical_rewards"]["procedural_recruit"] = [
    {"profile": "ogre", "weight": 95}, {"profile": "troll", "weight": 5},
]
MISSION_TEMPLATES["dragon_roost"]["critical_rewards"] = {
    "items": ["knight_blade", "specialist_tome"], "perk": {"track": "combat", "level": "expert"},
    "procedural_recruit": [
        {"profile": "dwarf", "weight": 75}, {"profile": "ogre", "weight": 23},
        {"profile": "dragonkin", "weight": 2},
    ],
}
MISSION_TEMPLATES["fallen_star_citadel"]["critical_rewards"] = {"items": ["mastery_codex"], "perk": {"track": "magic", "level": "master"}}
MISSION_TEMPLATES["hunt_the_alpha"]["critical_rewards"]["standalone_perk"] = "moon_sense"
MISSION_TEMPLATES["goblin_chieftain"]["critical_rewards"]["procedural_recruit"] = [{"profile": "goblin_boss", "weight": 100}]

MISSION_TEMPLATES["blood_moon_den"] = _expanded_mission(
    "The Blood-Moon Den",
    "A hunter's map marks a den that exists only when the Beast Tide passes beneath a red moon. Its curse can be survived, mastered, or carried home.",
    "A", "survival", 21, 4, [7200, 14400],
    {"materials": {"food": 65, "medicine": 30, "cloth": 30}},
    {"transform": {"race": "Werewolf", "standalone_perks": ["lycanthrope", "moon_sense"]}, "items": ["specialist_tome"]},
    ["Rare transformation path", "Specialist training item", "Beast materials"],
    critical_any=[{
        "kind": "all", "label": "Human Master Survivalist with hunter gear, LUK 9+, and Moon Sense",
        "conditions": [
            {"kind": "race", "value": "Human"}, {"kind": "perk", "track": "survival", "level": "master"},
            {"kind": "item_tag", "value": "scavenging_gear"}, {"kind": "attribute", "attribute": "luk", "op": ">=", "value": 9},
            {"kind": "trait", "value": "moon_sense"},
        ],
    }], event="great_beast_tide",
)
MISSION_TEMPLATES["blood_moon_den"]["pool_weight"] = 2

# A broad event catalog keeps a flavored board from repeating the same authored
# contract across the larger rank floors. These remain event-exclusive.
_EVENT_CONTRACTS = {
    "goblin_warhost": [
        ("goblin_smoke_signals", "Smoke over the Hedgerows", "Goblin scouts are marking undefended farms with greasy smoke signals.", "E", "survival"),
        ("goblin_bridge_trappers", "Bridge-Trapper Gang", "A trap crew is wiring the river bridge before the warhost advances.", "D", "building"),
        ("goblin_boar_riders", "Boar-Rider Patrol", "Fast goblin cavalry is running messages and stolen weapons between camps.", "D", "combat"),
        ("goblin_captive_cart", "The Captive Cart", "Prisoners are being moved behind a shielded supply wagon.", "D", "combat"),
        ("goblin_powder_mill", "Blackpowder Mill", "A hidden mill is producing crude explosives for the siege lines.", "C", "building"),
        ("goblin_tunnel_map", "Map the Under-Roads", "Fresh tunnels now connect warrens beneath every major road.", "C", "scavenging"),
        ("goblin_shaman_circle", "Circle of Crooked Staves", "War shamans are binding stolen magic into the invasion standard.", "B", "magic"),
        ("hobgoblin_vanguard", "The Ironcap Vanguard", "Disciplined hobgoblins are drilling the scattered raiders into an army.", "B", "combat"),
        ("goblin_siege_line", "Break the Siege Line", "Towers and rams are assembling outside a walled refuge.", "A", "combat"),
        ("goblin_emerald_throne", "The Emerald Throne", "An ancient goblin crown is turning a warlord into something far more dangerous.", "S", "magic"),
    ],
    "ashen_procession": [
        ("undead_whispering_well", "The Whispering Well", "Names spoken into the village well return in the voices of the dead.", "E", "magic"),
        ("undead_bone_collectors", "Bone Collectors", "Grave robbers that no longer breathe are gathering remains for the Procession.", "D", "combat"),
        ("undead_corpse_lanterns", "Corpse-Lantern Road", "Pale lanterns lure travelers onto a road that vanished decades ago.", "D", "survival"),
        ("undead_chapel_bell", "The Thirteenth Bell", "A ruined chapel rings after midnight and another corpse rises with every note.", "D", "magic"),
        ("undead_plague_ossuary", "Plague Ossuary", "A sealed bone house contains medicine records and a waking congregation.", "C", "medicine"),
        ("undead_drowned_choir", "The Drowned Choir", "Sunken singers are calling the river's dead back to shore.", "C", "magic"),
        ("undead_black_hearse", "The Black Hearse", "An armored hearse carries a relic that commands lesser dead.", "B", "combat"),
        ("undead_death_knight", "Knight without a Grave", "A fallen champion challenges every armed traveler on the old king's road.", "B", "combat"),
        ("undead_hollow_cathedral", "Hollow Cathedral", "The Procession is gathering beneath a cathedral built over a mass grave.", "A", "magic"),
        ("undead_last_funeral", "The Last Funeral", "An undying monarch intends to bury the entire region in one final rite.", "S", "magic"),
    ],
    "arcane_convergence": [
        ("arcane_crystal_rain", "Crystal Rain", "A glittering storm leaves useful shards and dangerous reflections behind.", "E", "scavenging"),
        ("arcane_runaway_golem", "Runaway Clay Golem", "A labor construct is rebuilding the same road directly through occupied homes.", "D", "building"),
        ("arcane_spellglass_field", "Spellglass Field", "A meadow has hardened into glass that repeats the last spell cast nearby.", "D", "magic"),
        ("arcane_bottled_storm", "The Bottled Storm", "An abandoned wagon carries a storm trapped in cracked alchemical vessels.", "D", "alchemy"),
        ("arcane_time_lost_caravan", "Yesterday's Caravan", "A caravan missing for years appears every dusk for eleven minutes.", "C", "survival"),
        ("arcane_living_library", "The Living Library", "Loose pages hunt readers through a library that rearranges itself.", "C", "magic"),
        ("arcane_gravity_well", "Gravity Well", "A mining camp and its ore now orbit a blue point above the quarry.", "B", "building"),
        ("arcane_dream_market", "Market of Borrowed Dreams", "A temporary bazaar trades memories for impossible equipment.", "B", "alchemy"),
        ("arcane_prism_tower", "The Prism Tower", "Seven overlapping versions of one tower are becoming real at once.", "A", "magic"),
        ("arcane_zero_hour", "Zero Hour", "The convergence has stopped time around a city while something inside continues moving.", "S", "magic"),
    ],
    "great_beast_tide": [
        ("beast_giant_spoor", "Tracks Larger than Wagons", "Fresh tracks reveal a migrating beast before the settlements see it.", "E", "survival"),
        ("beast_razorboar_nest", "Razorboar Nest", "Displaced razorboars have rooted beneath a grain store.", "D", "combat"),
        ("beast_webbed_caravan", "The Webbed Caravan", "A merchant train hangs intact above the road in enormous silver webs.", "D", "survival"),
        ("beast_horned_stampede", "Turn the Horned Stampede", "A frightened herd is hours away from flattening two villages.", "D", "survival"),
        ("beast_razorwing_cliffs", "Razorwing Cliffs", "Aerial predators have nested around a valuable cliffside ruin.", "C", "combat"),
        ("beast_breeding_hollow", "Breeding Hollow", "The Tide's young are gathering in a warm cavern full of discarded prey.", "C", "medicine"),
        ("beast_white_fang", "Hunt of the White Fang", "A cunning predator is stalking hunters sent after lesser beasts.", "B", "combat"),
        ("beast_thunderherd", "Beneath the Thunderherd", "Valuable minerals shake loose beneath a migration of armored giants.", "B", "scavenging"),
        ("beast_leviathan_crossing", "Leviathan Crossing", "A river leviathan is dragging an entire flooded ecosystem upstream.", "A", "survival"),
        ("beast_world_eater_wake", "Wake of the World-Eater", "The Tide parts around a creature that consumes terrain rather than prey.", "S", "combat"),
    ],
    "starfall_omen": [
        ("starfall_fallen_sparks", "Gather the Fallen Sparks", "Living sparks scatter from the crater and hide in metal objects.", "E", "scavenging"),
        ("starfall_metal_thieves", "Star-Metal Thieves", "A scavenger gang has weapons forged from still-burning fragments.", "D", "combat"),
        ("starfall_silent_farm", "The Silent Farm", "Everything near one fragment has lost its sound, including the people.", "D", "medicine"),
        ("starfall_compass_storm", "Compass Storm", "Navigation fails around a moving cluster of magnetic splinters.", "D", "survival"),
        ("starfall_glasswood", "The Glasswood", "A forest crystallized by impact light contains trapped supplies and creatures.", "C", "scavenging"),
        ("starfall_hollow_signal", "Signal from the Hollow Stone", "A fragment transmits a voice that knows the listeners by name.", "C", "magic"),
        ("starfall_void_pilgrims", "Voidsent Pilgrims", "Masked outsiders follow a rift leaking aether from a ruined world and carry instruments built to feed on its magic.", "B", "combat"),
        ("starfall_gravity_scar", "The Gravity Scar", "Ruins are falling sideways into a luminous wound across the hills.", "B", "building"),
        ("starfall_black_observatory", "Black Observatory", "A structure unfolded from the meteor and has begun charting the camp.", "A", "magic"),
        ("starfall_second_sun", "The Second Sun", "A fragment beneath the crater is brightening toward an extinction-level release.", "S", "magic"),
    ],
}
_EVENT_MATERIALS = {
    "E": {"food": 9, "wood": 10}, "D": {"food": 14, "scrap": 16},
    "C": {"wood": 24, "scrap": 28, "medicine": 7}, "B": {"food": 28, "scrap": 45, "cloth": 18},
    "A": {"wood": 60, "scrap": 75, "medicine": 20}, "S": {"wood": 100, "scrap": 140, "medicine": 40, "cloth": 55},
}
_EVENT_CRITICAL_ITEMS = {"E": "training_manual", "D": "training_manual", "C": "field_pack", "B": "specialist_tome", "A": "specialist_tome", "S": "mastery_codex"}


def _event_materials(event_id: str, stat: str, rank: str) -> dict[str, int]:
    """Build a reward bundle from what the party actually does at the site."""
    totals = {"E": 19, "D": 30, "C": 59, "B": 91, "A": 155, "S": 335}
    profiles = {
        "combat": (("scrap", 0.48), ("food", 0.32), ("medicine", 0.20)),
        "building": (("scrap", 0.52), ("wood", 0.38), ("cloth", 0.10)),
        "magic": (("cloth", 0.42), ("medicine", 0.34), ("scrap", 0.24)),
        "alchemy": (("medicine", 0.50), ("cloth", 0.35), ("scrap", 0.15)),
        "survival": (("food", 0.48), ("wood", 0.34), ("medicine", 0.18)),
        "scavenging": (("scrap", 0.50), ("wood", 0.30), ("cloth", 0.20)),
    }
    profile = list(profiles.get(stat, profiles["scavenging"]))
    # Event identity nudges the haul without creating arbitrary resource types.
    event_resource = {
        "goblin_warhost": "scrap", "ashen_procession": "cloth",
        "arcane_convergence": "medicine", "great_beast_tide": "food",
        "starfall_omen": "scrap",
    }.get(event_id)
    if event_resource:
        for index, (resource, share) in enumerate(profile):
            if resource == event_resource:
                profile[index] = (resource, share + 0.08)
            else:
                profile[index] = (resource, share - 0.04)
    total = totals[rank]
    result = {resource: max(1, round(total * share)) for resource, share in profile}
    difference = total - sum(result.values())
    first_resource = profile[0][0]
    result[first_resource] += difference
    return result


for _event_id, _contracts in _EVENT_CONTRACTS.items():
    for _contract_id, _name, _description, _rank, _stat in _contracts:
        MISSION_TEMPLATES[_contract_id] = _expanded_mission(
            _name, _description, _rank, _stat, {"E": 10, "D": 13, "C": 15, "B": 18, "A": 21, "S": 24}[_rank],
            {"E": 1, "D": 2, "C": 3, "B": 3, "A": 4, "S": 5}[_rank],
            {"E": [60, 300], "D": [300, 1800], "C": [1800, 3600], "B": [3600, 7200], "A": [7200, 14400], "S": [14400, 86400]}[_rank],
            {"materials": _event_materials(_event_id, _stat, _rank)}, {"item": _EVENT_CRITICAL_ITEMS[_rank]},
            [f"{_event_id.replace('_', ' ').title()} supplies", "Training or specialist loot"], event=_event_id,
        )

MISSION_TEMPLATES["goblin_captive_cart"].update({
    "combat_encounter": {
        "id": "goblin_captive_cart", "name": "Extraction Battle",
        "description": "Extract the wounded courier alive. Capturing the cartmaster and recovering the stolen dispatches are optional objectives.",
    },
    "critical_rewards": {"item": "ironcap_buckler"},
    "reward_preview": ["Rescue commission and recovered supplies", "Chance for a Cartmaster's Route Book from a live capture", "Ironcap Buckler for complete recovery"],
    "narrative": {
        "approach": "The captive cart appeared between hedgerows exactly when the informant promised. {party} waited until the lead guards passed, then closed the road behind the cartmaster before the wagon could reach the warhost line.",
        "critical_failure": "The rescue became a catastrophe. The courier never crossed the guild line, and the survivors returned with the sound of the cart wheels fading east behind them.",
        "failure": "The party escaped the ambush site, but the captive cart broke through with its prisoner still aboard. The guild learned where the route led and paid for that knowledge dearly.",
        "success": "The courier reached the ambush line alive. The guild abandoned the road before the larger warhost could respond, carrying home the person the contract had actually asked them to save.",
        "critical_success": "The rescue became a precise dismantling of the entire escort. The courier survived, the cartmaster arrived in Fortcamp alive for questioning, and the stolen dispatches exposed the next warhost route.",
    },
})

# Consequence contracts never enter a normal roll. They are rumors, reprisals, and
# opportunities caused by earlier expeditions, and can surface on a later board.
MISSION_TEMPLATES.update({
    "black_banner_ledger": _expanded_mission("The Black-Banner Ledger", "A captured raider ledger names the villages paying protection and the courier collecting the next tithe.", "C", "scavenging", 15, 3, [1800, 3600], {"materials": {"food": 20, "scrap": 25, "cloth": 16}}, {"item": "breaching_charge"}, ["Raider intelligence", "Recovered tribute", "Story consequence"]),
    "black_banner_convoy": _expanded_mission("The Tithe Convoy", "The Black Banner is moving its collected tribute under heavy guard before the guild can use the stolen ledger against it.", "B", "combat", 18, 3, [3600, 7200], {"materials": {"food": 35, "wood": 35, "scrap": 45, "medicine": 12}}, {"items": ["knight_blade", "training_manual"]}, ["Major recovered tribute", "Story consequence"]),
    "black_banner_court": _expanded_mission("Court of the Empty Crown", "The raider captains have gathered in the roofless royal court to choose a warlord and answer the guild's attacks.", "A", "combat", 21, 4, [7200, 14400], {"materials": {"food": 50, "wood": 60, "scrap": 85, "medicine": 20}}, {"items": ["tower_shield", "mastery_codex"]}, ["Black Banner treasury", "Story climax"]),
    "bell_beneath_mud": _expanded_mission("The Bell Beneath the Mud", "The flooded road has exposed a chapel bell whose toll is drawing the unburied toward the river.", "C", "magic", 15, 3, [1800, 3600], {"materials": {"cloth": 20, "medicine": 16, "scrap": 22}}, {"item": "corpse_lantern"}, ["Ashen relic", "Story consequence"]),
    "processions_empty_hearse": _expanded_mission("The Procession's Empty Hearse", "After the bell fell silent, an empty black hearse began following the road toward Fortcamp and stopping at every grave.", "A", "magic", 21, 4, [7200, 14400], {"materials": {"cloth": 40, "medicine": 28, "scrap": 65}}, {"items": ["mourning_blade", "specialist_tome"]}, ["Procession relics", "Story climax"]),
    "brass_foreman": _expanded_mission("The Brass Foreman Wakes", "Machines salvaged from the old works have begun answering a command signal from a sealed office beneath the foundry.", "C", "building", 16, 3, [1800, 3600], {"materials": {"scrap": 38, "wood": 25}}, {"item": "hard_hat"}, ["Meridian machinery", "Story consequence"]),
    "meridian_engine": _expanded_mission("The Meridian Engine", "Every arcane machine in the valley is drawing power toward an engine buried below the observatory and counting down in a forgotten language.", "A", "magic", 22, 4, [7200, 14400], {"materials": {"scrap": 80, "medicine": 30, "cloth": 35}}, {"items": ["archmage_grimoire", "mastery_codex"]}, ["Ancient arcane engine", "Story climax"]),
    "wounded_colossus": _expanded_mission("The Wounded Colossus", "A titan driven from the migration route has collapsed near the farms, wounded by weapons made from star-metal.", "B", "medicine", 18, 3, [3600, 7200], {"materials": {"food": 30, "medicine": 30, "wood": 28}}, {"item": "titanbone_maul"}, ["Titan encounter", "Story consequence"]),
    "shepherd_of_titans": _expanded_mission("The Shepherd of Titans", "The creature that wounded the colossus is steering the entire migration toward the old capital for an unknown purpose.", "A", "survival", 21, 4, [7200, 14400], {"materials": {"food": 48, "medicine": 25, "scrap": 55}}, {"items": ["apex_claw", "specialist_tome"]}, ["Migration secret", "Story climax"]),
    "signal_knows_name": _expanded_mission("The Signal Knows Your Name", "A hollow star-stone repeats the names of the last expedition and gives directions to a place missing from every map.", "B", "magic", 18, 3, [3600, 7200], {"materials": {"scrap": 45, "cloth": 28, "medicine": 15}}, {"item": "voidglass_mantle"}, ["Extraterrestrial signal", "Story consequence"]),
    "door_between_dead_stars": _expanded_mission("The Door Between Dead Stars", "The signal has opened a door into a magic-starved world where Voidsent nobles are fighting over the route back to Fortcamp.", "S", "magic", 24, 5, [14400, 86400], {"materials": {"scrap": 130, "cloth": 70, "medicine": 45}}, {"items": ["starfall_core", "mastery_codex"]}, ["Voidsent relics", "Story climax"]),
})
for _mission_id in (
    "black_banner_ledger", "black_banner_convoy", "black_banner_court", "bell_beneath_mud",
    "processions_empty_hearse", "brass_foreman", "meridian_engine", "wounded_colossus",
    "shepherd_of_titans", "signal_knows_name", "door_between_dead_stars",
):
    MISSION_TEMPLATES[_mission_id]["trigger_only"] = True

# A successful expedition can create a persistent consequence for the next board.
# Critical Success improves the roll. Triggered contracts can themselves continue
# the thread, producing a small public story arc rather than an isolated encounter.
_BOARD_FOLLOWUPS = {
    "raider_checkpoint": ("black_banner_ledger", 25), "highway_ambush": ("black_banner_ledger", 28),
    "bandit_outpost": ("black_banner_ledger", 35), "goblin_warcamp": ("black_banner_ledger", 18),
    "black_banner_ledger": ("black_banner_convoy", 60), "black_banner_convoy": ("black_banner_court", 75),
    "flooded_underpass": ("bell_beneath_mud", 20), "restless_graves": ("bell_beneath_mud", 25),
    "undead_drowned_choir": ("bell_beneath_mud", 38), "bell_beneath_mud": ("processions_empty_hearse", 65),
    "collapsed_workshop": ("brass_foreman", 22), "industrial_yard": ("brass_foreman", 20),
    "haunted_foundry": ("brass_foreman", 38), "arcane_observatory": ("meridian_engine", 28),
    "brass_foreman": ("meridian_engine", 65),
    "stampede_route": ("wounded_colossus", 24), "hunt_the_alpha": ("wounded_colossus", 30),
    "titan_migration": ("wounded_colossus", 42), "wounded_colossus": ("shepherd_of_titans", 70),
    "starfall_hollow_signal": ("signal_knows_name", 35), "starfall_black_observatory": ("signal_knows_name", 45),
    "tomb_beyond_sky": ("signal_knows_name", 35), "signal_knows_name": ("door_between_dead_stars", 70),
}
for _source_id, (_followup_id, _chance) in _BOARD_FOLLOWUPS.items():
    MISSION_TEMPLATES[_source_id].setdefault("board_followups", []).append({
        "template_id": _followup_id, "chance": _chance, "critical_bonus": 20,
    })

_CONSEQUENCE_REWARDS = {
    "black_banner_ledger": {"guaranteed_items": ["black_banner_cipher"]},
    "black_banner_convoy": {"standalone_perk": "bannerbreaker"},
    "black_banner_court": {"guaranteed_items": ["empty_crown_standard"], "world_flag": {"id": "broke_black_banner_court", "name": "Broke the Black Banner Court"}},
    "bell_beneath_mud": {"guaranteed_items": ["mudbound_clapper"]},
    "processions_empty_hearse": {"guaranteed_items": ["bell_of_last_rites"], "standalone_perk": "keeper_of_last_rites", "world_flag": {"id": "laid_hearse_to_rest", "name": "Laid the Empty Hearse to Rest"}},
    "brass_foreman": {"guaranteed_items": ["brass_foreman_key"]},
    "meridian_engine": {"guaranteed_items": ["meridian_heart"], "standalone_perk": "meridian_attunement", "world_flag": {"id": "mastered_meridian_engine", "name": "Mastered the Meridian Engine"}},
    "wounded_colossus": {"guaranteed_items": ["colossus_heartblood"]},
    "shepherd_of_titans": {"guaranteed_items": ["titan_shepherds_horn"], "standalone_perk": "titan_speaker", "world_flag": {"id": "restored_titan_roads", "name": "Restored the Titan Roads"}},
    "signal_knows_name": {"guaranteed_items": ["echoing_starstone"]},
    "door_between_dead_stars": {"guaranteed_items": ["starless_gate_sigil"], "standalone_perk": "riftwalker", "world_flag": {"id": "sealed_starless_treaty", "name": "Sealed the Starless Treaty"}},
}
for _mission_id, _special_rewards in _CONSEQUENCE_REWARDS.items():
    MISSION_TEMPLATES[_mission_id]["rewards"].update(_special_rewards)
    _preview = MISSION_TEMPLATES[_mission_id].setdefault("reward_preview", [])
    if _special_rewards.get("guaranteed_items"):
        _preview.append("Guaranteed story relic")
    if _special_rewards.get("standalone_perk"):
        _preview.append("Exclusive story perk")
    if _special_rewards.get("world_flag"):
        _preview.append("Permanent world outcome")

# A flawless crossing of the final Starless Gate can also persuade a Voidsent
# exile to join. The planar relic and treaty remain guaranteed on normal success.
MISSION_TEMPLATES["door_between_dead_stars"]["critical_rewards"]["procedural_recruit"] = [
    {"profile": "voidsent", "weight": 100},
]

# Ordinary expeditions draw survivors from the people who plausibly live near
# that mission. Hidden event definitions are attached without entering mission
# summaries, visible hints, or reward previews.
for _mission_id, _region in MISSION_RECRUIT_REGIONS.items():
    if _mission_id in MISSION_TEMPLATES:
        MISSION_TEMPLATES[_mission_id]["recruit_region"] = _region
for _mission_id, _secret_events in SECRET_RECRUIT_EVENTS.items():
    if _mission_id in MISSION_TEMPLATES:
        MISSION_TEMPLATES[_mission_id]["secret_events"] = _secret_events

_EVENT_ADVANTAGE_PERKS = {
    "goblin_warhost": ["warhost_veteran", "warhost_command", "hobgoblin_discipline", "kobold_trapsmith", "orcish_might", "bugbear_ambush"],
    "ashen_procession": ["graveward", "soul_anchor", "deathless", "blood_sense", "wailing_magic"],
    "arcane_convergence": ["ley_touched", "stormbound", "gravity_walker", "mana_body", "constructed", "dream_sense", "elven_senses"],
    "great_beast_tide": ["beast_bond", "apex_instinct", "titan_strength", "scaled_hide", "winged", "horned_guard", "feral_agility"],
    "starfall_omen": ["star_touched", "stellar_aegis", "void_sight", "astral_sense", "void_adapted", "aether_hunger", "alien_physiology", "gravity_walker"],
}
for _mission in MISSION_TEMPLATES.values():
    _advantages = _EVENT_ADVANTAGE_PERKS.get(_mission.get("event"))
    if _advantages:
        _mission.setdefault("modifiers", []).append({
            "kind": "any", "conditions": [{"kind": "trait", "value": perk} for perk in _advantages],
            "bonus": 3, "label": "Event race or relic affinity",
        })

# Only contracts with a credible patron, bounty, rescue commission, or settlement
# defense payment award gold. Ruin delves and pure salvage runs pay in recovered goods.
PAID_CONTRACT_IDS = {
    "missing_trapper", "highway_ambush", "quarantine_house", "bandit_outpost", "iron_ogre_bridge",
    "dragon_roost", "goblin_warcamp", "goblin_smoke_signals", "goblin_boar_riders", "goblin_captive_cart",
    "goblin_siege_line", "undead_bone_collectors", "undead_chapel_bell", "undead_plague_ossuary",
    "undead_black_hearse", "undead_death_knight", "undead_hollow_cathedral", "undead_last_funeral",
    "arcane_runaway_golem", "arcane_time_lost_caravan", "arcane_living_library", "arcane_zero_hour",
    "stampede_route", "hunt_the_alpha", "beast_horned_stampede", "beast_white_fang",
    "beast_leviathan_crossing", "beast_world_eater_wake", "starfall_metal_thieves",
    "starfall_silent_farm", "starfall_compass_storm", "starfall_void_pilgrims",
    "starfall_black_observatory", "starfall_second_sun",
    "black_banner_ledger", "black_banner_convoy", "black_banner_court", "bell_beneath_mud",
    "processions_empty_hearse", "wounded_colossus", "shepherd_of_titans",
}
for _mission_id, _mission in MISSION_TEMPLATES.items():
    _mission["id"] = _mission_id
    _preview = _mission.setdefault("reward_preview", [])
    if "Bonus loot rolls" not in _preview:
        _preview.append("Bonus loot rolls")
    if _mission.get("event") and "Event relics" not in _preview:
        _preview.append("Event relics")
    if _mission.get("event") and "Rare event recruit" not in _preview:
        _preview.append("Rare event recruit")
    if MISSION_RANKS.index(_mission.get("rank", "E")) >= MISSION_RANKS.index("C") and "Rare Champion encounter" not in _preview:
        _preview.append("Rare Champion encounter")
    if _mission_id in PAID_CONTRACT_IDS:
        _mission["pays_gold"] = True
        if "Gold" not in _preview:
            _preview.append("Gold")

# Fort-of-Chains-style mission aftermath. Each result is assembled from a mission-specific
# opening plus the rolled outcome, then optional triggered/special-event paragraphs.
MISSION_NARRATIVES = {
    "roadside_store": {
        "approach": "{party} reached the roadside store under a sky gone flat with dust. The front room had already been picked clean, so {lead} led the search toward the warped stockroom and the collapsed aisle behind it.",
        "critical_failure": "The interior gave way at the worst possible moment. Shelving crashed, loose glass scattered across the floor, and the team was forced out before they could secure anything useful. They returned tired and rattled, with the store still standing behind them like a challenge left unfinished.",
        "failure": "The team worked through the obvious hiding places but the building fought them for every meter. By the time the structure started creaking in earnest, they had to withdraw rather than gamble the whole party on one locked room.",
        "success": "Careful searching paid off. The team opened the safer caches, bundled everything that could still be carried, and marked the remaining hazards before heading home with a worthwhile haul.",
        "critical_success": "The team found the store's forgotten back route and reached the sealed stock before the unstable interior became a problem. What looked like a picked-over ruin turned into one of the cleanest scavenging runs the camp had seen yet.",
    },
    "raider_checkpoint": {
        "approach": "The checkpoint sat across the road in layers of welded sheet metal and old concrete barriers. {party} moved in slowly while {lead} watched for tripwires, firing lanes, and anything the vanished raiders had left armed behind them.",
        "critical_failure": "A hidden mechanism snapped alive before the team could isolate it. The checkpoint became a mess of noise and flying debris, forcing an immediate retreat. Nobody wanted to stay long enough to learn what other surprises had been left behind.",
        "failure": "The party neutralized the most obvious traps but the secured section proved too dangerous to force. They withdrew with little to show for the risk rather than turn a salvage run into a casualty report.",
        "success": "One trap after another was disabled until the roadblock finally belonged to the party. They stripped the useful gear, emptied the accessible caches, and left the dead checkpoint far less dangerous than they found it.",
        "critical_success": "The team read the defenses almost perfectly. They bypassed the nastiest traps, breached the protected cache, and had enough time left to search the perimeter for anyone or anything the raiders had abandoned.",
    },
    "industrial_yard": {
        "approach": "The industrial yard was a maze of buckled fencing, silent machinery, and maintenance sheds leaning under years of weather. {lead} took point while {party} searched for equipment that had survived without becoming a deathtrap.",
        "critical_failure": "A section of machinery shifted under load and turned the salvage attempt into a scramble for open ground. The team escaped the collapsing bay, but the useful material disappeared beneath twisted steel with it.",
        "failure": "Most of the promising machinery had corroded beyond safe recovery. The team spent the mission separating junk from hazards and returned without enough intact material to justify the effort.",
        "success": "The party identified the machines worth dismantling and recovered parts in a controlled sequence. By the end of the run, the camp had both useful salvage and a much better idea of how to build with it.",
        "critical_success": "The yard turned out to be a treasure house for anyone who knew what to look for. Intact tooling, clean stock, and overlooked maintenance supplies came out piece by piece until the team had to stop simply because they could carry no more.",
    },
    "field_clinic": {
        "approach": "The ruined clinic still smelled faintly of antiseptic beneath the dust. {party} entered around a collapsed treatment wing while {lead} sorted useful medical stock from spoiled supplies and unstable debris.",
        "critical_failure": "A hurried search disturbed part of the damaged ceiling. The team had to abandon the treatment rooms and get clear before the rest followed it down, leaving the clinic's best supplies out of reach.",
        "failure": "The obvious cabinets had already been emptied and the remaining stock was too damaged to trust. The team returned with experience instead of medicine, frustrated by how close the useful rooms had seemed.",
        "success": "The search was methodical and careful. Sealed supplies, clean cloth, and usable medical equipment were recovered without contaminating the haul, giving the camp real treatment options for the first time.",
        "critical_success": "The team found a protected emergency store behind the clinic's damaged triage area. The cache had stayed dry and sealed, turning a dangerous medical scavenging run into an exceptional recovery.",
    },
    "ash_tunnel": {
        "approach": "Smoke hung low in the Ash Tunnel, trapped beneath the old ceiling with the smell of wet concrete and burned wiring. {party} advanced between abandoned cars while {lead} searched for a route that would not box them into the heat.",
        "critical_failure": "The tunnel shifted from difficult to dangerous in seconds. Heat rolled through the passage and falling debris cut off the planned route, forcing the party to abandon the cargo and fight their way back through the smoke.",
        "failure": "The party reached the edge of the cargo site but could not make the final approach safely. They marked what they saw and withdrew before fatigue and bad air turned hesitation into disaster.",
        "success": "The team threaded a safe path through the wreckage, reached the stranded cargo, and hauled the most useful crates back through the tunnel before conditions worsened.",
        "critical_success": "The hazards lined up in the party's favor. They controlled the worst of the heat, found an overlooked service path, and recovered both the cargo and evidence of other survivors who had once used the tunnel.",
    },
    "old_armory": {
        "approach": "The old armory had survived because it was built to keep people out. {party} studied the reinforced entrance while {lead} looked for the least dangerous way to defeat a lock designed to resist exactly this kind of visit.",
        "critical_failure": "The breach went wrong and the entrance became more dangerous instead of less. The party broke contact before damaged hardware or unstable ammunition could turn the armory into a tomb.",
        "failure": "The outer defenses yielded, but the team could not open the protected storage area without taking an unacceptable risk. They withdrew with the armory still sealed behind them.",
        "success": "Patience won. The party opened the armory without destroying what was inside and recovered equipment that had been waiting years for someone capable of reaching it.",
        "critical_success": "The team defeated the armory's defenses cleanly and found the interior remarkably intact. They had time to choose the best equipment rather than simply grabbing whatever was closest to the door.",
    },
    "summoning_trace": {
        "approach": "The magical trace led {party} beyond the camp's familiar routes to a place where the air itself seemed slightly out of step. {lead} followed the strongest distortions while the rest of the team kept watch for whatever had caused them.",
        "critical_failure": "The trace collapsed violently when the party tried to interact with it. Light, pressure, and disorientation drove them back, and whatever had been on the other side vanished before they could understand it.",
        "failure": "The team mapped the phenomenon but could not stabilize it. The trace faded piece by piece until only a few recoverable materials remained to prove it had ever been there.",
        "success": "The party held the trace together long enough to recover strange residue and equipment from its center. They returned with more questions than answers, but also with something tangible to study.",
        "critical_success": "The distortion settled instead of breaking. For a few crucial moments the party could see the pattern behind it, and something—or someone—on the far side had time to answer before the trace finally closed.",
    },
    "deep_expedition": {
        "approach": "For the Deep Wilds expedition, {party} left the last mapped trail behind and stayed out long enough for the camp to become a direction rather than a place. {lead} set the pace through country nobody in the settlement had properly surveyed.",
        "critical_failure": "Weather, bad ground, and dwindling supplies compounded faster than the party could solve them. The expedition turned back before the return route disappeared entirely, arriving home exhausted and empty-handed.",
        "failure": "The team pushed far beyond the safe routes but never found a haul worth the distance. They returned with new map notes and little else, having spent most of the expedition simply keeping the road home open.",
        "success": "The long route paid off. The party located untouched stores and useful materials well beyond the usual scavenging radius, then brought the haul home in stages without losing the trail.",
        "critical_success": "The expedition found more than supplies: a viable route, overlooked resources, and signs that the region was less empty than the maps suggested. They returned with a haul large enough to change what the settlement could attempt next.",
    },
    "goblin_warcamp": {
        "approach": "The Goblin Warcamp spread across the service road in patched tents, scrap palisades, and cooking fires. {party} watched patrols from cover while {lead} chose whether to break the camp quickly or peel its defenses apart one section at a time.",
        "critical_failure": "The first clash drew far more of the camp than expected. Horns sounded, fighters spilled from behind the palisade, and the party had to abandon the attack before they were surrounded. The warcamp was left angry, alert, and very much intact.",
        "failure": "The party forced its way into the outer camp but could not control the fight long enough to reach the stores or prisoners. They disengaged before the defenders could close the road behind them.",
        "success": "Once the chieftain was out of the fight, the camp's defense broke. The party chose whether to leave or pursue the goblins who ran.",
        "critical_success": "The party freed the captives and disabled the alarm before bringing down the chieftain. No reinforcements reached the camp.",
    },
}
MISSION_TEMPLATES["goblin_warcamp"]["combat_encounter"] = {
    "id": "goblin_warcamp", "name": "Tactical Battle",
    "description": "Fight through a goblin warcamp, free the captives, and silence the alarm before defeating its chieftain.",
}
MISSION_TEMPLATES["goblin_warcamp"]["reward_preview"].append("Optional tactical battle")

for _mission_id, _narrative in MISSION_NARRATIVES.items():
    if _mission_id in MISSION_TEMPLATES:
        MISSION_TEMPLATES[_mission_id]["narrative"] = _narrative

# The world is organized around consequences of the same fallen kingdom rather
# than a collection of unrelated biomes. These threads give every ordinary and
# event contract a recurring place, faction, history, and clue vocabulary.
WORLD_STORY_THREADS = {
    "broken_crown": {
        "name": "Roads of the Broken Crown",
        "context": "The old Kingdom of Lareth is gone, but its roads still connect Fortcamp to hungry villages, abandoned works, and the Black Banner raiders filling the vacuum.",
        "anchor": "the cracked crown stamped on old Lareth milestones",
        "clue": "another sign that the Black Banner is searching old royal sites rather than raiding at random",
    },
    "ashen_oath": {
        "name": "The Unpaid Ashen Oath",
        "context": "Lareth's last monarch promised the dead a proper burial, then spent their graves and names to defend the capital. The Ashen Procession walks because that debt was never paid.",
        "anchor": "the same funerary knot seen along the Procession's road",
        "clue": "a fragment of the burial roll linking the restless dead to Lareth's final royal court",
    },
    "meridian": {
        "name": "The Broken Meridian",
        "context": "The Meridian Collegium powered Lareth with linked observatories, foundries, and planar engines. Its final experiment bent gravity, weather, and time across the valley.",
        "anchor": "a three-ring Meridian seal cut into the surviving machinery",
        "clue": "a machine record showing that the Collegium's final experiment was interrupted rather than destroyed",
    },
    "titan_roads": {
        "name": "The Titan Roads",
        "context": "Great beasts follow migration paths older than Lareth. War, starfall, and the reawakening Meridian network are forcing those paths toward settled land.",
        "anchor": "an ancient migration mark carved long before the royal road existed",
        "clue": "evidence that something intelligent is turning the migration instead of merely frightening it",
    },
    "starless_gate": {
        "name": "The Starless Gate",
        "context": "Starfall debris comes from worlds touched by the Meridian disaster. Aliens seek a road home while Voidsent follow the leaking aether back toward its source.",
        "anchor": "a star-map whose missing center lies directly beneath old Lareth",
        "clue": "a repeating signal that treats Fortcamp as one point in a much larger broken gateway",
    },
}

_THREAD_MISSIONS = {
    "ashen_oath": {"bell_beneath_mud", "processions_empty_hearse", "quarantine_house"},
    "meridian": {"industrial_yard", "collapsed_workshop", "arcane_observatory", "haunted_foundry", "planar_breach", "summoning_trace", "brass_foreman", "meridian_engine"},
    "titan_roads": {"deep_expedition", "iron_ogre_bridge", "dragon_roost", "wounded_colossus", "shepherd_of_titans"},
    "starless_gate": {"fallen_star_citadel", "signal_knows_name", "door_between_dead_stars"},
}
_EVENT_THREADS = {
    "goblin_warhost": "broken_crown", "ashen_procession": "ashen_oath",
    "arcane_convergence": "meridian", "great_beast_tide": "titan_roads",
    "starfall_omen": "starless_gate",
}


def _mission_thread(mission_id: str, mission: dict) -> str:
    if mission.get("event") in _EVENT_THREADS:
        return _EVENT_THREADS[mission["event"]]
    for thread_id, mission_ids in _THREAD_MISSIONS.items():
        if mission_id in mission_ids:
            return thread_id
    return "broken_crown"


def _thread_narrative(mission: dict, thread: dict) -> dict:
    name, description = mission["name"], mission["description"]
    anchor, clue = thread["anchor"], thread["clue"]
    return {
        "approach": [
            f"{{party}} followed the contract to {name}. {description} Near the approach, {{lead}} recognized {anchor}; this trouble belonged to a story the guild had encountered before.",
            f"Word of {name} reached Fortcamp through traders already familiar with the region's worsening pattern. {{party}} went to investigate while {{lead}} kept watch for {anchor}.",
        ],
        "critical_failure": [
            "The danger moved sooner than the party expected. Their route collapsed, the objective was lost, and the survivors had to choose one another over the contract. Whatever caused the incident now knows the guild intervened.",
            f"The expedition broke apart at the decisive moment. {{lead}} brought the party home, but {clue} remained beyond reach and the situation was left more active than before.",
        ],
        "failure": [
            "The party reached the heart of the problem but could not control it long enough to finish the work. They returned with observations instead of spoils, adding one incomplete piece to the guild's map of the region.",
            f"Progress exposed {clue}, but pressing farther would have trapped the party. {{lead}} ordered a retreat and carried the warning back to Fortcamp.",
        ],
        "success": [
            f"The objective was secured after the party adjusted to what the contract had failed to mention. Among the recovered evidence was {clue}; the mission had solved a local problem and widened the larger one.",
            f"{{party}} completed the work and searched beyond the obvious reward. They found {clue}, giving Fortcamp a clearer picture of why these incidents keep touching the same roads.",
        ],
        "critical_success": [
            f"The operation landed cleanly enough for a second investigation after the main objective. {{lead}} traced {anchor} to {clue}, turning a successful contract into a discovery that may change the next guild board.",
            f"Everything the party learned on earlier expeditions mattered at once. The team secured the objective, protected the route, and returned with {clue} before anyone else could erase it.",
        ],
    }


for _mission_id, _mission in MISSION_TEMPLATES.items():
    if _mission.get("chain_only"):
        continue
    _thread_id = _mission_thread(_mission_id, _mission)
    _thread = WORLD_STORY_THREADS[_thread_id]
    _mission["story_thread"] = _thread_id
    _mission["story_thread_name"] = _thread["name"]
    _mission["world_context"] = _thread["context"]
    if _mission_id in MISSION_NARRATIVES:
        _mission["thread_epilogue"] = [
            f"Before leaving, the party documented {_thread['anchor']}. It may be connected to {_thread['clue']}.",
            f"The guild archivist placed the report under {_thread['name']}: {_thread['clue']}.",
        ]
    else:
        _mission["narrative"] = _thread_narrative(_mission, _thread)

# First non-Celestial Private Contract and the equipment that makes its defense
# preparation materially different on later runs. Private contracts never join
# the shared server roll; a player earns them from a person, faction, or prior
# consequence and has a limited window to claim them.
STANDALONE_PERKS.update({
    "trapper": {
        "name": "Trapper", "description": "Builds field snares and reads likely enemy approaches.",
        "effect": "Unlocks Iron-Jaw Snares during defense preparation.",
    },
    "field_fortifier": {
        "name": "Field Fortifier", "description": "Turns carried tools into useful cover under time pressure.",
        "effect": "Adds preparation budget and unlocks raised firing platforms.",
    },
})
ITEMS.update({
    "trappers_roll": {
        "name": "Trapper's Roll", "slot": "accessory", "tags": ["trapping_gear", "survival_gear"],
        "bonuses": {"survival": 2}, "attribute_bonuses": {"dex": 1}, "granted_perks": ["trapper"],
        "rarity": "uncommon", "description": "Wire, jaws, chalk, and stakes packed for quickly setting a field snare.",
    },
    "hedgerow_engineers_kit": {
        "name": "Hedgerow Engineer's Kit", "slot": "accessory",
        "tags": ["defense_gear", "construction_gear"], "bonuses": {"building": 3, "survival": 1},
        "attribute_bonuses": {"int": 1}, "granted_perks": ["field_fortifier"], "rarity": "rare",
        "description": "Compact braces and tools that add 2 preparation points and unlock a raised firing platform in defense battles.",
    },
})
MISSION_TEMPLATES["hedgerow_terms"] = {
    "name": "Terms at Briar Ford",
    "description": "Keeper Mara Fen will share the watch network's warnings if Fortcamp agrees how its fighters will answer raids without leaving the farms undefended.",
    "rank": "E", "stat": "survival", "difficulty": 10, "party_size": 1,
    "mission_form": "diplomacy", "durations": [300], "pool_weight": 0, "chain_only": True,
    "chain_id": "hedgerow_watch", "chain_step": 1, "chain_total": 2,
    "private_source_name": "A sealed note from Keeper Mara Fen", "chain_next": "hedgerow_watch_defense",
    "claim_requirements": [],
    "visible_hints": ["This is a roll-driven negotiation.", "Survival knowledge and practical field experience make the agreement more credible."],
    "modifiers": [
        {"kind": "trait", "value": "scout", "bonus": 2, "label": "A Scout understands how warning routes fail"},
        {"kind": "attribute", "attribute": "luk", "op": ">=", "value": 7, "bonus": 1, "label": "LUK 7+ finds a compromise both sides can accept"},
    ],
    "critical_any": [{"kind": "stat", "stat": "survival", "op": ">=", "value": 8, "label": "Survival 8+"}],
    "special_events": [], "rewards": {}, "critical_rewards": {},
    "reward_preview": ["Hedgerow Watch faction contact", "Can unlock a prepared defense contract"],
    "narrative": {
        "approach": "Mara Fen met {lead} at Briar Ford with three farm ledgers and a map of signal fires. She did not need another promise of protection; she wanted to know which roads Fortcamp would actually defend when two warnings arrived together.",
        "critical_failure": "The discussion ended with both sides less certain than before. Mara kept the watch routes closed to Fortcamp and sent word that the farms would make their own plans.",
        "failure": "Mara accepted that Fortcamp meant well, but the proposed patrols left too many gaps. She postponed the agreement until the guild could offer a plan that worked beyond a single road.",
        "success": "The agreement divided the warning routes without pretending every farm could be guarded at once. Mara handed over the signal code and promised to send for Fortcamp before the next raiding party reached the hedgerow.",
        "critical_success": "The final plan used the farmers as observers without asking them to fight. Mara opened the full watch network to Fortcamp and marked the ground where a small force could hold off a much larger raid.",
    },
}
MISSION_TEMPLATES["hedgerow_watch_defense"] = {
    "name": "Hold the Hedgerow Watch",
    "description": "Keeper Mara Fen asks the guild to hold a warning post long enough for nearby farms to evacuate before a warhost raiding party arrives.",
    "rank": "E", "stat": "combat", "difficulty": 11, "party_size": 2, "pays_gold": True,
    "mission_form": "defense",
    "durations": [1], "pool_weight": 0, "chain_only": True,
    "chain_id": "hedgerow_watch", "chain_step": 2, "chain_total": 2,
    "private_source_name": "Keeper Mara's warning horn",
    "claim_requirements": [],
    "visible_hints": [
        "You will deploy the party and build basic defenses before initiative begins.",
        "Kobolds, Engineers, construction gear, and trapping gear add preparation options.",
        "Critical Success requires the keeper to remain unharmed and every guild defender to remain standing.",
    ],
    "combat_critical_condition": "Keep Mara unharmed and finish with every guild defender standing.",
    "modifiers": [], "critical_any": [], "special_events": [],
    "combat_encounter": {
        "id": "frontier_watch_defense", "name": "Prepared Defense",
        "description": "Deploy the defenders, spend a limited preparation budget, and keep the watch keeper alive.",
    },
    "rewards": {"materials": {"food": 5, "cloth": 3}},
    "critical_rewards": {},
    "reward_rolls": [
        {"source": "abandoned raider field gear", "chance": 38, "critical_bonus": 12, "reward": {"item": "trappers_roll"}},
        {"source": "Keeper Mara's private stores", "chance": 18, "critical_bonus": 17, "reward": {"item": "hedgerow_engineers_kit"}},
    ],
    "reward_preview": ["Scaled guild commission", "Chance for field-defense equipment", "Recovered food and cloth"],
    "narrative": {
        "approach": "Keeper Mara Fen had already sent the farmhands west when {party} reached the Hedgerow Watch. The guild had only minutes to choose firing positions, brace the road, and decide where the first attacker would be stopped.",
        "critical_failure": "The defense broke around the signal post. The guild pulled back through the hedgerow, but Mara never reached the Fortcamp road and the warning fire went dark behind them.",
        "failure": "The party survived, but the watch could not be held. Mara abandoned the signal post before the raiders surrounded it, leaving the farms with less warning than the guild had promised.",
        "success": "The prepared line forced the raiders to fight for every stretch of road. When the last attacker broke, Mara climbed back to the signal basket and sent the all-clear across the farms.",
        "critical_success": "The defenses held exactly where the party intended. Mara's warning fire never dimmed, the raiders left their field gear behind, and none of the farm roads fell silent.",
    },
}
MISSION_TEMPLATES["goblin_smoke_signals"]["chain_next"] = "hedgerow_terms"

# The audit runs last so it sees every ordinary, event, consequence, and private
# chain template after all of their world and reward data has been attached.
from .mission_refinement import apply_mission_refinement

apply_mission_refinement(MISSION_TEMPLATES)
from .tactical_contracts import apply_tactical_contracts
apply_tactical_contracts(MISSION_TEMPLATES)
from .perk_effects import annotate_perks
annotate_perks(STANDALONE_PERKS)
from .mission_storylines import apply_storylines
apply_storylines(MISSION_TEMPLATES)
from .mission_loot import apply_loot
apply_loot(ITEMS,MISSION_TEMPLATES)
from .gear_expansion import apply_gear_expansion
apply_gear_expansion(ITEMS, MISSION_TEMPLATES, GENERAL_LOOT_TABLE, EVENT_REWARD_TABLES)
for _item_id, _item in ITEMS.items():
    _item["icon"] = f"/assets/catalogue/items/{_item_id}.png"

from .progression_content import apply_progression
apply_progression(BUILDINGS, MISSION_TEMPLATES, ITEMS, PERK_TRACKS, GUILD_HALL_UPGRADES)
from .gear_progression import apply_slot_gear
apply_slot_gear(ITEMS,MISSION_TEMPLATES,GENERAL_LOOT_TABLE,EVENT_REWARD_TABLES)
for _item_id,_item in ITEMS.items():
    _item['icon']=f'/assets/catalogue/items/{_item_id}.png'
from .prison_recruitment import apply_prison_contracts
apply_prison_contracts(MISSION_TEMPLATES)
