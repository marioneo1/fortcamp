import test from 'node:test';
import assert from 'node:assert/strict';
import {fitMapWidth,wheelZoom,bindMapPan} from './battle-camera.js';
import {readHideDetails,saveHideEquipped} from './equipment-ui.js';

test('fit view preserves map proportions within both viewport dimensions',()=>{
  for(const [w,h,vw,vh] of [[8,8,900,500],[24,8,700,500],[8,24,900,500],[16,16,320,230]]){
    const width=fitMapWidth(w,h,vw,vh);
    assert.ok(width<=vw);assert.ok(width*h/w<=vh);
  }
});
test('wheel zoom is precise, normalizes device units and bounds extreme gestures',()=>{
  const next=wheelZoom(1,{deltaY:-10,deltaMode:0});assert.ok(next>1&&next<1.05);
  assert.equal(wheelZoom(1,{deltaY:16,deltaMode:0}),wheelZoom(1,{deltaY:1,deltaMode:1}));
  assert.equal(wheelZoom(3,{deltaY:-10000}),3);assert.equal(wheelZoom(.25,{deltaY:10000}),.25);
});
test('gear detail preference starts visible and remembers independent hide choice',()=>{
  const values=new Map(),storage={getItem:key=>values.get(key),setItem:(key,value)=>values.set(key,value)};
  assert.equal(readHideDetails(storage,'details'),false);
  saveHideEquipped(storage,'details',true);assert.equal(readHideDetails(storage,'details'),true);
  saveHideEquipped(storage,'details',false);assert.equal(readHideDetails(storage,'details'),false);
});

test('right click cancels, but right drag, left click and interrupted gestures do not',()=>{
 let cancelled=0,captured=false;const classes=new Set();
 const v={scrollLeft:30,scrollTop:40,classList:{add:x=>classes.add(x),remove:x=>classes.delete(x)},setPointerCapture:()=>captured=true,hasPointerCapture:()=>captured,releasePointerCapture:()=>captured=false};
 bindMapPan(v,()=>cancelled++);
 const e=(type,x=100,y=100,button=2)=>({type,pointerId:1,clientX:x,clientY:y,button,preventDefault(){}});
 v.onpointerdown(e('pointerdown'));v.onpointerup(e('pointerup'));assert.equal(cancelled,1);
 v.onpointerdown(e('pointerdown'));v.onpointermove(e('pointermove',120,110));v.onpointerup(e('pointerup',120,110));assert.equal(cancelled,1);assert.equal(v.scrollLeft,10);assert.equal(v.scrollTop,30);
 v.onpointerdown(e('pointerdown',100,100,0));v.onpointerup(e('pointerup',100,100,0));assert.equal(cancelled,1);
 v.onpointerdown(e('pointerdown'));v.onpointercancel(e('pointercancel'));assert.equal(cancelled,1);assert.equal(classes.size,0);
});

test('right-click inspects the pressed unit; right-drag from a unit only pans',()=>{
 let cancelled=0;const inspected=[],v={scrollLeft:0,scrollTop:0,classList:{add(){},remove(){}},setPointerCapture(){},hasPointerCapture(){return false}};
 bindMapPan(v,()=>cancelled++,(id)=>inspected.push(id));
 const e=(type,x=10)=>({type,button:2,pointerId:1,clientX:x,clientY:10,preventDefault(){},target:{closest(){return {dataset:{battleUnit:'ally'}}}}});
 v.onpointerdown(e('pointerdown'));v.onpointerup(e('pointerup'));assert.deepEqual(inspected,['ally']);assert.equal(cancelled,0);
 v.onpointerdown(e('pointerdown'));v.onpointermove(e('pointermove',30));v.onpointerup(e('pointerup',30));assert.deepEqual(inspected,['ally']);assert.equal(cancelled,0);
});

test('right-click on an owned map effect opens effect details, while dragging still only pans',()=>{
 const inspected=[],v={scrollLeft:0,scrollTop:0,classList:{add(){},remove(){}},setPointerCapture(){},hasPointerCapture(){return false}};
 bindMapPan(v,()=>assert.fail('effect click must not cancel'),(...args)=>inspected.push(args));
 const e=x=>({type:'pointerup',button:2,pointerId:1,clientX:x,clientY:10,preventDefault(){},target:{closest(selector){return selector==='[data-unit-status]'?{dataset:{unitStatus:'mark',statusOwner:'ranger'}}:{dataset:{battleUnit:'boss'}}}}});
 v.onpointerdown(e(10));v.onpointerup(e(10));
 assert.equal(inspected.length,1);assert.equal(inspected[0][0],'boss');assert.deepEqual(inspected[0][2],{id:'mark',owner:'ranger'});
 v.onpointerdown(e(10));v.onpointermove(e(30));v.onpointerup(e(30));assert.equal(inspected.length,1);
});
