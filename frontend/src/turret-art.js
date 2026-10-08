const root='/assets/tactical-props-v1/';
// Fetch the bolt before its short flight so the first shot is visible too.
const preloads=[];if(typeof Image!=='undefined')for(const src of [root+'turret_bolt.png','/assets/engineer-v1/bolt.png','/assets/engineer-v2/explosive_bolt.png']){const bolt=new Image();bolt.src=src;preloads.push(bolt)}
export function isTurret(unit){return unit?.entity_kind==='scrap_turret'||unit?.entity_kind==='heavy_emplacement'}
export function turretMarkup(unit,battle){
 const base=unit.engineer_machine?'/assets/engineer-v1/':root,prefix=unit.engineer_machine?(unit.machine_kind==='heavy_emplacement'?'heavy_':'sentry_'):'turret_';
 const owner=battle?.units?.[unit.operator_id];
 const unfinished=unit.alive!==false&&unit.under_construction;
 return `<span class="turret-body ${owner?.overclock_until!=null?'engineer-overclock':''} ${unit.machine_fading?'machine-fading':''}" aria-hidden="true">${unfinished?`<img class="turret-frame turret-idle" src="/assets/engineer-v2/${prefix}unfinished.png" alt="" draggable="false"><b class="engineer-building-label">Building</b>`:(unit.alive===false?['destroyed']:['idle','fire','recoil']).map(frame=>`<img class="turret-frame turret-${frame}" src="${base}${prefix}${frame}.png" alt="" draggable="false">`).join('')}${owner?.portrait?`<img class="engineer-operator" src="${owner.portrait}" alt="Operator" draggable="false">`:owner?'<span class="engineer-operator">OP</span>':''}</span>`;
}
export function turretBearing(from,to){return Math.atan2(to.y-from.y,to.x-from.x)*180/Math.PI+90}
export function emitTurretAttack(field,event,battle,delay=0,tokenFor=null){
 const actor=battle.units?.[event.attacker_id];if(!isTurret(actor)||!event.from||!event.to)return;
 const body=()=>tokenFor?.(event.attacker_id)?.querySelector('.turret-body')||field.querySelector(`[data-battle-unit="${event.attacker_id}"] .turret-body`);
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const schedule=(offset,fn)=>setTimeout(()=>{if(field?.isConnected&&!document.hidden)fn()},delay+offset);
 schedule(0,()=>{const token=body();if(token){token.style.setProperty('--turret-bearing',turretBearing(event.from,event.to)+'deg');if(!reduced)token.dataset.frame='fire'}});
 schedule(45,()=>{
  const token=body();if(token&&!reduced)token.dataset.frame='recoil';if(reduced)return;
  const cw=field.clientWidth/battle.width,ch=field.clientHeight/battle.height,dx=(event.to.x-event.from.x)*cw,dy=(event.to.y-event.from.y)*ch;
  const bolt=document.createElement('img');bolt.className='turret-projectile';bolt.src=actor.machine_kind==='heavy_emplacement'?'/assets/engineer-v2/explosive_bolt.png':actor.engineer_machine?'/assets/engineer-v1/bolt.png':root+'turret_bolt.png';bolt.style.cssText=`left:${(event.from.x+.5)*cw}px;top:${(event.from.y+.5)*ch}px;width:${cw*.3}px;height:${ch*.65}px`;field.append(bolt);
  const angle=turretBearing(event.from,event.to),motion=bolt.animate([{transform:`translate(-50%,-50%) rotate(${angle}deg)`,opacity:1},{transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) rotate(${angle}deg)`,opacity:1}],{duration:175,fill:'both'});motion.onfinish=motion.oncancel=()=>bolt.remove();
 });
 schedule(350,()=>{const token=body();if(token)delete token.dataset.frame});
}
