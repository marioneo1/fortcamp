import {skillIconMarkup} from './ability-icons.js';
export function selectBattleSkill(view,id){
  const actor=view.units?.[view.current_unit_id],skills=actor?.skills||[];
  if(!skills.length)return view;
  const selected=skills.find(skill=>skill.id===id)||actor.special||skills[0];
  const previews=view.skill_previews?.[selected.id];
  return {...view,units:{...view.units,[actor.id]:{...actor,special:selected}},
    attack_previews:previews?Object.fromEntries(Object.entries(view.attack_previews||{}).map(([target,actions])=>[target,{...actions,skill:previews[target]??null}])):view.attack_previews};
}
export function skillAvailability(actor,skill=actor?.special){
  if(actor?.acted)return {available:false,reason:'Main action already used'};
  return skill?.availability||{available:!!skill&&!actor?.special_used,reason:actor?.special_used?'Shared technique use spent':null};
}
export function skillTiming(skill){
  const state=skill?.availability;
  if(!state)return '';
  if(state.cooldown_remaining)return `Ready in ${state.cooldown_remaining} turns`;
  if(state.uses_remaining!==null&&state.uses_remaining!==undefined)return `${state.uses_remaining} use${state.uses_remaining===1?'':'s'} left`;
  return 'Ready';
}
export function skillPicker(actor,escape){
  const skills=actor?.skills||[],passives=actor?.passives||[];
  if(!skills.length&&!passives.length)return '';
  const modern=skills.some(s=>s.ability_version);
  const groups=[['Character skills',skills.filter(s=>s.source_kind==='character')],['Equipment and proficiency',skills.filter(s=>s.source_kind!=='character')]];
  return (skills.length?`<label class="battle-skill-picker">Ability<select id="battle-gear-skill" ${actor.acted||!modern&&actor.special_used?'disabled':''}>${groups.filter(([,rows])=>rows.length).map(([label,rows])=>`<optgroup label="${label}">${rows.map(skill=>`<option value="${escape(skill.id)}" ${skill.id===actor.special?.id?'selected':''}>${escape(skill.name)}${skill.source_name?` · ${escape(skill.source_name)}`:''}${skillTiming(skill)?` · ${escape(skillTiming(skill))}`:''}</option>`).join('')}</optgroup>`).join('')}</select><small>${modern?'Each technique has its own cooldown or uses. Switching techniques does not spend an action.':'All equipped techniques share one use per battle.'}</small></label>`:'')+(passives.length?`<details class="battle-passives"><summary>Character passives (${passives.length})</summary>${passives.map(p=>`<p>${skillIconMarkup({...p,type:"passive"},escape)}<b>${escape(p.name)}</b> · ${escape(p.description)}</p>`).join('')}</details>`:'');
}
