import test from 'node:test';
import assert from 'node:assert/strict';
import {createHoverScheduler} from './combat-hover.js';
function clock(){let id=0;const frames=new Map();return {requestFrame:fn=>{frames.set(++id,fn);return id},cancelFrame:id=>frames.delete(id),get count(){return frames.size},flush(){const next=[...frames.values()];frames.clear();next.forEach(fn=>fn())}}}
test('pointer bursts render once per frame using the latest target and coordinates',()=>{
 const time=clock(),painted=[],hover=createHoverScheduler((...args)=>painted.push(args),time);
 for(let i=0;i<100;i++)hover.show('enemy',{x:i,y:i});
 assert.equal(time.count,1);assert.equal(painted.length,0);time.flush();assert.deepEqual(painted,[['enemy',{x:99,y:99}]]);
 hover.show('ally',{x:200,y:20});time.flush();assert.equal(painted.length,2);assert.equal(painted[1][0],'ally');
});
test('leaving or rebinding cancels a pending hover rather than showing a stale card',()=>{
 const time=clock(),painted=[],hover=createHoverScheduler(x=>painted.push(x),time);
 hover.show('old enemy');hover.cancel();time.flush();assert.deepEqual(painted,[]);
 hover.show('new enemy');time.flush();assert.deepEqual(painted,['new enemy']);
});

test('switching units has no intent delay and a fast sweep renders only its latest target',()=>{
 const time=clock(),painted=[],hover=createHoverScheduler(id=>painted.push(id),time);
 hover.show('a');time.flush();hover.show('b');hover.show('c');time.flush();
 assert.deepEqual(painted,['a','c']);
 hover.show('a');time.flush();assert.deepEqual(painted,['a','c','a']);
});
