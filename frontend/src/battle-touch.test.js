import test from 'node:test';
import assert from 'node:assert/strict';
import {bindBattleTouch} from './battle-touch.js';

class Viewport extends EventTarget{
 scrollLeft=40;scrollTop=60;capture=new Set();
 closest(selector){return selector==='[data-battle-unit]'?{dataset:{battleUnit:'enemy'}}:null}
 setPointerCapture(id){this.capture.add(id)}
 hasPointerCapture(id){return this.capture.has(id)}
 releasePointerCapture(id){this.capture.delete(id)}
 send(type,x=100,y=100,id=1,pointerType='touch'){
  const e=new Event(type,{cancelable:true});Object.assign(e,{clientX:x,clientY:y,pointerId:id,pointerType});this.dispatchEvent(e);return e;
 }
}
test('touch taps and desktop mouse events retain normal click behavior',()=>{
 const v=new Viewport(),controller=bindBattleTouch(v);
 v.send('pointerdown');v.send('pointerup');assert.equal(v.send('click').defaultPrevented,false);
 v.send('pointerdown',100,100,1,'mouse');v.send('pointermove',150,150,1,'mouse');v.send('pointerup',150,150,1,'mouse');
 assert.equal(v.scrollLeft,40);assert.equal(v.scrollTop,60);controller.abort();
});
test('a drag pans and suppresses its click without eating the next deliberate tap',()=>{
 const v=new Viewport(),controller=bindBattleTouch(v);
 v.send('pointerdown');v.send('pointermove',130,120);v.send('pointerup',130,120);
 assert.equal(v.scrollLeft,10);assert.equal(v.scrollTop,40);assert.equal(v.send('click').defaultPrevented,true);
 v.send('pointerdown');v.send('pointerup');assert.equal(v.send('click').defaultPrevented,false);controller.abort();
});
test('pinch zoom follows the midpoint and lifting fingers does not issue an action',()=>{
 const v=new Viewport(),zoom=[],controller=bindBattleTouch(v,{zoomAt:()=>1,onZoom:(...args)=>zoom.push(args)});
 v.send('pointerdown',100,100,1);v.send('pointerdown',200,100,2);v.send('pointermove',300,100,2);
 assert.deepEqual(zoom.at(-1),[2,{x:200,y:100}]);v.send('pointerup',300,100,2);v.send('pointerup',100,100,1);
 assert.equal(v.send('click').defaultPrevented,true);assert.equal(v.scrollLeft,40);controller.abort();
});
test('long press opens one inspector and never also clicks the unit',async()=>{
 const v=new Viewport(),inspected=[],controller=bindBattleTouch(v,{onInspect:id=>inspected.push(id)});
 v.send('pointerdown');await new Promise(resolve=>setTimeout(resolve,470));v.send('pointerup');
 assert.deepEqual(inspected,['enemy']);assert.equal(v.send('click').defaultPrevented,true);controller.abort();
});
test('cancelling or rebinding a touch gesture clears pending long press',async()=>{
 const v=new Viewport(),inspect=()=>assert.fail('cancelled hold must not inspect');
 bindBattleTouch(v,{onInspect:inspect});v.send('pointerdown');v.send('pointercancel');
 bindBattleTouch(v,{onInspect:inspect});v.send('pointerdown');const controller=bindBattleTouch(v);
 await new Promise(resolve=>setTimeout(resolve,470));controller.abort();
});
