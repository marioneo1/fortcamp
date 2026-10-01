import test from 'node:test';import assert from 'node:assert/strict';
import {applyContractUpdate} from './contract-state.js';
test('a reservation leaves the public board immediately without duplicating private entries',()=>{
  const m={id:'one',status:'reserved'},lists={pool:{missions:[{id:'one'},{id:'other'}]},privateContracts:[m],activeMissions:[]};
  const next=applyContractUpdate(lists,m);
  assert.deepEqual(next.pool.missions,[{id:'other'}]);assert.equal(next.privateContracts.length,1);assert.equal(lists.pool.missions.length,2);
});
test('started and finished private contracts disappear while their saved expedition/result stays accessible',()=>{
  const lists={pool:null,privateContracts:[{id:'one'},{id:'other'}],activeMissions:[{id:'one',status:'reserved'}]};
  for(const status of ['decision','battle','claimed','completed']){
    const next=applyContractUpdate(lists,{id:'one',status});assert.deepEqual(next.privateContracts,[{id:'other'}]);
    assert.equal(next.activeMissions.length,1);assert.equal(next.activeMissions[0].status,status);
  }
});
