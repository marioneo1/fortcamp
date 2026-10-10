import {bindPlacementPanel,placementPoint,placementCursor,clearPlacementCursor} from './combat-placement-panel.js';
// Only construction needs a placement window; combat skills use normal targeting.
let session=null,binding=null;
export function resetEngineerPlacement(){session=null;binding?.abort();document.querySelectorAll('.engineer-panel,.engineer-layer').forEach(n=>n.remove());document.querySelectorAll('.placement-cursor-valid,.placement-cursor-invalid').forEach(clearPlacementCursor)}
export function engineerCommand(view,selection){
 const a=view.units?.[view.current_unit_id],skill=a?.special,k=skill?.engineer_kind;
 if(!k)return null;
 const base={action:'skill',skill_id:skill.id};
 if(a.construction||['rapid_assembly','overclock'].includes(k))return base;
 if(k==='scuttle_protocol')return (view.engineer.machines||[]).includes(selection.target)&&(!a.mounted_machine||a.mounted_machine===selection.target)?{...base,target_id:selection.target}:null;
 if(k==='man_the_guns')return a.mounted_machine?view.engineer.exits.some(p=>p.x===selection.point?.x&&p.y===selection.point?.y)?{...base,...selection.point}:null:view.engineer.mounts.includes(selection.target)?{...base,target_id:selection.target}:null;
 if(!selection.point)return null;
 if(k==='dynamite')return view.engineer.dynamite_cells.some(p=>p.x===selection.point.x&&p.y===selection.point.y)?{...base,...selection.point}:null;
 return (k==='proximity_charge'?view.engineer.mine_placement||[]:view.engineer.placement).some(p=>p.x===selection.point.x&&p.y===selection.point.y)?{...base,...selection.point}:null;
}
export function mountEngineer({view,mode,field,send,cancel,escape,blocked=()=>false}){
 binding?.abort();clearPlacementCursor(field);document.querySelectorAll('.engineer-panel,.engineer-layer').forEach(n=>n.remove());
 if(!field||!view.engineer||mode!=='skill')return;
 const a=view.units[view.current_unit_id],skill=a.special,k=skill?.engineer_kind;if(!['sentry_turret','heavy_emplacement'].includes(k))return;
 const key=`${view.seed}:${a.id}:${a.ability_activation}:${skill.id}`;
 if(session?.key!==key)session={key,point:null,target:null};const s=session;binding=new AbortController();const opts={signal:binding.signal};
 const panel=document.createElement('section'),layer=document.createElement('div');panel.className='summoner-panel engineer-panel';layer.className='summoner-target-layer engineer-layer';field.closest('.battle-viewport').parentElement.append(panel);field.append(layer);
 bindPlacementPanel(panel,'engineer',binding.signal);
 const close=()=>{resetEngineerPlacement();cancel()};
 let cells=a.construction||['rapid_assembly','overclock','scuttle_protocol'].includes(k)?[a]:k==='man_the_guns'?a.mounted_machine?view.engineer.exits:view.engineer.mounts.map(id=>view.units[id]):k==='dynamite'?view.engineer.dynamite_cells:view.engineer.placement;
 function paint(){
  const command=engineerCommand(view,s);panel.innerHTML=`<header data-placement-handle><small>FIELD ENGINEERING · DRAG TO MOVE</small><h3>${escape(skill.name)}</h3></header><p>${escape(skill.description)}</p><p class="engineer-capacity">Sentries ${view.engineer.sentry_used}/3 · Heavy ${view.engineer.heavy_used}/1</p><footer><button data-engineer-confirm ${!command||blocked()||skill.availability?.available===false?'disabled':''}><kbd>E</kbd> Confirm</button><button data-engineer-cancel><kbd>C</kbd> Cancel</button></footer>`;
  panel.querySelector('[data-engineer-confirm]').onclick=()=>{if(blocked())return;const cmd=engineerCommand(view,s);if(cmd){resetEngineerPlacement();send(cmd)}};
  panel.querySelector('[data-engineer-cancel]').onclick=close;
  layer.innerHTML=cells.map(p=>`<i class="${p.id===s.target||p.x===s.point?.x&&p.y===s.point?.y?'chosen':''}" style="left:${p.x/view.width*100}%;top:${p.y/view.height*100}%;width:${100/view.width}%;height:${100/view.height}%"></i>`).join('');
  if(s.point&&!a.construction&&['sentry_turret','heavy_emplacement','proximity_charge','dynamite'].includes(k))layer.innerHTML+=`<img class="engineer-placement-preview" src="/assets/engineer-v1/${{sentry_turret:'sentry_idle',heavy_emplacement:'heavy_idle',proximity_charge:'mine',dynamite:'dynamite'}[k]}.png" style="left:${s.point.x/view.width*100}%;top:${s.point.y/view.height*100}%;width:${100/view.width}%;height:${100/view.height}%" alt="">`;
 }
 field.addEventListener('click',e=>{e.stopImmediatePropagation();if(blocked())return;const token=e.target.closest('[data-battle-unit]')?.dataset.battleUnit,cell=e.target.closest('[data-battle-cell]')?.dataset.battleCell;if(token){s.target=token;s.point={x:view.units[token].x,y:view.units[token].y}}else if(cell){const [x,y]=cell.split(',').map(Number);s.point={x,y};s.target=null}paint()},{...opts,capture:true});
 panel.addEventListener('contextmenu',e=>{e.preventDefault();close()},opts);
 field.addEventListener('pointermove',e=>{const p=placementPoint(field,view,e);placementCursor(field,!!a.construction||cells.some(q=>q.x===p.x&&q.y===p.y))},opts);
 document.addEventListener('keydown',e=>{if(!field.isConnected||e.target.closest?.('input,select,textarea'))return;const key=e.key.toLowerCase();if(['c','escape','e'].includes(key)){e.preventDefault();e.stopImmediatePropagation();if(key==='e'){if(!e.repeat)panel.querySelector('[data-engineer-confirm]:not(:disabled)')?.click()}else close()}},{...opts,capture:true});paint();
}
export function engineerHazardsMarkup(view){return (view.engineer_hazards||[]).map(h=>`<span class="engineer-hazard ${h.kind}" data-hazard-id="${h.id}" style="left:${h.x/view.width*100}%;top:${h.y/view.height*100}%;width:${100/view.width}%;height:${100/view.height}%" title="${h.proximity_trigger?'Proximity Dynamite: anyone within one cell triggers damage and knockback':h.kind==='mine'?'Armed mine: allies and enemies trigger it within one cell':'Dynamite: explodes next owner turn'}"><img src="/assets/engineer-v1/${h.kind}.png" alt=""><b>${h.kind==='mine'||h.proximity_trigger?'!':'1'}</b></span>`).join('')}
export function emitEngineerEffect(field,event,battle,delay){
 if(event.skill==='engineer_dynamite_throw'){
  setTimeout(()=>{
   if(!field.isConnected)return;
   const el=document.createElement('img');el.className='engineer-thrown-dynamite';el.src='/assets/engineer-v1/dynamite.png';el.alt='';
   const cw=field.clientWidth/battle.width,ch=field.clientHeight/battle.height,dx=(event.x-event.from.x)*cw,dy=(event.y-event.from.y)*ch;
   el.style.cssText=`left:${(event.from.x+.5)/battle.width*100}%;top:${(event.from.y+.5)/battle.height*100}%;width:${.55/battle.width*100}%`;
   field.append(el);
   const frames=Array.from({length:17},(_,i)=>{const t=i/16;return {offset:t,transform:`translate(calc(-50% + ${dx*t}px),calc(-50% + ${dy*t-Math.sin(Math.PI*t)*ch*.85}px)) rotate(${t*270}deg)`}});
   el.animate(frames,{duration:420}).onfinish=()=>el.remove();
  },delay+180);return true;
 }
 if(event.skill==='engineer_rapid_assembly'){
  setTimeout(()=>{
   if(!field.isConnected)return;
   const cue=document.createElement('span');cue.className='engineer-assembly-cue';cue.setAttribute('aria-hidden','true');
   cue.style.cssText=`left:${(event.x+.5)/battle.width*100}%;top:${(event.y+.5)/battle.height*100}%;width:${1.45/battle.width*100}%`;
   cue.innerHTML='<svg viewBox="0 0 100 100"><g fill="none" stroke="currentColor" stroke-width="3"><path d="M38 9h24l3 10 9 5 10-2 12 21-7 8v10l7 8-12 21-10-2-9 5-3 10H38l-3-10-9-5-10 2L4 69l7-8V51l-7-8 12-21 10 2 9-5Z" transform="translate(0 -6) scale(1 .94)"/><circle cx="50" cy="47" r="21"/><path d="m36 48 9 9 21-24" stroke-width="5"/></g></svg><i></i><i></i><i></i><i></i>';
   field.append(cue);cue.animate([{opacity:0,transform:'translate(-50%,-50%) scale(.65) rotate(-18deg)'},{opacity:1,offset:.2,transform:'translate(-50%,-50%) scale(1) rotate(0deg)'},{opacity:.85,offset:.6,transform:'translate(-50%,-50%) scale(1.04) rotate(4deg)'},{opacity:0,transform:'translate(-50%,-50%) scale(1.18) rotate(12deg)'}],{duration:750}).onfinish=()=>cue.remove();
  },delay);return true;
 }
 if(event.skill==='engineer_build')return true;
 if(event.skill==='engineer_cross_blast'){
  setTimeout(()=>{if(!field.isConnected)return;const el=document.createElement('img');el.className='engineer-impact';el.src='/assets/engineer-v2/cross_blast.png';el.style.cssText=`left:${(event.x+.5)/battle.width*100}%;top:${(event.y+.5)/battle.height*100}%;width:${3/battle.width*100}%`;field.append(el);el.animate([{opacity:0,transform:'translate(-50%,-50%) scale(.7)'},{opacity:1,offset:.15,transform:'translate(-50%,-50%) scale(1)'},{opacity:0,transform:'translate(-50%,-50%) scale(1.08)'}],{duration:600}).onfinish=()=>el.remove()},delay);return true;
 }
 if(event.skill!=='engineer_explosion')return false;
 setTimeout(()=>{if(!field.isConnected)return;const el=document.createElement('img');el.className='engineer-impact';el.src=`/assets/engineer-v1/${event.skill==='engineer_explosion'?'explosion':'rapid_assembly'}.png`;el.style.cssText=`left:${(event.x+.5)/battle.width*100}%;top:${(event.y+.5)/battle.height*100}%;width:${(event.skill==='engineer_explosion'?2.5:1.3)/battle.width*100}%`;field.append(el);const anim=el.animate([{opacity:0,transform:'translate(-50%,-50%) scale(.4)'},{opacity:1,offset:.15,transform:'translate(-50%,-50%) scale(1)'},{opacity:0,transform:'translate(-50%,-50%) scale(1.1)'}],{duration:600});anim.onfinish=()=>el.remove()},delay);return true;
}

