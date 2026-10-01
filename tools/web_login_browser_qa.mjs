const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const check=async(expression,label)=>{if(!await evaluate(expression))throw Error(label);console.log('PASS '+label)};
try{
await call('Runtime.enable');await call('Page.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1100,height:900,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/web-login/preview.html'});await new Promise(r=>setTimeout(r,1800));
await check(`document.querySelectorAll('[data-web-guild]').length===2`,'actual app startup presents server picker');
await check(`document.querySelector('#web-login').textContent.includes('DEVELOPMENT')&&!document.querySelector('#web-login guild')`,'development is labelled and server names escaped');
await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
await check(`document.documentElement.scrollWidth<=innerWidth`,'narrow server picker has no horizontal overflow');
await evaluate(`document.querySelector('[data-web-guild="20"]').click()`);await new Promise(r=>setTimeout(r,800));
await check(`!document.querySelector('#game').classList.contains('hidden')&&document.querySelector('#identity-label').textContent.includes('server 20')`,'server selection opens real game under selected guild');
await check(`document.querySelector('#web-change-server')&&document.querySelector('.web-dev-badge')`,'web account controls and persistent DEV badge present');
await check(`JSON.parse(localStorage.getItem('fortcamp-web:qa-web-dev')).identity.guild_id==='20'`,'saved session belongs to selected server');
await check(`window.webRequests.some(r=>r.path==='/api/state'&&r.headers.Authorization==='Bearer fixture-20')`,'game requests use selected server session');
await check(`window.unexpectedWebApi.length===0`,'startup makes no unexpected API calls');
await check(`document.documentElement.scrollWidth<=innerWidth`,'web game header fits narrow screen');
if(errors.length)throw Error(errors.join('\n'));console.log('PASS no login or game startup script errors');
}finally{ws.close()}
