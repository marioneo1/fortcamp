// Isolated Druid UI regression fixture; no live API or player saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<120;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(200)}
assert.equal(await evaluate('Boolean(window.mageReady)'),true);


const cards=[];
for(const fixture of ['druid_inspect','druid_hover']){
 await evaluate(`window.mageShow('${fixture}')`);await wait(250);
 const p=await evaluate(`(()=>{const el=document.querySelector('.battle-token.enemy'),r=el.getBoundingClientRect();return {x:r.x+r.width*.8,y:r.y+r.height*.8}})()`);
 await call('Input.dispatchMouseEvent',{type:'mouseMoved',...p,buttons:0});await wait(50);
 // Use the unit itself, not an individual attached status badge, for the summary.
 await evaluate(`(()=>{const el=document.querySelector('.battle-token.enemy');el.dispatchEvent(new MouseEvent('mousemove',{clientX:${p.x},clientY:${p.y},bubbles:true}))})()`);
 await evaluate(`new Promise(requestAnimationFrame)`);
 const card=await evaluate(`(()=>{const el=document.getElementById('combat-unit-inspect'),r=el.getBoundingClientRect();return {width:r.width,height:r.height,hidden:el.hidden,text:el.textContent}})()`);
 assert.equal(card.hidden,false);assert.ok(card.width>card.height*1.8);assert.match(card.text,/Right-click to inspect stats and effects/);cards.push(card);
}
assert.equal(cards[0].width,cards[1].width);assert.equal(cards[0].height,cards[1].height);
const pointerWork=await evaluate(`(async()=>{
 const tip=document.getElementById('combat-unit-inspect'),token=document.querySelector('.battle-token.enemy'),original=token.getBoundingClientRect.bind(token),r=original(),first=tip.firstElementChild;
 const width=Object.getOwnPropertyDescriptor(HTMLElement.prototype,'offsetWidth').get,height=Object.getOwnPropertyDescriptor(HTMLElement.prototype,'offsetHeight').get;
 let reads=0,rects=0,mutations=0;
 Object.defineProperty(tip,'offsetWidth',{configurable:true,get(){reads++;return width.call(this)}});Object.defineProperty(tip,'offsetHeight',{configurable:true,get(){reads++;return height.call(this)}});
 token.getBoundingClientRect=()=>{rects++;return original()};
 const observer=new MutationObserver(records=>mutations+=records.length);observer.observe(tip,{childList:true,subtree:true});
 for(let i=0;i<100;i++)token.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:r.right-5+(i%2),clientY:r.bottom-5}));
 await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);
 observer.disconnect();delete tip.offsetWidth;delete tip.offsetHeight;token.getBoundingClientRect=original;
 return {reads,rects,mutations,retained:first===tip.firstElementChild};
})()`);
assert.deepEqual(pointerWork,{reads:0,rects:0,mutations:0,retained:true});
await evaluate(`(async()=>{const tip=document.getElementById('combat-unit-inspect'),token=document.querySelector('.battle-token.enemy');tip.hidden=true;token.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:800,clientY:400}));token.dispatchEvent(new MouseEvent('mouseleave',{relatedTarget:document.body}));await new Promise(requestAnimationFrame)})()`);
assert.equal(await evaluate(`document.getElementById('combat-unit-inspect').hidden`),true,'leaving before the scheduled frame must cancel display');
// A new playback status snapshot still invalidates the cached explanation.
await evaluate(`(async()=>{const token=document.querySelector('.battle-token.enemy');token.presentationStatuses=[{id:'barrier',amount:13,turns:2}];token.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:800,clientY:400}));await new Promise(requestAnimationFrame)})()`);
assert.match(await evaluate(`document.getElementById('combat-unit-inspect').textContent`),/Barrier/);
assert.doesNotMatch(await evaluate(`document.querySelector('#combat-unit-inspect .inspect-effects').textContent`),/Poison/);
await evaluate(`window.mageShow('druid_hover')`);await wait(100);
await evaluate(`(async()=>{const token=document.querySelector('.battle-token.enemy');delete token.presentationStatuses;token.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:800,clientY:400}));await new Promise(requestAnimationFrame)})()`);
const retainedAfterRebind=await evaluate(`(async()=>{const tip=document.getElementById('combat-unit-inspect'),first=tip.firstElementChild;document.querySelector('[data-combat-mode="move"]').click();document.querySelector('.battle-token.enemy').dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:800,clientY:400}));await new Promise(requestAnimationFrame);return first===tip.firstElementChild})()`);
assert.equal(retainedAfterRebind,true,'unchanged control redraw must retain hover content');
const effects=await evaluate(`(()=>{const el=document.querySelector('#combat-unit-inspect .inspect-effects'),r=el.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,scrollHeight:el.scrollHeight,clientHeight:el.clientHeight}})()`);
assert.ok(effects.scrollHeight<=effects.clientHeight,'three summary rows and more hint fit without scrolling');
assert.equal(await evaluate(`document.querySelectorAll('#combat-unit-inspect .compact-effect').length`),3);
assert.match(await evaluate(`document.querySelector('#combat-unit-inspect .inspect-more').textContent`),/\+11 more effects/);
assert.equal(await evaluate(`getComputedStyle(document.querySelector('#combat-unit-inspect .inspect-effects')).overflowY`),'hidden');
assert.equal(await evaluate(`getComputedStyle(document.getElementById('combat-unit-inspect')).pointerEvents`),'none');
await writeFile('staging-ui/druid-v1/compact-hover.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:5,y:5,buttons:0});await wait(180);
assert.equal(await evaluate(`document.getElementById('combat-unit-inspect').hidden`),true);
await evaluate(`window.mageShow('druid_inspect')`);await wait(100);
const sweep=await evaluate(`(async()=>{
 const tokens=[...document.querySelectorAll('.battle-token[data-battle-unit]')].slice(0,3),tip=document.getElementById('combat-unit-inspect');
 if(tokens.length!==3)throw Error('Need three units for sweep');
 const pause=ms=>new Promise(r=>setTimeout(r,ms)),frame=()=>new Promise(requestAnimationFrame);
 const hover=i=>tokens[i].dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:800+i,clientY:400}));
 hover(0);await frame();const first=tip.firstElementChild;
 hover(1);const hiddenWhileSwitching=tip.hidden;hover(2);await frame();
 const latest=tip.dataset.unitId===tokens[2].dataset.battleUnit&&!tip.hidden;
 const plainStats=!tip.querySelector('.inspect-stat-help,.inspect-stat,[tabindex],abbr[title]');
 hover(0);await frame();const reused=tip.firstElementChild===first;
 hover(1);tokens[1].dispatchEvent(new MouseEvent('mouseleave',{relatedTarget:document.body}));await pause(150);
 const cancelled=tip.hidden;
 return {hiddenWhileSwitching,latest,plainStats,reused,cancelled};
})()`);
assert.deepEqual(sweep,{hiddenWhileSwitching:false,latest:true,plainStats:true,reused:true,cancelled:true});
const rightPoint=await evaluate(`(()=>{const token=document.querySelectorAll('.battle-token[data-battle-unit]')[2],r=token.getBoundingClientRect();token.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:r.x+r.width*.8,clientY:r.y+r.height*.8}));return {x:r.x+r.width*.8,y:r.y+r.height*.8}})()`);
await call('Input.dispatchMouseEvent',{type:'mousePressed',...rightPoint,button:'right',buttons:2,clickCount:1});
await call('Input.dispatchMouseEvent',{type:'mouseReleased',...rightPoint,button:'right',buttons:0,clickCount:1});
assert.equal(await evaluate(`Boolean(document.getElementById('combat-unit-window'))`),true);
assert.equal(await evaluate(`(()=>{const stat=document.querySelector('#combat-unit-window .inspect-stat');stat.dispatchEvent(new PointerEvent('pointermove',{bubbles:true}));return Boolean(document.getElementById('combat-stat-tooltip')?.textContent)})()`),true,'pinned Unit details retains stat calculation tooltips');
await wait(150);assert.equal(await evaluate(`document.getElementById('combat-unit-inspect').hidden`),true);
await evaluate(`document.getElementById('combat-unit-window').remove();document.getElementById('combat-stat-tooltip')?.remove()`);
const commands=await evaluate(`(()=>{const buttons=[...document.querySelectorAll('.battle-primary-panel .combat-actions>button')],rects=buttons.map(b=>b.getBoundingClientRect());return {count:buttons.length,squares:rects.every(r=>r.width===88&&r.height===88),rows:rects[0].top===rects[2].top&&rects[3].top>rects[0].top,icons:buttons.every(b=>getComputedStyle(b.querySelector('.combat-action-art')).width==='72px')}})()`);
assert.deepEqual(commands,{count:6,squares:true,rows:true,icons:true});
await writeFile('staging-ui/druid-v1/command-tiles.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
assert.deepEqual(errors,[]);console.log('PASS fixed hover, zero repeated layout reads, three-unit sweep without timer, plain summary stats, cached return, exit cancellation, immediate right-click and six square command tiles.');ws.close();
