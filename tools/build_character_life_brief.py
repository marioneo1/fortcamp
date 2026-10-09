"""Build/check the offline, single-file GPT character-life brief; no save access."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'docs' / 'content'
CONTRACT = CONTENT / 'character-story-contract-v0.2.json'
PROMPT = CONTENT / 'CHARACTER_STORY_AUTHORING_PROMPT.md'
OUTPUT = CONTENT / 'CHARACTER_LIFE_GPT_BRIEF.md'
REQUEST = CONTENT / 'CHARACTER_LIFE_CURRENT_REQUEST.md'
SOURCE = CONTENT / 'drafts' / 'character_blueprints_pilot_001_revision_2.json'
REVIEW = CONTENT / 'reviews' / 'character_blueprints_pilot_001_revision_2.md'


def build():
    sys.path.insert(0, str(ROOT))
    from backend.relationships import PERSONALITIES
    from backend.races import RACE_CATALOG, RACE_GROUPS
    from backend.job_loadouts import JOBS

    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    expected = {
        'races': list(RACE_CATALOG),
        'race_families': {key: sorted(value) for key, value in RACE_GROUPS.items()},
        'personalities': list(PERSONALITIES),
        'jobs': list(JOBS),
    }
    for key, value in expected.items():
        if contract['existing_ids'][key] != value:
            raise ValueError(f'Authoring contract {key} differs from canonical code; review/update the contract first.')
    prompt = PROMPT.read_text(encoding='utf-8')
    master = prompt.split('```text', 1)[1].split('```', 1)[0].strip()
    request = REQUEST.read_text(encoding='utf-8').strip()
    source = SOURCE.read_text(encoding='utf-8-sig').strip()
    json.loads(source)  # Refuse to package a broken source submission.
    review = REVIEW.read_text(encoding='utf-8').strip()
    return (
        '# Fortcamp character-life authoring brief - v0.2\n\n'
        'Upload this ONE file to a FRESH GPT Chat. Execute the current task below\n'
        'when reading this attachment; no extra project explanation is required.\n'
        'If the interface requires a message, use: "Run the attached brief."\n\n'
        'Status: proposal only. All new history/arc/cap capabilities need review before\n'
        'implementation. This bundle contains the master prompt, CURRENT revision task,\n'
        'draft registry/output contract, source submission and review. Execute only\n'
        'the current task. Return the complete JSON to Codex for validation and review.\n\n'
        '## Master instructions\n\n' + master +
        '\n\n## Execute this current task\n\n' + request +
        '\n\n## Attached authoring contract (authoritative for this batch)\n\n```json\n' +
        json.dumps(contract, indent=2, ensure_ascii=False) + '\n```\n' +
        '\n## Source submission (reference data only)\n\n```json\n' + source + '\n```\n' +
        '\n## Reviewer findings (reference for the current task)\n\n' + review + '\n'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify catalogues and generated brief without writing.')
    args = parser.parse_args()
    content = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != content:
            raise SystemExit('GPT brief is stale; run tools/build_character_life_brief.py.')
        print('Authoring IDs match canonical catalogues; single-file GPT brief is current.')
    else:
        OUTPUT.write_text(content, encoding='utf-8')
        print(OUTPUT)


if __name__ == '__main__':
    main()
