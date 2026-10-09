// Isolated authored encounter presentation; never reads live saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');await call('Page.bringToFront');
await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:true});
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(200)}
await evaluate(`window.mageShow('swarm_before')`);await wait(800);
await evaluate(`window.mageShow('swarm_after')`);await wait(50);
assert.equal(await evaluate(`Boolean(document.querySelector('[data-battle-unit="transition-contract_enemy_1"]'))`),true,'rat remains visible until merging');
await wait(450);
assert.equal(await evaluate(`Boolean(document.querySelector('[data-battle-unit="transition-contract_enemy_1"]'))`),false,'merged rat disappears at merge');
assert.equal(await evaluate(`document.querySelector('[data-battle-unit="contract_enemy_0"] > i > b').textContent`),'14');
await wait(300);
assert.ok(await evaluate(`Boolean(document.querySelector('[data-battle-unit="player"] [data-unit-status="rat_weakness"]'))`));
await writeFile('data/browser-qa/rat-swarm.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`window.mageShow('bandit_before')`);await wait(600);
await evaluate(`window.mageShow('bandit_talk')`);await wait(150);
assert.ok(await evaluate(`document.querySelector('.combat-dialogue')?.textContent.includes('This road is ours')`));
// Unit Details opens through actual right-click controls, independent of module fixture data.
const target=await evaluate(`document.querySelector('[data-battle-unit="contract_enemy_1"]').getBoundingClientRect().toJSON()`);
await call('Input.dispatchMouseEvent',{type:'mousePressed',x:target.x+target.width/2,y:target.y+target.height/2,button:'right',buttons:2,clickCount:1});
await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:target.x+target.width/2,y:target.y+target.height/2,button:'right',clickCount:1});
await wait(100);
assert.ok(await evaluate(`document.querySelector('#combat-unit-window').textContent.includes('Road Trapper')`));
assert.ok(await evaluate(`document.querySelector('#combat-unit-window').textContent.includes('Road Bola')`));
assert.deepEqual(errors,[]);console.log('Rat merge body/HP timing, Weakness, bandit dialogue and inspectable mixed kit passed.');ws.close();
