"""Recruitable race profiles, habitats, rarity bands, and hidden encounters."""
from __future__ import annotations


ADDITIONAL_RECRUIT_PROFILES = {
    "dark_elf": {
        "race": "Dark Elf", "series": "Original", "archetypes": ["adept", "scout", "fighter"],
        "extra_traits": ["darkvision", "ley_touched"], "attribute_bonuses": {"dex": 1, "int": 2},
        "first_names": ["Veyra", "Nym", "Sarith", "Ilvara", "Drisin", "Xune"],
        "last_names": ["Nightbloom", "Deepstar", "Gloamveil", "Underbough"],
    },
    "dryad": {
        "race": "Dryad", "series": "Original", "archetypes": ["medic", "adept", "scout"],
        "extra_traits": ["verdant_soul", "beast_bond"], "attribute_bonuses": {"vit": 1, "int": 2, "luk": 1},
        "first_names": ["Aster", "Bryony", "Elowen", "Hazel", "Ilex", "Sorrel"],
        "last_names": ["Rootsong", "Greenwake", "Old-Grove", "Rainbark"],
    },
    "faun": {
        "race": "Faun", "series": "Original", "archetypes": ["scout", "medic", "adept"],
        "extra_traits": ["wildsong", "pathfinder"], "attribute_bonuses": {"agi": 1, "luk": 2},
        "first_names": ["Piper", "Cyr", "Mallow", "Tansy", "Bramble", "Lute"],
        "last_names": ["Reedstep", "Thornpipe", "Dewhoof", "Merryglen"],
    },
    "catfolk": {
        "race": "Catfolk", "series": "Original", "archetypes": ["scout", "fighter", "medic"],
        "extra_traits": ["night_paws", "feral_agility"], "attribute_bonuses": {"dex": 1, "agi": 2},
        "first_names": ["Miri", "Kesh", "Nya", "Rook", "Sable", "Tavi"],
        "last_names": ["Softstep", "Moonwhisker", "Belltail", "Rooftop"],
    },
    "foxkin": {
        "race": "Foxkin", "series": "Original", "archetypes": ["adept", "scout", "medic"],
        "extra_traits": ["foxfire", "trickster"], "attribute_bonuses": {"int": 1, "agi": 1, "luk": 2},
        "first_names": ["Aki", "Inari", "Kiko", "Ren", "Suzu", "Yori"],
        "last_names": ["Nine-Lanterns", "Embertail", "Shrinepath", "Mistfur"],
    },
    "merfolk": {
        "race": "Merfolk", "series": "Original", "archetypes": ["medic", "scout", "fighter"],
        "extra_traits": ["waterborn", "tide_sense"], "attribute_bonuses": {"vit": 1, "dex": 1, "int": 1},
        "first_names": ["Maris", "Neris", "Ondine", "Pel", "Tethys", "Varo"],
        "last_names": ["Bluecurrent", "Pearl-Reef", "Deepwater", "Foamcrest"],
    },
    "dragonkin": {
        "race": "Dragonkin", "series": "Original", "archetypes": ["fighter", "adept", "builder"],
        "extra_traits": ["draconic_legacy", "scaled_hide"], "attribute_bonuses": {"str": 2, "vit": 2, "int": 1},
        "first_names": ["Arrax", "Cindra", "Kael", "Rhaska", "Syrax", "Veyna"],
        "last_names": ["Emberscale", "Skyclaw", "Bronzewing", "Old-Flame"],
    },
    "fairy": {
        "race": "Fairy", "series": "Original", "archetypes": ["adept", "medic", "scout"],
        "extra_traits": ["winged", "glamour", "ley_touched"], "attribute_bonuses": {"agi": 2, "int": 2, "luk": 2},
        "first_names": ["Blink", "Dew", "Fable", "Luma", "Pollen", "Whim"],
        "last_names": ["Glimmerwing", "Bluebell", "Sunmote", "Secret-Laugh"],
    },
    "slimefolk": {
        "race": "Slimefolk", "series": "Original", "archetypes": ["medic", "adept", "builder"],
        "extra_traits": ["amorphous", "alchemical_body"], "attribute_bonuses": {"vit": 2, "luk": 1},
        "first_names": ["Bloop", "Ceria", "Gel", "Mallow", "Opal", "Visku"],
        "last_names": ["Brightdrop", "Many-Shapes", "Glasspool", "Softbody"],
    },
    "automaton": {
        "race": "Automaton", "series": "Original", "archetypes": ["builder", "fighter", "adept"],
        "extra_traits": ["constructed", "precision_core"], "attribute_bonuses": {"vit": 2, "int": 2},
        "first_names": ["Bell", "Delta", "Kite", "Morrow", "Unit", "Vox"],
        "last_names": ["Brass-Series", "Clockheart", "Foundry-Nine", "Unshackled"],
    },
    "aasimar": {
        "race": "Aasimar", "series": "Original", "archetypes": ["medic", "adept", "fighter"],
        "extra_traits": ["divine_magic", "radiant_soul"], "attribute_bonuses": {"int": 2, "vit": 1, "luk": 2},
        "first_names": ["Aurel", "Caelia", "Iriel", "Lucent", "Seren", "Vesper"],
        "last_names": ["Dawnward", "Hallowed", "Mercy-Star", "Sun-Vow"],
    },
    "vampire": {
        "race": "Vampire", "series": "Original", "archetypes": ["fighter", "adept", "scout"],
        "extra_traits": ["deathless", "blood_sense", "night_paws"], "attribute_bonuses": {"str": 1, "agi": 2, "int": 1},
        "first_names": ["Carmilla", "Dorian", "Ilyana", "Lazlo", "Mara", "Vladis"],
        "last_names": ["Crimsoncourt", "Nightglass", "Pale-Crown", "Velvetgrave"],
    },
    "undead": {
        "race": "Undead", "series": "Original", "archetypes": ["builder", "fighter", "scout", "adept"],
        "extra_traits": ["deathless", "graveward"], "attribute_bonuses": {"vit": 2, "luk": 1},
        "first_names": ["Rattle", "Morrow", "Ivory", "Knell", "Pall", "Dirge"],
        "last_names": ["Bonebound", "Crypt-Walker", "Old-Epitaph", "Bellkeeper"],
    },
    "alien": {
        "race": "Alien", "series": "Original", "archetypes": ["scout", "adept", "fighter"],
        "extra_traits": ["alien_physiology", "gravity_walker"], "attribute_bonuses": {"agi": 2, "int": 1, "luk": 1},
        "first_names": ["Aru", "Cinderstar", "Ixo", "Kepler", "Nyra", "Vela"],
        "last_names": ["Far-Traveler", "Long-Signal", "Red-Orbit", "Worldless"],
    },
    "voidsent": {
        "race": "Voidsent", "series": "Original", "archetypes": ["adept", "fighter", "scout"],
        "extra_traits": ["void_adapted", "aether_hunger", "void_sight"], "attribute_bonuses": {"vit": 1, "int": 2, "luk": 1},
        "first_names": ["Cairn", "Eidolon", "Nox", "Serein", "Umbra", "Vanta"],
        "last_names": ["Beyond-the-Rift", "Last-Star", "No-Horizon", "World-Eater"],
    },
    "banshee": {
        "race": "Banshee", "series": "Original", "archetypes": ["adept", "scout"],
        "extra_traits": ["deathless", "wailing_magic", "incorporeal"], "attribute_bonuses": {"agi": 2, "int": 2, "luk": 1},
        "first_names": ["Eira", "Keening", "Mourn", "Nuala", "Siofra", "Wail"],
        "last_names": ["Last-Cry", "Veilwalker", "Hollow-Song", "Grey-Memory"],
    },
    "ogre": {
        "race": "Ogre", "series": "Original", "archetypes": ["fighter", "builder", "medic"],
        "extra_traits": ["titan_strength", "iron_stomach"], "attribute_bonuses": {"str": 3, "vit": 2},
        "first_names": ["Borga", "Duma", "Gorr", "Marda", "Ogg", "Vrana"],
        "last_names": ["Bridgeback", "Ironbelly", "Rockeater", "Two-Hammers"],
    },
    "troll": {
        "race": "Troll", "series": "Original", "archetypes": ["fighter", "medic", "builder"],
        "extra_traits": ["regeneration", "troll_blood"], "attribute_bonuses": {"str": 2, "vit": 3},
        "first_names": ["Broll", "Grenda", "Hruk", "Moss", "Torga", "Ulm"],
        "last_names": ["Dawnmender", "Mirehide", "Stone-Regrows", "Underbridge"],
    },
}

