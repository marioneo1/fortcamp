// Effekseer 1.70e trial. Shares Pixi's canvas/context and the board's existing clock.
import {burningSources} from './burning-scene.js';
const ROOT='/vendor/effekseer-1.70e/';
let runtimePromise;
export function loadEffekseerRuntime(){
  if(!runtimePromise)runtimePromise=new Promise((resolve,reject)=>{
    const script=document.createElement('script');script.src=ROOT+'effekseer.js';
    script.onerror=()=>reject(Error('Effekseer script failed to load'));
    script.onload=()=>window.effekseer.initRuntime(ROOT+'effekseer.wasm',()=>resolve(window.effekseer),reject);
    document.head.append(script);
  });
  return runtimePromise;
}
export async function createEffekseerFire(renderer,width,height,{load=loadEffekseerRuntime,isCancelled=()=>false}={}){
  const runtime=await load();if(isCancelled())throw Error('Effekseer initialization cancelled');
  const context=runtime.createContext();
  if(!context)throw Error('Effekseer context unavailable');
  let effect;
  try{
    context.init(renderer.gl,{instanceMaxCount:512,squareMaxCount:512});
    context.setRestorationOfStatesFlag(false);renderer.reset();
    await new Promise((resolve,reject)=>{
      const timeout=setTimeout(()=>reject(Error('Effekseer effect load timed out')),15000);
      effect=context.loadEffect('/assets/effekseer/campfire-v1/campfire.efk?v=continuous-20260930',1,()=>{clearTimeout(timeout);resolve()},(message,url)=>{clearTimeout(timeout);reject(Error(`${message}: ${url}`))});
    });
    if(isCancelled())throw Error('Effekseer initialization cancelled');
  }
  catch(error){runtime.releaseContext(context);renderer.reset();throw error}
  let enabled=false,time=0,starts=0,destroyed=false;
  let sources=burningSources(width,height).map(s=>({...s,handle:null}));
  // Orthographic pixel coordinates: world Y rises from the bottom of the viewport.
  function resize(w,h){
    width=w;height=h;context.stopAll();sources=burningSources(width,height).map(s=>({...s,handle:null}));
    context.setProjectionMatrix([2/width,0,0,0,0,2/height,0,0,0,0,-.01,0,-1,-1,0,1]);
    context.setCameraMatrix([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);renderer.reset();
    if(enabled)seedScene();
  }
  resize(width,height);
  function start(source){
    source.handle=context.play(effect,source.x,source.y,0);
    if(source.handle){source.handle.setScale(source.scaleX,source.scaleY,source.scaleY);source.handle.setAllColor(255,185,75,245);starts++}
  }
  function seedScene(){
    // Unequal ages keep the cropped tongues from becoming a synchronized fire border.
    for(const [index,source] of sources.entries()){start(source);context.update(18+index*7)}
    context.update(55);renderer.reset();
  }
  return {
    resize,
    setEnabled(value){
      context.stopAll();enabled=value;time=0;
      for(const source of sources)source.handle=null;
      // Seed a visible established fire for static/reduced-motion composition.
      if(enabled)seedScene();renderer.reset();
    },
    update(dt){
      if(!enabled||destroyed)return;time+=dt;
      for(const source of sources){
        // Native emitters run continuously; particles still curl, age and fade independently.
        if(!source.handle?.exists)start(source);
        if(source.handle?.exists){
          const swell=1+.07*Math.sin(time*.53+source.phase)+.035*Math.sin(time*1.17+source.phase);
          source.handle.setScale(source.scaleX,source.scaleY*swell,source.scaleY);
        }
      }
      context.update(dt*60);
    },
    draw(){if(enabled&&!destroyed){context.draw();renderer.reset()}},
    diagnostics(){return {engine:'effekseer',enabled,starts,active:sources.filter(s=>s.handle?.exists).length,instances:512-context.getRestInstancesCount(),time}},
    destroy(){if(destroyed)return;destroyed=true;context.stopAll();context.releaseEffect(effect);runtime.releaseContext(context);renderer.reset()},
  };
}
