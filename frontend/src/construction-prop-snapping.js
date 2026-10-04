import {propBounds,isSeat,isTable,placementError} from './construction-geometry.js';
import furniture from './construction-furniture.json' with {type:'json'};

// Seat docking is a small optional adjustment, never a teleport across the map.
export function snapSeat(item,plan,size){
 if(!isSeat(item))return {item,snapped:false};
 const [l,t,r,b]=propBounds(item),cx=(l+r)/2,cy=(t+b)/2,w=r-l,h=b-t;
 let best=null;
 for(const table of plan.props.filter(p=>p.id!==item.id&&isTable(p))){
  const [tl,tt,tr,tb]=propBounds(table),tx=(tl+tr)/2,ty=(tt+tb)/2;
  for(const [x,y] of [[tx,tt-h*.3],[tx,tb+h*.3],[tl-w*.3,ty],[tr+w*.3,ty]]){
   const dx=x-cx,dy=y-cy,distance=Math.hypot(dx,dy);
   if(distance>furniture.snap_reach||best&&distance>=best.distance)continue;
   // Keep offsets in their supported range by transferring whole-cell movement.
   let px=item.x,py=item.y,ox=(item.offset_x||0)+dx,oy=(item.offset_y||0)+dy;
   if(ox>.5){px++;ox--}else if(ox<-.5){px--;ox++}
   if(oy>.5){py++;oy--}else if(oy<-.5){py--;oy++}
   if(Math.abs(ox)>.5||Math.abs(oy)>.5)continue;
   const candidate={...item,x:px,y:py,offset_x:Math.round(ox*1000)/1000,offset_y:Math.round(oy*1000)/1000};
   if(!placementError(candidate,'props',size,plan))best={item:candidate,snapped:true,tableId:table.id,distance};
  }
 }
 return best||{item,snapped:false};
}
