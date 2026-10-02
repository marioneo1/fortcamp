const replies=new Map();
const openCards=new Set();
const profileCards=new Set();
export const pendingPrisonActions=new Set();
export function agreementCost(p,items={}){
 const r=p.recruitment;
 if(r.route==='heirloom')return items[r.requested_item]?.name||r.requested_item?.replaceAll('_',' ')||'Field Pack';
 return `${r.cost} ${{debt:'gold',rebuild:'wood',wounded:'medicine'}[r.route]||'supplies'}`;
}
export function prisonerConfirmation(p,action,items={}){
 if(action==='sell')return {title:`Sell ${p.name}?`,message:'This removes the prisoner from your custody. They will no longer be available to recruit.',details:[['You receive',`${p.sale_value??8} gold`]],confirmLabel:'Sell prisoner',danger:true};
 return {title:`Fulfill ${p.name}'s agreement?`,message:'The payment is consumed once when you confirm.',details:[['You give',agreementCost(p,items)],['Result',p.recruitment.requires_proof?'Unlock their personal task. Complete it before recruiting.':'Their agreement is fulfilled. You can then offer recruitment.']],confirmLabel:'Fulfill agreement'};
}
export function prisonerRecruitmentMarkup(p,esc,items={},context={}){
 const r=p.recruitment;if(!r)return '';
 const quest=['rival','former','proof','rescue'].includes(r.route)||r.requires_proof&&r.payment_met,secured=p.holding==='prison_cell';
 const ready=secured&&(r.terms_met||!r.requires_terms&&r.resistance<=0),profile=profileCards.has(p.id);
 const button=(action,label,enabled=true)=>`<button data-prisoner-action="${action}" data-prisoner-id="${esc(p.id)}" ${enabled&&!pendingPrisonActions.has(p.id)?'':'disabled'}>${label}</button>`;
 return `<details class="prison-recruitment" data-prison-talk="${esc(p.id)}" ${openCards.has(p.id)?'open':''}><summary>Recruitment <span>${ready?'Ready to join':r.requires_terms?'Personal agreement required':`Resistance ${r.resistance}`}</span></summary>
 <div class="prison-detail-tabs" role="tablist" aria-label="Prisoner details"><button role="tab" id="prison-talk-tab-${esc(p.id)}" aria-controls="prison-talk-panel-${esc(p.id)}" data-prison-view="talk" aria-selected="${!profile}">Conversation &amp; terms</button><button role="tab" id="prison-profile-tab-${esc(p.id)}" aria-controls="prison-profile-panel-${esc(p.id)}" data-prison-view="profile" aria-selected="${profile}">Recruit profile</button></div>
 <section role="tabpanel" id="prison-talk-panel-${esc(p.id)}" aria-labelledby="prison-talk-tab-${esc(p.id)}" data-prison-panel="talk" ${profile?'hidden':''}><div class="prison-talk-reply" role="status">${esc(replies.get(p.id)||(r.revealed?r.terms_text:null)||'Speak with the prisoner to learn what they need.')}</div>
 ${r.revealed?`<div class="prison-terms"><small>PERSONAL AGREEMENT</small><b>${r.terms_met?'Agreement fulfilled':quest?'Complete their personal task':`Requested: ${esc(agreementCost(p,items))}`}</b><p>${r.terms_met?'You can now offer a place in your roster.':quest?(r.quest_id?'Their task is on Private Contracts. Complete it to fulfill this agreement.':'Request their personal task to add it to Private Contracts.'):r.requires_proof?'Payment unlocks a personal task. They must also see it completed.':'Payment is consumed once. Equipped items cannot be offered.'}</p></div>`:''}
 <div class="prisoner-actions prison-primary-actions">${button('talk',r.revealed?'Talk again':'Discuss their terms')}${r.revealed&&!r.terms_met?button(quest?'quest':'fulfill',quest?(r.quest_id?'Open Private Contract':'Request personal task'):'Fulfill agreement',secured):''}${button('recruit','Offer recruitment',ready)}</div>
 <div class="prison-negotiation"><div><b>Warden negotiation</b><span>Resistance ${r.resistance}</span></div><progress aria-label="Remaining resistance" value="${Math.max(0,r.resistance)}" max="${Math.max(r.resistance,r.requires_terms?36:18)}"></progress><p>${r.requires_terms?'Negotiation lowers resistance, but their personal agreement is still required.':'Reach zero resistance to recruit without paying their requested terms.'} Wardens use effective INT. Each warden can negotiate once every 30 minutes across all their prisoners.</p>${button('negotiate','Negotiate',secured&&r.resistance>0&&(context.negotiationReady??true))}</div>
 ${!secured?'<p class="prison-custody-note">Secure this prisoner in a cell before negotiating or recruiting.</p>':''}${context.wardenLabel?`<p class="prison-warden-status">${esc(context.wardenLabel)}</p>`:''}</section>
 <section role="tabpanel" id="prison-profile-panel-${esc(p.id)}" aria-labelledby="prison-profile-tab-${esc(p.id)}" data-prison-panel="profile" ${profile?'':'hidden'}><div class="prison-attribute-grid">${Object.entries(r.candidate?.attributes||{}).map(([a,v])=>`<div><small>${esc(a.toUpperCase())}</small><b>${esc(v)}</b></div>`).join('')}</div><p class="prison-profile-note">${esc(r.profile_note||'Attributes shown are their starting recruit profile.')}</p><div class="prison-terms"><small>STARTING LOYALTY</small><b>${r.terms_met||r.requires_terms?'80 after their agreement':'70 through negotiation / 80 through an agreement'}</b></div></section></details>`;
}
export function rememberPrisonReply(id,text){if(text)replies.set(id,text);openCards.add(id)}
export function bindPrisonCards(root){root.querySelectorAll('[data-prison-talk]').forEach(d=>{
 d.ontoggle=()=>{if(d.open)openCards.add(d.dataset.prisonTalk);else openCards.delete(d.dataset.prisonTalk)};
 d.querySelectorAll('[data-prison-view]').forEach(button=>{button.onkeydown=event=>{const tabs=[...d.querySelectorAll('[data-prison-view]')],i=tabs.indexOf(button),next=event.key==='Home'?0:event.key==='End'?tabs.length-1:event.key==='ArrowRight'?(i+1)%tabs.length:event.key==='ArrowLeft'?(i+tabs.length-1)%tabs.length:null;if(next!==null){event.preventDefault();tabs[next].click();tabs[next].focus()}};button.onclick=()=>{
  const profile=button.dataset.prisonView==='profile';if(profile)profileCards.add(d.dataset.prisonTalk);else profileCards.delete(d.dataset.prisonTalk);
  d.querySelectorAll('[data-prison-view]').forEach(b=>b.setAttribute('aria-selected',String(b===button)));
  d.querySelectorAll('[data-prison-panel]').forEach(panel=>panel.hidden=panel.dataset.prisonPanel!==button.dataset.prisonView);
 };});
})}

