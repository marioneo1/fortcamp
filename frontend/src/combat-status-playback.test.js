import test from 'node:test';
import assert from 'node:assert/strict';
import {statusPlaybackPlan} from './combat-status-playback.js';
test('Meteor Burn and later flame entries appear at their individual contacts, not final stack count',()=>{
 const previous={units:{rat:{statuses:[]}}},one=[{id:'burn',layers:[{}]}],two=[{id:'burn',layers:[{},{}]}];
 const battle={units:{rat:{statuses:one}}};
 const timeline=[{start:0,duration:1000,event:{type:'mage_cast'}},{start:420,duration:900,event:{type:'combat_feedback',unit_id:'rat',statuses_snapshot:one}},{start:850,duration:900,event:{type:'combat_feedback',unit_id:'rat',statuses_snapshot:two}}];
 const [plan]=statusPlaybackPlan(previous,battle,timeline);
 assert.deepEqual(plan.initial,[]);assert.deepEqual(plan.changes.slice(0,2),[{at:420,statuses:one},{at:850,statuses:two}]);
 assert.equal(plan.changes.at(-1).final,true);assert.ok(plan.changes.at(-1).at>=1000);assert.deepEqual(plan.changes.at(-1).statuses,one);
});
test('status removals and old recordings reconcile only at playback end',()=>{
 const previous={units:{rat:{statuses:[{id:'burn',stacks:3}]}}},battle={units:{rat:{statuses:[]}}};
 const [plan]=statusPlaybackPlan(previous,battle,[{start:0,duration:500,event:{type:'movement'}}]);
 assert.equal(plan.initial[0].stacks,3);assert.deepEqual(plan.changes,[{at:500,statuses:[],final:true}]);
 assert.deepEqual(statusPlaybackPlan(battle,battle,[]),[]);
});
