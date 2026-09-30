"""Generate four authorized guild-board candidates, preserve originals, and build a listening page.

Run once with .venv/Scripts/python.exe tools/generate_music_candidates.py.
Saved originals are reused. An interrupted paid request is never retried automatically.
Use --process-only to rebuild previews without contacting ElevenLabs.
"""
import argparse
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.error
import urllib.request

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'staging-music/guild-board-candidates-v1'
FINAL = ROOT / 'frontend/public/assets/music/guild-board-candidates-v1'
COMMON = (
    'Original instrumental background music for a modern fantasy guild-management RPG. '
    'Warm, inviting, quietly adventurous, comfortable for long reading sessions. '
    'Use felt piano, softly plucked acoustic strings, mid-register clarinet, warm low strings, '
    'rounded bass and restrained soft hand percussion. Soft transients and controlled warm treble. '
    'A memorable short melody returns with small variations and generous breathing space. '
    'No piercing high notes, bright bell leads, shrill piccolo, harsh cymbals, chiptune, EDM drops, '
    'vocals, speech, humming or choir. Keep all melodic leads in the low or middle register. '
    'Maintain a repeating gameplay arrangement with subtle development, no dramatic song arc. '
    'Begin already in the groove, no long intro or silence. The final phrase should return naturally '
    'to the first phrase at the same harmony, pulse and instrumentation, no final cadence or fade-out. '
    'Two minutes. Original composition, do not imitate any existing soundtrack. '
)
CANDIDATES = [
    {'id':'01_lanternlight','name':'Lanternlight','description':'Gentle piano melody, soft plucked strings, and a relaxed straight groove.',
     'direction':'92 BPM, gentle 4/4 pulse. Felt piano carries a simple singable four-bar motif; clarinet answers sparingly. Warm major harmony with a little wistfulness. Intimate, welcoming, lightly buoyant. Percussion stays unobtrusive.'},
    {'id':'02_guildhall_shuffle','name':'Guildhall Shuffle','description':'A playful plucked-string hook with a light, relaxed swing.',
     'direction':'94 BPM with very gentle swing. Soft lute-like plucked strings carry a catchy rhythmic motif, felt piano adds warm chords, rounded acoustic bass supplies an easy walking groove. Subtle brush-like hand percussion. Playful guild bustle, elegant rather than comedic, never busy or frantic.'},
    {'id':'03_roads_waiting','name':'Roads Waiting','description':'Mellow clarinet and piano, with a more lyrical sense of adventure.',
     'direction':'88 BPM, steady understated 4/4. Mellow mid-low clarinet carries a lyrical memorable melody over felt piano and warm legato low strings. Rounded bass and soft muted drums maintain forward motion. A hopeful journey waiting beyond the guild doors, calm and quietly curious, no epic crescendo.'},
    {'id':'04_mapmakers_clock','name':"Mapmaker's Clock",'description':'A repeating plucked pattern and piano hook with a little mystery.',
     'direction':'96 BPM, gentle 4/4. Muted plucked strings repeat a satisfying rhythmic ostinato while felt piano develops a short distinct melodic hook. Mid-low clarinet gives occasional responses. Warm modal harmony adds a hint of mystery without menace. Soft wooden hand percussion and rounded bass, polished and quietly addictive, no ticking sound effects.'},
]


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temporary.replace(path)


