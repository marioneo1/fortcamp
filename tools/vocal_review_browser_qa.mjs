// Isolated tester QA: does not connect to the game, accounts or saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const version='approved',total=144;
const tabs=await(await fetch('http://127.0.0.1:9237/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
try{
 await call('Runtime.enable');await call('Page.enable');
 await call('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:`file:///E:/Other%20Games/Fortcamp/fortcamp-dev/frontend/public/assets/sfx/voice-tester/preview.html`});
 for(let i=0;i<50;i++){if(await evaluate('document.querySelectorAll(".card[data-name]").length>0'))break;await wait(100)}
 assert.equal(await evaluate('document.querySelectorAll(".card[data-name]").length'),total);
 // Check rendered identity and requested audio, not just the presence of files.
 const cards=await evaluate(`Array.from(document.querySelectorAll('.card[data-name]')).map(el=>({id:el.dataset.name,label:el.querySelector('strong').textContent,filename:el.querySelector('.filename').textContent}))`);
 for(const card of cards){
  const [race,gender,personality,event,variant]=card.id.split('_'),cap=s=>s[0].toUpperCase()+s.slice(1);
  assert.equal(card.label,`${cap(race)} ${gender} · ${cap(personality)} · ${cap(event)} ${variant}`,card.id);
  assert.equal(card.filename,card.id+'.wav');
 }
 for(const race of ['human','goblin'])for(const gender of ['male','female']){
  const id=`${race}_${gender}_survivor_death_3`;
  const selected=await evaluate(`(()=>{const c=clips.find(c=>c.name==='${id}');document.querySelector('[data-name="${id}"] .line button').click();return {src:player.src,file:c.file,now:$('now').textContent}})()`);
  assert.equal(new URL(selected.src).pathname.split('/').at(-1),id+'.wav');
  assert.ok(selected.src.endsWith(selected.file.replace('../','')));
  assert.ok(selected.now.includes(gender));
  await evaluate(`$('stop').click()`);
 }
 await evaluate(`$('gender').value='Female';$('gender').dispatchEvent(new Event('change'));$('race').value='Goblin';$('race').dispatchEvent(new Event('change'));$('personality').value='Opportunist';$('personality').dispatchEvent(new Event('change'));$('event').value='Attack';$('event').dispatchEvent(new Event('change'))`);
 assert.equal(await evaluate('document.querySelectorAll(".card[data-name]").length'),3);
 await evaluate(`document.querySelector('.redo').click();const n=document.querySelector('.notes');n.value='QA only: sounds too human';n.dispatchEvent(new Event('input'))`);
 assert.match(await evaluate(`$('feedback').value`),/goblin_female_opportunist_attack_1.wav: REDO — QA only/);
 await call('Page.reload');await wait(350);
 assert.equal(await evaluate(`JSON.parse(localStorage.getItem('fortcamp-vocal-review-${version}')).goblin_female_opportunist_attack_1.rating`),'redo');
 await evaluate(`$('review').value='';$('review').dispatchEvent(new Event('change'));$('gender').value='Female';$('gender').dispatchEvent(new Event('change'));$('race').value='Human';$('race').dispatchEvent(new Event('change'))`);
 assert.equal(await evaluate('document.querySelectorAll(".card[data-name]").length'),36);
 const r=await evaluate(`document.querySelector('.line button').getBoundingClientRect().toJSON()`);
 await call('Input.dispatchMouseEvent',{type:'mousePressed',x:r.x+r.width/2,y:r.y+r.height/2,button:'left',clickCount:1});
 await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:r.x+r.width/2,y:r.y+r.height/2,button:'left',clickCount:1});
 await wait(100);
 assert.equal(await evaluate('player.error'),null);
 assert.match(await evaluate(`$('now').textContent`),/Playing: Human female/);
 assert.equal(await evaluate('player.paused'),false);
 await evaluate(`$('stop').click()`);assert.equal(await evaluate('player.paused'),true);
 // Sequence can be stopped immediately without queued clips restarting.
 await evaluate(`$('sequence').click();$('stop').click()`);await wait(600);
 assert.equal(await evaluate('player.paused&&queue.length===0'),true);
 assert.equal(await evaluate(`$('now').textContent`),'Stopped');
 await evaluate(`localStorage.removeItem('fortcamp-vocal-review-${version}');ratings={};save();render()`);
 const shot=await call('Page.captureScreenshot',{format:'png'});
 await writeFile(`staging-ui/vocal-review-${version}/desktop.png`,Buffer.from(shot.data,'base64'));
 await call('Emulation.setDeviceMetricsOverride',{width:430,height:932,deviceScaleFactor:1,mobile:true});
 assert.equal(await evaluate('document.documentElement.scrollWidth<=window.innerWidth'),true);
 const mobile=await call('Page.captureScreenshot',{format:'png'});
 await writeFile(`staging-ui/vocal-review-${version}/mobile.png`,Buffer.from(mobile.data,'base64'));
 assert.deepEqual(errors,[]);
 console.log(`Tester QA passed: ${total} clips, filtering, filename feedback, rating persistence, real playback, stop/sequence, mobile width.`);
}finally{await call('Browser.close').catch(()=>{});ws.close()}
