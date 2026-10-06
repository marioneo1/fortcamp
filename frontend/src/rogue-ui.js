let session=null, bindings=null, popup=null;
export function rogueSession(view){
 const actor=view.units?.[view.current_unit_id],id=actor?.special?.id,key=`${view.seed}:${actor?.id}:${id}`;
 if(session?.key!==key)session={key,rotation:0,target:null,landing:null,center:null,hover:null,attack:'basic',phase:'choose'};
 return session;
}
export function resetRoguePlacement(){session=null;bindings?.abort();popup?.remove();popup=null}
export function placementCommand(view,s){
 const id=view.units?.[view.current_unit_id]?.special?.id,p=view.rogue_previews?.[id];if(!p)return null;
 if(p.kind==='shadowstep'&&p.targets?.[s.target]?.some(c=>c.x===s.landing?.x&&c.y===s.landing?.y))return {action:'skill',skill_id:id,target_id:s.target,...s.landing};
 if(p.kind==='backflip'&&p.landings.some(c=>c.x===s.landing?.x&&c.y===s.landing?.y))return {action:'skill',skill_id:id,...s.landing};
 if(p.kind==='caltrops'&&p.strips[`${s.center?.x},${s.center?.y},${s.rotation}`])return {action:'skill',skill_id:id,...s.center,rotation:s.rotation};
 if(p.kind==='throwing_knife'&&p.attacks[s.attack]?.[s.target])return {action:s.attack==='basic'?'attack':'skill',...(s.attack==='basic'?{}:{skill_id:s.attack}),target_id:s.target,knife_skill_id:id};
 return null;
}
export function roguePreviewView(view,mode){
 const id=view.units?.[view.current_unit_id]?.special?.id,p=view.rogue_previews?.[id];if(mode!=='skill'||p?.kind!=='throwing_knife')return view;
 const s=rogueSession(view);return {...view,attack_previews:Object.fromEntries(Object.entries(p.attacks[s.attack]||{}).map(([id,forecast])=>[id,{skill:forecast}]))};
}
export function selectRogueCell(view,s,c,id){
 const p=view.rogue_previews?.[view.units?.[view.current_unit_id]?.special?.id];if(!p||s.phase==='confirm')return;
 if(p.kind==='shadowstep'){if(p.targets[id]?.length){s.target=id;s.landing=null}else s.landing=c}
 else if(p.kind==='backflip')s.landing=c;
 else if(p.kind==='caltrops')s.center={...c};
 else s.target=id||Object.values(view.units).find(u=>u.x===c.x&&u.y===c.y&&p.attacks[s.attack]?.[u.id])?.id;
 if(placementCommand(view,s))s.phase='confirm';
}
export function mountRoguePlacement({view,mode,field,host,send,cancel,escape,refreshPreview,blocked=()=>false}){
 bindings?.abort();popup?.remove();popup=null;field?.classList.remove('rogue-placement');host?.querySelector('.rogue-placement-panel')?.remove();field?.querySelector('.rogue-target-layer')?.remove();
 const actor=view.units?.[view.current_unit_id],p=view.rogue_previews?.[actor?.special?.id];if(!field||mode!=='skill'||!p)return;
 field.classList.add('rogue-placement');bindings=new AbortController();const opts={signal:bindings.signal},s=rogueSession(view),layer=document.createElement('div'),panel=document.createElement('section'),viewport=field.closest('.battle-viewport');
 layer.className='rogue-target-layer';panel.className='rogue-placement-panel';field.append(layer);host.append(panel);
 const finishCancel=()=>{resetRoguePlacement();cancel()};
 const name=id=>id==='basic'?'Basic Attack':actor.skills.find(a=>a.id===id)?.name||id;
 const paint=()=>{
  const center=s.phase==='confirm'?s.center:s.hover||s.center;
  let cells=p.kind==='shadowstep'?p.targets[s.target]||[]:p.kind==='backflip'?p.landings:p.kind==='caltrops'?p.strips[`${center?.x},${center?.y},${s.rotation}`]||[]:[];
  const legal=p.kind!=='caltrops'||!!p.strips[`${center?.x},${center?.y},${s.rotation}`];
  if(p.kind==='caltrops'&&center&&!cells.length)cells=[-1,0,1].map(i=>({x:center.x+(s.rotation?0:i),y:center.y+(s.rotation?i:0)})).filter(c=>c.x>=0&&c.x<view.width&&c.y>=0&&c.y<view.height);
  layer.innerHTML=cells.map(c=>`<i class="${!legal?'invalid':s.phase==='confirm'?'chosen':''}" style="left:${c.x/view.width*100}%;top:${c.y/view.height*100}%;width:${100/view.width}%;height:${100/view.height}%"></i>`).join('');
  const help={shadowstep:'Choose an enemy, then an adjacent landing.',backflip:'Choose a highlighted cardinal landing.',caltrops:'Click or drag to choose a three-tile strip. R rotates.',throwing_knife:'Choose a target beyond melee range.'}[p.kind];
  panel.innerHTML=`<div><strong>${escape(actor.special.name)}</strong><small>${help} ${p.kind==='throwing_knife'?escape(name(s.attack))+' · Main attack ends activation.':'Quick Action: main action remains.'}</small></div>${p.kind==='caltrops'?'<button data-rogue-rotate>R · Rotate</button>':''}${p.kind==='throwing_knife'?'<button data-rogue-change>Choose attack</button>':''}<button data-rogue-cancel>C · Cancel</button>`;
  panel.querySelector('[data-rogue-cancel]').onclick=finishCancel;
  const rotate=()=>{if(!blocked()){s.rotation=1-s.rotation;paint()}};panel.querySelector('[data-rogue-rotate]')?.addEventListener('click',rotate);
  panel.querySelector('[data-rogue-change]')?.addEventListener('click',()=>{s.phase='choose';s.target=null;paint()});
  popup?.remove();popup=null;
  const choosing=p.kind==='throwing_knife'&&s.phase==='choose';if(!choosing&&s.phase!=='confirm')return;
  popup=document.createElement('div');popup.className='rogue-map-prompt';
  const target=view.units[s.target],label=choosing?'Choose a knife attack':p.kind==='throwing_knife'?`Use ${name(s.attack)} on ${target?.name||'target'}?`:`Confirm ${actor.special.name}?`;
  popup.innerHTML=`<section role="dialog" aria-modal="false" aria-label="${escape(label)}" class="rogue-prompt-card"><small>${choosing?'THROWING KNIFE':'CONFIRM ACTION'}</small><h3>${escape(label)}</h3>${choosing?`<div class="rogue-attack-choices">${Object.keys(p.attacks).map(id=>`<button data-rogue-attack="${escape(id)}">${escape(name(id))}</button>`).join('')}</div>`:`<p>${p.kind==='caltrops'?'Three trap tiles. Your main action remains available.':p.kind==='throwing_knife'?'Uses this main attack and Throwing Knife cooldowns. Ends activation.':'Your main action remains available.'}</p><button data-rogue-confirm ${!placementCommand(view,s)||blocked()?'disabled':''}>Confirm</button>`}<button data-rogue-cancel>Cancel</button></section>`;
  const stage=viewport.closest('.battle-map-stage')||viewport.parentElement;stage.append(popup);const place=()=>{if(popup){popup.style.left=viewport.offsetLeft+'px';popup.style.top=viewport.offsetTop+'px';popup.style.width=viewport.offsetWidth+'px';popup.style.height=viewport.offsetHeight+'px'}};place();
  popup.querySelector('[data-rogue-cancel]').onclick=finishCancel;
  popup.querySelector('[data-rogue-confirm]')?.addEventListener('click',()=>{if(blocked())return;const command=placementCommand(view,s);if(command){resetRoguePlacement();send(command)}});
  popup.querySelectorAll('[data-rogue-attack]').forEach(b=>b.onclick=()=>{if(blocked())return;s.attack=b.dataset.rogueAttack;s.target=null;s.phase='target';if(refreshPreview)refreshPreview();else paint()});
 };
 const point=e=>{const rect=field.getBoundingClientRect();return {x:Math.floor((e.clientX-rect.left)/rect.width*view.width),y:Math.floor((e.clientY-rect.top)/rect.height*view.height)}};
 const selectedPoint=e=>{const id=e.target.closest('[data-battle-unit]')?.dataset.battleUnit,cell=e.target.closest('[data-battle-cell]')?.dataset.battleCell;return {id,c:cell?Object.fromEntries(cell.split(',').map((v,i)=>[i?'y':'x',Number(v)])):view.units[id]?{x:view.units[id].x,y:view.units[id].y}:point(e)}};
 field.addEventListener('click',e=>{e.stopImmediatePropagation();if(blocked()||s.phase==='confirm'||p.kind==='throwing_knife'&&s.phase==='choose')return;const {c,id}=selectedPoint(e);selectRogueCell(view,s,c,id);paint()}, {...opts,capture:true});
 if(p.kind==='caltrops'){
  let dragging=false;
  field.addEventListener('pointerdown',e=>{if(e.button===0&&!blocked()&&s.phase!=='confirm'){dragging=true;s.hover=point(e);paint()}},opts);
  document.addEventListener('pointerup',e=>{if(!dragging)return;dragging=false;if(!field.contains(e.target)){s.center=null;s.hover=null;paint();return}selectRogueCell(view,s,point(e));paint()},opts);
  field.addEventListener('pointermove',e=>{if(blocked()||s.phase==='confirm'||e.buttons===2)return;const c=point(e);if(c.x!==s.hover?.x||c.y!==s.hover?.y){s.hover=c;paint()}},opts);
 }
 const observer=new ResizeObserver(()=>{if(popup){popup.style.left=viewport.offsetLeft+'px';popup.style.top=viewport.offsetTop+'px';popup.style.width=viewport.offsetWidth+'px';popup.style.height=viewport.offsetHeight+'px'}});observer.observe(viewport);bindings.signal.addEventListener('abort',()=>observer.disconnect(),{once:true});
 document.addEventListener('keydown',e=>{if(e.target.closest?.('input,textarea,select,[contenteditable]'))return;if(['c','escape'].includes(e.key.toLowerCase())){e.preventDefault();e.stopImmediatePropagation();finishCancel()}else if(p.kind==='caltrops'&&e.key.toLowerCase()==='r'){e.preventDefault();e.stopImmediatePropagation();if(!blocked()){s.rotation=1-s.rotation;paint()}}},{...opts,capture:true});paint();
}
