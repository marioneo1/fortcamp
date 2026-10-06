import {impactTimeline} from './combat-impact.js';
// The hook stays attached through the target's actual push/pull and rebound.
export function chainLifetime(event,events){
 const rows=impactTimeline(events),cast=rows.find(r=>r.event.type==='chain_attack'&&r.event.attack_packet===event.attack_packet);
 const start=cast?.start||0;
 const end=Math.max(start+400,...rows.filter(r=>r.event.attack_packet===event.attack_packet&&
  ['movement','collision_recoil'].includes(r.event.type)).map(r=>r.start+r.duration));
 return end-start+120;
}
export function chainTravel(from,to,elapsed){
 const progress=Math.max(0,Math.min(1,elapsed/220));
 return {x:from.x+(to.x-from.x)*progress,y:from.y+(to.y-from.y)*progress};
}
export function displacementPreviewMarkup(preview,battle,escape){
 return (preview?.tactics||[]).map(effect=>{
  const p=effect.destination;if(!p)return '';
  const marker=(point,label,kind='')=>`<span class="displacement-preview-label ${kind}" style="left:${(point.x+.5)/battle.width*100}%;top:${(point.y+.85)/battle.height*100}%">${escape(label)}</span>`;
  const destination=marker(p,`${effect.type==='pull'?'PULL':'PUSH'} ENDS HERE`);
  const collision=effect.solid_collision&&effect.collision_cell?marker(effect.collision_cell,
   `IMPACT +${effect.collision_damage||0}${effect.collision_target_name?` / ${effect.collision_target_name} ${effect.bystander_damage||0}`:''}`,'collision'):'';
  return destination+collision;
 }).join('');
}
// Short, resolved action effects. No persistent ground tiles or opaque ground panels.
export function fighterEffectMarkup(event,battle){
 const x=(event.x+.5)/battle.width*100,y=(event.y+.5)/battle.height*100;
 if(event.type==='ground_impact'&&event.effect_art==='groundbreaker')return `<div class="fighter-ground-impact martial-ground-impact" style="left:${x}%;top:${y}%;width:${3/battle.width*100}%">${Array.from({length:4},(_,i)=>`<img class="ground-phase phase-${i}" src="/assets/martial-jobs-v1/groundbreaker-${i+1}.png" alt="">`).join('')}</div>`;
 if(event.type==='ground_impact')return `<div class="fighter-ground-impact" style="left:${x}%;top:${y}%;width:${(event.radius*2+1)/battle.width*100}%"><img src="/assets/combat-fighter-v3/earth-impact.png" alt=""><i></i></div>`;
 if(event.type==='fighter_rally')return `<div class="fighter-rally-wave" style="left:${x}%;top:${y}%;width:${(event.radius*2+1)/battle.width*100}%"></div>`;
 if(event.type==='chain_attack'){
  const a=event.from_point,b=event.to_point;
  if(!a||!b)return '';
  return `<svg class="fighter-chain" viewBox="0 0 ${battle.width*100} ${battle.height*100}" preserveAspectRatio="none"><line class="chain-shadow"/><line class="chain-metal"/><line class="chain-links"/><g class="chain-hook"><image href="/assets/combat-controls-v2/chain_hook.png" x="-44" y="-24" width="48" height="48"/></g></svg>`;
 }
 return '';
}
export function emitFighterEffect(field,event,battle,delay,events=battle.animation_events||[event]){
 const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
 const markup=fighterEffectMarkup(event,battle);if(!markup)return;
 setTimeout(()=>{
  if(!layer.isConnected||document.hidden)return;
  const holder=document.createElement('div');holder.className='fighter-action-effect';holder.innerHTML=markup;layer.append(holder);
  if(event.type==='chain_attack'){
   const lifetime=chainLifetime(event,events),begin=performance.now();
   const target=field.querySelector(`[data-battle-unit="transition-${CSS.escape(event.target_id)}"]`)||field.querySelector(`[data-battle-unit="${CSS.escape(event.target_id)}"]`);
   const lines=[...holder.querySelectorAll('line')],hook=holder.querySelector('.chain-hook');
   const origin={x:(event.from_point.x+.5)*100,y:(event.from_point.y+.5)*100};
   const initial={x:(event.to_point.x+.5)*100,y:(event.to_point.y+.5)*100};
   const tick=()=>{
    if(!holder.isConnected||!field.isConnected){holder.remove();return}
    const elapsed=performance.now()-begin;if(elapsed>=lifetime){holder.remove();return}
    let destination=initial;
    if(event.hit&&elapsed>=220&&target?.isConnected){const box=field.getBoundingClientRect(),r=target.getBoundingClientRect();destination={x:((r.left+r.right)/2-box.left)/box.width*battle.width*100,y:((r.top+r.bottom)/2-box.top)/box.height*battle.height*100}}
    let point=chainTravel(origin,destination,elapsed);
    if(!event.hit&&elapsed>220)point=chainTravel(initial,origin,(elapsed-220)/180*220);
    for(const line of lines){line.setAttribute('x1',origin.x);line.setAttribute('y1',origin.y);line.setAttribute('x2',point.x);line.setAttribute('y2',point.y)}
    hook.setAttribute('transform',`translate(${point.x} ${point.y}) rotate(${Math.atan2(point.y-origin.y,point.x-origin.x)*180/Math.PI})`);
    holder.style.opacity=String(Math.min(1,(lifetime-elapsed)/120));
    requestAnimationFrame(tick);
   };tick();
  }else setTimeout(()=>holder.remove(),700);
 },delay);
}
