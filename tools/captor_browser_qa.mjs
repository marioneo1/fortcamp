// Isolated Captor UI regression fixture; no live API or player saves.
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


await evaluate(`window.mageShow('captor_ready')`);await wait(900);
assert.equal(await evaluate(`document.querySelectorAll('[data-combat-mode="attack"]').length`),1);
assert.equal(await evaluate(`document.querySelectorAll('[data-combat-mode="subdue"]').length`),1);
assert.ok(await evaluate(`document.querySelector('.captor-resolve meter').max>0`));
// Use a known local portrait so network-independent geometry checks exercise a real face.
await evaluate(`{const enemy=document.querySelector('.battle-token.enemy'),img=enemy.querySelector('img');if(img)img.src=document.querySelector('.battle-token.player img').src}`);
assert.ok(await evaluate(`(()=>{const token=document.querySelector('.battle-token.enemy'),face=token.querySelector('.portrait-crop')||token.querySelector('img')||token.querySelector(':scope>span'),r=token.querySelector('.captor-resolve').getBoundingClientRect(),f=face.getBoundingClientRect();return r.top>=f.bottom&&token.querySelector(':scope>i b').textContent==='80'})()`));
await evaluate(`document.querySelector('[data-combat-mode="attack"]').click()`);
assert.equal(await evaluate(`window.mageInspect().mode`),'attack');
assert.ok(await evaluate(`document.querySelector('.battlefield').classList.contains('mode-attack')`));
await evaluate(`document.querySelector('.battle-token.enemy').click()`);await wait(300);
assert.equal(await evaluate(`window.mageSent.at(-1).body.action`),'attack');
await evaluate(`window.mageShow('captor_ready')`);await wait(200);
await evaluate(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true}))`);
assert.equal(await evaluate(`window.mageInspect().mode`),'subdue');
await evaluate(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'a',bubbles:true}))`);
assert.equal(await evaluate(`window.mageInspect().mode`),'attack');
await evaluate(`document.dispatchEvent(new KeyboardEvent('keydown',{key:'n',bubbles:true}))`);
await evaluate(`document.querySelector('.battle-token.enemy').click()`);await wait(300);
assert.equal(await evaluate(`window.mageSent.at(-1).body.action`),'subdue');
await evaluate(`window.mageShow('captor_ready')`);await wait(200);

await writeFile('data/browser-qa/captor-ready.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('captor_abduct')`);await wait(500);
await evaluate(`document.querySelector('[data-hotbar-skill="job:captor:abduct"]').click()`);
assert.ok(await evaluate(`Boolean(document.querySelector('.captor-drag-prompt.summoner-panel [data-placement-handle]'))`));
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.captor-drag-prompt')).pointerEvents`),'auto');
assert.notEqual(await evaluate(`getComputedStyle(document.querySelector('.captor-drag-prompt')).backgroundImage`),'none');
await writeFile('data/browser-qa/captor-abduct.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
const enemy=await evaluate(`Object.values(window.mageInspect().previews['job:captor:abduct'])[0]`);
assert.ok(enemy.drag_destinations);
await evaluate(`document.querySelector('.battle-token.enemy').click()`);
assert.ok(await evaluate(`document.querySelectorAll('.captor-drag-layer i').length>0`));
const key=Object.keys(enemy.drag_destinations)[0];
await evaluate(`document.querySelector('[data-battle-cell="${key}"]').click()`);
assert.equal(await evaluate(`document.querySelector('[data-captor-confirm]').disabled`),false);
await evaluate(`document.querySelector('[data-captor-confirm]').click()`);await wait(300);
assert.equal(await evaluate(`window.mageSent.at(-1).body.skill_id`),'job:captor:abduct');
await evaluate(`window.mageShow('captor_hold')`);await wait(900);
assert.match(await evaluate(`document.querySelector('[data-hotbar-skill="job:captor:restraining_hold"]').textContent`),/Release Hold/);
await writeFile('data/browser-qa/captor-hold.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('captor_ready')`);await wait(800);
await evaluate(`window.mageShow('captor_bola')`);await wait(100);
assert.ok(await evaluate(`Boolean(document.querySelector('.captor-projectile'))`));
await wait(700);
assert.equal(await evaluate(`document.querySelectorAll('.captor-projectile,.captor-effect').length`),0);
assert.deepEqual(errors,[]);console.log('Captor commands, Resolve, Abduct confirmation, Release Hold, Bola playback: PASS');ws.close();