export function prisonWorkspaceMarkup(prisoners,{state,selectedId,capacity,esc,portrait,format,items}){
 const all=state.prisoners||[],secured=all.filter(p=>p.holding==='prison_cell'),stockade=all.filter(p=>p.holding==='temporary_stockade');
 const selected=prisoners.find(p=>p.id===selectedId),now=Math.floor(Date.now()/1000);
 const remaining=p=>p.holding==='temporary_stockade'?Math.max(0,(p.stockade_expires_at||0)-now):(p.stockade_remaining_seconds??3600);
 const ready=p=>p.holding==='prison_cell'&&(p.recruitment?.terms_met||!p.recruitment?.requires_terms&&p.recruitment?.resistance<=0);
 const status=p=>p.holding==='temporary_stockade'?`Stockade · ${format(remaining(p))} left`:ready(p)?'Ready to recruit':p.recruitment?.requires_terms?'Agreement required':'Secured';
 const list=prisoners.map(p=>`<button class="prison-list-row ${p.id===selectedId?'selected':''} ${p.holding==='temporary_stockade'?'urgent':''}" data-prison-select="${esc(p.id)}" aria-pressed="${p.id===selectedId}">${portrait(p)}<span><b>${esc(p.name)}</b><small>${esc(p.race)}${p.boss?' · Boss':''}</small><em>${esc(status(p))}</em></span></button>`).join('');
 let detail='<div class="prison-empty"><h3>No prisoners to display</h3><p>Capture an opponent and bring them back, or change your search filters.</p></div>';
 if(selected){
  const p=selected,inStockade=p.holding==='temporary_stockade',full=secured.length>=capacity;
  const index=[...secured].sort((a,b)=>(a.captured_at||0)-(b.captured_at||0)||a.id.localeCompare(b.id)).findIndex(q=>q.id===p.id);
  const cell=state.buildings.filter(b=>b.type==='prison_cell').sort((a,b)=>a.id.localeCompare(b.id))[Math.floor(index/4)];
  const warden=state.characters.find(c=>cell?.assigned?.includes(c.id)&&c.status==='idle');
  const cooldown=warden?Math.max(0,(state.prison_warden_sessions?.[warden.id]||0)-now):0;
  const wardenLabel=inStockade?'No warden coverage in the stockade.':!warden?'Assign an available warden through Manage prison facilities.':`${warden.name} · ${cooldown?`Next session in ${format(cooldown)}`:'Ready to negotiate'}`;
  const swaps=secured.filter(q=>q.id!==p.id).map(q=>`<option value="${esc(q.id)}">${esc(q.name)} · ${format(remaining(q))} stockade time</option>`).join('');
  detail=`<article class="prison-selected"><header class="prison-identity">${portrait(p,true)}<div><div class="eyebrow">${p.boss?'PRIORITY CAPTIVE':'IN YOUR CUSTODY'}</div><h3>${esc(p.name)}</h3><p>${esc(p.race)} · ${esc(p.recruitment?.rank||'E')}-rank</p><span class="prison-status-badge">${esc(status(p))}</span></div></header>${inStockade?`<div class="prison-stockade-alert"><b>${format(remaining(p))} before removal</b><p>Secure or sell this prisoner before their stockade time runs out. Swapping never resets the timer.</p></div>`:''}${prisonerRecruitmentMarkup(p,esc,items,{wardenLabel,negotiationReady:!!warden&&!cooldown&&!inStockade})}<details class="prison-custody"><summary>Holding &amp; sale <span>${p.sale_value??8} gold sale value</span></summary><p>Moving a prisoner to the stockade resumes their remaining one-hour timer. Selling permanently removes them.</p><div class="prisoner-actions">${inStockade&&capacity?`${full?`<label>Move this prisoner out of a cell<select data-prisoner-swap="${esc(p.id)}"><option value="">Choose a prisoner to swap…</option>${swaps}</select></label>`:''}<button data-prisoner-action="secure" data-prisoner-id="${esc(p.id)}" ${full?'disabled':''}>${full?'Swap into cell':'Secure in cell'}</button>`:!inStockade?`<button data-prisoner-action="stockade" data-prisoner-id="${esc(p.id)}">Move to stockade</button>`:'<p>Build a Prison Cell to secure this prisoner.</p>'}<button class="danger" data-prisoner-action="sell" data-prisoner-id="${esc(p.id)}">Sell prisoner · ${p.sale_value??8} gold</button></div></details></article>`;
 }
 return `<section class="prison-workspace"><div class="prison-dashboard"><div><small>SECURE CELLS</small><b>${secured.length} / ${capacity}</b></div><div><small>FREE SPACES</small><b>${Math.max(0,capacity-secured.length)}</b></div><div class="${stockade.length?'urgent':''}"><small>TEMPORARY STOCKADE</small><b>${stockade.length}</b></div></div><div class="prison-workspace-body"><nav class="prison-selection" aria-label="Choose a prisoner"><div class="prison-list-heading">${prisoners.length} ${prisoners.length===1?'prisoner':'prisoners'}</div>${list||'<p>No matching prisoners.</p>'}</nav><div class="prison-detail">${detail}</div></div></section>`;
}
