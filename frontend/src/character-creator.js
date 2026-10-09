import {escapeHTML as esc} from './mission-board-ui.js';
import {raceEffects} from './character-effects.js';

export function startingRaces(content){
  return Object.entries(content.races||{}).filter(([,race])=>race.starting_selectable===true).sort(([a],[b])=>a==='Human'?-1:b==='Human'?1:a.localeCompare(b));
}
export function mountCharacterCreator(root,content){
  const race=root.querySelector('#cc-race'),perk=root.querySelector('#cc-trait');
  race.innerHTML=startingRaces(content).map(([name])=>`<option value="${esc(name)}">${esc(name)}</option>`).join('');race.value='Human';
  const roles=content.starting_roles||{};
  perk.innerHTML=Object.entries(roles).map(([id,role])=>`<option value="${id}">${esc(role.name)}</option>`).join('');
  const updateRace=()=>{
    const profile=content.races?.[race.value]?.gameplay;
    root.querySelector('#creator-race-info').innerHTML=`<b>${esc(race.value)}</b><p>${esc(profile?.summary||'')}</p><div class="tags">${raceEffects(profile).map(effect=>`<span>${esc(effect)}</span>`).join('')||'<span>No racial combat modifiers</span>'}</div>`;
  };
  const updateTraining=()=>{
    const role=roles[perk.value];if(!role)return;
    const job=content.job_loadouts?.jobs?.[perk.value],skills=(job?.starter_skills||[]).map(id=>content.job_loadouts.skills[id]);
    const kit=role.kit.map(id=>content.items[id]?.name||id);
    root.querySelector('#creator-training-info').innerHTML=`<b>${esc(role.name)}</b><p>${esc(role.description)}</p><div class="creator-job-skills">${skills.map(skill=>`<div><b>${esc(skill.name)} <small>· ${esc(skill.type)}</small></b><p>${esc(skill.description)}</p></div>`).join('')}</div><b>Starter equipment</b><p>${kit.map(esc).join(' + ')} / Worn Jacket / Work Boots.</p><p>Three starting skills are equipped. Active and passive skills share five slots. Successful contracts unlock more choices; basic actions and gear abilities use no slots.</p>`;
  };
  race.onchange=updateRace;perk.onchange=updateTraining;
  updateRace();updateTraining();
}
