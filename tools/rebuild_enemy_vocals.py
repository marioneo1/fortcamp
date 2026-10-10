"""Rebuild the approved voice pack/tester offline, without paid generation."""
import json
from pathlib import Path
from generate_sfx_pack import process

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'staging-sfx/enemy-vocals-approved'
SFX = ROOT / 'frontend/public/assets/sfx'


def main():
    manifest = json.loads((SOURCES / 'manifest.json').read_text(encoding='utf-8'))
    cards = []
    for clip in manifest['clips']:
        destination = SFX / clip['file']
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = SOURCES / clip['source_file']
        if clip.get('approved_wav'):
            # Exact edited/approved bytes are retained, never reprocessed.
            destination.write_bytes((SOURCES / clip['approved_wav']).read_bytes())
        else:
            process(source, destination, False)
        cards.append({'name': clip['name'], 'status': 'Installed approved pack',
                      'file': '../' + clip['file']})
    folder = SFX / 'voice-tester'
    folder.mkdir(parents=True, exist_ok=True)
    template = (ROOT / 'tools/vocal_review_template.html').read_text(encoding='utf-8')
    template = template.replace('This pack is for review, not installed in combat.', 'These are the installed combat voices. Female attacks and Goblin female hurt/death use the approved revisions.')
    (folder / 'preview.html').write_text(template.replace('__CATALOGUE__', json.dumps(cards)), encoding='utf-8')
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Rebuilt {len(cards)} installed clips and one tester; no API calls.')


if __name__ == '__main__':
    main()
