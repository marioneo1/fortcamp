// Isolated Cleric UI regression fixture; no live API or player saves.
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
assert.equal(await evaluate(`Array.from(document.querySelectorAll('.ability-icon img')).filter(i=>i.src.includes('cleric-v1')).every(i=>i.naturalWidth>0)`),true);
await evaluate(`document.querySelector('[data-hotbar-skill="job:cleric:sanctuary"]').click()`);
await evaluate(`document.querySelector('[data-battle-cell="3,3"]').dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:document.querySelector('[data-battle-cell="3,3"]').getBoundingClientRect().x+10,clientY:document.querySelector('[data-battle-cell="3,3"]').getBoundingClientRect().y+10}))`);
assert.equal(await evaluate(`document.querySelectorAll('.spell-area').length`),9);
await evaluate(`document.querySelector('[data-hotbar-skill="job:cleric:holy_light"]').click()`);
await evaluate(`document.querySelector('[data-battle-cell="3,3"]').dispatchEvent(new PointerEvent('pointermove',{bubbles:true,clientX:document.querySelector('[data-battle-cell="3,3"]').getBoundingClientRect().x+10,clientY:document.querySelector('[data-battle-cell="3,3"]').getBoundingClientRect().y+10}))`);
assert.equal(await evaluate(`document.querySelectorAll('.spell-area').length`),5);
await writeFile('staging-ui/cleric-v1/holy-preview.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('cleric_rest')`);await wait(100);
assert.equal(await evaluate(`document.querySelector('[data-hotbar-skill="job:cleric:rest"]').textContent.includes('End Rest')`),true);
await evaluate(`window.mageShow('cleric_priest')`);await wait(100);
assert.equal(await evaluate(`document.querySelector('[data-hotbar-skill="job:cleric:sanctuary"]').textContent.includes('Regeneration')`),true);
await evaluate(`document.querySelector('[data-hotbar-skill="job:cleric:heal"]').click()`);
assert.equal(await evaluate(`document.querySelectorAll('.spell-self-target').length`),1);
await evaluate(`window.mageShow('cleric_sanctuary')`);await wait(100);
assert.ok(await evaluate(`document.querySelectorAll('.zone-sanctuary').length>0`));
await evaluate(`window.mageShow('cleric_light')`);await wait(300);
assert.ok(await evaluate(`document.querySelectorAll('.cleric-holy-impact').length>0`));
await writeFile('staging-ui/cleric-v1/holy-impact.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await wait(1300);assert.equal(await evaluate(`document.querySelectorAll('.cleric-holy-impact').length`),0);
assert.deepEqual(errors,[]);console.log('PASS Cleric icons, 3x3 Sanctuary, 5-cell cross, End Rest, self-only Priest heal, Regeneration name, Sanctuary and holy impact/cleanup.');ws.close();
