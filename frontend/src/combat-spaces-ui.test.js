import {test} from 'node:test';
import assert from 'node:assert/strict';
import {zoneOverlay,zoneCellHelp} from './combat-spaces-ui.js';
import {statusDetails,tacticalPreviewText} from './combat-status-ui.js';
test('zone cells keep grid position and explain ownership timing and effect',()=>{
 const zones=[{kind:'ember',name:'Ember Patch',owner_name:'Aya',remaining:2,description:'Applies Burn',cells:[{x:2,y:3}]}];
 const html=zoneOverlay(zones,x=>String(x));
 assert.match(html,/grid-column:3;grid-row:4/);
 assert.match(html,/zone-ember/);
 assert.match(zoneCellHelp(zones,2,3),/Aya.*2 owner activations.*Burn/);
 assert.equal(zoneCellHelp(zones,0,0),'');
 assert.match(tacticalPreviewText({zones:[{...zones[0],turns:2}]}),/Ember Patch.*1 tiles.*2 owner activations/);
 assert.match(statusDetails({id:'wild_form',name:'Prowler',description:'Melee form',turns:2}).details[0],/no HP refill/);
});
