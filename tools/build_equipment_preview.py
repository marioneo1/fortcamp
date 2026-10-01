"""Read-only equipment fixture; no player database or live requests."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.game import new_game, public_content
from backend.content import ITEMS

state=new_game({'name':'Armory Tester'})
state['inventory']=[{'instance_id':f'preview-{i}','item_id':iid} for i,iid in enumerate(ITEMS)]
state['inventory'].append({'instance_id':'duplicate-knife','item_id':'rusty_knife'})
char=state['characters'][0]
char['status']='incapacitated'
char['equipment']={slot:None for slot in char['equipment']}
char['equipment']['weapon']='preview-0'
payload=json.dumps({'state':state,'content':public_content()},ensure_ascii=True).replace('</','<\\/')
html='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Equipment preview</title></head><body><main style="max-width:1100px;margin:auto;padding:20px"><h1>Equipment & Inventory</h1><section id="armory"></section></main><script type="module">
import '/frontend/src/styles.css'; import '/frontend/src/equipment-ui.css';
import {mountEquipmentBrowser} from '/frontend/src/equipment-ui.js';
const {state,content}=PAYLOAD;window.fixture={state,content};window.equipCalls=[];
function render(){mountEquipmentBrowser(document.querySelector('#armory'),{state,content,character:state.characters[0],editable:c=>['idle','incapacitated'].includes(c.status),onError:e=>{throw e},onEquip:async(slot,id)=>{state.characters[0].equipment[slot]=id;window.equipCalls.push({slot,id});render()}})}render();window.previewReady=true;
</script></body></html>'''.replace('PAYLOAD',payload)
out=ROOT/'staging-ui'/'equipment-icons-v1'/'equipment-preview.html'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(html,encoding='utf-8')
print(out)
