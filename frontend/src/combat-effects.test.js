import test from 'node:test';
import assert from 'node:assert/strict';
import {createCombatEffects} from './combat-effects.js';
function setup({reduced=false,fail=false}={}){
 const old={window:globalThis.window,document:globalThis.document,requestAnimationFrame:globalThis.requestAnimationFrame,cancelAnimationFrame:globalThis.cancelAnimationFrame,performance:globalThis.performance};
 let now=0,serial=0;const frames=new Map(),calls={plays:0,draws:0,stops:0};
 const gl={COLOR_BUFFER_BIT:1,viewport(){},clearColor(){},clear(){}};
 const handles=[];const context={init(){},loadEffect(url,scale,ok){queueMicrotask(ok);return {}},setProjectionMatrix(){},setCameraMatrix(){},update(){},draw(){calls.draws++},play(){calls.plays++;const h={exists:true,setScale(){},setAllColor(){},setLocation(){}};handles.push(h);return h},stopAll(){calls.stops++;handles.forEach(h=>h.exists=false)},releaseEffect(){},getRestInstancesCount:()=>256-handles.filter(h=>h.exists).length};
 const element=()=>({style:{},setAttribute(){},remove(){},getContext:()=>gl,animate:()=>({})});
 const field={clientWidth:800,clientHeight:800,isConnected:true,contains:()=>true,append(){},closest:()=>null};
 globalThis.window={matchMedia:()=>({matches:reduced})};globalThis.document={hidden:false,createElement:element};
 globalThis.performance={now:()=>now};globalThis.requestAnimationFrame=fn=>{frames.set(++serial,fn);return serial};globalThis.cancelAnimationFrame=id=>frames.delete(id);
 const fx=createCombatEffects({load:async()=>{if(fail)throw Error('missing');return {createContext:()=>context,releaseContext(){}}}});
 return {fx,calls,field,ready:async()=>{fx.mount(field);await new Promise(r=>setImmediate(r))},tick(t){now=t;const callbacks=[...frames.values()];frames.clear();callbacks.forEach(fn=>fn(t))},restore(){fx.destroy();Object.assign(globalThis,old)}};
}
test('native projectile and death bursts finish and release active handles at idle',async()=>{
 const s=setup();try{await s.ready();s.fx.emit({type:'magic_projectile',from:{x:0,y:0},to:{x:2,y:2}},{width:8,height:8});s.fx.emit({type:'death_burst',x:2,y:2,race:'Human'},{width:8,height:8},220);s.tick(100);assert.equal(s.calls.plays,1);s.tick(300);assert.equal(s.calls.plays,2);s.tick(900);assert.equal(s.fx.diagnostics().pending,0);assert.equal(s.fx.diagnostics().active,0);assert.equal(s.fx.diagnostics().engine,'effekseer')}finally{s.restore()}
});
test('reduced motion and hidden pages suppress cosmetic events; pause clears queued work',async()=>{
 const s=setup({reduced:true});try{await s.ready();s.fx.emit({type:'death_burst',x:1,y:1},{width:8,height:8});assert.equal(s.fx.diagnostics().pending,0)}finally{s.restore()}
 const t=setup();try{await t.ready();document.hidden=true;t.fx.emit({type:'death_burst',x:1,y:1},{width:8,height:8});assert.equal(t.fx.diagnostics().pending,0);document.hidden=false;t.fx.emit({type:'death_burst',x:1,y:1},{width:8,height:8});t.fx.pause();assert.equal(t.fx.diagnostics().pending,0);assert.equal(t.fx.diagnostics().active,0)}finally{t.restore()}
});
test('missing native runtime uses an explicit bounded fallback',async()=>{
 const s=setup({fail:true});try{await s.ready();assert.equal(s.fx.diagnostics().engine,'fallback');s.fx.emit({type:'death_burst',x:1,y:1},{width:8,height:8});s.tick(20);assert.equal(s.fx.diagnostics().pending,0);assert.equal(s.fx.diagnostics().played,1)}finally{s.restore()}
});
