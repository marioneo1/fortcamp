// Effekseer 1.70e trial. Shares Pixi's canvas/context and the board's existing clock.
const ROOT='/vendor/effekseer-1.70e/';
let runtimePromise;
function loadRuntime(){
  if(!runtimePromise)runtimePromise=new Promise((resolve,reject)=>{
    const script=document.createElement('script');script.src=ROOT+'effekseer.js';
    script.onerror=()=>reject(Error('Effekseer script failed to load'));
    script.onload=()=>window.effekseer.initRuntime(ROOT+'effekseer.wasm',()=>resolve(window.effekseer),reject);
    document.head.append(script);
  });
  return runtimePromise;
}
export async function createEffekseerFire(renderer,width,height,{load=loadRuntime,isCancelled=()=>false}={}){
  const runtime=await load();if(isCancelled())throw Error('Effekseer initialization cancelled');
  const context=runtime.createContext();
  if(!context)throw Error('Effekseer context unavailable');
  let effect;
  try{
    context.init(renderer.gl,{instanceMaxCount:512,squareMaxCount:512});
    context.setRestorationOfStatesFlag(false);renderer.reset();
    await new Promise((resolve,reject)=>{
      const timeout=setTimeout(()=>reject(Error('Effekseer effect load timed out')),15000);
      effect=context.loadEffect('/assets/effekseer/campfire-v1/campfire.efk',1,()=>{clearTimeout(timeout);resolve()},(message,url)=>{clearTimeout(timeout);reject(Error(`${message}: ${url}`))});
    });
    if(isCancelled())throw Error('Effekseer initialization cancelled');
  }
  catch(error){runtime.releaseContext(context);renderer.reset();throw error}
  let enabled=false,time=0,starts=0,destroyed=false;
  const sources=[{x:28,wait:0,handle:null},{x:width-28,wait:4.5,handle:null}];
  // Orthographic pixel coordinates: world Y rises from the bottom of the viewport.
  function resize(w,h){
    width=w;height=h;sources[1].x=width-28;
    context.setProjectionMatrix([2/width,0,0,0,0,2/height,0,0,0,0,-.01,0,-1,-1,0,1]);
    context.setCameraMatrix([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);renderer.reset();
  }
  resize(width,height);
  function start(source){
    source.handle=context.play(effect,source.x,8,0);
    if(source.handle){source.handle.setScale(66,66,66);source.handle.setAllColor(255,163,53,210);starts++}
    source.wait=16+Math.random()*7;
  }
  return {
    resize,
    setEnabled(value){
      context.stopAll();enabled=value;time=0;
      for(let i=0;i<sources.length;i++){sources[i].handle=null;sources[i].wait=i*4.5}
      // Seed a visible established fire for static/reduced-motion composition.
      if(enabled){start(sources[0]);context.update(35)}renderer.reset();
    },
    update(dt){
      if(!enabled||destroyed)return;time+=dt;
      for(const source of sources){source.wait-=dt;if(source.wait<=0&&!source.handle?.exists)start(source)}
      context.update(dt*60);
    },
    draw(){if(enabled&&!destroyed){context.draw();renderer.reset()}},
    diagnostics(){return {engine:'effekseer',enabled,starts,active:sources.filter(s=>s.handle?.exists).length,instances:512-context.getRestInstancesCount(),time}},
    destroy(){if(destroyed)return;destroyed=true;context.stopAll();context.releaseEffect(effect);runtime.releaseContext(context);renderer.reset()},
  };
}
