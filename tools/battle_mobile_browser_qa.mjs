// Isolated Chrome touch emulation. Actual iOS Safari still needs device QA.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const rect=selector=>evaluate(`document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect().toJSON()`);
const media=async mobile=>{
 await call('Emulation.setTouchEmulationEnabled',{enabled:mobile,maxTouchPoints:5});
 await call('Emulation.setEmulatedMedia',{features:[{name:'hover',value:mobile?'none':'hover'},{name:'pointer',value:mobile?'coarse':'fine'}]});
};
await call('Runtime.enable');await call('Page.enable');await call('Page.bringToFront');await media(false);
await call('Page.navigate',{url:'about:blank'});await wait(100);
await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:true});
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(200)}
assert.equal(await evaluate('Boolean(window.mageReady)'),true);
await evaluate(`localStorage.setItem('fortcamp:battle-hud:v1',JSON.stringify({skills:{x:.5,y:1,width:1216}}));window.mageShow('captor_ready')`);await wait(200);
const desktop=await rect('.hud-skills'),saved=await evaluate(`localStorage.getItem('fortcamp:battle-hud:v1')`);
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.mobile-battle-tabs')).display`),'none');
await media(true);
await call('Emulation.setDeviceMetricsOverride',{width:430,height:760,deviceScaleFactor:1,mobile:true});await wait(200);
assert.equal(await evaluate(`matchMedia('(max-width:1100px) and (hover:none) and (pointer:coarse)').matches`),true);
const panel=await rect('.hud-skills');assert.ok(panel.width<=430&&panel.x>=0&&panel.bottom<=760);
assert.ok((await rect('#battle-viewport')).height>=410,'map retains most of the usable portrait height');
assert.ok(panel.height<=140,'compact single-row controls');
assert.ok((await rect('.active-unit-portrait')).height<=41);
for(const selector of ['[data-mobile-cancel]','[data-mobile-tab="skills"]','[data-combat-mode="move"]']){
 const r=await rect(selector);assert.ok(r.width>=44&&r.height>=44,`${selector} has finger-sized target`);
}
await evaluate(`document.querySelector('[data-mobile-tab="skills"]').click()`);
assert.notEqual(await evaluate(`getComputedStyle(document.querySelector('.combat-hotbar')).display`),'none');
await evaluate(`document.querySelector('[data-mobile-turns]').click()`);assert.ok(await evaluate(`Boolean(document.querySelector('.hud-turns-popup'))`));
await evaluate(`document.querySelector('[data-close-turns]').click()`);assert.equal(await evaluate(`Boolean(document.querySelector('.hud-turns-popup'))`),false);
await evaluate(`document.querySelector('[data-mobile-collapse]').click()`);assert.ok((await rect('.hud-skills')).height<70);
await wait(200);
// A touch drag on the map must never become a server movement/attack command.
const sent=await evaluate('window.mageSent.length'),before=await evaluate(`({x:document.querySelector('#battle-viewport').scrollLeft,y:document.querySelector('#battle-viewport').scrollTop})`);
const touch=async(type,points)=>call('Input.dispatchTouchEvent',{type,touchPoints:points.map(([id,x,y])=>({id,x,y,radiusX:3,radiusY:3,force:1}))});
await touch('touchStart',[[1,210,300]]);await touch('touchMove',[[1,250,340]]);await touch('touchEnd',[]);await wait(150);
const after=await evaluate(`({x:document.querySelector('#battle-viewport').scrollLeft,y:document.querySelector('#battle-viewport').scrollTop})`);
assert.ok(Math.abs(before.x-after.x)>20&&Math.abs(before.y-after.y)>20,JSON.stringify({before,after,viewport:await rect('#battle-viewport')}));assert.equal(await evaluate('window.mageSent.length'),sent);
const zoomBefore=await rect('.battlefield');

await touch('touchStart',[[1,150,300],[2,250,300]]);await touch('touchMove',[[1,125,300],[2,275,300]]);await touch('touchEnd',[]);await wait(150);
assert.ok((await rect('.battlefield')).width>zoomBefore.width*1.3,JSON.stringify({before:zoomBefore,after:await rect('.battlefield'),viewport:await rect('#battle-viewport')}));assert.equal(await evaluate('window.mageSent.length'),sent);
await evaluate(`document.querySelector('[data-mobile-collapse]').click()`);
await evaluate(`document.querySelector('[data-battle-fit]').click()`);await wait(150);
// Long-press opens persistent details without issuing a combat action.
const unit=await rect('[data-battle-unit]');
await touch('touchStart',[[1,unit.x+unit.width/2,unit.y+unit.height/2]]);await wait(520);await touch('touchEnd',[]);await wait(100);
const inspector=await rect('#combat-unit-window');
assert.ok(inspector.width<=430&&inspector.x>=0&&inspector.right<=430);
assert.equal(await evaluate('window.mageSent.length'),sent);
await evaluate(`document.querySelector('#combat-unit-window button').click()`);
assert.equal(await evaluate(`Boolean(document.querySelector('#combat-unit-window'))`),false);
await evaluate(`document.querySelector('[data-mobile-cancel]').click()`);
assert.ok(await evaluate(`document.querySelector('.battlefield').classList.contains('mode-move')`));
let shot=await call('Page.captureScreenshot',{format:'png'});await writeFile('data/browser-qa/mobile-portrait.png',Buffer.from(shot.data,'base64'));
await call('Emulation.setDeviceMetricsOverride',{width:932,height:430,deviceScaleFactor:1,mobile:true});await wait(200);
const landscape=await rect('.hud-skills');assert.ok(landscape.x>=0&&landscape.right<=932&&landscape.bottom<=430);
await evaluate(`document.querySelector('[data-battle-fit]').click()`);await wait(150);
shot=await call('Page.captureScreenshot',{format:'png'});await writeFile('data/browser-qa/mobile-landscape.png',Buffer.from(shot.data,'base64'));
assert.equal(await evaluate(`localStorage.getItem('fortcamp:battle-hud:v1')`),saved);
await media(false);await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});await wait(200);
const restored=await rect('.hud-skills');assert.ok(Math.abs(restored.width-desktop.width)<1);
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.mobile-battle-tabs')).display`),'none');
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/battle-lab/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.labFixtureReady)'))break;await wait(200)}
assert.equal(await evaluate('Boolean(window.labFixtureReady)'),true);
await media(true);
for(const [width,height] of [[430,760],[932,430]]){
 await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:true});
 await evaluate('window.labOpen()');await wait(200);
 await evaluate(`document.querySelector('[data-lab-team-source]').value='jobs';document.querySelector('[data-lab-team-source]').dispatchEvent(new Event('change'));document.querySelector('[data-tester-job]').scrollIntoView({block:'center'})`);
 const job=await rect('[data-tester-job]');
 assert.ok(job.width>=100&&job.x>=0&&job.right<=width&&job.top>=0&&job.bottom<=height,'Job selector is reachable at '+width);
 const hit=await evaluate(`(()=>{const s=document.querySelector('[data-tester-job]'),r=s.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)===s})()`);
 assert.equal(hit,true,'class selector is not covered');
 await evaluate(`(()=>{const s=document.querySelector('[data-tester-job]');s.value='mage';s.dispatchEvent(new Event('change'))})()`);
 assert.equal(await evaluate(`document.querySelector('[data-tester-job]').value`),'mage');
 await evaluate(`document.querySelector('[data-lab-close]').click()`);
}
await media(false);
assert.deepEqual(errors,[]);console.log('Mobile battle gestures/layout, desktop restoration and reachable Battle Lab class selection in both orientations passed.');ws.close();
