import {snapHud,hudPosition,hudScale,resizeHudScale} from './battle-hud-geometry.js';
import {MOBILE_BATTLE_QUERY} from './battle-touch.js';
import './battle-hud.css';
import './battle-mobile.css';
import {bindPlacementPanel} from './combat-placement-panel.js';
const toolPaths={"center": "<circle cx=\"12\" cy=\"12\" r=\"6\"/><path d=\"M12 2v6m0 8v6M2 12h6m8 0h6\"/>", "supplies": "<path d=\"M8 7V4h8v3M5 7h14v14H5zM5 12h14M9 12v3h6v-3\"/>", "history": "<path d=\"M5 3h14v18H5zM9 7h6M9 11h6M9 15h4\"/>", "options": "<path d=\"M4 6h16M4 12h16M4 18h16M8 3v6m8 0v6M9 15v6\"/>", "edit": "<path d=\"M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z\"/>", "reset": "<path d=\"M4 9a8 8 0 1 1 0 6M4 3v6h6\"/>", "done": "<path d=\"m4 12 5 5L20 6\"/>"};
const toolIcon=id=>`<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${toolPaths[id]}</svg>`;
const KEY='fortcamp:battle-hud:v1';
let bindings,observer,effectsBindings,turnBindings,editing=false,mobileTab='commands',mobileCollapsed=false;
let saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch{}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(saved))}catch{}};
const clamp=(v,max)=>Math.max(0,Math.min(Math.max(0,max),v));

// Transform before DOM reconciliation so the battlefield and tokens keep their identity.
export function floatingBattleMarkup(fragment){
 const root=fragment.querySelector('.battle-layout.layout-a');if(!root)return;
 root.classList.add('floating-battle');
 const field=root.querySelector('.battlefield'),space=document.createElement('div');space.className='battle-camera-space';field.before(space);space.append(field);
 const header=fragment.querySelector('.layout-a-header'),dock=root.querySelector('.battle-command-dock');
 const groups=[];
 const group=(node,id,label)=>{if(!node)return;node.classList.add('hud-group');node.dataset.hudGroup=id;node.insertAdjacentHTML('afterbegin',`<button class="hud-handle" data-hud-handle="${id}" aria-label="Move ${label}" title="Drag to move; arrow keys adjust position">${label}<span aria-hidden="true">&#x283f;</span></button>`);if(['title','actor','turns','skills'].includes(id))node.insertAdjacentHTML('beforeend',`<button class="hud-resize-handle" data-hud-resize="${id}" aria-label="Resize ${label}" title="Drag to resize; arrow keys adjust size">&#x2922;</button>`);groups.push(node)};
 header.firstElementChild.append(header.querySelector('.battle-objectives'));
 const titleGroup=header.firstElementChild;group(titleGroup,'title','Battle, objectives & tools');
 const turn=header.querySelector('.turn-order'),turnWrap=document.createElement('div');turnWrap.className='hud-turn-order layout-a-header';turnWrap.append(turn);turn.insertAdjacentHTML('beforeend','<span class="turn-overflow" hidden></span>');turnWrap.tabIndex=0;turnWrap.setAttribute('role','button');turnWrap.setAttribute('aria-label','Inspect full turn order');turnWrap.title='Click to inspect the full turn order';group(turnWrap,'turns','Turn order');
 const actor=dock.querySelector('.dock-actor'),preview=dock.querySelector('.battle-action-preview');
 const actorGroup=document.createElement('div');actorGroup.className='hud-actor-group';actorGroup.append(actor,preview);group(actorGroup,'actor','Character & action');
 const skills=document.createElement('div');skills.className='hud-skills';
 const bar=dock.querySelector('.combat-hotbar'),effects=dock.querySelector('.combat-status-tray');if(bar)skills.append(bar);
 if(effects)skills.append(effects);
 group(skills,'skills','Command, skills & effects');
 const commands=dock.querySelector('.battle-primary-panel');commands.querySelector('.eyebrow')?.remove();commands.insertAdjacentHTML('afterbegin','<header class="hud-commands-header"><b>Command</b></header>');for(const button of commands.querySelectorAll('.combat-actions>button')){const key=button.querySelector('kbd');if(key)button.prepend(key)}
 skills.prepend(commands);
 const tools=root.querySelector('.battle-field-toolbar');tools.querySelector('small')?.remove();
 const center=tools.querySelector('[data-battle-fit]');
 tools.insertAdjacentHTML('beforeend','<button data-hud-edit></button><button data-hud-reset hidden></button>');
 const toolRow=document.createElement('div');toolRow.className='hud-tool-buttons';toolRow.append(...tools.children);tools.append(toolRow);
 for(const [selector,id,label] of [['[data-battle-fit]','center','Center map'],['[data-battle-popup="supplies"]','supplies','Battle supplies'],['[data-battle-popup="history"]','history','Battle history'],['[data-battle-popup="options"]','options','Battle options'],['[data-hud-edit]','edit','Edit layout'],['[data-hud-reset]','reset','Reset layout']]){
  const button=tools.querySelector(selector);button.innerHTML=toolIcon(id);button.setAttribute('aria-label',label);button.title=label;
 }
 center.title='Center and fit the map';
 titleGroup.append(tools);
 tools.querySelector('.hud-tool-buttons').insertAdjacentHTML('beforeend','<button class="mobile-battle-control" data-mobile-objectives aria-label="Show objectives" title="Objectives">Goals</button><button class="mobile-battle-control" data-mobile-turns aria-label="Show turn order" title="Turn order">Order</button>');
 skills.insertAdjacentHTML('afterbegin','<nav class="mobile-battle-tabs" aria-label="Battle controls"><button data-mobile-tab="commands">Commands</button><button data-mobile-tab="skills">Skills</button><button data-mobile-tab="effects">Effects</button><button data-mobile-cancel>Cancel</button><button data-mobile-collapse aria-label="Hide controls">Hide</button></nav>');
 const context=dock.querySelector('.context-action-menu');if(context)group(context,'context','Context actions');
 const lab=fragment.querySelector('.battle-lab-toolbar');if(lab){group(lab,'lab','Battle Lab');tools.querySelector('.hud-tool-buttons').insertAdjacentHTML('beforeend','<button class="mobile-battle-control" data-mobile-lab aria-expanded="false">Lab</button>')}
 header.remove();dock.remove();root.append(...groups);
 root.insertAdjacentHTML('beforeend','<div class="hud-guides" aria-hidden="true"></div>');
}

