import {test} from 'node:test';
import assert from 'node:assert/strict';
import {statusDetails,tacticalPreviewText} from './combat-status-ui.js';
import {describeGear} from './equipment-ui.js';
test('statuses show finite absorption, owner, clock and reaction availability',()=>{
 assert.match(statusDetails({id:'barrier',amount:6,turns:1,expiry:'target_end'}).details.join(' '),/6 damage.*activation end/);
 assert.match(statusDetails({id:'mark',source_name:'Aya',accuracy:10,turns:2}).details.join(' '),/Owner: Aya.*10 accuracy/);
 assert.equal(statusDetails({id:'reaction',ready:false,reactions:['Riposte']}).name,'Reaction spent');
 assert.match(statusDetails({id:'footing',resistance:25}).description,/25%/);
 assert.match(statusDetails({id:'poison',turns:2,expiry:'target_start'}).details.join(' '),/2 damage ticks/);
});
test('previews explain redirection, resistance, collision and lethal loot loss',()=>{
 const text=tacticalPreviewText({intercepted_by:'Guard',barrier:6,tactics:[{type:'push',destination:{x:4,y:2},resistance:25,pit:'lethal',blocked:null}]});
 assert.match(text,/Intercepted by Guard/);assert.match(text,/cell 5, 3/);assert.match(text,/25% resistance/);assert.match(text,/body and gear lost/);
 assert.match(tacticalPreviewText({tactics:[{type:'pull',destination:{x:1,y:2},resistance:0,blocked:'Wall',collision_damage:2}]}),/Stopped: Wall.*2 collision damage/);
 assert.equal(tacticalPreviewText(null),'');
 assert.match(describeGear({combat_reaction:{name:'Riposte',description:'Half-power counter.'}},{}).join(' '),/Reaction.*Riposte/);
});
