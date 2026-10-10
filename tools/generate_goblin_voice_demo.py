"""Generate retained Goblin voice-design demos only; never install or batch voices."""
import base64
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'staging-sfx' / 'goblin-voice-demo-v1'
OUT.mkdir(parents=True, exist_ok=True)
key = os.environ.get('ELEVENLABS_VOICES_KEY') or dotenv_values(ROOT / '.env').get('ELEVENLABS_VOICES_KEY')
if not key:
    raise SystemExit('ELEVENLABS_VOICES_KEY is not configured')

TEXT = ('[sly] Keep your hands off my loot. You want a fight? Come closer, then! '
        '[angry] Hah! Hyah! [grunts] Ngh! [pained] Argh! [strained] Ugh... ahh...')
DESCRIPTIONS = {
    'male': 'An adult male fantasy goblin bandit with a compact wiry body: medium-high pitch, gravelly nasal rasp, scratchy throaty growl, sharp consonants and a sly sneering delivery. Clearly a small rough creature, not a child, not a cartoon squeak, not a deep human warrior. Agile and scrappy. English is intelligible. Expressive close-mic dry game voice acting, suitable for short effort grunts, pain cries and dying gasps. No music, reverb or background sounds.',
    'female': 'An adult female fantasy goblin bandit with a compact wiry body: high-mid pitch, smoky scratchy nasal rasp, slightly guttural growl, sharp consonants and a cunning fierce delivery. Clearly female and a small rough creature, not a child, not a fairy, not a cartoon squeak. Agile and scrappy. English is intelligible. Expressive close-mic dry game voice acting, suitable for short effort grunts, pain cries and dying gasps. No music, reverb or background sounds.',
}

def generate(gender):
    manifest = OUT / f'{gender}.json'
    if manifest.exists():
        print(f'{gender}: retained previews reused', flush=True)
        return
    payload = dict(voice_description=DESCRIPTIONS[gender], model_id='eleven_ttv_v3',
                   text=TEXT, seed=61009 if gender == 'male' else 61010,
                   guidance_scale=5, loudness=0.1)
    request = urllib.request.Request('https://api.elevenlabs.io/v1/text-to-voice/design?output_format=mp3_44100_128',
                                     data=json.dumps(payload).encode(),
                                     headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.load(response)
    previews = []
    for index, preview in enumerate(data['previews'], 1):
        file = OUT / f'goblin_{gender}_preview_{index}.mp3'
        file.write_bytes(base64.b64decode(preview['audio_base_64']))
        previews.append({k: v for k, v in preview.items() if k != 'audio_base_64'} | {'file': file.name})
    manifest.write_text(json.dumps({'status': 'awaiting user listening review; not installed',
                                    'request': payload, 'previews': previews}, indent=2), encoding='utf-8')
    print(f'{gender}: {len(previews)} previews saved', flush=True)

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(generate, DESCRIPTIONS))
