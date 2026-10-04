import {staminaHTML,staminaView,staminaCosts} from './stamina.js';
import {rankedCandidates,suggestAssignments} from './mission-planner.js';

export function mountMissionPlanner(root,m,characters,{esc,title,portrait,metrics,rating,statLabel,debug,onChange,onClaimDebug,onHire}){
  const primary=m.roles?.length?m.roles.map(r=>({...r,key:r.id})):Array.from({length:m.party_size},(_,i)=>({key:`party-${i}`,label:i===0?'Lead candidate':`Party member ${i+1}`}));
  const guards=Array.from({length:m.bodyguard_slots||0},(_,i)=>({key:`guard-${i}`,label:`Bodyguard ${i+1}`,guard:true}));
  const slots=[...primary,...guards],draft={},hired=new Map();
  let active=slots[0]?.key,query='',sort='fit',page=0;
  const pageSize=12;
  const nextReady=()=>Math.min(Infinity,...characters.filter(c=>c.status==='idle'&&!staminaView(c).eligible).map(c=>Number(c.stamina.updated_at)+(1-Number(c.stamina.balance))*18));
  let readyAt=nextReady();
  const score=(c,slot)=>slot.guard?metrics(c).dps+metrics(c).constitution/2:slot.metric?metrics(c)[slot.metric]||0:rating(c,m.stat);
  const scoreText=(c,slot)=>slot.guard?`${metrics(c).dps} DPS · ${metrics(c).constitution} CON`:slot.metric?`${score(c,slot)} ${slot.metric==='constitution'?'CON':slot.metric.toUpperCase()}`:`${rating(c,m.stat)} ${statLabel}`;
  const selection=()=>({mercenary_ids:Object.values(draft).filter(id=>hired.has(id)),party_ids:primary.map(slot=>draft[slot.key]).filter(Boolean),role_assignments:m.roles?.length?Object.fromEntries(primary.filter(slot=>draft[slot.key]).map(slot=>[slot.key,draft[slot.key]])):null,bodyguard_ids:guards.map(slot=>draft[slot.key]).filter(Boolean)});
  root.innerHTML=`<div class="mission-planner">
    <header class="planner-header"><div><div class="eyebrow">${esc(m.rank||'')} RANK · ${esc(title(m.mission_form||'operation'))}</div><h2>${esc(m.name)}</h2></div><span class="planner-time">${m.has_decisions?'Interactive story':m.combat_encounter?'Tactical battle':(m.duration_seconds?`${Math.ceil(m.duration_seconds/60)} min`:'Play immediately')}</span></header>
    <div class="planner-body"><aside class="planner-brief"><div class="eyebrow">THE CONTRACT</div><p>${esc(m.description)}</p>${m.objective?`<div class="planner-objective"><b>Objective</b><p>${esc(m.objective)}</p></div>`:''}
      ${m.combat_encounter?`<div class="combat-notice"><b>${esc(m.combat_encounter.name)}</b><p>${esc(m.combat_encounter.description)}</p><small>Positioning and objectives decide the outcome.</small></div>`:`<div class="planner-objective"><b>${esc(statLabel)} check · DC ${m.difficulty}</b><p>The strongest selected character leads. Other capable party members can support the roll.</p></div>`}
      ${(m.reward_preview||[]).length?`<h3>Possible rewards</h3><div class="chips">${m.reward_preview.map(x=>`<span>${esc(x)}</span>`).join('')}</div><small class="muted">Item drops are rolled; previews aren't guaranteed rewards.</small>`:''}
      ${(m.requirements||[]).length?`<h3>Requirements</h3><ul>${m.requirements.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}
      ${(m.visible_hints||[]).length?`<details><summary>Contract clues</summary><ul>${m.visible_hints.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details>`:''}
      ${m.story_thread?.name?`<details><summary>${esc(m.story_thread.name)}</summary><p>${esc(m.story_thread.context||'')}</p></details>`:''}
      ${m.world_trigger?`<p class="world-consequence">Uncovered by ${esc(m.world_trigger.triggered_by)} after ${esc(m.world_trigger.source_mission)}.</p>`:''}
      ${m.chain?`<p class="chain-deadline">Private chain · chapter ${m.chain.step}/${m.chain.total}<br>Claim by ${new Date(m.chain.claim_by*1000).toLocaleString()}</p>`:''}
    </aside><section class="planner-assignment"><div class="planner-section-heading"><div><div class="eyebrow">BUILD YOUR LINEUP</div><h3>Assign ${m.party_size} character${m.party_size===1?'':'s'}</h3></div><button type="button" data-suggest-team>Suggest team</button></div>
      <p class="planner-stamina-help">Costs ${staminaCosts[m.rank]||1} stamina per character, including bodyguards and mercenaries. Depart with at least 1 point; you may borrow the rest. Recover 1 point every 18 seconds, including offline.</p><div class="planner-hiring"><button type="button" data-hire-mercenaries disabled>Hire mercenaries</button><small data-hire-info>Assign a crew member to open your hiring board.</small></div><div class="planner-slots"></div><div class="planner-roster-toolbar"><label class="planner-search"><span>Search available roster</span><input type="search" placeholder="Name, race, specialty…" autocomplete="off" data-planner-search></label><label><span>Sort</span><select data-planner-sort><option value="fit">Best fit first</option><option value="name">Name A–Z</option></select></label></div>
      <div class="planner-candidate-heading"></div><div class="planner-candidates"></div><div class="planner-pages"></div>
    </section></div><footer class="planner-footer"><div id="odds" class="odds" aria-live="polite">Choose a slot, then a character. Only available characters are listed.</div><div class="planner-claim"><span data-planner-count></span><button id="claim-mission" class="primary big" disabled>${m.has_decisions?'Begin Contract':m.combat_encounter?'Begin Tactical Battle':'Start Expedition'}</button></div></footer>
    ${debug?`<details class="planner-debug"><summary>Debug resolution</summary><div class="debug-complete"><small>Force an outcome and bypass requirements.</small>${['critical_failure','failure','success','critical_success'].map(outcome=>`<button data-debug-available="${outcome}">${title(outcome)}</button>`).join('')}</div></details>`:''}
  </div>`;

  const get=s=>root.querySelector(s);
  const mobileBrief=document.createElement('details');mobileBrief.className='planner-mobile-brief';
  mobileBrief.innerHTML='<summary>Contract briefing, rewards & requirements</summary>'+get('.planner-brief').innerHTML;
  get('.planner-body').prepend(mobileBrief);
  function renderSlots(){
    get('.planner-slots').innerHTML=slots.map(slot=>{
      const c=characters.find(c=>c.id===draft[slot.key]);
      return `<div class="planner-slot ${slot.key===active?'active':''} ${c?'filled':''} ${slot.guard?'guard-slot':''}"><button data-planner-slot="${esc(slot.key)}"><span class="planner-slot-label">${esc(slot.label)}${slot.guard?' · optional':''}</span><span class="planner-slot-person">${c?`${portrait(c)}<span><b>${esc(c.name)}</b><small>${esc(scoreText(c,slot))}</small>${staminaHTML(c)}</span>`:'<span class="slot-empty">＋ Choose character</span>'}</span>${slot.metric?`<small>Recommended ${slot.metric==='constitution'?'CON':slot.metric.toUpperCase()} ${slot.recommended}</small>`:''}</button>${c?`<button class="planner-remove" data-planner-remove="${esc(slot.key)}" aria-label="Remove ${esc(c.name)} from ${esc(slot.label)}">×</button>`:''}</div>`;
    }).join('');
    const ownAssigned=primary.some(slot=>characters.some(c=>c.id===draft[slot.key]&&!c.temporary_mercenary));
    get('[data-hire-mercenaries]').disabled=!ownAssigned||!onHire;
    const fee=selection().mercenary_ids.reduce((sum,id)=>sum+(hired.get(id)?.mercenary_fee||0),0);
    get('[data-hire-info]').textContent=fee?`${selection().mercenary_ids.length} hired ? ${fee} gold on departure ? mission check penalty`:ownAssigned?'Fill a missing slot with a temporary hired sword.':'Assign a crew member to open your hiring board.';
    get('[data-planner-count]').textContent=`${selection().party_ids.length}/${m.party_size} assigned${guards.length?` · ${selection().bodyguard_ids.length}/${guards.length} bodyguards`:''}`;
    root.querySelectorAll('[data-planner-slot]').forEach(btn=>btn.onclick=()=>{active=btn.dataset.plannerSlot;page=0;renderSlots();renderCandidates()});
    root.querySelectorAll('[data-planner-remove]').forEach(btn=>btn.onclick=()=>{delete draft[btn.dataset.plannerRemove];active=btn.dataset.plannerRemove;renderSlots();renderCandidates();onChange()});
  }
  function renderCandidates(){
    const slot=slots.find(s=>s.key===active)||slots[0];
    let candidates=rankedCandidates(characters,c=>score(c,slot),query).filter(({character:c})=>!slots.some(s=>s.key!==active&&draft[s.key]===c.id));
    if(sort==='name')candidates.sort((a,b)=>a.character.name.localeCompare(b.character.name));
    const pages=Math.max(1,Math.ceil(candidates.length/pageSize));page=Math.min(page,pages-1);
    get('.planner-candidate-heading').innerHTML=`<b>${esc(slot.label)} candidates</b><span>${candidates.length} available · ${slot.guard?'DPS + CON · combat backup only':slot.metric?`ranked by ${slot.metric==='constitution'?'CON':slot.metric.toUpperCase()}`:`ranked by ${esc(statLabel)}`}</span>${slot.description?`<small>${esc(slot.description)}</small>`:''}${slot.guard?'<small>Bodyguards do not improve mission rolls.</small>':''}`;
    get('.planner-candidates').innerHTML=candidates.slice(page*pageSize,(page+1)*pageSize).map(({character:c},index)=>{
      const assigned=slots.find(s=>draft[s.key]===c.id),chosen=assigned?.key===active,locked=assigned&&!chosen;
      return `<button class="planner-candidate ${chosen?'selected':''}" data-planner-character="${esc(c.id)}" ${locked?'disabled':''}>${portrait(c)}<span class="candidate-info"><b>${esc(c.name)}</b><small>${esc(c.race)} · ${esc(c.specialty||'Adventurer')}</small><span>${esc(scoreText(c,slot))}${slot.metric==='dps'?` · ${esc(metrics(c).weapon)}`:''}</span>${staminaHTML(c)}${locked?`<em>Assigned: ${esc(assigned.label)}</em>`:chosen?'<em>Selected</em>':sort==='fit'&&page===0&&index===0?'<em>Top available fit</em>':''}</span><span class="candidate-select">${chosen?'✓':locked?'':'＋'}</span></button>`;
    }).join('')||`<div class="planner-empty"><b>${query?'No matching available characters':'No available characters'}</b><p>${query?'Try another name, race, or specialty.':'Characters on missions, injured, or below 1 stamina cannot join.'}</p></div>`;
    get('.planner-pages').innerHTML=`<small>Showing ${candidates.length?page*pageSize+1:0}–${Math.min((page+1)*pageSize,candidates.length)} of ${candidates.length} · ${characters.filter(c=>c.status!=='idle'||!staminaView(c).eligible).length} unavailable hidden</small><div><button data-page-back ${page===0?'disabled':''} aria-label="Previous roster page">‹</button><span>${page+1} / ${pages}</span><button data-page-next ${page===pages-1?'disabled':''} aria-label="Next roster page">›</button></div>`;
    get('[data-page-back]').onclick=()=>{page--;renderCandidates()};get('[data-page-next]').onclick=()=>{page++;renderCandidates()};
    root.querySelectorAll('[data-planner-character]').forEach(btn=>btn.onclick=()=>{
      const id=btn.dataset.plannerCharacter;
      if(draft[active]===id)delete draft[active];else{draft[active]=id;const next=slots.find(s=>!draft[s.key]&&!s.guard);if(next){active=next.key;page=0}}
      renderSlots();renderCandidates();onChange();
    });
  }
  get('[data-hire-mercenaries]').onclick=()=>onHire();
  get('[data-planner-search]').oninput=e=>{query=e.target.value;page=0;renderCandidates()};
  get('[data-planner-sort]').onchange=e=>{sort=e.target.value;page=0;renderCandidates()};
  get('[data-suggest-team]').onclick=()=>{
    const suggested=suggestAssignments(characters,primary,score);
    for(const slot of primary)delete draft[slot.key];
    Object.assign(draft,suggested);
    for(const slot of guards)if(Object.values(suggested).includes(draft[slot.key]))delete draft[slot.key];
    active=primary[0].key;page=0;renderSlots();renderCandidates();onChange();
  };
  root.querySelectorAll('[data-debug-available]').forEach(btn=>btn.onclick=()=>onClaimDebug(btn.dataset.debugAvailable,selection()));
  renderSlots();renderCandidates();
  return {selection,tick(now){if(now>=readyAt){readyAt=nextReady();renderCandidates();onChange()}},addMercenary(c){
    if(Object.values(draft).includes(c.id))throw new Error('This mercenary is already assigned');
    const slot=primary.find(s=>!draft[s.key])||guards.find(s=>!draft[s.key]);
    if(!slot)throw new Error('Remove a selected character to free a party or bodyguard slot');
    hired.set(c.id,c);characters=characters.filter(x=>x.id!==c.id).concat(c);draft[slot.key]=c.id;
    renderSlots();renderCandidates();onChange();
  },refresh(nextCharacters){
    for(const c of nextCharacters)if(!c.temporary_mercenary)hired.delete(c.id);
    characters=[...nextCharacters.filter(c=>!c.temporary_mercenary),...hired.values()];
    for(const slot of slots)if(draft[slot.key]&&!characters.some(c=>c.id===draft[slot.key]&&c.status==='idle'))delete draft[slot.key];
    readyAt=nextReady();renderSlots();renderCandidates();onChange();
  }};
}
