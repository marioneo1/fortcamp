"""Isolated Mage visual fixtures: never read saves or call live endpoints."""
import json,re,sys
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from backend import combat,combat_mage as mage,combat_conditions as conditions,job_loadouts as jobs
from backend.game import new_game,public_content
from tests.test_mage_jobs import MageTests
from PIL import Image
state=new_game({'name':'Mage Preview','starting_role':'mage'});views={}
preview_face=ROOT/'staging-ui/mage-v1/preview-face.png';preview_face.parent.mkdir(parents=True,exist_ok=True)
portrait=ROOT/'portraits/aasimar_female_healer.png'
if portrait.exists():
 atlas=Image.open(portrait);atlas.crop((0,0,atlas.width//5,atlas.height//4)).save(preview_face)
def fixture(keys,debuffer=False):
 b,a,t=MageTests().fixture(keys,debuffer);profile=combat._player_unit(state,state['characters'][0],2,2);a.update(name='Mage Tester',portrait='/staging-ui/mage-v1/preview-face.png' if preview_face.exists() else profile['portrait'],weapon=profile['weapon'],weapon_type=profile['weapon_type'],job_description=jobs.JOBS['mage']['description'],special=a['skills'][0]);t.update(name='Training target',portrait=a['portrait'],x=5,y=2)
 b['units']['second']={**deepcopy(t),'id':'second','x':6,'y':3,'name':'Second target'};b['units']['ally']={**deepcopy(a),'id':'ally','x':2,'y':4,'name':'Monk ally','attack_elevation_rule':'melee','statuses':[],'skills':[],'passives':[]}
 b['animation_events']=[];return b,a,t
b,a,t=fixture(['chain_lightning','fireball','flash_freeze','typhoon','enchant_weapon']);conditions.apply(t,'wet',2,a);views['elemental']=combat.battle_view(b)
with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t)
views['frozen']=combat.battle_view(b)
for material in ['grass','dirt','stone']:
 surface=deepcopy(b);surface['ground_tiles']=[{'x':x,'y':y,'material':material} for y in range(surface['height']) for x in range(surface['width'])]
 mage.scorch(surface,a,{'x':5,'y':4},2);views['surface_'+material]=combat.battle_view(surface)
for name,key in [('fireball','fireball'),('chain','chain_lightning'),('gravity','singularity'),('wind','typhoon')]:
 b,a,t=fixture([key]);a['special']=a['skills'][0];conditions.apply(t,'wet',2,a)
 with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)),patch('backend.combat_mage.roll',return_value=1):mage.execute(b,a,a if key=='typhoon' else t,a['special'])
 views[name]=combat.battle_view(b)
b,a,t=fixture(['flash_freeze','singularity','meteor','enchant_weapon'],True);a['special']=a['skills'][0];mage.execute(b,a,t,jobs.SKILLS['job:mage:flash_freeze']);views['armed']=combat.battle_view(b)
b,a,t=fixture(['meteor']);mage.execute(b,a,t,a['special']);views['channel']=combat.battle_view(b);a['ability_activation']+=1;b['animation_events']=[]
with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):mage.settle(b,a,'start')
views['meteor']=combat.battle_view(b)
b,a,t=fixture(['fireball'])
combat.spaces.place_zone(b,t,{'zone':'scorched','turns':2},[{'x':2,'y':3},{'x':1,'y':3}])
combat.spaces.place_zone(b,t,{'zone':'caltrops','turns':2},[{'x':2,'y':3},{'x':1,'y':3}])
views['navigation']=combat.battle_view(b)
views['navigation']['door_controls']=[{'x':4,'y':1,'gate_id':'qa_open','operation':'Open','label':'Open test door','help':'Open the door','command':{'action':'interact','target_id':'qa_open'}},{'x':5,'y':1,'gate_id':'qa_close','operation':'Close','label':'Close test door','help':'Close the door','command':{'action':'interact','target_id':'qa_close'}}]
b,a,t=fixture(['flash_freeze']);t['boss']=True
b['units']={a['id']:a,t['id']:t};b.update(turn_order=[a['id'],t['id']],turn_index=0)
views['boss_freeze_ready']=combat.battle_view(b)
p= mage.packet(b,a,'flash_freeze',t,2)
with patch('backend.combat_mage.roll',return_value=1):mage.freeze(b,a,t,packet=p)
t['status_activation']=[99,0];conditions.start_activation(b,t);conditions.finish_activation(t)
views['boss_freeze_expired']=combat.battle_view(b)
# Bard support fixtures share the real combat UI and never touch player saves.
b,a,t=fixture(['meteor'])
a.update(job_id='bard',name='Bard Tester',job_description=jobs.JOBS['bard']['description'],
         skills=[deepcopy(jobs.SKILLS['job:bard:'+k]) for k in ('accelerando','quickening_chorus','war_anthem','song_of_peace','cue_the_strike')],
         passives=[deepcopy(jobs.SKILLS['job:bard:maestro']),deepcopy(jobs.SKILLS['job:bard:battle_musician'])])
