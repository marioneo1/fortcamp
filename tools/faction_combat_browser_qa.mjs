// Requires the local fixture server on 8766 and an isolated Chrome CDP session on 9229.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r=>ws.onopen=r);
let serial=0; const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setFocusEmulationEnabled',{enabled:true});
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/faction-combat-preview/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.factionReady)'))break;await new Promise(r=>setTimeout(r,100))}
await evaluate('window.factionTradePreview()');
for(let i=0;i<50;i++){if(await evaluate('Boolean(document.querySelector("#camp-trade-dialog")?.open)'))break;await new Promise(r=>setTimeout(r,100))}
assert.equal(await evaluate('document.querySelectorAll(".trade-rotation .trade-offer").length'),4);
assert.equal(await evaluate('document.querySelectorAll(".faction-contact").length'),3);
assert.equal(await evaluate('document.querySelectorAll(".trade-starters [data-offer]").length'),10);
await evaluate('document.querySelector(".trade-starters").open=true');
assert.equal(await evaluate(`document.querySelector('[data-offer="camp:frayed_capture_net"]').textContent.includes('6 gold')`),true);
for(const width of [1440,800,430]){
 await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
 assert.equal(await evaluate('(()=>{const d=document.querySelector("#camp-trade-dialog");return d.scrollWidth<=d.clientWidth+1})()'),true);
}
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await writeFile('staging-ui/faction-combat-preview/trade.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate('document.querySelector("[data-faction-contract]:not(:disabled)").click()');
for(let i=0;i<50;i++){if(await evaluate('!document.querySelector("#camp-trade-dialog").open'))break;await new Promise(r=>setTimeout(r,100))}
assert.equal(await evaluate('window.factionRequests.length'),1);
assert.equal(await evaluate('document.querySelector("#camp-trade-dialog").open'),false);
assert.equal(await evaluate('document.querySelector("#mission-modal").classList.contains("hidden")'),false);
await evaluate('window.factionSupportPreview()');
assert.equal(await evaluate('document.querySelectorAll("[data-supply]").length'),2);
await evaluate('document.querySelector(".battle-supplies").open=true');
assert.equal(await evaluate('document.querySelector("[data-supply-target=ally]").disabled'),false);
assert.equal(await evaluate('document.querySelector("[data-supply-target=player]").disabled'),true);
await writeFile('staging-ui/faction-combat-preview/support.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate('document.querySelector("[data-supply-target=ally]").click()');await new Promise(r=>setTimeout(r,150));
assert.deepEqual(await evaluate('window.gearCommands.at(-1)'),{action:'use_item',item_id:'dressing',target_id:'ally'});
assert.deepEqual(errors,[]);
console.log('PASS: actual Trade, responsive layout, private agreement opens, owned supply action');
await call('Browser.close');
