"""Isolated real UI/VFX preview. All game API calls are mocked; saves untouched."""
from pathlib import Path
import subprocess,sys,json
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.game import new_game,normalize_state,public_content
from backend.relationships import conversation
from backend.combat import create_goblin_warcamp_battle,battle_view,apply_player_command
subprocess.run([sys.executable,str(ROOT/'tools/build_gear_battle_preview.py')],check=True)
state=new_game({'name':'Preview Leader'})
c=deepcopy(state['characters'][0]);c.update(id='companion',is_player=False,name='Mog',personality_id='guardian',loyalty=80);c.pop('relationship',None);state['characters'].append(c)
state=normalize_state(state);state['meals']={'trail_meal':1,'study_meal':1,'rest_meal':1}
c['service_record'].update(missions_taken=6,missions_completed=4,missions_failed=2,kills=7,total_damage=210,combat_turns=30,highest_turn_damage=18)
replies={}
for topic in ['recent','food','trust','outlook']:
    after=deepcopy(state);reply=conversation(after,'companion',topic=topic);replies[topic]={'reply':reply,'state':after}
battle=create_goblin_warcamp_battle(state,['player'],'vfx-preview')
battle['turn_order']=['player','gob_guard','gob_chief','gob_archer','gob_horn'];battle['turn_index']=0
battle['units']['player'].update(x=2,y=2,attack=100,attack_range=4,attack_elevation_rule='ignore')
battle['units']['gob_guard'].update(x=3,y=2,hp=1,evasion=0)
before=battle_view(battle);after=apply_player_command(battle,{'action':'attack','target_id':'gob_guard'})
payload=json.dumps({'state':state,'content':public_content(),'replies':replies,'before':before,'after':after},ensure_ascii=True)
source=(ROOT/'staging-ui/equipment-icons-v1/battle-preview.js').read_text(encoding='utf-8')
source+='\nconst relationshipFixture='+payload+';\n'+"""
identity={guild_id:'fixture-guild',user_id:'fixture-user'};state=relationshipFixture.state;content=relationshipFixture.content;
window.relationshipRequests=[];const previousFixtureFetch=window.fetch;
window.fetch=(url,options)=>{if(String(url).endsWith('/conversation')){const request=JSON.parse(options.body);window.relationshipRequests.push(request);return Promise.resolve(new Response(JSON.stringify(relationshipFixture.replies[request.topic||'recent']),{status:200}))}return previousFixtureFetch(url,options)};
window.relationshipPreview=()=>{combatEffects.pause();$('#mission-modal').classList.add('hidden');selectedCharacterId='companion';rosterDetailTab='conversation';renderRoster();$('.tabs button[data-tab="roster"]').click()};
window.nativePreview=()=>{$('#mission-modal').classList.remove('hidden');renderBattle(structuredClone(relationshipFixture.before));};
window.nativeCast=()=>{const next=structuredClone(relationshipFixture.after);renderBattle(next);animateBattleMovement(relationshipFixture.before,next)};
window.nativeDiagnostics=()=>combatEffects.diagnostics();window.nativePreview();window.relationshipReady=true;
window.qolEquipment=()=>{window.relationshipPreview();
 state.inventory.push({instance_id:'preview-equipped',item_id:'meridian_field_projector'},{instance_id:'preview-spare',item_id:'meridian_field_projector'});
 state.characters.find(c=>c.id==='companion').equipment.weapon='preview-equipped';
 rosterDetailTab='equipment';renderRoster();
};
window.qolContract=()=>openMission({id:'preview-contract',name:'A guild contract',rank:'E',status:'available',party_size:1,description:'Check the canal.',reward_preview:['Contract payment','Possible equipment discoveries']});
"""
folder=ROOT/'staging-ui/combat-relationships';folder.mkdir(parents=True,exist_ok=True)
(folder/'preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'staging-ui/equipment-icons-v1/battle-preview.html').read_text(encoding='utf-8').replace('/staging-ui/equipment-icons-v1/battle-preview.js','/staging-ui/combat-relationships/preview.js')
(folder/'preview.html').write_text(page,encoding='utf-8')
print(folder/'preview.html')
