import {Renderer,Texture} from '@pixi/core';
import {Container} from '@pixi/display';
import '@pixi/extract';
import {Emitter} from '@pixi/particle-emitter';
import {createParticlePreset,WindBehavior} from './particle-presets.js';
import {vfxTextures} from './vfx-textures.js';
import {makeParticleTexture} from './particle-textures.js';
import {createEnergyRibbon} from './particle-ribbons.js';
import {createMeteorShower} from './particle-comets.js';
import {createAtmosphere} from './particle-atmosphere.js';

Emitter.registerBehavior(WindBehavior);
export async function createParticleRenderer({canvas,width,height,fireTrial=true}){
  // No Application or shared ticker: the board owns one loop and suspension.
  const renderer=new Renderer({view:canvas,width,height,resolution:Math.min(1,1920/width),backgroundAlpha:0,antialias:false,powerPreference:'low-power'});
  const stage=new Container(),currents=new Container(),layers=new Container(),ornaments=new Container();stage.addChild(currents,layers,ornaments);
  let emitters=[],ribbons=[],atmosphere=[],comet=null,fire=null,fireLoading=null,fireFailed=false,theme=null,version=0,time=0,destroyed=false;
  const textureCache=new Map();
  function texture(name){if(!textureCache.has(name)){const image=name.startsWith('fx:')?makeParticleTexture(name):vfxTextures.get(name);if(image)textureCache.set(name,Texture.from(image))}return textureCache.get(name)}
  function clear(){emitters.forEach(e=>e.destroy());emitters=[];layers.removeChildren();ribbons.forEach(r=>r.destroy());ribbons=[];atmosphere.forEach(r=>r.destroy());atmosphere=[];currents.removeChildren();comet?.destroy();comet=null;ornaments.removeChildren()}
  async function setTheme(next){
    theme=next;const request=++version,presets=createParticlePreset(next,width,height);
    const names=[...new Set(presets.flatMap(p=>p.config.behaviors.find(b=>b.type==='textureRandom').config.textures))];
    await vfxTextures.load(names.filter(n=>!n.startsWith('fx:')));if(destroyed||request!==version)return false;
    if(next==='goblin'&&fireTrial&&!fire&&!fireFailed){
      try{
        if(!fireLoading)fireLoading=import('./effekseer-fire.js').then(m=>m.createEffekseerFire(renderer,width,height,{isCancelled:()=>destroyed}));
        fire=await fireLoading;fire.resize(width,height);
      }
      catch(error){fireFailed=true;console.warn('Effekseer fire trial unavailable; smoke and sparks remain.',error)}
      if(destroyed){fire?.destroy();fire=null;return false}
      if(request!==version)return false;
    }
    fire?.setEnabled(next==='goblin');
    clear();time=0;
    for(const {config} of presets){
      const behavior=config.behaviors.find(b=>b.type==='textureRandom'),available=behavior.config.textures.map(texture).filter(Boolean);
      if(!available.length)continue;behavior.config.textures=available;emitters.push(new Emitter(layers,config));
    }
    if(next==='arcane'){
      for(const options of [
        {y:.18,phase:0,amplitude:height*.065,thickness:70,tint:0x76bfff,alpha:.42},
        {y:.66,phase:2.3,amplitude:height*.09,thickness:100,tint:0xac85ed,alpha:.34},
        {y:.9,phase:4,amplitude:height*.045,thickness:50,tint:0x6bddd1,alpha:.25},
      ]){const ribbon=createEnergyRibbon(texture('fx:beam'),width,height,options);ribbons.push(ribbon);currents.addChild(ribbon.mesh)}
    }
    if(next==='starfall'){comet=createMeteorShower(texture,width,height);ornaments.addChild(...comet.sprites)}
    if(next==='starfall'){
      for(let i=0;i<2;i++){
        const effect=createAtmosphere(texture('fx:beam'),width,height,'gravity',i);
        atmosphere.push(effect);currents.addChild(effect.mesh);
      }
    }
    // Seed an established atmosphere, also used for reduced-motion stills.
    for(let i=0;i<80;i++)emitters.forEach(e=>e.update(.25));
    render();return true;
  }
  function update(dt){
    time+=dt;emitters.forEach(e=>e.update(dt));ribbons.forEach(r=>r.update(time));atmosphere.forEach(r=>r.update(time));comet?.update(dt);fire?.update(dt);
  }
  function render(){if(!destroyed){renderer.render(stage);fire?.draw()}}
  return {
    setTheme,update,render,
    resize(w,h){width=w;height=h;renderer.resolution=Math.min(1,1920/w);renderer.resize(w,h);fire?.resize(w,h)},
    diagnostics(){return {renderer:'pixi',particles:emitters.reduce((n,e)=>n+e.particleCount,0),emitters:emitters.length,ribbons:ribbons.length,atmosphere:atmosphere.length,fire:fire?.diagnostics(),ornaments:0,comet:comet?.diagnostics(),theme,viewport:[width,height]}},
    pixelSignature(){const p=renderer.extract.pixels(stage);let hash=0;for(let i=0;i<p.length;i+=32)hash=(hash*31+p[i]+p[i+3])|0;return hash},
    destroy(){if(destroyed)return;destroyed=true;version++;fire?.destroy();fire=null;clear();stage.destroy({children:true});textureCache.forEach(t=>t.destroy(true));renderer.destroy(false)},
  };
}
