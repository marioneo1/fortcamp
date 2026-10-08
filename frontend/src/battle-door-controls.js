// Permanent doorway controls; commands come from the authoritative battle view.
export function doorControlsMarkup(battle, escape){
 return (battle.door_controls||[]).map((control,index)=>{
 const peer=battle.door_controls.find((c,i)=>i!==index&&c.gate_id===control.gate_id);
 const shiftX=peer?Math.sign(control.x-peer.x)*12:0,shiftY=peer?Math.sign(control.y-peer.y)*12:0;
 return `<button class="battle-door-control ${control.operation==='Close'?'is-open':'is-closed'}" data-door-control="${index}" data-navigation-open="${escape(control.gate_id)}" aria-label="${escape(control.label)}" title="${escape(control.label+' - '+control.help)}" style="--door-x-shift:${shiftX}px;--door-y-shift:${shiftY}px;left:${(control.x+.5)/battle.width*100}%;top:${(control.y+.5)/battle.height*100}%" ${control.disabled?'disabled':''}><img src="/assets/combat-navigation-v1/${control.operation==='Close'?'door_close':'door_open'}.png" alt=""></button>`}).join('');
}
export function bindDoorControls(root,battle,send){
 root.querySelectorAll('[data-door-control]').forEach(button=>{
  button.onpointerdown=event=>event.stopPropagation();
  button.onclick=event=>{event.stopPropagation();const control=battle.door_controls?.[Number(button.dataset.doorControl)];if(control&&!control.disabled)send(control.command)};
 });
}