// Adopted from the player's exported layout; obsolete standalone groups are ignored.
const defaults={title:{x:0,y:0},turns:{x:0.49998039795173677,y:0},actor:{x:0,y:1},skills:{x:0.4999691874022197,y:0.9999909647535035,width:1215.99609375},context:{x:.5,y:.5},lab:{x:0,y:0.21903375339443312}};
export function mountBattleHud(host,{openEffects,effectsKey,effectsMarkup,onCancel=()=>{}}={}){
 const popup=document.querySelector('.hud-effects-popup:not(.hud-turns-popup)');if(popup&&popup.dataset.effectsOwner!==String(effectsKey))closeHudEffects();else if(popup&&effectsMarkup)popup.querySelector('.hud-effects-content').innerHTML=effectsMarkup();
 bindings?.abort();observer?.disconnect();const root=host.querySelector('.floating-battle');if(!root)return;
 bindings=new AbortController();const {signal}=bindings,groups=[...root.querySelectorAll('[data-hud-group]')],guides=root.querySelector('.hud-guides');
 const size=()=>({width:root.clientWidth,height:root.clientHeight});
 const trimEffects=()=>{
  const tray=root.querySelector('.combat-status-tray');if(!tray)return;
  const button=tray.querySelector('[data-all-effects]'),icons=tray.querySelector('.status-tray-icons'),badges=[...tray.querySelectorAll('.status-badge')],total=Number(button.dataset.effectCount);
  const columns=Math.max(1,Math.floor((icons.clientWidth+6)/36)),rows=Math.max(0,Math.floor((icons.clientHeight+6)/36));
  const count=Math.min(badges.length,columns*rows);badges.forEach((badge,i)=>badge.hidden=i>=count);button.textContent=total>count?`+${total-count} more`:'All effects';
 };
 const syncControls=()=>{
  const skills=root.querySelector('.hud-skills');
  const columns=Math.ceil(root.querySelectorAll('.battle-primary-panel .combat-actions>button').length/2);
  const tile=Math.min(88,Math.max(40,Math.floor((skills.clientWidth-24-50-120-10*(columns+3))/(columns+5))));
  root.style.setProperty('--hud-command-columns',String(columns));
  root.style.setProperty('--hud-tile',`${tile}px`);
  skills.style.setProperty('--hud-command-width',`${columns*tile+(columns-1)*10+12}px`);
  skills.style.setProperty('--hud-skill-width',`${5*tile+40+25}px`);
 };

 const store=node=>{const b=size(),r=node.getBoundingClientRect(),o=root.getBoundingClientRect();saved[node.dataset.hudGroup]={x:clamp(r.left-o.left,b.width-r.width)/Math.max(1,b.width-r.width),y:clamp(r.top-o.top,b.height-r.height)/Math.max(1,b.height-r.height),...(['title','actor','turns','skills'].includes(node.dataset.hudGroup)?{scale:Number(node.dataset.hudScale)||1}:{}),...(node.dataset.hudGroup==='skills'?{width:node.offsetWidth}:{})};save()};
 const turns=root.querySelector('.hud-turn-order');
 const turnContent=()=>{const list=turns.querySelector('.turn-order>div').cloneNode(true);list.querySelectorAll('[hidden]').forEach(n=>n.hidden=false);return list.outerHTML};
 const trimTurns=()=>{const chips=[...turns.querySelectorAll('.turn-chip')],count=Math.min(10,Math.max(1,Math.floor((root.clientWidth-130)/114))),more=turns.querySelector('.turn-overflow');chips.forEach((chip,i)=>chip.hidden=i>=count);more.hidden=chips.length<=count;more.textContent=`+${chips.length-count} more`;const full=document.querySelector('.hud-turns-content');if(full)full.innerHTML=turnContent()};
 const place=()=>{
  if(window.matchMedia(MOBILE_BATTLE_QUERY).matches){groups.forEach(n=>{n.style.transform='';n.style.removeProperty('--hud-panel-scale')});trimEffects();return}
  const skillPanel=root.querySelector('.hud-skills');skillPanel.style.width=`${Math.min(Math.max(650,saved.skills?.width||defaults.skills.width),root.clientWidth-24)}px`;
  syncControls();trimTurns();
  const b=size(),actor=groups.find(n=>n.dataset.hudGroup==='actor');
  for(const node of groups){
   const id=node.dataset.hudGroup,stored=saved[id];
   const scale=hudScale(stored?.scale??1,{width:node.offsetWidth,height:node.offsetHeight},b);node.dataset.hudScale=String(scale);node.style.setProperty('--hud-panel-scale',String(scale));node.style.transform=`scale(${scale})`;
   const r=node.getBoundingClientRect(),p=hudPosition(stored,r,b,defaults[id]);
   if(!stored){
    if(id==='turns'&&(b.width<1150||turns.querySelectorAll('.turn-chip:not([hidden])').length>4))p.y=(root.querySelector('[data-hud-group="title"]')?.offsetHeight||90)+12;
   }
   node.style.left=`${p.x}px`;node.style.top=`${p.y}px`;
  }
  if(actor&&!saved.actor){const bar=skillPanel.getBoundingClientRect(),card=actor.getBoundingClientRect();if(card.left<bar.right&&card.right>bar.left&&card.top<bar.bottom&&card.bottom>bar.top)actor.style.top=`${clamp(parseFloat(skillPanel.style.top)-card.height-12,b.height-card.height)}px`}

 };

 const edit=()=>{root.classList.toggle('hud-editing',editing);const button=root.querySelector('[data-hud-edit]');button.innerHTML=toolIcon(editing?'done':'edit');button.title=editing?'Done editing':'Edit layout';button.setAttribute('aria-label',button.title);root.querySelector('[data-hud-reset]').hidden=!editing;root.querySelector('[data-hud-edit]').setAttribute('aria-pressed',String(editing));place()};
 root.querySelector('[data-hud-edit]').onclick=()=>{editing=!editing;edit()};
 root.querySelector('[data-hud-reset]').onclick=()=>{saved={};save();groups.forEach(n=>n.style.width='');place()};
 let drag=null;
 root.addEventListener('pointerdown',e=>{const handle=e.target.closest('[data-hud-handle]');if(!editing||!handle||e.button!==0)return;const node=handle.closest('.hud-group'),r=node.getBoundingClientRect();drag={node,id:e.pointerId,dx:e.clientX-r.left,dy:e.clientY-r.top};handle.setPointerCapture(e.pointerId);node.classList.add('hud-dragging');e.preventDefault();e.stopPropagation()},{signal});
 root.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const r=drag.node.getBoundingClientRect(),o=root.getBoundingClientRect(),b=size(),candidate={x:e.clientX-o.left-drag.dx,y:e.clientY-o.top-drag.dy,width:r.width,height:r.height};const other=groups.filter(n=>n!==drag.node).map(n=>{const p=n.getBoundingClientRect();return {x:p.left-o.left,y:p.top-o.top,width:p.width,height:p.height}});const p=snapHud(candidate,other,b,e.shiftKey?0:8);drag.node.style.left=`${p.x}px`;drag.node.style.top=`${p.y}px`;guides.innerHTML=p.guides.map(g=>`<i class="guide-${g.axis}" style="${g.axis==='x'?'left':'top'}:${g.value}px"></i>`).join('');e.preventDefault()},{signal});
 const finish=()=>{if(!drag)return;store(drag.node);drag.node.classList.remove('hud-dragging');drag=null;guides.innerHTML=''};
 root.addEventListener('pointerup',finish,{signal});root.addEventListener('pointercancel',finish,{signal});root.addEventListener('lostpointercapture',finish,{signal});
 root.addEventListener('keydown',e=>{const h=e.target.closest('[data-hud-handle]');if(!editing||!h||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;const n=h.closest('.hud-group'),r=n.getBoundingClientRect(),o=root.getBoundingClientRect(),step=e.shiftKey?1:8,b=size();n.style.left=`${clamp(r.left-o.left+(e.key==='ArrowLeft'?-step:e.key==='ArrowRight'?step:0),b.width-r.width)}px`;n.style.top=`${clamp(r.top-o.top+(e.key==='ArrowUp'?-step:e.key==='ArrowDown'?step:0),b.height-r.height)}px`;store(n);e.preventDefault();e.stopPropagation()},{signal});
 root.querySelector('[data-all-effects]')?.addEventListener('click',()=>openEffects?.(),{signal});
 const openTurns=()=>{if(!editing)openHudTurns(host.closest('#mission-modal')||host,turnContent())};
 const mobileSync=()=>{
  root.dataset.mobileTab=mobileTab;root.classList.toggle('mobile-controls-collapsed',mobileCollapsed);
  root.querySelectorAll('[data-mobile-tab]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.mobileTab===mobileTab)));
  const collapse=root.querySelector('[data-mobile-collapse]');collapse.textContent=mobileCollapsed?'Show':'Hide';collapse.setAttribute('aria-label',mobileCollapsed?'Show controls':'Hide controls');
  trimEffects();
 };
 root.querySelectorAll('[data-mobile-tab]').forEach(button=>button.onclick=()=>{mobileTab=button.dataset.mobileTab;mobileCollapsed=false;mobileSync()});
 root.querySelector('[data-mobile-collapse]').onclick=()=>{mobileCollapsed=!mobileCollapsed;mobileSync()};
 root.querySelector('[data-mobile-cancel]').onclick=()=>onCancel();
 root.querySelector('[data-mobile-turns]').onclick=()=>openHudTurns(host.closest('#mission-modal')||host,turnContent());
 root.querySelector('[data-mobile-objectives]').onclick=event=>{const shown=root.classList.toggle('mobile-objectives-open');event.currentTarget.setAttribute('aria-expanded',String(shown))};
 root.querySelector('[data-mobile-lab]')?.addEventListener('click',event=>{event.currentTarget.setAttribute('aria-expanded',String(root.classList.toggle('mobile-lab-open')))},{signal});
 mobileSync();
 window.matchMedia(MOBILE_BATTLE_QUERY).addEventListener('change',place,{signal});
 turns.addEventListener('click',openTurns,{signal});turns.addEventListener('keydown',e=>{if(e.target===turns&&['Enter',' '].includes(e.key)){e.preventDefault();e.stopPropagation();openTurns()}},{signal});
 // Resize uniformly, rather than squeezing text and icons into new proportions.
 let resizing=null;
 root.addEventListener('pointerdown',e=>{
  const handle=e.target.closest('[data-hud-resize]');if(!editing||!handle||e.button!==0)return;
  const node=handle.closest('.hud-group');resizing={node,id:e.pointerId,x:e.clientX,y:e.clientY,scale:Number(node.dataset.hudScale)||1,size:{width:node.offsetWidth,height:node.offsetHeight}};
  handle.setPointerCapture(e.pointerId);node.classList.add('hud-resizing');e.preventDefault();e.stopPropagation();
 },{signal});
 root.addEventListener('pointermove',e=>{
  if(!resizing||resizing.id!==e.pointerId)return;
  const {node,scale,x,y,size:base}=resizing,next=resizeHudScale(scale,e.clientX-x,e.clientY-y,base,size());
  node.dataset.hudScale=String(next);node.style.setProperty('--hud-panel-scale',String(next));node.style.transform=`scale(${next})`;
  const r=node.getBoundingClientRect();node.style.left=`${clamp(parseFloat(node.style.left)||0,root.clientWidth-r.width)}px`;node.style.top=`${clamp(parseFloat(node.style.top)||0,root.clientHeight-r.height)}px`;
  e.preventDefault();e.stopPropagation();
 },{signal});
 const finishResize=()=>{if(!resizing)return;store(resizing.node);resizing.node.classList.remove('hud-resizing');resizing=null;place();trimEffects()};
 root.addEventListener('pointerup',finishResize,{signal});root.addEventListener('pointercancel',finishResize,{signal});root.addEventListener('lostpointercapture',finishResize,{signal});
 root.addEventListener('keydown',e=>{
  const handle=e.target.closest('[data-hud-resize]');if(!editing||!handle||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;
  const node=handle.closest('.hud-group'),step=e.shiftKey?.01:.05,next=hudScale((Number(node.dataset.hudScale)||1)+(['ArrowRight','ArrowUp'].includes(e.key)?step:-step),{width:node.offsetWidth,height:node.offsetHeight},size());
  node.dataset.hudScale=String(next);node.style.transform=`scale(${next})`;node.style.setProperty('--hud-panel-scale',String(next));store(node);place();e.preventDefault();e.stopPropagation();
 },{signal});
 observer=new ResizeObserver(entries=>{if(entries.some(e=>e.target===root))place();else syncControls();trimEffects()});observer.observe(root);const skillGroup=root.querySelector('.hud-skills');if(skillGroup)observer.observe(skillGroup);edit();trimEffects();
}

export function closeHudEffects(){effectsBindings?.abort();document.querySelector('.hud-effects-popup:not(.hud-turns-popup)')?.remove()}
export function openHudEffects(host,markup,name,owner){
 closeHudEffects();
 const popup=document.createElement('section');popup.className='hud-inspection-panel hud-effects-popup';popup.dataset.effectsOwner=String(owner);popup.setAttribute('role','dialog');popup.setAttribute('aria-label',`${name} active effects`);popup.innerHTML=`<header data-placement-handle><small>ACTIVE EFFECTS - DRAG TO MOVE</small><h3></h3><button data-close-effects aria-label="Close effects">&times;</button></header><div class="hud-effects-content">${markup}</div>`;popup.querySelector('[data-close-effects]').title='Close effects';popup.querySelector('h3').textContent=name;host.append(popup);
 effectsBindings=new AbortController();const {signal}=effectsBindings;bindPlacementPanel(popup,'battle-effects',signal);popup.querySelector('[data-close-effects]').onclick=closeHudEffects;
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeHudEffects();e.stopImmediatePropagation();e.preventDefault()}},{signal,capture:true});
}

export function closeHudTurns(){turnBindings?.abort();document.querySelector('.hud-turns-popup')?.remove()}
function openHudTurns(host,markup){
 closeHudTurns();
 const panel=document.createElement('section');panel.className='hud-inspection-panel hud-effects-popup hud-turns-popup';
 panel.innerHTML=`<header data-placement-handle><small>TURN ORDER - DRAG TO MOVE</small><h3>Upcoming activations</h3><button data-close-turns aria-label="Close turn order">&times;</button></header><div class="hud-turns-content hud-full-turns layout-a-header">${markup}</div>`;
 panel.setAttribute('role','dialog');panel.setAttribute('aria-label','Full turn order');host.append(panel);
 turnBindings=new AbortController();const {signal}=turnBindings;bindPlacementPanel(panel,'battle-turn-order',signal);
 panel.querySelector('[data-close-turns]').title='Close turn order';panel.querySelector('[data-close-turns]').onclick=closeHudTurns;
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeHudTurns();e.preventDefault();e.stopImmediatePropagation()}},{signal,capture:true});
}
