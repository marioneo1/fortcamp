# Fortcamp race names: single-upload GPT brief

Upload only this file to a FRESH GPT chat. Start batch 1 now. If a message
is required, say "Run the attached brief." Download the JSON, then say NEXT
for the next six races. Save all seven outputs to
`docs/content/drafts/names/` in fortcamp-dev and tell Codex they are ready.
Names are drafts; do not install them or rename existing characters.

You are authoring large ORIGINAL character-name pools for Fortcamp, a tactical
fantasy game. Execute batch 1 from the attached manifest now. Do not ask the user
to explain the project. Only one batch per response. On NEXT, produce the next
batch in manifest order, retaining this contract. There are seven batches of six
races, not one enormous response. On REGENERATE BATCH N, replace only that batch.

Use the exact race IDs and allowed genders in the attached registry. Banshee and
Dryad are female-only in THIS GAME. All other listed races currently allow male
and female, including constructs and Harpy. These are game settings, not claims
about D&D. Never add a race or alter its gender rules.

STYLE AND SOURCES
- Prefer established D&D naming STRUCTURE and sound where an appropriate
  analogue exists, with ORIGINAL names rather than copied official name lists.
  Read the official references if browsing is available; record only sources
  actually consulted. Distinguish verified convention from an inspired analogue
  and an original Fortcamp proposal. Do not claim all 42 races have official rules.
- The supplied per-race style guide includes alternatives for non-D&D races.
  Other RPG naming styles and real-world linguistic influences may guide sound;
  they do not import another setting's clans, gods, politics or named characters.
  When sources are unavailable, say so and use the provided fallback guidance.
- Do not copy famous characters, deities, named canon houses, named guilds or
  obvious franchise names. The exclusion manifest also lists existing Fortcamp
  tokens and protected identities. Do not deliberately reuse those to pad pools.
- Names should be pronounceable, distinguishable and usable in combat UI. Most
  given names 3-12 characters; hard maximum 18 Unicode characters. Second-name
  components max 22, titles/epithets max 24. Avoid apostrophe spam, forced exotic
  spelling, joke names, slurs, modern memes and serial-number padding.
- Vary consonants, vowels, cadence, length and initials. Do not fill a pool by
  changing one letter, attaching the same suffix or renaming all women with -a.
  Different races should not all sound like elves or share the same handful of
  names. Ordinary people need ordinary names, not all legendary grimdark titles.
- Gendered pools reflect the chosen naming style; shared names are intentionally
  usable by either gender. Never infer gender from art. Do not duplicate a shared
  name in male/female arrays. For genuinely nongendered naming traditions, use
  the shared-pool exception below rather than inventing artificial gender markers.

QUANTITY, PER RACE
- Ordinary gendered style: 60 male given names, 60 female, 20 shared.
- Female-only races: male=[], 120 female given names, shared=[]; do not add male
  boss names. Shared-pool exception does not override the game's allowed genders.
- Optional nongendered style for Manaforged, Automaton, Homunculus, Slimefolk or
  Alien: male=[], female=[], 140 shared given names. This changes only the naming
  style; it does not change the allowed genders. Otherwise use the ordinary counts.
- 40 second-name components TOTAL across family/clan/byname/designation arrays;
  choose which categories fit, never force a surname system onto every race.
  At least one category must be nonempty. Explain that components are optional
  if the culture normally uses only one name.
- Leader personal-name pool: 10 male, 10 female, 4 shared. For female-only races:
  male=[], female=24, shared=[]. For a nongendered style: shared=24, others=[].
- 12 contextual leader titles and 12 contextual epithets. Leader given names must
  be distinct from ordinary given names, but ordinary names can ALSO belong to a
  leader. The special pool adds variety; it does not establish noble birth.

BOSSES AND HIERARCHY
- A boss is a combat role, not automatically king, noble, elder or divine. Titles
  are OPTIONAL and selected only when their role/context fits. Prefer portable
  roles: patrol leader, captain, ritual leader, veteran, camp chief, spokesperson.
