import {playbackDuration} from './combat-playback.js';
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
 const active=elementalFrozen(unit);
 if(!active||unit?.alive===false||unit?.conscious===false)return '';
 return `<span class="mage-ice-shell" aria-hidden="true" style="--ice-surface:url('${FROZEN_ROOT}frozen_${surfaceSeed(unit.id)%4+1}.png')"><span class="ice-surface"></span><span class="ice-glint"></span></span>`;
}
export function frozenTransitionPlan(previous,battle,timeline){
 const plans=[],end=Math.max(playbackDuration(timeline),...timeline.map(r=>r.start),0);
 for(const [id,unit] of Object.entries(battle.units||{})){
  let active=elementalFrozen(previous?.units?.[id]),onset=null;
  const change=(next,delay,mode)=>{if(next===active)return;if(!next&&mode==='thaw'&&onset!==null)delay=Math.max(delay,onset+500);plans.push({id,mode:next?'freeze':mode,delay:Math.max(0,delay)});active=next;if(next)onset=delay};
  for(const row of timeline.filter(r=>r.event.unit_id===id&&r.event.type==='combat_feedback').sort((a,b)=>a.start-b.start)){
   const e=row.event,hit=e.amount>0&&['physical','magic','fire','lightning','collision','restraint'].includes(e.kind);
   if(Array.isArray(e.statuses_snapshot))change(elementalFrozen({statuses:e.statuses_snapshot}),row.start,hit?'break':'thaw');
   else if(e.kind==='status'&&e.status_id==='freeze'&&elementalFrozen(unit))change(true,row.start,'freeze');
   else if(active&&hit&&!elementalFrozen(unit))change(false,row.start,'break');
  }
  const final=elementalFrozen(unit);
  // Old recordings may only have the final state; modern snapshots also retain
  // Freeze -> thaw entirely contained within one server response (solo vs boss).
  if(active!==final){
   const relevant=timeline.filter(r=>r.event.unit_id===id&&r.event.type==='combat_feedback');
   const hit=relevant.find(r=>r.event.amount>0&&['physical','magic','fire','lightning','collision','restraint'].includes(r.event.kind));
   const application=relevant.find(r=>r.event.kind==='status'&&r.event.status_id==='freeze');
   change(final,final?application?.start||0:onset!==null?Math.max(end,onset+500):(hit?.start??end),hit?'break':'thaw');
  }
 }
 return plans;
}
export function animateFrozenTransitions(previous,battle,timeline,tokenFor){
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 const plans=frozenTransitionPlan(previous,battle,timeline);if(plans.length)warmFrozenSurfaces();
 for(const id of new Set(plans.map(p=>p.id))){
  const token=tokenFor(id);if(!token)continue;
  const generation=Symbol();token.icePlaybackGeneration=generation;
  token.querySelectorAll('.mage-ice-transition').forEach(n=>n.remove());
  let shell=token.querySelector('.mage-ice-shell');
  if(!shell){token.insertAdjacentHTML('beforeend',frozenMarkup({id,alive:true,statuses:[{id:'freeze',elemental_freeze:true}]}));shell=token.querySelector('.mage-ice-shell')}
  if(shell)shell.style.visibility=elementalFrozen(previous?.units?.[id])?'':'hidden';
  const valid=()=>token.isConnected&&token.icePlaybackGeneration===generation;
  let phase=0;
  for(const plan of plans.filter(p=>p.id===id))setTimeout(()=>{
   if(!valid())return;
   const currentPhase=++phase;token.querySelectorAll('.mage-ice-transition').forEach(n=>n.remove());
   if(shell)shell.style.visibility='hidden';
   if(reduced||document.hidden){if(shell)shell.style.visibility=plan.mode==='freeze'?'':'hidden';return}
   const overlay=document.createElement('span');overlay.className='mage-ice-transition';overlay.setAttribute('aria-hidden','true');token.append(overlay);
   const interval=plan.mode==='thaw'?160:85;
   for(let i=0;i<4;i++)setTimeout(()=>{
    if(!valid()){overlay.remove();return}
    overlay.style.backgroundImage=`url('${FROZEN_ROOT}${plan.mode}_${i+1}.png')`;
    overlay.style.opacity=plan.mode==='freeze'?'.76':String(.8-i*.1);
    if(plan.mode==='break')overlay.style.transform=`scale(${1+i*.09})`;
   },i*interval);
   setTimeout(()=>{overlay.remove();if(valid()&&phase===currentPhase&&shell)shell.style.visibility=plan.mode==='freeze'?'':'hidden'},4*interval);
  },plan.delay);
 }
 return Math.max(0,...plans.map(p=>p.delay+(p.mode==='thaw'?640:340)));
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
  const fire=`<foreignObject x="${px-28}" y="${py-28}" width="156" height="156"><div xmlns="http://www.w3.org/1999/xhtml" class="scorch-flame scorch-main-flame" style="animation-duration:${3200+seed%800}ms;animation-delay:-${seed%4000}ms"></div></foreignObject>`;
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
