import {test} from 'node:test';
import assert from 'node:assert/strict';
import {loadoutSelection} from './job-loadout-rules.js';
test('active and passive IDs share five slots and can always be removed',()=>{
  const full=['a','b','c','passive1','passive2'];
  assert.deepEqual(loadoutSelection(full,'d'),full);
  assert.deepEqual(loadoutSelection(full,'passive1'),['a','b','c','passive2']);
  assert.deepEqual(loadoutSelection(['a'],'b'),['a','b']);
  assert.deepEqual(full,['a','b','c','passive1','passive2']);
});
