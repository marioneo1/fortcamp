// Offline real-map preview. No saves or live game endpoints.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9238/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/lighting-v1/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.lightingReady)'))break;await wait(150)}
assert.equal(await evaluate('Boolean(window.lightingReady)'),true);
const mountMarker=await evaluate(`(async()=>{const {mountMarkup}=await import('/frontend/src/mount-art.js');const field=document.querySelector('.battlefield');const token=document.createElement('button');token.className='battle-token boar-prop enemy valid-target';token.style='grid-column:2;grid-row:2';token.innerHTML=mountMarkup({alive:true,mount_facing:'e'});field.append(token);const s=getComputedStyle(token,'::after');const result={display:s.display,art:s.backgroundImage,inset:s.left,opacity:s.opacity};token.classList.add('dead');result.dead=getComputedStyle(token,'::after').display;token.classList.remove('dead');field.classList.add('support-targeting');result.support=getComputedStyle(token,'::after').display;field.classList.remove('support-targeting');token.remove();return result})()`);
assert.equal(mountMarker.display,'block');assert.ok(mountMarker.art.includes('target_hostile'));assert.ok(parseFloat(mountMarker.inset)<0);assert.equal(mountMarker.dead,'none');assert.equal(mountMarker.support,'none');
for(const scene of ['goblin_warcamp','tool_shed']){
 await evaluate(`window.lightingShow('${scene}')`);
 if(scene==='goblin_warcamp'){
  const walls=await evaluate(`(()=>{const walls=[...document.querySelectorAll('.palisade.has-prop-art:not(.multi-cell-asset)')];return walls.map(p=>({filter:getComputedStyle(p).filter,art:getComputedStyle(p).backgroundImage,before:getComputedStyle(p,'::before').content,hpShadow:getComputedStyle(p.querySelector('.terrain-hp')).boxShadow}))})()`);
  assert.ok(walls.length>0);
  for(const wall of walls){assert.ok(!wall.filter.includes('drop-shadow'));assert.equal(wall.hpShadow,'none');assert.notEqual(wall.art,'none');assert.ok(['none','normal'].includes(wall.before));}
 }

 assert.equal(await evaluate('document.querySelectorAll("[data-dev-launcher]").length'),1);
 for(const [preset,label] of [[12,'Day'],[29,'Dusk'],[42,'Night'],[59,'Dawn']]){
  await evaluate(`document.querySelector('[data-light-preset="${preset}"]').click()`);
  assert.equal(await evaluate('document.querySelector(".lighting-lab-panel output").textContent'),label);
  assert.equal(await evaluate('document.querySelectorAll("#battle-light-grade").length'),1);
  assert.equal(await evaluate('document.querySelector(".battlefield").classList.contains("map-lit")'),true);
  assert.ok(await evaluate(`(()=>{const p=document.querySelector('.battle-decoration.has-prop-art');return getComputedStyle(p,p.classList.contains('multi-cell-asset')?'::before':null).filter.includes('battle-light-grade')})()`));
  assert.equal(await evaluate('getComputedStyle(document.querySelector(".battle-token")).filter'),'none');
 }
 await evaluate('document.querySelector("[data-light-preset=\\"12\\"]").click()');
 const shadowBefore=await evaluate('document.querySelector(".battlefield").style.getPropertyValue("--sun-shadow-x")');
 await evaluate('(()=>{const scrub=document.querySelector("[data-light-time]");scrub.value=22;scrub.dispatchEvent(new Event("input"))})()');
 assert.notEqual(await evaluate('document.querySelector(".battlefield").style.getPropertyValue("--sun-shadow-x")'),shadowBefore);
 await evaluate('document.querySelector("[data-light-shadows]").click()');
 assert.equal(await evaluate('document.querySelector(".battlefield").classList.contains("map-sun-shadows")'),false);
 await evaluate('document.querySelector("[data-light-shadows]").click();document.querySelector("[data-light-enable]").click()');
 assert.equal(await evaluate('document.querySelector(".battlefield").classList.contains("map-lit")'),false);
 await evaluate('document.querySelector("[data-light-enable]").click()');
 if(scene==='goblin_warcamp'){
  assert.ok(await evaluate('document.querySelectorAll(".lighting-large-prop").length>0'));
  assert.ok(await evaluate(`(()=>{const field=document.querySelector('.battlefield'),r=field.getBoundingClientRect();return [...field.querySelectorAll('.battle-decoration')].some(p=>{const b=p.getBoundingClientRect(),art=getComputedStyle(p,'::before'),w=parseFloat(art.width)||b.width,h=parseFloat(art.height)||b.height,cx=(b.left+b.right)/2,cy=(b.top+b.bottom)/2;return (cy-h/2<r.top||cx+w/2>r.right||cx-w/2<r.left||cy+h/2>r.bottom)&&art.filter.includes('battle-light-grade')})})()`));
 }
 if(scene==='tool_shed'){
  assert.ok(await evaluate('document.querySelectorAll(".lighting-indoor-prop").length>0'));
  const indoorBefore=await evaluate(`(()=>{const p=document.querySelector('.lighting-indoor-prop');return getComputedStyle(p,p.classList.contains('multi-cell-asset')?'::before':null).filter})()`);
  await evaluate('document.querySelector("[data-light-preset=\\"12\\"]").click()');
  assert.equal(await evaluate(`(()=>{const p=document.querySelector('.lighting-indoor-prop');return getComputedStyle(p,p.classList.contains('multi-cell-asset')?'::before':null).filter})()`),indoorBefore);
 }
 await evaluate('document.querySelector("[data-light-preset=\\"42\\"]").click()');
 await writeFile(`data/browser-qa/lighting-${scene}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
}
await evaluate('window.lightingShow("goblin_captive_cart")');
const cart=await evaluate(`(()=>{const p=document.querySelector('[data-battle-terrain="cart_body"]'),s=getComputedStyle(p);return {shadow:s.boxShadow,border:s.borderTopWidth,art:s.getPropertyValue('--battle-prop')}})()`);
assert.equal(cart.shadow,'none');assert.equal(cart.border,'0px');assert.match(cart.art,/prison_wagon/);
assert.equal(await evaluate('getComputedStyle(document.querySelector("[data-battle-terrain=cart_body]")).filter'),'none');
assert.ok(await evaluate('getComputedStyle(document.querySelector("[data-battle-terrain=cart_body]"),"::before").filter.includes("battle-light-grade")'));
await writeFile('data/browser-qa/lighting-prison-cart.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate('window.lightingShow("prison_proof_e")');
assert.ok(await evaluate(`(()=>{const walls=[...document.querySelectorAll('.palisade.has-prop-art')];return walls.length>0&&walls.every(p=>getComputedStyle(p).boxShadow==='none')})()`));
await evaluate('document.querySelector("[data-light-preset=\\"12\\"]").click()');
const stableShadow=await evaluate('getComputedStyle(document.querySelector(".lighting-large-prop"),"::before").filter');
for(let index=0;index<3;index++){
 await evaluate('window.lightingRedraw()');
 assert.equal(await evaluate('getComputedStyle(document.querySelector(".lighting-large-prop"),"::before").filter'),stableShadow);
}
await wait(2100);
assert.equal(await evaluate('getComputedStyle(document.querySelector(".lighting-large-prop"),"::before").filter'),stableShadow);
await writeFile('data/browser-qa/lighting-promise-proven.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate('document.querySelector("[data-light-play]").click()');await wait(600);
assert.equal(await evaluate('document.querySelector("[data-light-play]").getAttribute("aria-pressed")'),'true');
await evaluate('document.querySelector("[data-light-close]").click()');
assert.equal(await evaluate('document.querySelectorAll(".lighting-preview-wash").length'),0);
assert.equal(await evaluate('document.querySelector(".battlefield").classList.contains("map-lit")'),true);
await evaluate('document.querySelector("[data-dev-launcher]").click()');
assert.equal(await evaluate('document.querySelector(".dev-tools-panel").open'),true);
assert.equal(await evaluate('document.querySelectorAll("[data-dev-tool=lighting]").length'),0);
await evaluate('document.querySelector("[data-dev-tool=battle]").click()');await wait(250);
await evaluate('document.querySelector("[data-lab-query]").value="pickpockets";document.querySelector("[data-lab-query]").dispatchEvent(new Event("input"))');
await evaluate('document.querySelector(".lab-mission").click()');
assert.equal(await evaluate('document.querySelector("[data-lab-radiant]").disabled'),false);
await evaluate('document.querySelector("[data-lab-radiant]").value="bear";document.querySelector("[data-lab-start]").click()');await wait(400);
assert.equal(await evaluate('window.lightRequests.at(-1).radiant_mode'),'bear');
assert.equal(await evaluate('!!document.querySelector("[data-radiant-choice]")'),true);
await call('Emulation.setDeviceMetricsOverride',{width:430,height:932,deviceScaleFactor:1,mobile:true});
await evaluate('window.lightingShow("tool_shed")');
assert.ok(await evaluate('document.querySelector(".lighting-lab-panel").getBoundingClientRect().right<=innerWidth'));
await evaluate('document.querySelector("[data-light-close]").click();document.querySelector("[data-lab-lighting]").click()');
assert.equal(await evaluate('document.querySelector(".lighting-lab-panel").hidden'),false);
await evaluate('window.lightingRegular()');
assert.equal(await evaluate('document.querySelector(".lighting-lab-panel").hidden'),true);
assert.equal(await evaluate('document.querySelector(".battlefield").classList.contains("map-lit")'),true);
assert.equal(await evaluate('document.querySelectorAll("[data-lab-lighting]").length'),0);
assert.deepEqual(errors,[]);
console.log('Day/dusk/night/dawn, two real maps, restore/close, developer hub, forced radiant popup, mobile width passed.');
await call('Browser.close');ws.close();
