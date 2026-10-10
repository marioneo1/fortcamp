import test from 'node:test';
import assert from 'node:assert/strict';
import {arrivalMinute,lightingAtMinute,colorMatrix,propShadowKind,footprintIndoors} from './battle-lighting.js';

test('selected props get shorter shadows; floor edging and debris do not',()=>{
 const prop=(art,classes=[])=>({style:{getPropertyValue:()=>art},classList:{contains:name=>classes.includes(name)}});
 assert.equal(propShadowKind(prop('crate_closed.png')),'small');
 assert.equal(propShadowKind(prop('oak_tree.png')),'large');
 assert.equal(propShadowKind(prop('crate_closed.png',['destroyed'])),'none');
 assert.equal(propShadowKind(prop('oak_tree.png',['ground-edging'])),'none');
 assert.equal(propShadowKind(prop('grass_clump.png')),'none');
 const indoor=new Set(['1,1','2,1','1,2','2,2']);
 assert.equal(footprintIndoors(1,1,2,2,indoor),true);
 assert.equal(footprintIndoors(2,1,2,2,indoor),false);
});

test('returning later advances saved arrival light without changing phase',()=>{
 const lighting={phase:'day',arrival_minute:12,arrived_at:1000};
 assert.equal(arrivalMinute(lighting,1000),12);
 assert.equal(arrivalMinute(lighting,1300),17);
 assert.ok(arrivalMinute(lighting,9000)<28);
 assert.equal(lightingAtMinute(arrivalMinute(lighting,9000)).phase,'day');
 assert.equal(arrivalMinute(lighting,999),12);
});
test('all arrival phases stay within their window on a long absence',()=>{
 for(const [phase,minute] of [['day',12],['dusk',29],['night',42],['dawn',59]]){
  assert.equal(lightingAtMinute(arrivalMinute({phase,arrival_minute:minute,arrived_at:0},100000)).phase,phase);
 }
});
test('night has a visible blue grade; daylight and moonlight drift smoothly',()=>{
 const night=lightingAtMinute(42);
 assert.ok(night.rgb[2]>night.rgb[0]*1.5);
 assert.ok(night.rgb[5]>night.rgb[3]);
 assert.notDeepEqual(lightingAtMinute(8).rgb,lightingAtMinute(22).rgb);
 assert.notDeepEqual(lightingAtMinute(33).rgb,lightingAtMinute(44).rgb);
 for(const boundary of [0,12,28,29,30,44,58,59,60]){
  const a=lightingAtMinute(boundary-.001),b=lightingAtMinute(boundary+.001);
  assert.ok(a.rgb.every((v,i)=>Math.abs(v-b.rgb[i])<.01));
  assert.ok(Math.abs(a.angle-b.angle)<.1);
  assert.ok(Math.abs(a.shadow-b.shadow)<.01);
 }
 assert.deepEqual(colorMatrix(night.rgb).split(' ').slice(-5),['0','0','0','1','0']);
});