RACE_TRAIT_PERKS = {
    "darkvision": {"name": "Darkvision", "description": "Sees clearly in caverns and lightless ruins.", "effect": "Can unlock underground and night-route opportunities."},
    "verdant_soul": {"name": "Verdant Soul", "description": "Carries a living bond with old forests and growing things.", "effect": "Can unlock grove, herb, and nature-related mission paths."},
    "wildsong": {"name": "Wildsong", "description": "Reads the moods of wild places through rhythm and sound.", "effect": "Can unlock peaceful wilderness encounters."},
    "night_paws": {"name": "Night Paws", "description": "Moves quietly and confidently after dark.", "effect": "Can unlock stealth and nocturnal routes."},
    "foxfire": {"name": "Foxfire", "description": "Conjures elusive spirit flame and misleading lights.", "effect": "Can unlock shrine, illusion, and secret-court encounters."},
    "trickster": {"name": "Trickster", "description": "Excels at misdirection, bargains, and lateral solutions.", "effect": "Can unlock deceptive or diplomatic mission paths."},
    "waterborn": {"name": "Waterborn", "description": "Is fully at home beneath deep or fast-moving water.", "effect": "Can unlock submerged routes and aquatic rescues."},
    "tide_sense": {"name": "Tide Sense", "description": "Feels currents, pressure changes, and approaching floods.", "effect": "Can unlock safer water-region approaches."},
    "draconic_legacy": {"name": "Draconic Legacy", "description": "Bears the endurance and presence of an ancient draconic bloodline.", "effect": "Can unlock dragon territory encounters and intimidation paths."},
    "glamour": {"name": "Glamour", "description": "Bends attention with subtle fae illusion.", "effect": "Can unlock hidden fae and social routes."},
    "amorphous": {"name": "Amorphous", "description": "Can compress and reshape a fluid body around obstacles.", "effect": "Can unlock narrow, flooded, or unstable passages."},
    "alchemical_body": {"name": "Alchemical Body", "description": "A mutable body naturally reacts to magical compounds.", "effect": "Can unlock unusual alchemy outcomes."},
    "precision_core": {"name": "Precision Core", "description": "A tireless constructed mind performs exact mechanical work.", "effect": "Can unlock foundry and machinery encounters."},
    "radiant_soul": {"name": "Radiant Soul", "description": "Channels a trace of celestial light.", "effect": "Can unlock sacred and planar mission paths."},
    "wailing_magic": {"name": "Wailing Magic", "description": "Shapes grief and spectral resonance into magic.", "effect": "Can unlock spirit and haunting-related routes."},
    "incorporeal": {"name": "Incorporeal", "description": "Can briefly pass through ordinary physical barriers.", "effect": "Can unlock sealed or obstructed paths."},
    "iron_stomach": {"name": "Iron Stomach", "description": "Can endure food and toxins that would stop most travelers.", "effect": "Can unlock hazardous provisioning routes."},
    "regeneration": {"name": "Regeneration", "description": "Recovers from wounds with unnatural speed.", "effect": "Can unlock high-risk endurance paths."},
    "troll_blood": {"name": "Troll Blood", "description": "Carries the stubborn vitality of old troll lineages.", "effect": "Can unlock ancient bridge and mire encounters."},
    "alien_physiology": {"name": "Alien Physiology", "description": "A body shaped by the pressures and chemistry of another world.", "effect": "Can unlock extraterrestrial relic and hostile-environment routes."},
    "aether_hunger": {"name": "Aether Hunger", "description": "A Voidsent survives by consuming loose magic leaking between ruined planes.", "effect": "Can unlock void-rift encounters, but may draw the attention of stronger outsiders."},
}


