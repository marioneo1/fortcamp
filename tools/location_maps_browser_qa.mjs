// Isolated encounter previews; no requests to live saves or mission APIs.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
await call('Runtime.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/overhead-props-v2/encounter-preview.html'});
for(let i=0;i<80;i++){if(await evaluate('Boolean(window.propCoverageReady)'))break;await new Promise(r=>setTimeout(r,100))}
assert.equal(await evaluate('Boolean(window.propCoverageReady)'),true);
for(const [mid,material,prop] of [
 ['tool_shed','shed_floor','repair_workbench'],['workshop_intruders','workshop_floor','iron_anvil'],
 ['undead_bone_collectors','grave_earth','mossy_gravestone'],['bone_patrol','forest_dark','grave_cross'],
 ['timber_creek','wood_bridge_bottom','stacked_planks'],['goblin_bridge','deep_river','bound_barrels'],['goblin_armory','workshop_floor','weapon_rack'],
 ['workshop_intruders_v2','smithy_cobbles','repair_workbench'],['workshop_intruders_v3','smithy_cobbles','small_coal_forge'],
 ['goblin_armory_v1','shed_floor','weapon_rack'],['goblin_armory_v2','shed_floor','weapon_rack']]){
 await evaluate(`window.propEncounter('${mid}')`);await new Promise(r=>setTimeout(r,220));
 assert.ok(await evaluate(`document.querySelectorAll('.ground-${material}').length>0`));
 const assets=await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).map(e=>e.style.getPropertyValue('--battle-prop'))");
 assert.ok(assets.some(a=>a.includes('/'+prop+'.png')),mid);
 for(const value of assets){const path=value.match(/url\(['"]?([^'")]+)/)?.[1];assert.equal((await fetch('http://127.0.0.1:8766'+path)).status,200,path)}
 const ground=await evaluate(`getComputedStyle(document.querySelector('.ground-${material}')).backgroundImage`);
 assert.ok(ground.includes('mega-terrain-tiles')||ground.includes('bridge-v1'),mid);
 const lantern=await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).find(e=>e.style.getPropertyValue('--battle-prop').includes('camp_lantern.png'))?.style.getPropertyValue('--asset-width')");
 if(lantern)assert.ok(Math.abs(parseFloat(lantern)-100/3)<.01,lantern);
 if(mid.includes('creek')||mid==='goblin_bridge'){
  const water=await evaluate("getComputedStyle(document.querySelector('.ground-deep_river')).backgroundImage");
  assert.ok(water.includes('water_deep.png'));
  assert.equal(await evaluate("document.querySelectorAll('.battle-cell.ground-deep_river:not(.void-tile)').length"),0);
 }
 await writeFile('staging-terrain/location-props-v1/'+mid+'-in-game.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
}
assert.deepEqual(errors,[]);console.log('PASS: seven authored locations and all new workshop/armory layouts, actual terrain textures, deep-water boundaries, bridge floors and every assigned sprite loads');
await Promise.race([call('Browser.close'),new Promise(r=>setTimeout(r,1000))]);ws.close();
