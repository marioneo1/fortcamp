// Runs against the isolated fixture, not the game server or live saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setFocusEmulationEnabled',{enabled:true});
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mercenary-preview/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.mercenaryReady)'))break;await new Promise(r=>setTimeout(r,100))}
await evaluate('window.mercenaryPlanner()');
assert.equal(await evaluate("document.querySelector('[data-hire-mercenaries]').disabled"),true);
await evaluate("document.querySelector('[data-planner-character=player]').click()");
assert.equal(await evaluate("document.querySelector('[data-hire-mercenaries]').disabled"),false);
await evaluate("document.querySelector('[data-hire-mercenaries]').click()");
for(let i=0;i<50;i++){if(await evaluate("document.querySelectorAll('[data-hire]').length===4"))break;await new Promise(r=>setTimeout(r,100))}
const shot=await call('Page.captureScreenshot',{format:'png'});await writeFile('staging-ui/mercenary-preview/hiring-board.png',Buffer.from(shot.data,'base64'));
await evaluate("document.querySelector('[data-hire]').click()");await new Promise(r=>setTimeout(r,150));
assert.equal(await evaluate("document.querySelectorAll('dialog.mercenary-market').length"),0);
assert.equal(await evaluate('window.mercenaryRequests.at(-1).mercenary_ids.length'),1);
assert.equal(await evaluate('window.mercenaryRequests.at(-1).party_ids.length'),2);
assert.match(await evaluate("document.querySelector('[data-hire-info]').textContent"),/15 gold/);
await evaluate('window.mercenaryRefresh()');await new Promise(r=>setTimeout(r,100));
assert.equal(await evaluate('window.mercenaryRequests.at(-1).mercenary_ids.length'),1);
await evaluate("document.querySelector('[data-hire-mercenaries]').click()");await new Promise(r=>setTimeout(r,100));
await evaluate("document.querySelector('[data-hire]:nth-of-type(1)').closest('article').nextElementSibling.querySelector('[data-hire]').click()");await new Promise(r=>setTimeout(r,100));
assert.equal(await evaluate('window.mercenaryRequests.at(-1).mercenary_ids.length'),2);
assert.equal(await evaluate('window.mercenaryRequests.at(-1).bodyguard_ids.length'),1);
await evaluate('window.mercenaryBattle()');
assert.equal(await evaluate("document.querySelectorAll('[data-dismiss-mercenary]').length"),1);
const notice=await call('Page.captureScreenshot',{format:'png'});await writeFile('staging-ui/mercenary-preview/hostile-arrival.png',Buffer.from(notice.data,'base64'));
await evaluate("document.querySelector('[data-dismiss-mercenary]').click()");
assert.equal(await evaluate("document.querySelectorAll('[data-dismiss-mercenary]').length"),0);
assert.deepEqual(errors,[]);
console.log('PASS: real private planner, two hires, selection persistence, prices, central arrival notice');
await call('Browser.close');
