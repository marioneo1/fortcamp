// Shared camp/map-authoring geometry. One unit is one square cell.
export const anchors={center:[.5,.5],north:[.5,0],east:[1,.5],south:[.5,1],west:[0,.5]};
export const wallArms={straight:[[-.5,0],[.5,0]],half:[[.5,0]],corner:[[.5,0],[0,.5]],tee:[[-.5,0],[.5,0],[0,.5]],cross:[[-.5,0],[.5,0],[0,-.5],[0,.5]],gate:[[-.5,0],[.5,0]]};
export function wallSegments(wall){
 const [ax,ay]=anchors[wall.anchor],start=[wall.x+ax,wall.y+ay];
 return wallArms[wall.shape].map(arm=>{let [dx,dy]=arm;for(let i=0;i<wall.rotation/90;i++)[dx,dy]=[-dy,dx];return [start,[start[0]+dx,start[1]+dy]]});
}
export const pointKey=p=>p.join(',');
export function wallConnections(walls){
 const nodes=new Map(),edges=new Set();
 for(const wall of walls)for(const [a,b] of wallSegments(wall)){
  const ka=pointKey(a),kb=pointKey(b),key=[ka,kb].sort().join('|');
  if(edges.has(key))continue;edges.add(key);
  for(const [k,p,other] of [[ka,a,kb],[kb,b,ka]]){if(!nodes.has(k))nodes.set(k,{point:p,neighbors:new Set()});nodes.get(k).neighbors.add(other)}
 }
 return nodes;
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
 const next={...item,rotation:(item.rotation+90)%360};
 if(layer==='props')[next.w,next.h]=[item.h,item.w];
 return next;
}
export function newPlan(){return {version:1,revision:0,ground:{},props:[],walls:[]}}
