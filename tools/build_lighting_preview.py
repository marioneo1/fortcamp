"""Two real maps in an offline lighting tester. Never reads player saves."""
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import battle_lab as lab
from backend.auth import Identity
from backend.game import new_game, public_content

state = new_game({'name': 'Lighting Tester', 'starting_role': 'mage'})
identity = Identity(guild_id='preview', user_id='tester', display_name='Tester', guild_admin=True)
catalogue = lab.catalogue()
views = {}
with patch.object(lab, 'settings', SimpleNamespace(environment='dev', game_debug_mode=True, dev_bypass_auth=True)):
    for mission_id in ['goblin_warcamp', 'goblin_captive_cart', 'prison_proof_e', 'tool_shed', 'goblin_pickpockets', 'ruined_well', 'supply_watch']:
        mission = next(m for m in catalogue if m['id'] == mission_id)
        views[mission_id] = lab.start_session(identity, lab.StartRequest(
            mission_id=mission_id, variant_id=mission['variants'][0]['id'], seed='lighting-preview'), state)
        if mission_id in lab.RADIANT_ELIGIBLE:
            for mode in ['bear', 'absent']:
                views[mission_id+'|'+mode] = lab.start_session(identity, lab.StartRequest(
                    mission_id=mission_id, variant_id=mission['variants'][0]['id'], seed='lighting-preview', radiant_mode=mode), state)

source = (ROOT / 'frontend/src/main.js').read_text(encoding='utf-8')
source = source.replace("from './", "from '/frontend/src/").replace("import './", "import '/frontend/src/").replace('import "./', 'import "/frontend/src/')
source = re.sub(r'import \{ DiscordSDK \} from [^;]+;', '', source).replace('\ninit();', '\n// Offline fixture replaces startup.')
source += '\nconst lightFixture=' + json.dumps({'state': state, 'content': public_content(), 'views': views, 'catalogue': {'missions': catalogue, 'characters': state['characters'], 'job_loadouts': lab.public_catalog(), 'starting_jobs': lab.STARTING_ROLES, 'weapons': []}}) + ';\n' + '''
state=lightFixture.state;content=lightFixture.content;pool={event:{id:'general'}};
appConfig={debug_mode:true,dev_bypass_auth:true,environment:'dev'};identity={guild_admin:true};
const originalFetch=window.fetch.bind(window);
window.lightRequests=[];
window.fetch=(url,options={})=>{
 if(String(url)==='/api/debug/battle-lab'){
  if(!options.method)return Promise.resolve(new Response(JSON.stringify(lightFixture.catalogue)));
  const request=JSON.parse(options.body);window.lightRequests.push(request);
  const result=lightFixture.views[request.mission_id+'|'+request.radiant_mode]||lightFixture.views[request.mission_id];
  return result?Promise.resolve(new Response(JSON.stringify(result))):Promise.reject(Error('Map not included in this offline fixture.'));
 }
 return String(url).startsWith('/api/')?Promise.reject(Error('Offline visual tester: no game-server requests.')):originalFetch(url,options);
};
$('#loading').classList.add('hidden');$('#game').classList.remove('hidden');
window.lightingShow=id=>{openLabBattle(structuredClone(lightFixture.views[id]));lightingLab.open();};
window.lightingRedraw=()=>renderBattle(activeBattleView);
window.lightingRegular=()=>{activeBattleLabSessionId=null;renderBattle(activeBattleView);};
const chooser=document.createElement('section');chooser.style='position:fixed;top:12px;right:12px;z-index:241;display:flex;gap:6px';
chooser.innerHTML='<button data-light-scene="goblin_warcamp">Outdoor camp</button><button data-light-scene="tool_shed">Tool shed</button>';
document.body.append(chooser);chooser.querySelectorAll('button').forEach(b=>b.onclick=()=>window.lightingShow(b.dataset.lightScene));
window.lightingShow('goblin_warcamp');window.lightingReady=true;
'''
folder = ROOT / 'staging-ui/lighting-v1'
folder.mkdir(parents=True, exist_ok=True)
(folder / 'preview.js').write_text(source, encoding='utf-8')
page = (ROOT / 'frontend/index.html').read_text(encoding='utf-8')
page = re.sub(r'<script type="module" src="/src/main.js[^>]+></script>', '<script type="module" src="/staging-ui/lighting-v1/preview.js"></script>', page)
(folder / 'preview.html').write_text(page, encoding='utf-8')
print(folder / 'preview.html')
