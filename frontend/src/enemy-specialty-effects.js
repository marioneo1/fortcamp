const ART={tripline:'tripline_hit',tripline_set:'tripline_prop',shakedown:'shakedown_hit',parting_cut:'parting_cut_hit',
 ankle_bite:'ankle_bite_hit',goliath_shot:'goliath_shot_hit',tag_team:'tag_team_hit',cornered_fury:'cornered_fury_hit',heel_cut:'heel_cut_hit',retreat:'retreat',stone:'stone'};
export function emitSpecialtyEffect(field,event,battle,delay){
 if(!event.skill?.startsWith('specialty_'))return false;
 const kind=event.skill.slice(10),art=ART[kind];if(!art)return false;
 setTimeout(()=>{
  if(!field.isConnected||document.hidden)return;
  const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
  if(kind==='retreat'&&event.from_point&&event.to_point){
   const trail=document.createElement('span'),from=event.from_point,to=event.to_point;
   const angle=Math.atan2(to.y-from.y,to.x-from.x)*180/Math.PI;
   Object.assign(trail.style,{position:'absolute',pointerEvents:'none',left:`${(from.x+.5+(to.x-from.x)*.22)/battle.width*100}%`,top:`${(from.y+.5+(to.y-from.y)*.22)/battle.height*100}%`,width:`${1.1/battle.width*100}%`,zIndex:'2'});
   // Neutral dirt and two boot scuffs, rather than a glowing magical footprint.
   trail.innerHTML='<svg viewBox="0 0 100 50" aria-hidden="true"><g fill="#baad8e"><ellipse cx="40" cy="17" rx="24" ry="7" opacity=".28"/><ellipse cx="38" cy="32" rx="20" ry="7" opacity=".22"/><circle cx="15" cy="9" r="2.4"/><circle cx="8" cy="30" r="1.8"/><circle cx="24" cy="43" r="2.1"/></g><g stroke="#67513a" stroke-width="3" stroke-linecap="round" opacity=".55"><path d="M27 17L73 19"/><path d="M26 32L68 33"/></g></svg>';
   layer.append(trail);
   const pose=s=>`translate(-50%,-50%) rotate(${angle}deg) scale(${s})`;
   const animation=trail.animate([{opacity:0,transform:pose(.35)},{opacity:.7,transform:pose(.8),offset:.35},{opacity:0,transform:pose(1.1)}],{duration:360,delay:30,easing:'ease-out',fill:'both'});
   animation.finished.then(()=>trail.remove(),()=>trail.remove());return;
  }
  const sprite=document.createElement('img');sprite.className='specialty-impact';sprite.src=`/assets/enemy-specialties-v1/${art}.png`;sprite.alt='';
  Object.assign(sprite.style,{position:'absolute',pointerEvents:'none',left:`${(event.x+.5)/battle.width*100}%`,top:`${(event.y+.5)/battle.height*100}%`,width:`${1.4/battle.width*100}%`,transform:'translate(-50%,-50%)',zIndex:'4'});
  layer.append(sprite);
  let frames=[{opacity:0,transform:'translate(-50%,-50%) scale(.65)'},{opacity:.95,offset:.25,transform:'translate(-50%,-50%) scale(1)'},{opacity:0,transform:'translate(-50%,-50%) scale(1.18)'}];
  if(kind==='stone'&&event.from_point){
   const r=field.getBoundingClientRect(),dx=(event.from_point.x-event.x)*r.width/battle.width,dy=(event.from_point.y-event.y)*r.height/battle.height;
   sprite.style.width=`${.55/battle.width*100}%`;
   frames=[{opacity:1,transform:`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px)) rotate(-20deg)`},{opacity:1,transform:'translate(-50%,-50%) rotate(160deg)'}];
  }
  const animation=sprite.animate(frames,{duration:kind==='stone'?220:480,easing:'ease-out',fill:'forwards'});
  animation.finished.then(()=>sprite.remove(),()=>sprite.remove());
 },delay);return true;
}

export function triplineArtwork(zone,x,y){
 const horizontal=zone.cells.every(c=>c.y===zone.cells[0].y);
 const w=Math.max(...zone.cells.map(c=>c.x))-x+1,h=Math.max(...zone.cells.map(c=>c.y))-y+1;
 const length=(horizontal?w:h)*100;
 // One continuous rope with two stakes across the complete footprint. Crop
 // the stray atlas edge in SVG without duplicating or editing the source PNG.
 const clip=`tripline-strip-${String(zone.id||'prop').replace(/[^a-z0-9-]/gi,'')}`,left=-length/2+16;
 const sx=(length-32)/232,sy=64/90;
 return `<g transform="translate(${w*50} ${h*50}) rotate(${horizontal?0:90})"><defs><clipPath id="${clip}"><rect x="${left}" y="-32" width="${length-32}" height="64"/></clipPath></defs><g clip-path="url(#${clip})"><image href="/assets/enemy-specialties-v1/tripline_prop.png" x="${left-24*sx}" y="${-32-88*sy}" width="${256*sx}" height="${256*sy}" preserveAspectRatio="none"/></g></g>`;
}