- Do not invent universal monarchies, matriarchies or caste systems. Do not make
  every female boss a queen/matriarch or every male boss a king/warlord.
- Use title records with text, role_context and gender (male/female/any). Respect
  female-only pools. Epithets have text and requires_context: the fact that must
  be true before displaying them. A name cannot invent kills, powers or history.
- Personal name, family/clan component, rank title and earned epithet are separate
  fields. Do not embed Captain or the Merciless inside given_names. Recruitment
  does not automatically rename someone or turn an earned title into a surname.
- Define compatible display formats. Dragonkin may PROPOSE clan-first ordering
  inspired by dragonborn; do not force that ordering on every race. No random
  mixing of incompatible naming traditions or required empty pools.

OUTPUT
Return ONE complete downloadable JSON file named race_names_00N.json. If file
creation is unavailable, return the complete raw JSON object with no markdown.
No prose outside the file, no TODOs, no ellipses and no partial arrays. Never
invent Python/random syllable generation to pretend it authored meaningful names.
Use this shape (replace explanatory strings/empty arrays with actual content):
{
  "schema_version": "names-0.1",
  "batch_id": "race_names_001",
  "revision": 1,
  "status": "draft",
  "entries": [{
    "race_id": "EXACT MANIFEST RACE",
    "allowed_genders": ["male", "female"],
    "naming_style": "gendered",
    "convention_basis": "verified_dnd OR dnd_inspired OR original_proposal",
    "style_notes": "One or two sentences; structure, sound and fallback rationale.",
    "sources_consulted": [{"title": "Actual consulted source", "url": "Actual source URL"}],
    "given_names": {"male": [], "female": [], "shared": []},
    "second_names": {"family": [], "clan": [], "byname": [], "designation": []},
    "leader_given_names": {"male": [], "female": [], "shared": []},
    "leader_titles": [{"text": "original title", "role_context": "when appropriate", "gender": "any"}],
    "epithets": [{"text": "original epithet", "requires_context": "supporting known fact"}],
    "ordinary_formats": ["{given} {family}"],
    "leader_formats": ["{title} {given} {family}", "{given} {family} {epithet}"]
  }],
  "self_review": {
    "race_count": 6,
    "actual_counts_by_race": {},
    "duplicates": [],
    "excluded_name_collisions": [],
    "overlength_items": [],
    "source_limitations": [],
    "shortfalls": [],
    "next_batch_id": "race_names_002"
  }
}

naming_style is gendered or shared. sources_consulted=[] is honest if no sources
were consulted; explain in source_limitations. Formats use only {given}, {family},
{clan}, {byname}, {designation}, {title}, {epithet}. Every referenced pool must be
nonempty. Give at least one short title-free format; avoid overlong combinations.
Allowed genders must exactly match the manifest, even when naming_style=shared.
actual_counts_by_race maps each race to counts of male/female/shared ordinary and
leader names, second-name total, title count and epithet count. Never fake counts.

Check duplicate strings case-insensitively after trimming whitespace and treating
straight/curly apostrophes or hyphen variants alike. Given names must be unique
across gender/shared/leader pools within the race. Prefer unique given names
across the batch too; flag intentional cross-race overlap, do not silently pad.
Second names can be shared across genders and boss tiers via the same pool.
Check eligibility, exclusion manifest, lengths, formats and actual counts.
Self-review is NOT proof a validator ran. Return a complete smaller batch with
explicit shortfalls if limits prevent the full request; do not truncate a race.
Codex will validate and review before integration. No game files/saves change.

## Complete race registry, batch manifest and exclusions

