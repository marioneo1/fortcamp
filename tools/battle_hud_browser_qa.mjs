// Isolated floating HUD regression fixture; no live API or player saves.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs=await(await fetch('http://127.0.0.1:9229/json')).json();
const ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
await new Promise(r=>ws.onopen=r);let serial=0;const pending=new Map(),errors=[];
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){pending.get(m.id)?.(m);pending.delete(m.id)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description)};
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,m=>m.error?reject(m.error):resolve(m.result));ws.send(JSON.stringify({id,method,params}))});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
const wait=ms=>new Promise(r=>setTimeout(r,ms));
await call('Runtime.enable');await call('Page.enable');await call('Network.enable');await call('Network.setCacheDisabled',{cacheDisabled:true});await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url:'about:blank'});await wait(100);errors.length=0;
await call('Page.navigate',{url:'http://127.0.0.1:8766/staging-ui/mage-v1/preview.html'});
for(let i=0;i<120;i++){if(await evaluate('Boolean(window.mageReady)'))break;await wait(200)}
assert.equal(await evaluate('Boolean(window.mageReady)'),true);




await evaluate(`(async()=>{localStorage.removeItem('fortcamp:battle-hud:v1');localStorage.removeItem('fortcamp:placement:battle-effects');await window.mageShow('captor_ready');document.querySelector('[data-hud-edit]').click();document.querySelector('[data-hud-reset]').click();document.querySelector('[data-hud-edit]').click();document.querySelector('[data-battle-fit]').click()})()`);await wait(500);
const rect=selector=>evaluate(`document.querySelector(${JSON.stringify(selector)}).getBoundingClientRect().toJSON()`);
const root=await rect('.floating-battle'),viewport=await rect('.battle-viewport'),field=await rect('.battlefield');
assert.equal(viewport.height,root.height);assert.equal(viewport.width,root.width);
assert.ok(Math.abs(field.height-(root.height-192))<=4,'fit map reserves edge-label space');
assert.ok(Math.abs(field.width-field.height)<2,'square map preserves proportions');
for(const id of ['title','turns','actor','skills'])assert.ok(await evaluate(`Boolean(document.querySelector('[data-hud-group="${id}"]'))`),id);

assert.equal(await evaluate(`document.querySelector('.hud-skills .combat-actions').offsetHeight`),await evaluate(`document.querySelector('.hud-skills .hotbar-slots').offsetHeight`),'grids share height');
assert.equal(await evaluate(`document.querySelector('.hud-skills .battle-primary-panel').textContent.includes('Command')`),true);
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.combat-action-help')).overflowY`),'visible');
const actorHeight=await evaluate(`document.querySelector('.hud-actor-group').offsetHeight`);
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.hud-skills .hotbar-slots')).gridTemplateRows.split(' ').length`),2,'two skill rows');
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.hud-skills .ability-icon')).width`),await evaluate(`getComputedStyle(document.querySelector('.battle-primary-panel .combat-action-art')).width`),'skill artwork matches command artwork');
assert.ok(await evaluate(`document.querySelector('.hud-skills .combat-status-tray').textContent.includes('No active effects')`));
assert.ok(await evaluate(`Boolean(document.querySelector('[data-hud-group="title"] .battle-objectives'))`),'objectives grouped under title');
for(const selector of ['.hud-skills','.hud-skills .hotbar-slots','.battle-primary-panel .combat-actions']){
 assert.equal(await evaluate(`(()=>{const n=document.querySelector('${selector}');return ['auto','scroll'].includes(getComputedStyle(n).overflowX)||['auto','scroll'].includes(getComputedStyle(n).overflowY)})()`),false,selector+' has no scroll overflow');
}

