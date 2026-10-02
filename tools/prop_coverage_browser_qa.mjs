// Actual UI with isolated fixture state; no live game API or saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/overhead-props-v2/encounter-preview.html'});
for(let i=0;i<80;i++){if(await evaluate('Boolean(window.propCoverageReady)'))break;await new Promise(r=>setTimeout(r,100))}
assert.equal(await evaluate('Boolean(window.propCoverageReady)'),true);
for(const [encounter,ids] of [['captive_cart',['dispatch_satchel','wagon_wheel','prison_wagon']],['investigation',['marked_farm_chart']],['defense',['spike_trap','iron_jaw_trap_spent']]]){
 await evaluate(`window.propEncounter('${encounter}')`);await new Promise(r=>setTimeout(r,200));
 const props=await evaluate(`Array.from(document.querySelectorAll('.has-prop-art')).map(el=>el.style.getPropertyValue('--battle-prop'))`);
 for(const id of ids)assert.ok(props.some(value=>value.includes('/'+id+'.png')),encounter+': '+id);
 assert.equal(await evaluate(`document.querySelectorAll('.battle-object:not(.has-prop-art)').length`),0);
 for(const value of props){const path=value.match(/url\(['"]?([^'")]+)/)?.[1];assert.equal((await fetch('http://127.0.0.1:8766'+path)).status,200,path)}
 await writeFile('staging-terrain/overhead-props-v2/'+encounter+'-installed.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
}
for(const width of [800,430]){await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});await evaluate("window.propEncounter('investigation')");assert.equal(await evaluate('document.querySelectorAll(".battle-object:not(.has-prop-art)").length'),0)}
assert.deepEqual(errors,[]);console.log('PASS: actual Captive Cart evidence/wheel/prison wagon, investigation chart, armed/spent defense traps, asset loading and narrow-screen rendering');
await call('Browser.close');ws.close();
