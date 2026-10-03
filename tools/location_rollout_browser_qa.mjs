// Actual combat renderer with isolated fixture state. Requires preview :8766
// and a dedicated headless Chrome CDP session :9229; never accesses live saves.
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
const out='staging-terrain/location-rollout-v1';await mkdir(out,{recursive:true});
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
try{
 await call('Runtime.enable');
 await call('Emulation.setDeviceMetricsOverride',{width:1600,height:1100,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/overhead-props-v2/encounter-preview.html'});
 for(let i=0;i<100;i++){if(await evaluate('Boolean(window.propCoverageReady)'))break;await new Promise(r=>setTimeout(r,100))}
 assert.equal(await evaluate('Boolean(window.propCoverageReady)'),true);
 const seen=new Set();let maps=0;
 for(const mid of ['chapel_patrol','roadside_toll','road_cache','goblin_armory','salvage_court']){
  for(let variant=1;variant<=4;variant++){
   const key=`${mid}_v${variant}`;
   await evaluate(`window.propEncounter('${key}')`);await new Promise(r=>setTimeout(r,120));
   const props=await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).map(e=>e.style.getPropertyValue('--battle-prop'))");
   assert.ok(props.length>=10,key);
   for(const value of props){const path=value.match(/url\(['\"]?([^'\")]+)/)?.[1];if(path&&!seen.has(path)){assert.equal((await fetch('http://127.0.0.1:8766'+path)).status,200,path);seen.add(path)}}
   const clip=await evaluate("(()=>{const r=document.querySelector('.battle-cell').parentElement.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1.5}})()");
   await writeFile(`${out}/${key}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip})).data,'base64'));
   maps++;
  }
 }
 assert.deepEqual(errors,[]);
 console.log(`PASS: ${maps} authored mission layouts render; ${seen.size} asset URLs load; no runtime exceptions.`);
}finally{await call('Browser.close');ws.close()}
