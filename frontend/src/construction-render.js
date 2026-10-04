import {wallArtImage} from './construction-wall-art.js';
import {wallSegments,wallConnections,wallPosts,pointKey,isTable,propBounds,propImageLayout} from './construction-geometry.js';
export const wallColors={timber:['#b98953','#5d3e28'],fieldstone:['#9d9d89','#434c42'],limestone:['#e4d4a8','#8f805e'],iron:['#aab4bf','#435464']};
const url=file=>`/assets/combat-terrain/${file}`;
export function constructionSVG(plan,size,catalogue,{selected='',ghost=null,facilities=[],definitions={},grid=true,background=true,wallKit='placeholder',placementBounds=false}={}){
 let html='';
 for(let y=0;y<size.h;y++)for(let x=0;x<size.w;x++){
  if(!background&&!plan.ground[`${x},${y}`])continue;
  const tile=plan.ground[`${x},${y}`],file=tile&&catalogue.ground[tile.asset]?.file||catalogue.ground.grass_short?.file;
  html+=`<rect x="${x}" y="${y}" width="1" height="1" fill="#45603d"/>`;
  if(file)html+=`<image href="${url(file)}" x="${x}" y="${y}" width="1" height="1" transform="rotate(${tile?.rotation||0} ${x+.5} ${y+.5})"/>`;
 }
 if(grid)html+=`<path d="${Array.from({length:size.w+1},(_,x)=>`M${x} 0V${size.h}`).join(' ')} ${Array.from({length:size.h+1},(_,y)=>`M0 ${y}H${size.w}`).join(' ')}" fill="none" stroke="#e0dfb6" stroke-opacity=".2" stroke-width=".015"/>`;
 for(const b of facilities){const d=definitions[b.type];if(d)html+=`<rect x="${b.x}" y="${b.y}" width="${d.w}" height="${d.h}" fill="#172b21" opacity=".7" stroke="#e2c988" stroke-width=".025"/><text x="${b.x+.12}" y="${b.y+.35}" font-size=".16" fill="#f5e4b8">${d.name.replaceAll('&','&amp;').replaceAll('<','&lt;')}</text>`}
 const drawProp=(p,preview=false)=>{
  const file=catalogue.props[p.asset]?.file;if(!file)return '';
  const {cx,cy,x,y,w,h}=propImageLayout(p),[left,top,right,bottom]=propBounds(p);
  // Rotate the art with its footprint; preserveAspectRatio prevents stretching.
  return `<g data-construction-id="${p.id}" data-construction-layer="props" class="construction-prop ${selected===p.id?'selected':''}" opacity="${preview?.6:1}"><rect data-prop-hit x="${left}" y="${top}" width="${right-left}" height="${bottom-top}" fill="transparent" pointer-events="all"/><image pointer-events="none" href="${url(file)}" x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid meet" transform="rotate(${p.rotation} ${cx} ${cy})"/>${placementBounds||selected===p.id||preview?`<rect data-placement-bounds="prop" x="${left}" y="${top}" width="${right-left}" height="${bottom-top}" fill="none" stroke="${ghost?.error&&preview?'#ff7666':preview?'#fff1ae':selected===p.id?'#91efd3':'#dfc98e'}" stroke-opacity=".95" stroke-width=".025" stroke-dasharray=".07 .035" pointer-events="none"/>`:''}</g>`;
 };
 html+=plan.props.slice().sort((a,b)=>Number(isTable(a))-Number(isTable(b))||(a.y+a.h)-(b.y+b.h)).map(p=>drawProp(p)).join('');
 const nodes=plan.walls.some(w=>!w.piece&&w.posts==='auto')?wallConnections(plan.walls):new Map(),caps=new Map();
 const drawWall=(wall,preview=false)=>{
  const [color,edge]=wallColors[wall.material],segments=wallSegments(wall);
  const start=segments[0][0];
  const path=segments.map(([a,b])=>{
   const gap=wall.broken||wall.shape==='gate'&&wall.open;
   const begin=gap?[a[0]+(b[0]-a[0])*.45,a[1]+(b[1]-a[1])*.45]:a;
   return `M${begin[0]} ${begin[1]}L${b[0]} ${b[1]}`;
  }).join(' ');
  if(!wall.piece&&!preview)for(const [a,b] of segments)for(const p of [a,b]){
   const key=pointKey(p),degree=nodes.get(key)?.neighbors.size||0;
   if(wall.posts==='both'&&key!==pointKey(start)||wall.posts==='auto'&&degree===1)caps.set(key,{p,color,edge});
  }
  const gate=wall.shape==='gate'?`<circle cx="${start[0]}" cy="${start[1]}" r=".075" fill="${wall.open?'#99d68b':'#e0a14c'}" stroke="#342e21" stroke-width=".02"/>`:'';
  const painted=wallArtImage(wall,wallKit);
  if(painted)return `<g data-construction-id="${wall.id}" data-construction-layer="walls" class="construction-wall ${selected===wall.id?'selected':''}" opacity="${preview?.65:1}"><g pointer-events="none">${painted}</g><path data-wall-hit d="${path}" fill="none" stroke="transparent" stroke-width=".22" pointer-events="stroke"/>${selected===wall.id||preview?`<path d="${path}" fill="none" stroke="${preview?'#ffefa1':'#91efd3'}" stroke-width=".03" stroke-dasharray=".08 .05" pointer-events="none"/>`:''}</g>`;
  const posts=wallPosts(wall).map(p=>`<rect x="${p[0]-.105}" y="${p[1]-.105}" width=".21" height=".21" rx=".025" fill="${color}" stroke="${edge}" stroke-width=".03"/>`).join('');
  return `<g data-construction-id="${wall.id}" data-construction-layer="walls" class="construction-wall ${selected===wall.id?'selected':''}" opacity="${preview?.6:1}"><path d="${path}" fill="none" stroke="${selected===wall.id?'#91efd3':edge}" stroke-width=".19" stroke-linecap="butt"/><path d="${path}" fill="none" stroke="${color}" stroke-width=".12" stroke-linecap="butt"/>${posts}${gate}</g>`;
 };
 html+=plan.walls.map(w=>drawWall(w)).join('');
 if(placementBounds)html+=wallPlacementBounds(plan.walls);
 for(const {p,color,edge} of caps.values())html+=`<rect x="${p[0]-.105}" y="${p[1]-.105}" width=".21" height=".21" rx=".025" fill="${color}" stroke="${edge}" stroke-width=".03" pointer-events="none"/>`;
 if(ghost)html+=ghost.layer==='props'?drawProp(ghost.item,true):ghost.layer==='walls'?drawWall(ghost.item,true)+wallPlacementBounds([ghost.item],ghost.error?'#ff7666':'#fff1ae'):`<rect x="${ghost.x}" y="${ghost.y}" width="1" height="1" fill="#e9dc99" opacity=".3"/>`;
 return html;
}
export function wallPlacementBounds(walls,color='#91efd3'){
 return walls.flatMap(w=>wallSegments(w)).map(([a,b])=>a[1]===b[1]
  ?`<rect data-placement-bounds="wall" x="${Math.min(a[0],b[0])-.08}" y="${a[1]-.08}" width="${Math.abs(a[0]-b[0])+.16}" height=".16" fill="none" stroke="${color}" stroke-width=".015" stroke-opacity=".6" stroke-dasharray=".07 .035" pointer-events="none"/>`
  :`<rect data-placement-bounds="wall" x="${a[0]-.08}" y="${Math.min(a[1],b[1])-.08}" width=".16" height="${Math.abs(a[1]-b[1])+.16}" fill="none" stroke="${color}" stroke-width=".015" stroke-opacity=".6" stroke-dasharray=".07 .035" pointer-events="none"/>`).join('');
}
