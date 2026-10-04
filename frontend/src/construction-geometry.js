// Shared camp/map-authoring geometry. One unit is one square cell.
import pieces from './construction-wall-pieces.json' with {type:'json'};
export const wallPieces=pieces;
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
export function rotatePlacement(item,layer){
 if(layer==='walls'&&item.piece){const piece=wallPieces[item.piece].next;return {...item,piece,shape:wallPieces[piece].shape,rotation:0};}
 const next={...item,rotation:(item.rotation+90)%360};
 if(layer==='props')[next.w,next.h]=[item.h,item.w];
 return next;
}
export function nudgePlacement(item,layer,key,fine=false){
 if(layer==='walls')return {...item,anchor:{ArrowLeft:'west',ArrowRight:'east',ArrowUp:'north',ArrowDown:'south',Home:'center'}[key]||item.anchor};
 const next={...item};if(key==='Home')return {...next,offset_x:0,offset_y:0};
 const axis=key==='ArrowLeft'||key==='ArrowRight'?'offset_x':'offset_y',sign=key==='ArrowLeft'||key==='ArrowUp'?-1:1;
 next[axis]=Math.round(Math.max(-.45,Math.min(.45,(next[axis]||0)+sign*(fine?.01:.05)))*1000)/1000;return next;
}
export function newPlan(){return {version:1,revision:0,ground:{},props:[],walls:[]}}
