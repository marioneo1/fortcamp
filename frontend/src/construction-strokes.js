import {anchors,wallSegments,rotatePlacement,placementError} from './construction-geometry.js';

export function rectangleCells(start,end){
 const cells=[];
 for(let y=Math.min(start.y,end.y);y<=Math.max(start.y,end.y);y++)for(let x=Math.min(start.x,end.x);x<=Math.max(start.x,end.x);x++)cells.push({x,y});
 return cells;
}

// Corners start the run once; continuation pieces extend their existing H/V arm.
export function wallRun(seed,dx,dy){
 if(!dx&&!dy)return [{...seed,id:'stroke_0'}];
 const vertical=Math.abs(dy)>Math.abs(dx),distance=vertical?dy:dx,sign=Math.sign(distance);
 let first={...seed};
 if(first.shape!=='corner'){
  const segment=wallSegments(first)[0],isVertical=segment[0][0]===segment[1][0];
  if(isVertical!==vertical)first=rotatePlacement(first,'walls');
 }
 const items=[{...first,id:'stroke_0'}];
 const arm=wallSegments(first).find(([a,b])=>vertical?a[0]===b[0]:a[1]===b[1]);
 for(let step=1;step<=Math.abs(distance);step++){
  let item={...first,id:`stroke_${step}`,x:first.x+(vertical?0:step*sign),y:first.y+(vertical?step*sign:0)};
  if(first.shape==='corner'){
   item.shape='straight';item.piece=vertical?(first.piece.includes('_west')?'vertical_plain_west':'vertical_plain'):(first.piece.includes('_south_')?'horizontal_plain_south':'horizontal_plain');
   const desired=arm.map(([x,y])=>[x+(vertical?0:step*sign),y+(vertical?step*sign:0)]).map(p=>p.join(',')).sort().join('|');
   let match;
   for(const anchor of ['center',...Object.keys(anchors).filter(a=>a!=='center')])for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
    const candidate={...item,x:item.x+dx,y:item.y+dy,anchor};
    if(wallSegments(candidate)[0].map(p=>p.join(',')).sort().join('|')===desired&&!match)match=candidate;
   }
   item=match||{...item,invalidConnection:true};
  }
  items.push(item);
 }
 return items;
}

export function wallRunError(items,plan,size){
 const context={...plan,walls:plan.walls.slice()};
 for(const item of items){if(item.invalidConnection)return 'Center this corner before extending its walls.';const error=placementError(item,'walls',size,context);if(error)return error;context.walls.push(item)}
 return '';
}
