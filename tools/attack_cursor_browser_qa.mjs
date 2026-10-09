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

await evaluate(`window.mageShow('bandit_adjacent')`);await wait(600);for(let i=0;i<60&&await evaluate('window.mageInspect().blocked');i++)await wait(100);
await call('Input.dispatchKeyEvent',{type:'keyDown',key:'a',code:'KeyA',windowsVirtualKeyCode:65});
await call('Input.dispatchKeyEvent',{type:'keyUp',key:'a',code:'KeyA',windowsVirtualKeyCode:65});
assert.equal(await evaluate('window.mageInspect().mode'),'attack');
const target='[data-battle-unit="contract_enemy_0"]';
const cursors=await evaluate(`(()=>{const t=document.querySelector('${target}');return [t,...t.querySelectorAll('*')].map(e=>({tag:e.tagName,cursor:getComputedStyle(e).cursor}))})()`);
assert.ok(cursors.length>2);assert.ok(cursors.every(c=>c.cursor.includes('attack_cursor.png')),JSON.stringify(cursors));
await evaluate('window.mageSent=[]');
await evaluate(`document.querySelector('${target}').click()`);await wait(100);
const sent=await evaluate('window.mageSent');
assert.equal(sent[0]?.body.action,'attack',JSON.stringify(sent));assert.equal(sent[0].body.target_id,'contract_enemy_0');assert.equal(sent[0].body.move_to,undefined);
await evaluate(`window.mageShow('bandit_before')`);await wait(600);for(let i=0;i<60&&await evaluate('window.mageInspect().blocked');i++)await wait(100);
await call('Input.dispatchKeyEvent',{type:'keyDown',key:'a',code:'KeyA',windowsVirtualKeyCode:65});
await call('Input.dispatchKeyEvent',{type:'keyUp',key:'a',code:'KeyA',windowsVirtualKeyCode:65});
await evaluate('window.mageSent=[]');await evaluate(`document.querySelector('${target}').click()`);
await wait(100);const approach=await evaluate('window.mageSent[0]?.body');
assert.equal(approach?.action,'attack');assert.ok(approach.move_to,'selected Attack includes its approach in one request');
assert.equal(await evaluate(`!!document.querySelector('.tile-action-menu')`),false);
for(const range of ['near','far']){
 await evaluate(`window.mageShow('driving_strike_${range}')`);await wait(600);
 for(let i=0;i<60&&await evaluate('window.mageInspect().blocked');i++)await wait(100);
 await evaluate(`document.querySelector('[data-hotbar-skill="job:fighter:bash"]').click()`);
 assert.equal(await evaluate('window.mageInspect().mode'),'skill');
 await evaluate('window.mageSent=[]');await evaluate(`document.querySelector('${target}').click()`);await wait(100);
 const command=await evaluate('window.mageSent[0]?.body');
 assert.equal(command?.action,'skill',range);assert.equal(command.skill_id,'job:fighter:bash');
 assert.equal(!!command.move_to,range==='far');
 assert.equal(await evaluate(`!!document.querySelector('.tile-action-menu')`),false);
}
await evaluate(`window.mageShow('door_approach')`);await wait(600);
for(let i=0;i<60&&await evaluate('window.mageInspect().blocked');i++)await wait(100);
assert.equal(await evaluate(`document.querySelectorAll('[data-door-control]').length`),1);
assert.equal(await evaluate(`document.querySelector('[data-door-control]').style.top`),'25%');
await evaluate(`window.fetch=()=>new Promise(()=>{});document.querySelector('[data-door-control]').click()`);
assert.deepEqual(await evaluate(`({x:window.mageInspect().actor.x,y:window.mageInspect().actor.y})`),{x:5,y:4},'door approach previews before network response');
assert.deepEqual(errors,[]);console.log('A hotkey, full-portrait sword cursor, direct adjacent attack and single-click distant attack, near/far Driving Strike, centered door and immediate approach passed.');ws.close();
