const replies=new Map();
const mealNames={trail_meal:'Trail Meal',study_meal:'Study Meal',rest_meal:'Rest Meal'};
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function recordSummary(character){
  const r=character.service_record||{},completed=r.missions_completed||0,failed=r.missions_failed||0;
  return {missions_taken:r.missions_taken||0,completed,failed,success_rate:completed+failed?Math.round(completed/(completed+failed)*100):null,kills:r.kills||0,subdues:r.subdues||0,times_defeated:r.times_defeated||0,total_damage:r.total_damage||0,damage_per_turn:r.combat_turns?Math.round(r.total_damage/r.combat_turns*10)/10:0,highest_turn_damage:r.highest_turn_damage||0};
}
const pending=new Set(),selectedTopics=new Map(),giftPanels=new Set();
const topics=[['recent','Last expedition','Talk about a job they joined.'],['food','Food preferences','Discover a favorite meal.'],['trust','Trust','Ask how they feel about your leadership.'],['outlook','Outlook','Hear what matters to them.']];
export function conversationHistory(id){return (replies.get(id)||[]).map(entry=>({...entry}))}
export function rememberConversation(id,entry){const history=replies.get(id)||[];history.push({...entry});replies.set(id,history.slice(-8))}
export function mountRelationships(root,{character,state,content,onAction,onError,portrait}){
  const previous=root.querySelector('.conversation-transcript'),scroll=previous?.scrollTop||0,atBottom=!previous||previous.scrollHeight-previous.clientHeight-scroll<25;
  root.dataset.conversationCharacter=character.id;
  const c=character,profile={...(content.personalities?.[c.personality_id]||{}),...(c.personality_override||{})};
  const avatar=c.is_player||c.id==='player',loyalty=avatar?100:c.loyalty??80,relation=c.relationship||{},busy=pending.has(c.id),away=!['idle','incapacitated'].includes(c.status||'idle');
  const now=Date.now()/1000,cooling=now<(relation.gift_ready_at||0),history=conversationHistory(c.id),topic=selectedTopics.get(c.id);
  const face=portrait?portrait(c):c.portrait_thumbnail||c.portrait?`<img src="${escape(c.portrait_thumbnail||c.portrait)}" alt="">`:`<span>${escape(c.name.slice(0,1))}</span>`;
  const tastes=relation.discovered_tastes||[];
  root.innerHTML=`<section class="conversation-workspace"><aside class="conversation-companion"><div class="conversation-portrait">${face}</div><div class="eyebrow">${avatar?'YOUR CHARACTER':'AT THE CAMP'}</div><h3>${escape(c.name)}</h3><p>${escape(c.race)} / ${escape(profile.name||'Companion')}</p>${avatar?'<p>This is your character. Conversations and gifts are available with your companions.</p>':`<div class="conversation-loyalty"><div><b>Loyalty</b><span>${loyalty}/100</span></div><progress value="${loyalty}" max="100" aria-label="Loyalty"></progress><small>${100-loyalty}% chance to act independently each activation.</small></div><p class="conversation-personality">${escape(profile.description||'Uses their own judgment when disobeying.')}</p><small>Conversations reveal preferences. Talking alone does not increase loyalty.</small>`}</aside>${avatar?'':`<div class="conversation-main"><header><div class="eyebrow">CONVERSATION</div><h3>A moment with ${escape(c.name)}</h3><p>Ask about their experiences, get to know them, or share a meal.</p></header><div class="conversation-transcript" role="log" aria-live="polite" aria-relevant="additions text" aria-label="Conversation with ${escape(c.name)}">${history.length?history.map(entry=>`<article class="conversation-exchange"><span class="conversation-prompt">You / ${escape(entry.prompt)}</span><div class="conversation-speech"><strong>${escape(c.name)}</strong><p>${escape(entry.text)}</p>${entry.gain?`<small class="conversation-gain">Loyalty +${entry.gain}</small>`:''}</div></article>`).join(''):'<div class="conversation-empty"><b>Choose something to talk about</b><p>They remember expeditions they actually joined. Food preferences belong to this character, not their personality.</p></div>'}</div>${away?'<p class="conversation-away">This character is away on assignment. You can talk when they return.</p>':''}<div class="conversation-topic-heading"><b>Choose a topic</b>${busy?'<span role="status">Waiting for a reply...</span>':''}</div><div class="conversation-topics">${topics.map(([id,label,help])=>`<button data-talk="${id}" class="${id===topic?'selected':''}" ${busy||away?'disabled':''}><b>${label}</b><small>${help}</small></button>`).join('')}</div><details class="conversation-gifts" ${giftPanels.has(c.id)?'open':''}><summary>Share a prepared meal <span>${cooling?'Cooling down':Object.values(state.meals||{}).reduce((sum,n)=>sum+n,0)+' available'}</span></summary><p>${cooling?`Next gift: ${escape(new Date(relation.gift_ready_at*1000).toLocaleString())}.`:'One gift every six hours. Favorite meals improve loyalty more.'} Prepare meals at Base / Kitchen.</p><div class="conversation-meals">${Object.entries(mealNames).map(([id,label])=>{const count=state.meals?.[id]||0,known=tastes.includes(id),taste=known?(id===relation.favorite_meal?'Favorite':id===relation.disliked_meal?'Dislikes':'Neutral'):'Preference unknown';return `<button data-meal="${id}" ${busy||away||cooling||count<1?'disabled':''} title="${escape(cooling?'Wait for the gift cooldown':count<1?'Prepare this meal in the Kitchen':taste)}"><b>${label}</b><span>${count} prepared</span><small class="${known&&id===relation.favorite_meal?'favorite':''}">${taste}</small></button>`}).join('')}</div></details></div>`}</section>`;
  const transcript=root.querySelector('.conversation-transcript');if(transcript)transcript.scrollTop=atBottom?transcript.scrollHeight:scroll;
  const gifts=root.querySelector('.conversation-gifts');if(gifts)gifts.ontoggle=()=>{if(!gifts.isConnected)return;gifts.open?giftPanels.add(c.id):giftPanels.delete(c.id)};
  async function send(payload){
    if(pending.has(c.id)||away)return;
    pending.add(c.id);if(payload.topic)selectedTopics.set(c.id,payload.topic);
    const prompt=payload.action==='talk'?topics.find(t=>t[0]===payload.topic)?.[1]||'Conversation':`Share ${mealNames[payload.meal]}`;
    mountRelationships(root,{character,state,content,onAction,onError,portrait});
    try{const result=await onAction(payload);state=result.state;character=state.characters.find(item=>item.id===c.id)||character;rememberConversation(c.id,{prompt,text:result.reply.text,gain:result.reply.loyalty_gain||0});return result}
    catch(error){onError(error)}finally{pending.delete(c.id);if(root.isConnected&&root.dataset.conversationCharacter===c.id)mountRelationships(root,{character,state,content,onAction,onError,portrait})}
  }
  root.querySelectorAll('[data-talk]').forEach(b=>b.onclick=()=>send({action:'talk',topic:b.dataset.talk}));
  root.querySelectorAll('[data-meal]').forEach(b=>b.onclick=()=>send({action:'gift_meal',meal:b.dataset.meal}));
}

export function mountServiceRecord(root,character){
  const r=recordSummary(character);
  const facts=[['Missions taken',r.missions_taken],['Completed',r.completed],['Failed',r.failed],['Success rate',r.success_rate===null?'?':r.success_rate+'%'],['Kills',r.kills],['Subdued',r.subdues],['Times defeated',r.times_defeated],['Damage dealt',r.total_damage],['Damage per turn',r.damage_per_turn],['Best turn damage',r.highest_turn_damage]];
  root.innerHTML=`<h3>Service Record</h3><div class="character-record-grid">${facts.map(([label,value])=>`<div><small>${escape(label)}</small><b>${escape(value)}</b></div>`).join('')}</div><small>Damage is measured per combat turn, not per second. Records begin with this update.</small>`;
}
