export function fitMapWidth(width,height,availableWidth,availableHeight){
  return Math.max(1,Math.min(availableWidth,availableHeight*width/height));
}
export function wheelZoom(current,event){
  const delta=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?300:1);
  return Math.max(.25,Math.min(3,current*Math.exp(-Math.max(-100,Math.min(100,delta))*.0015)));
}
export function bindMapWheel(viewport,{width,height,onZoom}){
  viewport.onwheel=event=>{
    // Keep modified wheel gestures available for ordinary scrolling/browser zoom.
    if(event.shiftKey||event.ctrlKey||event.metaKey||event.deltaY===0)return;
    const field=viewport.querySelector('.battlefield');if(!field)return;
    event.preventDefault();
    const before=field.getBoundingClientRect(),fx=(event.clientX-before.left)/before.width,fy=(event.clientY-before.top)/before.height;
    const zoom=wheelZoom(before.width/(width*72),event);
    onZoom(zoom);sizeBattleMap(viewport,{width,height,fit:false,zoom});
    const after=field.getBoundingClientRect();
    viewport.scrollLeft+=after.left+fx*after.width-event.clientX;
    viewport.scrollTop+=after.top+fy*after.height-event.clientY;
  };
}
export function bindMapPan(viewport){
  let drag=null;
  viewport.oncontextmenu=e=>e.preventDefault();
  viewport.onpointerdown=e=>{
    if(e.button!==2)return;
    e.preventDefault();drag={id:e.pointerId,x:e.clientX,y:e.clientY,left:viewport.scrollLeft,top:viewport.scrollTop};
    viewport.setPointerCapture(e.pointerId);viewport.classList.add('is-panning');
  };
  viewport.onpointermove=e=>{
    if(!drag||drag.id!==e.pointerId)return;
    viewport.scrollLeft=drag.left+drag.x-e.clientX;viewport.scrollTop=drag.top+drag.y-e.clientY;
  };
  const stop=e=>{if(!drag||drag.id!==e.pointerId)return;drag=null;viewport.classList.remove('is-panning');if(viewport.hasPointerCapture(e.pointerId))viewport.releasePointerCapture(e.pointerId)};
  viewport.onpointerup=stop;viewport.onpointercancel=stop;viewport.onlostpointercapture=()=>{drag=null;viewport.classList.remove('is-panning')};
}
export function sizeBattleMap(viewport,{width,height,fit,zoom}){
  const field=viewport?.querySelector('.battlefield');if(!field)return;
  const availableHeight=Math.max(120,window.innerHeight-viewport.getBoundingClientRect().top-28);
  viewport.style.maxHeight=`${availableHeight}px`;
  const pixels=fit?fitMapWidth(width,height,viewport.clientWidth-4,availableHeight-4):width*72*zoom;
  field.style.width=`${pixels}px`;field.style.minWidth='0';
  if(fit){viewport.scrollTop=0;viewport.scrollLeft=0}
}
