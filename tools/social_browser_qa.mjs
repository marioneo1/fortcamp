// Actual UI with isolated fixture state; no live game API or saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
await call('Runtime.enable');await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/combat-relationships/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.relationshipReady)'))break;await new Promise(r=>setTimeout(r,100))}
await evaluate('window.relationshipPreview()');
assert.equal(await evaluate('document.querySelectorAll("[data-talk]").length'),4);
await evaluate('document.querySelector(".conversation-gifts").open=true');await new Promise(r=>setTimeout(r,50));
await evaluate('document.querySelector("[data-talk=food]").click();document.querySelector("[data-talk=food]").click()');
await new Promise(r=>setTimeout(r,150));
assert.equal(await evaluate('window.relationshipRequests.length'),1);
assert.equal(await evaluate('document.querySelectorAll(".conversation-exchange").length'),1);
assert.equal(await evaluate('document.querySelector(".conversation-speech").textContent.includes("favorite")'),true);
assert.equal(await evaluate('document.querySelectorAll(".conversation-meals .favorite").length'),1);
assert.equal(await evaluate('document.querySelector(".conversation-gifts").open'),true);
await evaluate('document.querySelector("[data-talk=trust]").click()');await new Promise(r=>setTimeout(r,100));
await evaluate('window.socialConversationRefresh()');
assert.equal(await evaluate('document.querySelectorAll(".conversation-exchange").length'),2);
for(const width of [1440,800,430]){
 await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
 assert.equal(await evaluate('document.querySelector(".conversation-workspace").scrollWidth<=document.querySelector(".conversation-workspace").clientWidth+1'),true);
}
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await writeFile('staging-ui/combat-relationships/conversation-refined.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate('window.prisonPreview()');
assert.equal(await evaluate('document.querySelectorAll("[data-prison-select]").length'),1);
assert.equal(await evaluate('document.querySelector(".prison-identity").textContent.includes("Vrix")'),true);
assert.equal(await evaluate('document.querySelector(".prison-recruitment").open'),true);
assert.equal(await evaluate('document.querySelector(".prison-warden-status").textContent.includes("Ready to negotiate")'),true);
await evaluate('window.socialStockadePreview();document.querySelector("[data-prison-select=stockade-preview]").click()');
assert.equal(await evaluate('document.querySelectorAll("[data-prison-select]").length'),5);
assert.equal(await evaluate('document.querySelector(".prison-stockade-alert").textContent.includes("before removal")'),true);
assert.equal(await evaluate('document.querySelector("[data-prisoner-action=negotiate]").disabled'),true);
await evaluate('document.querySelector(".prison-custody").open=true');
assert.equal(await evaluate('document.querySelector("[data-prisoner-action=secure]").disabled'),true);
await evaluate('(()=>{const s=document.querySelector("[data-prisoner-swap]");s.value="prison-fixture-captive";s.dispatchEvent(new Event("change"))})()');
assert.equal(await evaluate('document.querySelector("[data-prisoner-action=secure]").disabled'),false);
await evaluate('window.workspaceRefresh()');
assert.equal(await evaluate('document.querySelector("[data-prison-select=stockade-preview]").getAttribute("aria-pressed")'),'true');
for(const width of [1440,800,430]){
 await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
 assert.equal(await evaluate('document.querySelector(".prison-workspace-body").scrollWidth<=document.querySelector(".prison-workspace-body").clientWidth+1'),true);
}
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await writeFile('staging-ui/combat-relationships/prison-refined.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
assert.deepEqual(errors,[]);console.log('PASS: conversation history/preferences, duplicate protection, gift state, prison selection, stockade warning, warden availability, explicit swaps, responsive layouts');
await call('Browser.close');
