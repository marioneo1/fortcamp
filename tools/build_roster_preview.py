from pathlib import Path
s=Path('frontend/src/main.js').read_text(encoding='utf-8')
render=s[s.index('function renderRoster(){'):s.index('\nconst portraitInput=')]
prefix='''<!doctype html><html><head><meta charset="utf-8"><title>Roster QA</title><link rel="stylesheet" href="../frontend/src/styles.css"></head><body><main class="shell"><section id="tab-roster"><div class="roster-layout"><div class="roster-browser"><div id="roster-list" class="roster-list"></div></div><div id="character-detail" class="detail-panel panel"></div></div></section></main><script type="module">
import {rosterPage} from '../frontend/src/roster-tools.js';
import {raceEffects,perkModifiers} from '../frontend/src/character-effects.js';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=(v='')=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const title=(s='')=>s.replaceAll('_',' ').replace(/\\b\\w/g,m=>m.toUpperCase());
const state={characters:Array.from({length:300},(_,i)=>({id:String(i),name:['Aya Quill','Mog Quickhand','Elma','Rikka Ashnose','Kip Wiretail','Nora Stone'][i%6]+` ${i+1}`,race:['Human','Goblin','Elf','Dwarf'][i%4],specialty:i%2?'Archer':'Fighter',status:i%5?'idle':'incapacitated',source_kind:i%7?'generic':'champion',equipment:{},attributes:{str:9,dex:7,agi:6,vit:8,int:4,luk:5},appearance:{},perks:{}})),buildings:[],prisoners:[],inventory:[]};
const content={champions:{},celestials:{},races:{},perk_tracks:{},slots:['weapon','armor','accessory'],items:{},buildings:{}};
content.races.Goblin={gameplay:{summary:'Fragile, extremely mobile skirmishers who excel at scavenging and infiltration.',hp_multiplier:.7,move_bonus:2,evasion:15,initiative_bonus:4,mission_bonuses:{scavenging:2,survival:1},form_bonuses:{infiltration:2}}};
const rosterCollectionOpen={champions:false,celestials:false,prisoners:false},appearanceEditorOpen={},appearanceDrafts={},rosterFilters={query:'',status:'',race:'',kind:'',sort:'name',page:0};
let selectedCharacterId=null,rosterDetailTab='overview',rosterNeedsRefresh=false;
const attributeNames=['str','dex','agi','vit','int','luk'],combatMetrics=c=>({constitution:12,dps:16,dps_attribute:'str',weapon:'Iron sword'}),perkRank=()=>0,equippedPerks=()=>[],effectiveAttribute=(c,a)=>c.attributes[a],equipmentEditable=()=>true,itemByInstance=()=>null;
const characterStatus=c=>c.status==='idle'?'Available':'Recovering in camp · 24m',portraitHTML=(c,small)=>`<div class="portrait ${small?'smallp':''}">${c.name.slice(0,1)}</div>`;
const assert=(ok,label)=>{if(!ok)throw new Error(label)};
'''
suffix='''
try{
renderRoster();assert($$('[data-roster]').length===24,'Paging');
$('#roster-search').value='goblin';$('#roster-search').dispatchEvent(new Event('input'));
assert($$('[data-roster]').length===24,'Filtered paging');assert($('#roster-page-controls').textContent.includes('75 matching'),'Search');
$$('[data-roster]')[0].click();$('[data-roster-tab="appearance"]').click();
$('#appearance-hair-color').value='brown';$('#appearance-hair-color').dispatchEvent(new Event('input'));renderRoster();assert($('#appearance-hair-color').value==='brown','Draft retained');
$('[data-roster-tab="equipment"]').click();assert(!document.querySelector('[data-roster-panel="equipment"]').classList.contains('hidden'),'Equipment tab');
$('[data-roster-tab="overview"]').click();document.title='ROSTER QA PASS';
const banner=document.createElement('p');banner.textContent='QA PASS · 300 characters · filters, paging, tabs and appearance drafts';banner.style.color='#78c98a';document.querySelector('main').prepend(banner);
}catch(error){document.title='ROSTER QA FAIL';document.body.insertAdjacentHTML('afterbegin',`<pre>${error.stack}</pre>`)}
</script></body></html>'''
Path('tools/roster-preview.html').write_text(prefix+render+suffix,encoding='utf-8')
