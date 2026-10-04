// Shared camp/map-authoring geometry. One unit is one square cell.
import pieces from './construction-wall-pieces.json' with {type:'json'};
import legacyPieces from './construction-wall-pieces-legacy.json' with {type:'json'};
import propArtBounds from './construction-prop-bounds.json' with {type:'json'};
import furniture from './construction-furniture.json' with {type:'json'};
export const isTable=p=>furniture.tables.includes(p.asset);
export const isSeat=p=>furniture.seats.includes(p.asset);
export function propsOverlap(a,b){
 const [al,at,ar,ab]=propBounds(a),[bl,bt,br,bb]=propBounds(b);
 const width=Math.min(ar,br)-Math.max(al,bl),height=Math.min(ab,bb)-Math.max(at,bt);
 if(width<=1e-7||height<=1e-7)return false;
 const seat=isSeat(a)&&isTable(b)?a:isSeat(b)&&isTable(a)?b:null;
 if(seat){const [l,t,r,b]=propBounds(seat);if(width*height<=(r-l)*(b-t)*furniture.tuck_fraction+1e-7)return false}
 return true;
}
export function defaultWallAnchor(piece){return piece.startsWith('corner_')?'center':piece.startsWith('vertical_')?'west':'north'}
export const availableWallPieces=pieces;
// Direction/facing is placement state, not a second library icon.
export function wallLibraryPiece(piece){
 if(piece?.startsWith('corner_'))return 'corner_north_west';
 return piece?.replace(/_(south|west)$/,'');
}
export function wallLibraryEntries(){
 return Object.entries(availableWallPieces).filter(([id])=>wallLibraryPiece(id)===id).map(([id,piece])=>[id,{...piece,name:id==='corner_north_west'?'Full-length corner':piece.name}]);
}
// Retired junctions remain readable in saved layouts, but cannot be selected as brushes.
export const wallPieces={...legacyPieces,...pieces};
export const anchors={center:[.5,.5],north:[.5,0],east:[1,.5],south:[.5,1],west:[0,.5]};
export const wallArms={straight:[[-.5,0],[.5,0]],half:[[.5,0]],corner:[[.5,0],[0,.5]],tee:[[-.5,0],[.5,0],[0,.5]],cross:[[-.5,0],[.5,0],[0,-.5],[0,.5]],gate:[[-.5,0],[.5,0]]};
export function wallSegments(wall){
 if(wall.piece){const [ax,ay]=anchors[wall.anchor];return wallPieces[wall.piece].segments.map(s=>s.map(([x,y])=>[wall.x+x+ax-.5,wall.y+y+ay-.5]));}
 const [ax,ay]=anchors[wall.anchor],start=[wall.x+ax,wall.y+ay];
 return wallArms[wall.shape].map(arm=>{let [dx,dy]=arm;for(let i=0;i<wall.rotation/90;i++)[dx,dy]=[-dy,dx];return [start,[start[0]+dx,start[1]+dy]]});
}
export const pointKey=p=>p.join(',');
export function wallConnections(walls){
 const nodes=new Map(),edges=new Set();
 for(const wall of walls)for(const segment of wallSegments(wall))for(const [a,b] of splitSegment(segment)){
  const ka=pointKey(a),kb=pointKey(b),key=[ka,kb].sort().join('|');
  if(edges.has(key))continue;edges.add(key);
  for(const [k,p,other] of [[ka,a,kb],[kb,b,ka]]){if(!nodes.has(k))nodes.set(k,{point:p,neighbors:new Set()});nodes.get(k).neighbors.add(other)}
 }
 return nodes;
}
function splitSegment([a,b]){
 const count=Math.max(1,Math.round(Math.max(Math.abs(b[0]-a[0]),Math.abs(b[1]-a[1]))*2));
 const point=i=>a.map((v,k)=>v+(b[k]-v)*i/count);
 return Array.from({length:count},(_,i)=>[point(i),point(i+1)]);
}
export function wallPosts(wall){
 const [ax,ay]=anchors[wall.anchor];
 return (wallPieces[wall.piece]?.posts||[]).map(([x,y])=>[wall.x+x+ax-.5,wall.y+y+ay-.5]);
}
export function snapAnchor(px,py){
 const x=Math.floor(px),y=Math.floor(py);
 const choices=Object.entries(anchors).map(([anchor,[ax,ay]])=>({anchor,distance:Math.hypot(px-x-ax,py-y-ay)}));
 return {x,y,anchor:choices.sort((a,b)=>a.distance-b.distance)[0].anchor};
}
export function validPlacement(item,layer,size){
 if(![item.x,item.y,item.rotation].every(Number.isInteger)||item.rotation<0||item.rotation>270||item.rotation%90)return false;
 if(item.x<0||item.y<0||item.x>=size.w||item.y>=size.h)return false;
 if(layer==='props')return [item.w,item.h].every(v=>Number.isInteger(v)&&v>=1&&v<=4)&&item.x+item.w<=size.w&&item.y+item.h<=size.h;
 return wallSegments(item).every(segment=>segment.every(([x,y])=>x>=0&&y>=0&&x<=size.w&&y<=size.h));
}
// Positive collinear overlap is a duplicate; meeting ends and perpendicular joins are allowed.
export function segmentsOverlap([a,b],[c,d]){
 const axis=a[1]===b[1]?0:1,other=1-axis;
 return c[other]===d[other]&&a[other]===c[other]&&Math.min(Math.max(a[axis],b[axis]),Math.max(c[axis],d[axis]))-Math.max(Math.min(a[axis],b[axis]),Math.min(c[axis],d[axis]))>1e-7;
}
export function propBounds(p){
 const layout=propImageLayout(p);
 if(layout.bounds)return layout.bounds;
 return [p.x+p.w*.04+(p.offset_x||0),p.y+p.h*.04+(p.offset_y||0),p.x+p.w*.96+(p.offset_x||0),p.y+p.h*.96+(p.offset_y||0)];
}
// Presentation and placement geometry share the exact same source measurements.
export function propImageLayout(p){
 const cx=p.x+p.w/2+(p.offset_x||0),cy=p.y+p.h/2+(p.offset_y||0);
 const w=p.rotation%180?p.h:p.w,h=p.rotation%180?p.w:p.h;
 const art=propArtBounds[p.asset];
 if(art){
  const [iw,ih]=art.size,[l,t,r,b]=art.bounds;
  const scale=art.fill?Math.min(w*art.fill/(r-l),h*art.fill/(b-t)):Math.min(w*.92/iw,h*.92/ih);
  const mx=art.fill?(l+r)/2:iw/2,my=art.fill?(t+b)/2:ih/2;
  const points=[[l,t],[r,t],[r,b],[l,b]].map(([x,y])=>{let dx=(x-mx)*scale,dy=(y-my)*scale;for(let turn=0;turn<(p.rotation||0)/90;turn++)[dx,dy]=[-dy,dx];return [cx+dx,cy+dy]});
  return {cx,cy,x:cx-mx*scale,y:cy-my*scale,w:iw*scale,h:ih*scale,bounds:[Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1])),Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))]};
 }
 return {cx,cy,x:cx-w*.46,y:cy-h*.46,w:w*.92,h:h*.92};
}
export function wallHitsProp(w,p){
 const [left,top,right,bottom]=propBounds(p);
 return wallSegments(w).some(([a,b])=>a[1]===b[1]
  ? a[1]>=top-.08&&a[1]<=bottom+.08&&Math.max(a[0],b[0])>left-.08&&Math.min(a[0],b[0])<right+.08
  : a[0]>=left-.08&&a[0]<=right+.08&&Math.max(a[1],b[1])>top-.08&&Math.min(a[1],b[1])<bottom+.08);
}
export function placementError(item,layer,size,plan){
 if(!validPlacement(item,layer,size))return 'That piece extends outside the camp.';
 if(layer==='walls'){
  const segments=wallSegments(item);
  if(plan.walls.some(w=>w.id!==item.id&&wallSegments(w).some(s=>segments.some(t=>segmentsOverlap(s,t)))))return 'A wall already occupies that position. Connecting wall ends is allowed.';
  if(plan.props.some(p=>wallHitsProp(item,p)))return 'That wall overlaps a prop. Move the prop or the wall.';
 }else if(layer==='props'){
  if(plan.walls.some(w=>wallHitsProp(w,item)))return 'That prop overlaps a wall. Adjust its position or choose another cell.';
  if(plan.props.some(p=>p.id!==item.id&&propsOverlap(item,p)))return 'Those props overlap. Adjust their positions; seats can tuck slightly under a table.';
 }
 return '';
}
const solidWall=w=>!w.broken&&!(w.shape==='gate'&&w.open);
export function constructionCellBlocked(plan,x,y){
 return plan.props.some(p=>p.blocking&&x>=p.x&&x<p.x+p.w&&y>=p.y&&y<p.y+p.h)||plan.walls.some(w=>solidWall(w)&&wallSegments(w).some(([a,b])=>a[1]===b[1]
  ?a[1]>y&&a[1]<y+1&&Math.max(a[0],b[0])>x&&Math.min(a[0],b[0])<x+1
  :a[0]>x&&a[0]<x+1&&Math.max(a[1],b[1])>y&&Math.min(a[1],b[1])<y+1));
}
export function constructionStepAllowed(plan,size,x,y,nx,ny){
 if(Math.abs(x-nx)+Math.abs(y-ny)!==1||[x,nx].some(v=>v<0||v>=size.w)||[y,ny].some(v=>v<0||v>=size.h)||constructionCellBlocked(plan,x,y)||constructionCellBlocked(plan,nx,ny))return false;
 return !plan.walls.some(w=>solidWall(w)&&wallSegments(w).some(([a,b])=>x!==nx
  ?a[0]===b[0]&&a[0]>Math.min(x,nx)+.5&&a[0]<Math.max(x,nx)+.5&&Math.min(a[1],b[1])<=y+.5&&Math.max(a[1],b[1])>=y+.5
  :a[1]===b[1]&&a[1]>Math.min(y,ny)+.5&&a[1]<Math.max(y,ny)+.5&&Math.min(a[0],b[0])<=x+.5&&Math.max(a[0],b[0])>=x+.5));
}
export function rotatePlacement(item,layer){
 if(layer==='walls'&&['tee','cross'].includes(item.shape))return {...item};
 if(layer==='walls'&&item.piece){const piece=wallPieces[item.piece].next;return {...item,piece,shape:wallPieces[piece].shape,anchor:{center:'center',north:'east',east:'south',south:'west',west:'north'}[item.anchor],rotation:0};}
 const next={...item,rotation:(item.rotation+90)%360};
 if(layer==='props')[next.w,next.h]=[item.h,item.w];
 return next;
}
export function nudgePlacement(item,layer,key,fine=false){
 if(layer==='walls')return {...item,anchor:{ArrowLeft:'west',ArrowRight:'east',ArrowUp:'north',ArrowDown:'south',Home:'center'}[key]||item.anchor};
 const next={...item};if(key==='Home')return {...next,offset_x:0,offset_y:0};
 const axis=key==='ArrowLeft'||key==='ArrowRight'?'offset_x':'offset_y',sign=key==='ArrowLeft'||key==='ArrowUp'?-1:1;
 next[axis]=Math.round(Math.max(-.5,Math.min(.5,(next[axis]||0)+sign*(fine?.01:.05)))*1000)/1000;return next;
}
export function newPlan(){return {version:1,revision:0,ground:{},props:[],walls:[]}}
