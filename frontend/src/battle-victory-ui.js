export function victoryMarkup(b,{expanded=false,escape}){
  if(!b.battle_won&&!b.decision_pending)return '';
  const esc=escape;
  if(!b.decision_pending&&!expanded)return `<div class="battle-victory-minimized"><span>Objective secured</span><button data-victory-expand>Finish operation</button></div>`;
  return `<div class="battle-victory-overlay"><section class="victory-decision" role="dialog" aria-label="Objective secured"><div><div class="eyebrow">PRIMARY OBJECTIVE SECURED</div><h3>${esc(b.victory_title||'Victory is secured.')}</h3><p>${esc(b.victory_description||'Withdraw now or continue pursuing optional objectives.')}</p></div><div><button data-combat-action="claim_victory" class="claim-victory">${esc(b.claim_victory_label||'Complete Mission')}</button>${b.decision_pending?'<button data-combat-action="continue_pursuit">Continue for optional objectives</button>':'<button data-victory-minimize>Continue for optional objectives</button>'}</div></section></div>`;
}