b['units']['ally'].update(x=3,y=3)
a['special']=a['skills'][0]
views['bard_ready']=combat.battle_view(b)
for song in combat.bard.SONGS:
 song_battle=deepcopy(b)
 combat.bard.begin_song(song_battle,song_battle['units'][a['id']],song)
 views['bard_'+song]=combat.battle_view(song_battle)
b,a,t=fixture(['meteor'])
a.update(job_id='cleric',name='Cleric Tester',intelligence=12,hp=20,max_hp=80,
         skills=[deepcopy(jobs.SKILLS['job:cleric:'+k]) for k in ('mend','heal','sanctuary','rest','holy_light')],passives=[])
b['units']['ally'].update(x=3,y=3,hp=10,max_hp=100)
a['special']=a['skills'][0];combat.cleric.adapt(a)
views['cleric_ready']=combat.battle_view(b)
rest_b=deepcopy(b);rest_a=rest_b['units'][a['id']];combat.cleric.execute(rest_b,rest_a,rest_a,rest_a['skills'][3]);rest_a['acted']=False
views['cleric_rest']=combat.battle_view(rest_b)
zone_b=deepcopy(b);zone_a=zone_b['units'][a['id']];combat.cleric.execute(zone_b,zone_a,zone_b['units']['ally'],zone_a['skills'][2]);zone_a['acted']=False
views['cleric_sanctuary']=combat.battle_view(zone_b)
light_b=deepcopy(b);light_a=light_b['units'][a['id']]
with patch('backend.combat._attack_hits',return_value=(True,{'damage_bonus':0,'chance':100},1)):
 combat.cleric.execute(light_b,light_a,light_b['units'][t['id']],light_a['skills'][4])
light_a['acted']=False;views['cleric_light']=combat.battle_view(light_b)
priest_b=deepcopy(b);priest=priest_b['units'][a['id']]
priest['skills']=[deepcopy(jobs.SKILLS['job:cleric:'+k]) for k in ('smite','heal','sanctuary','holy_light')]
priest['passives']=[deepcopy(jobs.SKILLS['job:cleric:battle_priest'])];priest['special']=priest['skills'][0];combat.cleric.adapt(priest)
views['cleric_priest']=combat.battle_view(priest_b)
# Druid portraits, placement, regeneration and shared living-terrain playback.
b,a,t=fixture(['fireball'])
a.update(job_id='druid',name='Druid Tester',hp=50,max_hp=100,intelligence=16,
         skills=[deepcopy(jobs.SKILLS['job:druid:'+k]) for k in ('prowler','bulwark','rat','rejuvenation','bramble_wall')],
         passives=[deepcopy(jobs.SKILLS['job:druid:natures_persistence']),deepcopy(jobs.SKILLS['job:druid:wild_instinct'])])
a['job_description']=jobs.JOBS['druid']['description']
a['special']=a['skills'][0];views['druid_ready']=combat.battle_view(b)
support_b=deepcopy(b);sa=support_b['units'][a['id']]
sa['skills']=[deepcopy(jobs.SKILLS['job:druid:'+k]) for k in ('prowler','living_armor','rat','rejuvenation','bramble_wall')]
sa['passives']=[];sa['special']=sa['skills'][-1];views['druid_support']=combat.battle_view(support_b)
inspect_b=deepcopy(support_b);inspect_b['units'][t['id']].update(boss=True,status_resistances={'stun':25,'burn':50},displacement_resistance=25)
views['druid_inspect']=combat.battle_view(inspect_b)
hover_b=deepcopy(inspect_b);ht=hover_b['units'][t['id']]
for sid in ('pestilence','armor_fracture','wet','slow','hobbled','blind','fear','mute','blister','stun'):conditions.apply(ht,sid,2,hover_b['units'][a['id']])
for sid,n in [('poison',5),('burn',4),('bleed',3)]:
 for _ in range(n):conditions.add_stack(ht,sid,2,hover_b['units'][a['id']])
views['druid_hover']=combat.battle_view(hover_b)
for kind in ('prowler','bulwark','rat'):
 fb=deepcopy(b);fa=fb['units'][a['id']];combat.druid.change(fb,fa,kind)
 fa['ability_activation']+=1;views['druid_'+kind]=combat.battle_view(fb)
