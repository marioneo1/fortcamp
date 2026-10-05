"""Build a browser QA fixture using real lab metadata/maps; never reads player saves."""
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import battle_lab as lab
from backend.auth import Identity
from backend.game import new_game

subprocess.run([sys.executable, str(ROOT / 'tools/build_gear_battle_preview.py')], check=True)
state = new_game({'name': 'Lab UI Tester', 'starting_role': 'mage'})
identity = Identity(guild_id='preview', user_id='tester', display_name='Tester', guild_admin=True)
missions = lab.catalogue()
views = {}
with patch.object(lab, 'settings', SimpleNamespace(environment='dev', game_debug_mode=True, dev_bypass_auth=True)):
    for mid in ['goblin_warcamp', 'goblin_captive_cart', 'goblin_smoke_signals', 'hedgerow_watch_defense','tool_shed','workshop_intruders','goblin_armory',*[m['id'] for m in missions if m['id'].startswith('material_')]]:
        for variant in next(m for m in missions if m['id'] == mid)['variants']:
            views[mid + '|' + variant['id']] = lab.start_session(
                identity, lab.StartRequest(mission_id=mid, variant_id=variant['id']), state)
            for preset in variant.get('layout_presets',[]):
                views[mid+'|'+variant['id']+'|'+preset['seed']]=lab.start_session(
                    identity,lab.StartRequest(mission_id=mid,variant_id=variant['id'],seed=preset['seed']),state)
source = (ROOT / 'staging-ui/equipment-icons-v1/battle-preview.js').read_text(encoding='utf-8')
source += '\nconst labFixture=' + json.dumps({'catalogue': {'missions': missions, 'characters': state['characters'],
                                                           'job_loadouts': lab.public_catalog(), 'starting_jobs': lab.STARTING_ROLES},
                                             'views': views}, ensure_ascii=True) + ';\n' + '''
const labOriginalFetch=window.fetch;
window.labRequests=[];
window.fetch=(url,options={})=>{
 if(String(url).startsWith('/api/debug/battle-lab')){
  window.labRequests.push({url,body:options.body?JSON.parse(options.body):null});
  if(!options.method)return Promise.resolve(new Response(JSON.stringify(labFixture.catalogue)));
  const body=JSON.parse(options.body||'{}');
  const view=structuredClone(labFixture.views[body.mission_id+'|'+body.variant_id+'|'+body.seed]||labFixture.views[body.mission_id+'|'+body.variant_id]);
  if(!view)return Promise.reject(Error('Unsupported preview request'));
  view.seed=body.seed;return Promise.resolve(new Response(JSON.stringify(view)));
 }
 return labOriginalFetch(url,options);
};
appConfig={debug_mode:true,dev_bypass_auth:true};identity={guild_admin:true};
$('#mission-modal').classList.add('hidden');activeBattleView=null;
$('#debug-pool-controls').classList.remove('hidden');
$('#debug-battle-lab').onclick=()=>battleLab.open();
window.labOpen=()=>battleLab.open();window.labCurrentBattle=()=>activeBattleView;window.labFixtureReady=true;
'''
destination = ROOT / 'staging-ui/battle-lab'
destination.mkdir(parents=True, exist_ok=True)
(destination / 'preview.js').write_text(source, encoding='utf-8')
page = (ROOT / 'staging-ui/equipment-icons-v1/battle-preview.html').read_text(encoding='utf-8').replace(
    '/staging-ui/equipment-icons-v1/battle-preview.js', '/staging-ui/battle-lab/preview.js')
(destination / 'preview.html').write_text(page, encoding='utf-8')
print('Built isolated Battle Lab browser fixture')
