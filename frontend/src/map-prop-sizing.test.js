import {test} from 'node:test';
import assert from 'node:assert/strict';
import {propArtScale,propVisualSpan} from './map-prop-sizing.js';

test('registered small clutter overrides old enlarged art settings',()=>{
  assert.ok(propArtScale({sprite:'dropped_coin_purse',art_scale:2})<1);
  assert.equal(propArtScale({sprite:'dropped_coin_purse',art_scale:2}),propArtScale({sprite:'dropped_coin_purse'}));
  assert.ok(propArtScale({sprite:'village_well'})>1);
});
test('wall calibration and intentional unregistered sizes survive',()=>{
  assert.equal(propArtScale({sprite:'structure:limestone_wall',edge_wall:true,art_scale:1.25}),1.25);
  assert.equal(propArtScale({sprite:'custom_statue',art_scale:1.7}),1.7);
});
test('tree canopy can cover neighbouring ground without expanding its trunk collision',()=>{
  const footprint=[1,1];assert.deepEqual(propVisualSpan({sprite:'oak_tree'},footprint),[2,2]);
  assert.deepEqual(footprint,[1,1]);assert.deepEqual(propVisualSpan({sprite:'wooden_bed'},[1,2]),[1,2]);
});
