import {escapeHTML as esc} from './mission-board-ui.js';
import {raceEffects} from './character-effects.js';

export function startingRaces(content){
  return Object.entries(content.races||{}).filter(([,race])=>race.rarity!=='Limited').sort(([a],[b])=>a==='Human'?-1:b==='Human'?1:a.localeCompare(b));
}
export function mountCharacterCreator(root,content){
  const race=root.querySelector('#cc-race'),perk=root.querySelector('#cc-trait'),training=root.querySelector('#cc-perk');
  race.innerHTML=startingRaces(content).map(([name])=>`<option value="${esc(name)}">${esc(name)}</option>`).join('');race.value='Human';
  const roles=content.starting_roles||{};
  perk.innerHTML=Object.entries(roles).map(([id,role])=>`<option value="${id}">${esc(role.name)}</option>`).join('');
  const tracks=content.proficiency_tracks||content.perk_tracks||{};
  training.innerHTML=Object.entries(tracks).map(([id,data])=>`<option value="${esc(id)}">${esc(data.name)}</option>`).join('');
  const updateRace=()=>{
    const profile=content.races?.[race.value]?.gameplay;
    root.querySelector('#creator-race-info').innerHTML=`<b>${esc(race.value)}</b><p>${esc(profile?.summary||'')}</p><div class="tags">${raceEffects(profile).map(effect=>`<span>${esc(effect)}</span>`).join('')||'<span>No racial combat modifiers</span>'}</div>`;
  };
  const updateTraining=()=>{
    const role=roles[perk.value];training.value=role.proficiency;training.disabled=true;
    const chosen=content.standalone_perks?.[role.perk],track=tracks[role.proficiency],kit=role.kit.map(id=>content.items[id]?.name||id);
    root.querySelector('#creator-training-info').innerHTML=`<b>${esc(chosen?.name||'Starting perk')}</b><p>${esc(chosen?.description||'')} ${esc(chosen?.effect||'')}</p><b>${esc(track?.name||'Proficiency')} · Basic</b><p>${esc(track?.description||'')}${track?.attribute_bonus?` +1 ${esc(track.attribute_bonus.toUpperCase())}.`:''} Improve work proficiencies through camp jobs and qualified teachers.</p><b>Starter equipment</b><p>${kit.map(esc).join(' + ')} / Worn Jacket / Work Boots. This starting role gives you a low-grade kit and matching training. You can change weapons and learn other professions later.</p>`;
  };
  race.onchange=updateRace;perk.onchange=updateTraining;training.onchange=updateTraining;
  updateRace();updateTraining();
}
