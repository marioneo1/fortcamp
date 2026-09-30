"""Generate a small regional ambience pack once; uncertain requests require manual review.
No music generation. Sources and request receipts stay local. Use --process-only to avoid API calls.
"""
import argparse, json, os, shutil, subprocess, urllib.request
from pathlib import Path
from dotenv import dotenv_values
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'staging-sfx/event-ambience-v1'
FINAL=ROOT/'frontend/public/assets/sfx/ambient'
PALETTE='Fantasy game environmental sound effect, distant perspective, warm softened treble, quiet natural detail, no music or instruments, no intelligible words, no screams or jump scares. '
CLIPS=[
('guild_chatter',16,'Quiet friendly guild hall: distant overlapping low human conversational murmurs without discernible words, an occasional soft chuckle, mugs set on wooden tables, paper rustling and gentle chair movement. Cozy, subdued, not a noisy tavern crowd.'),
('goblin_chatter',8,'A small goblin patrol in the distance, brief low raspy creature chatter and chuckles, shuffling feet and leather creaks. Not human conversation, not cute squeaks.'),
('goblin_camp',8,'Distant rough camp activity: several uneven marching footsteps, leather and wooden equipment creaks, a brief low guttural goblin grunt. No battle impacts.'),
('ashen_procession',10,'A distant slow procession: dragging feet on gravel, creaking old wood, a little dry ash moving in the wind. Subtle eerie environmental texture, no voices.'),
('arcane_disturbance',10,'An unstable magical disturbance at a distant ruin: low resonant air vibration, a brief soft electrical crackle, then settling wind. No bright bell, musical notes or loud discharge.'),
('beast_call',8,'One distant large forest creature gives a low throaty animal call, answered very faintly farther away. Leaves rustle. Natural and imposing, no piercing roar.'),
('beast_passage',8,'A large unseen creature moves through woodland in the distance, heavy muted footsteps, bending branches and rustling leaves. No crashes or growling attack.'),
('starfall_machine',12,'Distant damaged alien machinery at an impact site: low irregular mechanical resonance, soft spatial warping and intermittent muted metal stress creaks. Unsettling nonmusical texture, no alarms, laser shots or shrill frequencies.'),
]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--process-only',action='store_true');args=parser.parse_args()
    SOURCE.mkdir(parents=True,exist_ok=True);FINAL.mkdir(parents=True,exist_ok=True)
    receipt=SOURCE/'generation_report.json';report=json.loads(receipt.read_text()) if receipt.exists() else {}
    key=os.getenv('ELEVENLABS_API_KEY') or dotenv_values(ROOT/'.env').get('ELEVENLABS_API_KEY')
    ffmpeg=shutil.which('ffmpeg');probe=shutil.which('ffprobe')
    if not ffmpeg or not probe:raise SystemExit('ffmpeg and ffprobe required before generation')
    def save():receipt.write_text(json.dumps(report,indent=2),encoding='utf-8')
    for identifier,seconds,description in CLIPS:
        source=SOURCE/(identifier+'.mp3');target=FINAL/(identifier+'.mp3');prompt=PALETTE+description
        if not source.exists():
            if args.process_only:raise SystemExit('Missing source: '+identifier)
            if not key:raise SystemExit('ELEVENLABS_API_KEY is not configured')
            if report.get(identifier,{}).get('status')=='request_pending':raise SystemExit('Uncertain previous paid request for '+identifier+'; review receipt before retrying')
            if len(prompt)>450:raise SystemExit('Prompt exceeds limit: '+identifier)
            report[identifier]={'prompt':prompt,'duration_seconds':seconds,'status':'request_pending'};save()
            print('Generating '+identifier,flush=True)
            request=urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128',data=json.dumps({'text':prompt,'duration_seconds':seconds,'prompt_influence':.65,'model_id':'eleven_text_to_sound_v2','loop':False}).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(request,timeout=120) as response:
                    body=response.read();cost=response.headers.get('character-cost')
            except Exception as error:
                raise SystemExit('Generation stopped for '+identifier+' ('+type(error).__name__+'); no automatic retry. Review the pending receipt.') from None
            source.write_bytes(body);report[identifier].update(status='source_saved',billed_character_cost=cost);save()
        if not target.exists() or not report.get(identifier,{}).get('technical_check'):
            measured_source=subprocess.check_output([ffmpeg,'-i',str(source),'-af','loudnorm=I=-26:TP=-5:LRA=8:print_format=json','-f','null','-'],stderr=subprocess.STDOUT,text=True)
            source_meter=json.loads(measured_source[measured_source.rfind('{'):measured_source.rfind('}')+1])
            # Very quiet generated murmurs need to enter the loudness meter's gating range first.
            boost='volume=20dB,' if float(source_meter['input_i']) < -45 else ''
            subprocess.run([ffmpeg,'-y','-v','error','-i',str(source),'-af',boost+f'lowpass=f=6500,loudnorm=I=-26:TP=-5:LRA=8,afade=t=in:d=0.6,afade=t=out:st={seconds-1}:d=1','-ar','48000','-ac','2','-b:a','160k',str(target)],check=True)
        measured=subprocess.check_output([ffmpeg,'-i',str(target),'-af','loudnorm=I=-26:TP=-5:LRA=8:print_format=json','-f','null','-'],stderr=subprocess.STDOUT,text=True)
        meter=json.loads(measured[measured.rfind('{'):measured.rfind('}')+1])
        duration=float(subprocess.check_output([probe,'-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(target)],text=True))
        if duration<2 or float(meter['input_tp'])> -3 or float(meter['input_i'])< -40:raise SystemExit('Unexpected audio levels: '+identifier)
        report.setdefault(identifier,{}).update(status='installed',technical_check={'duration':duration,'loudness_lufs':meter['input_i'],'peak_dbtp':meter['input_tp']},listening_review='Pending human review');save()
        print('Installed '+identifier,flush=True)
    (FINAL/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    cards=''.join('<p>'+i+'</p><audio controls preload="none" src="'+i+'.mp3"></audio>' for i,_,_ in CLIPS)
    page='<html><meta charset="utf-8"><title>Fortcamp ambience</title><style>body{background:#20231e;color:#eee;font:16px system-ui;max-width:750px;margin:40px auto}audio{width:100%}</style><h1>Regional ambience</h1><p>Quiet environmental accents; review with music playing. Originals are preserved.</p>'+cards+'<script>const clips=[...document.querySelectorAll("audio")];clips.forEach(a=>{a.volume=.35;a.addEventListener("play",()=>clips.forEach(b=>{if(a!==b)b.pause()}))});</script></html>'
    (FINAL/'preview.html').write_text(page,encoding='utf-8')
    for i,_,_ in CLIPS:shutil.copy2(FINAL/(i+'.mp3'),SOURCE/(i+'_preview.mp3'))
    (SOURCE/'LISTEN.html').write_text(page.replace('.mp3','_preview.mp3'),encoding='utf-8')
    print('Installed '+str(len(CLIPS))+' ambience clips; total API-reported cost: '+str(sum(float(v.get('billed_character_cost') or 0) for v in report.values())),flush=True)
if __name__=='__main__':main()
