"""Generate one reusable black-powder bolt impact; retained originals avoid rebilling."""
from pathlib import Path
import json,urllib.request,os
from dotenv import dotenv_values
from generate_sfx_pack import process,ROOT,FINAL
def generate(name,prompt,duration,pack):
 folder=ROOT/'staging-sfx'/pack;folder.mkdir(parents=True,exist_ok=True)
 source=folder/(name+'.mp3')
 if not source.exists():
  key=os.getenv('ELEVENLABS_API_KEY') or dotenv_values(ROOT/'.env').get('ELEVENLABS_API_KEY')
  if not key:raise SystemExit('ElevenLabs key missing')
  req=urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128',data=json.dumps({'text':prompt,'duration_seconds':duration,'prompt_influence':.65,'model_id':'eleven_text_to_sound_v2','loop':False}).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=120) as response:source.write_bytes(response.read())
 metrics=process(source,FINAL/(name+'.wav'),False)
 (folder/'generation_report.json').write_text(json.dumps({'prompt':prompt,'metrics':metrics},indent=2),encoding='utf-8')
 print('Installed '+name+'; original retained.')
def main():
 generate('engineer_bolt_explosion','Single close fantasy black-powder explosive arrow impact: quick solid wooden bolt thud immediately followed by a weighty low boom and brief crunchy stone, wood and iron debris. Punchy grounded cannonball blast, short dry decay. No music, voices, whistling, metallic ringing, shrill tail or magic.',1.2,'engineer-impact-v2')
 generate('engineer_rapid_assembly','Single short fantasy engineer preparation cue: fast mechanical ratchet winding, three crisp wooden tool and iron latch clicks accelerating into a satisfying sturdy locking clack, tiny dry sparks. Clear energetic ready confirmation, compact close sound. No voices, music, magic, explosion, ringing or shrill whine.',.9,'engineer-preparation-v1')
if __name__=='__main__':main()
