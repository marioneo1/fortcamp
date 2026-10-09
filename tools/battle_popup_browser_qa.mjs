// Isolated floating HUD regression fixture; no live API or player saves.
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





const rect=selector=>evaluate(`document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect().toJSON()`);
const mouse=(type,x,y,extra={})=>call('Input.dispatchMouseEvent',{type,x,y,...extra});
async function click(selector){const r=await rect(selector);await mouse('mousePressed',r.x+r.width/2,r.y+r.height/2,{button:'left',clickCount:1});await mouse('mouseReleased',r.x+r.width/2,r.y+r.height/2,{button:'left',clickCount:1});await wait(40)}
async function drag(selector){const r=await rect(selector);await mouse('mousePressed',r.x+35,r.y+12,{button:'left',clickCount:1});await mouse('mouseMoved',r.x+65,r.y+32,{button:'left',buttons:1});await mouse('mouseReleased',r.x+65,r.y+32,{button:'left',clickCount:1})}
await evaluate(`window.mageShow('captor_ready')`);await wait(300);
for(const kind of ['supplies','history','options','passives','skill-order']){
 await evaluate(`document.querySelector('[data-battle-popup="${kind}"]').click()`);
 const close='#battle-popup-'+kind+' [data-close-battle-popup]';
 assert.equal((await rect(close)).width,38);
 await click(close);
 assert.equal(await evaluate(`document.querySelector('#battle-popup-${kind}').open`),false,kind+' closes with real pointer');
}
for(const [fixture,skill,panel,cancel] of [
 ['engineer_ready','job:engineer:sentry_turret','.engineer-panel','[data-engineer-cancel]'],
 ['summoner_ready','job:summoner:bound_companion','.summoner-panel','[data-summon-cancel]'],
 ['captor_abduct','job:captor:abduct','.captor-drag-prompt','[data-captor-cancel]']
]){
 await evaluate(`window.mageShow('${fixture}')`);await wait(300);
 await evaluate(`document.querySelector('[data-hotbar-skill="${skill}"]').click()`);
 // Use the shared header regardless of each class's panel name.
 await drag('[data-placement-handle]');
 if(await evaluate(`Boolean(document.querySelector('${cancel}'))`))await click(cancel);
 assert.equal(await evaluate(`Boolean(document.querySelector('${cancel}'))`),false,fixture+' cancels');
}
await evaluate(`window.mageShow('captor_ready')`);await wait(300);
await evaluate(`(async()=>{const m=await import('/frontend/src/combat-hotbar.js'),b=window.mageInspect().battle;})()`);
// Open inspectors using the same exported UI functions as right-click.
await evaluate(`(async()=>{const m=await import('/frontend/src/combat-hotbar.js'),a=window.mageInspect().actor,b={id:'qa',units:{[a.id]:a},status_definitions:{},width:8,height:8};window.popupQaBattle=b;window.popupQaEscape=x=>String(x);m.openUnitInspector(b,a.id,window.popupQaEscape,{clientX:300,clientY:250})})()`);
await drag('#combat-unit-window .unit-window-handle');await click('#combat-unit-window .unit-window-handle button');
assert.equal(await evaluate(`Boolean(document.querySelector('#combat-unit-window'))`),false,'unit inspector closes after drag');
await evaluate(`(async()=>{const m=await import('/frontend/src/combat-hotbar.js'),b=window.popupQaBattle,a=Object.values(b.units)[0];a.statuses=[{id:'burn',turns:2,stacks:2}];m.openEffectInspector(b,a.id,'burn','',window.popupQaEscape,{clientX:300,clientY:250})})()`);
await drag('#combat-effect-window .unit-window-handle');await click('#combat-effect-window .unit-window-handle button');
assert.equal(await evaluate(`Boolean(document.querySelector('#combat-effect-window'))`),false,'effect inspector closes after drag');
assert.equal((await rect('#mission-close')).width,38,'battle close matches toolbar size');
assert.equal(await evaluate(`document.querySelector('#mission-close').getAttribute('aria-label')`),'Close battle view');
assert.deepEqual(errors,[]);console.log('PASS: real pointer Close/Cancel on battle utilities, placement prompts and dragged unit/effect inspectors');ws.close();
