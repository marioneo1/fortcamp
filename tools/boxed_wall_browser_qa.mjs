import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
try{
 await call('Emulation.setDeviceMetricsOverride',{width:1600,height:1100,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/overhead-props-v2/encounter-preview.html'});
 for(let i=0;i<100;i++){if(await evaluate('Boolean(window.propCoverageReady)'))break;await new Promise(r=>setTimeout(r,100))}
 assert.equal(await evaluate('Boolean(window.propCoverageReady)'),true);
 for(let i=1;i<=4;i++){
  await evaluate(`window.propEncounter('limestone_boxed_${i}')`);
  await new Promise(r=>setTimeout(r,200));
  const assets=await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).map(e=>e.style.getPropertyValue('--battle-prop')).filter(s=>s.includes('building-v9-boxed'))");
  assert.ok(assets.length>=6);
  assert.equal(await evaluate("document.querySelectorAll('.wall-connector').length"),0);
  for(const value of assets){const path=value.match(/url\(['\"]?([^'\")]+)/)?.[1];assert.equal((await fetch('http://127.0.0.1:8766'+path)).status,200)}
  await writeFile(`staging-terrain/building-toolset-v9-boxed-reference/in-game-${i}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false})).data,'base64'));
 }
 console.log('PASS: four candidate maps render six generated pieces; assets load; no assembled wall connectors.');
}finally{await call('Browser.close');ws.close()}
