import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createBoardVFX} from './board-vfx.js';
function setup(){
  const calls={draw:0},frames=new Map(),listeners=new Map(),motionListeners=new Map();let sequence=0,time=0;
  const ctx=new Proxy({clearRect(){calls.draw++},createRadialGradient:()=>({addColorStop(){}}),createLinearGradient:()=>({addColorStop(){}})},{get:(object,key)=>object[key]||(()=>{})});
  const canvas={getContext:()=>ctx,setAttribute(){},dataset:{},remove(){calls.removed=true}},classes=new Set();
  const document={hidden:false,createElement:()=>canvas,body:{prepend(){},classList:{toggle:(name,value)=>value?classes.add(name):classes.delete(name),remove:name=>classes.delete(name)}},addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener:name=>listeners.delete(name)};
  const motion={matches:false,addEventListener:(name,fn)=>motionListeners.set(name,fn),removeEventListener:name=>motionListeners.delete(name)};
  const window={innerWidth:1440,innerHeight:900,performance:{now:()=>time},matchMedia:()=>motion,addEventListener(){},removeEventListener(){}};
  const vfx=createBoardVFX({document,window,requestFrame:fn=>{const id=++sequence;frames.set(id,fn);return id},cancelFrame:id=>frames.delete(id),random:()=>.5});
  return {vfx,frames,document,motion,canvas,calls,listeners,motionListeners,advance:ms=>{time+=ms;const current=[...frames.values()];frames.clear();current.forEach(fn=>fn(time))}};
}
test('regional backdrops animate at a bounded rate without restarting on unchanged polls',()=>{
  const s=setup();s.vfx.setEvent({id:'great_beast_tide',theme:'beast'});assert.equal(s.frames.size,1);const draws=s.calls.draw;
  for(let i=0;i<20;i++)s.vfx.setEvent({id:'great_beast_tide',theme:'beast'});assert.equal(s.frames.size,1);assert.equal(s.calls.draw,draws);
  s.advance(16);assert.equal(s.calls.draw,draws);s.advance(34);assert.equal(s.calls.draw,draws+1);assert.equal(s.frames.size,1);s.vfx.dispose();assert.equal(s.frames.size,0);
});
test('hidden pages, other tabs, and general contracts stop background animation',()=>{
  const s=setup();s.vfx.setEvent({id:'ashen_procession',theme:'undead'});s.document.hidden=true;s.listeners.get('visibilitychange')();assert.equal(s.frames.size,0);
  s.document.hidden=false;s.listeners.get('visibilitychange')();assert.equal(s.frames.size,1);
  s.vfx.setEvent({id:'ashen_procession',theme:'undead'},false);assert.equal(s.frames.size,0);assert.equal(s.canvas.hidden,true);
  s.vfx.setEvent({id:'general',theme:'general'});assert.equal(s.frames.size,0);s.vfx.dispose();
});
test('reduced motion keeps a static backdrop and dynamically cancels running animation',()=>{
  const s=setup();s.motion.matches=true;s.vfx.setEvent({id:'arcane_convergence',theme:'arcane'});assert.equal(s.frames.size,0);assert.equal(s.canvas.hidden,false);
  s.motion.matches=false;s.motionListeners.get('change')();assert.equal(s.frames.size,1);
  s.motion.matches=true;s.motionListeners.get('change')();assert.equal(s.frames.size,0);s.vfx.dispose();assert.equal(s.calls.removed,true);
});
