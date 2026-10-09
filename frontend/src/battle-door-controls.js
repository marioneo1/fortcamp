// Permanent doorway controls; commands come from the authoritative battle view.
import {previewMovement} from './movement-preview.js';
export function doorCommand(battle,control){
 if(control.command.action!=='navigate')return control.command;
 // A supplied movement route can start immediately, just like a floor click.
 // Distant/unreachable approaches still use the server's entrance planner.
 const nodes=new Map((battle.movement_tree||[]).map(n=>[`${n.x},${n.y}`,n]));
 const choices=(control.approaches||[]).map(destination=>{
  const preview=previewMovement(battle,destination);if(!preview)return null;
  const path=preview.preview_movement_points;
  const cost=path.slice(1).reduce((total,p,i)=>total+(nodes.get(`${path[i].x},${path[i].y}`)?.steps?.find(s=>s[0]===p.x&&s[1]===p.y)?.[2]??1),0);
  return {destination,cost};
 }).filter(Boolean).sort((a,b)=>a.cost-b.cost);
 const command={...control.command,operate_gate:true,gate_operation:control.operation};
 return choices.length?{...command,position:{...choices[0].destination}}:command;
}
export function doorControlsMarkup(battle, escape){
 return (battle.door_controls||[]).map((control,index)=>{
 const shiftX=0,shiftY=0;
 return `<button class="battle-door-control ${control.operation==='Close'?'is-open':'is-closed'}" data-door-control="${index}" data-navigation-open="${escape(control.gate_id)}" aria-label="${escape(control.label)}" title="${escape(control.label+' - '+control.help)}" style="--door-x-shift:${shiftX}px;--door-y-shift:${shiftY}px;left:${(control.x+.5)/battle.width*100}%;top:${(control.y+.5)/battle.height*100}%" ${control.disabled?'disabled':''}><img src="/assets/combat-navigation-v1/${control.operation==='Close'?'door_close':'door_open'}.png" alt=""></button>`}).join('');
}
export function bindDoorControls(root,battle,send){
 root.querySelectorAll('[data-door-control]').forEach(button=>{
  button.onpointerdown=event=>event.stopPropagation();
  button.onclick=event=>{event.stopPropagation();const control=battle.door_controls?.[Number(button.dataset.doorControl)];if(control&&!control.disabled)send(doorCommand(battle,control))};
 });
}