# Player-facing discovery information. Secret lineup recipes are deliberately absent.
RACE_CATALOG = {
    "Human": ("Common", "Settlements, roads, ruins, and rescue missions"),
    "Goblin": ("Common", "Goblin camps, warrens, and the Green Warhost"),
    "Dwarf": ("Uncommon", "Mines, mountain roads, workshops, and foundries"),
    "Wood Elf": ("Uncommon", "Old forests, herb grounds, and wild trails"),
    "Half-Orc": ("Uncommon", "Frontier roads, mercenary camps, and war zones"),
    "Halfling": ("Uncommon", "Farms, trade roads, orchards, and settlements"),
    "Tiefling": ("Rare", "Planar ruins, occult sites, and arcane disturbances"),
    "Hobgoblin": ("Uncommon", "Organized Green Warhost forces"),
    "Bugbear": ("Rare", "Deep Warhost territory and ambush grounds"),
    "Kobold": ("Common", "Warhost tunnels, trapworks, and mines"),
    "Orc": ("Uncommon", "Warhost fronts, badlands, and contested roads"),
    "Revenant": ("Very Rare", "High-rank Ashen Procession missions"),
    "Undead": ("Uncommon", "Graveyards, ossuaries, and Ashen Procession routes"),
    "High Elf": ("Rare", "Leyline sites, observatories, and arcane ruins"),
    "Gnome": ("Uncommon", "Workshops, mines, and Arcane Convergence sites"),
    "Manaforged": ("Mythic", "The deepest Arcane Convergence missions"),
    "Homunculus": ("Rare", "Laboratories and alchemical incidents"),
    "Dreamkin": ("Very Rare", "Dream markets and unstable leyline sites"),
    "Lizardfolk": ("Uncommon", "Marshes, flooded roads, and Beast Tide wetlands"),
    "Harpy": ("Rare", "Cliffs and aerial Beast Tide nests"),
    "Minotaur": ("Mythic", "The greatest Beast Tide migrations"),
    "Centaur": ("Very Rare", "Open plains and major Beast Tide routes"),
    "Astral Elf": ("Rare", "Starfall ruins and celestial signals"),
    "Voidsent": ("Very Rare", "Rifts where dead worlds bleed magic into ours"),
    "Alien": ("Rare", "Crater fields, silent signals, and moving Starfall fragments"),
    "Dark Elf": ("Rare", "Deep ruins, under-roads, and planar breaches"),
    "Dryad": ("Rare", "Ancient groves and undisturbed herb grounds"),
    "Faun": ("Uncommon", "Woodland paths, orchards, and hidden meadows"),
    "Catfolk": ("Uncommon", "Trade roads, rooftops, and frontier settlements"),
    "Foxkin": ("Rare", "Shrines, dream markets, and enchanted woods"),
    "Merfolk": ("Rare", "Flooded ruins, rivers, and coastal routes"),
    "Dragonkin": ("Mythic", "Dragon territory, volcanic quarries, and great hunts"),
    "Fairy": ("Mythic", "Hidden groves and powerful leyline blooms"),
    "Slimefolk": ("Uncommon", "Alchemical spills, sewers, and wet ruins"),
    "Automaton": ("Very Rare", "Foundries, workshops, and arcane laboratories"),
    "Aasimar": ("Mythic", "Sacred breaches and celestial events"),
    "Vampire": ("Mythic", "Noble crypts during the Ashen Procession"),
    "Banshee": ("Very Rare", "Haunted roads, drowned ruins, and grave sites"),
    "Ogre": ("Rare", "Mountain bridges, siege lines, and badland camps"),
    "Troll": ("Mythic", "Ancient bridges, deep mires, and Warhost fringes"),
    "Werewolf": ("Secret", "A rare transformation associated with the Blood-Moon Den"),
    "Celestial": ("Limited", "Unique gods reached through hidden, claimant-only mission chains"),
}

