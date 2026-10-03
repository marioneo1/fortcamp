// Actual combat renderer with isolated fixture state. Requires preview :8766
// and a dedicated headless Chrome CDP session :9229; never accesses live saves.
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
const commandCamps=process.argv.includes('--command-camps');
const beginnerSites=process.argv.includes('--beginner-sites');
const sizeAudit=process.argv.includes('--size-audit');
const activitySites=process.argv.includes('--activity-sites');
const roadSites=process.argv.includes('--road-sites');
const out=roadSites?'staging-terrain/road-locations-v1':activitySites?'staging-terrain/environment-ground-v1/in-game':sizeAudit?'staging-terrain/prop-size-audit/in-game':beginnerSites?'staging-terrain/beginner-locations-v1':commandCamps?'staging-terrain/command-locations-v1':'staging-terrain/location-rollout-v1';await mkdir(out,{recursive:true});
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);
let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
try{
 await call('Runtime.enable');
 await call('Emulation.setDeviceMetricsOverride',{width:1600,height:1100,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-terrain/overhead-props-v2/encounter-preview.html'});
 for(let i=0;i<100;i++){if(await evaluate('Boolean(window.propCoverageReady)'))break;await new Promise(r=>setTimeout(r,100))}
 assert.equal(await evaluate('Boolean(window.propCoverageReady)'),true);
 const seen=new Set();let maps=0;
 for(const mid of roadSites?['highway_ambush']:activitySites?['herbs_wall','prison_proof_d']:sizeAudit?[]:beginnerSites?['rats_storehouse','wolves_fence','herbs_wall','goblin_pickpockets','ruined_well','supply_watch','prison_proof_d']:
                 commandCamps?['prison_rival_d','prison_former_e','prison_former_c','goblin_chieftain','hobgoblin_vanguard']:
                              ['chapel_patrol','roadside_toll','road_cache','goblin_armory','salvage_court']){
  for(let variant=1;variant<=4;variant++){
   const key=`${mid}_v${variant}`;
   await evaluate(`window.propEncounter('${key}')`);await new Promise(r=>setTimeout(r,120));
   if(activitySites||roadSites){
    const backgrounds=await evaluate("Array.from(document.querySelectorAll('.battle-cell[style*=\"--authored-ground\"]')).map(e=>getComputedStyle(e).backgroundImage)");
    assert.ok(backgrounds.length>=(roadSites?40:60),'Authored ground reached the actual renderer');
    assert.ok(backgrounds.every(v=>v.includes('environment-ground-v1/')));
    const urls=[...new Set(backgrounds.flatMap(v=>Array.from(v.matchAll(/url\([\"']?([^\"'\)]+)/g),m=>m[1])))];
    for(const url of urls){assert.equal((await fetch(new URL(url,'http://127.0.0.1:8766'))).status,200);seen.add(url)}
    await evaluate(`Promise.all(${JSON.stringify(urls)}.map(url=>new Promise((resolve,reject)=>{const image=new Image();image.onload=resolve;image.onerror=reject;image.src=url})))`);
   }
   const props=await evaluate("Array.from(document.querySelectorAll('.has-prop-art')).map(e=>e.style.getPropertyValue('--battle-prop'))");
   assert.ok(props.length>=(mid==='goblin_pickpockets'?6:10),key);
   for(const value of props){const path=value.match(/url\(['\"]?([^'\")]+)/)?.[1];if(path&&!seen.has(path)){assert.equal((await fetch('http://127.0.0.1:8766'+path)).status,200,path);seen.add(path)}}
   const clip=await evaluate("(()=>{const r=document.querySelector('.battle-cell').parentElement.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1.5}})()");
   await writeFile(`${out}/${key}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip})).data,'base64'));
   maps++;
  }
 }
 if(sizeAudit){
  for(const key of ['captive_cart','ruined_well_v1','hobgoblin_vanguard_v3','herbs_wall_v1','herbs_wall_v2','herbs_wall_v3','herbs_wall_v4']){
   await evaluate(`window.propEncounter('${key}')`);await new Promise(r=>setTimeout(r,150));
   const urls=await evaluate("Array.from(new Set(Array.from(document.querySelectorAll('.battlefield *')).flatMap(e=>[e.style.getPropertyValue('--battle-prop'),getComputedStyle(e).backgroundImage,getComputedStyle(e,'::before').backgroundImage]).flatMap(v=>Array.from(v.matchAll(/url\\([\"']?([^\"'\\)]+)/g),m=>m[1]))))");
   for(const path of urls){if(!seen.has(path)){const url=new URL(path,'http://127.0.0.1:8766');assert.equal((await fetch(url)).status,200,url.href);seen.add(path)}}
   await evaluate(`Promise.all(${JSON.stringify(urls)}.map(url=>new Promise((resolve,reject)=>{const img=new Image();img.onload=resolve;img.onerror=()=>reject(Error('Image failed: '+url));img.src=url})))`);
   await new Promise(r=>setTimeout(r,400));
   const measured=await evaluate(`(()=>{const cell=document.querySelector('.battle-cell').getBoundingClientRect();return {cellWidth:cell.width,props:Array.from(document.querySelectorAll('[data-battle-terrain]')).map(e=>({id:e.dataset.battleTerrain,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,artWidth:getComputedStyle(e,'::before').width}))}})()`);
   if(key==='captive_cart'){
    const cart=measured.props.find(p=>p.id==='cart_body');assert.ok(cart);assert.ok(Math.abs(cart.width/measured.cellWidth-2)<.05,'Prison cart must really span two tile columns');
   }
   if(key==='ruined_well_v1'){
    const well=measured.props.find(p=>p.id.includes('village_well'));assert.ok(well);assert.ok(Math.abs(well.width/measured.cellWidth-2)<.05,'Well must really span two tile columns');
   }
   const clip=await evaluate("(()=>{const r=document.querySelector('.battle-cell').parentElement.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1.5}})()");
   await writeFile(`${out}/${key}.png`,Buffer.from((await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip})).data,'base64'));
   await writeFile(`${out}/${key}.json`,JSON.stringify(measured,null,2));maps++;
  }
 }
 assert.deepEqual(errors,[]);
 console.log(`PASS: ${maps} authored mission layouts render; ${seen.size} asset URLs load; no runtime exceptions.`);
}finally{
 // Chrome may close its socket before acknowledging Browser.close.
 const disconnected=new Promise(resolve=>ws.addEventListener('close',resolve,{once:true}));
 await Promise.race([call('Browser.close'),disconnected]);ws.close();
}
