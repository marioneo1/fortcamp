import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Texture} from '@pixi/core';
import {updateRibbonVertices} from './particle-ribbons.js';
import {createShootingStar,createMeteorShower} from './particle-comets.js';
import {atmosphereVertices,flameStrength} from './particle-atmosphere.js';
import {createParticlePreset} from './particle-presets.js';
test('gravity and flame shapes move without invalid geometry on narrow and wide boards',()=>{
  for(const width of [390,1440])for(const kind of ['gravity','flame']){
    const a=new Float32Array(128),b=new Float32Array(128);
    atmosphereVertices(a,width,1100,0,{kind,index:0});atmosphereVertices(b,width,1100,1,{kind,index:0});
    assert.ok([...b].every(Number.isFinite));assert.notDeepEqual(a,b);
  }
});
test('campfires have brief bursts and long quiet gaps instead of constant flames',()=>{
  const values=Array.from({length:190},(_,i)=>flameStrength(i/10,0));
  assert.ok(values.every(n=>n>=0&&n<=1));assert.ok(values.filter(n=>n===0).length>130);assert.ok(values.some(n=>n>.5));
});
test('Starfall uses tiny procedural light instead of floating painted cutouts',()=>{
  const presets=createParticlePreset('starfall',1440,1100);
  assert.ok(presets.every(p=>p.config.behaviors.find(b=>b.type==='textureRandom').config.textures.every(n=>n.startsWith('fx:'))));
});
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
test('meteor showers stagger several flights, stay bounded, and leave quiet gaps',()=>{
  const shower=createMeteorShower(()=>Texture.EMPTY,1440,1100,()=>.5);
  let overlap=false,quietAfterBurst=false,maxActive=0;
  for(let i=0;i<500;i++){
    shower.update(.1);const state=shower.diagnostics();maxActive=Math.max(maxActive,state.active);
    if(state.active>1)overlap=true;
    if(state.flights>=8&&!state.queued&&!state.active)quietAfterBurst=true;
    assert.ok(shower.sprites.every(s=>Number.isFinite(s.x)&&Number.isFinite(s.y)));
  }
  assert.ok(overlap);assert.ok(quietAfterBurst);assert.ok(maxActive<=4);assert.ok(shower.diagnostics().flights>=16);shower.destroy();
});