# Families are broad, overlapping mission categories rather than displayed races.
# Characters always keep their concrete race name in saves and throughout the UI.
BEASTKIN_RACES = frozenset({
    "Catfolk", "Foxkin", "Faun", "Harpy", "Centaur", "Minotaur",
    "Lizardfolk", "Kobold", "Merfolk", "Dragonkin", "Werewolf",
})
RACE_GROUPS = {
    "Beastkin": BEASTKIN_RACES,
    "Deathless": frozenset({"Undead", "Banshee", "Revenant", "Vampire"}),
    "Goblinoid": frozenset({"Goblin", "Hobgoblin", "Bugbear"}),
    "Elven": frozenset({"Wood Elf", "High Elf", "Dark Elf", "Astral Elf"}),
    "Construct": frozenset({"Automaton", "Manaforged", "Homunculus"}),
    "Giantkin": frozenset({"Ogre", "Troll", "Minotaur"}),
    "Fae": frozenset({"Fairy", "Dryad", "Faun", "Foxkin"}),
    "Planar": frozenset({"Tiefling", "Aasimar", "Voidsent", "Celestial"}),
}
RACE_FAMILIES = {
    race: tuple(group for group, members in RACE_GROUPS.items() if race in members)
    for race in RACE_CATALOG
}


# Strong racial identities. These values deliberately create visible differences
# now; exact numbers can be tuned after more encounters exist. Mission bonuses are
# capped by the mission analyzer, while combat values apply to derived battle units.
def _race_identity(
    summary: str, *, hp: float = 1.0, hp_bonus: int = 0, move: int = 0,
    evasion: int = 0, armor: int = 0, initiative: int = 0,
    movement: str = "ground", mission: dict[str, int] | None = None,
    forms: dict[str, int] | None = None, resist: tuple[str, ...] = (),
    weak: tuple[str, ...] = (), limitations: tuple[str, ...] = (),
) -> dict:
    return {
        "summary": summary, "hp_multiplier": hp, "hp_bonus": hp_bonus,
        "move_bonus": move, "evasion": evasion, "armor_bonus": armor,
        "initiative_bonus": initiative, "movement_type": movement,
        "mission_bonuses": mission or {}, "form_bonuses": forms or {},
        "resistances": list(resist), "weaknesses": list(weak),
        "limitations": list(limitations),
    }


