import test from 'node:test';
import assert from 'node:assert/strict';
import {restartWalking,trackBattleAnimation} from './live-dom.js';
const token=()=>{
  const classes=new Set();return {classes,classList:{add:c=>classes.add(c),remove:c=>classes.delete(c)},getBoundingClientRect:()=>({x:200,y:100,width:40,height:40}),getAnimations:()=>[]};
};
const animation=()=>{
  const result=new EventTarget();result.cancelCount=0;result.cancel=()=>{result.cancelCount++;result.dispatchEvent(new Event('cancel'))};return result;
};
test('retargeting starts at the currently drawn position and cancels the old glide',()=>{
  const t=token(),a=animation();t.getAnimations=()=>[a];
  assert.deepEqual(restartWalking(t,{x:195,y:110}),{x:-25,y:-10});assert.equal(a.cancelCount,1);
});
test('a cancelled earlier glide does not clear the replacement walking state',()=>{
  const t=token(),old=animation(),next=animation();trackBattleAnimation(t,old,'is-walking');trackBattleAnimation(t,next,'is-walking');
  old.cancel();assert.equal(t.classes.has('is-walking'),true);
  next.dispatchEvent(new Event('finish'));assert.equal(t.classes.has('is-walking'),false);assert.equal(next.cancelCount,1);
});
test('finished effects release their animation and completion callback runs only once',()=>{
  const t=token(),a=animation();let completions=0;trackBattleAnimation(t,a,'is-hit',()=>completions++);
  a.dispatchEvent(new Event('finish'));assert.equal(completions,1);assert.equal(a.cancelCount,1);assert.equal(t.classes.has('is-hit'),false);
});
