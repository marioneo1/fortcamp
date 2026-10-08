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

const network=[];ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.method==='Network.responseReceived')network.push({url:m.params.response.url,cache:m.params.response.fromDiskCache||m.params.response.fromPrefetchCache||false,status:m.params.response.status,headers:m.params.response.headers})});
await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:false});
// Optional read-only comparison against the running dev asset server.
const asset=(process.argv.includes('--live-assets')?'http://127.0.0.1:5174':'http://127.0.0.1:8766')+'/assets/druid-v1/prowler.png';
for(let i=0;i<2;i++){
 const timing=await evaluate(`(async()=>{const start=performance.now(),img=new Image();img.src='${asset}';document.body.append(img);await img.decode();img.remove();return performance.now()-start})()`);
 console.log('Repeated live-dev image decode ms',i,Math.round(timing));await wait(50);
}
console.log('Live-dev image responses',network.filter(r=>r.url===asset).map(r=>({status:r.status,cache:r.cache,cacheControl:r.headers['Cache-Control']})));
await evaluate(`window.mageShow('druid_inspect')`);await wait(350);
const enemy=await evaluate(`(()=>{const r=document.querySelector('.battle-token.enemy').getBoundingClientRect();return {x:r.x+r.width*.8,y:r.y+r.height*.8}})()`);await right(enemy);
await evaluate(`window.mageShow('druid_hover')`);await wait(200);
await right(await point('#combat-unit-window [data-effect-id="innate_resistance"]'));
const stats=await evaluate(`(async()=>{
 const unitBody=document.querySelector('.unit-window-body'),effectBody=document.querySelector('.effect-window-body');
 const oldUnit=unitBody.firstElementChild,oldEffect=effectBody.firstElementChild;
 const times=[];for(let i=0;i<20;i++){const start=performance.now();await window.mageShow('druid_hover');times.push(performance.now()-start)}
 const start=performance.now();document.querySelector('[data-battle-popup="history"]').click();const dialog=document.getElementById('battle-popup-history');dialog.getBoundingClientRect();const history=performance.now()-start;dialog.close();
 return {renderMedianMs:times.sort((a,b)=>a-b)[10],renderMaxMs:Math.max(...times),historyMs:history,retainedUnit:oldUnit===unitBody.firstElementChild,retainedEffect:oldEffect===effectBody.firstElementChild};
})()`);
console.log('Inspector / History profile',JSON.stringify(stats));
assert.equal(stats.retainedUnit,true,'unchanged battle redraw must preserve Unit details DOM');
assert.equal(stats.retainedEffect,true,'unchanged battle redraw must preserve Effect details DOM');
assert.equal(await evaluate('window.mageSent.length'),0,'opening History must not send an API request');
await evaluate(`window.mageShow('druid_inspect')`);await wait(50);
assert.equal(await evaluate(`document.querySelectorAll('#combat-unit-window .effect-detail-card').length`),1,'changed effects must still refresh');
const heavy=await evaluate(`(async()=>{
 const b=document.getElementById('combat-unit-window')._battle,enemy=Object.values(b.units).find(u=>u.team==='enemy');
 b.width=24;b.height=24;b.log=Array.from({length:2000},(_,i)=>'Combat entry '+i+': target took damage, gained a status and moved.');
 for(let i=0;i<70;i++){const id='qa-'+i;b.units[id]={...structuredClone(enemy),id,x:8+i%14,y:6+Math.floor(i/14)}}
 const start=performance.now();document.querySelector('[data-combat-mode="move"]').click();document.querySelector('.battlefield').getBoundingClientRect();const renderMs=performance.now()-start;
 await new Promise(requestAnimationFrame);
 const historyStart=performance.now();document.querySelector('[data-battle-popup="history"]').click();document.getElementById('battle-popup-history').getBoundingClientRect();const historyMs=performance.now()-historyStart;
 document.getElementById('battle-popup-history').close();return {renderMs,historyMs,cells:document.querySelectorAll('[data-battle-cell]').length,tokens:document.querySelectorAll('.battle-token').length,historyEntries:b.log.length};
})()`);
console.log('Heavy isolated battle profile',JSON.stringify(heavy));
assert.deepEqual(errors,[]);ws.close();
