// Isolated Druid UI regression fixture; no live API or player saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<120;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(200)}
assert.equal(await evaluate('Boolean(window.mageReady)'),true);


await evaluate(`window.mageShow('druid_hover')`);await wait(250);
await call('Performance.enable');
const metrics=async()=>Object.fromEntries((await call('Performance.getMetrics')).metrics.map(m=>[m.name,m.value]));

async function sample(){
 const points=await evaluate(`Array.from(document.querySelectorAll('.battle-token[data-battle-unit]')).slice(0,3).map(t=>{const r=t.getBoundingClientRect();return {x:r.x+r.width*.8,y:r.y+r.height*.8}})`);
 const before=await metrics();
 for(let i=0;i<90;i++){const p=points[Math.floor(i/3)%3];await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:p.x+(i%3),y:p.y,buttons:0});await wait(17)}
 const after=await metrics(),result={name:'actual-three-unit-sweep'};for(const key of ['LayoutCount','RecalcStyleCount','LayoutDuration','RecalcStyleDuration','ScriptDuration','TaskDuration'])result[key]=after[key]-before[key];console.log(JSON.stringify(result));return result;
}
const sweep=await sample();
async function positionBenchmark(name,legacy){
 await evaluate(`(async()=>{const tip=document.getElementById('combat-unit-inspect'),token=document.querySelector('.battle-token');token.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:400,clientY:300}));await new Promise(requestAnimationFrame);tip.style.setProperty('left','0px','important');tip.style.setProperty('top','0px','important');tip.style.transform='none';await new Promise(requestAnimationFrame)})()`);
 const before=await metrics();
 await evaluate(`(async()=>{const tip=document.getElementById('combat-unit-inspect');for(let i=0;i<90;i++){${legacy?"tip.style.setProperty('left',(400+i)+'px','important');tip.style.setProperty('top','300px','important')":"tip.style.transform='translate3d('+(400+i)+'px,300px,0)'"};await new Promise(requestAnimationFrame)}})()`);
 const after=await metrics(),result={name};for(const key of ['LayoutCount','RecalcStyleCount','LayoutDuration','RecalcStyleDuration','ScriptDuration','TaskDuration'])result[key]=after[key]-before[key];console.log(JSON.stringify(result));return result;
}
const legacyPosition=await positionBenchmark('isolated-left-top',true),transformPosition=await positionBenchmark('isolated-transform',false);
assert.ok(transformPosition.LayoutCount<legacyPosition.LayoutCount/2,'transform movement should avoid most position layouts');
await writeFile('data/browser-qa/hover-profile.json',JSON.stringify({sweep,legacyPosition,transformPosition},null,2));
assert.deepEqual(errors,[]);ws.close();
