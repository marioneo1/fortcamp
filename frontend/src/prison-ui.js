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
export function prisonerRecruitmentMarkup(p,esc,items={}){
 const r=p.recruitment;if(!r)return '';
 const quest=['rival','former','proof','rescue'].includes(r.route)||r.requires_proof&&r.payment_met,secured=p.holding==='prison_cell';
 const ready=secured&&(r.terms_met||!r.requires_terms&&r.resistance<=0),profile=profileCards.has(p.id);
 const button=(action,label,enabled=true)=>`<button data-prisoner-action="${action}" data-prisoner-id="${esc(p.id)}" ${enabled&&!pendingPrisonActions.has(p.id)?'':'disabled'}>${label}</button>`;
 return `<details class="prison-recruitment" data-prison-talk="${esc(p.id)}" ${openCards.has(p.id)?'open':''}><summary>Recruitment <span>${ready?'Ready to join':r.requires_terms?'Personal agreement required':`Resistance ${r.resistance}`}</span></summary>
 <div class="prison-detail-tabs" role="tablist" aria-label="Prisoner details"><button role="tab" id="prison-talk-tab-${esc(p.id)}" aria-controls="prison-talk-panel-${esc(p.id)}" data-prison-view="talk" aria-selected="${!profile}">Conversation &amp; terms</button><button role="tab" id="prison-profile-tab-${esc(p.id)}" aria-controls="prison-profile-panel-${esc(p.id)}" data-prison-view="profile" aria-selected="${profile}">Recruit profile</button></div>
 <section role="tabpanel" id="prison-talk-panel-${esc(p.id)}" aria-labelledby="prison-talk-tab-${esc(p.id)}" data-prison-panel="talk" ${profile?'hidden':''}><div class="prison-talk-reply" role="status">${esc(replies.get(p.id)||(r.revealed?r.terms_text:null)||'Speak with the prisoner to learn what they need.')}</div>
 ${r.revealed?`<div class="prison-terms"><small>PERSONAL AGREEMENT</small><b>${r.terms_met?'Agreement fulfilled':quest?'Complete their personal task':`Requested: ${esc(agreementCost(p,items))}`}</b><p>${r.terms_met?'You can now offer a place in your roster.':quest?'This task is on Private Contracts and belongs to this prisoner.':r.requires_proof?'Payment unlocks a personal task. They must also see it completed.':'Payment is consumed once. Equipped items cannot be offered.'}</p></div>`:''}
 <div class="prisoner-actions prison-primary-actions">${button('talk',r.revealed?'Talk again':'Discuss their terms')}${r.revealed&&!r.terms_met?button(quest?'quest':'fulfill',quest?'Open Private Contract':'Fulfill agreement',secured):''}${button('recruit','Offer recruitment',ready)}</div>
 <div class="prison-negotiation"><div><b>Warden negotiation</b><span>Resistance ${r.resistance}</span></div><progress aria-label="Remaining resistance" value="${Math.max(0,r.resistance)}" max="${Math.max(r.resistance,r.requires_terms?36:18)}"></progress><p>${r.requires_terms?'Negotiation lowers resistance, but their personal agreement is still required.':'Reach zero resistance to recruit without paying their requested terms.'} Wardens use effective INT. Each warden can negotiate once every 30 minutes across all their prisoners.</p>${button('negotiate','Negotiate',secured&&r.resistance>0)}</div>
 ${!secured?'<p class="prison-custody-note">Secure this prisoner in a cell before negotiating or recruiting.</p>':''}</section>
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
