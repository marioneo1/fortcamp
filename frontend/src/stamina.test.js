import test from 'node:test';
import assert from 'node:assert/strict';
import {staminaView,staminaCosts,staminaLabel} from './stamina.js';
import {rankedCandidates} from './mission-planner.js';

test('recovery handles fractional points, debt, offline time and the cap',()=>{
  const c={stamina:{balance:-99,updated_at:1000}};
  assert.equal(staminaView(c,2799).eligible,false);
  assert.equal(staminaView(c,2800).current,1);
  assert.equal(staminaView(c,4582).current,100);
  assert.equal(staminaView(c,999).current,-99);
  assert.equal(staminaView({},1000).current,100);
  assert.match(staminaLabel(c,1000),/Ready in 30m 0s/);
});
test('team suggestions exclude tired units without excluding borrowing candidates',()=>{
  const now=Date.now()/1000;
  const rows=[{id:'tired',name:'Tired',status:'idle',score:100,stamina:{balance:-99,updated_at:now}},
    {id:'borrow',name:'Borrow',status:'idle',score:1,stamina:{balance:1,updated_at:now}}];
  assert.deepEqual(rankedCandidates(rows,c=>c.score).map(r=>r.character.id),['borrow']);
  assert.deepEqual(staminaCosts,{E:1,D:3,C:5,B:10,A:50,S:100});
});
