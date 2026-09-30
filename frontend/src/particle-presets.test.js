import {test} from 'node:test';
import assert from 'node:assert/strict';
import {PARTICLE_PRESETS,createParticlePreset,WindBehavior} from './particle-presets.js';
import {Emitter} from '@pixi/particle-emitter';
import {Container} from '@pixi/display';
import {Texture} from '@pixi/core';
test('all presets cap particles, fade at both ends and disable independent tickers',()=>{
  for(const name of PARTICLE_PRESETS){
    const layers=createParticlePreset(name,1440,900);assert.ok(layers.length);
    assert.ok(layers.reduce((n,l)=>n+l.config.maxParticles,0)<=80);
    for(const {config:c} of layers){assert.equal(c.autoUpdate,false);const alpha=c.behaviors.find(b=>b.type==='alpha').config.alpha.list;assert.equal(alpha[0].value,0);assert.equal(alpha.at(-1).value,0)}
  }
});
test('leaf rotation does not redirect movement, and uniform scaling preserves aspect ratio',()=>{
  const b=new WindBehavior({velocity:[10,10,20,20],size:[25,25],spin:0,sway:0,grow:1});
  let scale;const p={config:{},texture:{width:100},scale:{set:v=>scale=v},x:0,y:0,age:1,agePercent:.5,next:null};
  b.initParticles(p);p.rotation=Math.PI;b.updateParticle(p,.5);assert.equal(p.x,5);assert.equal(p.y,10);assert.equal(scale,.25);
});
test('the actual emitter spawns finite, visible particles for every preset',()=>{
  Emitter.registerBehavior(WindBehavior);
  for(const name of PARTICLE_PRESETS){
    const parent=new Container(),emitters=[];
    for(const {config} of createParticlePreset(name,1440,900)){
      config.behaviors.find(b=>b.type==='textureRandom').config.textures=[Texture.EMPTY];
      emitters.push(new Emitter(parent,config));
    }
    for(let i=0;i<80;i++)emitters.forEach(e=>e.update(.25));
    assert.ok(parent.children.length>0,name);
    for(const p of parent.children){assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y),name);assert.ok(Number.isFinite(p.scale.x),name)}
    assert.ok(parent.children.some(p=>p.alpha>0),name);emitters.forEach(e=>e.destroy());parent.destroy();
  }
});
