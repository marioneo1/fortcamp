"""Package canonical races and name-authoring instructions for one GPT upload."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'docs/content'
OUTPUT = CONTENT / 'RACE_NAMES_GPT_BRIEF.md'

# Design inspirations, not an assertion of official D&D lore for these races.
GUIDANCE = {
    'Human': 'D&D human traditions; several coherent regional sound palettes, not all one pseudo-English family. Invent no Fortcamp countries.',
    'Goblin': 'D&D goblinoid inspiration: compact, sharp names and practical bynames; distinguish from kobolds. Avoid comedy-only names.',
    'Dwarf': 'D&D dwarf personal and clan-name structure; solid consonants with varied cadence, not every surname Iron-something.',
    'Wood Elf': 'D&D elf structure; melodic personal/family names, woodland emphasis without making every name a translated leaf.',
    'Half-Orc': 'D&D half-orc/human-orc naming influences; several plausible blends, not only brutal epithets.',
    'Halfling': 'D&D halfling personal/family structure; approachable, grounded sound without copying official families.',
    'Tiefling': 'D&D ancestral/infernal and chosen concept-name inspiration; variety beyond sinister names. Describe any mixed tradition explicitly.',
    'Hobgoblin': 'D&D goblinoid inspiration, more measured and formal cadence; military titles conditional, not racial birth names.',
    'Bugbear': 'D&D goblinoid analogue; lower, weightier sound and useful bynames, distinct from both goblins and ogres.',
    'Kobold': 'D&D draconic/kobold inspiration; short sibilant or clipped names, distinct from longer Dragonkin names.',
    'Orc': 'D&D orc inspiration; forceful but varied names and clan/byname options. Do not encode universal evil or war leadership.',
    'Revenant': 'Returned-person concept; former-life personal names and optional remembered bynames. No single official racial culture assumed.',
    'Undead': 'Former-life names across a coherent broad palette; optional grave-era aliases. No assumption that all are mindless or named Bone-something.',
    'High Elf': 'D&D elf structure, longer measured lyrical sound; distinguish Wood Elf while retaining related naming texture.',
    'Gnome': 'D&D gnome name/nickname inspiration, lively but pronounceable; no gag or machinery word for every given name.',
    'Manaforged': 'Original proposal, warforged-style self-chosen concept names as analogue; arcane/material sound, not official Eberron lore. Shared naming is suitable.',
    'Homunculus': 'Original proposal with alchemical/constructed-person inspiration; chosen personal names or workshop bynames, not disposable specimen labels only.',
    'Dreamkin': 'Original dream/folklore-inspired palette; soft and uncanny, but distinct readable people, not random dream sentences.',
    'Lizardfolk': 'D&D lizardfolk/draconic inspiration; concise reptilian sounds, optional descriptive bynames. Verify conventions rather than assume gender endings.',
    'Harpy': 'Original proposal drawing on classical harpy imagery and avian cadence; BOTH male and female exist here. Not automatically an aarakocra culture.',
    'Minotaur': 'D&D minotaur analogue where documented; optional classical labyrinth/bull phonetic inspiration, no copied gods/heroes or imported setting clans.',
    'Centaur': 'D&D centaur analogue where documented; classical/steppe-inspired cadence as alternatives, without claiming one universal culture.',
    'Astral Elf': 'D&D astral-elf/elf analogue; restrained stellar cadence, no copying named Spelljammer factions or adding cosmic rank to every name.',
    'Voidsent': 'Original void/extraplanar palette; coherent alien sound and chosen aliases, not copied Final Fantasy identities or universal demon titles.',
    'Alien': 'Original coherent nonhuman phonetic palette or chosen translation names; no uniform earth-star catalogue, random keyboard strings or copied sci-fi species.',
    'Dark Elf': 'D&D drow-style phonetic inspiration; original family names, no established drow houses, automatic matriarchy or universal malicious titles.',
    'Dryad': 'FEMALE ONLY here. Original botanical/classical dryad inspiration; personal names and optional grove bynames, no copied mythic individuals.',
    'Faun': 'Original pastoral/classical faun with D&D satyr as analogue; related inspiration is not exact species equivalence or compulsory revelry.',
    'Catfolk': 'D&D tabaxi may inspire translated evocative naming, but Catfolk is not automatically tabaxi. Prefer short personal names and optional feline bynames.',
    'Foxkin': 'Original fox-folklore palette; Japanese-inspired syllabic naming is an option, not obligatory universal kitsune culture or divine names.',
    'Merfolk': 'D&D aquatic folk/classical maritime analogue; liquid readable names and sea/clan bynames. Do not equate merfolk with tritons.',
    'Dragonkin': 'D&D dragonborn naming STRUCTURE as analogue; possible original clan-first format plus draconic personal names, without declaring biological equivalence.',
    'Fairy': 'D&D fey and European fairy folklore inspiration; bright/strange but not all childish or sugary names. Original personal and optional nature names.',
    'Slimefolk': 'Original proposal; fluid but readable chosen names, mineral/color/textural bynames sparingly. Shared naming suitable; avoid joke goo noises.',
    'Automaton': 'Original mechanical-person palette, warforged naming as analogy only; chosen names and meaningful designations, never numbering filler.',
    'Aasimar': 'D&D aasimar inspiration; personal names may reflect upbringing, not all angel names or implied divine office.',
    'Vampire': 'Former-life names with restrained Gothic influence as alternative; not every vampire noble, Eastern European or a copied famous vampire.',
    'Banshee': 'FEMALE ONLY here. Irish/Scottish Gaelic-inspired sound or remembered former-life names; no invented translations/etymology, no all-Wail aliases.',
    'Ogre': 'D&D giant/ogre analogue; short heavy names with varied vowels and practical bynames; do not make every ogre a comic fool.',
    'Troll': 'D&D troll or Scandinavian folklore as clearly labeled alternative; rough resonant sound, distinct from ogres, no imported genealogy.',
    'Werewolf': 'Former-life personal/family naming; optional pack epithet only when context supports it. Do not treat infection/form as a universal birth culture.',
    'Celestial': 'Original luminous/celestial-inspired pool; no real deity/angel canon identities or universal hierarchy. Existing unique Celestials stay protected; this pool does not authorize generic spawns.',
}


def build():
    sys.path.insert(0, str(ROOT))
    from backend.races import RACE_CATALOG, generated_genders
    from backend.content import RECRUIT_PROFILES, GENERIC_FIRST_NAMES, GENERIC_LAST_NAMES, CHAMPIONS, CELESTIALS
    races = list(RACE_CATALOG)
    if set(races) != set(GUIDANCE):
        raise ValueError('Race catalogue changed: review naming guidance before rebuilding.')
    excluded = set(GENERIC_FIRST_NAMES + GENERIC_LAST_NAMES)
    for profile in RECRUIT_PROFILES.values():
        excluded.update(profile.get('first_names', []))
        excluded.update(profile.get('last_names', []))
    protected = {v.get('name', k) for catalog in (CHAMPIONS, CELESTIALS) for k, v in catalog.items()}
    registry = {
        'status': 'Authoring snapshot only; no importer or runtime naming change.',
        'catalog_snapshot_date': '2026-10-08',
        'races': [{'race_id': r, 'allowed_genders': list(generated_genders(r)),
                   'style_guidance': GUIDANCE[r]} for r in races],
        'batches': [{'batch_id': f'race_names_{i//6+1:03}', 'races': races[i:i+6]}
                    for i in range(0, len(races), 6)],
        'excluded_existing_tokens': sorted(excluded),
        'protected_named_identities': sorted(protected),
        'source_starting_points': [
            {'title': 'D&D 2014 Basic Rules: Races (official; naming sections)',
             'url': 'https://www.dndbeyond.com/sources/dnd/basic-rules-2014/races'},
            {'title': 'D&D Beyond species directory (official; some material requires access)',
             'url': 'https://www.dndbeyond.com/species'},
        ],
    }
    source = (CONTENT / 'RACE_NAMES_AUTHORING_PROMPT.md').read_text(encoding='utf-8')
    master = source.split('```text', 1)[1].split('```', 1)[0].strip()
    return ('# Fortcamp race names: single-upload GPT brief\n\n'
            'Upload only this file to a FRESH GPT chat. Start batch 1 now. If a message\n'
            'is required, say "Run the attached brief." Download the JSON, then say NEXT\n'
            'for the next six races. Save all seven outputs to\n'
            '`docs/content/drafts/names/` in fortcamp-dev and tell Codex they are ready.\n'
            'Names are drafts; do not install them or rename existing characters.\n\n' +
            master + '\n\n## Complete race registry, batch manifest and exclusions\n\n```json\n' +
            json.dumps(registry, indent=2, ensure_ascii=False) + '\n```\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != result:
            raise SystemExit('Name brief is stale; rebuild it.')
        print('All 42 race guides, gender rules and generated brief match current sources.')
    else:
        OUTPUT.write_text(result, encoding='utf-8')
        print(OUTPUT)


if __name__ == '__main__':
    main()
