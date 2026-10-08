// Isolated Engineer UI regression fixture; no live API or player saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:true});await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'about:blank'});await wait(100);errors.length=0;
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<120;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(200)}
assert.equal(await evaluate('Boolean(window.mageReady)'),true);


await evaluate(`window.mageShow('engineer_ready')`);await wait(500);
await evaluate(`document.querySelector('[data-hotbar-skill="job:engineer:sentry_turret"]').click()`);
assert.equal(await evaluate(`document.querySelector('[data-engineer-confirm]').disabled`),true);
const point=await evaluate(`(()=>{const cell=document.querySelector('.engineer-layer i');return {left:cell.style.left,top:cell.style.top}})()`);
assert.ok(point.left);
await evaluate(`document.querySelector('[data-battle-cell="2,1"]').click()`);
assert.equal(await evaluate(`document.querySelector('[data-engineer-confirm]').disabled`),false);
assert.equal(await evaluate(`document.querySelectorAll('.engineer-placement-preview').length`),1);
await evaluate(`document.querySelector('[data-engineer-confirm]').click()`);await wait(300);
assert.deepEqual(await evaluate(`window.mageSent.at(-1).body`),{action:'skill',skill_id:'job:engineer:sentry_turret',x:2,y:1});
await evaluate(`window.mageShow('engineer_mounted')`);await wait(1300);
assert.equal(await evaluate(`document.querySelectorAll('.engineer-operator').length`),1);
assert.equal(await evaluate(`document.querySelectorAll('[data-battle-unit="player"]').length`),0);
assert.equal(await evaluate(`document.querySelectorAll('img[src$="heavy_idle.png"]').length`)>0,true);
await writeFile('data/browser-qa/engineer-mounted.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('engineer_hazards')`);await wait(300);
assert.equal(await evaluate(`document.querySelectorAll('.engineer-hazard').length`),2);
await writeFile('data/browser-qa/engineer-hazards.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('engineer_ready')`);await wait(350);
await evaluate(`document.querySelector('[data-hotbar-skill="job:engineer:sentry_turret"]').click()`);
const handle=await evaluate(`(()=>{const r=document.querySelector('[data-placement-handle]').getBoundingClientRect();return {x:r.left+40,y:r.top+12}})()`);
await call('Input.dispatchMouseEvent',{type:'mousePressed',x:handle.x,y:handle.y,button:'left',clickCount:1});
await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:handle.x+75,y:handle.y+25,button:'left',buttons:1});
await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:handle.x+75,y:handle.y+25,button:'left',clickCount:1});
assert.equal(await evaluate(`document.querySelector('.engineer-panel').style.position`),'fixed');
const saved=await evaluate(`localStorage.getItem('fortcamp:placement:engineer')`);assert.ok(saved);
await evaluate(`document.querySelector('[data-battle-cell="2,1"]').click();document.dispatchEvent(new KeyboardEvent('keydown',{key:'e',bubbles:true}))`);await wait(200);
assert.equal(await evaluate(`window.mageSent.at(-1).body.skill_id`),'job:engineer:sentry_turret');
await evaluate(`(async()=>{await window.mageShow('engineer_ready');document.querySelector('[data-hotbar-skill="job:engineer:sentry_turret"]').click()})()`);await wait(100);
assert.equal(await evaluate(`document.querySelector('.engineer-panel').style.position`),'fixed');
await evaluate(`window.mageShow('engineer_direct')`);await wait(1000);
for(const skill of ['dynamite','proximity_charge','rapid_assembly','man_the_guns','scuttle_protocol']){
 await evaluate(`document.querySelector('[data-hotbar-skill="job:engineer:${skill}"]').click()`);await wait(100);
 assert.equal(await evaluate(`document.querySelectorAll('.engineer-panel').length`),0,skill+' should use normal targeting');
 if(skill==='rapid_assembly')assert.equal(await evaluate(`document.querySelectorAll('.spell-self-target').length`),1);
 if(skill==='scuttle_protocol'){
  await evaluate(`document.querySelector('[data-battle-unit="machine_1"]').dispatchEvent(new MouseEvent('pointermove',{bubbles:true}))`);
  assert.ok(await evaluate(`document.querySelectorAll('.spell-area').length`)>0);
  assert.ok(await evaluate(`document.querySelectorAll('[data-aoe-preview]').length`)>0);
 }
}
await evaluate(`window.mageShow('engineer_unfinished')`);await wait(150);
assert.equal(await evaluate(`document.querySelectorAll('img[src$="sentry_unfinished.png"]').length`),1);
await evaluate(`window.mageShow('engineer_destroyed')`);await wait(30);
assert.equal(await evaluate(`document.querySelectorAll('[data-battle-unit="transition-machine_1"]').length`),1);
await wait(3000);assert.equal(await evaluate(`document.querySelectorAll('[data-battle-unit="transition-machine_1"]').length`),0);
assert.equal(await evaluate(`document.querySelectorAll('img[src$="sentry_destroyed.png"]').length`),1);
await evaluate(`window.mageShow('engineer_hazards')`);await wait(100);
await evaluate(`window.mageShow('engineer_exploded')`);await wait(30);
assert.equal(await evaluate(`document.querySelectorAll('.engineer-hazard').length`),2);
await wait(3500);assert.equal(await evaluate(`document.querySelectorAll('.engineer-hazard').length`),0);
assert.deepEqual(errors,[]);ws.close();console.log('PASS Engineer placement, drag/remember/E confirm, direct targeting, unfinished machines, delayed wrecks and mine explosions.');
