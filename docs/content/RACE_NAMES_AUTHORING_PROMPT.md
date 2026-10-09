# Fortcamp name-pool authoring instructions

Source for the generated single-upload brief. Draft authoring only; no names are
installed by this file. Codex maintains the attached registry and batch list.

```text
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
```
