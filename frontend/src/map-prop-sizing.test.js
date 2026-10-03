import {test} from 'node:test';
import assert from 'node:assert/strict';
import {propArtScale,propVisualSpan} from './map-prop-sizing.js';
import aliases from './retired-prop-aliases.json' with {type:'json'};
import registry from './map-prop-art.json' with {type:'json'};

test('retired garden artwork falls back to existing approved sprites without changing saved occupancy',()=>{
  for(const [oldSprite,replacement] of Object.entries(aliases)){
    assert.ok(registry[replacement]);assert.equal(registry[oldSprite],undefined);
    assert.equal(propArtScale({sprite:oldSprite}),propArtScale({sprite:replacement}));
    assert.deepEqual(propVisualSpan({sprite:oldSprite},[2,2]),[2,2]);
  }
  assert.ok(Object.values(registry).every(path=>!path.includes('garden-v1')));
});

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
test('connected crop rails and corner stakes retain their explicit modular dimensions',()=>{
 assert.equal(propArtScale({sprite:'horticulture_fence_joined',ground_edging:true,art_scale:1}),1);
 assert.equal(propArtScale({sprite:'horticulture_fence_post',ground_edging:true,art_scale:.18}),.18);
});
