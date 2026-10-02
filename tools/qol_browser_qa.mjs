import assert from 'node:assert/strict';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
await call('Runtime.enable');await call('Page.enable');
await call('Emulation.setFocusEmulationEnabled',{enabled:true});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/combat-relationships/preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.relationshipReady)'))break;await new Promise(r=>setTimeout(r,100))}
for(const [width,height] of [[1440,1000],[1280,720],[800,700]]){
 await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await evaluate('window.nativePreview()');await new Promise(r=>setTimeout(r,150));
 const dimensions=await evaluate(`(()=>{const v=document.querySelector('#battle-viewport'),f=v.querySelector('.battlefield'),r=f.getBoundingClientRect(),b=v.getBoundingClientRect();return {width:r.width,height:r.height,availableWidth:v.clientWidth,availableHeight:v.clientHeight,bottom:b.bottom,screen:innerHeight}})()`);
 assert.ok(dimensions.width<=dimensions.availableWidth+1,JSON.stringify(dimensions));assert.ok(dimensions.height<=dimensions.availableHeight+1,JSON.stringify(dimensions));assert.ok(dimensions.bottom<=height,JSON.stringify(dimensions));
 console.log('fit map',width,height,dimensions);
 const zoomed=await evaluate("(()=>{document.querySelector('[data-battle-zoom=in]').click();return document.querySelector('.battlefield').getBoundingClientRect().width})()");
 assert.ok(zoomed>dimensions.width,'Zoom in must enlarge the fitted map');
 await evaluate("document.querySelector('[data-battle-fit]').click()");
}
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await new Promise(r=>setTimeout(r,150));
await evaluate('window.relationshipPreview()');
assert.equal(await evaluate("document.querySelector('[data-roster-panel=conversation] .character-record-grid')===null"),true);
await evaluate("document.querySelector('[data-roster-tab=record]').click()");assert.equal(await evaluate("!document.querySelector('[data-roster-panel=record]').classList.contains('hidden')"),true);
await evaluate("document.querySelector('[data-roster-tab=overview]').click();document.querySelector('[data-stat-help]').focus()");
const tooltip=await evaluate("(()=>{const p=document.querySelector('.floating-help'),r=p.getBoundingClientRect();return {hidden:p.hidden,text:p.textContent,left:r.left,right:r.right,bottom:r.bottom}})()");
assert.equal(tooltip.hidden,false);assert.match(tooltip.text,/Effective attribute/);assert.ok(tooltip.left>=0&&tooltip.right<=1440&&tooltip.bottom<=1000);
await evaluate("localStorage.removeItem('fortcamp:hide-equipped:fixture-guild:fixture-user:details');window.qolEquipment()");
assert.equal(await evaluate("[...document.querySelectorAll('.armory-effects')].every(d=>d.open)"),true);
assert.match(await evaluate("document.querySelector('.armory-equipped-details').textContent"),/Meridian|Grants|Uses/);
await evaluate("document.querySelector('[data-hide-details]').click();document.querySelector('[data-roster-tab=overview]').click();document.querySelector('[data-roster-tab=equipment]').click()");
assert.equal(await evaluate("[...document.querySelectorAll('.armory-effects')].every(d=>!d.open)"),true);
await evaluate("window.qolContract()");assert.equal(await evaluate("document.querySelector('#mission-modal').classList.contains('hidden')"),false);
await evaluate("document.querySelector('.reservation-heading').click()");assert.equal(await evaluate("document.querySelector('#mission-modal').classList.contains('hidden')"),false);
await evaluate("document.querySelector('#mission-modal').click()");assert.equal(await evaluate("document.querySelector('#mission-modal').classList.contains('hidden')"),true);
assert.deepEqual(errors,[]);console.log('Gear details, tooltips, record tab and outside-click dismissal passed.');
await call('Browser.close');ws.close();
