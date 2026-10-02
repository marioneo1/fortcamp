import assert from 'node:assert/strict';
let tabs;for(let i=0;i<30;i++){try{tabs=await(await fetch('http://127.0.0.1:9229/json')).json();break}catch{await new Promise(r=>setTimeout(r,100))}}
if(!tabs)throw Error('Start local QA Chrome on port 9229 first');
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/combat-relationships/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.relationshipReady)'))break;await new Promise(r=>setTimeout(r,100))}
for(let i=0;i<100;i++){if(await evaluate('window.nativeDiagnostics?.().engine')==='effekseer')break;await new Promise(r=>setTimeout(r,100))}
const before=await evaluate('window.nativeDiagnostics()');assert.equal(before.engine,'effekseer');console.log('native before',before);
await evaluate('window.nativeCast()');await new Promise(r=>setTimeout(r,270));
console.log('native during',await evaluate('window.nativeDiagnostics()'));
const image=await call('Page.captureScreenshot',{format:'png'});const {writeFile}=await import('node:fs/promises');await writeFile('staging-ui/combat-relationships/native-effects.png',Buffer.from(image.data,'base64'));
await new Promise(r=>setTimeout(r,1000));const idle=await evaluate('window.nativeDiagnostics()');assert.equal(idle.pending,0);assert.equal(idle.active,0);assert.equal(idle.played,2);console.log('native idle',idle);
await evaluate('window.relationshipPreview()');const visible=await evaluate("!document.querySelector('[data-roster-panel=conversation]').classList.contains('hidden')");assert.equal(visible,true);console.log('conversation pane visible',visible);
await evaluate("document.querySelector('[data-talk=food]').click()");await new Promise(r=>setTimeout(r,300));console.log('food',await evaluate("document.querySelector('.relationship-reply').textContent"));
assert.deepEqual(errors,[]);console.log('runtime errors',errors);await call('Browser.close');ws.close();
