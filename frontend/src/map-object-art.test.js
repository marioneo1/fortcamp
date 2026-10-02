import {test} from 'node:test';
import assert from 'node:assert/strict';
import {paintedObjectSprite,paintedTerrainSprite,paintedDestroyedTerrainSprite} from './map-object-art.js';

test('older saved mission evidence and carts receive art without rewriting the save',()=>{
  for(const id of ['dispatch_satchel','loose_wheel','signal_chart']){
    const saved={id,state:'ground',portable:true};assert.ok(paintedObjectSprite(saved));assert.equal(saved.sprite,undefined);
  }
  assert.equal(paintedTerrainSprite({id:'cart_body',kind:'wagon'}),'prison_wagon');
  assert.equal(paintedTerrainSprite({id:'other_cart',kind:'wagon'}),'wooden_handcart');
  assert.equal(paintedTerrainSprite({kind:'wall'}),'structure:stone_wall_straight');
});
test('spent traps and broken carts retain their own identity while explicit custom art wins',()=>{
  for(const sprite of ['spike_trap','iron_jaw_trap'])assert.equal(paintedDestroyedTerrainSprite({prepared_trap:true,sprite,destroyed_sprite:sprite}),sprite+'_spent');
  assert.equal(paintedDestroyedTerrainSprite({id:'cart_body',kind:'rubble',destroyed_sprite:'structure:wooden_barricade'}),'prison_wagon_broken');
  assert.equal(paintedDestroyedTerrainSprite({id:'cart_body',destroyed_sprite:'custom_wreck'}),'custom_wreck');
  assert.equal(paintedObjectSprite({id:'signal_chart',sprite:'custom_evidence'}),'custom_evidence');
  assert.equal(paintedObjectSprite({id:'alarm_horn',state:'disabled'}),'alarm_bell_disabled');
});
