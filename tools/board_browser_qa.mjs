import {writeFileSync} from 'node:fs';
const list=await (await fetch('http://127.0.0.1:9229/json')).json();const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let sequence=0;const pending=new Map(),errors=[];ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text+' '+JSON.stringify(m.params.exceptionDetails.exception))};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
await call('Runtime.enable');await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mission-board-v1/board-preview.html'});
await new Promise(r=>setTimeout(r,1800));
console.log('Ready',await evaluate('window.previewReady'), 'errors',errors);
console.log('Layout',await evaluate(`({cards:document.querySelectorAll('.guild-contract').length,icons:[...document.images].filter(i=>i.src.includes('mission-board-v1')).every(i=>i.complete&&i.naturalWidth>0),overflow:document.documentElement.scrollWidth>innerWidth})`));
const normal=await call('Page.captureScreenshot',{format:'png'});writeFileSync('staging-ui/mission-board-v1/board-desktop.png',Buffer.from(normal.data,'base64'));
await evaluate(`window.previewEvent('goblin_warhost')`);await new Promise(r=>setTimeout(r,500));const event=await call('Page.captureScreenshot',{format:'png'});writeFileSync('staging-ui/mission-board-v1/board-goblin.png',Buffer.from(event.data,'base64'));

const check=async(expression,label)=>{if(!await evaluate(expression))throw Error('Failed: '+label);console.log('PASS '+label)};
await check(`!document.querySelector('#mission-grid').textContent.includes('HIDDEN SECRET NAME')`,'locked rank hides mission names');
await check(`document.querySelector('.mission-stack').textContent.charCodeAt(0)===215&&document.querySelector('.mission-stack').textContent.includes('2')`,'duplicates stack with readable copy count');
await evaluate(`window.originalCard=document.querySelector('[data-mission-action]');originalCard.focus();window.previewRefresh()`);
await check(`window.originalCard===document.activeElement`,'polling preserves card identity and keyboard focus');
await evaluate(`window.rankE=document.querySelector('[data-rank-board="E"]');rankE.open=false`);await new Promise(r=>setTimeout(r,80));await evaluate('window.previewRefresh()');
await check(`document.querySelector('[data-rank-board="E"]')===rankE&&!rankE.open`,'collapsed rank stays collapsed through polling');
await evaluate(`document.querySelector('#board-search').value='hedgerows';document.querySelector('#board-search').dispatchEvent(new Event('input'));document.querySelector('#board-search').focus();window.previewRefresh()`);
await check(`document.activeElement.id==='board-search'&&[...document.querySelectorAll('#mission-grid .guild-contract h3')].every(e=>e.closest('article').textContent.toLowerCase().includes('hedgerows'))`,'search filters and preserves input focus');
await evaluate(`document.querySelector('#board-reset').click();window.previewDropdown=document.querySelector('#board-form');previewDropdown.focus();window.previewRefresh()`);
await check(`document.activeElement===previewDropdown`,'form control retains focus during polling');
await evaluate(`document.querySelector('[data-contract-view="private"]').click()`);
await check(`!document.querySelector('#tab-private').classList.contains('hidden')&&document.querySelectorAll('#private-contract-grid .guild-contract').length===2`,'private navigation and shared cards');
await evaluate(`document.querySelector('#private-contract-grid [data-mission-action]').click()`);await check(`window.lastOpened==='private-1'`,'private inspect button opens correct contract');
await evaluate(`document.querySelector('#tab-private [data-contract-view="missions"]').click();document.querySelector('#mission-grid [data-mission-action]').click()`);await check(`String(window.lastOpened).startsWith('quest-')`,'public inspect button opens correct contract');
await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
await check(`[...document.querySelectorAll('.guild-event-halo,.guild-event-particles i')].every(e=>getComputedStyle(e).animationName==='none')`,'reduced motion disables decorative effects');
await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
await evaluate(`window.scrollTo(0,0);window.previewEvent('starfall_omen')`);await new Promise(r=>setTimeout(r,200));
await check(`document.documentElement.scrollWidth<=innerWidth`,'narrow board has no horizontal overflow');
await check(`getComputedStyle(document.querySelector('.rank-mission-grid')).gridTemplateColumns.split(' ').length===1`,'narrow board uses one readable column');
const mobile=await call('Page.captureScreenshot',{format:'png'});writeFileSync('staging-ui/mission-board-v1/board-mobile.png',Buffer.from(mobile.data,'base64'));
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
await evaluate(`document.querySelector('[data-rank-board="E"]').open=true;document.querySelector('[data-rank-board="E"]').scrollIntoView({block:'start'});window.previewRefresh()`);
const cards=await call('Page.captureScreenshot',{format:'png'});writeFileSync('staging-ui/mission-board-v1/board-contracts.png',Buffer.from(cards.data,'base64'));

