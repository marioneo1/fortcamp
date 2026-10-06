"""Isolated Mage visual fixtures: never read saves or call live endpoints."""
import json,re,sys
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend import combat,combat_mage as mage,combat_conditions as conditions,job_loadouts as jobs
from backend.game import new_game,public_content
from tests.test_mage_jobs import MageTests
state=new_game({'name':'Mage Preview','starting_role':'mage'});views={}
def fixture(keys,debuffer=False):
 b,a,t=MageTests().fixture(keys,debuffer);profile=combat._player_unit(state,state['characters'][0],2,2);a.update(name='Mage Tester',portrait=profile['portrait'],weapon=profile['weapon'],weapon_type=profile['weapon_type'],job_description=jobs.JOBS['mage']['description'],special=a['skills'][0]);t.update(name='Training target',portrait='',x=5,y=2)
 b['units']['second']={**deepcopy(t),'id':'second','x':6,'y':3,'name':'Second target'};b['units']['ally']={**deepcopy(a),'id':'ally','x':2,'y':4,'name':'Monk ally','attack_elevation_rule':'melee','statuses':[],'skills':[],'passives':[]}
 b['animation_events']=[];return b,a,t
b,a,t=fixture(['chain_lightning','fireball','flash_freeze','typhoon','enchant_weapon']);conditions.apply(t,'wet',2,a);views['elemental']=combat.battle_view(b)
with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
views['frozen']=combat.battle_view(b)
for name,key in [('fireball','fireball'),('chain','chain_lightning'),('gravity','singularity'),('wind','typhoon')]:
 b,a,t=fixture([key]);a['special']=a['skills'][0];conditions.apply(t,'wet',2,a)
 with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)),patch('backend.combat_mage.roll',return_value=1):mage.execute(b,a,a if key=='typhoon' else t,a['special'])
 views[name]=combat.battle_view(b)
b,a,t=fixture(['flash_freeze','singularity','meteor','enchant_weapon'],True);a['special']=a['skills'][0];mage.execute(b,a,t,jobs.SKILLS['job:mage:flash_freeze']);views['armed']=combat.battle_view(b)
b,a,t=fixture(['meteor']);mage.execute(b,a,t,a['special']);views['channel']=combat.battle_view(b);a['ability_activation']+=1;b['animation_events']=[]
with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):mage.settle(b,a,'start')
views['meteor']=combat.battle_view(b)
source=(ROOT/'frontend/src/main.js').read_text();source=source.replace("from './","from '/frontend/src/").replace("import './","import '/frontend/src/").replace('import "./','import "/frontend/src/')
source=re.sub(r'import \{ DiscordSDK \} from [^;]+;','',source).replace('\ninit();','\n// Isolated fixture replaces startup.')
source+='\nconst mageFixture='+json.dumps({'state':state,'content':public_content(),'views':views},ensure_ascii=True)+';\n'+'''
state=mageFixture.state;content=mageFixture.content;pool={event:{id:'general'}};
const originalFetch=window.fetch.bind(window);window.mageSent=[];
window.fetch=(url,options)=>{if(String(url).startsWith('/api/')){window.mageSent.push({url,body:JSON.parse(options?.body||'{}')});return Promise.resolve({ok:true,json:async()=>({battle:structuredClone(mageFixture.views.elemental)})})}return originalFetch(url,options)};
$('#loading').classList.add('hidden');$('#game').classList.remove('hidden');$('#mission-modal').classList.remove('hidden');
activeBattleMissionId='mage-preview';window.mageShow=name=>{combatPlayback.clear();renderBattle(structuredClone(mageFixture.views[name]))};
window.mageShow('elemental');window.mageReady=true;window.mageInspect=()=>({mode:selectedCombatAction,actor:activeBattleView.units[activeBattleView.current_unit_id],previews:activeBattleView.skill_previews,blocked:combatPlaybackBlocked(),pending:combatRequestPending});
'''
out=ROOT/'staging-ui/mage-v1';out.mkdir(parents=True,exist_ok=True);(out/'preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'frontend/index.html').read_text();page=re.sub(r'<script type="module" src="/src/main.js[^>]+></script>','<script type="module" src="/staging-ui/mage-v1/preview.js"></script>',page);(out/'preview.html').write_text(page,encoding='utf-8');print(out/'preview.html')
