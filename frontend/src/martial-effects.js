// Alpha-sprite effects follow resolved packets; no second combat simulation.
export const MARTIAL_EFFECTS={brace:'protection',second_wind:'restoration',victory_strike:'force',
 reckless_blow:'force',skullbreaker:'force',death_defiance:'force',bloodthirst:'restoration',unstoppable:'protection'};
export function martialAuraMarkup(unit){
 if(unit.alive===false||unit.conscious===false)return '';
 const ids=new Set((unit.statuses||[]).map(s=>s.id));
 return `${ids.has('brace_defense')?'<span class="martial-aura brace-aura" aria-hidden="true"><img src="/assets/martial-jobs-v1/protection-3.png" alt=""></span>':''}${ids.has('death_defiance')?'<span class="martial-aura defiance-aura" aria-hidden="true"><img src="/assets/martial-jobs-v1/force-3.png" alt=""></span>':''}`;
}
export function emitMartialEffect(field,event,battle,delay){
 const family=MARTIAL_EFFECTS[event.skill];if(!family)return;
 setTimeout(()=>{
  if(!field.isConnected||document.hidden)return;
  const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
  const effect=document.createElement('span');effect.className='martial-effect';
  effect.style.left=`${(event.x+.5)/battle.width*100}%`;effect.style.top=`${(event.y+.5)/battle.height*100}%`;
  effect.style.width=`${1.7/battle.width*100}%`;
  effect.innerHTML=Array.from({length:4},(_,i)=>`<img src="/assets/martial-jobs-v1/${family}-${i+1}.png" alt="" style="opacity:0">`).join('');layer.append(effect);
  const images=[...effect.children],begin=performance.now(),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const tick=()=>{
   const p=Math.min(1,(performance.now()-begin)/560);
   if(!effect.isConnected||p>=1){effect.remove();return}
   const phase=reduced?2:Math.min(3,Math.floor(p*4));
   images.forEach((image,i)=>image.style.opacity=i===phase?String(Math.sin(p*Math.PI)*.72):'0');
   effect.style.transform=`translate(-50%,-50%) scale(${reduced?1:.7+p*.45})`;
   requestAnimationFrame(tick);
  };tick();
 },delay);
}
