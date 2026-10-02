"""Isolated real-UI fixture. Does not open any game database or call live APIs."""
from pathlib import Path
from copy import deepcopy
import json
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.game import new_game, normalize_state, public_content
from backend.economy import trade_view
from backend.combat import create_battle, battle_view, _advance_to_player

subprocess.run([sys.executable, str(ROOT/'tools/build_gear_battle_preview.py')], check=True)
state = normalize_state(new_game({'name': 'Captain', 'attributes': {'int': 12}}))
ally = deepcopy(state['characters'][0]); ally.update(id='ally', name='Scout', is_player=False, loyalty=100)
state['characters'].append(ally); state['mission_rank'] = 'C'; state['resources']['gold'] = 100
state['factions'].update(hedgerow=20, meridian=20, lantern=20)
state['inventory'].extend([{'instance_id':'dressing', 'item_id':'field_dressing'}, {'instance_id':'coat', 'item_id':'medic_coat'}])
state['characters'][0]['equipment']['body'] = 'coat'
battle = create_battle(state, ['player', 'ally'], 'support-preview', 'goblin_warcamp', defer_start=True)
battle['turn_order'] = ['player','ally','gob_chief','gob_archer','gob_horn','gob_guard']; battle['terrain'] = []; battle['elevation'] = []
battle['units']['player'].update(x=1,y=6); battle['units']['ally'].update(x=2,y=6,hp=20)
_advance_to_player(battle)
payload = json.dumps({'state':state, 'content':public_content(), 'trade':trade_view(state,'preview:camp'), 'battle':battle_view(battle)}, ensure_ascii=True)
source = (ROOT/'staging-ui/equipment-icons-v1/battle-preview.js').read_text(encoding='utf-8')
source += '\nconst factionFixture='+payload+';\n'+'''
state=factionFixture.state;content=factionFixture.content;identity={guild_id:'preview',user_id:'camp'};pool={event:{id:'general'},missions:[]};
const factionFetch=window.fetch;window.factionRequests=[];
window.fetch=(url,options)=>{
 if(String(url).endsWith('/api/trade'))return Promise.resolve(new Response(JSON.stringify({state:factionFixture.state,trade:factionFixture.trade}),{status:200}));
 if(String(url).includes('/api/factions/contracts/')){window.factionRequests.push(url);return Promise.resolve(new Response(JSON.stringify({state:factionFixture.state,mission:{id:'private-preview',name:'A Signal Both Sides Trust',status:'available',rank:'E',party_size:1,description:'Agree a code with the farmers.',reward_preview:['Guild fee']}}),{status:200}))}
 if(String(url).endsWith('/analysis'))return Promise.resolve(new Response(JSON.stringify({analysis:{claimable:true,roles:[],requirements:[],probabilities:{critical_failure:5,failure:25,success:65,critical_success:5}}}),{status:200}));
 return factionFetch(url,options);
};
window.factionTradePreview=()=>{activeBattleView=null;$('#mission-modal').classList.add('hidden');baseView='supplies';renderBase();$('.tabs button[data-tab="base"]').click();$('#camp-trade').click()};
window.factionSupportPreview=()=>{document.querySelectorAll('dialog').forEach(d=>d.close());$('#mission-modal').classList.remove('hidden');activeBattleMissionId='support-preview';renderBattle(structuredClone(factionFixture.battle))};
window.factionReady=true;
'''
folder=ROOT/'staging-ui/faction-combat-preview'; folder.mkdir(parents=True,exist_ok=True)
(folder/'preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'staging-ui/equipment-icons-v1/battle-preview.html').read_text(encoding='utf-8').replace('/staging-ui/equipment-icons-v1/battle-preview.js','/staging-ui/faction-combat-preview/preview.js')
(folder/'preview.html').write_text(page,encoding='utf-8')
print(folder/'preview.html')