```json
{
  "status": "Authoring snapshot only; no importer or runtime naming change.",
  "catalog_snapshot_date": "2026-10-08",
  "races": [
    {
      "race_id": "Human",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D human traditions; several coherent regional sound palettes, not all one pseudo-English family. Invent no Fortcamp countries."
    },
    {
      "race_id": "Goblin",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D goblinoid inspiration: compact, sharp names and practical bynames; distinguish from kobolds. Avoid comedy-only names."
    },
    {
      "race_id": "Dwarf",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D dwarf personal and clan-name structure; solid consonants with varied cadence, not every surname Iron-something."
    },
    {
      "race_id": "Wood Elf",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D elf structure; melodic personal/family names, woodland emphasis without making every name a translated leaf."
    },
    {
      "race_id": "Half-Orc",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D half-orc/human-orc naming influences; several plausible blends, not only brutal epithets."
    },
    {
      "race_id": "Halfling",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D halfling personal/family structure; approachable, grounded sound without copying official families."
    },
    {
      "race_id": "Tiefling",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D ancestral/infernal and chosen concept-name inspiration; variety beyond sinister names. Describe any mixed tradition explicitly."
    },
    {
      "race_id": "Hobgoblin",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D goblinoid inspiration, more measured and formal cadence; military titles conditional, not racial birth names."
    },
    {
      "race_id": "Bugbear",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D goblinoid analogue; lower, weightier sound and useful bynames, distinct from both goblins and ogres."
    },
    {
      "race_id": "Kobold",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D draconic/kobold inspiration; short sibilant or clipped names, distinct from longer Dragonkin names."
    },
    {
      "race_id": "Orc",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D orc inspiration; forceful but varied names and clan/byname options. Do not encode universal evil or war leadership."
    },
    {
      "race_id": "Revenant",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Returned-person concept; former-life personal names and optional remembered bynames. No single official racial culture assumed."
    },
    {
      "race_id": "Undead",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Former-life names across a coherent broad palette; optional grave-era aliases. No assumption that all are mindless or named Bone-something."
    },
    {
      "race_id": "High Elf",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D elf structure, longer measured lyrical sound; distinguish Wood Elf while retaining related naming texture."
    },
    {
      "race_id": "Gnome",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D gnome name/nickname inspiration, lively but pronounceable; no gag or machinery word for every given name."
    },
    {
      "race_id": "Manaforged",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original proposal, warforged-style self-chosen concept names as analogue; arcane/material sound, not official Eberron lore. Shared naming is suitable."
    },
    {
      "race_id": "Homunculus",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original proposal with alchemical/constructed-person inspiration; chosen personal names or workshop bynames, not disposable specimen labels only."
    },
    {
      "race_id": "Dreamkin",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original dream/folklore-inspired palette; soft and uncanny, but distinct readable people, not random dream sentences."
    },
    {
      "race_id": "Lizardfolk",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D lizardfolk/draconic inspiration; concise reptilian sounds, optional descriptive bynames. Verify conventions rather than assume gender endings."
    },
    {
      "race_id": "Harpy",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original proposal drawing on classical harpy imagery and avian cadence; BOTH male and female exist here. Not automatically an aarakocra culture."
    },
    {
      "race_id": "Minotaur",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D minotaur analogue where documented; optional classical labyrinth/bull phonetic inspiration, no copied gods/heroes or imported setting clans."
    },
    {
      "race_id": "Centaur",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D centaur analogue where documented; classical/steppe-inspired cadence as alternatives, without claiming one universal culture."
    },
    {
      "race_id": "Astral Elf",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D astral-elf/elf analogue; restrained stellar cadence, no copying named Spelljammer factions or adding cosmic rank to every name."
    },
    {
      "race_id": "Voidsent",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original void/extraplanar palette; coherent alien sound and chosen aliases, not copied Final Fantasy identities or universal demon titles."
    },
    {
      "race_id": "Alien",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original coherent nonhuman phonetic palette or chosen translation names; no uniform earth-star catalogue, random keyboard strings or copied sci-fi species."
    },
    {
      "race_id": "Dark Elf",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D drow-style phonetic inspiration; original family names, no established drow houses, automatic matriarchy or universal malicious titles."
    },
    {
      "race_id": "Dryad",
      "allowed_genders": [
        "female"
      ],
      "style_guidance": "FEMALE ONLY here. Original botanical/classical dryad inspiration; personal names and optional grove bynames, no copied mythic individuals."
    },
    {
      "race_id": "Faun",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original pastoral/classical faun with D&D satyr as analogue; related inspiration is not exact species equivalence or compulsory revelry."
    },
    {
      "race_id": "Catfolk",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D tabaxi may inspire translated evocative naming, but Catfolk is not automatically tabaxi. Prefer short personal names and optional feline bynames."
    },
    {
      "race_id": "Foxkin",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original fox-folklore palette; Japanese-inspired syllabic naming is an option, not obligatory universal kitsune culture or divine names."
    },
    {
      "race_id": "Merfolk",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D aquatic folk/classical maritime analogue; liquid readable names and sea/clan bynames. Do not equate merfolk with tritons."
    },
    {
      "race_id": "Dragonkin",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D dragonborn naming STRUCTURE as analogue; possible original clan-first format plus draconic personal names, without declaring biological equivalence."
    },
    {
      "race_id": "Fairy",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D fey and European fairy folklore inspiration; bright/strange but not all childish or sugary names. Original personal and optional nature names."
    },
    {
      "race_id": "Slimefolk",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original proposal; fluid but readable chosen names, mineral/color/textural bynames sparingly. Shared naming suitable; avoid joke goo noises."
    },
    {
      "race_id": "Automaton",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original mechanical-person palette, warforged naming as analogy only; chosen names and meaningful designations, never numbering filler."
    },
    {
      "race_id": "Aasimar",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D aasimar inspiration; personal names may reflect upbringing, not all angel names or implied divine office."
    },
    {
      "race_id": "Vampire",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Former-life names with restrained Gothic influence as alternative; not every vampire noble, Eastern European or a copied famous vampire."
    },
    {
      "race_id": "Banshee",
      "allowed_genders": [
        "female"
      ],
      "style_guidance": "FEMALE ONLY here. Irish/Scottish Gaelic-inspired sound or remembered former-life names; no invented translations/etymology, no all-Wail aliases."
    },
    {
      "race_id": "Ogre",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D giant/ogre analogue; short heavy names with varied vowels and practical bynames; do not make every ogre a comic fool."
    },
    {
      "race_id": "Troll",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "D&D troll or Scandinavian folklore as clearly labeled alternative; rough resonant sound, distinct from ogres, no imported genealogy."
    },
    {
      "race_id": "Werewolf",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Former-life personal/family naming; optional pack epithet only when context supports it. Do not treat infection/form as a universal birth culture."
    },
    {
      "race_id": "Celestial",
      "allowed_genders": [
        "male",
        "female"
      ],
      "style_guidance": "Original luminous/celestial-inspired pool; no real deity/angel canon identities or universal hierarchy. Existing unique Celestials stay protected; this pool does not authorize generic spawns."
    }
  ],
  "batches": [
    {
      "batch_id": "race_names_001",
      "races": [
        "Human",
        "Goblin",
        "Dwarf",
        "Wood Elf",
        "Half-Orc",
        "Halfling"
      ]
    },
    {
      "batch_id": "race_names_002",
      "races": [
        "Tiefling",
        "Hobgoblin",
        "Bugbear",
        "Kobold",
        "Orc",
        "Revenant"
      ]
    },
    {
      "batch_id": "race_names_003",
      "races": [
        "Undead",
        "High Elf",
        "Gnome",
        "Manaforged",
        "Homunculus",
        "Dreamkin"
      ]
    },
    {
      "batch_id": "race_names_004",
      "races": [
        "Lizardfolk",
        "Harpy",
        "Minotaur",
        "Centaur",
        "Astral Elf",
        "Voidsent"
      ]
    },
    {
      "batch_id": "race_names_005",
      "races": [
        "Alien",
        "Dark Elf",
        "Dryad",
        "Faun",
        "Catfolk",
        "Foxkin"
      ]
    },
    {
      "batch_id": "race_names_006",
      "races": [
        "Merfolk",
        "Dragonkin",
        "Fairy",
        "Slimefolk",
        "Automaton",
        "Aasimar"
      ]
    },
    {
      "batch_id": "race_names_007",
      "races": [
        "Vampire",
        "Banshee",
        "Ogre",
        "Troll",
        "Werewolf",
        "Celestial"
      ]
    }
  ],
  "excluded_existing_tokens": [
    "Adel",
    "Aelira",
    "Aerie",
    "Aki",
    "Alba",
    "Anvilward",
    "Arrax",
    "Aru",
    "Ashhorn",
    "Ashnose",
    "Ashspear",
    "Ashwake",
    "Aster",
    "Astrael",
    "Aurel",
    "Avaris",
    "Axiom",
    "Aya",
    "Azhak",
    "Banner-Breaker",
    "Bell",
    "Bellkeeper",
    "Belltail",
    "Beyond-the-Rift",
    "Blacktusk",
    "Blink",
    "Bloop",
    "Blue-Core",
    "Bluebell",
    "Bluecurrent",
    "Bonebound",
    "Borga",
    "Brakka",
    "Bram",
    "Bramble",
    "Brass-Series",
    "Bridgeback",
    "Brightdrop",
    "Brightsocket",
    "Brik",
    "Broadback",
    "Broadhand",
    "Broll",
    "Brom",
    "Bronzewing",
    "Brum",
    "Bryony",
    "Caelen",
    "Caelia",
    "Caelum",
    "Cairn",
    "Carmilla",
    "Ceria",
    "Chain-Cutter",
    "Cinder-Vow",
    "Cinderstar",
    "Cindra",
    "Cipher",
    "Clockheart",
    "Cloudcry",
    "Cloudstep",
    "Coilwick",
    "Comet-Veil",
    "Concordant",
    "Copperclaw",
    "Coppervein",
    "Cora",
    "Corvin",
    "Crimsoncourt",
    "Crookblade",
    "Cross",
    "Crypt-Walker",
    "Cyr",
    "Dagna",
    "Dama",
    "Dane",
    "Dawnmender",
    "Dawnscript",
    "Dawnward",
    "Deepburrow",
    "Deepdelve",
    "Deepstar",
    "Deepwater",
    "Delta",
    "Dew",
    "Dewhoof",
    "Dirge",
    "Dorian",
    "Drav",
    "Dren",
    "Drisin",
    "Drok",
    "Duma",
    "Echo",
    "Eidolon",
    "Eira",
    "Elowen",
    "Ember",
    "Emberscale",
    "Embertail",
    "Emberveil",
    "Fable",
    "Faela",
    "Far-Blood",
    "Far-Lantern",
    "Far-Traveler",
    "Farstrider",
    "Fernwatch",
    "Fizz",
    "Foamcrest",
    "Foundry-Nine",
    "Gara",
    "Gatekeeper",
    "Gel",
    "Ghazra",
    "Glassborn",
    "Glasspool",
    "Glimmerwing",
    "Gloamveil",
    "Goodbarrel",
    "Gorr",
    "Grass-Sea",
    "Greenpath",
    "Greenwake",
    "Grenda",
    "Grey-Memory",
    "Greyhand",
    "Grin",
    "Grol",
    "Hale",
    "Half-Awake",
    "Hallowed",
    "Harka",
    "Hazel",
    "Hearthlane",
    "High-Nest",
    "Hollow-Song",
    "Hruk",
    "Ilex",
    "Ilvara",
    "Ilyana",
    "Inari",
    "Ione",
    "Iriel",
    "Iris",
    "Iron-Ear",
    "Ironbelly",
    "Ironrank",
    "Ironroot",
    "Isska",
    "Istra",
    "Ithil",
    "Ivory",
    "Ixo",
    "Kael",
    "Kalai",
    "Kallista",
    "Kara",
    "Keening",
    "Kelda",
    "Kepler",
    "Kesh",
    "Kestrel",
    "Keth",
    "Kezra",
    "Kiko",
    "Kip",
    "Kiri",
    "Kite",
    "Knell",
    "Korr",
    "Korun",
    "Krag",
    "Last-Cry",
    "Last-Star",
    "Last-Vow",
    "Lazlo",
    "Lethan",
    "Liora",
    "Long-Signal",
    "Longarm",
    "Lucent",
    "Lucid",
    "Luma",
    "Lumen",
    "Lute",
    "Lyss",
    "Malk",
    "Mallow",
    "Many-Shapes",
    "Many-Teeth",
    "Mara",
    "Maraag",
    "Marchborn",
    "Marda",
    "Maris",
    "Marsh-Claw",
    "Mazha",
    "Mellis",
    "Mercy-Star",
    "Merek",
    "Meros",
    "Merryglen",
    "Mika",
    "Milo",
    "Mira",
    "Mirehide",
    "Mirelle",
    "Miri",
    "Mistfur",
    "Mog",
    "Mogg",
    "Moonarchive",
    "Moonwhisker",
    "Mordai",
    "Morka",
    "Morrow",
    "Moss",
    "Mossback",
    "Mourn",
    "Naeris",
    "Nella",
    "Neris",
    "Nessa",
    "Nib",
    "Night-Orbit",
    "Nightbloom",
    "Nightbrush",
    "Nightglass",
    "Nikka",
    "Niko",
    "Nim",
    "Nimara",
    "Nine-Lanterns",
    "Ninth Batch",
    "No-Horizon",
    "Nox",
    "Nuala",
    "Nya",
    "Nym",
    "Nyra",
    "Nyx",
    "Oathkeeper",
    "Ogg",
    "Old-Epitaph",
    "Old-Flame",
    "Old-Grove",
    "Ondine",
    "Oneir",
    "Opal",
    "Open-Sky",
    "Orbi",
    "Orik",
    "Orion",
    "Orren",
    "Orun",
    "Oryn",
    "Owlwood",
    "Pale-Crown",
    "Pall",
    "Pearl-Reef",
    "Pel",
    "Pella",
    "Pelor",
    "Pexa",
    "Pim",
    "Piper",
    "Pollen",
    "Prism",
    "Prismgear",
    "Quickhand",
    "Quickstep",
    "Quietmaul",
    "Quill",
    "Quin",
    "Rainbark",
    "Rainleaf",
    "Rattle",
    "Red-Maze",
    "Red-Orbit",
    "Red-Seal",
    "Redbanner",
    "Redknife",
    "Redstar",
    "Reed-Stalker",
    "Reedstep",
    "Rekk",
    "Ren",
    "Returned",
    "Reverie",
    "Reyes",
    "Rhaska",
    "Rho",
    "Ridgewing",
    "Rikka",
    "Rin",
    "Rissa",
    "Riven",
    "Rockeater",
    "Rooftop",
    "Rook",
    "Rootsong",
    "Rowan",
    "Runa",
    "Rusttooth",
    "Ruzza",
    "Sabine",
    "Sable",
    "Saffra",
    "Sarith",
    "Scree",
    "Secret-Laugh",
    "Sera",
    "Serein",
    "Seren",
    "Seven",
    "Shrinepath",
    "Silverbranch",
    "Siofra",
    "Skarn",
    "Skiv",
    "Skyclaw",
    "Snik",
    "Soft-Bell",
    "Softbody",
    "Softstep",
    "Somna",
    "Sootfoot",
    "Sorrel",
    "Spark-Eye",
    "Sszara",
    "Starwake",
    "Stillwater",
    "Stone",
    "Stone-Regrows",
    "Stoneblood",
    "Stoneheel",
    "Stonehorn",
    "Stonejaw",
    "Stormfeather",
    "Sun-Vow",
    "Sunmote",
    "Sunscale",
    "Sura",
    "Suzu",
    "Sylvi",
    "Syrax",
    "Takka",
    "Talen",
    "Talla",
    "Talon",
    "Tansy",
    "Tauren",
    "Tavi",
    "Tess",
    "Tethys",
    "Theren",
    "Thessa",
    "Thistlewick",
    "Thok",
    "Thornpipe",
    "Thrain",
    "Thunderhoof",
    "Tin-Ear",
    "Tinkertide",
    "Tizzi",
    "Tobin",
    "Torga",
    "Torv",
    "Two-Hammers",
    "Two-Roads",
    "Ulm",
    "Umbra",
    "Unbound",
    "Unburied",
    "Underbough",
    "Underbridge",
    "Unit",
    "Unshackled",
    "Usha",
    "Vaelis",
    "Vale",
    "Vanta",
    "Varo",
    "Vasha",
    "Vector",
    "Veilwalker",
    "Vek",
    "Vela",
    "Velka",
    "Velum",
    "Velvetgrave",
    "Venn",
    "Vesper",
    "Vessel",
    "Vexa",
    "Vey",
    "Veyna",
    "Veyra",
    "Visku",
    "Vladis",
    "Vox",
    "Vrana",
    "Vriss",
    "Vrix",
    "Vurna",
    "Wail",
    "Ward",
    "Warm-Stone",
    "Whim",
    "Wiretail",
    "World-Eater",
    "Worldless",
    "Wren",
    "Xune",
    "Yara",
    "Yori",
    "Zara",
    "Zhal"
  ],
  "protected_named_identities": [
    "Ai Hayasaka",
    "Aira Shiratori",
    "Ais Wallenstein",
    "Akane Kurokawa",
    "Akeno Himejima",
    "Albedo",
    "Alice Zuberg",
    "Ami Kawashima",
    "Android 18",
    "Anko Mitarashi",
    "Anna Yamada",
    "Annie Leonhart",
    "Anubis",
    "Anya Forger",
    "Aoi Kanzaki",
    "Aqua",
    "Asa Mitaka",
    "Asuka Langley",
    "Asuna Yuuki",
    "Athena",
    "Ayame",
    "Bellona",
    "Boa Hancock",
    "Bulma",
    "C.C.",
    "Carrot",
    "Cayena Hill",
    "Cha Hae-In",
    "Chika Fujiwara",
    "Chisato Nishikigi",
    "Chizuru Mizuhara",
    "Conis",
    "Darkness",
    "Deborah Seymour",
    "Diana",
    "Echidna",
    "Elma",
    "Emilia",
    "Endorsi Jahad",
    "Eris Miserian",
    "Erza Scarlet",
    "Esdeath",
    "Falin Touden",
    "Faye Valentine",
    "Fern",
    "Florentia Lombardi",
    "Freyja",
    "Frieren",
    "Goblin Slayer",
    "Guts",
    "Han Sooyoung",
    "Hana Inuzuka",
    "Hanabi Hyuga",
    "Hecate",
    "Hestia",
    "Himiko Toga",
    "Himmel",
    "Hinata Hyūga",
    "Historia Reiss",
    "Hitagi Senjougahara",
    "Hitori Gotoh",
    "Holo",
    "Homura Akemi",
    "Hwa Ryun",
    "Ichika Nakano",
    "Ihwa",
    "Ikuyo Kita",
    "Ino Yamanaka",
    "Iroha Isshiki",
    "Isane Kotetsu",
    "Isis",
    "Itsuki Nakano",
    "Jeanne d'Arc",
    "Jewelry Bonney",
    "Jinshi",
    "Jiyoung Yoo",
    "Juvelian Floyen",
    "Kaguya Shinomiya",
    "Kakashi Hatake",
    "Kallen Kōzuki",
    "Kana Arima",
    "Kanao Tsuyuri",
    "Kanna Kamui",
    "Karin Uzumaki",
    "Karui",
    "Kasumi Miwa",
    "Kaya",
    "Kim Dokja",
    "Kobeni Higashiyama",
    "Kotori Itsuka",
    "Kozuki Hiyori",
    "Kukaku Shiba",
    "Kurenai Yuhi",
    "Kurisu Makise",
    "Kurumi Tokisaki",
    "Kyoka Jiro",
    "Latte Ectrie",
    "Levi Ackerman",
    "Lisa Yadomaru",
    "Loid Forger",
    "Lucy Heartfilia",
    "Mabui",
    "Mai Sakurajima",
    "Maki Zenin",
    "Makima",
    "Makino",
    "Mami Nanami",
    "Maomao",
    "Marcille Donato",
    "Marguerite",
    "Marin Kitagawa",
    "Maximilian Calypse",
    "Medea Solon",
    "Megumin",
    "Mei Hatsume",
    "Melissa Podebrat",
    "Mikasa Ackerman",
    "Mikoto Misaka",
    "Miku Nakano",
    "Mikuru Asahina",
    "Milim Nava",
    "Mina Ashido",
    "Mina Carolina",
    "Minori Kushieda",
    "Mirko",
    "Mitsuri Kanroji",
    "Momo Ayase",
    "Momo Yaoyorozu",
    "Motoko Kusanagi",
    "Nami",
    "Navier Ellie Trovi",
    "Nefertari Vivi",
    "Nelliel Tu Odelschwanck",
    "Nezuko Kamado",
    "Nico Robin",
    "Nifa",
    "Nijika Ijichi",
    "Nino Nakano",
    "Nobara Kugisaki",
    "Nojiko",
    "Ochaco Uraraka",
    "Odin",
    "Origami Tobiichi",
    "Orihime Inoue",
    "Penelope Eckart",
    "Perona",
    "Petra Ral",
    "Pieck Finger",
    "Power",
    "Psyche Callista",
    "Rachel",
    "Raphtalia",
    "Raviel Ivansia",
    "Rei Ayanami",
    "Rem",
    "Retsu Unohana",
    "Revy",
    "Reze",
    "Rias Gremory",
    "Rico Brzenska",
    "Rikka Takanashi",
    "Rin Tohsaka",
    "Riruka Dokugamine",
    "Riza Hawkeye",
    "Roronoa Zoro",
    "Roxana Agriche",
    "Roxy Migurdia",
    "Ruby Hoshino",
    "Ruka Sarashina",
    "Rukia Kuchiki",
    "Rumiko Manbagi",
    "Ryo Yamada",
    "Ryuu Lion",
    "Ryūko Matoi",
    "Saber",
    "Saki Kawasaki",
    "Sakura Matou",
    "Samui",
    "Satoru Gojo",
    "Satsuki Kiryūin",
    "Seiko Ayase",
    "Seraphine Vale",
    "Shalltear Bloodfallen",
    "Shinobu Kocho",
    "Shion",
    "Shizuka Hiratsuka",
    "Shizune",
    "Shoko Ieiri",
    "Shoko Komi",
    "Shuna",
    "Shuri von Neuschwanstein",
    "Sinon",
    "Soi Fon",
    "Sumi Sakurasawa",
    "Sung Jinwoo",
    "Sword Maiden",
    "Sylphiette",
    "Taiga Aisaka",
    "Takina Inoue",
    "Tashigi",
    "Temari",
    "Tenten",
    "Tohka Yatogami",
    "Tohru",
    "Tsume Inuzuka",
    "Tsunade",
    "Tsuyu Asui",
    "Twenty-Fifth Bam",
    "Ulti",
    "Usagi Tsukino",
    "Utahime Iori",
    "Vinsmoke Reiju",
    "Violet Evergarden",
    "Vladilena Milizé",
    "Winry Rockbell",
    "Wiz",
    "Yamato",
    "Yoko Littner",
    "Yoo Joonghyuk",
    "Yor Forger",
    "Yoru",
    "Yoruichi Shihōin",
    "Yotsuba Nakano",
    "Yugao Uzuki",
    "Yui Yuigahama",
    "Yuki Nagato",
    "Yuki Tsukumo",
    "Yukino Yukinoshita",
    "Yunyun",
    "Yuri Jahad",
    "Zero Two",
    "Übel"
  ],
  "source_starting_points": [
    {
      "title": "D&D 2014 Basic Rules: Races (official; naming sections)",
      "url": "https://www.dndbeyond.com/sources/dnd/basic-rules-2014/races"
    },
    {
      "title": "D&D Beyond species directory (official; some material requires access)",
      "url": "https://www.dndbeyond.com/species"
    }
  ]
}
```
