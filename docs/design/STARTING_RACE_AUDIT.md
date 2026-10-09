# Starting race selection audit

October 8, 2026. Implemented in dev after user approval; production unchanged.

## Starting choices

Human, Dwarf, Wood Elf, High Elf, Half-Orc, Halfling, Gnome, Tiefling,
Goblin, Hobgoblin, Orc, Kobold, Lizardfolk, Catfolk.

These 14 give players generalist, durable, agile, magical and beastfolk options
without giving away most discovery rewards. Rarity alone is not the rule:
High Elf and Tiefling are reasonable starting identities despite being Rare.
This is an eligibility audit, not a claim that every racial profile is balanced.
Goblin, Kobold and Gnome durability still needs continued starter-map testing.

## Discover and recruit

Bugbear, Revenant, Undead, Manaforged, Homunculus, Dreamkin, Harpy,
Minotaur, Centaur, Astral Elf, Voidsent, Alien, Dark Elf, Dryad, Faun,
Foxkin, Merfolk, Dragonkin, Fairy, Slimefolk, Automaton, Aasimar,
Vampire, Banshee, Ogre, Troll.

Keep these 26 in the world and existing recruitment systems. Flying, extreme
durability, unusual bodies and planar identities make useful discoveries.
Dark Elf, Faun and Foxkin could be added later if the starting roster feels too
restrictive; their exclusion is a discovery/presentation choice, not a lore ban.
Do not invent new unlock requirements in this pass.

## Special acquisition

- Werewolf: retain its documented secret transformation acquisition.
- Celestial: retain limited, claimant-only discovery chains.

## Findings and implementation boundary

Previously the creator and API excluded only Limited rarity, permitting 41
races including Secret Werewolf. Both now enforce the approved 14-race policy.

Implemented one backend STARTING_RACES list, exposed starting_selectable in
the content response and made the creator follow it. The creation API rejects
all other races. Do not filter the full race catalogue: recruitment, name pools,
portraits and Battle Lab need the complete roster. Preserve existing player
characters and saves, regardless of their race. No racial stats, combat rules,
recruitment chances or production data should change with this restriction.

Validation: five onboarding tests, creator filtering test and frontend build pass.
Restart the dev backend when automatic reload is off to load the new policy.

The submitted name pools should still cover all 42 races. Starting eligibility
does not remove any race from content-authoring contracts.