const dividerGaps=await evaluate(`(()=>{const r=s=>document.querySelector(s).getBoundingClientRect(),c=[...document.querySelectorAll('.hud-skills .combat-actions>button')].map(n=>n.getBoundingClientRect()),s=[...document.querySelectorAll('.hud-skills .hotbar-slots>button')].map(n=>n.getBoundingClientRect()),bar=r('.hud-skills .combat-hotbar'),effects=r('.hud-skills .combat-status-tray');return [bar.left-Math.max(...c.map(r=>r.right)),effects.left-Math.max(...s.map(r=>r.right)),Math.min(...s.map(r=>r.left))-bar.left]})()`);
assert.ok(dividerGaps.every(g=>g>=11),'icons have breathing room around dividers');
assert.ok(await evaluate(`Boolean(document.querySelector('[data-hud-group="title"] .battle-field-toolbar'))`),'tools merged beneath objectives');
const initialSkills=await rect('.hud-skills');assert.ok(Math.abs(initialSkills.width-1215.996)<1,'exported default width');
assert.ok(Math.abs((initialSkills.left-root.left)/(root.width-initialSkills.width)-.499969)<.001,'exported centered default');
assert.ok(Math.abs(initialSkills.bottom-root.bottom)<1,'exported bottom default');
const objectiveRect=await rect('.battle-objectives'),toolRect=await rect('.battle-field-toolbar');assert.ok(toolRect.top>objectiveRect.bottom,'tools follow objectives');
// Every authored battle summary fits the fixed card at its normal font size.
const clipped=await evaluate(`(async()=>{const {summaries}=await import('/frontend/src/combat-action-summary.js'),help=document.querySelector('.hud-actor-group .combat-action-help'),original=help.textContent,bad=[];for(const [name,text] of Object.entries(summaries)){help.textContent=text;if(help.scrollHeight>help.clientHeight+1)bad.push(name)}help.textContent=original;return bad})()`);
assert.deepEqual(clipped,[],'all authored action summaries fit');
// Right-drag shifts a fitted map; further dragging clamps, and Center restores it.
const panMouse=(type,x,y,extra={})=>call('Input.dispatchMouseEvent',{type,x,y,...extra});
await panMouse('mousePressed',root.x+root.width/2,root.y+root.height/2-110,{button:'right',clickCount:1});
await panMouse('mouseMoved',root.x+root.width/2+25,root.y+root.height/2-110+25,{button:'right',buttons:2});
await panMouse('mouseReleased',root.x+root.width/2+25,root.y+root.height/2-110+25,{button:'right',clickCount:1});
const panned=await rect('.battlefield');assert.ok(panned.x>field.x+20);assert.ok(panned.y>field.y+20);
await evaluate(`document.querySelector('[data-combat-mode="move"]').click()`);const retained=await rect('.battlefield');assert.ok(Math.abs(retained.x-panned.x)<2,'camera nudge survives redraw');
await panMouse('mousePressed',root.x+root.width/2,root.y+root.height/2-110,{button:'right',clickCount:1});
await panMouse('mouseMoved',root.x+root.width/2+500,root.y+root.height/2-110+500,{button:'right',buttons:2});
await panMouse('mouseReleased',root.x+root.width/2+500,root.y+root.height/2-110+500,{button:'right',clickCount:1});
const limited=await rect('.battlefield');assert.ok(limited.x-field.x<=122&&limited.y-field.y<=122,'fitted camera cannot drag the map away');

