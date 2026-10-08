import test from 'node:test';
import assert from 'node:assert/strict';
import {hotbarPage,hotbarMarkup,unitInspectMarkup,cursorCardPosition,areaForecastMarkup} from './combat-hotbar.js';
const esc=s=>String(s??'').replaceAll('<','&lt;');
test('innate Summon Orders uses a normal numbered tile and explains its free command cost',()=>{
 const skill={id:'innate:summoner:orders',name:'Summon Orders',source_kind:'innate',summoner_kind:'orders',free_action:true,description:'Costs no equipped skill slot.',availability:{available:true},range:0};
 const html=hotbarMarkup({skills:[skill]},0,null,esc);
 assert.match(html,/data-hotbar-skill="innate:summoner:orders"/);assert.match(html,/data-hotbar-key="1"/);
 assert.match(html,/Free command; no action or loadout slot/);assert.match(html,/summoner-v1\/bound_companion.png/);
});

test('cursor-following summary has plain stats while pinned inspection retains calculation help',()=>{
 const unit={id:'qa',name:'Tester',hp:20,max_hp:30,attack:10,armor:3,move:4,attack_range:2,statuses:[],stat_explanations:{Attack:'Calculated attack ingredients',Health:'Calculated health ingredients'}};
 const summary=unitInspectMarkup(unit,{},esc,null,null,{compact:true});
 assert.match(summary,/ATK/);assert.match(summary,/20\/30 HP/);
 assert.doesNotMatch(summary,/inspect-stat-help|class="inspect-stat"|tabindex=|<abbr|Calculated attack ingredients|Calculated health ingredients/);
 const details=unitInspectMarkup(unit,{},esc);
 assert.match(details,/class="inspect-stat" tabindex="0"/);
 assert.match(details,/Calculated attack ingredients/);assert.match(details,/Calculated health ingredients/);
});

test('hover limits effects and reports overflow while pinned details retains the complete list',()=>{
 const unit={id:'qa',name:'Tester',hp:20,max_hp:30,statuses:[{id:'burn',stacks:2},{id:'poison',stacks:2},{id:'bleed',stacks:1},{id:'wet',turns:2},{id:'blind',turns:1}]};
 const summary=unitInspectMarkup(unit,{},esc,null,null,{compact:true});
 assert.equal((summary.match(/class="compact-effect"/g)||[]).length,3);
 assert.match(summary,/\+2 more effects/);assert.match(summary,/Right-click for all/);
 const details=unitInspectMarkup(unit,{},esc);
 assert.equal((details.match(/class="effect-detail-card"/g)||[]).length,5);
 assert.doesNotMatch(details,/inspect-more/);
});

test('Cleric charges and End Rest stay explicit while Priest regeneration uses its transformed name',()=>{
 const skills=[
  {id:'job:cleric:mend',cleric_kind:'mend',name:'Mend',range:1,target:'ally',availability:{available:true,uses_remaining:3}},
  {id:'job:cleric:rest',cleric_kind:'rest',name:'Rest',range:1,self_only:true,availability:{available:true}},
  {id:'job:cleric:sanctuary',cleric_kind:'sanctuary',name:'Regeneration',range:1,self_only:true,availability:{available:true}}
 ];
 const html=hotbarMarkup({skills,cleric_rest:{turns:2}},0,null,esc);
 assert.match(html,/3 left/);assert.match(html,/>End Rest</);assert.match(html,/>Regeneration</);
 assert.match(html,/Target yourself/);assert.match(html,/assets\/cleric-v1\/sanctuary.png/);
});
test('hotbar preserves all skills and assigns ten keys per page',()=>{
 const skills=Array.from({length:23},(_,i)=>({id:`skill-${i}`,name:`Skill ${i}`,description:'Description',source_kind:i<5?'character':'gear',availability:{available:true},range:2,target:'enemy'}));
 const actor={skills};assert.equal(hotbarPage(actor,0).pages,3);assert.equal(hotbarPage(actor,1).skills.length,10);assert.equal(hotbarPage(actor,99).skills.length,3);
 const markup=hotbarMarkup(actor,0,null,esc);assert.equal((markup.match(/data-hotbar-key=/g)||[]).length,10);assert.ok(markup.includes('data-hotbar-key="0"'));
});
test('skill readiness and selected state are shown without changing abilities',()=>{
 const actor={skills:[{id:'bind',name:'Binding Line',description:'Bind',availability:{available:false,reason:'Cooldown'},range:2,target:'enemy'}]};
 const markup=hotbarMarkup(actor,0,'bind',esc);assert.ok(markup.includes('disabled'));assert.ok(markup.includes('aria-pressed="true"'));assert.ok(markup.includes('Cooldown'));
});
test('active Bard Songs expose an explicit Stop Playing command',()=>{
 const skills=[
  {id:'job:bard:war_anthem',name:'War Anthem',bard_kind:'war_anthem',source_kind:'character',availability:{available:true},range:0,target:'self'},
  {id:'job:bard:accelerando',name:'Accelerando',bard_kind:'accelerando',source_kind:'character',availability:{available:true},range:0,target:'self'}
 ];
 const html=hotbarMarkup({bard_song:'war_anthem',skills},0,null,esc);
 assert.match(html,/data-hotbar-stop-song="true"/);
 assert.match(html,/>Stop Playing</);
 assert.match(html,/Stop war anthem first/);
});
test('unit inspection explains statuses, guard and remaining time',()=>{
 const html=unitInspectMarkup({name:'Raider',hp:20,max_hp:30,armor:2,move:4,guarding:true,statuses:[{id:'vulnerable',turns:1}]},{vulnerable:{name:'Vulnerable',icon:'v',description:'The next direct hit ignores 3 armor.'}},esc);
 assert.ok(html.includes('25% less damage'));assert.match(html,/ignores 3 Armor/i);assert.ok(html.includes('1 target turn'));assert.ok(html.includes('20/30 HP'));
});

