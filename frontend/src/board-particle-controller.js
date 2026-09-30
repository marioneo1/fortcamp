import {PARTICLE_PRESETS} from './particle-presets.js';
const defaultLoader=async options=>(await import('./particle-renderer.js')).createParticleRenderer(options);
export function createBoardVFX({document=globalThis.document,window=globalThis.window,requestFrame=fn=>window.requestAnimationFrame(fn),cancelFrame=id=>window.cancelAnimationFrame(id),loadRenderer=defaultLoader,loadFallback=async options=>(await import('./board-vfx-fallback.js')).createBoardVFX(options)}={}){
  const canvas=document.createElement('canvas');canvas.className='board-regional-backdrop';canvas.setAttribute('aria-hidden','true');canvas.hidden=true;document.body.prepend(canvas);
  const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
  let theme=null,active=false,frame=null,last=0,disposed=false,backend=null,loading=null,fallback=null,failed=false,revision=0,ready=false;
  const dimensions=()=>({width:Math.max(1,window.innerWidth),height:Math.max(1,window.innerHeight)});
  function stop(){if(frame!==null)cancelFrame(frame);frame=null}
  function tick(stamp){
    frame=null;if(!active||!ready||disposed||document.hidden||motion.matches||!backend)return;
    const elapsed=stamp-last,interval=1000/(window.innerWidth<700?30:60);
    if(elapsed>=interval-1){backend.update(Math.min(.1,elapsed/1000));backend.render();last=stamp}
    frame=requestFrame(tick);
  }
  function resume(){
    stop();if(!active||!ready||disposed||document.hidden||!backend)return;
    backend.render();if(!motion.matches){last=window.performance.now();frame=requestFrame(tick)}
  }
  async function prepare(){
    const request=++revision;ready=false;stop();canvas.hidden=true;
    if(failed){if(!fallback)fallback=await loadFallback({document,window,requestFrame,cancelFrame});if(disposed){fallback.dispose();return}fallback.setEvent({id:theme,theme},active);return}
    try{
      if(!loading)loading=loadRenderer({canvas,...dimensions()});
      const nextBackend=await loading;
      if(disposed){if(backend!==nextBackend){backend=nextBackend;nextBackend.destroy()}return}
      backend=nextBackend;if(request!==revision||!active)return;
      const {width,height}=dimensions();backend.resize(width,height);
      const result=await backend.setTheme(theme);
      if(disposed||request!==revision||!active||result===false)return;
      ready=true;canvas.dataset.renderer='pixi';canvas.hidden=false;resume();
    }catch(error){
      if(disposed)return;failed=true;backend?.destroy();backend=null;canvas.hidden=true;
      console.warn('Particle renderer unavailable; using the painted canvas fallback.',error);
      if(active)await prepare();
    }
  }
  function visibility(){if(document.hidden)stop();else resume()}
  function motionChange(){resume()}
  function resize(){if(active&&!failed)prepare()}
  window.addEventListener('resize',resize);document.addEventListener('visibilitychange',visibility);motion.addEventListener('change',motionChange);
  return {
    setEvent(event,enabled=true){
      const next=PARTICLE_PRESETS.includes(event?.theme)&&event?.id!=='general'?event.theme:null,wanted=!!(next&&enabled);
      if(next===theme&&wanted===active)return;
      theme=next;active=wanted;canvas.dataset.theme=theme||'general';document.body.classList.toggle('board-vfx-active',active);
      if(!active){revision++;ready=false;stop();canvas.hidden=true;fallback?.setEvent(event,false)}else prepare();
    },
    diagnostics(){return backend?.diagnostics()||{renderer:failed?'fallback':'loading',particles:0}},
    pixelSignature(){return backend?.pixelSignature()||0},
    dispose(){disposed=true;revision++;stop();backend?.destroy();fallback?.dispose();canvas.remove();document.body.classList.remove('board-vfx-active');window.removeEventListener('resize',resize);document.removeEventListener('visibilitychange',visibility);motion.removeEventListener('change',motionChange)},
  };
}
