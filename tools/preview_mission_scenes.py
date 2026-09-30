import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.game import new_game,analyze_mission,public_content
from backend.content import MISSION_TEMPLATES
from backend.mission_decisions import decision_view,initial_scene
state=new_game({'name':'Aya Quill','attributes':{'str':7,'dex':8,'int':9,'agi':7,'vit':6,'luk':7}})
for i in range(2):
    from copy import deepcopy
    char=deepcopy(state['characters'][0]);char.update(id=f'ally{i}',name=['Elma','Mog Quickhand'][i]);state['characters'].append(char)
template=MISSION_TEMPLATES['black_banner_ledger'];analysis=analyze_mission(state,template,[c['id'] for c in state['characters']]);analysis['scene']=initial_scene()
scene=decision_view(state,template,analysis)
html='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mission choices preview</title><link rel="stylesheet" href="../frontend/src/styles.css"></head><body><div class="modal"><div class="modal-card"><div id="scene"></div></div></div><script type="module">
import {mountDecisionScene} from '../frontend/src/mission-scene-ui.js';
const esc=(v='')=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const title=s=>s.replaceAll('_',' ').replace(/\\b\\w/g,m=>m.toUpperCase());
const scene=SCENE;
mountDecisionScene(document.querySelector('#scene'),{name:'The Black-Banner Ledger'},scene,{esc,title,onChoose:async payload=>{if(payload.node_id!=='case'||payload.revision!==0)throw Error('Invalid payload')}});
if(document.querySelectorAll('[data-scene-choice]').length!==3)throw Error('Missing authored choices');
if([...document.querySelectorAll('.scene-odds')].some(el=>!el.textContent.includes('Critical Failure')))throw Error('Missing visible odds');
document.title='SCENE QA PASS';
</script></body></html>'''.replace('SCENE;',json.dumps(scene,ensure_ascii=False)+';')
Path('tools/mission-scene-preview.html').write_text(html,encoding='utf-8')
