import test from 'node:test';
import assert from 'node:assert/strict';
import {swapSkillSlots,applySkillOrder,bindSkillSwaps} from './combat-skill-order.js';
import {hotbarSkills,hotbarMarkup} from './combat-hotbar.js';
import {intrinsicTraits} from './combat-traits.js';
import {visibleStatuses,statusVisual} from './combat-status-presentation.js';
const esc=s=>String(s??'');
test('Slotted passives share slots with actives, preserve loadout order and never cast',()=>{
 const actor={skills:[{id:'job:fighter:bash',name:'Bash',source_kind:'character',availability:{available:true}}],passives:[{id:'job:fighter:intercept',type:'passive',name:'Intercept',description:'Redirect a hit',reaction:{id:'intercept'}}],skill_slot_order:['job:fighter:intercept','job:fighter:bash']};
 assert.deepEqual(hotbarSkills(actor).map(s=>s.id),actor.skill_slot_order);
 const html=hotbarMarkup(actor,0,null,esc);
 assert.match(html,/data-hotbar-slot="job:fighter:intercept"/);
 assert.doesNotMatch(html,/data-hotbar-skill="job:fighter:intercept"/);
 assert.match(html,/Equipped passive/);
 assert.equal(intrinsicTraits({...actor,reactions:[{id:'intercept',name:'Intercept'}]}).length,0);
});
test('Swap exchanges positions, preserves source arrays and ignores retired saved IDs',()=>{
 const ids=['a','p','b'],next=swapSkillSlots(ids,'a','b');
 assert.deepEqual(next,['b','p','a']);assert.deepEqual(ids,['a','p','b']);
 assert.deepEqual(swapSkillSlots(ids,'bad','a'),ids);
 assert.deepEqual(applySkillOrder([{id:'a'},{id:'b'},{id:'new'}],['retired','b','b']).map(s=>s.id),['b','a','new']);
});
test('Drag drop swaps only on valid drop; cancelled drag is free',()=>{
 const buttons=['a','b'].map(id=>({dataset:{hotbarSlot:id},classList:{add(){},remove(){}}})),swaps=[];
 const root={querySelectorAll:()=>buttons};bindSkillSwaps(root,(...ids)=>swaps.push(ids));
 const event={dataTransfer:{setData(){}},preventDefault(){},stopPropagation(){}};
 buttons[0].ondragstart(event);buttons[0].ondragend();buttons[1].ondrop(event);assert.equal(swaps.length,0);
 buttons[0].ondragstart(event);buttons[1].ondrop(event);assert.deepEqual(swaps,[['a','b']]);
});
test('Multiple cooldown passives stay distinct on map, with remaining-turn counts',()=>{
 const statuses=visibleStatuses({statuses:[{id:'passive_readiness',source_id:'one',skill_id:'job:barbarian:bloodthirst',cooldown_remaining:2},{id:'passive_readiness',source_id:'two',skill_id:'job:barbarian:unstoppable',cooldown_remaining:3}]});
 assert.equal(statuses.length,2);assert.equal(statusVisual(statuses[0]).count,2);
 assert.match(statusVisual(statuses[1]).image,/unstoppable/);
});
test('Arrange exposes all pages without casting and innate traits remain outside slotted skills',()=>{
 const actor={fury_cap:5,job_description:'Fury rule',race:'Goblin',race_summary:'Fast, fragile',skills:Array.from({length:13},(_,i)=>({id:'gear:'+i,name:'Gear '+i,availability:{available:true}}))};
 const html=hotbarMarkup(actor,0,null,esc,true);
 assert.equal((html.match(/data-hotbar-slot=/g)||[]).length,13);
 assert.doesNotMatch(html,/data-hotbar-skill=/);
 assert.deepEqual(intrinsicTraits(actor).map(p=>p.id),['race','fury']);
});
