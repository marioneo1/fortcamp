// Isolated Druid UI regression fixture; no live API or player saves.
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

await evaluate(`window.mageShow('cleric_ready')`);await wait(200);
assert.equal(await evaluate(`document.querySelectorAll('[data-hotbar-skill^="job:cleric:"]').length`),5);
await evaluate(`window.mageShow('druid_ready')`);await wait(650);
assert.equal(await evaluate(`document.querySelectorAll('[data-hotbar-skill]').length>0&&Array.from(document.querySelectorAll('[data-hotbar-skill]')).every(b=>!b.textContent.includes('Humanoid Form'))`),true);
assert.equal(await evaluate(`document.querySelectorAll('[data-hotbar-skill^="job:druid:"]').length`),5);
assert.equal(await evaluate(`Array.from(document.querySelectorAll('.ability-icon img')).filter(i=>i.src.includes('druid-v1')).every(i=>i.naturalWidth>0)`),true);
await evaluate(`document.querySelector('[data-hotbar-skill="job:druid:bramble_wall"]').click()`);
await evaluate(`document.querySelector('[data-battle-cell="3,3"]').click()`);
assert.equal(await evaluate(`Boolean(document.querySelector('[data-rogue-confirm]'))`),true);
assert.match(await evaluate(`document.querySelector('.rogue-prompt-card').textContent`),/shared|share/);
assert.equal(await evaluate(`window.mageSent.length`),0);
await writeFile('staging-ui/druid-v1/placement.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`document.querySelector('[data-rogue-confirm]').click()`);await wait(150);
const sent=await evaluate(`window.mageSent.at(-1).body`);assert.equal(sent.skill_id,'job:druid:bramble_wall');assert.equal(sent.rotation,0);assert.equal(sent.x,3);
for(const [key,target] of [['rejuvenation','ally'],['living_armor','player']]){
 await evaluate(`window.mageShow('druid_support')`);await wait(150);
 await evaluate(`document.querySelector('[data-hotbar-skill="job:druid:${key}"]').click()`);
 const actorId=await evaluate(`window.mageInspect().actor.id`),targetId=target==='player'?actorId:target;
 const count=await evaluate(`window.mageSent.length`);
 await evaluate(`document.querySelector('[data-battle-unit="${targetId}"]').click()`);await wait(150);
 assert.equal(await evaluate(`window.mageSent.length`),count+1);
 const command=await evaluate(`window.mageSent.at(-1).body`);assert.equal(command.skill_id,'job:druid:'+key);assert.equal(command.target_id,targetId);
}
for(const kind of ['prowler','bulwark','rat']){
 await evaluate(`window.mageShow('druid_${kind}')`);await wait(650);
 assert.match(await evaluate(`window.mageInspect().actor.portrait`),new RegExp('portrait_'+kind));
 assert.equal(await evaluate(`document.querySelector('[data-hotbar-skill="job:druid:${kind}"]').textContent.includes('Humanoid Form')`),true);
 assert.equal(await evaluate(`document.querySelector('[data-hotbar-skill="job:druid:rejuvenation"]').getAttribute('aria-disabled')`),'true');
 await evaluate(`document.querySelector('[data-hotbar-skill="job:druid:${kind}"]').click()`);
 assert.equal(await evaluate(`document.querySelector('.spell-self-label')?.textContent`),'SELF');
 await writeFile(`staging-ui/druid-v1/${kind}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
}
await evaluate(`window.mageShow('druid_wall')`);await wait(250);
assert.equal(await evaluate(`document.querySelectorAll('.battle-terrain.bramble_wall').length`),3);
await writeFile('staging-ui/druid-v1/wall.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('druid_lash')`);await wait(100);
assert.equal(await evaluate(`document.querySelectorAll('.druid-vine-lash').length`),1);
await writeFile('staging-ui/druid-v1/lash.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await wait(900);assert.equal(await evaluate(`document.querySelectorAll('.druid-vine-lash').length`),0);
await evaluate(`window.mageShow('druid_growth')`);await wait(180);
assert.ok(await evaluate(`document.querySelectorAll('.druid-transformation').length>0`));
await wait(800);assert.equal(await evaluate(`document.querySelectorAll('.druid-transformation').length`),0);

await evaluate(`window.mageShow('druid_support')`);await wait(250);
const selfId=await evaluate(`window.mageInspect().actor.id`);
await evaluate(`document.querySelector('[data-hotbar-skill="job:druid:prowler"]').click()`);
assert.equal(await evaluate(`document.querySelector('.spell-self-target')?.dataset.battleUnit`),selfId);
assert.equal(await evaluate(`document.querySelector('.spell-self-target .spell-self-label')?.textContent`),'SELF');
const rect=await evaluate(`(()=>{const r=document.querySelector('[data-battle-unit="'+window.mageInspect().actor.id+'"]').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);
const beforeCount=await evaluate(`window.mageSent.length`);
await call('Input.dispatchMouseEvent',{type:'mousePressed',...rect,button:'right',buttons:2,clickCount:1});
await call('Input.dispatchMouseEvent',{type:'mouseReleased',...rect,button:'right',buttons:0,clickCount:1});await wait(80);
assert.equal(await evaluate(`document.getElementById('combat-unit-window')?.dataset.unitId`),selfId);
assert.equal(await evaluate(`window.mageSent.length`),beforeCount);
assert.match(await evaluate(`document.querySelector('#combat-unit-window .unit-window-body').textContent`),/Armor|ARM/);
const initial=await evaluate(`(()=>{const r=document.querySelector('.unit-window-handle').getBoundingClientRect();return {x:r.x+100,y:r.y+15}})()`);
const oldLeft=await evaluate(`parseFloat(document.getElementById('combat-unit-window').style.left)`);
await call('Input.dispatchMouseEvent',{type:'mousePressed',...initial,button:'left',buttons:1,clickCount:1});
await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:initial.x-60,y:initial.y-30,button:'left',buttons:1});
await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:initial.x-60,y:initial.y-30,button:'left',buttons:0});
assert.ok(await evaluate(`parseFloat(document.getElementById('combat-unit-window').style.left)<${oldLeft}`));
const armor=await evaluate(`(()=>{const el=Array.from(document.querySelectorAll('#combat-unit-window .inspect-stat')).find(el=>el.textContent.startsWith('ARM'));const r=el.getBoundingClientRect();return {x:r.x+10,y:r.y+10}})()`);
await call('Input.dispatchMouseEvent',{type:'mouseMoved',...armor,buttons:0});await wait(50);
assert.ok(await evaluate(`Boolean(document.getElementById('combat-stat-tooltip'))`));
assert.ok(await evaluate(`document.getElementById('combat-stat-tooltip').getBoundingClientRect().bottom<=innerHeight`));
assert.match(await evaluate(`document.querySelector('#combat-unit-window .unit-window-body').textContent`),/Armor is flat reduction/);
await writeFile('staging-ui/druid-v1/inspector.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`document.querySelector('#combat-unit-window button').click()`);
assert.equal(await evaluate(`document.getElementById('combat-unit-window')===null`),true);

await evaluate(`window.mageShow('druid_inspect')`);await wait(200);
const enemyPoint=await evaluate(`(()=>{const el=document.querySelector('.battle-token.enemy'),r=el.getBoundingClientRect();return {x:r.x+r.width*.8,y:r.y+r.height*.8,id:el.dataset.battleUnit}})()`);
await call('Input.dispatchMouseEvent',{type:'mousePressed',...enemyPoint,button:'right',buttons:2,clickCount:1});
await call('Input.dispatchMouseEvent',{type:'mouseReleased',...enemyPoint,button:'right',buttons:0,clickCount:1});await wait(80);
assert.equal(await evaluate(`document.getElementById('combat-unit-window')?.dataset.unitId`),enemyPoint.id);
const text=await evaluate(`document.querySelector('#combat-unit-window .unit-window-body').textContent`);
assert.match(text,/Innate resistances/);assert.match(text,/Push \/ pull: 25%/);assert.match(text,/stun: 25%/);assert.match(text,/at most 1 target turn/);
await evaluate(`document.querySelector('#combat-unit-window button').click()`);
assert.deepEqual(errors,[]);console.log('PASS Druid placement/confirmation command, three animal portraits, humanoid return, animal spell restriction, shared wall rendering, lash/growth effects and cleanup.');ws.close();
