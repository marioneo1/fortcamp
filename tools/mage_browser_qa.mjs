import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json(),ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||JSON.stringify(m.params.exceptionDetails))};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value},wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<180;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(180)}
console.log('Startup errors:',errors);assert.equal(await evaluate('Boolean(window.mageReady)'),true);await wait(400);
assert.equal(await evaluate(`Array.from(document.images).filter(i=>i.src.includes('mage-v1')&&i.getClientRects().length).every(i=>i.complete&&i.naturalWidth>0)`),true);
await writeFile('staging-ui/mage-v1/elemental.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`document.querySelector('[data-hotbar-skill="job:mage:enchant_weapon"]').click();document.querySelector('.battle-token.player.current').click()`);await wait(150);
assert.equal(await evaluate(`Boolean(document.querySelector('.mage-element-prompt'))`),true);assert.equal(await evaluate('window.mageSent.length'),0);
await writeFile('staging-ui/mage-v1/enchant.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`document.querySelector('[data-mage-cancel]').click()`);assert.equal(await evaluate('window.mageSent.length'),0);
await evaluate(`document.querySelector('[data-hotbar-skill="job:mage:enchant_weapon"]').click();document.querySelector('.battle-token.player.current').click();document.querySelector('[data-mage-element="frost"]').click()`);await wait(250);
assert.equal(await evaluate('window.mageSent[0].body.element'),'frost');
await evaluate(`window.mageShow('frozen')`);await wait(650);assert.ok(await evaluate(`document.querySelectorAll('.mage-ice-shell .ice-surface').length>0`));
await writeFile('staging-ui/mage-v1/frozen.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
for(const material of ['grass','dirt','stone']){
 await evaluate(`window.mageShow('surface_${material}')`);await wait(650);
 const counts=await evaluate(`({flames:document.querySelectorAll('.scorch-main-flame').length,minis:document.querySelectorAll('.scorch-mini-flame').length,soot:document.querySelectorAll('.scorch-soot').length,legacy:document.querySelectorAll('.mage-zone-flame').length})`);
 assert.ok(counts.soot>0&&counts.flames===counts.soot&&counts.minis===0);assert.equal(counts.legacy,0);
 const surfaceLoaded=await evaluate(`Promise.all([...new Set(Array.from(document.querySelectorAll('.battlefield svg image')).map(i=>i.getAttribute('href')).filter(h=>h?.includes('mage-scorched-v2')))].map(async url=>(await fetch(url)).ok)).then(v=>v.every(Boolean))`);assert.equal(surfaceLoaded,true);
 const geometry=await evaluate(`(()=>{const shell=document.querySelector('.mage-ice-shell'),face=shell.parentElement.querySelector('.portrait-crop'),a=shell.getBoundingClientRect(),b=face.getBoundingClientRect();return {delta:Math.abs(a.x-b.x)+Math.abs(a.y-b.y)+Math.abs(a.width-b.width),flame:document.querySelector('.scorch-flame').getBoundingClientRect().width}})()`);assert.ok(geometry.delta<1&&geometry.flame>10);
 await writeFile(`staging-ui/mage-v1/surface-${material}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
}
await evaluate(`window.mageShow('fireball')`);await wait(280);assert.ok(await evaluate(`document.querySelectorAll('.mage-ice-transition').length>0`));await wait(1000);assert.equal(await evaluate(`document.querySelectorAll('.mage-ice-transition').length`),0);
await evaluate(`window.mageShow('channel')`);await wait(250);assert.ok(await evaluate(`document.querySelectorAll('.zone-meteor_armed').length>0`));
await writeFile('staging-ui/mage-v1/channel.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('meteor')`);await wait(100);assert.ok(await evaluate(`Array.from(document.querySelectorAll('[data-scorch-cell]')).some(n=>n.style.visibility==='hidden')`));await wait(200);assert.ok(await evaluate(`document.querySelectorAll('.mage-effect').length>0`));
assert.equal(await evaluate(`Array.from(document.querySelectorAll('.mage-effect')).every(i=>i.complete&&i.naturalWidth>0)`),true);
await writeFile('staging-ui/mage-v1/meteor.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));await wait(1300);assert.equal(await evaluate(`document.querySelectorAll('.mage-effect').length`),0);assert.equal(await evaluate(`document.querySelectorAll('[data-scorch-cell][style*=hidden]').length`),0);
for(const name of ['chain','fireball','gravity','wind']){await evaluate(`window.mageShow('${name}')`);let visible=false;for(let i=0;i<25;i++){await wait(40);if(await evaluate(`document.querySelectorAll('.mage-effect').length>0`)){visible=true;break}}assert.ok(visible,`${name} has a visible impact`);await writeFile(`staging-ui/mage-v1/${name}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));await wait(2200)}
assert.deepEqual(errors,[]);console.log('Mage browser checks passed: icons, cancelled/selected enchant, ice shell, channel telegraph, all five impact effects and cleanup.');ws.close();
