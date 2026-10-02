import test from 'node:test';
import assert from 'node:assert/strict';
import {fitMapWidth} from './battle-camera.js';
import {readHideDetails,saveHideEquipped} from './equipment-ui.js';

test('fit view preserves map proportions within both viewport dimensions',()=>{
  for(const [w,h,vw,vh] of [[8,8,900,500],[24,8,700,500],[8,24,900,500],[16,16,320,230]]){
    const width=fitMapWidth(w,h,vw,vh);
    assert.ok(width<=vw);assert.ok(width*h/w<=vh);
  }
});
test('gear detail preference starts visible and remembers independent hide choice',()=>{
  const values=new Map(),storage={getItem:key=>values.get(key),setItem:(key,value)=>values.set(key,value)};
  assert.equal(readHideDetails(storage,'details'),false);
  saveHideEquipped(storage,'details',true);assert.equal(readHideDetails(storage,'details'),true);
  saveHideEquipped(storage,'details',false);assert.equal(readHideDetails(storage,'details'),false);
});
