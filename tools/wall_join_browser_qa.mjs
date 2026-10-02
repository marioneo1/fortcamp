import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
try{
 await call('Emulation.setDeviceMetricsOverride',{width:1280,height:760,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/building-toolset-v2/join-preview.html'});
 for(let i=0;i<80;i++){if(await evaluate('Boolean(window.joinPreviewReady)'))break;await new Promise(r=>setTimeout(r,100))}
 assert.equal(await evaluate('Boolean(window.joinPreviewReady)'),true);
 for(const material of ['timber','fieldstone','limestone','iron']){
  await evaluate(`document.querySelector('#material').value='${material}';window.drawJoins()`);
  await evaluate(`Promise.all(Array.from(document.querySelectorAll('.has-prop-art')).map(e=>new Promise((resolve,reject)=>{const i=new Image();i.onload=resolve;i.onerror=reject;i.src=e.style.getPropertyValue('--battle-prop').match(/url\\(['"]?([^'")]+)/)[1]})))`);
  const clips=await evaluate("Array.from(document.querySelectorAll('.wall-connector')).map(e=>getComputedStyle(e,'::before').clipPath)");
  assert.ok(clips.length>=10);assert.equal(await evaluate("Array.from(document.querySelectorAll('.wall-connector')).every(e=>getComputedStyle(e,'::before').visibility==='visible')"),true);assert.ok(clips.some(c=>c!=='inset(0%)'),clips);assert.equal(await evaluate("Array.from(document.querySelectorAll('.assembled-wall')).every(e=>getComputedStyle(e,'::before').visibility==='hidden')"),true);for(const rotation of [90,180,270,0])await evaluate(`document.querySelector('#rotation').value='${rotation}';window.drawJoins()`);
  await new Promise(r=>setTimeout(r,100));
  await writeFile(`staging-terrain/building-toolset-v4/${material}-joins-fixed.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:1280,height:1040,scale:1}})).data,'base64'));
 }
 await evaluate("document.querySelector('#fix').checked=false;window.drawJoins()");
 assert.equal(await evaluate("document.querySelectorAll('.wall-connector').length"),0);
 console.log('PASS: enlarged joins in all four materials; real CSS clips matching wall art, no stretching');
}finally{await Promise.race([call('Browser.close'),new Promise(r=>setTimeout(r,1000))]);ws.close()}
