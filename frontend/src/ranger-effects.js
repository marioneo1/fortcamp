const root='/assets/ranger-v1/';
// Share the attack packet's contact time; projectile flight does not advance turns.
export function emitRangerEffect(field,event,battle,delay=0){
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const schedule=(ms,fn)=>setTimeout(()=>{if(field?.isConnected&&!document.hidden)fn()},delay+ms);
 const sprite=(name,at,size,frames,duration)=>{
  const cw=field.clientWidth/battle.width,ch=field.clientHeight/battle.height;
  const el=document.createElement('img');el.className='rogue-effect-sprite';el.src=root+name+'.png';
  el.style.cssText=`left:${(at.x+.5)*cw}px;top:${(at.y+.5)*ch}px;width:${cw*size}px;height:${ch*size}px;pointer-events:none;z-index:90`;
  field.append(el);const animation=el.animate(reduced?[{opacity:.8,transform:'translate(-50%,-50%)'},{opacity:0,transform:'translate(-50%,-50%)'}]:frames,{duration,fill:'both'});animation.onfinish=animation.oncancel=()=>el.remove();
 };
 const pulse=(name,at,size=1.1)=>sprite(name,at,size,[{opacity:0,transform:'translate(-50%,-50%) scale(.55)'},{opacity:.85,transform:'translate(-50%,-50%) scale(1)',offset:.25},{opacity:0,transform:'translate(-50%,-50%) scale(1.2)'}],420);
 if(!event.attack_event){const unit=battle.units?.[event.unit_id];if(unit)schedule(0,()=>pulse(event.status_id==='mark'?'quarry_ring':'steady_ring',unit));return}
 if(!event.from||!event.to)return;
 const poison=event.ranger_poison||['poison_attack','pestilence_shot','rupturing_blow'].includes(event.ranger_skill);
 schedule(30,()=>{
  const cw=field.clientWidth/battle.width,ch=field.clientHeight/battle.height,dx=(event.to.x-event.from.x)*cw,dy=(event.to.y-event.from.y)*ch,angle=Math.atan2(dy,dx)*180/Math.PI;
  sprite(poison?'poison_arrow':'arrow',event.from,.8,[{opacity:1,transform:`translate(-50%,-50%) rotate(${angle}deg)`},{opacity:1,transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) rotate(${angle}deg)`},{opacity:0,transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) rotate(${angle}deg)`}],190);
 });
 if(event.hit&&(poison||event.critical))schedule(220,()=>pulse(event.ranger_skill==='rupturing_blow'?'rupture_burst':poison?'poison_contact':'critical_spark',event.to,poison?1:1.2));
}