test('hover forecast distinguishes damage on hit, accuracy, barrier and interception',()=>{
 const html=unitInspectMarkup({name:'Guard',race:'Goblin',hp:20,max_hp:30,attack:9,armor:10,effective_armor:7,move:5,weapon:'Cudgel'}, {},esc,
  {damage_on_hit:11,chance:80,absorbed_damage:5,intercepted_by:'Protector',move_to:{x:2,y:2},movement_cost:3});
 assert.match(html,/11 HP damage on hit/);assert.match(html,/80% accuracy/);
 assert.match(html,/Barrier absorbs 5/);assert.match(html,/Intercepted by Protector/);
 assert.match(html,/Approach: 3 movement/);assert.match(html,/title="Armor">ARM<\/abbr><\/dt><dd>7<\/dd>/);
 assert.match(html,/Cudgel/);
});

test('cursor card follows the lower right and stays within screen edges',()=>{
 assert.deepEqual(cursorCardPosition(100,100,390,500,1440,900),{left:118,top:118});
 assert.deepEqual(cursorCardPosition(1400,880,390,500,1440,900),{left:1042,top:392});
});

test('area forecasts show each affected enemy, excluding allies and absent enemies',()=>{
 const battle={width:8,height:8,current_unit_id:'p',units:{p:{id:'p',team:'player',alive:true,x:2,y:2},a:{id:'a',team:'enemy',alive:true,x:3,y:2},b:{id:'b',team:'enemy',alive:true,x:4,y:2},c:{id:'c',team:'enemy',alive:true,x:7,y:7}}};
 const preview={zones:[{kind:'impact',cells:[{x:3,y:2},{x:4,y:2}]}],target_forecasts:{a:{damage_on_hit:24,chance:80,push:2,resistance:0},b:{damage_on_hit:19,chance:75,push:1,resistance:50}}};
 const html=areaForecastMarkup(preview,battle,esc);
 assert.equal((html.match(/data-aoe-preview=/g)||[]).length,2);assert.match(html,/24 damage/);assert.match(html,/19 damage/);assert.match(html,/50% resist/);assert.doesNotMatch(html,/data-aoe-preview="[pc]"/);
});

test('cooldowns use a large overlay and keep counts when the main action is spent',()=>{
 const skill={id:'rally',name:'Hold Together',description:'Support',range:1,target:'ally',availability:{available:false,cooldown_remaining:4,uses_remaining:null,reason:'Ready in 4 turns'}};
 const html=hotbarMarkup({acted:true,skills:[skill]},0,null,esc);
 assert.match(html,/class="skill-cooldown" aria-hidden="true">4</);
 assert.match(html,/cooling-down/);assert.match(html,/Ready in 4 turns/);
 assert.doesNotMatch(html,/<small>Ready/);
 const ready=hotbarMarkup({skills:[{...skill,availability:{available:true,cooldown_remaining:0,uses_remaining:null}}]},0,null,esc);
 assert.doesNotMatch(ready,/class="skill-cooldown"/);assert.doesNotMatch(ready,/<small>Ready/);
});

