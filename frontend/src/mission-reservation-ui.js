import {escapeHTML as esc,boardIcon,rankSeal} from './mission-board-ui.js';

// Retrying a reservation is safe: the server returns the existing owned contract.
export async function reserveContract(api,id,{delay=ms=>new Promise(r=>setTimeout(r,ms)),onRetry=()=>{}}={}){
  for(let attempt=0;attempt<2;attempt++){
    try{return await api(`/api/missions/${encodeURIComponent(id)}/claim`,{method:'POST',body:'{}'})}
    catch(error){
      if(attempt||![502,503,504].includes(error.status))throw error;
      onRetry();await delay(600);
    }
  }
}

export function reservationMarkup(m,{cost,remaining,phase}){
  const mode=m.combat_encounter?'Tactical battle':m.has_decisions?'Story choices':'Expedition check';
  const phaseLabel={wave1:'Opening wave',wave2:'Second wave',free:'Free-for-all'}[phase]||'Current wave';
  return `<section class="reservation-panel">
    <header class="reservation-heading">${rankSeal(m.rank)}<div><div class="eyebrow">PUBLIC CONTRACT · ${esc(mode)}</div><h2>${esc(m.name)}</h2><span>${m.party_size} character${m.party_size===1?'':'s'} needed when you start</span></div></header>
    <div class="reservation-columns"><div class="reservation-brief"><h3>The job</h3><p>${esc(m.description)}</p>${m.objective?`<div class="reservation-objective"><b>Objective</b><p>${esc(m.objective)}</p></div>`:''}${m.story_thread?.context?`<p class="reservation-context">${esc(m.story_thread.context)}</p>`:''}
    <div class="reservation-rewards"><h3>${boardIcon('utility_reward')}Possible rewards</h3><div>${(m.reward_preview||[]).map(p=>`<span>${esc(p)}</span>`).join('')||'<span>Discover rewards through the contract</span>'}</div><small>Special drops are rolled, even on a successful expedition.</small></div>
    ${(m.requirements||[]).length?`<details><summary>Requirements when starting</summary><ul>${m.requirements.map(r=>`<li>${esc(r)}</li>`).join('')}</ul></details>`:''}</div>
    <aside class="reservation-ticket"><div class="eyebrow">${esc(phaseLabel)}</div><div class="reservation-cost"><b>${cost}</b><span>Contract Point${cost===1?'':'s'}</span></div><div class="reservation-balance"><span>Your allowance</span><b>${remaining} left</b></div><p>Save this contract now.<br>Choose your team when you're ready.</p><div class="reservation-window">${boardIcon('utility_clock')}<span><b>24 hours to start</b><small>Your characters stay available until departure.</small></span></div><small>Abandoning a claimed contract does not refund points.</small></aside></div>
    <footer class="reservation-footer"><div><p id="reservation-status" role="status" aria-live="polite">${remaining<cost?'Not enough points in this wave.':'Ready to save to your Private Contracts.'}</p><small id="reservation-help">Claiming secures the contract. It does not start the expedition.</small></div><button id="reserve-contract" class="primary" ${remaining<cost?'disabled':''}>Claim contract <span>· ${cost} point${cost===1?'':'s'}</span></button></footer>
  </section>`;
}

export function mountReservation(root,m,{budget,cost,api,onRefresh,onOpen,onBrowse}){
  root.innerHTML=reservationMarkup(m,{cost,remaining:budget?.remaining??5,phase:budget?.phase});
  const button=root.querySelector('#reserve-contract'),status=root.querySelector('#reservation-status'),help=root.querySelector('#reservation-help');
  button.onclick=async()=>{
    if(button.disabled)return;
    status.classList.remove('reservation-error','reservation-saved');
    button.disabled=true;button.textContent='Saving contract…';status.textContent='Securing your place on the board…';
    try{
      const data=await reserveContract(api,m.id,{onRetry:()=>{status.textContent='The server connection was interrupted. Retrying once…'}});
      status.textContent='Saved to your Private Contracts.';status.classList.add('reservation-saved');help.textContent='Assign a team now, or return to this contract later.';
      button.textContent='Assign team now';button.disabled=false;button.onclick=()=>onOpen(data.mission);
      const browse=document.createElement('button');browse.className='reservation-browse';browse.textContent='Keep browsing';browse.onclick=onBrowse;button.before(browse);
      // A refresh failure must not turn an already successful claim into a retry.
      try{await onRefresh()}catch{help.textContent='Your contract is saved. Refresh the board to update your allowance.'}
    }catch(error){
      status.textContent=[502,503,504].includes(error.status)?'The game server is temporarily unavailable. Try again shortly.':error.message;
      status.classList.add('reservation-error');button.disabled=false;button.textContent='Retry claim';
    }
  };
}
