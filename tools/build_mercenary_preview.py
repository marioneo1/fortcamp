"""Isolated mercenary UI fixture; never reads or writes a player database."""
from pathlib import Path
from copy import deepcopy
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.game import new_game,normalize_state,public_content
from backend.mercenaries import market,decorate_battle
from backend.combat import create_goblin_warcamp_battle,battle_view

subprocess.run([sys.executable,str(ROOT/'tools/build_relationship_combat_preview.py')],check=True)
state=normalize_state(new_game({'name':'Test Captain','traits':['guard']}))
state['resources']['gold']=100;state['mission_rank']='D'
offers=market(state,'mercenary-preview','D')
mission={'id':'hiring-preview','name':'The road to Lareth','description':'Escort a wagon past a raider checkpoint.','rank':'D','stat':'combat','difficulty':14,'party_size':2,'bodyguard_slots':1,'status':'reserved'}
battle=create_goblin_warcamp_battle(state,['player'],'mercenary-ui',defer_start=True)
decorate_battle(state,{},battle,'mercenary-ui',force='hostile')
payload=json.dumps({'state':state,'content':public_content(),'offers':offers,'mission':mission,'battle':battle_view(battle)},ensure_ascii=True)
source=(ROOT/'staging-ui/combat-relationships/preview.js').read_text(encoding='utf-8')
source+='\nconst mercenaryFixture='+payload+';\n'+"""
const oldMercFetch=window.fetch;
window.mercenaryRequests=[];
window.fetch=(url,options)=>{
 if(String(url).includes('/api/mercenaries'))return Promise.resolve(new Response(JSON.stringify({offers:mercenaryFixture.offers,state:mercenaryFixture.state}),{status:200}));
 if(String(url).endsWith('/analysis')){const request=JSON.parse(options.body);window.mercenaryRequests.push(request);return Promise.resolve(new Response(JSON.stringify({analysis:{probabilities:{critical_failure:5,failure:25,success:65,critical_success:5},claimable:true,roles:[],requirements:[],critical_success_available:true,mercenary_fee:(request.mercenary_ids?.length||0 )*15,mercenary_penalty:-(request.mercenary_ids?.length||0)}}),{status:200}))}
 return oldMercFetch(url,options);
};
window.mercenaryPlanner=async()=>{state=structuredClone(mercenaryFixture.state);content=mercenaryFixture.content;await openMission(mercenaryFixture.mission)};
window.mercenaryBattle=()=>{document.querySelectorAll('dialog').forEach(d=>d.remove());renderBattle(structuredClone(mercenaryFixture.battle))};
window.mercenaryRefresh=()=>missionPlanner.refresh(state.characters);
window.mercenaryReady=true;
"""
folder=ROOT/'staging-ui/mercenary-preview';folder.mkdir(parents=True,exist_ok=True)
(folder/'preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'staging-ui/combat-relationships/preview.html').read_text(encoding='utf-8').replace('/staging-ui/combat-relationships/preview.js','/staging-ui/mercenary-preview/preview.js')
(folder/'preview.html').write_text(page,encoding='utf-8')
print(folder/'preview.html')
