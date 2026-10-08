import {test} from 'node:test';
import assert from 'node:assert/strict';
import {statusDetails,statusSummary,tacticalPreviewText} from './combat-status-ui.js';
import {describeGear} from './equipment-ui.js';

test('rally area explains both one-use bonuses without undefined zone fields',()=>{
 const text=tacticalPreviewText({zones:[{kind:'rally',cells:[{x:0,y:0}]}]});
 assert.match(text,/next direct hit -25%, next attack \+25%/);
 assert.doesNotMatch(text,/undefined/);
});
test('statuses show finite absorption, owner, clock and reaction availability',()=>{
 assert.match(statusDetails({id:'barrier',amount:6,turns:1,expiry:'target_end'}).details.join(' '),/6 damage.*activation end/);
 assert.match(statusDetails({id:'mark',source_name:'Aya',accuracy:10,turns:2}).details.join(' '),/Owner: Aya.*10 accuracy/);
 assert.equal(statusDetails({id:'reaction',ready:false,reactions:['Riposte']}).name,'Reaction spent');
 assert.match(statusDetails({id:'footing',resistance:25}).description,/25%/);
 assert.match(statusDetails({id:'poison',turns:2,expiry:'target_start'}).description,/10% max HP at turn end/);
 assert.match(statusDetails({id:'deployment',owner_name:'Aya',policy:'commanded',ready:false}).description,/Aya.*owner action.*No extra initiative/);
 assert.match(statusDetails({id:'deployment',owner_name:'Aya',policy:'automatic',ready:true,stationary:true}).details.join(' '),/Ready this owner activation.*Stationary/);
});
test('previews explain redirection, resistance, collision and lethal loot loss',()=>{
 const text=tacticalPreviewText({intercepted_by:'Guard',barrier:6,tactics:[{type:'push',destination:{x:4,y:2},resistance:25,pit:'lethal',blocked:null}]});
 assert.match(text,/Intercepted by Guard/);assert.match(text,/cell 5, 3/);assert.match(text,/25% resistance/);assert.match(text,/body and gear lost/);
 assert.match(tacticalPreviewText({tactics:[{type:'pull',destination:{x:1,y:2},resistance:0,blocked:'Wall',collision_damage:2}]}),/Stopped: Wall.*2 collision damage/);
 assert.equal(tacticalPreviewText(null),'');
 assert.match(describeGear({combat_reaction:{name:'Riposte',description:'Half-power counter.'}},{}).join(' '),/Reaction.*Riposte/);
});

test('Rogue forecast uses readable multipliers without corrupted punctuation',()=>{
 const text=tacticalPreviewText({debuff_stacks:{bleed:3,hobbled:1},exploit_power:300,position_power:200});
 assert.match(text,/Exploit: 4 debuff stacks: 3.0x damage/);assert.match(text,/Cheap Shot: 2.0x positional damage/);assert.doesNotMatch(text,/\?/);
 const poison=statusDetails({id:'poison',stacks:4});assert.match(poison.details.join(' '),/4 turns remaining/);assert.match(poison.description,/extend duration, not damage/);
});

test('compact effect summaries keep damage scopes, owner restrictions and stack meanings',()=>{
 assert.match(statusSummary({id:'poison',stacks:8}),/10%.*duration, not damage/);
 assert.match(statusSummary({id:'burn',stacks:4}),/8%.*minimum 4/);
 assert.match(statusSummary({id:'bleed',layers:[{},{},{}]}),/15%.*Movement does not trigger/);
 assert.match(statusSummary({id:'bard_war_anthem'}),/Direct damage.*excludes DoTs/);
 assert.match(statusSummary({id:'pestilence'}),/including DoTs and collisions/);
 assert.match(statusSummary({id:'mark',quarry:true}),/marking Ranger.*other attackers gain no benefit/);
 const enchant=statusDetails({id:'weapon_enchant',element:'lightning',turns:2,paralyzed_targets:['a']});
 assert.match(enchant.description,/25%.*only once.*not consumed/);assert.doesNotMatch(enchant.description,/20%|Burn/);
});
