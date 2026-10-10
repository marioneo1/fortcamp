const root='/assets/boar-mount-v1/';
export function mountedAnimal(unit){return !!unit?.boar_mount&&!!unit?.rider_id}
export function mountedCorpse(unit){return !!unit?.boar_mount&&unit.alive===false&&!!unit.mounted_death}
export function mountAngle(facing){return {n:0,ne:45,e:90,se:135,s:180,sw:225,w:270,nw:315}[facing]??0}
export function turnMount(token,dx,dy){
 const body=token?.querySelector('.boar-body');if(!body||!dx&&!dy)return;
 const angle=Math.atan2(dy,dx)*180/Math.PI+90;
 const previous=parseFloat(body.style.getPropertyValue('--mount-angle'))||0;
 const next=previous+((angle-previous+540)%360+360)%360-180;
 body.style.setProperty('--mount-angle',`${next}deg`);
}
export function mountMarkup(unit){
 return `<span class="boar-shadow" aria-hidden="true"><span class="boar-body" data-mount-facing="${unit.mount_facing||'n'}" aria-hidden="true" style="--mount-angle:${mountAngle(unit.mount_facing)}deg"><img class="boar-idle" src="${root}${unit.alive===false?'dead':'idle_n'}.png?v=3" alt="" draggable="false"></span></span>`;
}
// Resolve the link at presentation time, not from the already-resolved final state.
export function motionPartner(id,previous,battle,timeline,at){
 let partner=previous?.units?.[id]?.animal_mount_id||previous?.units?.[id]?.rider_id;
 for(const row of timeline){
  const e=row.event;
  if(e.mount_boarding&&row.start+row.duration<=at){
   const animal=battle.units?.[e.unit_id]?.animal_mount_id;
   if(e.unit_id===id)partner=animal;
   else if(animal===id)partner=e.unit_id;
  }
  if(['mount_fall','mount_release'].includes(e.type)){
   const before=e.unit_snapshot;
   const other=before?.animal_mount_id||before?.rider_id||e.mount_id;
   if(e.unit_id===id||other===id){
    if(at>=row.start)partner=null;
    else if(!partner)partner=e.unit_id===id?other:e.unit_id;
   }
  }
 }
 return partner||null;
}
export function pairedMotionFrames(frames,unit,partner,cw,ch){
 return frames.map(frame=>({...frame,transform:`translate(${(unit.x-partner.x)*cw}px,${(unit.y-partner.y)*ch}px) ${frame.transform}`}));
}
// Avoid loading a first mount pose during an attack or movement animation.
const preloads=[];
if(typeof Image!=='undefined')for(const file of ['idle_n','dead']){
 const img=new Image();img.src=root+file+'.png?v=3';preloads.push(img);
}
