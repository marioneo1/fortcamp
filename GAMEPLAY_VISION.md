# Fortcamp gameplay charter

This is the standing design direction agreed with the player. Use it when adding missions, characters, perks, equipment, or encounters. Keep all content SFW; reference Fort of Chains for structural ideas rather than copying adult stories or content.

## Missions unfold

A contract can combine scenes, informed choices, checks, combat, and extraction. Its form describes its purpose, not a guaranteed resolution method. Keep plentiful pure roll missions alongside tactical ones.

Each failed check needs an authored consequence. It can cost an optional discovery while the mission continues, close negotiations, change a route, start a fight, or expose an unusual opponent. Critical failure does not automatically finish a contract if a playable recovery encounter remains. Never award final loot or impose the standard mission-failure injury before that encounter is resolved.

Choices should communicate what a character is trying and the meaningful risk. Provide exact odds for visible checks. Some secrets and unexpected opponents can remain hidden. Save rolls and decisions; reopening, polling, or submitting twice cannot reroll them or duplicate rewards. Bodyguards protect characters in combat without adding to normal scene rolls.

Offer different combat approaches where they make sense: direct assault, scouting an opening, preparing cover with technical expertise. Night attacks need working sleep and detection mechanics before being sold as stealth. Larger deployment requires map capacity and scenario-specific slots.

Earned follow-ups appear immediately in owner-only Private Contracts, retaining their discovery rolls and original 24-hour claim window. Faction dialogue should build relationships and unlock personal requests; permanent reputation and recurring favors are the next extension.

## Character identity matters

Race substantially changes derived HP, movement, evasion, armor, initiative, and relevant checks. Goblins are fragile, fast skirmishers; racial disadvantages matter alongside strengths. Display actual implemented modifiers. Do not present future elemental affinities, upkeep, daylight, or loyalty restrictions as working rules.

Perks can grant abilities, passive combat effects, attribute changes, specialist capability, support, or noncombat systems. Some still unlock mission paths, but a path flag must not be the default implementation for every perk. Equipment-granted perks use the same mechanics as permanent ones, apply once, and disappear when unequipped. Stack bonuses within documented caps rather than inflating them indefinitely. Champion-specific perks deserve individually authored mechanics instead of arbitrary generic stat buffs.

## Rewards create builds

Separate the chance to receive loot from its rarity and its source. General, faction, event, mission-exclusive, capture-only, and secret-path pools can coexist. Higher ranks offer more rolls and better rarity odds. A rank never guarantees a jackpot.

Give event missions identifiable themed rewards. Keep some items exclusive to their mission or discovery route; do not leak them into broad random pools. Reward a defeated unexpected opponent with an appropriate chance, requiring its trophy to be recovered. Failure grants little or nothing. Gold remains restricted to contracts where payment or looted coin makes sense.

Gear should offer different build options: granted perks, weapon techniques, protections, positioning, preparation, support, or interaction effects. Stat bonuses can accompany those identities. Avoid universal upgrades that obsolete every alternative.

## Stories remain readable

Write clear English, concrete scenes, dialogue, setbacks, decisions, and consequences. Results should remember player choices and actual combat outcomes. Avoid internal criterion labels, forced appearance descriptions, and a list of attacks pretending to be a story. Generate names for ordinary NPCs; preserve established unique Champions and Celestials.

## Playable first pass: September 30

- Authored decision scenes: Smoke over the Hedgerows, The Black-Banner Ledger, The Bell Beneath the Mud, and Terms at Briar Ford.
- Combat approach choices: Goblin Warcamp and the eleven tactical contracts registered in `backend/tactical_contracts.py`.
- Timed critical-failure recovery encounters: Flooded Underpass, Restless Graves, and Goblin Supply Carts.
- Eight exclusive equipment pieces; optional discoveries use separate drop checks, and exceptional investigation opponents have trophy chances only after recovery.
- Rank-weighted rarity selection, general/faction mixing, and a dedicated first event cache.
- Core standalone perks now have shared bounded mechanics, including movement, armor, accuracy, specialist checks, regeneration, magic reduction, and enemy-family damage. Named Champion perks still need individual batches; the whole 310-perk catalog is not declared complete.
- Roster racial identity cards and racial perk tooltips show working numerical effects for all catalogued races.

Next authored batches should expand faction diplomacy, add scene continuations after combat and route-specific mission endings, then implement sleep/detection and coordinated night approaches. Preserve the existing mission and loot variety while expanding coverage.