RACE_GAMEPLAY = {
    "Human": _race_identity("Adaptable and dependable without an extreme racial weakness.", mission={"scavenging": 1}),
    "Goblin": _race_identity("Fragile, extremely mobile skirmishers who excel at scavenging and infiltration.", hp=.70, move=2, evasion=15, initiative=4, mission={"scavenging": 2, "survival": 1}, forms={"infiltration": 2}, limitations=("Low maximum health",)),
    "Dwarf": _race_identity("Slow, armored, and difficult to dislodge; exceptional around structures and machinery.", hp=1.15, move=-1, evasion=-5, armor=2, mission={"building": 2}, forms={"recovery": 1}),
    "Wood Elf": _race_identity("Fast woodland scouts with strong ranged positioning and survival instincts.", hp=.90, move=1, evasion=10, initiative=2, mission={"survival": 2, "medicine": 1}, forms={"investigation": 1}),
    "Half-Orc": _race_identity("Hard-hitting frontier survivors who remain mobile despite their strength.", hp=1.15, armor=1, mission={"combat": 1, "survival": 1}, forms={"defense": 1}),
    "Halfling": _race_identity("Small, evasive opportunists who survive through speed and improbable luck.", hp=.78, move=1, evasion=13, initiative=2, mission={"scavenging": 1}, forms={"infiltration": 2}),
    "Tiefling": _race_identity("Planar-blooded generalists comfortable around heat, curses, and unstable magic.", hp=.95, evasion=4, initiative=1, mission={"magic": 2}, forms={"containment": 1}, resist=("burn",), weak=("radiant",)),
    "Hobgoblin": _race_identity("Disciplined soldiers whose defense and formation control exceed their speed.", hp=1.10, armor=2, initiative=1, mission={"combat": 2}, forms={"defense": 2}),
    "Bugbear": _race_identity("Powerful ambushers who trade sustained defense for a dangerous opening strike.", hp=1.12, move=1, evasion=5, initiative=3, mission={"combat": 1, "survival": 1}, forms={"infiltration": 2}),
    "Kobold": _race_identity("Fragile tunnel runners and trapsmiths who are strongest when allowed to prepare.", hp=.72, move=1, evasion=12, initiative=3, mission={"building": 2, "scavenging": 1}, forms={"infiltration": 1, "defense": 1}, limitations=("Low maximum health",)),
    "Orc": _race_identity("Aggressive and durable fighters with limited subtlety but excellent staying power.", hp=1.22, armor=1, evasion=-4, mission={"combat": 2}, forms={"hunt": 1}),
    "Revenant": _race_identity("Relentless oath-bound dead who resist injury but struggle to disengage.", hp=1.25, move=-1, armor=2, initiative=-1, mission={"combat": 1, "magic": 1}, resist=("poison", "sleep", "fear"), weak=("radiant",)),
    "Undead": _race_identity("Tireless bodies immune to mortal needs, but vulnerable to sacred power.", hp=1.12, move=-1, armor=1, mission={"survival": 2}, resist=("poison", "sleep", "bleed"), weak=("radiant",)),
    "High Elf": _race_identity("Precise, magically gifted specialists whose physical resilience is modest.", hp=.88, evasion=6, initiative=2, mission={"magic": 2}, forms={"investigation": 1}),
    "Gnome": _race_identity("Small arcane engineers who solve technical problems faster than they endure direct hits.", hp=.76, evasion=8, initiative=2, mission={"building": 2, "magic": 1}, forms={"investigation": 1}),
    "Manaforged": _race_identity("Heavy magical constructs with exceptional durability and poor natural recovery.", hp=1.32, move=-1, armor=3, evasion=-7, mission={"magic": 2, "building": 2}, resist=("poison", "sleep", "bleed"), weak=("disruption",), limitations=("Cannot recover through ordinary medicine",)),
    "Homunculus": _race_identity("Purpose-built magical bodies that adapt quickly but can destabilize under disruption.", hp=.88, evasion=6, initiative=2, mission={"alchemy": 2, "medicine": 1, "magic": 1}, weak=("disruption",)),
    "Dreamkin": _race_identity("Elusive mind-walkers with exceptional magical perception and fragile bodies.", hp=.72, move=1, evasion=16, initiative=3, mission={"magic": 2}, forms={"investigation": 2}, resist=("sleep", "charm")),
    "Lizardfolk": _race_identity("Armored wetland hunters who endure hazards and move freely through shallow water.", hp=1.15, armor=2, evasion=-2, movement="amphibious", mission={"survival": 2}, forms={"hunt": 1}),
    "Harpy": _race_identity("Fast aerial scouts who ignore pits and ground obstacles but cannot take heavy punishment.", hp=.78, move=2, evasion=14, initiative=4, movement="flying", mission={"survival": 1}, forms={"investigation": 1}, weak=("bind",)),
    "Minotaur": _race_identity("Massive shock fighters with tremendous health and very little ability to evade.", hp=1.45, hp_bonus=8, move=-1, evasion=-12, armor=2, mission={"combat": 2}, forms={"defense": 1}, limitations=("Large body struggles in confined routes",)),
    "Centaur": _race_identity("Extremely fast open-ground combatants who lose their advantage indoors.", hp=1.18, move=2, evasion=4, initiative=3, mission={"survival": 2}, forms={"escort": 1}, limitations=("Confined interiors restrict movement",)),
    "Astral Elf": _race_identity("Star-touched scouts who combine precision, mobility, and planar awareness.", hp=.90, move=1, evasion=10, initiative=3, mission={"magic": 2, "survival": 1}, forms={"investigation": 1}),
    "Voidsent": _race_identity("Durable outsiders empowered by loose magic and endangered by aether starvation.", hp=1.18, armor=1, evasion=4, mission={"magic": 2}, forms={"containment": 2}, resist=("magic",), weak=("radiant",), limitations=("Long deployments require an aether source",)),
    "Alien": _race_identity("Unfamiliar biology handles hostile environments well but interacts unpredictably with medicine.", hp=1.05, move=1, evasion=7, initiative=2, mission={"survival": 2, "magic": 1}, forms={"investigation": 1}, limitations=("Ordinary medicine is less effective",)),
    "Dark Elf": _race_identity("Swift under-road specialists skilled in darkness, stealth, and dangerous magic.", hp=.88, move=1, evasion=11, initiative=3, mission={"magic": 1, "survival": 1}, forms={"infiltration": 2}),
    "Dryad": _race_identity("Resilient living spirits who thrive near natural ground and suffer around fire.", hp=1.20, armor=1, move=-1, mission={"medicine": 2, "survival": 2}, forms={"containment": 1}, resist=("poison",), weak=("burn",)),
    "Faun": _race_identity("Quick pathfinders and natural negotiators with little interest in heavy armor.", hp=.88, move=1, evasion=9, initiative=2, mission={"survival": 2}, forms={"escort": 1, "diplomacy": 1}),
    "Catfolk": _race_identity("Highly mobile nocturnal scouts with strong evasion and modest endurance.", hp=.86, move=1, evasion=14, initiative=4, mission={"scavenging": 1, "survival": 1}, forms={"infiltration": 1}),
    "Foxkin": _race_identity("Elusive illusionists and negotiators who win through misdirection rather than force.", hp=.82, move=1, evasion=13, initiative=3, mission={"magic": 1}, forms={"diplomacy": 2, "infiltration": 1}),
    "Merfolk": _race_identity("Exceptional aquatic rescuers whose mobility drops on dry ground.", hp=1.02, move=-1, evasion=3, movement="amphibious", mission={"medicine": 1, "survival": 2}, forms={"rescue": 2}, limitations=("Reduced movement away from water",)),
    "Dragonkin": _race_identity("Heavily protected elite combatants with draconic endurance and elemental vulnerability choices later.", hp=1.30, armor=3, evasion=-5, mission={"combat": 2, "magic": 1}, forms={"defense": 1}),
    "Fairy": _race_identity("Tiny flying spellcasters who are exceptionally hard to hit and exceptionally easy to injure.", hp=.52, move=2, evasion=20, initiative=5, movement="flying", mission={"magic": 2}, forms={"investigation": 1, "diplomacy": 1}, weak=("bind",), limitations=("Extremely low maximum health",)),
    "Slimefolk": _race_identity("Amorphous bodies absorb impacts and pass narrow spaces but react badly to freezing.", hp=1.18, move=-1, evasion=7, armor=1, movement="amorphous", mission={"alchemy": 2, "scavenging": 1}, forms={"recovery": 1}, resist=("bleed", "impact"), weak=("freeze",)),
    "Automaton": _race_identity("Precise armored workers immune to mortal ailments but vulnerable to disruption.", hp=1.28, move=-1, armor=3, evasion=-6, mission={"building": 2}, forms={"defense": 1}, resist=("poison", "sleep", "bleed"), weak=("disruption",), limitations=("Requires repair instead of ordinary medicine",)),
    "Aasimar": _race_identity("Radiant protectors with strong resistance to corruption and broad magical utility.", hp=1.12, armor=1, mission={"medicine": 1, "magic": 2}, forms={"rescue": 1, "containment": 1}, resist=("radiant", "fear")),
    "Vampire": _race_identity("Fast, powerful night hunters whose strength comes with severe radiant vulnerability.", hp=1.08, move=1, evasion=10, initiative=4, mission={"combat": 1, "magic": 1}, forms={"infiltration": 1}, resist=("poison", "sleep"), weak=("radiant",), limitations=("Daylight penalties will apply on exposed maps",)),
    "Banshee": _race_identity("Incorporeal flying casters who evade physical threats but cannot endure focused magic.", hp=.68, move=2, evasion=18, initiative=4, movement="flying", mission={"magic": 2}, forms={"infiltration": 2}, resist=("bleed", "bind"), weak=("magic", "radiant")),
    "Ogre": _race_identity("Enormous bruisers with high health, crushing strength, and poor evasion.", hp=1.48, hp_bonus=10, move=-1, evasion=-12, armor=1, mission={"combat": 2, "building": 1}, forms={"defense": 1}),
    "Troll": _race_identity("Extremely durable regenerators who are slow and especially vulnerable to fire.", hp=1.58, hp_bonus=8, move=-1, evasion=-14, armor=1, mission={"survival": 2}, forms={"defense": 1}, resist=("poison",), weak=("burn",)),
    "Werewolf": _race_identity("Fast predatory fighters with strong pursuit and unreliable control under later moon rules.", hp=1.24, move=1, evasion=8, initiative=3, mission={"combat": 2, "survival": 1}, forms={"hunt": 2}, weak=("silver",)),
    "Celestial": _race_identity("Unique divine beings with exceptional resilience and influence, constrained by personal oaths.", hp=1.35, armor=2, evasion=5, initiative=2, mission={"magic": 2, "combat": 1}, forms={"diplomacy": 2, "containment": 1}, resist=("radiant", "fear"), limitations=("Divine oaths can forbid specific choices",)),
}


