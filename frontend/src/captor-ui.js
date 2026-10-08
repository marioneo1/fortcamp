import {bindPlacementPanel} from './combat-placement-panel.js';
let controller=null,panel=null;
export function resetCaptor(){controller?.abort();panel?.remove();panel=null}
export function mountCaptor(view,mode,host,send,cancel,escape,blocked=()=>false){
 controller?.abort();panel?.remove();host?.querySelector('.captor-drag-layer')?.remove();
 const actor=view.units?.[view.current_unit_id],skill=actor?.special,field=host?.querySelector('.battlefield');
 if(!field||mode!=='skill'||skill?.captor_kind!=='abduct')return;
 const previews=view.skill_previews?.[skill.id]||{};controller=new AbortController();const opts={signal:controller.signal};
 panel=document.createElement('section');panel.className='summoner-panel captor-drag-prompt';host.querySelector('.battle-map-stage').append(panel);
 bindPlacementPanel(panel,'captor-abduct',controller.signal);
 const layer=document.createElement('div');layer.className='rogue-target-layer captor-drag-layer';field.append(layer);
 let target=null,destination=null;
 const close=()=>{resetCaptor();layer.remove();cancel()};
 panel.addEventListener('contextmenu',e=>{e.preventDefault();close()},opts);
 function paint(){
  const options=previews[target]?.drag_destinations||{};
  layer.innerHTML=Object.keys(options).map(key=>{const [x,y]=key.split(',').map(Number);return `<i style="left:${x/view.width*100}%;top:${y/view.height*100}%;width:${100/view.width}%;height:${100/view.height}%" class="${key===destination?'chosen':''}"></i>`}).join('');
  if(destination&&options[destination]){
   const route=options[destination];layer.innerHTML+=route.path.map(p=>`<i style="left:${p.x/view.width*100}%;top:${p.y/view.height*100}%;width:${100/view.width}%;height:${100/view.height}%" class="chosen"></i>`).join('');
  }
  panel.innerHTML=`<header data-placement-handle><small>CAPTOR - DRAG TO MOVE</small><h3>Abduct</h3></header><p>${target?`Drag ${escape(view.units[target].name)} to a highlighted tile.`:'Choose a Hobbled enemy, then a drag destination.'}</p><footer><button data-captor-confirm ${destination?'':'disabled'}><kbd>E</kbd> Confirm</button><button data-captor-cancel><kbd>C</kbd> Cancel</button></footer>`;
  panel.querySelector('[data-captor-cancel]').onclick=close;
  panel.querySelector('[data-captor-confirm]').onclick=()=>{if(blocked()||!destination)return;const [x,y]=destination.split(',').map(Number),preview=previews[target];const command={action:'skill',skill_id:skill.id,target_id:target,x,y,...(preview.move_to?{move_to:preview.move_to}:{})};resetCaptor();layer.remove();send(command)};
 }
 field.addEventListener('click',e=>{e.stopImmediatePropagation();if(blocked())return;const id=e.target.closest('[data-battle-unit]')?.dataset.battleUnit,cell=e.target.closest('[data-battle-cell]')?.dataset.battleCell;if(id&&previews[id]){target=id;destination=null}else if(cell&&previews[target]?.drag_destinations[cell])destination=cell;paint()},{...opts,capture:true});
 field.addEventListener('pointermove',e=>{const rect=field.getBoundingClientRect(),x=Math.floor((e.clientX-rect.left)/rect.width*view.width),y=Math.floor((e.clientY-rect.top)/rect.height*view.height);const id=e.target.closest('[data-battle-unit]')?.dataset.battleUnit;field.classList.toggle('spell-invalid',!(id&&previews[id]||previews[target]?.drag_destinations[`${x},${y}`]))},opts);
 document.addEventListener('keydown',e=>{if(e.target.closest?.('input,textarea,select'))return;const key=e.key.toLowerCase();if(['e','c','escape'].includes(key)){e.preventDefault();e.stopImmediatePropagation();if(key==='e')panel.querySelector('[data-captor-confirm]:not(:disabled)')?.click();else close()}},{...opts,capture:true});
 paint();
}

