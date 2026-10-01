import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createEffekseerFire} from './effekseer-fire.js';
function setup({fail=false}={}){
  const calls={updates:[],plays:0,draws:0,stop:0,releases:0,effects:0,locations:[],projections:[]};
  const context={init(gl,limits){calls.limits=limits},setRestorationOfStatesFlag(){},loadEffect(url,scale,ok,bad){queueMicrotask(()=>fail?bad('missing',url):ok());return {}},setProjectionMatrix:m=>calls.projections.push(m),setCameraMatrix(){},play(effect,x,y){calls.plays++;calls.locations.push([x,y]);return {exists:true,setScale(){},setAllColor(){}}},update:n=>calls.updates.push(n),draw(){calls.draws++},stopAll(){calls.stop++},getRestInstancesCount:()=>480,releaseEffect(){calls.effects++}};
  const runtime={createContext:()=>context,releaseContext(){calls.releases++}},renderer={gl:{},reset(){}};
  return {calls,renderer,runtime};
}
test('Effekseer uses the shared clock, seeds stills, and stops updating outside goblin events',async()=>{
  const s=setup(),fire=await createEffekseerFire(s.renderer,1440,1100,{load:async()=>s.runtime});
  fire.setEnabled(true);assert.equal(s.calls.plays,3);assert.ok(s.calls.updates.every(n=>n>0));
  assert.ok(s.calls.locations.every(([,y])=>y<0),'flame bases stay below the camera');
  fire.update(.1);assert.equal(s.calls.updates.at(-1),6);fire.draw();assert.equal(s.calls.draws,1);
  fire.setEnabled(false);const count=s.calls.updates.length;fire.update(.1);fire.draw();assert.equal(s.calls.updates.length,count);assert.equal(s.calls.draws,1);
  fire.destroy();fire.destroy();assert.equal(s.calls.releases,1);assert.equal(s.calls.effects,1);assert.equal(s.calls.limits.instanceMaxCount,512);
});
test('resize reuses the context and positions the second source against the new edge',async()=>{
  const s=setup(),fire=await createEffekseerFire(s.renderer,1440,1100,{load:async()=>s.runtime});
  fire.resize(390,844);fire.setEnabled(true);fire.update(4.6);
  assert.equal(s.calls.locations.at(-1)[0],390*.85);assert.ok(s.calls.locations.every(([,y])=>y<0));assert.ok(s.calls.projections.at(-1).every(Number.isFinite));fire.destroy();
});
test('missing effect releases its context and cancellation never creates a stale context',async()=>{
  const s=setup({fail:true});await assert.rejects(createEffekseerFire(s.renderer,1440,1100,{load:async()=>s.runtime}),/missing/);assert.equal(s.calls.releases,1);
  let created=false;await assert.rejects(createEffekseerFire(s.renderer,1440,1100,{load:async()=>({createContext(){created=true}}),isCancelled:()=>true}),/cancelled/);assert.equal(created,false);
});
