"""Build an isolated fixture using the actual battle UI, with no database requests."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.content import ITEMS
from backend.game import new_game, public_content
from backend.combat import create_goblin_warcamp_battle, battle_view

state = new_game({'name': 'Gear UI Tester'})
for iid in ['mooncord_sling', 'meridian_field_projector', 'rescue_gloves', 'ferrymans_boots']:
    state['inventory'].append({'instance_id': iid, 'item_id': iid})
    state['characters'][0]['equipment'][ITEMS[iid]['slot']] = iid
battle = create_goblin_warcamp_battle(state, ['player'], 'gear-ui-fixture')
battle['turn_order'] = ['player', 'gob_guard', 'gob_chief', 'gob_archer', 'gob_horn']
battle['turn_index'] = 0
battle['units']['player'].update(x=2, y=2)
battle['units']['gob_guard'].update(x=3, y=2)
payload = json.dumps({'state':state,'content':public_content(),'battle':battle_view(battle)},ensure_ascii=True)
source = (ROOT / 'frontend/src/main.js').read_text(encoding='utf-8')
source = source.replace('from \'./', 'from \'/frontend/src/').replace('import \'./', 'import \'/frontend/src/').replace('import "./', 'import "/frontend/src/')
source = re.sub(r'import \{ DiscordSDK \} from [^;]+;', '', source)
source = source.replace('\ninit();', '\n// Fixture replaces application startup.')
source += '\nconst fixture=' + payload + ';\n' + '''
state=fixture.state;content=fixture.content;pool={event:{id:'general'}};
activeBattleMissionId='gear-ui-fixture';window.gearCommands=[];
const originalFetch=window.fetch.bind(window);
window.fetch=(url,options)=>{
 if(String(url).startsWith('/api/')){
  if(String(url).endsWith('/battle/command')){window.gearCommands.push(JSON.parse(options.body));return Promise.resolve(new Response(JSON.stringify({battle:fixture.battle}),{status:200}))}
  return Promise.reject(new Error('Unexpected fixture API request: '+url));
 }
 return originalFetch(url,options);
};
$('#loading').classList.add('hidden');$('#game').classList.remove('hidden');$('#mission-modal').classList.remove('hidden');
window.gearRender=()=>renderBattle(fixture.battle);
window.gearSend=()=>sendCombat({action:'skill',target_id:'gob_guard'});
window.gearPreparation=()=>renderBattlePreparation({...fixture.battle,status:'preparing',preparation:{zone:[],deployment_zone:[],available:[],placements:[],budget:4,remaining:4}});
window.gearCreator=()=>{mountCharacterCreator($('#creator'),content);$('#game').classList.add('hidden');$('#mission-modal').classList.add('hidden');$('#creator').classList.remove('hidden')};
window.gearRender();window.gearReady=true;
'''
folder = ROOT / 'staging-ui/equipment-icons-v1'
folder.mkdir(parents=True, exist_ok=True)
(folder / 'battle-preview.js').write_text(source,encoding='utf-8')
page = (ROOT / 'frontend/index.html').read_text(encoding='utf-8')
page = re.sub(r'<script type="module" src="/src/main.js[^>]+></script>', '<script type="module" src="/staging-ui/equipment-icons-v1/battle-preview.js"></script>', page)
(folder / 'battle-preview.html').write_text(page,encoding='utf-8')
print(folder / 'battle-preview.html')
