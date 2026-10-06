import {caltropsArtwork} from './caltrops-art.js';
export function zoneOverlay(zones,escape){
  return (zones||[]).filter(z=>z.cells?.length).map((zone,index)=>{
    const x=Math.min(...zone.cells.map(c=>c.x)),y=Math.min(...zone.cells.map(c=>c.y));
    const w=Math.max(...zone.cells.map(c=>c.x))-x+1,h=Math.max(...zone.cells.map(c=>c.y))-y+1;
    const cells=new Set(zone.cells.map(c=>`${c.x},${c.y}`)),clip=`zone-art-${String(zone.id||index).replace(/[^a-z0-9-]/gi,'')}`;
    const rects=zone.cells.map(c=>`<rect x="${(c.x-x)*100}" y="${(c.y-y)*100}" width="100" height="100"/>`).join('');
    const boundary=zone.cells.map(c=>{
      const px=(c.x-x)*100,py=(c.y-y)*100;let path='';
      if(!cells.has(`${c.x},${c.y-1}`))path+=`M${px},${py}h100`;
      if(!cells.has(`${c.x+1},${c.y}`))path+=`M${px+100},${py}v100`;
      if(!cells.has(`${c.x},${c.y+1}`))path+=`M${px},${py+100}h100`;
      if(!cells.has(`${c.x-1},${c.y}`))path+=`M${px},${py}v100`;
      return path;
    }).join('');
    const image=(name,px,py,pw,ph,cls,delay=0)=>`<image href="/assets/combat-presentation-v2/effects/${name}.png" x="${px}" y="${py}" width="${pw}" height="${ph}" preserveAspectRatio="xMidYMid meet" class="${cls}" style="animation-delay:-${delay}s"/>`;
    const bases={ember:'ember_ground',binding:'binding_ring',sanctuary:'sanctuary_ring',thorns:'thorn_ground'};
    const accents={ember:['flame_lick','ember_motes'],binding:['binding_tether'],sanctuary:['restoration_wisp'],thorns:['thorn_growth']};
    const pieces=accents[zone.kind]||accents.binding;
    let artwork=image(bases[zone.kind]||'binding_ring',0,0,w*100,h*100,`zone-base ${zone.kind==='binding'?'zone-orbit':''}`);
    for(const [i,c] of zone.cells.entries()){
      const px=(c.x-x)*100,py=(c.y-y)*100;
      artwork+=image(pieces[i%pieces.length],px+12,py+15,76,76,`zone-accent accent-${zone.kind}`,i*.37);
    }
    if(['scorched','meteor_armed','flash_freeze_armed'].includes(zone.kind)){
      artwork=zone.cells.map(c=>{const px=(c.x-x)*100,py=(c.y-y)*100;return zone.kind==='scorched'?`<image href="/assets/mage-v1/scorched_tile.png" x="${px}" y="${py}" width="100" height="100" class="mage-zone-tile"/><image href="/assets/mage-v1/fire_contact.png" x="${px+20}" y="${py+20}" width="60" height="60" class="mage-zone-flame"/>`:`<rect x="${px+3}" y="${py+3}" width="94" height="94" rx="6" class="mage-telegraph-cell"/>`}).join('');
      if(zone.kind!=='scorched')artwork+=`<text x="${w*50}" y="${h*50}" class="mage-telegraph-label">${zone.kind==='meteor_armed'?'METEOR INCOMING':'FREEZE ARMED'}</text>`;
    }
    if(zone.kind==='caltrops')artwork=caltropsArtwork(zone.cells,x,y,clip);
    const description=`${zone.name} | ${zone.owner_name} | ${zone.remaining} owner activations | ${zone.description}`;
    return `<div class="battle-zone painted-zone zone-${escape(zone.kind)}" style="grid-column:${x+1};grid-row:${y+1};grid-column-end:span ${w};grid-row-end:span ${h}" title="${escape(description)}" aria-label="${escape(description)}"><svg viewBox="0 0 ${w*100} ${h*100}" preserveAspectRatio="none" aria-hidden="true"><defs><clipPath id="${clip}">${rects}</clipPath></defs><g clip-path="url(#${clip})">${artwork}<path d="${boundary}" class="zone-boundary"/></g></svg></div>`;
  }).join('');
}
export function zoneCellHelp(zones,x,y){
  return (zones||[]).filter(z=>z.cells.some(p=>p.x===x&&p.y===y)).map(z=>`${z.name} | ${z.owner_name} | ${z.remaining} owner activations | ${z.description} | `).join('');
}