await evaluate(`document.querySelector('[data-battle-fit]').click()`);const centered=await rect('.battlefield');assert.ok(Math.abs(centered.x-field.x)<2);assert.ok(Math.abs(centered.y-field.y)<2);
// Zoomed-in maps can be pulled far enough vertically to clear the action bar.
await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:root.x+root.width/2,y:root.y+350,deltaX:0,deltaY:-100});await wait(80);
const zoomStart=await rect('.battlefield');
await panMouse('mousePressed',root.x+root.width/2,root.y+350,{button:'right',clickCount:1});
await panMouse('mouseMoved',root.x+root.width/2,root.y+650,{button:'right',buttons:2});
await panMouse('mouseReleased',root.x+root.width/2,root.y+650,{button:'right',clickCount:1});
assert.ok((await rect('.battlefield')).y>=zoomStart.y+295,'zoomed right-drag provides vertical clearance');
await evaluate(`document.querySelector('[data-battle-fit]').click()`);
await writeFile('data/browser-qa/hud-default.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));
await evaluate(`document.querySelector('[data-hud-edit]').click()`);
const handle=await rect('[data-hud-handle="title"]'),title=await rect('[data-hud-group="title"]');
const dragX=root.x+(root.width-title.width)/2+(handle.x+25-title.x);
const mouse=(type,x,y,extra={})=>call('Input.dispatchMouseEvent',{type,x,y,...extra});
await mouse('mousePressed',handle.x+25,handle.y+8,{button:'left',clickCount:1});
await mouse('mouseMoved',dragX,root.y+280,{button:'left',buttons:1});
await wait(100);
assert.ok(await evaluate(`document.querySelectorAll('.hud-guides i').length>0`),'alignment guides visible');
await mouse('mouseReleased',dragX,root.y+280,{button:'left',clickCount:1});
const moved=await rect('[data-hud-group="title"]');
assert.ok(Math.abs(moved.x-root.x-(root.width-title.width)/2)<2,'center snapping');
assert.ok(await evaluate(`JSON.parse(localStorage.getItem('fortcamp:battle-hud:v1')).title.y>0`));
await evaluate(`(async()=>{document.querySelector('[data-hud-edit]').click();await window.mageShow('captor_ready')})()`);await wait(100);
const restored=await rect('[data-hud-group="title"]');assert.ok(Math.abs(moved.x-restored.x)<2);assert.ok(Math.abs(moved.y-restored.y)<12);

// The CSS resize grip keeps icon sizes, persists width and never sends a combat command.
await evaluate(`document.querySelector('[data-hud-edit]').click()`);
const skills=await rect('[data-hud-group="skills"]');
await mouse('mousePressed',skills.right-3,skills.bottom-3,{button:'left',clickCount:1});
await mouse('mouseMoved',skills.right-53,skills.bottom-3,{button:'left',buttons:1});
await mouse('mouseReleased',skills.right-53,skills.bottom-3,{button:'left',clickCount:1});
await wait(100);
assert.ok((await rect('[data-hud-group="skills"]')).width<skills.width,'skills resize works');
assert.ok(await evaluate(`JSON.parse(localStorage.getItem('fortcamp:battle-hud:v1')).skills.width>0`),'width saved');
await evaluate(`document.querySelector('[data-hud-reset]').click();document.querySelector('[data-hud-edit]').click();window.hudToken=document.querySelector('[data-battle-unit]')`);

// Inject presentation-only effects into the isolated current actor, then redraw via a normal mode switch.
await evaluate(`window.mageInspect().actor.statuses=['burn','poison','bleed','wet','blind','slow','fear','barrier'].map(id=>({id,turns:2,stacks:2}));document.querySelector('[data-combat-mode="attack"]').click()`);
assert.equal(await evaluate(`document.querySelector('[data-all-effects]').textContent`),'All effects');
const badgeRects=await evaluate(`Array.from(document.querySelectorAll('.status-tray-icons .status-badge')).map(n=>n.getBoundingClientRect().toJSON())`);
assert.ok(badgeRects[1].left>badgeRects[0].left&&badgeRects[1].top===badgeRects[0].top,'effects fill across first');
assert.ok(badgeRects.at(-1).top>badgeRects[0].top,'effects wrap into a second row');
await evaluate(`(()=>{const a=window.mageInspect().actor,base=a.skills[0];while(a.skills.length<10)a.skills.push({...base,id:'qa:skill:'+a.skills.length,name:'Extra skill'});document.querySelector('[data-combat-mode="attack"]').click()})()`);
assert.equal(await evaluate(`document.querySelectorAll('.hud-skills [data-hotbar-slot]').length`),10);
const lastSkill=await rect('.hud-skills [data-hotbar-slot]:last-child'),skillBounds=await rect('.hud-skills');
assert.ok(lastSkill.bottom+28<=skillBounds.bottom,'all ten skills and labels fit without scrolling');
assert.equal(await evaluate(`getComputedStyle(document.querySelector('.battlefield')).overflow`),'visible','edge HP labels are not clipped by battlefield');

assert.equal(await evaluate(`window.hudToken===document.querySelector('[data-battle-unit]')`),true,'tokens retained across HUD redraw');
await evaluate(`document.querySelector('[data-all-effects]').click()`);
assert.equal(await evaluate(`document.querySelectorAll('.hud-effects-popup [data-effect-id]').length`),8);
await evaluate(`document.querySelector('[data-all-effects]').click()`);assert.equal(await evaluate(`document.querySelectorAll('.hud-effects-popup').length`),1);
await wait(100);const popup=await rect('.hud-effects-popup header');
await mouse('mousePressed',popup.x+50,popup.y+15,{button:'left',clickCount:1});
await mouse('mouseMoved',popup.x+120,popup.y+80,{button:'left',buttons:1});
await mouse('mouseReleased',popup.x+120,popup.y+80,{button:'left',clickCount:1});
assert.ok(await evaluate(`Boolean(localStorage.getItem('fortcamp:placement:battle-effects'))`));
const closeEffects=await rect('[data-close-effects]');
await mouse('mousePressed',closeEffects.x+19,closeEffects.y+19,{button:'left',clickCount:1});
await mouse('mouseReleased',closeEffects.x+19,closeEffects.y+19,{button:'left',clickCount:1});
assert.equal(await evaluate(`document.querySelectorAll('.hud-effects-popup').length`),0,'real pointer click closes dragged effects window');
await evaluate(`document.querySelector('[data-hud-edit]').click();document.querySelector('[data-hud-reset]').click();document.querySelector('[data-hud-edit]').click()`);
assert.deepEqual(await evaluate(`JSON.parse(localStorage.getItem('fortcamp:battle-hud:v1'))`),{});
await evaluate(`document.querySelector('[data-battle-fit]').click()`);await wait(100);
await mouse('mouseMoved',10,300);await wait(120);
await writeFile('data/browser-qa/hud-effects.png',Buffer.from((await call('Page.captureScreenshot',{format:'png'})).data,'base64'));

await evaluate(`window.mageShow('hud_crowd')`);await wait(300);
assert.equal(await evaluate(`document.querySelectorAll('.hud-turn-order .turn-chip:not([hidden])').length`),10);
assert.match(await evaluate(`document.querySelector('.turn-overflow').textContent`),/\+3 more/);
assert.equal(await evaluate(`document.querySelector('.turn-overflow').tagName`),'SPAN');
await evaluate(`document.querySelector('.hud-turn-order').click()`);await wait(100);
assert.equal(await evaluate(`document.querySelectorAll('.hud-turns-content .turn-chip').length`),13);
const th=await rect('.hud-turns-popup header');
await mouse('mousePressed',th.x+50,th.y+15,{button:'left',clickCount:1});await mouse('mouseMoved',th.x+90,th.y+65,{button:'left',buttons:1});await mouse('mouseReleased',th.x+90,th.y+65,{button:'left',clickCount:1});
assert.ok(await evaluate(`Boolean(localStorage.getItem('fortcamp:placement:battle-turn-order'))`));
await evaluate(`window.mageShow('captor_ready')`);await wait(150);assert.equal(await evaluate(`document.querySelectorAll('.hud-turns-content .turn-chip').length`),2,'open full order updates as units leave');
const closeTurns=await rect('[data-close-turns]');
await mouse('mousePressed',closeTurns.x+closeTurns.width/2,closeTurns.y+closeTurns.height/2,{button:'left',clickCount:1});
await mouse('mouseReleased',closeTurns.x+closeTurns.width/2,closeTurns.y+closeTurns.height/2,{button:'left',clickCount:1});
assert.equal(await evaluate(`document.querySelectorAll('.hud-turns-popup').length`),0,'real pointer click closes dragged turn-order window');
await evaluate(`window.mageShow('hud_crowd')`);await wait(150);
// Smaller windows retain reachable controls and deliberately stack the central panels above edge controls.
for(const width of [1200,900]){
 await call('Emulation.setDeviceMetricsOverride',{width,height:850,deviceScaleFactor:1,mobile:false});await wait(150);
 const out=await evaluate(`(()=>{const r=document.querySelector('.floating-battle').getBoundingClientRect();return [...document.querySelectorAll('[data-hud-group]')].filter(n=>{const b=n.getBoundingClientRect();return b.left<r.left-1||b.right>r.right+1||b.top<r.top-1||b.bottom>r.bottom+1}).map(n=>n.dataset.hudGroup)})()`);
 assert.deepEqual(out,[],`all groups inside ${width}px window`);
 const sections=await evaluate(`['.battle-primary-panel','.combat-hotbar','.combat-status-tray'].map(s=>document.querySelector('.hud-skills '+s).getBoundingClientRect().toJSON())`);
 assert.ok(sections[0].right<=sections[1].left+1&&sections[1].right<=sections[2].left+1,'three sections do not overlap');
 const tools=await evaluate(`Array.from(document.querySelectorAll('.hud-tool-buttons button:not([hidden])')).filter(n=>n.getClientRects().length).map(n=>n.getBoundingClientRect().top)`);
 assert.ok(tools.every(y=>y===tools[0]),'tools stay in one row');
}
assert.deepEqual(errors,[]);console.log('PASS: label-safe fit, bounded pan/recenter, matching two-row panels/icons, effects visibility/overflow, turn-order cap/full popup/drag/refresh, HUD drag/snap/persistence, responsive bounds; no browser exceptions');ws.close();
