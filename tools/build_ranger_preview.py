"""Build isolated Ranger UI/animation fixtures without reading or writing saves."""
import json
from pathlib import Path
import re
import sys
from copy import deepcopy
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend import combat, combat_ranger as ranger, combat_conditions as conditions, job_loadouts as jobs
from backend.game import new_game, public_content
from tests.test_ranger_jobs import RangerTests

state=new_game({'name':'Ranger Preview','starting_role':'ranger'})
views={}
for name,keys in [('marksman',['mark_quarry','longshot','multi_shot','rapid_fire']),('dot',['mark_quarry','poison_attack','pestilence_shot','rupturing_blow','multi_shot'])]:
    b,a,t=RangerTests().fixture(keys)
    b['title']='Ranger firing range';a['name']='Ranger Tester';a['portrait']='';a['weapon']=combat._player_unit(state,state['characters'][0],2,2)['weapon'];t.update(name='Training target',portrait='',x=6,y=2)
    a['special']=a['skills'][0];conditions.mark(b,a,t,3,0);t['statuses'][-1]['quarry']=True
    if name=='marksman':a['passives']=[deepcopy(jobs.SKILLS['job:ranger:sharpshooter'])];ranger.start(a);ranger.finish(a)
    else:
        ranger.poison(b,a,t,4);conditions.add_stack(t,'bleed',2,a);conditions.apply(t,'pestilence',3,a)
    b['animation_events']=[];views[name]=combat.battle_view(b)
    if name=='marksman':
        with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)),patch('backend.combat_ranger.roll',return_value=4):ranger.execute(b,a,t,jobs.SKILLS['job:ranger:multi_shot'])
        views['volley']=combat.battle_view(b)

source=(ROOT/'frontend/src/main.js').read_text(encoding='utf-8')
source=source.replace("from './","from '/frontend/src/").replace("import './","import '/frontend/src/").replace('import "./','import "/frontend/src/')
source=re.sub(r'import \{ DiscordSDK \} from [^;]+;','',source).replace('\ninit();','\n// Isolated fixture replaces startup.')
source+='\nconst rangerFixture='+json.dumps({'state':state,'content':public_content(),'views':views},ensure_ascii=True)+';\n'+'''
state=rangerFixture.state;content=rangerFixture.content;pool={event:{id:'general'}};
const originalFetch=window.fetch.bind(window);
window.fetch=(url,options)=>String(url).startsWith('/api/')?Promise.reject(Error('Fixture does not use live APIs')):originalFetch(url,options);
$('#loading').classList.add('hidden');$('#game').classList.remove('hidden');$('#mission-modal').classList.remove('hidden');
activeBattleMissionId='ranger-preview';window.rangerShow=name=>renderBattle(structuredClone(rangerFixture.views[name]));
window.rangerShow('marksman');window.rangerReady=true;
'''
destination=ROOT/'staging-ui/ranger-v1';destination.mkdir(parents=True,exist_ok=True)
(destination/'preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
page=re.sub(r'<script type="module" src="/src/main.js[^>]+></script>','<script type="module" src="/staging-ui/ranger-v1/preview.js"></script>',page)
(destination/'preview.html').write_text(page,encoding='utf-8')
print(destination/'preview.html')