await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'no-preference'}]});
await evaluate(`window.vfxHash=()=>window.previewBackdrop.pixelSignature();window.waitForParticles=async()=>{for(let i=0;i<100;i++){const c=document.querySelector('.board-regional-backdrop');if(!c.hidden&&c.dataset.renderer==='pixi')return true;await new Promise(r=>setTimeout(r,50))}return false}`);
for(const id of ['goblin_warhost','ashen_procession','arcane_convergence','great_beast_tide','starfall_omen']){
  await evaluate(`window.previewEvent('${id}')`);await check(`waitForParticles()`,'Pixi renderer ready for '+id);const before=await evaluate('vfxHash()');await new Promise(r=>setTimeout(r,220));await check(`vfxHash()!==${before}`,'background visibly animates for '+id);
  await check(`previewBackdrop.diagnostics().particles>0&&previewBackdrop.diagnostics().particles<=80`,'bounded live emitter particles for '+id);
}
await check(`performance.getEntriesByType('resource').filter(e=>e.name.includes('/vfx/environment-v1/')).length>=18`,'regional painted textures are requested lazily across event previews');
await check(`(async()=>{const {vfxTextures}=await import('/frontend/src/vfx-textures.js');const {createParticlePreset,PARTICLE_PRESETS}=await import('/frontend/src/particle-presets.js');return PARTICLE_PRESETS.filter(n=>!['rain','snow'].includes(n)).flatMap(n=>createParticlePreset(n,1440,1100)).flatMap(p=>p.config.behaviors.find(b=>b.type==='textureRandom').config.textures).every(name=>vfxTextures.get(name)?.naturalWidth>0)})()`,'every emitter texture loads successfully');
for(const weather of ['rain','snow']){
  await evaluate(`previewWeather('${weather}')`);await check(`waitForParticles()`,'weather preset ready: '+weather);const before=await evaluate('vfxHash()');await new Promise(r=>setTimeout(r,220));await check(`vfxHash()!==${before}`,'weather preset animates: '+weather);
  await check(`previewBackdrop.diagnostics().particles>0&&previewBackdrop.diagnostics().particles<=80`,'bounded weather particles: '+weather);
}
await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
const still=await evaluate('vfxHash()');await new Promise(r=>setTimeout(r,220));await check(`vfxHash()===${still}`,'reduced motion freezes full-board backdrop');
await evaluate(`window.previewEvent('general')`);await check(`document.querySelector('.board-regional-backdrop').hidden`,'ordinary board has no event backdrop');
await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'no-preference'}]});
await evaluate(`window.scrollTo(0,0);window.previewEvent('great_beast_tide')`);await new Promise(r=>setTimeout(r,300));
const backdrop=await call('Page.captureScreenshot',{format:'png'});writeFileSync('staging-ui/mission-board-v1/board-beast-background.png',Buffer.from(backdrop.data,'base64'));
if(errors.length)throw Error(JSON.stringify(errors));console.log('PASS no script errors');
ws.close();