export function emitCaptorEffect(field,event,battle,delay){
 if(!event.skill?.startsWith('captor_'))return false;
 setTimeout(()=>{
  if(!field.isConnected)return;
  const to=event.to||event,from={x:event.x,y:event.y},cw=field.clientWidth/battle.width,ch=field.clientHeight/battle.height;
  const el=document.createElement('span');el.className='captor-effect';el.style.cssText=`left:${(to.x+.5)/battle.width*100}%;top:${(to.y+.5)/battle.height*100}%;width:${1.1/battle.width*100}%`;
  if(event.skill==='captor_blitz')el.innerHTML='<svg viewBox="0 0 100 100"><path d="m10 25 35 0-15 18h45L55 65h35M5 75h27"/></svg>';
  else el.innerHTML='<img src="/assets/captor-v1/rope_prop.png" alt="">';
  field.append(el);
  if(event.skill==='captor_hook_and_drag'){
   const dx=(to.x-from.x)*cw,dy=(to.y-from.y)*ch,tether=document.createElement('span');tether.className='captor-tether';tether.style.cssText=`left:${(from.x+.5)/battle.width*100}%;top:${(from.y+.5)/battle.height*100}%;width:${Math.hypot(dx,dy)}px;transform:rotate(${Math.atan2(dy,dx)}rad)`;field.append(tether);tether.animate([{opacity:0,scale:'0 1'},{opacity:1,scale:'1 1',offset:.39},{opacity:.9,scale:'.4 1',offset:.8},{opacity:0,scale:'.4 1'}],{duration:560}).onfinish=()=>tether.remove();
  }
  if(['captor_bola','captor_hook_and_drag'].includes(event.skill)){
   const projectile=document.createElement('img');projectile.className='captor-projectile';projectile.src=`/assets/captor-v1/${event.skill==='captor_bola'?'bola_prop':'hook_prop'}.png`;projectile.style.cssText=`left:${(from.x+.5)/battle.width*100}%;top:${(from.y+.5)/battle.height*100}%;width:${.55/battle.width*100}%`;field.append(projectile);
   projectile.animate([{transform:'translate(-50%,-50%) scale(.6) rotate(-60deg)'},{transform:`translate(calc(-50% + ${(to.x-from.x)*cw}px),calc(-50% + ${(to.y-from.y)*ch}px)) scale(1) rotate(180deg)`}],{duration:220}).onfinish=()=>projectile.remove();
   el.style.opacity='0';setTimeout(()=>{el.style.opacity='1';el.animate([{transform:'translate(-50%,-50%) scale(1.4)',opacity:1},{transform:'translate(-50%,-50%) scale(.75)',opacity:.8},{transform:'translate(-50%,-50%) scale(.9)',opacity:0}],{duration:340}).onfinish=()=>el.remove()},220);
  }else el.animate([{transform:'translate(-50%,-50%) scale(1.4)',opacity:0},{transform:'translate(-50%,-50%) scale(.85)',opacity:1,offset:.35},{transform:'translate(-50%,-50%) scale(.9)',opacity:0}],{duration:560}).onfinish=()=>el.remove();
 },delay);return true;
}

export function animateResolvePlayback(previous,battle,timeline,tokenFor){
 for(const unit of Object.values(battle.units||{})){
  const node=tokenFor(unit.id)?.querySelector('.captor-resolve');if(!node)continue;
  function paint(value){node.querySelector('meter').value=value;node.querySelector('small').textContent=value===0?'CAPTURE READY':`${value} RES`}
  paint(previous?.units?.[unit.id]?.resolve??unit.max_resolve);
  const rows=timeline.filter(r=>r.event.unit_id===unit.id&&r.event.kind==='resolve');
  for(const row of rows)setTimeout(()=>paint(row.event.resolve),row.start);
  if(!rows.length)paint(unit.resolve);
 }
}
