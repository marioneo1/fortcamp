import test from 'node:test';
import assert from 'node:assert/strict';
import {attackCommand,nextCombatMode,approachDescription} from './combat-targeting.js';
test('attack approach sends only target and explicit destination, not a client movement budget',()=>{
 const preview={move_to:{x:3,y:5},movement_cost:2,path:[{x:2,y:5,cost:1}]};
 assert.deepEqual(attackCommand('subdue','enemy',preview),{action:'subdue',target_id:'enemy',move_to:{x:3,y:5}});
 assert.deepEqual(attackCommand('attack','enemy',{}),{action:'attack',target_id:'enemy'});
 assert.match(approachDescription(preview),/2 movement points/);
});
test('used actions return to move; repositioning and intentional carry-to-throw preserve their choice',()=>{
 for(const action of ['attack','subdue','skill','throw','guard','end_turn'])assert.equal(nextCombatMode(action,null,'attack'),'move');
 assert.equal(nextCombatMode('move',null,'move'),'move');assert.equal(nextCombatMode('carry','throw','move'),'throw');
});