def ffmpeg(*arguments):
    result = subprocess.run([shutil.which('ffmpeg'), '-hide_banner', '-nostdin', '-y', *map(str, arguments)],
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError('Audio processing failed: ' + result.stderr[-1200:])
    return result.stderr


def meter(path):
    output = ffmpeg('-i', path, '-af', 'loudnorm=I=-20:TP=-2:LRA=9:print_format=json', '-f', 'null', '-')
    return json.loads(output[output.rfind('{'):output.rfind('}')+1])


def duration(path):
    result = subprocess.run([shutil.which('ffprobe'), '-v', 'error', '-show_entries', 'format=duration',
                             '-of', 'default=noprint_wrappers=1:nokey=1', str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def process(source, candidate):
    # Match integrated loudness in two passes; preserve the source exactly as received.
    measured = meter(source)
    normalization = (f"loudnorm=I=-20:TP=-2:LRA=9:measured_I={measured['input_i']}:"
                     f"measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:"
                     f"measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true")
    listen = FINAL / (candidate['id'] + '.mp3')
    ffmpeg('-v', 'error', '-i', source, '-af', normalization, '-ar', '48000', '-ac', '2', '-b:a', '192k', listen)
    seconds = duration(listen)
    if seconds < 90:
        raise ValueError('Unexpectedly short candidate; original kept, no further purchases made.')
    # A cyclic crossfade smooths the technical seam; it cannot certify musical phrasing.
    crossfade = 1.5
    seam = (f'[0:a]asplit=3[tail][head][body];'
            f'[tail]atrim=start={seconds-crossfade},asetpts=PTS-STARTPTS[t];'
            f'[head]atrim=end={crossfade},asetpts=PTS-STARTPTS[h];'
            f'[t][h]acrossfade=d={crossfade}:c1=tri:c2=tri[join];'
            f'[body]atrim=start={crossfade}:end={seconds-crossfade},asetpts=PTS-STARTPTS[b];'
            '[join][b]concat=n=2:v=0:a=1[out]')
    loop = FINAL / (candidate['id'] + '_loop_preview.mp3')
    ffmpeg('-v', 'error', '-i', listen, '-filter_complex', seam, '-map', '[out]', '-ar', '48000', '-ac', '2', '-b:a', '192k', loop)
    final_meter = meter(listen)
    if float(final_meter['input_tp']) > -.5:
        raise ValueError('Preview true peak is too high; originals preserved.')
    return {'source_duration_seconds':round(duration(source),3), 'preview_duration_seconds':round(seconds,3),
            'loop_preview_duration_seconds':round(duration(loop),3), 'integrated_lufs':final_meter['input_i'],
            'true_peak_dbfs':final_meter['input_tp'], 'loudness_range_lu':final_meter['input_lra'],
            'loop_crossfade_seconds':crossfade, 'listening_review':'Pending user listening; musical seam and treble comfort are not automatically certified.'}


def preview(report):
    completed = [c for c in CANDIDATES if (FINAL / (c['id']+'.mp3')).exists()]
    cards = ''.join(f'''<article><div class="eyebrow">CANDIDATE {index+1:02}</div><h2>{html.escape(c['name'])}</h2>
<p>{html.escape(c['description'])}</p><audio controls preload="none" src="{c['id']}.mp3"></audio>
<label><input type="checkbox" data-repeat> Repeat original</label><details><summary>Loop-seam trial</summary>
<p>The loop trial blends the end into the start. Judge whether the musical transition works for you.</p>
<audio controls loop preload="none" src="{c['id']}_loop_preview.mp3"></audio></details>
<div class="downloads"><a href="{c['id']}.mp3" download>Download candidate</a><a href="{c['id']}_loop_preview.mp3" download>Download loop trial</a></div></article>'''
                    for index,c in enumerate(completed))
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fortcamp · Guild-board music candidates</title><style>
:root{color-scheme:dark}body{background:#121812;color:#eae9df;font:15px system-ui;margin:0;padding:24px}main{max-width:1080px;margin:auto}h1{margin-bottom:12px}.muted,p{color:#b6bfae;line-height:1.65}.eyebrow{color:#d7b66a;font-size:11px;letter-spacing:.15em}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}article{padding:22px;border:1px solid #46513e;background:#1c251c;border-radius:16px}h2{margin:8px 0}audio{width:100%;margin:10px 0}label{display:block;margin:8px 0}details{border-top:1px solid #46513e;margin-top:18px;padding-top:15px}summary{cursor:pointer}.downloads{display:flex;gap:16px;flex-wrap:wrap;margin-top:20px}a{color:#e0c27e}button{padding:9px 14px;background:#333e2d;color:inherit;border:1px solid #647051;border-radius:8px;cursor:pointer}.controls{display:flex;align-items:center;gap:18px;margin:20px 0}input[type=range]{accent-color:#d7b66a}@media(max-width:720px){.grid{grid-template-columns:1fr}}
</style><main><div class="eyebrow">FORTCAMP MUSIC · GUILD BOARD</div><h1>Four directions, one warm palette</h1>
<p>Compare the melody, listening comfort and repetition. You can keep any number of candidates. These are auditions, not a change to the game's default music.</p>
<div class="controls"><label>Preview volume <input id="volume" aria-label="Preview volume" type="range" min="0" max="100" value="55"></label><button id="stop">Stop all</button></div><div class="grid">''' + cards + '''</div></main><script>
const tracks=[...document.querySelectorAll('audio')],slider=document.querySelector('#volume');
const apply=()=>tracks.forEach(a=>a.volume=Number(slider.value)/100);apply();slider.oninput=apply;
tracks.forEach(a=>a.addEventListener('play',()=>tracks.forEach(other=>{if(other!==a)other.pause()})));
document.querySelector('#stop').onclick=()=>tracks.forEach(a=>a.pause());
document.querySelectorAll('[data-repeat]').forEach(box=>box.onchange=()=>box.closest('article').querySelector('audio').loop=box.checked);
</script></html>'''
    (FINAL / 'preview.html').write_text(page, encoding='utf-8')
    # A directly openable copy beside the source material.
    local_page = page
    for c in completed:
        for suffix in ('.mp3','_loop_preview.mp3'):
            name=c['id']+suffix
            shutil.copy2(FINAL/name,SOURCE/name)
    (SOURCE / 'LISTEN.html').write_text(local_page, encoding='utf-8')
    write_json(FINAL / 'manifest.json', {'pack':'guild-board-candidates-v1','status':'audition, not selected',
                'candidates':[{**c,'technical_check':report[c['id']].get('technical_check')} for c in completed]})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--process-only',action='store_true')
    args=parser.parse_args()
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise SystemExit('ffmpeg and ffprobe are required before any paid request.')
    key=os.getenv('ELEVENLABS_MUSIC_IMAGE_KEY') or dotenv_values(ROOT / '.env').get('ELEVENLABS_MUSIC_IMAGE_KEY')
    if not key and not args.process_only:
        raise SystemExit('ELEVENLABS_MUSIC_IMAGE_KEY is not configured.')
    SOURCE.mkdir(parents=True,exist_ok=True);FINAL.mkdir(parents=True,exist_ok=True)
    path=SOURCE/'generation_report.json'
    report=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    for candidate in CANDIDATES:
        identifier=candidate['id'];source=SOURCE/(identifier+'_original.mp3')
        if not source.exists():
            if args.process_only:continue
            previous=report.get(identifier,{})
            if previous.get('request_state') in {'started','uncertain','failed'}:
                raise SystemExit(identifier+': previous request needs inspection; no automatic paid retry.')
            prompt=COMMON+candidate['direction']
            payload={'prompt':prompt,'music_length_ms':120000,'force_instrumental':True,'model_id':'music_v2_5'}
            report[identifier]={**candidate,'request':payload,'requested_at':datetime.now(timezone.utc).isoformat(),'request_state':'started'}
            write_json(path,report)
            print('Generating '+identifier+' (120 seconds, instrumental)',flush=True)
            request=urllib.request.Request('https://api.elevenlabs.io/v1/music?output_format=auto',
                data=json.dumps(payload).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(request,timeout=360) as response:
                    temporary=source.with_suffix('.mp3.partial')
                    with temporary.open('wb') as out:
                        shutil.copyfileobj(response,out)
                    if temporary.stat().st_size<10000:raise ValueError('Response was unexpectedly small.')
                    temporary.replace(source)
                    report[identifier].update(request_state='received',song_id=response.headers.get('song-id'),billed_character_cost=response.headers.get('character-cost'))
                    write_json(path,report)
            except urllib.error.HTTPError as error:
                raw=error.read().decode('utf-8',errors='replace').replace(key,'[redacted]')[:800]
                report[identifier].update(request_state='failed',http_status=error.code,error=raw);write_json(path,report)
                raise SystemExit(f'ElevenLabs HTTP {error.code}: {raw}. Stopped without retrying paid requests.')
            except Exception as error:
                report[identifier]['request_state']='uncertain';write_json(path,report)
                raise SystemExit(f'{identifier}: request interrupted ({type(error).__name__}). No automatic retry; any partial download is retained.')
        report.setdefault(identifier,{**candidate})['technical_check']=process(source,candidate)
        write_json(path,report);preview(report)
        print(identifier+': '+json.dumps(report[identifier]['technical_check']),flush=True)
    print('Listening page: '+str(SOURCE/'LISTEN.html'),flush=True)


if __name__=='__main__':main()
