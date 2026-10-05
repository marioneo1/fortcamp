import {loadEffekseerRuntime} from './effekseer-fire.js';

export function bloodKind(race='Human'){
  if(['Golem','Automaton'].includes(race))return 'sparks';
  if(['Undead','Revenant','Banshee'].includes(race))return 'dust';
  if(race==='Slimefolk')return 'slime';
  return 'blood';
}
const colors={blood:[205,25,40,235],slime:[40,225,185,230],sparks:[255,195,75,235],dust:[180,165,145,210],spell:[145,185,255,245]};
export function createCombatEffects({load=loadEffekseerRuntime}={}){
  let field,canvas,gl,context,runtime,effects={},loading,frame=0,last=0,jobs=[],epoch=0,played=0,engine='loading';
  const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function mount(next){
    field=next;if(!field)return;
    if(canvas&&!field.contains(canvas))field.append(canvas);
    if(!loading)loading=initialize();
  }
  async function initialize(){
    const generation=epoch;
    canvas=document.createElement('canvas');canvas.className='combat-effects-layer';canvas.setAttribute('aria-hidden','true');field?.append(canvas);
    try{
      runtime=await load();if(generation!==epoch)return;
      gl=canvas.getContext('webgl',{alpha:true,antialias:false});if(!gl)throw Error('WebGL unavailable');
      context=runtime.createContext();context.init(gl,{instanceMaxCount:256,squareMaxCount:512});
      await Promise.all(['blood','spell'].map(name=>new Promise((resolve,reject)=>{
        const timeout=setTimeout(()=>reject(Error('Combat effect load timed out')),10000);
        effects[name]=context.loadEffect(`/assets/effekseer/combat-v1/${name}.efk?v=combat-1`,1,()=>{clearTimeout(timeout);resolve()},()=>{clearTimeout(timeout);reject(Error('Combat effect missing'))});
      })));
      if(generation!==epoch){release();return}engine='effekseer';resize();
    }catch(error){release();engine='fallback';canvas?.remove();canvas=null;console.warn('Combat VFX fallback:',error.message)}
  }
  function resize(){
    if(!context||!field)return;
    const w=Math.max(1,field.clientWidth),h=Math.max(1,field.clientHeight);
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h)}
    context.setProjectionMatrix([2/w,0,0,0,0,2/h,0,0,0,0,-.01,0,-1,-1,0,1]);
    context.setCameraMatrix([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
  }
  function fallback(job){
    if(!field)return;const dot=document.createElement('i');dot.className=`combat-fx-fallback ${job.kind==='spell'?'spell':'burst'}`;
    dot.style.left=`${(job.to.x+.5)/job.width*100}%`;dot.style.top=`${(job.to.y+.5)/job.height*100}%`;
    dot.style.background=`rgb(${colors[job.kind].slice(0,3).join(',')})`;field.append(dot);
    const animation=dot.animate([{transform:'translate(-50%,-50%) scale(.4)',opacity:.9},{transform:'translate(-50%,-50%) scale(2.2)',opacity:0}],{duration:350});animation.onfinish=()=>dot.remove();
  }
  function emit(event,battle,delay=0){
    if(!field||reduced()||document.hidden||event.bloodless)return;
    const spell=event.type==='magic_projectile';
    const to=spell?event.to:{x:event.x,y:event.y};if(!to)return;
    jobs.push({kind:spell?'spell':bloodKind(event.race),from:event.from||to,to,width:battle.width,height:battle.height,start:performance.now()+delay,duration:spell?220:520,handle:null});
    jobs=jobs.slice(-32);if(!frame){last=performance.now();frame=requestAnimationFrame(tick)}
  }
  function tick(now){
    frame=0;
    if(!field?.isConnected||field.closest('.hidden')||document.hidden){jobs=[];context?.stopAll();clear();return}
    resize();const dt=Math.min(.05,Math.max(0,(now-last)/1000));last=now;
    jobs=jobs.filter(job=>{
      if(now<job.start)return true;
      if(engine==='loading')return now-job.start<300;
      if(engine==='fallback'){fallback(job);played++;return false}
      const cw=canvas.width/job.width,ch=canvas.height/job.height;
      if(!job.handle){
        job.handle=context.play(effects[job.kind==='spell'?'spell':'blood'],(job.from.x+.5)*cw,canvas.height-(job.from.y+.5)*ch,0);
        const scale=cw*(job.kind==='spell'?.48:.85);job.handle?.setScale(scale,scale,scale);job.handle?.setAllColor(...colors[job.kind]);played++;
      }
      const p=Math.min(1,(now-job.start)/job.duration);
      if(job.kind==='spell')job.handle?.setLocation((job.from.x+(job.to.x-job.from.x)*p+.5)*cw,canvas.height-(job.from.y+(job.to.y-job.from.y)*p+.5)*ch,0);
      return p<1;
    });
    if(context){gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);context.update(dt*60);context.draw()}
    if(jobs.length)frame=requestAnimationFrame(tick);else {context?.stopAll();context?.update(1);clear()}
  }
  function clear(){if(gl){gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT)}}
  function release(){if(context){context.stopAll();Object.values(effects).forEach(effect=>context.releaseEffect(effect));runtime.releaseContext(context);context=null;effects={}}}
  function destroy(){epoch++;cancelAnimationFrame(frame);frame=0;jobs=[];release();canvas?.remove();canvas=null;loading=null;gl=null;engine='loading'}
  function pause(){cancelAnimationFrame(frame);frame=0;jobs=[];context?.stopAll();context?.update(1);clear();canvas?.remove()}
  return {mount,emit,pause,destroy,diagnostics:()=>({engine,played,pending:jobs.length,active:jobs.filter(job=>job.handle?.exists).length,instances:context?256-context.getRestInstancesCount():0})};
}
