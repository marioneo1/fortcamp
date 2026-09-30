import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createBoardVFX} from './board-vfx.js';
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
function setup(loadRenderer){
  const calls={loads:0,renders:0,updates:[],themes:[],destroy:0},frames=new Map(),listeners=new Map(),motionListeners=new Map();let sequence=0,time=0;
  const backend={resize(){},setTheme:async theme=>{calls.themes.push(theme);return true},render(){calls.renders++},update:dt=>calls.updates.push(dt),destroy(){calls.destroy++},diagnostics:()=>({renderer:'pixi'})};
  const canvas={setAttribute(){},dataset:{},remove(){calls.removed=true}};
  const document={hidden:false,createElement:()=>canvas,body:{prepend(){},classList:{toggle(){},remove(){}}},addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener:name=>listeners.delete(name)};
  const motion={matches:false,addEventListener:(name,fn)=>motionListeners.set(name,fn),removeEventListener:name=>motionListeners.delete(name)};
  const window={innerWidth:1440,innerHeight:900,performance:{now:()=>time},matchMedia:()=>motion,addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener:name=>listeners.delete(name)};
  const fallbackCalls=[];
  const vfx=createBoardVFX({document,window,loadRenderer:loadRenderer||(async()=>{calls.loads++;return backend}),loadFallback:async()=>({setEvent:(...args)=>fallbackCalls.push(args),dispose(){}}),requestFrame:fn=>{const id=++sequence;frames.set(id,fn);return id},cancelFrame:id=>frames.delete(id)});
  return {vfx,frames,document,motion,canvas,calls,listeners,motionListeners,backend,fallbackCalls,advance:ms=>{time+=ms;const current=[...frames.values()];frames.clear();current.forEach(fn=>fn(time))}};
}
test('Pixi loads lazily and unchanged polls preserve one loop and emitter state',async()=>{
  const s=setup();assert.equal(s.calls.loads,0);s.vfx.setEvent({id:'beast',theme:'beast'});await flush();assert.equal(s.calls.loads,1);assert.equal(s.frames.size,1);
  for(let i=0;i<20;i++)s.vfx.setEvent({id:'beast',theme:'beast'});
  assert.deepEqual(s.calls.themes,['beast']);s.advance(17);assert.equal(s.calls.updates.length,1);
  s.document.hidden=true;s.listeners.get('visibilitychange')();assert.equal(s.frames.size,0);
  s.document.hidden=false;s.listeners.get('visibilitychange')();s.advance(5000);assert.equal(s.calls.updates.at(-1),.1);
  s.vfx.setEvent({id:'general'});assert.equal(s.canvas.hidden,true);assert.equal(s.frames.size,0);
  s.vfx.dispose();assert.equal(s.calls.destroy,1);
});
test('reduced motion renders a still and motion preference changes pause/resume',async()=>{
  const s=setup();s.motion.matches=true;s.vfx.setEvent({id:'undead',theme:'undead'});await flush();assert.equal(s.canvas.hidden,false);assert.equal(s.frames.size,0);
  s.motion.matches=false;s.motionListeners.get('change')();assert.equal(s.frames.size,1);
  s.motion.matches=true;s.motionListeners.get('change')();assert.equal(s.frames.size,0);s.vfx.dispose();
});
test('leaving during async initialization never shows or runs the abandoned effect',async()=>{
  let resolve;const s=setup(()=>new Promise(r=>resolve=r));s.vfx.setEvent({id:'beast',theme:'beast'});s.vfx.setEvent({id:'general'});resolve(s.backend);await flush();assert.equal(s.canvas.hidden,true);assert.equal(s.frames.size,0);assert.equal(s.calls.themes.length,0);s.vfx.dispose();
});
test('disposing during a shared load destroys the renderer once',async()=>{
  let resolve;const s=setup(()=>new Promise(r=>resolve=r));s.vfx.setEvent({id:'beast',theme:'beast'});s.vfx.setEvent({id:'goblin',theme:'goblin'});s.vfx.dispose();resolve(s.backend);await flush();assert.equal(s.calls.destroy,1);assert.equal(s.frames.size,0);
});
test('unavailable WebGL falls back without retrying the failing renderer',async()=>{
  let loads=0;const s=setup(async()=>{loads++;throw Error('GPU unavailable')});const warn=console.warn;console.warn=()=>{};
  try{s.vfx.setEvent({id:'beast',theme:'beast'});await flush();s.vfx.setEvent({id:'goblin',theme:'goblin'});await flush();assert.equal(loads,1);assert.equal(s.fallbackCalls.at(-1)[0].theme,'goblin');assert.equal(s.frames.size,0);s.vfx.dispose()}finally{console.warn=warn}
});
