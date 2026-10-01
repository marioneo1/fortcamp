import test from 'node:test';
import assert from 'node:assert/strict';
import {reserveContract,reservationMarkup} from './mission-reservation-ui.js';

test('temporary gateway failure retries the same reservation exactly once',async()=>{
  const calls=[];let retries=0;
  const response=await reserveContract(async(path,options)=>{calls.push({path,options});if(calls.length===1)throw Object.assign(new Error('gateway'),{status:502});return {mission:{status:'reserved'}}},'same-contract',{delay:async()=>{},onRetry:()=>retries++});
  assert.equal(response.mission.status,'reserved');assert.equal(retries,1);assert.equal(calls.length,2);assert.deepEqual(calls[0],calls[1]);assert.equal(calls[0].options.body,'{}');
});
test('budget rejections and authentication errors are not retried',async()=>{
  for(const status of [409,401,403]){let calls=0;await assert.rejects(reserveContract(async()=>{calls++;throw Object.assign(new Error('rejected'),{status})},'id',{delay:async()=>{}}));assert.equal(calls,1)}
});
test('persistent gateway failure is bounded and returned to the panel',async()=>{
  let calls=0;await assert.rejects(reserveContract(async()=>{calls++;throw Object.assign(new Error('gateway'),{status:504})},'id',{delay:async()=>{}}),/gateway/);assert.equal(calls,2);
});
test('claim panel shows allowance, delayed assignment and rolled rewards without a team selector',()=>{
  const html=reservationMarkup({rank:'E',name:'<Contract>',party_size:1,description:'A local job.',reward_preview:['Rare boots']},{cost:1,remaining:0,phase:'free'});
  assert.match(html,/&lt;Contract&gt;/);assert.match(html,/Free-for-all/);assert.match(html,/24 hours to start/);assert.match(html,/0 left/);assert.match(html,/Special drops are rolled/);assert.match(html,/id="reserve-contract"[^>]*disabled/);assert.doesNotMatch(html,/planner-assignment/);
});
