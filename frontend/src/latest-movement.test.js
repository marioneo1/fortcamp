import test from 'node:test';
import assert from 'node:assert/strict';
import {createLatestMovement} from './latest-movement.js';
test('rapid movement coalesces to the latest destination instead of replaying every click',()=>{
  const queue=createLatestMovement();
  for(let x=0;x<100;x++)queue.remember({action:'move',x,y:2},'battle:unit:1');
  assert.equal(queue.peek('battle:other:1'),null);
  const preview=queue.peek('battle:unit:1');preview.x=0;
  assert.equal(queue.peek('battle:unit:1').x,99);
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

test('Guard waits behind the final chosen move and repeated presses cannot queue another turn',()=>{
  const queue=createLatestMovement(),context='lab:actor:1';
  queue.remember({action:'move',x:2,y:3},context);
  queue.remember({action:'move',x:3,y:3},context);
  assert.equal(queue.commit({action:'guard'},context,'move'),true);
  assert.equal(queue.commit({action:'guard'},context),false);
  queue.remember({action:'move',x:9,y:9},context);
  assert.deepEqual(queue.take(context),{action:'move',x:3,y:3});
  assert.equal(queue.hasAction(context),true);
  assert.deepEqual(queue.takeAction(context),{command:{action:'guard'},nextMode:'move'});
  assert.equal(queue.takeAction(context),null);
});
test('buffered actions are discarded after a failed move, scouting interruption or actor change',()=>{
  for(const context of ['lab:actor:2','lab:other:1','other:actor:1']){
    const queue=createLatestMovement();queue.commit({action:'guard'},'lab:actor:1');
    assert.equal(queue.takeAction(context),null);
    assert.equal(queue.takeAction('lab:actor:1'),null);
  }
  const queue=createLatestMovement();queue.commit({action:'attack',target_id:'enemy'},'a');
  queue.clear();assert.equal(queue.hasAction('a'),false);assert.equal(queue.takeAction('a'),null);
});

test('consuming pending work does not discard the chosen position for the following action',()=>{
 const q=createLatestMovement();q.remember({action:'move',x:2,y:1},'turn');
 q.take('turn');assert.deepEqual(q.destination('turn'),{x:2,y:1});
 assert.equal(q.destination('next'),null);q.clear();assert.equal(q.destination('turn'),null);
});
