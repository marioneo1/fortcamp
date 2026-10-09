// Isolated fixture: no live saves, credentials or game-server calls.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:true});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(150)}
assert.equal(await evaluate('Boolean(window.mageReady)'),true);
for(const width of [1440,1000]){
 await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
 for(const fixture of ['elemental','captor_ready']){
  await evaluate(`window.mageShow('${fixture}')`);await wait(200);
  const layout=await evaluate(`(()=>{const panel=document.querySelector('.battle-primary-panel'),grid=panel.querySelector('.combat-actions'),buttons=[...grid.children],r=panel.getBoundingClientRect();return {labels:buttons.map(b=>b.textContent.trim()),rows:[...new Set(buttons.map(b=>Math.round(b.getBoundingClientRect().top)))],columns:getComputedStyle(grid).gridTemplateColumns,placements:buttons.map(b=>({label:b.textContent,col:getComputedStyle(b).gridColumn,row:getComputedStyle(b).gridRow})),panelBottom:r.bottom,groupBottom:panel.closest('.hud-skills').getBoundingClientRect().bottom,inside:buttons.every(b=>b.getBoundingClientRect().bottom+28<=panel.closest('.hud-skills').getBoundingClientRect().bottom+1),guard:!!panel.querySelector('[data-combat-action="guard"]'),help:panel.querySelector('[data-combat-action="end_turn"]').dataset.description}})()`);
  assert.equal(layout.guard,false);
  assert.equal(layout.rows.length,2,JSON.stringify(layout));
  assert.ok(layout.inside,JSON.stringify(layout));
  assert.equal(layout.labels.length,fixture==='elemental'?6:7);
  assert.match(layout.labels.at(-1),/Retreat All/);
  assert.match(layout.help,/Guard.*25%/);
  console.log(width,fixture,layout.columns,layout.rows);
 }
}
for(const ready of [false,true]){
 await evaluate(`window.mageShow('command_exit_${ready?'ready':'hold'}')`);await wait(100);
 await evaluate(`if(!document.querySelector('.context-action-menu'))document.querySelector('[data-context-toggle]').click()`);
 const exit=await evaluate(`(()=>{const button=[...document.querySelectorAll('[data-context-action]')].find(b=>b.textContent.includes('Leave Map'));return {found:!!button,disabled:button?.disabled}})()`);
 assert.equal(exit.found,true);assert.equal(exit.disabled,!ready);
}
assert.deepEqual(errors,[]);
await writeFile('data/browser-qa/command-layout.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
console.log('Two-row commands, optional Subdue, Guard description and held/ready Leave Map passed.');ws.close();
