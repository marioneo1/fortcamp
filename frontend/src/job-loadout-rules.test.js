import {test} from 'node:test';
import assert from 'node:assert/strict';
import {loadoutSelection,jobSkillRows} from './job-loadout-rules.js';
test('active and passive IDs share five slots and can always be removed',()=>{
  const full=['a','b','c','passive1','passive2'];
  assert.deepEqual(loadoutSelection(full,'d'),full);
  assert.deepEqual(loadoutSelection(full,'passive1'),['a','b','c','passive2']);
  assert.deepEqual(loadoutSelection(['a'],'b'),['a','b']);
  assert.deepEqual(full,['a','b','c','passive1','passive2']);
});

test('future skills remain locked and list the successes still required',()=>{
 const job={starter_skills:['a','b'],unlocks:[{skill_id:'c',contracts:2},{skill_id:'d',contracts:5}]};
 const rows=jobSkillRows(job,['a','b','c'],3);
 assert.equal(rows.length,4);assert.equal(rows[2].learned,true);
 assert.equal(rows[3].learned,false);assert.equal(rows[3].remaining,2);
 assert.equal(jobSkillRows(job,['a','b'],0)[2].remaining,2);
});