def race_gameplay(race: str) -> dict:
    return RACE_GAMEPLAY.get(race, RACE_GAMEPLAY["Human"])


def race_mission_bonus(race: str, stat: str, mission_form: str) -> int:
    profile = race_gameplay(race)
    return int(profile["mission_bonuses"].get(stat, 0)) + int(profile["form_bonuses"].get(mission_form, 0))


def race_families(race: str) -> tuple[str, ...]:
    return RACE_FAMILIES.get(race, ())


def race_family(race: str) -> str | None:
    """Backward-compatible primary family; new logic should use race_families."""
    families = race_families(race)
    return families[0] if families else None

REGIONAL_RECRUIT_TABLES = {
    "frontier": [("survivor", "D", 18), ("halfling", "D", 8), ("half_orc", "C", 6), ("catfolk", "C", 5)],
    "deepwood": [("survivor", "D", 10), ("wood_elf", "D", 12), ("faun", "D", 8), ("dryad", "B", 3), ("fairy", "S", 1)],
    "mountains": [("survivor", "D", 8), ("dwarf", "D", 13), ("gnome", "C", 8), ("ogre", "B", 4), ("troll", "S", 1), ("dragonkin", "S", 1)],
    "waters": [("survivor", "D", 10), ("lizardfolk", "D", 11), ("slimefolk", "C", 7), ("merfolk", "B", 3)],
    "ruins": [("survivor", "D", 10), ("tiefling", "C", 7), ("dark_elf", "B", 5), ("slimefolk", "C", 6), ("automaton", "A", 2)],
}

