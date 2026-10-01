export function selectBattleSkill(view,id){
  const actor=view.units?.[view.current_unit_id],skills=actor?.skills||[];
  if(!skills.length)return view;
  const selected=skills.find(skill=>skill.id===id)||actor.special||skills[0];
  const previews=view.skill_previews?.[selected.id];
  return {...view,units:{...view.units,[actor.id]:{...actor,special:selected}},
    attack_previews:previews?Object.fromEntries(Object.entries(view.attack_previews||{}).map(([target,actions])=>[target,{...actions,skill:previews[target]??null}])):view.attack_previews};
}
export function skillPicker(actor,escape){
  if((actor?.skills||[]).length<2)return '';
  return `<label class="battle-skill-picker">Equipped technique<select id="battle-gear-skill" ${actor.acted||actor.special_used?'disabled':''}>${actor.skills.map(skill=>`<option value="${escape(skill.id)}" ${skill.id===actor.special?.id?'selected':''}>${escape(skill.name)}${skill.source_name?` · ${escape(skill.source_name)}`:''}</option>`).join('')}</select><small>Choose one technique. All equipped techniques share one use per battle.</small></label>`;
}
