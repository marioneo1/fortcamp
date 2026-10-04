export function zoneOverlay(zones,escape){
  return (zones||[]).flatMap(zone=>zone.cells.map(cell=>`<div class="battle-zone zone-${escape(zone.kind)}" style="grid-column:${cell.x+1};grid-row:${cell.y+1}" title="${escape(zone.name)} | ${escape(zone.owner_name)} | ${zone.remaining} owner activations | ${escape(zone.description)}"><span>${escape(zone.name)}</span></div>`)).join('');
}
export function zoneCellHelp(zones,x,y){
  return (zones||[]).filter(z=>z.cells.some(p=>p.x===x&&p.y===y)).map(z=>`${z.name} | ${z.owner_name} | ${z.remaining} owner activations | ${z.description} | `).join('');
}
