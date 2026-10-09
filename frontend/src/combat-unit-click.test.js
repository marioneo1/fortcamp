import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {attackCommand,selectedSkillCommand} from './combat-targeting.js';

// Exercise the real bindings, including the branch that previously opened a
// generic Move & Attack menu instead of executing the selected technique.
const main=readFileSync(new URL('./main.js',import.meta.url),'utf8');
const unitStart=main.indexOf("$$('[data-battle-unit]').forEach(token=>token.onclick=e=>{");
const unitCode=main.slice(unitStart,main.indexOf("$$('[data-battle-object]').forEach",unitStart));
const cellStart=main.lastIndexOf("$$('[data-battle-cell]').forEach(cell=>cell.onclick=",unitStart);
const cellCode=main.slice(cellStart,unitStart);
function bind({mode='skill',target='enemy',preview={},skill={id:'job:fighter:bash',name:'Driving Strike',target:'enemy'},cell=false}={}){
 const sent=[],renders=[],unit={id:target,team:target==='enemy'?'enemy':'player',alive:true,conscious:true,x:4,y:2};
 const actor={id:'hero',skills:[skill],special:skill};
 const b={seed:'click-qa',current_unit_id:'hero',units:{hero:actor,[target]:unit},attack_previews:{[target]:{[mode]:preview}}};
 const button={dataset:cell?{battleCell:'4,2'}:{battleUnit:target}};
 const c={b,current:actor,selectedCombatAction:mode,selectedGearSkills:new Map(),bardCueAllyId:null,bardCueActorId:null,bardCueSkillId:null,
  tileActionMenu:null,retreatAllArmed:false,contextMenuOpen:false,throwTargets:new Set(),contextActions:[],
  $$:()=>[button],attackCommand,renderBattle:()=>renders.push(true),
  tileActionsForBattle:()=>['attack','skill','subdue'].map(action=>({command:{action,target_id:target}})),
  sendCombat:command=>sent.push(selectedSkillCommand(command,actor))};
 vm.createContext(c);vm.runInContext(cell?cellCode:unitCode,c);
 button.onclick({stopPropagation(){}});
 return {sent:JSON.parse(JSON.stringify(sent)),renders,c};
}

for(const [name,skill,target] of [
 ['Driving Strike',{id:'job:fighter:bash',target:'enemy'},'enemy'],
 ['Ranger shot',{id:'job:ranger:poison_attack',target:'enemy'},'enemy'],
 ['Monk follow-up',{id:'job:monk:iron_reversal',target:'enemy'},'enemy'],
 ['Captor technique',{id:'job:captor:bola',target:'enemy'},'enemy'],
 ['Ally healing',{id:'job:cleric:mend',target:'ally'},'ally'],
 ['Ally protection',{id:'job:druid:living_armor',target:'ally'},'ally'],
])test(`${name} executes the selected skill with or without an approach`,()=>{
 for(const preview of [{chance:91},{chance:91,move_to:{x:3,y:2},movement_cost:2}]){
  const {sent,renders}=bind({skill,target,preview});
  assert.deepEqual(sent,[{action:'skill',skill_id:skill.id,target_id:target,...(preview.move_to?{move_to:preview.move_to}:{})}]);
  assert.equal(renders.length,0);
 }
});
test('Subdue executes its approach without a generic attack menu',()=>{
 const {sent,renders}=bind({mode:'subdue',preview:{move_to:{x:3,y:2}}});
 assert.deepEqual(sent,[{action:'subdue',target_id:'enemy',move_to:{x:3,y:2}}]);assert.equal(renders.length,0);
});
test('an invalid selected skill never offers basic Attack as a substitute',()=>{
 const {sent,renders,c}=bind({preview:null});
 assert.deepEqual(sent,[]);assert.equal(renders.length,0);assert.equal(c.tileActionMenu,null);
});
test('clicking the enemy floor respects the selected skill despite other available actions',()=>{
 const {sent,renders}=bind({cell:true});
 assert.deepEqual(sent,[{action:'skill',target_id:'enemy',skill_id:'job:fighter:bash'}]);assert.equal(renders.length,0);
});
