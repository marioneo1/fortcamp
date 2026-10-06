// Presentation only: generated materials never decide damage or status duration.
export const FROZEN_ROOT='/assets/mage-frozen-v2/';
export const SCORCH_ROOT='/assets/mage-scorched-v2/';
let frozenWarm=false;
export function warmFrozenSurfaces(){
 if(frozenWarm||typeof Image==='undefined')return;frozenWarm=true;
 for(const kind of ['freeze','frozen','break','thaw'])for(let i=1;i<=4;i++){const image=new Image();image.src=`${FROZEN_ROOT}${kind}_${i}.png`}
}
export function surfaceSeed(value){let h=2166136261;for(const c of String(value)){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}
export function elementalFrozen(unit){return !!unit?.statuses?.some(s=>s.id==='freeze'&&s.elemental_freeze)}
export function frozenMarkup(unit){
 if(!elementalFrozen(unit)||unit.alive===false||unit.conscious===false)return '';
 return `<span class="mage-ice-shell" aria-hidden="true" style="--ice-surface:url('${FROZEN_ROOT}frozen_${surfaceSeed(unit.id)%4+1}.png')"><span class="ice-surface"></span><span class="ice-glint"></span></span>`;
}
export function frozenTransitionPlan(previous,battle,timeline){
 const plans=[];
 for(const [id,unit] of Object.entries(battle.units||{})){
  const before=elementalFrozen(previous?.units?.[id]),after=elementalFrozen(unit);
  if(before===after)continue;
  const relevant=timeline.filter(r=>r.event.unit_id===id&&r.event.type==='combat_feedback');
  const application=relevant.find(r=>r.event.kind==='status'&&r.event.status_id==='freeze');
  const hit=relevant.find(r=>r.event.amount>0&&['physical','magic','fire','lightning','collision','restraint'].includes(r.event.kind));
  plans.push({id,mode:after?'freeze':hit?'break':'thaw',delay:Math.max(0,(after?application:hit)?.start||0)});
 }
 return plans;
}
export function animateFrozenTransitions(previous,battle,timeline,tokenFor){
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const plans=frozenTransitionPlan(previous,battle,timeline);if(plans.length)warmFrozenSurfaces();
 for(const plan of plans){
  const token=tokenFor(plan.id);if(!token)continue;
  const persistent=token.querySelector('.mage-ice-shell');
  if(plan.mode==='freeze'&&persistent)persistent.style.visibility='hidden';
  const overlay=document.createElement('span');overlay.className='mage-ice-transition';overlay.setAttribute('aria-hidden','true');
  // The old surface remains present until the damage contact that actually breaks it.
  if(plan.mode!=='freeze'){overlay.style.backgroundImage=`url('${FROZEN_ROOT}frozen_1.png')`;token.append(overlay)}
  setTimeout(()=>{
   if(!token.isConnected){overlay.remove();return}
   if(reduced||document.hidden){overlay.remove();if(persistent)persistent.style.visibility='';return}
   if(!overlay.isConnected)token.append(overlay);
   const interval=plan.mode==='thaw'?160:85;
   for(let i=0;i<4;i++)setTimeout(()=>{
    if(!token.isConnected){overlay.remove();return}
    overlay.style.backgroundImage=`url('${FROZEN_ROOT}${plan.mode}_${i+1}.png')`;
    overlay.style.opacity=plan.mode==='freeze'?'.76':String(.8-i*.1);
    if(plan.mode==='break')overlay.style.transform=`scale(${1+i*.09})`;
   },i*interval);
   setTimeout(()=>{overlay.remove();if(persistent?.isConnected)persistent.style.visibility=''},4*interval);
  },plan.delay);
 }
}
export function scorchedArtwork(zone,x,y,width,height,clip){
 const mask=clip+'-scorch-soft',blur=clip+'-scorch-blur';
 const rects=zone.cells.map(c=>`<rect x="${(c.x-x)*100}" y="${(c.y-y)*100}" width="100" height="100" fill="white"/>`).join('');
 const image=(name,px,py,size,cls,angle=0)=>`<image href="${SCORCH_ROOT}${name}.png" x="${px}" y="${py}" width="${size}" height="${size}" preserveAspectRatio="xMidYMid meet" class="${cls}" transform="rotate(${angle} ${px+size/2} ${py+size/2})"/>`;
 let artwork='';
 for(const c of zone.cells){
  const seed=surfaceSeed(`${c.x}:${c.y}:scorch`),px=(c.x-x)*100,py=(c.y-y)*100;
  const soot=image(`soot_${seed%4+1}`,px-28,py-28,156,'scorch-soot',seed%360);
  const ash=seed%3!==0?image(`ash_${(seed>>>4)%4+1}`,px+8,py+5,84,'scorch-ash',(seed>>>8)%360):'';
  const fire=`<foreignObject x="${px-28}" y="${py-28}" width="156" height="156"><div xmlns="http://www.w3.org/1999/xhtml" class="scorch-flame scorch-main-flame" style="animation-duration:${1700+seed%500}ms;animation-delay:-${seed%2000}ms"></div></foreignObject>`;
  artwork+=`<g data-scorch-cell="${c.x},${c.y}"><g class="scorch-ground">${soot}${ash}</g>${fire}</g>`;
 }
 return `<defs><filter id="${blur}" x="-10%" y="-10%" width="120%" height="120%"><feMorphology operator="erode" radius="8"/><feGaussianBlur stdDeviation="7"/></filter><mask id="${mask}" maskUnits="userSpaceOnUse" x="0" y="0" width="${width*100}" height="${height*100}" style="mask-type:alpha"><g filter="url(#${blur})">${rects}</g></mask></defs><g mask="url(#${mask})">${artwork}</g>`;
}

// New ground is revealed at its actual spell contact, even though the API returns final state.
export function scorchedRevealPlan(previous,timeline){
 const seen=new Set((previous?.zones||[]).filter(z=>z.kind==='scorched').flatMap(z=>z.cells.map(c=>`${c.x},${c.y}`))),plans=[];
 for(const {event,start} of timeline){
  if(event.type!=='zone_created')continue;
  for(const c of event.cells||[]){const key=`${c.x},${c.y}`;if(!seen.has(key)){plans.push({key,delay:start});seen.add(key)}}
 }
 return plans;
}
export function animateScorchedTransitions(previous,timeline,field){
 for(const plan of scorchedRevealPlan(previous,timeline)){
  for(const node of field.querySelectorAll(`[data-scorch-cell="${plan.key}"]`)){
   node.style.visibility='hidden';
   setTimeout(()=>{if(node.isConnected)node.style.visibility=''},Math.max(0,plan.delay));
  }
 }
}
