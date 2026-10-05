import test from 'node:test';
import assert from 'node:assert/strict';
import {hotbarPage,hotbarMarkup,unitInspectMarkup} from './combat-hotbar.js';
const esc=s=>String(s??'').replaceAll('<','&lt;');
test('hotbar preserves all skills and assigns ten keys per page',()=>{
 const skills=Array.from({length:23},(_,i)=>({id:`skill-${i}`,name:`Skill ${i}`,description:'Description',source_kind:i<5?'character':'gear',availability:{available:true},range:2,target:'enemy'}));
 const actor={skills};assert.equal(hotbarPage(actor,0).pages,3);assert.equal(hotbarPage(actor,1).skills.length,10);assert.equal(hotbarPage(actor,99).skills.length,3);
 const markup=hotbarMarkup(actor,0,null,esc);assert.equal((markup.match(/data-hotbar-key=/g)||[]).length,10);assert.ok(markup.includes('data-hotbar-key="0"'));
});
test('skill readiness and selected state are shown without changing abilities',()=>{
 const actor={skills:[{id:'bind',name:'Binding Line',description:'Bind',availability:{available:false,reason:'Cooldown'},range:2,target:'enemy'}]};
 const markup=hotbarMarkup(actor,0,'bind',esc);assert.ok(markup.includes('disabled'));assert.ok(markup.includes('aria-pressed="true"'));assert.ok(markup.includes('Cooldown'));
});
test('unit inspection explains statuses, guard and remaining time',()=>{
 const html=unitInspectMarkup({name:'Raider',hp:20,max_hp:30,armor:2,move:4,guarding:true,statuses:[{id:'vulnerable',turns:1}]},{vulnerable:{name:'Vulnerable',icon:'v',description:'The next direct hit ignores 3 armor.'}},esc);
 assert.ok(html.includes('25% less damage'));assert.ok(html.includes('ignores 3 armor'));assert.ok(html.includes('1 activation'));assert.ok(html.includes('20/30 HP'));
});

test('hover forecast distinguishes damage on hit, accuracy, barrier and interception',()=>{
 const html=unitInspectMarkup({name:'Guard',race:'Goblin',hp:20,max_hp:30,attack:9,armor:10,effective_armor:7,move:5,weapon:'Cudgel'}, {},esc,
  {damage_on_hit:11,chance:80,absorbed_damage:5,intercepted_by:'Protector',move_to:{x:2,y:2},movement_cost:3});
 assert.match(html,/11 HP damage on hit/);assert.match(html,/80% accuracy/);
 assert.match(html,/Barrier absorbs 5/);assert.match(html,/Intercepted by Protector/);
 assert.match(html,/Approach: 3 movement/);assert.match(html,/<dt>Armor<\/dt><dd>7<\/dd>/);
 assert.match(html,/Cudgel/);
});