export function hazardDeparturePlans(previous,battle,timeline){
 const remaining=new Set((battle.engineer_hazards||[]).map(h=>h.id)),seen=new Set();
 return timeline.filter(row=>row.event.type==='martial_effect'&&row.event.skill==='engineer_explosion'&&row.event.hazard_id&&!remaining.has(row.event.hazard_id)).flatMap(row=>{
  const id=row.event.hazard_id;if(seen.has(id))return [];seen.add(id);
  const hazard=(previous?.engineer_hazards||[]).find(h=>h.id===id)||row.event.hazard_snapshot;
  const birth=timeline.find(r=>r.event.skill==='engineer_dynamite_throw'&&r.event.hazard_id===id);
  return hazard?[{hazard,start:row.start,...(birth?{appear:birth.start+600}:{})}]:[];
 });
}
export function animateEngineerHazards(previous,battle,timeline,field){
 for(const {hazard,start,appear=0} of hazardDeparturePlans(previous,battle,timeline)){
  const holder=document.createElement('div');holder.innerHTML=engineerHazardsMarkup({...battle,engineer_hazards:[hazard]});const ghost=holder.firstElementChild;field.append(ghost);ghost.style.visibility=appear?'hidden':'';setTimeout(()=>{ghost.style.visibility=''},appear);setTimeout(()=>ghost.remove(),start);
 }
 for(const row of timeline.filter(r=>r.event.skill==='engineer_dynamite_throw')){
  const hazard=(battle.engineer_hazards||[]).find(h=>h.id===row.event.hazard_id);
  if(!hazard)continue;
  const placed=[...field.querySelectorAll('.engineer-hazard')].find(el=>el.dataset.hazardId===hazard.id);
  if(placed){placed.style.visibility='hidden';setTimeout(()=>{placed.style.visibility=''},row.start+600)}
 }
}
