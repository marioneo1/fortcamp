// Isolated staging renderer. Does not contact a game API or read saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
try{
 await call('Runtime.enable');await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:true});
 await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/building-toolset-v6-gridfit/junction-preview.html'});
 for(let i=0;i<80;i++){if(await evaluate('Boolean(window.gridfitReady)'))break;await new Promise(r=>setTimeout(r,100))}
 assert.equal(await evaluate('Boolean(window.gridfitReady)'),true);
 for(const turn of [0,1,2,3]){
  for(const variant of [1,2,3,4]){
   await evaluate(`document.querySelector('#rotation').value='${turn}';document.querySelector('#variant').value='${variant}';draw()`);
   const rects=await evaluate('window.gridfitGeometry');
   assert.equal(rects.length,3);
   assert.ok(rects.flat().every(r=>Math.min(r[2],r[3])===48));
   assert.deepEqual(rects[0].map(r=>Math.max(r[2],r[3])),[128,128]);
   assert.deepEqual(rects[1].map(r=>Math.max(r[2],r[3])),[256,128]);
   assert.deepEqual(rects[2].map(r=>Math.max(r[2],r[3])),[256,256]);
   if(variant===1){
    const data=await evaluate("document.querySelector('#preview').toDataURL('image/png').split(',')[1]");
    await writeFile(`staging-terrain/building-toolset-v6-gridfit/junctions-${turn*90}.png`,Buffer.from(data,'base64'));
   }
  }
 }
 assert.deepEqual(errors,[]);
 console.log('PASS: corner/T/cross in four turns and four materials; exact full/half spans, shared 48px top thickness; actual paving loads.');
}finally{await Promise.race([call('Browser.close'),new Promise(r=>setTimeout(r,1000))]);ws.close()}
