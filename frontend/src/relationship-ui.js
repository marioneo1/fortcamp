const replies=new Map();
const mealNames={trail_meal:'Trail Meal',study_meal:'Study Meal',rest_meal:'Rest Meal'};
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function recordSummary(character){
  const r=character.service_record||{},completed=r.missions_completed||0,failed=r.missions_failed||0;
  return {missions_taken:r.missions_taken||0,completed,failed,success_rate:completed+failed?Math.round(completed/(completed+failed)*100):null,kills:r.kills||0,subdues:r.subdues||0,times_defeated:r.times_defeated||0,total_damage:r.total_damage||0,damage_per_turn:r.combat_turns?Math.round(r.total_damage/r.combat_turns*10)/10:0,highest_turn_damage:r.highest_turn_damage||0};
}
export function mountRelationships(root,{character,state,content,onAction,onError}){
  const c=character,r=recordSummary(c),profile={...(content.personalities?.[c.personality_id]||{}),...(c.personality_override||{})};
  const avatar=c.is_player||c.id==='player',loyalty=avatar?100:c.loyalty??80,relation=c.relationship||{};
  const facts=[['Missions taken',r.missions_taken],['Completed',r.completed],['Failed',r.failed],['Success rate',r.success_rate===null?'?':r.success_rate+'%'],['Kills',r.kills],['Subdued',r.subdues],['Times defeated',r.times_defeated],['Damage dealt',r.total_damage],['Damage per turn',r.damage_per_turn],['Best turn damage',r.highest_turn_damage]];
  root.innerHTML=`<div class="relationship-panel"><h3>${avatar?'Your service record':escape(profile?.name||'Companion')}</h3>${avatar?'':`<p>${escape(profile?.description||'Uses their own judgment when disobeying.')}</p><b>Loyalty ${loyalty}/100</b><p class="loyalty-note">${100-loyalty}% chance to act independently, checked once per turn. Personality decides the action. Success builds loyalty; repeated clicks cannot reroll it.</p>`}<div class="character-record-grid">${facts.map(([label,value])=>`<div><small>${escape(label)}</small><b>${escape(value)}</b></div>`).join('')}</div><small>Damage is measured per combat turn, not per second. Records begin with this update.</small>${avatar?'':`<h3>Talk with ${escape(c.name)}</h3><div class="relationship-actions">${[['recent','Last expedition'],['food','Food preferences'],['trust','Trust'],['outlook','Outlook']].map(([id,label])=>`<button data-talk="${id}">${label}</button>`).join('')}</div><h3>Offer a prepared meal</h3><small>Kitchen meals are consumed. One gift every six hours; talking does not farm loyalty.</small><div class="relationship-actions">${Object.entries(mealNames).map(([id,label])=>`<button data-meal="${id}" ${(state.meals?.[id]||0)<1||Date.now()/1000<(relation.gift_ready_at||0)?'disabled':''}>${label} (${state.meals?.[id]||0})</button>`).join('')}</div>${(relation.discovered_tastes||[]).length?`<p>Discovered: ${(relation.discovered_tastes||[]).map(id=>`${escape(mealNames[id])} ? ${id===relation.favorite_meal?'favorite':id===relation.disliked_meal?'dislikes':'enjoys normally'}`).join('; ')}</p>`:''}<div class="relationship-reply" role="status">${escape(replies.get(c.id)||'Choose a topic. Your companion remembers expeditions they actually joined.')}</div>`}</div>`;
  async function send(payload){
    root.querySelectorAll('button').forEach(b=>b.disabled=true);
    try{const result=await onAction(payload);state=result.state;character=state.characters.find(item=>item.id===c.id)||character;replies.set(c.id,result.reply.text+(result.reply.loyalty_gain?` (Loyalty +${result.reply.loyalty_gain})`:''));return result}
    catch(error){onError(error)}finally{mountRelationships(root,{character,state,content,onAction,onError})}
  }
  root.querySelectorAll('[data-talk]').forEach(b=>b.onclick=()=>send({action:'talk',topic:b.dataset.talk}));
  root.querySelectorAll('[data-meal]').forEach(b=>b.onclick=()=>send({action:'gift_meal',meal:b.dataset.meal}));
}
