import test from 'node:test';
import assert from 'node:assert/strict';
import {fitMapWidth,wheelZoom} from './battle-camera.js';
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
