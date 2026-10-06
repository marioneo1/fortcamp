// Cosmetic only: coordinates and contacts come from the resolved combat packet.
export function emitMonkTechnique(field,event,battle,delay){
 if(event.skill!=='heaven_piercing')return;
 const target=event.target_point||battle.units?.[event.target_id];if(!target)return;
 setTimeout(()=>{
  if(!field.isConnected||document.hidden)return;
  const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
  const effect=document.createElement('span');effect.className='monk-force-lance';
  const dx=target.x-event.x,dy=target.y-event.y,distance=Math.hypot(dx,dy);
  effect.style.left=`${(event.x+.5)/battle.width*100}%`;effect.style.top=`${(event.y+.5)/battle.height*100}%`;
  effect.style.width=`${Math.max(1,distance)/battle.width*100}%`;
  effect.style.height=`${field.clientWidth/battle.width*.9}px`;
  effect.style.transform=`translateY(-50%) rotate(${Math.atan2(dy,dx)*180/Math.PI}deg)`;
  effect.innerHTML='<img src="/assets/monk-v1/force_lance.png" alt="">';layer.append(effect);
  const animation=effect.animate([{opacity:0,scale:'.65 1'},{opacity:.9,scale:'1 1',offset:.36},{opacity:0,scale:'1.08 1'}],{duration:440,easing:'ease-out'});
  animation.onfinish=()=>effect.remove();animation.oncancel=()=>effect.remove();
 },delay+60);
}

export function monkAuraMarkup(unit){
 if(unit.alive===false||unit.conscious===false)return '';
 return (unit.statuses||[]).some(s=>s.id==='iron_reversal')?'<span class="monk-reversal-aura" aria-hidden="true"><img src="/assets/monk-v1/defensive_flow.png" alt=""></span>':'';
}
