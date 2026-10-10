const clamp=(v,max)=>Math.max(0,Math.min(Math.max(0,max),v));
// Resize the complete panel, preserving its internal tracks and proportions.
export function hudScale(requested,size,bounds){
 const value=Number.isFinite(Number(requested))?Number(requested):1;
 return Math.min(Math.max(.5,Math.min(1.5,value)),Math.max(.1,(bounds.width-8)/Math.max(1,size.width)),Math.max(.1,(bounds.height-8)/Math.max(1,size.height)));
}
export function resizeHudScale(initial,dx,dy,size,bounds){
 const delta=(dx*size.width+dy*size.height)/(size.width**2+size.height**2);
 return hudScale(initial+delta,size,bounds);
}
export function snapHud(rect,others,bounds,threshold=8){
 const result={x:rect.x,y:rect.y,guides:[]};
 for(const [axis,size,total] of [['x','width',bounds.width],['y','height',bounds.height]]){
  const anchors=[0,total/2,total,...others.flatMap(r=>[r[axis],r[axis]+r[size]/2,r[axis]+r[size]])];
  let best=threshold+1,line=null,delta=0;
  for(const offset of [0,rect[size]/2,rect[size]])for(const anchor of anchors){const d=anchor-rect[axis]-offset;if(Math.abs(d)<best){best=Math.abs(d);delta=d;line=anchor}}
  if(best<=threshold){result[axis]+=delta;result.guides.push({axis,value:line})}
  result[axis]=clamp(result[axis],total-rect[size]);
 }
 return result;
}
export function hudPosition(savedPosition,size,bounds,fallback){
 return {x:clamp((savedPosition?.x??fallback.x)*Math.max(0,bounds.width-size.width),bounds.width-size.width),y:clamp((savedPosition?.y??fallback.y)*Math.max(0,bounds.height-size.height),bounds.height-size.height)};
}
