# Race-name pools

October 8, 2026. **Seven submitted batches validated and installed in dev.**
Production remains on the preceding release. Original submissions are preserved.

Upload [RACE_NAMES_GPT_BRIEF.md](RACE_NAMES_GPT_BRIEF.md) alone to a fresh GPT chat.
If a message is required: `Run the attached brief.` Download the returned file,
then say `Next` for another six races. Seven batches cover all 42 current races.
Save `race_names_001.json` through `race_names_007.json` in
`E:\Other Games\Fortcamp\fortcamp-dev\docs\content\drafts\names\`.
Tell Codex when they are ready; the user need not assemble manifests or prompts.

## Scope and conventions

Male/female/shared ordinary and leader personal-name pools; family, clan, byname
or designation components; contextual titles and epithets; compatible display
formats. Dryad/Banshee remain female-only. Shared naming for constructed/other
people does not change their actual allowed genders. Boss status does not imply
royalty or create racial political lore. Animal encounter names are outside this
character-name batch.

Use original names following suitable D&D structures where supported by actual
sources. The official [2014 Basic Rules naming sections](https://www.dndbeyond.com/sources/dnd/basic-rules-2014/races)
are a starting point; [species directory](https://www.dndbeyond.com/species) can
locate additional material. Other influences in the brief are proposed analogues,
not asserted D&D canon or approved Fortcamp cultures. Source access limitations
must be reported. No copied canon identity or imported dynasty is required.

## Implemented generation

`backend/character_names.py` selects from the compiled
`backend/name_pools/race_names.json`, cached once per process. Generic and racial
recruitment, contract humanoid enemies, goblin chiefs/reinforcements and captive
cart identities use compatible names after the final gender is known. Female-only
Dryad/Banshee and shared construct naming retain the canonical gender rules.
Dragonkin clan-first formats are supported without imposing them on other races.

Bosses/special recruits use leader given-name pools. Titles and epithets are stored
but require an explicit matching context before use; current encounter integration
uses title-free names. Authored Courier/Cartmaster role labels remain. Single names
remain possible, while most generated people use a second component where supported.
Names stay at most 48 characters. Retry/fallback selection avoids duplicate full
names within a recruitment roster or generated encounter, including player names.

Naming uses a separate seeded random stream. Legacy RNG draws remain so the name
expansion does not change existing stat/portrait/reward roll sequences. Seeded
generated identities are reproducible; already saved names are not rewritten.
Existing placeholder migrations retain their previous naming behavior. Named
champions/Celestials and player-entered names remain protected. Celestial pool
availability does not authorize generic Celestial spawns. Animals keep species names.

Validation accepted all 42 entries with no removals, duplicate warnings, forbidden
existing tokens or schema/gender/length/format errors: 5,840 ordinary given names,
1,008 leader given names, 1,680 second components, 504 titles and 504 epithets.
Report: [RACE_NAMES_IMPORT.json](reviews/RACE_NAMES_IMPORT.json), including source
hashes. Source/convention claims are retained as author metadata; they have not
been independently certified as D&D lore. No new racial cultures or histories
were inferred from a name. Character-life story content remains proposal-only.

## Maintenance

Run `python tools/import_race_names.py` after reviewing a new submission, then
`python tools/import_race_names.py --check`. The runtime bundle is self-contained;
production will not need draft files to generate names when a future release is
authorized. Do not move or edit originals to make them appear approved: approval
and compilation are recorded separately. Eight dedicated name tests exercise all
race/gender/tier combinations, seeded reproducibility, uniqueness, contextual
titles, recruitment/enemy integration and saved identity preservation.

Source prompt: RACE_NAMES_AUTHORING_PROMPT.md. Builder:
`tools/build_race_names_brief.py`; run it and then `--check` after editing the
prompt or changing canonical races/name exclusions. Guidance must cover exactly
the current race catalogue. Changing a race's allowed genders requires explicit
canonical review; never infer a change from a generated name file.
