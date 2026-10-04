import {wallSegments,wallConnections,pointKey} from './construction-geometry.js';
export const wallColors={timber:['#b98953','#5d3e28'],fieldstone:['#9d9d89','#434c42'],limestone:['#e4d4a8','#8f805e'],iron:['#aab4bf','#435464']};
const url=file=>`/assets/combat-terrain/${file}`;
export function constructionSVG(plan,size,catalogue,{selected='',ghost=null,facilities=[],definitions={},grid=true}={}){
 let html='';
 for(let y=0;y<size.h;y++)for(let x=0;x<size.w;x++){
  const tile=plan.ground[`${x},${y}`],file=tile&&catalogue.ground[tile.asset]?.file||catalogue.ground.grass_short?.file;
  html+=`<rect x="${x}" y="${y}" width="1" height="1" fill="#45603d"/>`;
  if(file)html+=`<image href="${url(file)}" x="${x}" y="${y}" width="1" height="1" transform="rotate(${tile?.rotation||0} ${x+.5} ${y+.5})"/>`;
 }
 if(grid)html+=`<path d="${Array.from({length:size.w+1},(_,x)=>`M${x} 0V${size.h}`).join(' ')} ${Array.from({length:size.h+1},(_,y)=>`M0 ${y}H${size.w}`).join(' ')}" fill="none" stroke="#e0dfb6" stroke-opacity=".2" stroke-width=".015"/>`;
 for(const b of facilities){const d=definitions[b.type];if(d)html+=`<rect x="${b.x}" y="${b.y}" width="${d.w}" height="${d.h}" fill="#172b21" opacity=".7" stroke="#e2c988" stroke-width=".025"/><text x="${b.x+.12}" y="${b.y+.35}" font-size=".16" fill="#f5e4b8">${d.name.replaceAll('&','&amp;').replaceAll('<','&lt;')}</text>`}
 const drawProp=(p,preview=false)=>{
  const file=catalogue.props[p.asset]?.file;if(!file)return '';
  const cx=p.x+p.w/2+(p.offset_x||0),cy=p.y+p.h/2+(p.offset_y||0);
  // Rotate the art with its footprint; preserveAspectRatio prevents stretching.
  const w=p.rotation%180?p.h:p.w,h=p.rotation%180?p.w:p.h;
  return `<g data-construction-id="${p.id}" data-construction-layer="props" class="construction-prop ${selected===p.id?'selected':''}" opacity="${preview?.6:1}"><image href="${url(file)}" x="${cx-w*.46}" y="${cy-h*.46}" width="${w*.92}" height="${h*.92}" preserveAspectRatio="xMidYMid meet" transform="rotate(${p.rotation} ${cx} ${cy})"/>${selected===p.id||preview?`<rect x="${p.x}" y="${p.y}" width="${p.w}" height="${p.h}" fill="none" stroke="${preview?'#fff1ae':'#91efd3'}" stroke-width=".035" stroke-dasharray=".1 .05"/>`:''}</g>`;
 };
 html+=plan.props.slice().sort((a,b)=>(a.y+a.h)-(b.y+b.h)).map(p=>drawProp(p)).join('');
 const nodes=wallConnections(plan.walls),caps=new Map();
 const drawWall=(wall,preview=false)=>{
  const [color,edge]=wallColors[wall.material],segments=wallSegments(wall);
  const start=segments[0][0];
  const path=segments.map(([a,b])=>{
   const gap=wall.broken||wall.shape==='gate'&&wall.open;
   const begin=gap?[a[0]+(b[0]-a[0])*.45,a[1]+(b[1]-a[1])*.45]:a;
   return `M${begin[0]} ${begin[1]}L${b[0]} ${b[1]}`;
  }).join(' ');
  if(!preview)for(const [a,b] of segments)for(const p of [a,b]){
   const key=pointKey(p),degree=nodes.get(key)?.neighbors.size||0;
   if(wall.posts==='both'&&key!==pointKey(start)||wall.posts==='auto'&&degree===1)caps.set(key,{p,color,edge});
  }
  const gate=wall.shape==='gate'?`<circle cx="${start[0]}" cy="${start[1]}" r=".075" fill="${wall.open?'#99d68b':'#e0a14c'}" stroke="#342e21" stroke-width=".02"/>`:'';
  return `<g data-construction-id="${wall.id}" data-construction-layer="walls" class="construction-wall ${selected===wall.id?'selected':''}" opacity="${preview?.6:1}"><path d="${path}" fill="none" stroke="${selected===wall.id?'#91efd3':edge}" stroke-width=".19" stroke-linecap="square"/><path d="${path}" fill="none" stroke="${color}" stroke-width=".12" stroke-linecap="square"/>${gate}</g>`;
 };
 html+=plan.walls.map(w=>drawWall(w)).join('');
 for(const {p,color,edge} of caps.values())html+=`<rect x="${p[0]-.105}" y="${p[1]-.105}" width=".21" height=".21" rx=".025" fill="${color}" stroke="${edge}" stroke-width=".03" pointer-events="none"/>`;
 if(ghost)html+=ghost.layer==='props'?drawProp(ghost.item,true):ghost.layer==='walls'?drawWall(ghost.item,true):`<rect x="${ghost.x}" y="${ghost.y}" width="1" height="1" fill="#e9dc99" opacity=".3"/>`;
 return html;
}
