export const staminaCosts={E:1,D:3,C:5,B:10,A:50,S:100};
export function staminaView(character,now=Date.now()/1000){
  const saved=character.stamina||{balance:100,updated_at:now};
  const current=Math.min(100,Number(saved.balance)+Math.max(0,now-Number(saved.updated_at))/18);
  return {current,eligible:current>=1,readyIn:Math.max(0,Math.ceil((1-current)*18)),fullIn:Math.max(0,Math.ceil((100-current)*18))};
}
export function staminaLabel(character,now=Date.now()/1000){
  const s=staminaView(character,now),wait=s.eligible?s.fullIn:s.readyIn;
  return `Stamina ${Math.floor(s.current)}/100${wait?` · ${s.eligible?'Full':'Ready'} in ${Math.floor(wait/60)}m ${wait%60}s`:''}`;
}
export function staminaHTML(character){
  const saved=character.stamina||{balance:100,updated_at:Date.now()/1000};
  return `<small class="stamina-readout" data-stamina-balance="${Number(saved.balance)}" data-stamina-at="${Number(saved.updated_at)}" title="Recover 1 point every 18 seconds, including offline. Depart with at least 1 point; borrowing delays your next departure.">${staminaLabel(character)}</small>`;
}
