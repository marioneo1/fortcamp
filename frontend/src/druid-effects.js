export const DRUID_EFFECTS={druid_prowler:['transform',.8,'#96c865'],druid_bulwark:['transform',1.1,'#cdab69'],
 druid_rat:['transform',.6,'#c6d3bb'],druid_normal:['transform',1,'#92d899'],druid_growth:['restoration',1,'#91e8a3']};
export function emitDruidForm(field,event,battle,delay){
 const profile=DRUID_EFFECTS[event.skill];if(!profile)return false;
 setTimeout(()=>{
  if(!field.isConnected||document.hidden)return;
  const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
  const ring=document.createElement('span');ring.className='druid-transformation';
  ring.style.cssText=`left:${(event.x+.5)/battle.width*100}%;top:${(event.y+.5)/battle.height*100}%;width:${1.7/battle.width*100}%;--druid-tint:${profile[2]}`;
  ring.innerHTML=`<img src="/assets/druid-v1/${profile[0]}.png" alt="">`;layer.append(ring);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  ring.animate(reduced?[{opacity:0},{opacity:.75},{opacity:0}]:[
   {opacity:0,transform:`translate(-50%,-50%) scale(.35) rotate(-35deg)`},
   {opacity:.9,transform:`translate(-50%,-50%) scale(${profile[1]}) rotate(15deg)`,offset:.45},
   {opacity:0,transform:`translate(-50%,-50%) scale(${profile[1]*1.35}) rotate(55deg)`}],
   {duration:560,easing:'ease-out'}).finished.then(()=>ring.remove(),()=>ring.remove());
 },delay);return true;
}
export function emitDruidLash(field,event,battle,delay){
 setTimeout(()=>{
  if(!field.isConnected||document.hidden)return;
  const layer=field.querySelector('.combat-feedback-layer');if(!layer)return;
  const frame=field.getBoundingClientRect(),dx=(event.to.x-event.from.x)*frame.width/battle.width,dy=(event.to.y-event.from.y)*frame.height/battle.height;
  const vine=document.createElement('span');vine.className='druid-vine-lash';
  vine.style.cssText=`left:${(event.from.x+.5)/battle.width*100}%;top:${(event.from.y+.5)/battle.height*100}%;width:${Math.hypot(dx,dy)}px;height:${frame.height/battle.height*.7}px;transform:translateY(-50%) rotate(${Math.atan2(dy,dx)}rad)`;
  vine.innerHTML='<img src="/assets/druid-v1/vine_lash.png" alt="">';layer.append(vine);
  const image=vine.firstElementChild;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  image.animate(reduced?[{opacity:0},{opacity:1,offset:.44},{opacity:0}]:[{transform:'scaleX(.12)',opacity:0},{transform:'scaleX(1)',opacity:1,offset:.44},{transform:'scaleX(.2)',opacity:0}],
   {duration:500,easing:'ease-in-out'}).finished.then(()=>vine.remove(),()=>vine.remove());
  const tile=Array.from(field.querySelectorAll('[data-battle-terrain]')).find(t=>t.dataset.battleTerrain===event.terrain_id);
  if(tile&&!reduced){
   const original=tile.style.getPropertyValue('--battle-prop');
   const frames=['bramble_ready','bramble_lash','bramble_settle'];
   frames.forEach((name,i)=>setTimeout(()=>{if(tile.isConnected)tile.style.setProperty('--battle-prop',`url('/assets/druid-v1/${name}.png')`)},i*140));
   setTimeout(()=>{if(tile.isConnected)tile.style.setProperty('--battle-prop',original)},500);
  }
 },delay);
}
