// Runs against an isolated fixture; never contacts the live game API.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text+' '+JSON.stringify(r.exceptionDetails.exception));return r.result.value};
const wait=()=>new Promise(r=>setTimeout(r,180));
await call('Runtime.enable');
await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:true});
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/battle-lab/preview.html'});
for(let i=0;i<80;i++){if(await evaluate('Boolean(window.labFixtureReady)'))break;await wait()}
assert.equal(await evaluate('Boolean(window.labFixtureReady)'),true);
await evaluate("document.querySelector('#debug-battle-lab').click()");await wait();
assert.equal(await evaluate('document.querySelector(".battle-lab").open'),true);
assert.equal(await evaluate('document.querySelectorAll("[data-lab-mission]").length'),79);
await evaluate("const a=document.querySelector('[data-lab-approach]');a.value='Choose the approach|||Scout an ambush position';a.dispatchEvent(new Event('change'));");
assert.equal(await evaluate('document.querySelectorAll("[data-lab-outcome] option").length'),3);
await writeFile('staging-ui/battle-lab/desktop.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate("document.querySelector('[data-lab-start]').click()");await wait();
assert.ok((await evaluate('document.querySelector(".battle-lab-toolbar").textContent')).includes('Goblin Warcamp'));
assert.ok((await evaluate('document.querySelector(".battle-log").textContent')).includes('asleep'));
await evaluate("document.querySelector('[data-lab-restart]').click()");await wait();
assert.equal(await evaluate('window.labRequests.filter(r=>r.body?.mission_id).length'),2);
await evaluate("document.querySelector('[data-lab-return]').click()");await wait();
await evaluate("{const q=document.querySelector('[data-lab-query]');q.value='captive cart';q.dispatchEvent(new Event('input'));}");
assert.equal(await evaluate('document.querySelectorAll("[data-lab-mission]").length'),1);
await evaluate("document.querySelector('[data-lab-mission]').click();document.querySelector('[data-lab-start]').click()");await wait();
assert.ok((await evaluate('document.querySelector(".battle-lab-toolbar").textContent')).includes('D Rank'));
const wagon=await evaluate("(()=>{const el=document.querySelector('[data-battle-terrain=cart_body]');const art=getComputedStyle(el,'::before');return {width:parseFloat(art.width)/el.offsetWidth,height:parseFloat(art.height)/el.offsetHeight,source:el.style.getPropertyValue('--battle-prop')}})()");
assert.ok(wagon.width>1.85&&wagon.width<=2);assert.ok(wagon.height>1.85&&wagon.height<=2);assert.ok(wagon.source.includes('prison_wagon'));
await writeFile('staging-ui/battle-lab/captive-cart.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate("document.querySelector('[data-lab-return]').click()");await wait();
await evaluate("{const q=document.querySelector('[data-lab-query]');q.value='hedgerow watch';q.dispatchEvent(new Event('input'));document.querySelector('[data-lab-mission]').click();document.querySelector('[data-lab-start]').click();}");await wait();
assert.ok(await evaluate('Boolean(document.querySelector("#start-defense"))'));
assert.ok(await evaluate('Boolean(document.querySelector("[data-lab-return]"))'));
await evaluate("document.querySelector('[data-lab-return]').click()");await wait();
await evaluate("{const q=document.querySelector('[data-lab-query]');q.value='intruders at the workshop';q.dispatchEvent(new Event('input'));document.querySelector('[data-lab-mission]').click();}");
assert.equal(await evaluate("document.querySelectorAll('[data-lab-layout] option').length"),5);
const presets=await evaluate("Array.from(document.querySelectorAll('[data-lab-layout] option')).slice(1).map(o=>({seed:o.value,label:o.textContent}))");
for(const preset of presets){
 await evaluate(`{const layout=document.querySelector('[data-lab-layout]');layout.value=${JSON.stringify(preset.seed)};layout.dispatchEvent(new Event('change'));}`);
 assert.equal(await evaluate("document.querySelector('[data-lab-seed]').value"),preset.seed);
 await evaluate("document.querySelector('[data-lab-start]').click()");await wait();
 assert.equal(await evaluate("window.labRequests.filter(r=>r.body?.mission_id).at(-1).body.seed"),preset.seed);
 await evaluate("document.querySelector('[data-lab-return]').click()");await wait();
 assert.equal(await evaluate("document.querySelector('[data-lab-layout]').value"),preset.seed);
}
await evaluate("document.querySelector('[data-lab-new-seed]').click()");
assert.equal(await evaluate("document.querySelector('[data-lab-layout]').value"),'');
await evaluate("{const q=document.querySelector('[data-lab-query]');q.value='building kit';q.dispatchEvent(new Event('input'));}");
assert.equal(await evaluate('document.querySelectorAll("[data-lab-mission]").length'),6);
for(const family of ['timber','fieldstone','limestone','iron','limestone_plan','fieldstone_plan']){
 await evaluate(`document.querySelector('[data-lab-mission="material_${family}"]').click()`);
 const layouts=await evaluate("Array.from(document.querySelectorAll('[data-lab-layout] option')).slice(1).map(o=>o.value)");
 assert.equal(layouts.length,4);
 const shown=new Set();
 for(const [index,seed] of layouts.entries()){
  await evaluate(`{const select=document.querySelector('[data-lab-layout]');select.value='${seed}';select.dispatchEvent(new Event('change'));document.querySelector('[data-lab-start]').click();}`);await wait();
  const battle=await evaluate('window.labCurrentBattle()');
  assert.equal(battle.material_showcase.family,family);
  battle.material_showcase.pieces.forEach(p=>shown.add(p));
  assert.ok((await evaluate('document.querySelector(".battle-lab-toolbar").textContent')).includes('MATERIAL TEST'));
  assert.ok(await evaluate('Boolean(document.querySelector(".lab-pieces"))'));
  if(['fieldstone','limestone'].includes(family))assert.ok(await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).some(e=>e.style.getPropertyValue('--battle-prop').includes('building-v4'))"));
  if(family.endsWith('_plan')){
   assert.ok(await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).some(e=>e.style.getPropertyValue('--battle-prop').includes('building-v5-topdown'))"));
   assert.equal(await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).filter(e=>e.style.getPropertyValue('--battle-prop').includes('building-v5-topdown')).every(e=>e.style.getPropertyValue('--asset-mirror-y')==='1')"),true);
  }
  if(family==='limestone'&&index===1){
   for(const direction of ['north_east','north_west','south_east','south_west'])
    assert.ok(await evaluate(`Array.from(document.querySelectorAll('.wall-connector')).some(e=>e.style.getPropertyValue('--battle-prop').includes('limestone_wall_${direction}.png')&&e.style.getPropertyValue('--asset-rotation')==='0deg')`));
  }
  if(['fieldstone','limestone'].includes(family)&&index===1){
   assert.equal(await evaluate("Array.from(document.querySelectorAll('.wall-cap')).every(e=>Number(getComputedStyle(e).zIndex)===4)"),true);
   assert.equal(await evaluate("Array.from(document.querySelectorAll('.wall-connector:not(.wall-cap)')).every(e=>Number(getComputedStyle(e).zIndex)===Number(e.style.getPropertyValue('--wall-art-layer')))"),true);
   assert.ok(await evaluate("Array.from(document.querySelectorAll('.wall-cap')).some(e=>e.style.getPropertyValue('--asset-rotation')==='180deg'&&e.style.getPropertyValue('--asset-mirror-y')==='-1')"));
  }
  await writeFile(`staging-terrain/${family.endsWith('_plan')?'building-toolset-v5-topdown':'building-toolset-v4'}/${family}-${index+1}-in-game.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
  await evaluate("document.querySelector('[data-lab-return]').click()");await wait();
 }
 assert.equal(shown.size,16,family);
}
await call('Emulation.setDeviceMetricsOverride',{width:430,height:900,deviceScaleFactor:1,mobile:false});await wait();
assert.ok(await evaluate('document.querySelector(".battle-lab").getBoundingClientRect().right<=430'));
assert.ok(await evaluate('document.querySelector(".lab-workspace").scrollHeight>document.querySelector(".lab-workspace").clientHeight'));
await writeFile('staging-ui/battle-lab/mobile.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
assert.deepEqual(errors,[]);
console.log('PASS: 79 entries, original mission workflows and all 24 material layouts; each material covers all 16 pieces; old and overhead stones coexist; mobile layout');
await Promise.race([call('Browser.close'),new Promise(r=>setTimeout(r,1000))]);ws.close();
