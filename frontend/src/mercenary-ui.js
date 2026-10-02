import {confirmAction} from './confirmation-ui.js';
let activeMarket=null;

export async function openMercenaryMarket({api,esc,portrait,onSelect,onRecruit,onError,selectedIds=[]}){
  if(activeMarket?.isConnected)return;
  const dialog=document.createElement('dialog');dialog.className='mercenary-market';
  activeMarket=dialog;
  dialog.innerHTML='<header><div><div class="eyebrow">PRIVATE HIRING BOARD</div><h2>Hired swords</h2></div><button data-close aria-label="Close hiring board">×</button></header><p>Hire for one contract. Payment is taken when the expedition starts. Your own crew remains the better long-term choice.</p><p class="muted">Hires impose −1 to mission checks each (maximum −4), including bodyguards. The group may betray you before departure. Repeated jobs build trust and lower fees.</p><div data-market-list>Loading your contacts…</div>';
  document.body.append(dialog);dialog.showModal();
  const close=()=>{dialog.close();dialog.remove();if(activeMarket===dialog)activeMarket=null};dialog.querySelector('[data-close]').onclick=close;
  dialog.addEventListener('cancel',event=>{event.preventDefault();close()});
  dialog.onclick=event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)close()}};
  try{
    const {offers,state}=await api('/api/mercenaries');
    if(!dialog.isConnected)return;
    dialog.querySelector('[data-market-list]').innerHTML=offers.map(o=>`<article class="mercenary-card">${portrait(o.character)}<div><h3>${esc(o.character.name)} <small>${esc(o.rank)} rank</small></h3><p>${esc(o.character.specialty)} · ${esc(o.character.race)}</p><small>Trust ${o.relationship}/100 · Betrayal ${o.betrayal_chance}%<br>${o.relationship_required} trust unlocks permanent service for ${o.buyout} gold.</small></div><div class="mercenary-buttons"><button data-hire="${esc(o.id)}" ${o.available&&!selectedIds.includes(o.id)?'':'disabled'}>${selectedIds.includes(o.id)?'Assigned':`Hire · ${o.fee} gold`}</button><button data-recruit="${esc(o.id)}" ${o.available&&o.relationship>=o.relationship_required?'':'disabled'}>Permanent service</button>${!o.available?`<small>${o.recovering_until>Date.now()/1000?'Recovering':'On a contract'}</small>`:''}</div></article>`).join('')+`<p>Your purse: <b>${state.resources.gold||0} gold</b>. Hiring several adds up to 2 percentage points of betrayal risk per additional hire. Trust reduces this; the group risk is capped at 25%.</p>`;
    dialog.querySelectorAll('[data-hire]').forEach(button=>button.onclick=()=>{
      const offer=offers.find(o=>o.id===button.dataset.hire);
      try{onSelect({...offer.character,mercenary_fee:offer.fee,mercenary_betrayal:offer.betrayal_chance});close()}catch(error){onError(error.message)}
    });
    dialog.querySelectorAll('[data-recruit]').forEach(button=>button.onclick=async()=>{
      const o=offers.find(o=>o.id===button.dataset.recruit);
      if(!await confirmAction({title:`Recruit ${o.character.name}?`,message:`Permanent service costs ${o.buyout} gold. They join your roster with their weapon.`,confirmLabel:`Recruit · ${o.buyout} gold`}))return;
      button.disabled=true;
      try{const result=await api(`/api/mercenaries/${encodeURIComponent(o.id)}/recruit`,{method:'POST',body:'{}'});onRecruit(result.state);close()}catch(error){onError(error.message);button.disabled=false}
    });
  }catch(error){close();onError(error.message)}
}
