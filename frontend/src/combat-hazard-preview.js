const ART='/assets/combat-navigation-v1/';
export function movementHazardMarkup(warning,escape){
 if(!warning)return '';
 const names={burn:'Burn',bleed:'Bleed',poison:'Poison',hobbled:'Hobble',bind:'Bind'};
 const effects=Object.entries(warning.effects||{}).map(([id,e])=>id==='engineer_disruption'?'Mine: stops movement and interrupts attacks':`${escape(names[id]||id)} ${e.chance<100?'up to ':''}+${e.stacks}${e.chance<100?` (${e.chance}% per entry)`:''}${['bleed','poison'].includes(id)?' &middot; hurts at turn end':id==='burn'?' &middot; also ticks at turn end':''}`);
 return `<img src="${ART}hazard.png" alt=""><div><strong>${warning.lethal?'Lethal route risk':warning.damage?`${warning.uncertain?'Up to ':''}${warning.damage} HP damage on this path`:'Hazards on this path'}</strong>${effects.map(text=>`<span>${text}</span>`).join('')}<small>Final path from START &middot; applied when you commit an action</small></div>`;
}
export function bindMovementHazards(field,battle,mode,escape,blocked=()=>false){
 if(!field)return;
 field._hazardBindings?.abort();const bindings=new AbortController();field._hazardBindings=bindings;
 const nodes=new Map((battle.movement_tree||[]).map(n=>[`${n.x},${n.y}`,n]));
 const viewport=field.closest('.battle-viewport'),host=viewport.closest('.battle-map-stage');
 host.querySelector('.movement-hazard-card')?.remove();
 const card=document.createElement('aside');card.className='movement-hazard-card';card.setAttribute('aria-live','polite');card.hidden=true;host.append(card);
 const position=()=>{if(!field.isConnected){resize.disconnect();card.remove();return}const r=viewport.getBoundingClientRect(),h=host.getBoundingClientRect();card.style.left=(r.left-h.left+10)+'px';card.style.top=(r.bottom-h.top-card.offsetHeight-10)+'px'};
 const resize=new ResizeObserver(position);resize.observe(viewport);bindings.signal.addEventListener('abort',()=>resize.disconnect(),{once:true});
 let last=null;
 const paint=warning=>{
  if(warning===last)return;last=warning;
  field.querySelectorAll('.hazard-path-preview').forEach(c=>c.classList.remove('hazard-path-preview'));
  card.hidden=!warning;card.innerHTML=movementHazardMarkup(warning,escape);
  position();
  for(const p of warning?.cells||[])field.querySelector(`[data-battle-cell="${p.x},${p.y}"]`)?.classList.add('hazard-path-preview');
 };
 const selected=()=>{const actor=battle.units?.[battle.current_unit_id];return mode()==='move'&&!blocked()?nodes.get(`${actor?.x},${actor?.y}`)?.hazard_forecast:null};
 host.querySelectorAll('.movement-hazard-card').forEach(c=>{if(c!==card)c.remove()});
 field.addEventListener('pointermove',e=>{
  if(mode()!=='move'||blocked()||e.buttons===2){paint(null);return}
  const r=field.getBoundingClientRect(),x=Math.floor((e.clientX-r.left)/r.width*battle.width),y=Math.floor((e.clientY-r.top)/r.height*battle.height);
  paint(nodes.get(`${x},${y}`)?.hazard_forecast||null);
 },{signal:bindings.signal});
 field.addEventListener('pointerleave',()=>paint(selected()),{signal:bindings.signal});paint(selected());
}
