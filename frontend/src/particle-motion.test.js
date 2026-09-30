import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Texture} from '@pixi/core';
import {updateRibbonVertices} from './particle-ribbons.js';
import {createShootingStar} from './particle-comets.js';
test('currents deform across the viewport while retaining finite geometry',()=>{
  const a=new Float32Array(160),b=new Float32Array(160),options={y:.3,phase:2,amplitude:80,thickness:70};
  updateRibbonVertices(a,1440,1100,0,options);updateRibbonVertices(b,1440,1100,1,options);
  assert.notDeepEqual(a,b);assert.ok([...b].every(Number.isFinite));assert.ok(a[0]<0&&a.at(-4)>1440);
});
test('shooting stars move quickly, leave their trail behind, then clear and wait',()=>{
  const star=createShootingStar(()=>Texture.EMPTY,1440,1100,()=>0);
  star.update(2.49);assert.equal(star.diagnostics().flights,0);star.update(.02);
  const x=star.head.x;star.update(.1);assert.ok(x-star.head.x>100);
  assert.ok(star.trail.x>star.head.x);assert.ok(star.trail.y<star.head.y);assert.ok(star.trail.width>100);
  for(let i=0;i<20;i++)star.update(.1);
  assert.equal(star.head.visible,false);assert.equal(star.trail.visible,false);assert.equal(star.diagnostics().flights,1);star.destroy();
});
