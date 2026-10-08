// Isolated Bard UI regression fixture; no live API or player saves.
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
for(const song of ['accelerando','quickening_chorus','war_anthem','song_of_peace']){
 await evaluate(`window.mageShow('bard_ready')`);await wait(100);
 await evaluate(`document.querySelector('[data-hotbar-skill="job:bard:${song}"]').click()`);
 await wait(100);
 const preview=await evaluate(`Array.from(document.querySelectorAll('.spell-area')).map(el=>el.dataset.battleCell).sort()`);
 assert.equal(preview.length,9,`${song} preview must cover a 3x3 space`);
 const selfLabel=await evaluate(`(()=>{const el=document.querySelector('.spell-self-label'),s=getComputedStyle(el);return {clip:s.clipPath,radius:s.borderRadius,height:el.getBoundingClientRect().height,unitHeight:el.parentElement.getBoundingClientRect().height}})()`);
 assert.equal(selfLabel.clip,'none',`${song} SELF label must not inherit circular portrait clipping`);
 assert.equal(selfLabel.radius,'4px');assert.ok(selfLabel.height<selfLabel.unitHeight*.5);
 await evaluate(`window.mageShow('bard_${song}')`);await wait(100);
 assert.equal(await evaluate(`document.querySelectorAll('.zone-bard_song .bard-performance-note').length`),9);
 assert.equal(await evaluate(`document.querySelectorAll('.zone-bard_song image').length`),0);
 assert.equal(await evaluate(`document.querySelector('[data-hotbar-skill="job:bard:${song}"]').textContent.includes('Stop Playing')`),true);
 if(song==='song_of_peace')await writeFile('staging-ui/mage-v1/bard-peace.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
 console.log(`PASS ${song}: nine-cell preview, dedicated notes, no binding artwork, Stop Playing`);
}
assert.deepEqual(errors,[]);ws.close();
