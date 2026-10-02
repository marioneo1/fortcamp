// Isolated actual-UI fixture; requires preview server 8766 and QA Chrome CDP 9229.
import assert from 'node:assert/strict';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const result=await call('Runtime.evaluate',{expression,returnByValue:true});if(result.exceptionDetails)throw Error(result.exceptionDetails.text);return result.result.value};
await call('Runtime.enable');
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/equipment-icons-v1/battle-preview.html'});
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.gearReady)'))break;await new Promise(r=>setTimeout(r,100))}
assert.equal(await evaluate('document.querySelector("[data-combat-mode=attack]").textContent.trim()'),'A Capture');
assert.equal(await evaluate('document.querySelector("[data-combat-mode=subdue]")===null'),true);
await evaluate('document.querySelector("[data-combat-mode=attack]").click()');
assert.equal(await evaluate('document.querySelector("[data-battle-unit=gob_guard]").title.includes("capture chance")'),true);
await evaluate('window.gearCreator()');
assert.deepEqual(await evaluate('[...document.querySelector("#cc-trait").options].map(o=>o.textContent)'),['Fighter','Ranger','Mage','Captor','Medic','Engineer']);
for(const [role,training,weapon] of [['fighter','combat','Chipped Sword'],['mage','magic','Cracked Wand'],['captor','combat','Frayed Capture Net'],['medic','medicine','Cracked Wand'],['engineer','building','Worn Mallet']]){
 await evaluate(`(()=>{const role=document.querySelector('#cc-trait');role.value=${JSON.stringify(role)};role.dispatchEvent(new Event('change'))})()`);
 assert.equal(await evaluate('document.querySelector("#cc-perk").value'),training);
 assert.equal(await evaluate('document.querySelector("#cc-perk").disabled'),true);
 assert.equal(await evaluate(`document.querySelector('#creator-training-info').textContent.includes(${JSON.stringify(weapon)})`),true);
}
await call('Emulation.setDeviceMetricsOverride',{width:430,height:1000,deviceScaleFactor:1,mobile:false});
assert.equal(await evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),true);
assert.deepEqual(errors,[]);
console.log('PASS: capture action and chance, no duplicate button, six roles, matching kits/training, mobile layout');
await call('Browser.close');
