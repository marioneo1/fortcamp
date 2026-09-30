"""Build a local preview from the live board renderers and representative safe fixtures."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=(ROOT/'frontend/src/main.js').read_text(encoding='utf-8')
    functions=source[source.index('function syncContractNavigation(){'):source.index('function currentMissionSelection(){')]
    page=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
    page=re.sub(r'<script type="module" src="/src/main.js[^>]+></script>','',page)
    page=page.replace('id="game" class="hidden shell"','id="game" class="shell"').replace('id="loading" class="center-card"','id="loading" class="hidden"').replace('</head>','<link rel="stylesheet" href="/frontend/src/styles.css"></head>')
    script=r"""
import {boardIcon,rankSeal,missionCard,eventHeader,filterChips,stableBoardHTML} from '/frontend/src/mission-board-ui.js';
import {matchesMission} from '/frontend/src/mission-planner.js';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=(v='')=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const title=s=>String(s||'').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
const rankBoardOpen={},missionFilters={query:'',rank:'',form:'',available:true,sort:'shortest'};
const content={mission_ranks:['E','D','C','B','A','S']};
const debugEnabled=()=>false,countdown=()=> '12:34',fmtDuration=v=>Math.ceil(v/60)+' min',openMission=m=>{window.lastOpened=m.id},openDecision=()=>{},openBattle=()=>{},showResult=()=>{},launchDebugBattle=()=>{},syncMusic=()=>{},rawApi=async()=>({}),toast=()=>{};
const names=['The Captive Cart','Smoke over the Hedgerows','Goblin Warcamp','A Road Worth Keeping','The Bell Beneath the Mud','Lost in the Old Quarry','A Market Without Merchants','The Wounded Colossus','The Black-Banner Ledger'];
const forms=['rescue','investigation','operation','defense','containment','recovery','infiltration','hunt','investigation'];
const descriptions=['Prisoners are being moved behind a shielded supply wagon. Find a way to stop it before it reaches the camp.','Smoke rises beyond the hedgerows. Follow the trail and find out who is using the abandoned signal post.','A goblin chieftain has gathered a warband on the old road. Break their hold before another caravan disappears.'];
let pool={rank:'C',registered_players:12,next_refresh:Date.now()/1000+1800,event:{id:'general'},missions:Array.from({length:15},(_,i)=>({id:'quest-'+i,template_id:'template-'+(i===9?2:i),name:names[i%9],description:descriptions[i%3],rank:['E','D','C'][Math.floor(i/5)],stat:['survival','combat','scavenging'][i%3],difficulty:12+i,party_size:i%3+1,duration_seconds:(i%4+1)*300,status:'available',mission_form:forms[i%9],resolution_mode:i%3===2?'combat':'roll',has_decisions:i%3===1,requirements:i%4===0?['A Skilled combatant']:[],roles:i%3===2?[{label:'Tank',metric:'constitution',recommended:12},{label:'Damage',metric:'dps',recommended:16}]:[],reward_preview:['Goblin gear','Gold chance','War Token','Recruit chance']})).concat(['B','A','S'].flatMap(rank=>[1,2].map(n=>({id:rank+n,rank,locked:true,status:'available',name:'HIDDEN SECRET NAME'}))))};
pool.missions[4]={...pool.missions[0],id:'quest-4'};
let privateContracts=[{...pool.missions[0],id:'private-1',private_source:'A rescued courier',expires_at:Date.now()/1000+86400,chain:{step:2,total:3}},{...pool.missions[1],id:'private-2',private_source:'The Black Banner trail',expires_at:Date.now()/1000+3600}];
let activeMissions=[{id:'active-1',name:'The Black-Banner Ledger',status:'decision'},{id:'active-2',name:'Goblin Warcamp',status:'battle'},{id:'active-3',name:'The Old Watchtower',status:'claimed',completes_at:Date.now()/1000+600}];
window.previewEvent=id=>{const events={general:{id:'general'},goblin_warhost:{id:'goblin_warhost',theme:'goblin',name:'The Green Warhost',splash:'Goblin bands are gathering under one banner. Roads are becoming unsafe, and the guild needs parties willing to go beyond the watch posts.'},ashen_procession:{id:'ashen_procession',theme:'undead',name:'The Ashen Procession',splash:'Cold ash falls across the old roads. The dead are following forgotten routes toward inhabited settlements.'},arcane_convergence:{id:'arcane_convergence',theme:'arcane',name:'Arcane Convergence',splash:'Unstable ley lines awaken old ruins and bend the weather. Familiar places no longer behave normally.'},great_beast_tide:{id:'great_beast_tide',theme:'beast',name:'The Great Beast Tide',splash:'Migrating creatures break old boundaries. Hunters, caravans, and settlements need help before the next wave arrives.'},starfall_omen:{id:'starfall_omen',theme:'starfall',name:'Starfall Omen',splash:'Unknown objects have fallen into inhabited lands. Settlements are damaged, and something hostile is moving through the impact sites.'}};pool.event=events[id];renderMissions()};
window.previewRefresh=()=>{renderMissions();renderPrivateContracts();renderActive()};
"""
    after="""
$$('.tabs button').forEach(btn=>btn.onclick=()=>{$$('.tabs button').forEach(x=>x.classList.remove('active'));btn.classList.add('active');$$('.tab-panel').forEach(x=>x.classList.add('hidden'));$(`#tab-${btn.dataset.tab}`).classList.remove('hidden');syncContractNavigation()});
renderMissions();renderPrivateContracts();renderActive();
window.previewReady=true;
"""
    page=page.replace('</body>','<script type="module">'+script+functions+after+'</script></body>')
    out=ROOT/'staging-ui/mission-board-v1/board-preview.html';out.write_text(page,encoding='utf-8');print(out)
if __name__=='__main__':main()
