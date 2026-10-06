"""Generate a guide-defined pack once, retain originals, and install checked WAVs.

Run with .venv/Scripts/python.exe tools/generate_sfx_pack.py.
Existing originals are reused: restarting never silently purchases more variants.
"""
import array
import argparse
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import wave

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / 'frontend/public/assets/sfx'


def process(source, destination, ui, melodic=False):
    decoded = source.with_suffix('.decoded.wav')
    channels = 2 if melodic else 1
    subprocess.run([shutil.which('ffmpeg'), '-y', '-v', 'error', '-i', str(source),
                    '-ar', '48000', '-ac', str(channels), '-c:a', 'pcm_s16le', str(decoded)], check=True)
    with wave.open(str(decoded), 'rb') as wav:
        samples = array.array('h', wav.readframes(wav.getnframes()))
    if sys.byteorder != 'little':
        samples.byteswap()
    original_peak = max(abs(s) for s in samples)
    clipped_samples = sum(abs(s) >= 32767 for s in samples)
    if original_peak < 100:
        raise ValueError('Generated audio is effectively silent; retained for review')
    active = [i for i, s in enumerate(samples) if abs(s) > max(20 if melodic else 65, original_peak * (.002 if melodic else .012))]
    first = max(0, active[0] // channels - 240) * channels
    last = min(len(samples) // channels, active[-1] // channels + 4800 if melodic else active[-1] // channels + 2400) * channels
    samples = samples[first:last]
    rms = math.sqrt(sum(s*s for s in samples) / len(samples))
    target_db = -24 if ui else -22 if melodic else -19
    gain = min(10 ** (target_db / 20) * 32768 / rms,
               10 ** (-3 / 20) * 32768 / max(abs(s) for s in samples))
    # Small edge fades suppress edit clicks without softening the central impact.
    frames = len(samples) // channels
    fade = min(144, frames // 4)
    tail_fade = min(1200 if melodic else 144, frames // 4)
    for i in range(len(samples)):
        frame = i // channels
        envelope = min(1, frame / fade, (frames-1-frame) / tail_fade)
        samples[i] = round(samples[i] * gain * envelope)
    # Keep the landing's initial weight; remove the unwanted late accent.
    # Derive from the retained source on every run, never from an edited WAV.
    if destination.stem == 'earthbreaker_land':
        end_frame=min(frames,round(.22*48000))
        # Dry low-frequency impact only: discard the entire later accent.
        # Two one-pole filters soften tonal/treble content; 12 ms ending avoids a click.
        alpha=1-math.exp(-2*math.pi*1000/48000)
        for channel in range(channels):
            low=low2=0.0
            for i in range(channel,end_frame*channels,channels):
                low+=alpha*(samples[i]-low);low2+=alpha*(low-low2)
                frame=i//channels
                edge=min(1,(end_frame-1-frame)/576)
                samples[i]=round(low2*max(0,edge))
        samples=samples[:end_frame*channels]
        frames=end_frame
    peak = max(abs(s) for s in samples)
    final_rms = math.sqrt(sum(s*s for s in samples) / len(samples))
    if sys.byteorder != 'little':
        samples.byteswap()
    with wave.open(str(destination), 'wb') as wav:
        wav.setparams((channels, 2, 48000, 0, 'NONE', 'not compressed'))
        wav.writeframes(samples.tobytes())
    return {'duration_seconds': round(frames/48000, 3), 'channels': channels,
            'peak_dbfs': round(20*math.log10(peak/32768), 2),
            'rms_dbfs': round(20*math.log10(final_rms/32768), 2),
            'gain_db': round(20*math.log10(gain), 2),
            'final_clipped_samples': sum(abs(s) >= 32767 for s in samples),
            'trimmed_leading_seconds': round(first/channels/48000, 3),
            'source_clipped_samples': clipped_samples}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack', choices=['first-pack', 'mission-melodic-v2', 'mission-outcomes-v3', 'action-expansion-v1','combat-impact-v1','fighter-contact-v1','fighter-weight-v1','fighter-earth-boom-v1','melee-families-v1','capture-net-v1','flesh-contact-v1','martial-jobs-v1','rogue-actions-v1'], default='mission-outcomes-v3')
    args = parser.parse_args()
    raw = ROOT / 'staging-sfx' / args.pack
    melodic = args.pack not in {'first-pack','combat-impact-v1','fighter-contact-v1','fighter-weight-v1','fighter-earth-boom-v1','melee-families-v1','capture-net-v1','flesh-contact-v1','martial-jobs-v1','rogue-actions-v1'}
    key = os.getenv('ELEVENLABS_API_KEY') or dotenv_values(ROOT / '.env').get('ELEVENLABS_API_KEY')
    if not key:
        raise SystemExit('ELEVENLABS_API_KEY is not configured')
    if not shutil.which('ffmpeg'):
        raise SystemExit('ffmpeg is required to decode and check audio')
    guide = (ROOT / 'SFX_GENERATION_GUIDE.md').read_text(encoding='utf-8')
    headings = {'first-pack': 'First production pack', 'mission-melodic-v2': 'Modern melodic mission pack', 'mission-outcomes-v3': 'Distinct mission outcomes v3', 'action-expansion-v1': 'Action expansion pack'}
    headings['combat-impact-v1']='Combat impact pack'
    headings['fighter-contact-v1']='Fighter contact pack'
    headings['fighter-weight-v1']='Fighter weight pack'
    headings['fighter-earth-boom-v1']='Fighter crater boom pack'
    headings['melee-families-v1']='Melee weapon families pack'
    headings['capture-net-v1']='Capture net pack'
    headings['flesh-contact-v1']='Flesh contact pack'
    headings['martial-jobs-v1']='Martial Jobs pack'
    headings['rogue-actions-v1']='Rogue action pack'
    section = guide.split('## ' + headings[args.pack])[1].split('\n## ')[0]
    palette_section = section if melodic or args.pack in {'combat-impact-v1','fighter-contact-v1','fighter-weight-v1','fighter-earth-boom-v1','melee-families-v1','capture-net-v1','flesh-contact-v1','martial-jobs-v1','rogue-actions-v1'} else guide
    palette = next(line[2:] for line in palette_section.splitlines() if line.startswith('> '))
    rows = re.findall(r'\| `([a-z_0-9]+\.wav)` \| ([\d.]+) s \| (.*?) \|', section)
    expected_count = {'first-pack': 12, 'mission-melodic-v2': 7, 'mission-outcomes-v3': 4, 'action-expansion-v1': 18,'combat-impact-v1':4,'fighter-contact-v1':1,'fighter-weight-v1':4,'fighter-earth-boom-v1':1,'melee-families-v1':12,'capture-net-v1':3,'flesh-contact-v1':6,'martial-jobs-v1':8,'rogue-actions-v1':4}[args.pack]
    if len(rows) != expected_count:
        raise SystemExit(f'Expected exactly {expected_count} effects')
    raw.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)
    report_path = raw / 'generation_report.json'
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    for filename, duration, description in rows:
        source = raw / filename.replace('.wav', '.mp3')
        prompt = palette + ' ' + description
        if filename.startswith('mission_'):
            prompt = palette.replace('no music, ', '') + ' ' + description
        if len(prompt) > 450:
            raise SystemExit(f'{filename}: prompt exceeds the 450-character API limit; no request made')
        if not source.exists():
            print('Generating ' + filename, flush=True)
            payload = {'text': prompt, 'duration_seconds': float(duration),
                       'prompt_influence': .8 if args.pack == 'mission-outcomes-v3' else .55, 'model_id': 'eleven_text_to_sound_v2', 'loop': False}
            request = urllib.request.Request(
                'https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128',
                data=json.dumps(payload).encode(),
                headers={'xi-api-key': key, 'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(request, timeout=120) as response:
                    audio = response.read()
                    cost = response.headers.get('character-cost')
            except urllib.error.HTTPError as error:
                try:
                    detail = json.loads(error.read()).get('detail', {})
                    status = detail.get('status', 'unknown') if isinstance(detail, dict) else 'validation_error'
                    message = detail.get('message', '') if isinstance(detail, dict) else ''
                    message = str(message).replace(key, '[redacted]')[:600]
                except (ValueError, AttributeError):
                    status, message = 'unknown', ''
                raise SystemExit(f'ElevenLabs HTTP {error.code}: {status}: {message}. Stopped without retrying paid requests')
            except urllib.error.URLError:
                raise SystemExit('Network connection failed; originals already generated remain saved')
            source.write_bytes(audio)
            report[filename] = {'prompt': prompt, 'requested_duration_seconds': float(duration),
                                'billed_character_cost': cost}
            report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        if melodic and (FINAL / filename).exists() and not report.get(filename, {}).get('technical_check'):
            shutil.copy2(FINAL / filename, raw / filename.replace('.wav', '.previous.wav'))
        metrics = process(source, FINAL / filename, filename.startswith('ui_'), melodic)
        report.setdefault(filename, {})['technical_check'] = metrics
        report[filename]['listening_review'] = 'Pending human review; automated metrics cannot judge style or unwanted voices.'
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(filename + ': ' + json.dumps(metrics), flush=True)
    preview_names = ['mission_critical_success_v3.wav', 'mission_success_v3.wav', 'mission_failure_v3.wav', 'mission_critical_failure_v3.wav',
                     'ui_click.wav', 'ui_confirm.wav', 'ui_cancel.wav', 'melee_swing.wav', 'melee_hit_light.wav',
                     'melee_hit_heavy.wav', 'subdue_hit.wav', 'unit_death.wav', 'unit_unconscious.wav', 'guard.wav']
    descriptions = {name: desc for name, _, desc in rows}
    if args.pack not in {'mission-outcomes-v3', 'action-expansion-v1'}:
        preview_names[:4] = ['mission_critical_success.wav', 'mission_success.wav', 'mission_failure.wav', 'mission_critical_failure.wav']
    if args.pack in {'action-expansion-v1','combat-impact-v1','fighter-contact-v1','fighter-weight-v1','fighter-earth-boom-v1','melee-families-v1','capture-net-v1','flesh-contact-v1','martial-jobs-v1','rogue-actions-v1'}:
        preview_names = [name for name, _, _ in rows] + preview_names
    cards = ''.join(f'<article><b>{html.escape(name)}</b><p>{html.escape(descriptions.get(name, "Original action pack"))}</p>'
                    f'<audio controls preload="none" src="{name}?v={args.pack}"></audio></article>' for name in preview_names if (FINAL / name).exists())
    preview = '<!doctype html><meta charset="utf-8"><title>Fortcamp sound pack</title>' + (
        '<style>body{background:#20231e;color:#eee;font:16px system-ui;max-width:850px;margin:40px auto}'
        'article{background:#30372d;padding:18px;margin:12px 0;border-radius:10px}audio{width:100%}</style>'
        f'<h1>Fortcamp · {html.escape(args.pack)}</h1><p>Generated game audio. Listening approval pending.</p>'
        + cards)
    (FINAL / 'preview.html').write_text(preview, encoding='utf-8')
    (FINAL / f'preview-{args.pack}.html').write_text(preview, encoding='utf-8')
    print(f'Installed {len(rows)} WAVs. Preview: /assets/sfx/preview.html', flush=True)
    for filename, _, _ in rows:
        with wave.open(str(FINAL / filename), 'rb') as wav:
            assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (2 if melodic else 1, 2, 48000)
            assert wav.getnframes() > 0
        assert report[filename]['technical_check']['final_clipped_samples'] == 0
    print(f'Verified {len(rows)} nonempty 48 kHz WAVs with no final clipped samples.')
    print('API reported total character-cost: ' + str(sum(float(v.get('billed_character_cost') or 0) for v in report.values())))


if __name__ == '__main__':
    main()
