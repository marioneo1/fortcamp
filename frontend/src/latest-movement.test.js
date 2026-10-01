import test from 'node:test';
import assert from 'node:assert/strict';
import {createLatestMovement} from './latest-movement.js';
test('rapid movement coalesces to the latest destination instead of replaying every click',()=>{
  const queue=createLatestMovement();
  for(let x=0;x<100;x++)queue.remember({action:'move',x,y:2},'battle:unit:1');
  assert.deepEqual(queue.take('battle:unit:1'),{action:'move',x:99,y:2});
  assert.equal(queue.take('battle:unit:1'),null);
});
test('pending movement cannot leak into a new actor, activation or battle',()=>{
  for(const context of ['other:unit:1','battle:other:1','battle:unit:2']){
    const queue=createLatestMovement();queue.remember({action:'move',x:1,y:2},'battle:unit:1');
    assert.equal(queue.take(context),null);assert.equal(queue.take('battle:unit:1'),null);
  }
});
test('closing a battle discards pending movement and remembers a copy of the command',()=>{
  const queue=createLatestMovement(),command={action:'move',x:1,y:2};queue.remember(command,'a');command.x=99;
  assert.equal(queue.take('a').x,1);queue.remember(command,'a');queue.clear();assert.equal(queue.take('a'),null);
});
