export function statusDetails(status,definitions={}){
  if(status.id==='passive_readiness')return {name:status.name,description:status.description,details:[status.spent?'Used for this battle':status.active_window?'Active now':status.ready?'Ready to trigger':`Ready in ${status.cooldown_remaining} of this character's turns`]};
  const base=definitions[status.id]||{name:status.id,icon:'•',description:'Status effect'};
  const details=[];
  if(status.id==='deployment')return {name:'Temporary deployment',icon:'◆',description:`Owned by ${status.owner_name}. ${status.policy==='automatic'?'Automatic targeting; shares owner output budget.':'Attack commands spend the owner action.'} No extra initiative turn, loot or prisoner reward.`,details:[status.ready?'Ready this owner activation':'Ready from the next owner activation',status.stationary?'Stationary device':'Uses its own movement budget']};
  if(status.id==='wild_form')return {name:status.name,icon:'◆',description:status.description,details:[`${status.turns} owner activations remaining · no HP refill`]};
  if(['open_guard','flowing_footwork','iron_reversal'].includes(status.id))return {...base,details:[status.id==='iron_reversal'?'One incoming direct attack · expires at next personal turn start':`${status.turns} turn window remaining · expires at ${status.source_name||'owner'}’s turn end`,...(status.source_name?[`From ${status.source_name}`]:[])]};
  if(status.id==='barrier')details.push(`${status.amount} damage absorption remaining`);
  if(status.id==='mark')details.push(`Owner: ${status.source_name||'unknown'} · +${status.accuracy||10} accuracy on their first hit`);
  if(status.id==='reaction')return {name:status.ready?'Reaction ready':'Reaction spent',icon:status.ready?'↶':'↷',description:`${(status.reactions||[]).join(' / ')}. One shared reaction, refreshed at activation start. Cannot chain.`,details:[]};
  if(status.id==='footing')return {name:'Knockback resistance',icon:'▣',description:`${status.resistance}% chance to resist a push or pull.`,details:[]};
  const duration=status.rounds??status.turns??status.duration;
  if(duration!=null){
    const clock=status.rounds!=null?'round':status.expiry==='target_start'?'damage tick':'activation';
    details.push(`${duration} ${clock}${duration===1?'':'s'} remaining${status.expiry==='target_end'?' · expires at activation end':''}`);
  }
  if(status.source_name&&status.id!=='mark')details.push(`From ${status.source_name}`);
  return {...base,details};
}

export function tacticalPreviewText(preview){
  if(!preview)return '';
  const parts=[];
  if(preview.intercepted_by)parts.push(`Intercepted by ${preview.intercepted_by}`);
  if(preview.barrier)parts.push(`${preview.barrier}-point Barrier`);
  for(const zone of preview.zones||[]){
    if(zone.kind==='rally')parts.push('Hold Together: remove Fear, next direct hit -25%, next attack +25%');
    else if(zone.name)parts.push(`${zone.name} · ${zone.cells.length} tiles · ${zone.turns} owner activations · ${zone.description}`);
  }
  for(const effect of preview.tactics||[]){
    const dest=effect.destination;
    parts.push(`On hit: ${effect.type} toward cell ${dest.x+1}, ${dest.y+1} · ${effect.resistance}% resistance`);
    if(effect.blocked)parts.push(`Stopped: ${effect.blocked}`);
    if(effect.pit)parts.push(effect.pit==='lethal'?'Lethal fall · body and gear lost':`${effect.pit==='deep'?'Deep':'Shallow'} pit · ${effect.pit==='deep'?'must climb out':'fall damage and Slow'}`);
    if(effect.collision_damage)parts.push(`${effect.collision_damage} collision damage if the hit and forced movement succeed${effect.collision_target_name?`; ${effect.collision_target_name} also takes ${effect.bystander_damage} damage`:''}`);
  }
  return parts.join(' · ');
}
