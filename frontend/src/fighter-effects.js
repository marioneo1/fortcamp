// Short, resolved action effects. No persistent ground tiles or opaque ground panels.
export function fighterEffectMarkup(event,battle){
 const x=(event.x+.5)/battle.width*100,y=(event.y+.5)/battle.height*100;
 if(event.type==='ground_impact')return `<div class="fighter-ground-impact" style="left:${x}%;top:${y}%;width:${(event.radius*2+1)/battle.width*100}%"><img src="/assets/combat-fighter-v3/earth-impact.png" alt=""><i></i></div>`;
 if(event.type==='fighter_rally')return `<div class="fighter-rally-wave" style="left:${x}%;top:${y}%;width:${(event.radius*2+1)/battle.width*100}%"></div>`;
 if(event.type==='chain_attack'){
  const a=event.from_point,b=event.to_point;
  if(!a||!b)return '';
  return `<svg class="fighter-chain" viewBox="0 0 ${battle.width*100} ${battle.height*100}" preserveAspectRatio="none"><line class="chain-shadow" x1="${(a.x+.5)*100}" y1="${(a.y+.5)*100}" x2="${(b.x+.5)*100}" y2="${(b.y+.5)*100}"/><line class="chain-links" x1="${(a.x+.5)*100}" y1="${(a.y+.5)*100}" x2="${(b.x+.5)*100}" y2="${(b.y+.5)*100}"/><circle cx="${(b.x+.5)*100}" cy="${(b.y+.5)*100}" r="13"/><image href="/assets/combat-fighter-v3/chain-effect.png" x="${(b.x+.5)*100-20}" y="${(b.y+.5)*100-20}" width="40" height="40"/></svg>`;
 }
 return '';
}
export function emitFighterEffect(field,event,battle,delay){
 const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
 const markup=fighterEffectMarkup(event,battle);if(!markup)return;
 setTimeout(()=>{
  if(!layer.isConnected||document.hidden)return;
  const holder=document.createElement('div');holder.className='fighter-action-effect';holder.innerHTML=markup;layer.append(holder);
  setTimeout(()=>holder.remove(),event.type==='chain_attack'?420:700);
 },delay);
}
