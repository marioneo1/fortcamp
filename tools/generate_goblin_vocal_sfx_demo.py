"""Six wordless Goblin auditions, retained in staging and never installed."""
import json
import os
import subprocess
import urllib.request
import urllib.error
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'staging-sfx' / 'goblin-vocal-sfx-demo-v1'
IDENTITIES = {
    'male': 'Adult male goblin, small wiry creature: medium-high pitch, gravelly nasal rasp, guttural scratchy throat, feral breath.',
    'female': 'Adult female goblin, small wiry creature: higher-mid pitch, sharp nasal rasp, smoky scratchy throat, feral breath.',
}
EVENTS = {
    'attack': ('One forceful lunging attack grunt with a snarling growl. Abrupt energetic onset, short breathy finish.', 1.1),
    'hurt': ('One involuntary pain yelp, raspy squeal cracking into a guttural grunt. Brief sharp pain, not a long scream.', 1.3),
    'death': ('One strained dying groan descending into a weak rattling exhalation, then silence. Compact, not theatrical.', 2.3),
}
EXCLUSIONS = (' Dry isolated vocal, exactly one event. No words or speech. No music, ambience, weapons, impacts, '
              'footsteps, body fall or reverb. Not a child, cartoon or giant monster.')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    key = os.getenv('ELEVENLABS_API_KEY') or dotenv_values(ROOT / '.env').get('ELEVENLABS_API_KEY')
    if not key:
        raise SystemExit('ElevenLabs SFX key is not configured')
    jobs = [(gender, event) for gender in IDENTITIES for event in EVENTS]
    def generate(job):
        gender, event = job
        prompt = IDENTITIES[gender] + ' ' + EVENTS[event][0] + EXCLUSIONS
        if len(prompt) > 450:
            raise ValueError('SFX prompt exceeds 450 characters')
        payload = {'text': prompt, 'duration_seconds': EVENTS[event][1],
                   'prompt_influence': .75, 'model_id': 'eleven_text_to_sound_v2', 'loop': False}
        file = OUT / f'goblin_{gender}_{event}.mp3'
        if not file.exists():
            request = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128',
                data=json.dumps(payload).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    file.write_bytes(response.read())
            except urllib.error.HTTPError as exc:
                raise RuntimeError(f'{gender} {event}: HTTP {exc.code}: {exc.read().decode()[:600]}') from None
        (OUT / f'{file.stem}.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
        print(f'{gender} {event}: saved', flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(generate, jobs))
    for gender in IDENTITIES:
        combined = bytearray()
        for event in EVENTS:
            source = OUT / f'goblin_{gender}_{event}.mp3'
            decoded = OUT / f'{source.stem}.wav'
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source),
                            '-af', 'volume=0.7', '-ac', '1', '-ar', '44100', '-c:a', 'pcm_s16le', str(decoded)], check=True)
            with wave.open(str(decoded), 'rb') as clip:
                combined.extend(clip.readframes(clip.getnframes()))
            combined.extend(bytes(int(44100 * .65) * 2))
        wav = OUT / f'goblin_{gender}_demo.wav'
        with wave.open(str(wav), 'wb') as clip:
            clip.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            clip.writeframes(combined)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(wav),
                        '-b:a', '64k', str(OUT / f'goblin_{gender}_demo.mp3')], check=True)
    cards = ''.join('<section><h2>' + gender.title() + ' Goblin</h2>' +
                    ''.join(f'<p>{event.title()}</p><audio controls preload="none" src="goblin_{gender}_{event}.mp3"></audio>'
                            for event in EVENTS) + '</section>' for gender in IDENTITIES)
    (OUT / 'preview.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Wordless Goblin auditions</title><style>body{background:#171a1d;color:#eee;font:17px system-ui;max-width:900px;margin:30px auto;padding:20px}'
        'main{display:flex;gap:30px;flex-wrap:wrap}section{padding:20px;background:#252b30;border-radius:12px}audio{width:min(320px,75vw)}</style>'
        '<h1>Wordless Goblin auditions</h1><p>Attack, hurt and death. SFX demos only; not installed in game.</p><main>' + cards + '</main>', encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps({'status': 'awaiting listening review; not installed',
        'method': 'ElevenLabs SFX; shared description per gender, no fixed voice identity guarantee',
        'sequence': list(EVENTS), 'files': [f'goblin_{g}_{e}.mp3' for g, e in jobs]}, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
