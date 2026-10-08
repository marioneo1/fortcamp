// Isolated fixtures only: never uses the live API or player saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const point=selector=>evaluate(`(()=>{const r=document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);
const right=async p=>{await call('Input.dispatchMouseEvent',{type:'mousePressed',...p,button:'right',buttons:2,clickCount:1});await call('Input.dispatchMouseEvent',{type:'mouseReleased',...p,button:'right',buttons:0,clickCount:1});await wait(50)};
const shot=async name=>writeFile(`staging-ui/druid-v1/${name}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<120;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(200)}
assert.equal(await evaluate('Boolean(window.mageReady)'),true);
await evaluate(`window.mageShow('druid_inspect')`);await wait(350);
const enemy=await evaluate(`(()=>{const r=document.querySelector('.battle-token.enemy').getBoundingClientRect();return {x:r.x+r.width*.8,y:r.y+r.height*.8}})()`);await right(enemy);
assert.equal(await evaluate(`Boolean(document.getElementById('combat-unit-window'))`),true);
await evaluate(`window.mageShow('druid_hover')`);await wait(200);
const layout=await evaluate(`(()=>{const panel=document.getElementById('combat-unit-window'),summary=panel.querySelector('.unit-detail-summary').getBoundingClientRect(),effects=panel.querySelector('.unit-detail-effects'),r=effects.getBoundingClientRect(),cards=[...panel.querySelectorAll('.effect-detail-card')].map(e=>e.getBoundingClientRect());return {width:panel.offsetWidth,height:panel.offsetHeight,summaryBottom:summary.bottom,effectsTop:r.top,scrollHeight:effects.scrollHeight,clientHeight:effects.clientHeight,count:cards.length,cardWidth:cards[1].width}})()`);
assert.ok(layout.width>=650);assert.ok(layout.height<700);assert.ok(layout.effectsTop>=layout.summaryBottom);assert.ok(layout.scrollHeight>layout.clientHeight);assert.equal(layout.count,14);assert.ok(layout.cardWidth>250);
// Move the unit window aside so effect popup and stats can be read together.
await evaluate(`Object.assign(document.getElementById('combat-unit-window').style,{left:'20px',top:'30px'})`);
await right(await point('#combat-unit-window [data-effect-id="innate_resistance"]'));
assert.equal(await evaluate(`document.querySelectorAll('#combat-effect-window').length`),1);
assert.equal(await evaluate(`document.querySelectorAll('#combat-unit-window').length`),1);
const resistanceText=await evaluate(`document.getElementById('combat-effect-window').textContent`);
for(const rule of ['stun: 25%','Burn still applies','Push / pull: 25%'])assert.ok(resistanceText.includes(rule));
await evaluate(`Object.assign(document.getElementById('combat-effect-window').style,{left:'730px',top:'40px'})`);
await shot('details-crowded');
// Repeated opens reuse one effect window and leave unit details untouched.
await right(await point('#combat-unit-window [data-effect-id="innate_resistance"]'));
assert.equal(await evaluate(`document.querySelectorAll('#combat-effect-window').length`),1);
await evaluate(`(()=>{const effects=document.querySelector('.unit-detail-effects');effects.scrollTop=effects.querySelector('[data-effect-id="poison"]').offsetTop-effects.offsetTop-15})()`);
await right(await point('#combat-unit-window [data-effect-id="poison"]'));
assert.equal(await evaluate(`document.getElementById('combat-effect-window').dataset.effectId`),'poison');
assert.match(await evaluate(`document.getElementById('combat-effect-window').textContent`),/10% max HP.*duration, not damage.*5 turns remaining/);
assert.equal(await evaluate(`document.querySelectorAll('#combat-effect-window').length`),1);
// Dragging the effect panel changes its location, independently of unit details.
const scrollBefore=await evaluate(`document.querySelector('.unit-detail-effects').scrollTop`);
assert.ok(scrollBefore>0);await evaluate(`window.mageShow('druid_hover')`);await wait(100);
assert.equal(await evaluate(`document.querySelector('.unit-detail-effects').scrollTop`),scrollBefore);
assert.equal(await evaluate(`document.getElementById('combat-effect-window').dataset.effectId`),'poison');
const handle=await point('#combat-effect-window .unit-window-handle');
await call('Input.dispatchMouseEvent',{type:'mouseMoved',...handle,buttons:0});await wait(50);
await call('Input.dispatchMouseEvent',{type:'mousePressed',...handle,button:'left',buttons:1,clickCount:1});
await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:handle.x+70,y:handle.y+60,button:'left',buttons:1});
await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:handle.x+70,y:handle.y+60,button:'left',buttons:0});
assert.equal(await evaluate(`parseFloat(document.getElementById('combat-effect-window').style.left)`),800);
assert.equal(await evaluate(`parseFloat(document.getElementById('combat-unit-window').style.left)`),20);
await evaluate(`document.querySelector('#combat-effect-window button').click()`);
assert.equal(await evaluate(`Boolean(document.getElementById('combat-effect-window'))`),false);
assert.equal(await evaluate(`Boolean(document.getElementById('combat-unit-window'))`),true);
await evaluate(`document.querySelector('#combat-unit-window button').click()`);
// Actual map badge hover retains complete rules; its right-click opens only the effect.
const badge=await point('.battle-token.enemy [data-unit-status="poison"]');
await call('Input.dispatchMouseEvent',{type:'mouseMoved',...badge,buttons:0});await wait(50);
assert.match(await evaluate(`document.getElementById('combat-unit-inspect').textContent`),/before damage modifiers.*one stack expires after each tick.*Right-click to keep this effect open/);
await right(badge);
assert.equal(await evaluate(`document.getElementById('combat-effect-window')?.dataset.effectId`),'poison');
assert.equal(await evaluate(`document.getElementById('combat-unit-window')===null`),true);
assert.equal(await evaluate(`document.getElementById('combat-unit-inspect').hidden`),true);
await shot('effect-pinned');
await evaluate(`document.querySelector('#combat-effect-window button').click()`);
// A smaller viewport stays bounded; overflow remains scrollable.
await evaluate(`window.mageShow('druid_inspect')`);await wait(150);await right(enemy);
await evaluate(`Object.assign(document.getElementById('combat-unit-window').style,{left:'8px',top:'8px'})`);
await call('Emulation.setDeviceMetricsOverride',{width:550,height:750,deviceScaleFactor:1,mobile:false});
await wait(100);
assert.ok(await evaluate(`(()=>{const r=document.getElementById('combat-unit-window').getBoundingClientRect();return r.width<=innerWidth&&r.right<=innerWidth&&r.bottom<=innerHeight})()`));
assert.deepEqual(errors,[]);
console.log('PASS 14-effect full-width grid, bounded scroll, independent singleton effect window, replacement, drag/close, map badge full hover and right-click, small viewport.');
ws.close();
