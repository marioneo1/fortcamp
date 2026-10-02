export function battleSupplyPanel(battle,esc){
  const actor=battle.units?.[battle.current_unit_id];
  if(!actor)return '';
  const stock=new Map();
  for(const supply of battle.supplies||[]){const group=stock.get(supply.item_id)||{...supply,count:0};group.count++;stock.set(supply.item_id,group)}
  const remaining=battle.supply_uses_remaining??3;
  const targets=(battle.supply_targets||[]).map(id=>battle.units[id]).filter(Boolean);
  return `<details class="battle-supplies"><summary>Battle supplies · ${remaining}/3 uses left</summary><p>One action, range 1. Supplies are consumed immediately. Does not revive; auto-battle keeps your supplies.</p>${[...stock.values()].map(s=>`<article><b>${esc(s.name)} ×${s.count}</b><small>${s.heal?`${s.heal} HP · `:''}${s.cleanses.length?`Treats ${esc(s.cleanses.join(', '))}`:'Healing'}</small><div>${targets.map(t=>{const useful=(s.heal>0&&t.hp<t.max_hp)||(t.statuses||[]).some(x=>s.cleanses.includes(x.id));return `<button data-supply="${esc(s.instance_id)}" data-supply-target="${esc(t.id)}" ${remaining&&useful&&!actor.acted?'':'disabled'}>${esc(t.id===actor.id?'Self':t.name)} · ${t.hp}/${t.max_hp} HP</button>`}).join('')}</div></article>`).join('')||'<p>No supplies in inventory. Buy dressings from Camp Trade or find them on missions.</p>'}</details>`;
}
