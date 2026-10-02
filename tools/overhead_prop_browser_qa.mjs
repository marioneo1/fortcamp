// Actual UI with isolated fixture state; no live game API or saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/overhead-props-v1/preview.html'});
await new Promise(r=>setTimeout(r,900));
assert.equal(await evaluate('document.querySelectorAll("article").length'),12);
for(const material of ['grass','dirt','stone']){
 await evaluate(`document.querySelector('[data-ground="${material}"]').click()`);
 const urls=await evaluate(`Array.from(document.querySelectorAll('.sample')).map(el=>getComputedStyle(el).getPropertyValue('--sprite')).concat([getComputedStyle(document.body).getPropertyValue('--ground')])`);
 for(const value of urls){const path=value.match(/url\(['"]?([^'")]+)/)?.[1];assert.ok(path);assert.equal((await fetch('http://127.0.0.1:8766'+path)).status,200,path)}
}
await evaluate('document.querySelector("[data-ground=dirt]").click()');
await writeFile('staging-terrain/overhead-props-v1/comparison.png',Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true})).data,'base64'));
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/overhead-props-v1/battle-preview.html'});
for(let i=0;i<80;i++){if(await evaluate('Boolean(window.gearReady&&window.propOverheadPreview)'))break;await new Promise(r=>setTimeout(r,100))}
assert.equal(await evaluate('Boolean(window.gearReady)'),true);
assert.ok(await evaluate(`Array.from(document.querySelectorAll('.has-prop-art')).some(el=>el.style.getPropertyValue('--battle-prop').includes('overhead-props-v1'))`));
await writeFile('staging-terrain/overhead-props-v1/warcamp-pilot.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate('window.propLegacyPreview()');
assert.equal(await evaluate(`Array.from(document.querySelectorAll('.has-prop-art')).some(el=>el.style.getPropertyValue('--battle-prop').includes('overhead-props-v1'))`),false);
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.battle-object.has-prop-art')).backgroundSize.endsWith('auto')`),true);
assert.deepEqual(errors,[]);console.log('PASS: 12 old/new comparisons, three material assets, actual warcamp old/new toggle, undistorted sizing');
await call('Browser.close');ws.close();