wall_b=deepcopy(b);wa=wall_b['units'][a['id']]
combat.druid.execute(wall_b,wa,{'x':3,'y':3},jobs.SKILLS['job:druid:bramble_wall'])
wa['acted']=False;wa['ability_cooldowns']={};wa['special']=wa['skills'][-1]
views['druid_wall']=combat.battle_view(wall_b)
lash_b=deepcopy(wall_b);lt=lash_b['units'][t['id']];lt.update(x=4,y=2)
lash_b['animation_events']=[]
with patch('backend.combat_druid.roll',return_value=1):combat.druid.adjacent_reactions(lash_b,lt,'qa')
views['druid_lash']=combat.battle_view(lash_b)
from tests.test_summoner_jobs import SummonerTests
sb,sa,st=SummonerTests().fixture(True)
sa.update(name='Summoner Tester',portrait=a['portrait'],source_kind='character',job_description=jobs.JOBS['summoner']['description'])
for skill in sa['skills']:skill['source_kind']='character'
sa['skills']=sa['skills'][:5];sa['special']=sa['skills'][1]
sb['animation_events']=[];views['summoner_ready']=combat.battle_view(sb)
combat.summoner.spawn(sb,sa,'bound_companion',combat.summoner.placement(sb,sa)[:1],'fire')
combat.summoner.spawn(sb,sa,'wisp_swarm',combat.summoner.placement(sb,sa,True)[:3])
sa['acted']=False;sb['animation_events']=[]
views['summoner_active']=combat.battle_view(sb)
sa['skills']=[deepcopy(jobs.SKILLS['job:summoner:'+key]) for key in ['transposition','spirit_projection','sacrifice','overload','life_pact']]
for skill in sa['skills']:skill['source_kind']='character'
sa['special']=sa['skills'][0]
for creature,pos in zip(combat.summoner.crew(sb,sa),[(4,2),(5,1),(6,2),(5,3)]):creature.update(x=pos[0],y=pos[1])
views['summoner_payoff']=combat.battle_view(sb)
fx=deepcopy(sb);fa=fx['units'][sa['id']];fa['special']=fa['skills'][2]
combat.summoner.command(fx,fa,fa['special'],{'x':5,'y':2})
views['summoner_sacrifice']=combat.battle_view(fx)
ox=deepcopy(sb);oa=ox['units'][sa['id']];ou=combat.summoner.crew(ox,oa)[0]
combat.summoner.command(ox,oa,next(s for s in oa['skills'] if s['summoner_kind']=='overload'),{'target_id':ou['id']})
views['summoner_overload']=combat.battle_view(ox)
dx=deepcopy(sb);da=dx['units'][sa['id']];dw=combat.summoner.group(dx,da,'wisp_swarm')[0]
dx['animation_events']=[]
attackers=[]
for i,pos in enumerate([(1,2),(2,1),(2,3),(5,0)]):
 enemy={**deepcopy(st),'id':f'qa_enemy_{i}','name':f'Attacker {i+1}','x':pos[0],'y':pos[1],'attack':1 if i<3 else 50,'statuses':[]}
 dx['units'][enemy['id']]=enemy;attackers.append(enemy)
