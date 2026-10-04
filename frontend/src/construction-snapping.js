import {anchors,wallSegments,rotatePlacement,placementError} from './construction-geometry.js';

const key=p=>p.join(',');
export function wallContacts(item,plan){
 const ports=new Set(plan.walls.filter(w=>w.id!==item.id).flatMap(w=>wallSegments(w).flat()).map(key));
 return [...new Map(wallSegments(item).flat().filter(p=>ports.has(key(p))).map(p=>[key(p),p])).values()];
}

// Only examine nearby pieces. Artwork/material never participates in geometric snapping.
function localPlan(item,plan){
 return {walls:plan.walls.filter(w=>Math.abs(w.x-item.x)<=3&&Math.abs(w.y-item.y)<=3),
  props:plan.props.filter(p=>p.x+p.w+(p.offset_x||0)>=item.x-2&&p.x+(p.offset_x||0)<=item.x+3&&p.y+p.h+(p.offset_y||0)>=item.y-2&&p.y+(p.offset_y||0)<=item.y+3)};
}

export function snapWall(item,plan,size,{allowRotate=item.shape==='corner',requiredContacts=[],reach=.85}={}){
 if(!item.piece)return {item,snapped:false,contacts:[]};
 const local=localPlan(item,plan),wanted=new Set(requiredContacts.map(key));
 const center=[item.x+anchors[item.anchor][0],item.y+anchors[item.anchor][1]];
 let facing=item,best=null;
 for(let turn=0;turn<(allowRotate?4:1);turn++,facing=rotatePlacement(facing,'walls')){
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++)for(const anchor of Object.keys(anchors)){
   const candidate={...facing,x:item.x+dx,y:item.y+dy,anchor};
   const distance=Math.hypot(candidate.x+anchors[anchor][0]-center[0],candidate.y+anchors[anchor][1]-center[1]);
   if(distance>reach||placementError(candidate,'walls',size,local))continue;
   const contacts=wallContacts(candidate,local);
   if(!contacts.length||wanted.size&&![...wanted].every(port=>contacts.some(p=>port===key(p))))continue;
   const segments=wallSegments(candidate),joint=segments.length===2?segments[0].find(p=>segments[1].some(q=>key(p)===key(q))):null;
   const jointConnected=joint&&contacts.some(p=>key(p)===key(joint));
   const score=distance+turn*.06+(anchor!==item.anchor ? .025 : 0)-Math.min(contacts.length,2)*.04-(jointConnected ? .2 : 0);
   if(!best||score<best.score)best={item:candidate,snapped:true,contacts,score};
  }
 }
 return best||{item,snapped:false,contacts:[]};
}

export function rotateSnappedWall(item,plan,size){
 const contacts=wallContacts(item,plan);
 let candidate=item;
 for(let turn=1;turn<=3;turn++){
  candidate=rotatePlacement(candidate,'walls');
  if(contacts.length){
   const result=snapWall(candidate,plan,size,{allowRotate:false,requiredContacts:contacts,reach:1.5});
   if(result.snapped)return result;
  }else if(!placementError(candidate,'walls',size,plan))return {item:candidate,snapped:false,contacts:[]};
 }
 return {item,snapped:contacts.length>0,contacts,blocked:true};
}
