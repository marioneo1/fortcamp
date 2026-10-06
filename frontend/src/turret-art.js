const root='/assets/tactical-props-v1/';
// Fetch the bolt before its short flight so the first shot is visible too.
const preloads=[];if(typeof Image!=='undefined'){const bolt=new Image();bolt.src=root+'turret_bolt.png';preloads.push(bolt)}
export function isTurret(unit){return unit?.entity_kind==='scrap_turret'}
export function turretMarkup(unit){return `<span class="turret-body" aria-hidden="true">${(unit.alive===false?['destroyed']:['idle','fire','recoil']).map(frame=>`<img class="turret-frame turret-${frame}" src="${root}turret_${frame}.png" alt="" draggable="false">`).join('')}</span>`}
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
  const bolt=document.createElement('img');bolt.className='turret-projectile';bolt.src=root+'turret_bolt.png';bolt.style.cssText=`left:${(event.from.x+.5)*cw}px;top:${(event.from.y+.5)*ch}px;width:${cw*.2}px;height:${ch*.55}px`;field.append(bolt);
  const angle=turretBearing(event.from,event.to),motion=bolt.animate([{transform:`translate(-50%,-50%) rotate(${angle}deg)`,opacity:1},{transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) rotate(${angle}deg)`,opacity:1}],{duration:175,fill:'both'});motion.onfinish=motion.oncancel=()=>bolt.remove();
 });
 schedule(350,()=>{const token=body();if(token)delete token.dataset.frame});
}
