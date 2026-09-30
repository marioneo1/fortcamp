const ROOT='/assets/mission-board-v1/';
export const escapeHTML=(value='')=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const title=value=>String(value||'').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
const FORMS=new Set(['recovery','rescue','defense','hunt','containment','investigation','infiltration','operation']);
const EVENTS=new Set(['goblin_warhost','ashen_procession','arcane_convergence','great_beast_tide','starfall_omen']);
export function boardIcon(name,cls=''){return `<img class="board-icon ${escapeHTML(cls)}" src="${ROOT}${escapeHTML(name)}.png" alt="" decoding="async" draggable="false">`}
export function rankSeal(rank){const letter=/^[EDCBAS]$/.test(rank)?rank:'E';return `<span class="guild-rank-seal">${boardIcon('rank_'+letter.toLowerCase())}<b>${letter}</b></span>`}
export function missionCard(m,{count=1,claimed=0,privateContract=false}={}){
  if(m.locked)return '';
  const form=FORMS.has(m.mission_form)?m.mission_form:'operation',rewards=m.reward_preview||[],roles=m.roles||[],requirements=m.requirements||[];
  const mode=m.resolution_mode==='combat'?'Combat':m.has_decisions?'Choices':null;
  const attr=privateContract?'data-private-mission':'data-mission',rank=/^[EDCBAS]$/.test(m.rank)?m.rank:'E';
  const seconds=Math.max(0,Number(m.duration_seconds)||0),minutes=Math.ceil(seconds/60),duration=minutes<60?`${minutes} min`:`${Math.floor(minutes/60)}h ${minutes%60?minutes%60+'m':''}`;
  const source=m.chain?`Story chain ${m.chain.step}/${m.chain.total}`:m.world_trigger?'World consequence':privateContract?m.private_source||'Earned follow-up':m.story_thread?.name||`${title(m.stat)} \u00b7 DC ${m.difficulty}`;
  return `<article class="mission guild-contract rank-${rank.toLowerCase()} ${privateContract?'private-contract':''} ${count?'':'claimed'}" ${attr}="${escapeHTML(m.id)}">
    <div class="contract-heading">${boardIcon('form_'+form,'contract-form-icon')}<div><span class="contract-kind">${title(form)}${mode?`<span class="contract-mode">${mode}</span>`:''}</span><h3>${escapeHTML(m.name)}</h3></div>${count>1?`<span class="mission-stack" title="${count} available copies">&times;${count}</span>`:''}</div>
    <div class="contract-context">${escapeHTML(source)}</div>
    <p class="contract-premise">${escapeHTML(m.description)}</p>
    <div class="contract-facts"><span>${boardIcon('utility_clock')}${duration}</span><span>${boardIcon('utility_party')}${Number(m.party_size)||1} ${(Number(m.party_size)||1)===1?'character':'characters'}</span>${privateContract?'<span class="contract-personal">Only you</span>':''}</div>
    ${roles.length?`<div class="contract-roles">${roles.map(r=>`<span>${escapeHTML(r.label)} <b>${escapeHTML(r.metric==='constitution'?'CON':String(r.metric||'').toUpperCase())} ${Number(r.recommended)||0}</b></span>`).join('')}<small>Recommended</small></div>`:''}
    <div class="contract-rewards"><span class="contract-section-label">${boardIcon('utility_reward')}Possible rewards</span><div>${rewards.slice(0,3).map(r=>`<span class="reward-pill">${escapeHTML(r)}</span>`).join('')||'<span class="muted">See contract details</span>'}${rewards.length>3?`<span class="reward-more">+${rewards.length-3} more</span>`:''}</div></div>
    ${requirements.length?`<div class="contract-requirements"><b>Required</b> ${requirements.slice(0,2).map(escapeHTML).join(' ? ')}${requirements.length>2?` ? +${requirements.length-2} more`:''}</div>`:''}
    ${m.world_trigger?`<div class="contract-origin">From ${escapeHTML(m.world_trigger.source_mission)}</div>`:''}
    ${privateContract?`<div class="contract-expiry">Claim within <span data-countdown-end="${Number(m.expires_at)||0}" data-countdown-suffix="">--:--</span></div>`:''}
    <footer class="contract-footer"><span>${privateContract?'Personal lead':count?`${count} available${claimed?` &middot; ${claimed} claimed`:''}`:`${claimed} claimed`}</span><button type="button" class="contract-open" data-mission-action="${escapeHTML(m.id)}" aria-label="Inspect ${escapeHTML(m.name)}">${count?'Inspect &amp; assign':'View contract'} <span aria-hidden="true">&rarr;</span></button></footer>
  </article>`;
}
export function eventHeader(event={id:'general'}){
  const special=EVENTS.has(event.id),emblem=special?'event_'+event.id:'utility_public';
  return `${special?`<div class="guild-event-scene" aria-hidden="true"><span class="event-atmosphere"></span><span class="event-orbit event-orbit-one"></span><span class="event-orbit event-orbit-two"></span><span class="event-trail"></span>${Array.from({length:18},(_,i)=>`<i class="event-mote" style="--i:${i};--x:${8+(i*37)%85}%;--y:${8+(i*23)%80}%;--duration:${7+i%7}s;--delay:-${1+i*.73}s"></i>`).join('')}</div>`:''}<div class="guild-event-art" aria-hidden="true"><div class="guild-event-halo"></div>${boardIcon(emblem)}<div class="guild-event-particles">${Array.from({length:7},(_,i)=>`<i style="--i:${i}"></i>`).join('')}</div></div><div class="guild-event-copy"><div class="eyebrow">${special?'REGIONAL EVENT':'THE GUILD IS OPEN'}</div><h2>${special?escapeHTML(event.name):'Find your next adventure.'}</h2><p>${special?escapeHTML(event.splash):'Choose a contract, assemble your party, and see where the road leads.'}</p><span class="guild-event-note">${special?'Event contracts and discoveries are in the pool.':'Shared contracts &middot; Personal stories &middot; Tactical encounters'}</span></div>`;
}
export function filterChips(filters){
  const entries=[['query',filters.query&&`Search: ${filters.query}`],['rank',filters.rank&&`${filters.rank} rank`],['form',filters.form&&title(filters.form)],['available',filters.available&&'Available only']].filter(([,value])=>value);
  return entries.map(([key,label])=>`<button type="button" class="board-filter-chip" data-clear-filter="${key}" aria-label="Remove ${escapeHTML(label)} filter">${escapeHTML(label)} <span aria-hidden="true">&times;</span></button>`).join('');
}
const rendered=new WeakMap();
export function stableBoardHTML(root,markup){
  const key=markup.replace(/<details\b[^>]*>/g,tag=>tag.replace(/\sopen(?=[ >])/g,'').replace(/\s+>/,'>'));
  if(rendered.get(root)===key)return false;
  const document=root.ownerDocument,focused=document.activeElement;
  const focusId=root.contains(focused)?focused.getAttribute('data-mission-action')||focused.closest('[data-rank-board]')?.dataset.rankBoard:null;
  const isMission=focused?.hasAttribute('data-mission-action'),scroll=globalThis.scrollY;
  root.innerHTML=markup;rendered.set(root,key);
  if(focusId){const target=isMission?root.querySelector(`[data-mission-action="${CSS.escape(focusId)}"]`):root.querySelector(`[data-rank-board="${CSS.escape(focusId)}"]>summary`);target?.focus({preventScroll:true})}
  if(Number.isFinite(scroll)&&globalThis.scrollY!==scroll)globalThis.scrollTo?.({top:scroll,behavior:'instant'});
  return true;
}