views['summoner_death_before']=combat.battle_view(dx)
with patch('backend.combat._attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
 for i,enemy in enumerate(attackers):
  combat._perform_attack(dx,enemy,da if i<3 else dw,'melee');combat._check_end(dx)
views['summoner_death_after']=combat.battle_view(dx)
born=deepcopy(dx);born['animation_events']=[]
combat.druid.visual(born,born['units'][dw['id']],'summoner_conjure','summoner_conjure')
born['animation_events'].extend(deepcopy(dx['animation_events']))
views['summoner_birth_death']=combat.battle_view(born)

# Engineer fixtures: real machinery rules, no live saves or endpoints.
from tests.test_engineer_jobs import EngineerTests
from backend import combat_engineer as engineer
eb,ea,et=EngineerTests().fixture();ea.update(name='Engineer Tester',portrait=a['portrait'],special=next(s for s in ea['skills'] if s['engineer_kind']=='sentry_turret'))
ea['skills']=ea['skills'][:5];views['engineer_ready']=combat.battle_view(eb)
eu=engineer.spawn(eb,ea,'heavy_emplacement',{'x':ea['x']+1,'y':ea['y']});ea['acted']=False
engineer.command(eb,ea,jobs.SKILLS['job:engineer:man_the_guns'],{'target_id':eu['id']});views['engineer_mounted']=combat.battle_view(eb)
engineer.command(eb,ea,jobs.SKILLS['job:engineer:overclock'],{});views['engineer_overclock']=combat.battle_view(eb)
engineer.unmount(eb,ea,eu,emergency=True);ea.pop('overclock_until',None);ea['acted']=False
engineer.command(eb,ea,jobs.SKILLS['job:engineer:proximity_charge'],engineer.placement(eb,ea)[0]);ea['acted']=False
engineer.command(eb,ea,jobs.SKILLS['job:engineer:dynamite'],{'x':ea['x']+1,'y':ea['y']});views['engineer_hazards']=combat.battle_view(eb)

ux,ua,ut=EngineerTests().fixture();ua.update(name='Engineer Tester',portrait=a['portrait'],special=ua['skills'][0])
engineer.spawn(ux,ua,'heavy_emplacement',{'x':ua['x']+1,'y':ua['y']})
views['engineer_direct']=combat.battle_view(ux)
cx,ca,ct=EngineerTests().fixture();ca.update(name='Engineer Tester',portrait=a['portrait'],special=ca['skills'][0])
engineer.command(cx,ca,ca['skills'][0],engineer.placement(cx,ca)[0]);ca['acted']=False
cx['animation_events']=[];views['engineer_unfinished']=combat.battle_view(cx)
cu=engineer.machines(cx,ca)[0]
combat._perform_attack(cx,ct,ca,'ballistic')
combat._deal_damage(cx,ct,cu);combat._deal_damage(cx,ct,cu)
views['engineer_destroyed']=combat.battle_view(cx)
hx=deepcopy(eb);hx['animation_events']=[];ha=hx['units'][ea['id']]
combat._perform_attack(hx,hx['units'][et['id']],ha,'ballistic')
for hazard in list(hx.get('engineer_hazards',[])):engineer.detonate(hx,hazard)
views['engineer_exploded']=combat.battle_view(hx)

dx,da,dt=EngineerTests().fixture()
da.update(portrait=ea.get('portrait'),name='Throw test')
dx['animation_events']=[]
views['engineer_throw_before']=combat.battle_view(dx)
engineer.command(dx,da,jobs.SKILLS['job:engineer:dynamite'],{'x':3,'y':2})
combat._perform_attack(dx,dt,da,'ballistic')
engineer.detonate(dx,dx['engineer_hazards'][0])
views['engineer_throw_after']=combat.battle_view(dx)

from tests.test_captor_jobs import CaptorTests
from backend import combat_captor as captor
cb,ca,ct=CaptorTests().fixture();ca.update(name='Captor Tester',portrait=a['portrait']);ct.update(armor=2,intelligence=4,agility=4,portrait=a['portrait'])
ca['skills']=ca['skills'][:5];ca['special']=ca['skills'][0];cb['animation_events']=[]
views['captor_ready']=combat.battle_view(cb)
conditions.add_stack(ct,'hobbled',4,ca)
views['captor_abduct']=combat.battle_view(cb)
held=deepcopy(cb);ha=held['units'][ca['id']];ht=held['units'][ct['id']]
captor.command(held,ha,jobs.SKILLS['job:captor:restraining_hold'],{'target_id':ht['id']});ha.update(acted=False,special=deepcopy(jobs.SKILLS['job:captor:restraining_hold']))
views['captor_hold']=combat.battle_view(held)
bola=deepcopy(cb);ba=bola['units'][ca['id']];bt=bola['units'][ct['id']];bola['animation_events']=[]
from unittest.mock import patch
with patch.object(captor,'roll',return_value=0):captor.command(bola,ba,jobs.SKILLS['job:captor:bola'],{'target_id':bt['id']})
views['captor_bola']=combat.battle_view(bola)

growth_b=deepcopy(b);ga=growth_b['units'][a['id']]
combat.druid.execute(growth_b,ga,ga,jobs.SKILLS['job:druid:living_armor']);ga['acted']=False
views['druid_growth']=combat.battle_view(growth_b)
views['hud_crowd']=deepcopy(views['captor_ready'])
for i in range(11):
 extra=deepcopy(next(iter(views['hud_crowd']['units'].values())));extra.update(id=f'hud-extra-{i}',name=f'Queue fighter {i+1}',team='enemy',x=i%8,y=7)
 views['hud_crowd']['units'][extra['id']]=extra;views['hud_crowd']['turn_order'].append(extra['id'])
from tests.test_encounter_behavior import EncounterBehaviorTests
from backend import combat_encounter_ai as encounter_ai
sw,sp,(sr,sd,st)=EncounterBehaviorTests().arena()
sr.update(x=6,y=5,hp=5,max_hp=8,attack=2);sd.update(x=6,y=6,hp=9,max_hp=9,attack=3);st.update(x=10,y=10)
sw.update(turn_order=['player',sr['id'],sd['id'],st['id']],turn_index=0)
views['swarm_before']=combat.battle_view(deepcopy(sw))
encounter_ai.merge(sw,sr,sd)
with patch.object(combat,'_attack_hits',return_value=(True,{'chance':100,'damage_bonus':0},1)):
    combat._perform_attack(sw,sr,sp,'melee')
views['swarm_after']=combat.battle_view(sw)
bb,bp,(be,bc)=EncounterBehaviorTests().arena('roadside_toll','variant-0')
bb.update(turn_order=['player',be['id'],bc['id']],turn_index=0)
views['bandit_before']=combat.battle_view(deepcopy(bb))
encounter_ai.say(bb,bc,'Hold still. This road is ours.','snare')
views['bandit_talk']=combat.battle_view(bb)
near=deepcopy(bb)
near['units']['player'].update(x=6,y=5)
views['bandit_adjacent']=combat.battle_view(near)
for label,arena in [('near',near),('far',bb)]:
    strike=deepcopy(arena)
    actor=strike['units']['player']
    actor['skills']=[deepcopy(jobs.SKILLS['job:fighter:bash'])]
    actor['special']=actor['skills'][0]
    views['driving_strike_'+label]=combat.battle_view(strike)
door=deepcopy(near)
door['terrain']=[{'id':'qa-door','name':'Post Door','kind':'gate','x':5,'y':4,
    'edge_wall':True,'wall_edges':['north'],'state':'closed','blocking':True}]
views['door_approach']=combat.battle_view(door)

# Withdrawal UI fixtures use an actual ready/holding extraction state.
for label,ready in [('command_exit_hold',False),('command_exit_ready',True)]:
    arena=deepcopy(bb)
    actor=arena['units']['player']
    arena['extraction']={'name':'QA exit','tiles':[{'x':actor['x'],'y':actor['y']}]}
    actor['exit_ready']=ready
    views[label]=combat.battle_view(arena)

source=(ROOT/'frontend/src/main.js').read_text();source=source.replace("from './","from '/frontend/src/").replace("import './","import '/frontend/src/").replace('import "./','import "/frontend/src/')
source=re.sub(r'import \{ DiscordSDK \} from [^;]+;','',source).replace('\ninit();','\n// Isolated fixture replaces startup.')
source+='\nconst mageFixture='+json.dumps({'state':state,'content':public_content(),'views':views},ensure_ascii=True)+';\n'+'''
state=mageFixture.state;content=mageFixture.content;pool={event:{id:'general'}};
const originalFetch=window.fetch.bind(window);window.mageSent=[];
window.fetch=(url,options)=>{if(String(url).startsWith('/api/')){window.mageSent.push({url,body:JSON.parse(options?.body||'{}')});return Promise.resolve({ok:true,json:async()=>({battle:structuredClone(mageFixture.views.elemental)})})}return originalFetch(url,options)};
$('#loading').classList.add('hidden');$('#game').classList.remove('hidden');$('#mission-modal').classList.remove('hidden');
activeBattleMissionId='mage-preview';window.mageShow=async name=>{const view=structuredClone(mageFixture.views[name]);await prepareMagePlayback(view);combatPlayback.clear();battleFit=false;battleZoom=1;renderBattle(view);$(\'#mission-modal .modal-card\').scrollTop=0};
window.mageShow('elemental');window.mageReady=true;window.mageInspect=()=>({mode:selectedCombatAction,actor:activeBattleView.units[activeBattleView.current_unit_id],previews:activeBattleView.skill_previews,blocked:combatPlaybackBlocked(),pending:combatRequestPending});
window.mageEventTimes=name=>impactTimeline(structuredClone(mageFixture.views[name].animation_events)).map(r=>({type:r.event.type,skill:r.event.skill,unit_id:r.event.unit_id,start:r.start,duration:r.duration}));
'''
out=ROOT/'staging-ui/mage-v1';out.mkdir(parents=True,exist_ok=True);(out/'preview.js').write_text(source,encoding='utf-8')
page=(ROOT/'frontend/index.html').read_text();page=re.sub(r'<script type="module" src="/src/main.js[^>]+></script>','<script type="module" src="/staging-ui/mage-v1/preview.js"></script>',page);(out/'preview.html').write_text(page,encoding='utf-8');print(out/'preview.html')