test('AoE forecasts warn for self and allies without colouring enemy damage as friendly fire',()=>{
 const units=Object.fromEntries(['self','ally','enemy'].map((id,x)=>[id,{id,team:id==='enemy'?'enemy':'player',alive:true,x,y:0}]));
 const html=areaForecastMarkup({zones:[{kind:'impact',cells:[{x:0,y:0},{x:1,y:0},{x:2,y:0}]}],target_forecasts:Object.fromEntries(Object.keys(units).map(id=>[id,{damage_on_hit:20,chance:100}]))},{width:8,height:8,current_unit_id:'self',units},esc);
 assert.equal((html.match(/friendly-fire-forecast/g)||[]).length,2);
 assert.match(html,/You &middot; 20 damage/);assert.match(html,/Ally &middot; 20 damage/);
 assert.match(html,/class="aoe-preview-chip "[^>]+data-aoe-preview="enemy"/);
});


test('Stop Playing stays available without a misleading restart cooldown overlay',()=>{
 const skill={id:'job:bard:song_of_peace',name:'Song of Peace',bard_kind:'song_of_peace',range:1,target:'ally',availability:{available:false,cooldown_remaining:4,reason:'Ready in 4 of your turns'}};
 const html=hotbarMarkup({bard_song:'song_of_peace',skills:[skill]},0,null,esc);
 assert.match(html,/Stop now using your main action/);
 assert.doesNotMatch(html,/class="skill-cooldown"|cooling-down|Ready in 4/);
 assert.match(html,/aria-disabled="false"/);
});


test('ordinary Song preview labels only recipients; Peace includes caster and enemies',()=>{
 const units={bard:{id:'bard',team:'player',alive:true,x:0,y:0},ally:{id:'ally',team:'player',alive:true,x:1,y:0},enemy:{id:'enemy',team:'enemy',alive:true,x:1,y:1}};
 const battle={units,width:5,height:5,current_unit_id:'bard'};
 const zone={kind:'bard_song',song:'war_anthem',cells:Object.values(units).map(({x,y})=>({x,y}))};
 const war=areaForecastMarkup({zones:[zone]},battle,esc);
 assert.match(war,/data-aoe-preview="ally"/);assert.doesNotMatch(war,/data-aoe-preview="(?:bard|enemy)"/);
 const peace=areaForecastMarkup({zones:[{...zone,song:'song_of_peace'}]},battle,esc);
 assert.equal((peace.match(/data-aoe-preview=/g)||[]).length,3);
});

test('unit stat help is keyboard accessible and uses server-provided calculations',()=>{
 const html=unitInspectMarkup({name:'Fighter',hp:30,max_hp:50,attack:20,armor:10,effective_armor:7,stat_explanations:{Armor:'10 armor minus 3 fracture = 7',Health:'24 plus VIT times 4'},statuses:[]},{},String);
 assert.match(html,/10 armor minus 3 fracture = 7/);assert.match(html,/24 plus VIT times 4/);assert.match(html,/inspect-stat[^>]*tabindex="0"/);
});

test('compact unit hover keeps essential forecasts and right-click hint without full passive prose',()=>{
 const unit={name:'Enemy',hp:20,max_hp:30,attack:10,armor:3,job_description:'Long job description',passives:[{name:'Long passive',description:'Detailed passive explanation'}],statuses:[{id:'poison',stacks:4},{id:'armor_fracture',turns:2}]};
 const html=unitInspectMarkup(unit,{},String,{damage_on_hit:12,chance:90},null,{compact:true});
 assert.match(html,/12 HP damage on hit/);assert.match(html,/Right-click to inspect stats and effects/);assert.match(html,/compact-effect/);assert.doesNotMatch(html,/Long job description|Detailed passive explanation/);
 const full=unitInspectMarkup(unit,{},String);assert.match(full,/Detailed passive explanation/);assert.match(full,/Right-click an effect to keep its details open/);
});

test('full details put bounded effect cards beneath the stats rather than in an unequal side column',()=>{
 const unit={name:'Boss',hp:70,max_hp:100,statuses:Array.from({length:12},(_,i)=>({id:'mark',quarry:true,source_id:String(i),source_name:'Ranger '+i,turns:3}))};
 const html=unitInspectMarkup(unit,{},String);
 assert.match(html,/unit-detail-summary/);assert.match(html,/unit-stat-strip/);assert.match(html,/unit-detail-effects/);assert.match(html,/effect-card-grid/);
 assert.equal((html.match(/class="effect-detail-card"/g)||[]).length,12);assert.doesNotMatch(html,/inspect-columns|inspect-overview/);
 assert.ok(html.indexOf('unit-stat-strip')<html.indexOf('unit-detail-effects'));
});
