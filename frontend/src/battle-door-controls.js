// Permanent doorway controls; commands come from the authoritative battle view.
export function doorControlsMarkup(battle, escape){
 return (battle.door_controls||[]).map((control,index)=>`<button class="battle-door-control ${control.operation==='Close'?'is-open':'is-closed'}" data-door-control="${index}" data-navigation-open="${escape(control.gate_id)}" aria-label="${escape(control.label)}" title="${escape(control.label+' ? '+control.help)}" style="left:${(control.x+.5)/battle.width*100}%;top:${(control.y+.5)/battle.height*100}%" ${control.disabled?'disabled':''}><img src="/assets/combat-controls-v2/pointer.png" alt=""><span aria-hidden="true">${control.operation==='Close'?'?':'+'}</span></button>`).join('');
}
export function bindDoorControls(root,battle,send){
 root.querySelectorAll('[data-door-control]').forEach(button=>{
  button.onpointerdown=event=>event.stopPropagation();
  button.onclick=event=>{event.stopPropagation();const control=battle.door_controls?.[Number(button.dataset.doorControl)];if(control&&!control.disabled)send(control.command)};
 });
}
