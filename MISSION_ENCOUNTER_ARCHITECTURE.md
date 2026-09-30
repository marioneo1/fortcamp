# Mission Encounter Architecture

## Implemented foundation

- `Smoke over the Hedgerows` is the first complete roll-to-combat investigation.
- It accepts one optional bodyguard. The bodyguard is validated and deployed but is excluded from the lead, support bonus, requirements, secret criteria, and probability calculation.
- Its hidden encounter check is seeded by the mission instance. Reloading or restarting cannot reroll whether the ambush occurred.
- A triggered ambush uses the `hedgerow_signal_site` scenario generator. The generator selects authored road, clearing, cover, elevation, deployment, and exit zones; it does not scatter independent random tiles.
- The same mission seed always compiles the same map. This makes saved battles stable and lets future Defense, Rescue, Recovery, Hunt, and Infiltration encounters reuse the compiler with their own scenario profiles.
- Debug mode exposes **Test Investigation Ambush** so this path can be opened directly.

Fortcamp missions use separate fields for **purpose**, **current resolution**,
**intended encounter**, and **combat disclosure**. A mission's purpose does not
decide whether it is a stat roll or a battle.

## Public contract types

- **Recovery:** Intended to become an adventure-mode expedition. The party moves
  through connected rooms, floors, basements, holes, and stairs; secures loot;
  and chooses whether to continue or extract. Generated floors should use authored
  room rules and encounter tables rather than unbounded random tiles.
- **Rescue:** Begins with search, travel, or investigation. The player may find a
  safe route, extract someone surrounded by enemies, or stay and eliminate the
  threat. The rescued character can become a movable defense or escort objective.
- **Escort:** A tactical route in which people or cargo move through danger.
- **Defense:** A tactical encounter built around protecting a person, object,
  structure, or boundary. Basic deployments allow starting positions. A later
  preparation phase will add ordinary traps; Trappers unlock advanced traps, and
  Engineers unlock ballistae, towers, walls, and engineered defenses.
- **Hunt:** Tracking and preparation use rolls; the confrontation is usually
  tactical. Objectives can include killing, capturing, driving off, or observing
  the quarry.
- **Containment:** Usually begins as a roll or choice sequence. Undead, creatures,
  constructs, or failed containment can create tactical combat.
- **Investigation:** Primarily rolls and informed choices. Evidence, choices, or
  chance may lead to combat. This possibility is not disclosed per contract.
- **Infiltration:** Intended tactical mode with detection, patrols, alarms, and
  stealth. Being discovered changes the encounter instead of automatically ending it.
- **Operation:** A larger mission allowed to combine rolls, decisions, tactical
  encounters, and extraction.
- **Diplomacy:** Dialogue choices and social rolls with factions. Agreements,
  reputation, introductions, and obligations can unlock Private Contracts.

## Resolution and disclosure

`resolution_mode` records what the current build can actually run. A contract is
only labeled as playable combat when its encounter and map exist.

`encounter_plan.mode` records its intended mature structure:

- `roll`
- `dialogue`
- `branching`
- `tactical`
- `adventure`

`encounter_plan.combat` controls design disclosure:

- `expected`: the premise clearly signals combat;
- `possible`: choices or failure may create combat;
- `unknown`: revealing the possibility would spoil the mission.

The mission board carries one general warning: contracts without an explicit
combat label can still become dangerous because of choices, failed rolls, or
discoveries. Hidden combat risk is never repeated on every card.

## Bodyguards

Uncertain investigations, diplomacy, containment, rescue, and broad operations
can provide bodyguard slots. A bodyguard:

- does not contribute stats or ordinary support bonuses to the primary roll;
- enters a tactical complication if one occurs;
- can protect or extract the principal mission characters;
- may contribute only through an explicit leadership, escort, faction, or support perk.

Selection, validation, encounter transfer, and post-mission release are implemented.
The first live use is `Smoke over the Hedgerows`; other contracts can reuse the
same fields when their tactical complication is authored.

## Private Contracts

**Private Contracts** is the player-owned counterpart to the shared mission board.
It will contain faction invitations, personal requests, Champion leads, Celestial
chapters, consequences from earlier choices, and direct messages from known NPCs.
Private Contracts can expire, but they never compete for the server-wide pool and
remain visible only to their owner.

## Race interaction

Race affects derived combat health, movement, evasion, initiative, armor, movement
type, resistances, weaknesses, mission aptitude, and form aptitude. These are strong
identities rather than cosmetic bonuses. Goblins, for example, have 70% base combat
health, +2 movement, +15 evasion, and +4 initiative, along with scavenging and
infiltration aptitude. Exact values remain balanceable without changing saved stats.
