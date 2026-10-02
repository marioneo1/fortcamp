export function fitMapWidth(width,height,availableWidth,availableHeight){
  return Math.max(1,Math.min(availableWidth,availableHeight*width/height));
}
export function sizeBattleMap(viewport,{width,height,fit,zoom}){
  const field=viewport?.querySelector('.battlefield');if(!field)return;
  const availableHeight=Math.max(120,window.innerHeight-viewport.getBoundingClientRect().top-28);
  viewport.style.maxHeight=`${availableHeight}px`;
  const pixels=fit?fitMapWidth(width,height,viewport.clientWidth-4,availableHeight-4):width*72*zoom;
  field.style.width=`${pixels}px`;field.style.minWidth='0';
  if(fit){viewport.scrollTop=0;viewport.scrollLeft=0}
}
