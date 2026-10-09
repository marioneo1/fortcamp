# Race-name pools

October 8, 2026. **Authoring prepared; generated names not received or installed.**

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

## Existing code and integration still needed

`backend/game.py:_make_procedural` currently chooses from small mixed first/last
name arrays before selecting gender. `backend/combat.py` also contains a short
separate humanoid-name list and goblin boss naming. New pools alone do not fix
those paths; integration must choose gender first, select compatible parts,
preserve deterministic seed behavior and avoid duplicate visible full names.
Unusual naming formats need deliberate support, not blind first+last concatenation.
Named characters, player names and existing saves must retain their identities.
Generating a Celestial pool does not authorize generic Celestial spawns.

When batches return, preserve submissions and review counts, race/gender IDs,
normalized duplicates, excluded names, lengths, style/source honesty and valid
formats. Author self-review is not validation. Approve content before runtime
integration; record accepted revisions and missing coverage in the content index.

## Maintenance

Source prompt: RACE_NAMES_AUTHORING_PROMPT.md. Builder:
`tools/build_race_names_brief.py`; run it and then `--check` after editing the
prompt or changing canonical races/name exclusions. Guidance must cover exactly
the current race catalogue. Changing a race's allowed genders requires explicit
canonical review; never infer a change from a generated name file.