MISSION_RECRUIT_REGIONS = {
    "roadside_store": "frontier", "raider_checkpoint": "frontier", "highway_ambush": "frontier",
    "bandit_outpost": "frontier", "quarantine_house": "frontier", "fallen_orchard": "deepwood",
    "missing_trapper": "deepwood", "charcoal_camp": "deepwood", "herb_meadow": "deepwood",
    "deep_expedition": "deepwood", "creekside_scrap": "waters", "flooded_underpass": "waters",
    "ash_tunnel": "mountains", "iron_ogre_bridge": "mountains", "dragon_roost": "mountains",
    "collapsed_workshop": "ruins", "industrial_yard": "ruins", "old_armory": "ruins",
    "arcane_observatory": "ruins", "haunted_foundry": "ruins", "planar_breach": "ruins",
}


# Conditions stay server-side. The client only receives whether the selected lineup
# has made one of these low-chance encounters possible.
SECRET_RECRUIT_EVENTS = {
    "haunted_foundry": [{
        "id": "the_sleeping_shift", "chance": 7, "critical_bonus": 5,
        "conditions": [
            {"kind": "race", "value": "Gnome"},
            {"kind": "trait", "value": "constructed"},
            {"kind": "trait", "value": "engineer"},
        ],
        "reward": {"procedural_recruit": [{"profile": "automaton", "weight": 100}]},
        "label": "A dormant worker woke beneath the foundry and chose to follow the party home.",
    }],
    "sealed_crypt": [{
        "id": "guest_behind_the_wall", "chance": 6, "critical_bonus": 5,
        "conditions": [
            {"kind": "race", "value": "Vampire"},
            {"kind": "trait", "value": "undead_hunter"},
            {"kind": "trait", "value": "divine_magic"},
        ],
        "reward": {"procedural_recruit": [{"profile": "vampire", "weight": 65}, {"profile": "banshee", "weight": 35}]},
        "label": "The party opened a chamber omitted from every map and its prisoner accepted sanctuary.",
    }],
    "titan_migration": [{
        "id": "egg_beneath_the_footfall", "chance": 5, "critical_bonus": 4,
        "conditions": [
            {"kind": "race", "value": "Lizardfolk"},
            {"kind": "race", "value": "Centaur"},
            {"kind": "trait", "value": "beast_bond"},
            {"kind": "trait", "value": "pathfinder"},
        ],
        "reward": {"procedural_recruit": [{"profile": "dragonkin", "weight": 100}]},
        "label": "A hidden clutch survived the migration, and its lone guardian pledged herself to the camp.",
    }],
    "planar_breach": [{
        "id": "accord_of_opposites", "chance": 5, "critical_bonus": 5,
        "conditions": [
            {"kind": "race", "value": "Tiefling"},
            {"kind": "race", "value": "High Elf"},
            {"kind": "trait", "value": "divine_magic"},
            {"kind": "trait", "value": "ley_touched"},
        ],
        "reward": {"procedural_recruit": [{"profile": "aasimar", "weight": 100}]},
        "label": "A second doorway briefly aligned with the breach, allowing a radiant exile to cross safely.",
    }],
    "heart_of_leyline": [{
        "id": "court_between_seconds", "chance": 4, "critical_bonus": 4,
        "conditions": [
            {"kind": "race", "value": "Dreamkin"},
            {"kind": "race", "value": "Dryad"},
            {"kind": "trait", "value": "foxfire"},
            {"kind": "trait", "value": "glamour"},
        ],
        "reward": {"procedural_recruit": [{"profile": "fairy", "weight": 100}]},
        "label": "For one heartbeat the hidden court became real, and one of its envoys remained behind.",
    }],
    "tomb_beyond_sky": [{
        "id": "pilgrim_of_the_first_light", "chance": 3, "critical_bonus": 4,
        "conditions": [
            {"kind": "race", "value": "Astral Elf"},
            {"kind": "race", "value": "Voidsent"},
            {"kind": "trait", "value": "stellar_aegis"},
            {"kind": "trait", "value": "soul_anchor"},
            {"kind": "attribute", "attribute": "luk", "op": ">=", "value": 10},
        ],
        "reward": {"items": ["celestial_halo"]}, "chain_start": "owl_of_bronze_1",
        "label": "The tomb answered the party's resonance. A bronze owl carried an invitation into the upper dark.",
    }],
    "undead_last_funeral": [{
        "id": "the_unweighed_heart", "chance": 4, "critical_bonus": 4,
        "conditions": [
            {"kind": "race", "value": "Vampire"}, {"kind": "race", "value": "Undead"},
            {"kind": "trait", "value": "divine_magic"}, {"kind": "trait", "value": "soul_anchor"},
            {"kind": "attribute", "attribute": "int", "op": ">=", "value": 10},
        ],
        "reward": {"items": ["ashen_reliquary"]}, "chain_start": "silent_scale_1",
        "label": "A black jackal watched the last grave close, then left a trail no ordinary eye could see.",
    }],
    "beast_world_eater_wake": [{
        "id": "the_second_moon_hunt", "chance": 4, "critical_bonus": 4,
        "conditions": [
            {"kind": "race", "value": "Centaur"}, {"kind": "race", "value": "Dryad"},
            {"kind": "trait", "value": "tracker"}, {"kind": "trait", "value": "moon_sense"},
            {"kind": "attribute", "attribute": "dex", "op": ">=", "value": 10},
        ],
        "reward": {"items": ["moonwood_longbow"]}, "chain_start": "silver_hunt_1",
        "label": "A silver arrow struck the World-Eater's wake from beyond sight, bearing a challenge for the hunters.",
    }],
    "arcane_zero_hour": [{
        "id": "the_golden_thread", "chance": 4, "critical_bonus": 4,
        "conditions": [
            {"kind": "race", "value": "Foxkin"}, {"kind": "race", "value": "High Elf"},
            {"kind": "trait", "value": "ley_touched"}, {"kind": "trait", "value": "glamour"},
            {"kind": "attribute", "attribute": "luk", "op": ">=", "value": 10},
        ],
        "reward": {"items": ["living_grimoire"]}, "chain_start": "golden_seidr_1",
        "label": "Time resumed around a single golden thread tied to the party's gear, leading north through empty air.",
    }],
}
