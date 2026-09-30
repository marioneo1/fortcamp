import {Renderer,Texture} from '@pixi/core';
import {Container} from '@pixi/display';
import {Sprite} from '@pixi/sprite';
import '@pixi/extract';
import {Emitter} from '@pixi/particle-emitter';
import {createParticlePreset,WindBehavior} from './particle-presets.js';
import {vfxTextures} from './vfx-textures.js';

Emitter.registerBehavior(WindBehavior);
const DECOR={arcane:['glyph_cyan','glyph_violet','arcane_ribbon'],starfall:['alien_comet']};
export async function createParticleRenderer({canvas,width,height}){
  // No Application or shared ticker: the board owns one loop and suspension.
  const renderer=new Renderer({view:canvas,width,height,resolution:Math.min(1,1920/width),backgroundAlpha:0,antialias:false,powerPreference:'low-power'});
  const stage=new Container(),layers=new Container(),ornaments=new Container();stage.addChild(layers,ornaments);
  let emitters=[],sprites=[],theme=null,version=0,time=0,destroyed=false;
  const textureCache=new Map();
  function texture(name){if(!textureCache.has(name)){const image=vfxTextures.get(name);if(image)textureCache.set(name,Texture.from(image))}return textureCache.get(name)}
  function clear(){emitters.forEach(e=>e.destroy());emitters=[];layers.removeChildren();ornaments.removeChildren().forEach(s=>s.destroy());sprites=[]}
  function ornament(name,x,y,size,alpha,speed){
    const tex=texture(name);if(!tex)return;
    const s=new Sprite(tex);s.anchor.set(.5);s.position.set(width*x,height*y);s.scale.set(size/tex.width);s.alpha=alpha;
    ornaments.addChild(s);sprites.push({sprite:s,name,x,y,alpha,speed});
  }
  async function setTheme(next){
    theme=next;const request=++version,presets=createParticlePreset(next,width,height);
    const names=[...new Set([...presets.flatMap(p=>p.config.behaviors.find(b=>b.type==='textureRandom').config.textures),...(DECOR[next]||[])])];
    await vfxTextures.load(names);if(destroyed||request!==version)return false;
    clear();time=0;
    for(const {config} of presets){
      const behavior=config.behaviors.find(b=>b.type==='textureRandom'),available=behavior.config.textures.map(texture).filter(Boolean);
      if(!available.length)continue;behavior.config.textures=available;emitters.push(new Emitter(layers,config));
    }
    if(next==='arcane'){
      ornament('glyph_cyan',.1,.3,220,.25,.028);ornament('glyph_violet',.9,.7,190,.2,-.023);ornament('arcane_ribbon',.9,.24,270,.1,.01);
    }
    if(next==='starfall')ornament('alien_comet',.9,.1,120,0,0);
    // Seed an established atmosphere, also used for reduced-motion stills.
    for(let i=0;i<80;i++)emitters.forEach(e=>e.update(.25));
    render();return true;
  }
  function update(dt){
    time+=dt;emitters.forEach(e=>e.update(dt));
    for(const d of sprites){
      const s=d.sprite;
      if(d.name==='alien_comet'){
        const phase=(time%19)/19,a=(phase-.3)/.2;
        s.visible=a>0&&a<1;s.alpha=s.visible?Math.sin(a*Math.PI)*.5:0;s.position.set(width*(.95-a*.78),height*(.04+a*.6));
      }else{s.rotation+=d.speed*dt;s.alpha=d.alpha*(.88+Math.sin(time*.4+d.x*8)*.12)}
    }
  }
  function render(){if(!destroyed)renderer.render(stage)}
  return {
    setTheme,update,render,
    resize(w,h){width=w;height=h;renderer.resolution=Math.min(1,1920/w);renderer.resize(w,h)},
    diagnostics(){return {renderer:'pixi',particles:emitters.reduce((n,e)=>n+e.particleCount,0),emitters:emitters.length,theme,viewport:[width,height]}},
    pixelSignature(){const p=renderer.extract.pixels(stage);let hash=0;for(let i=0;i<p.length;i+=32)hash=(hash*31+p[i]+p[i+3])|0;return hash},
    destroy(){if(destroyed)return;destroyed=true;version++;clear();stage.destroy({children:true});textureCache.forEach(t=>t.destroy(true));renderer.destroy(false)},
  };
}
