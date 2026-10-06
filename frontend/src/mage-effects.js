// Painted Mage assets use the same contact clock as damage and forced movement.
import {frozenMarkup,warmFrozenSurfaces} from './mage-surfaces.js';
const root='/assets/mage-v1/';
export const MAGE_ELEMENTS=[{id:'fire',name:'Fire',description:'One Burn stack per weapon hit.'},{id:'frost',name:'Frost',description:'20% Freeze chance per hit; later hits break the ice.'},{id:'lightning',name:'Lightning',description:'25% Paralysis chance against Wet; once successfully per target.'}];
export function enchantCommand(command,element){if(!MAGE_ELEMENTS.some(e=>e.id===element))throw Error('Choose a supported element');return {...command,element}}
export function chooseEnchant({view,command,send,cancel,escape,blocked}){
 const host=document.querySelector('.battle-map-stage'),viewport=document.getElementById('battle-viewport');if(!host||!viewport)return;
 host.querySelector('.mage-element-prompt')?.remove();
 const popup=document.createElement('div');popup.className='rogue-map-prompt mage-element-prompt';
 const target=view.units?.[command.target_id],r=viewport.getBoundingClientRect(),h=host.getBoundingClientRect();popup.style.cssText=`left:${r.left-h.left}px;top:${r.top-h.top}px;width:${r.width}px;height:${r.height}px`;
 popup.innerHTML=`<section role="dialog" aria-label="Choose weapon enchantment" class="rogue-prompt-card mage-enchant-card"><small>ENCHANT WEAPON</small><h3>${escape(target?.name||'Ally')}'s enchantment</h3><p>Choose the element. Selecting one casts the spell.</p><div class="mage-element-choices">${MAGE_ELEMENTS.map(e=>`<button data-mage-element="${e.id}" class="element-${e.id}"><b>${e.name}</b><small>${escape(e.description)}</small></button>`).join('')}</div><button data-mage-cancel>Cancel</button></section>`;
 const close=()=>{popup.remove()},key=e=>{if(e.key==='Escape'||e.key.toLowerCase()==='c'){e.preventDefault();e.stopImmediatePropagation();close();cancel?.()}};
 for(const btn of popup.querySelectorAll('[data-mage-element]'))btn.onclick=()=>{if(blocked?.()||!popup.isConnected)return;const result=enchantCommand(command,btn.dataset.mageElement);close();send(result)};
 popup.querySelector('[data-mage-cancel]').onclick=()=>{close();cancel?.()};popup.addEventListener('keydown',key);host.append(popup);popup.querySelector('button')?.focus();return close;
}
export function mageStatusMarkup(unit){
 if(unit.alive===false||unit.conscious===false)return '';
 const has=id=>unit.statuses?.some(s=>s.id===id);
 return `${frozenMarkup(unit)}${has('wet')?'<span class="mage-wet-rim" aria-hidden="true"></span>':''}${has('channeling')?'<span class="mage-channel-orbit" aria-hidden="true"></span>':''}`;
}
export function emitMageEffect(field,event,battle,delay=0){
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const at={x:event.x,y:event.y},cw=field.clientWidth/battle.width,ch=field.clientHeight/battle.height;
 const sprite=(name,where,size,frames,ms)=>{
  if(!field.isConnected||document.hidden)return;
  const img=document.createElement('img');img.src=root+name+'.png';img.className='mage-effect';img.setAttribute('aria-hidden','true');img.style.cssText=`left:${(where.x+.5)*cw}px;top:${(where.y+.5)*ch}px;width:${cw*size}px;height:${ch*size}px`;
  field.append(img);const animation=img.animate(reduced?[{opacity:.8,transform:'translate(-50%,-50%)'},{opacity:0,transform:'translate(-50%,-50%)'}]:frames,{duration:ms,fill:'both'});animation.onfinish=animation.oncancel=()=>img.remove();
 };
 const later=(ms,fn)=>setTimeout(fn,Math.max(0,delay+ms));
 const pulse=(name,size=1.3,spin=0)=>sprite(name,at,size,[{opacity:.9,transform:'translate(-50%,-50%) scale(.8)'},{opacity:.95,offset:.15,transform:'translate(-50%,-50%) scale(1)'},{opacity:0,transform:`translate(-50%,-50%) scale(1.15) rotate(${spin}deg)`}],550);
 const k=event.mage_skill,contact=event.contact_ms??240;
 if(k==='flash_freeze_armed'||(k==='enchant_weapon'&&event.enchant_element==='frost'))warmFrozenSurfaces();
 if(k==='chain_lightning'){
  later(contact-80,()=>{if(!field.isConnected||document.hidden)return;const from=event.from_point,dx=(at.x-from.x)*cw,dy=(at.y-from.y)*ch,angle=Math.atan2(dy,dx)*180/Math.PI;
   const img=document.createElement('img');img.src=root+'lightning_arc.png';img.className='mage-effect mage-lightning';img.style.cssText=`left:${(from.x+.5)*cw+dx/2}px;top:${(from.y+.5)*ch+dy/2}px;width:${Math.max(cw*.65,Math.hypot(dx,dy))}px;height:${ch*.7}px;--bolt-angle:${angle}deg`;field.append(img);const animation=img.animate(reduced?[{opacity:.8},{opacity:0}]:[{opacity:0},{opacity:1,offset:.15},{opacity:.25,offset:.4},{opacity:.95,offset:.55},{opacity:0}],{duration:280,fill:'both'});animation.onfinish=animation.oncancel=()=>img.remove();
  });return;
 }
 if(k==='fireball')later(0,()=>{const from=event.from_point,dx=(at.x-from.x)*cw,dy=(at.y-from.y)*ch;sprite('fire_contact',from,.8,[{opacity:0,transform:'translate(-50%,-50%) scale(.35)'},{opacity:.95,offset:.2,transform:'translate(-50%,-50%) scale(.7)'},{opacity:1,offset:.95,transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) scale(.8)`},{opacity:0,transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) scale(.8)`}],contact)});
 if(k==='meteor')later(0,()=>sprite('meteor_rock',at,2.5,[{opacity:0,transform:'translate(-130%,-210%) scale(.45)'},{opacity:1,offset:.15,transform:'translate(-120%,-185%) scale(.7)'},{opacity:1,offset:.9,transform:'translate(-50%,-50%) scale(1)'},{opacity:0,transform:'translate(-50%,-50%) scale(1.05)'}],contact));
 if(k.endsWith('_armed')){later(contact,()=>pulse(k==='meteor_armed'?'gravity_vortex':'frost_ground',2.2,15));return}
 later(contact,()=>pulse(k==='meteor'||k==='fireball'?'fire_contact':k==='flash_freeze'?'frost_ground':k==='singularity'?'gravity_vortex':k==='typhoon'?'wind_ring':event.enchant_element==='fire'?'fire_contact':event.enchant_element==='frost'?'frost_ground':'lightning_arc',k==='enchant_weapon'?1.2:(event.radius||1)*2+1,k==='typhoon'?100:k==='singularity'?70:0));
}
