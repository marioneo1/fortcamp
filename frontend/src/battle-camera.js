export function fitMapWidth(width,height,availableWidth,availableHeight){
  return Math.max(1,Math.min(availableWidth,availableHeight*width/height));
}
// Keep labels clear of the viewport and allow a small camera nudge even at Fit.
export function floatingMapFrame(width,height,vw,vh,fit,zoom,touch=false){
 const margin=touch?24:96,slack=touch?(fit?60:Math.max(120,vh*.3)):(fit?120:Math.max(360,vh*.45)),pixels=fit?fitMapWidth(width,height,Math.max(1,vw-margin*2),Math.max(1,vh-margin*2)):width*72*zoom;
 return {pixels,width:Math.max(vw,pixels+margin*2)+slack*2,height:Math.max(vh,pixels*height/width+margin*2)+slack*2};
}
export function centerBattleMap(viewport){
 if(!viewport)return;
 viewport.scrollLeft=(viewport.scrollWidth-viewport.clientWidth)/2;
 viewport.scrollTop=(viewport.scrollHeight-viewport.clientHeight)/2;
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
export function bindMapPan(viewport,onCancel=()=>{},onInspect=()=>{}){
  let drag=null;
  viewport.oncontextmenu=e=>e.preventDefault();
  viewport.onpointerdown=e=>{
    if(e.button!==2)return;
    const badge=e.target?.closest?.('[data-unit-status]');
    e.preventDefault();drag={id:e.pointerId,x:e.clientX,y:e.clientY,left:viewport.scrollLeft,top:viewport.scrollTop,moved:false,unit:e.target?.closest?.('[data-battle-unit]')?.dataset.battleUnit,status:badge?{id:badge.dataset.unitStatus,owner:badge.dataset.statusOwner}:null};
    viewport.setPointerCapture(e.pointerId);viewport.classList.add('is-panning');
  };
  viewport.onpointermove=e=>{
    if(!drag||drag.id!==e.pointerId)return;
    if(Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>5)drag.moved=true;
    viewport.scrollLeft=drag.left+drag.x-e.clientX;viewport.scrollTop=drag.top+drag.y-e.clientY;
  };
  const stop=e=>{if(!drag||drag.id!==e.pointerId)return;const cancel=e.type==='pointerup'&&!drag.moved,unit=drag.unit,status=drag.status;drag=null;viewport.classList.remove('is-panning');if(viewport.hasPointerCapture(e.pointerId))viewport.releasePointerCapture(e.pointerId);if(cancel){if(unit)onInspect(unit,e,status);else onCancel()}};
  viewport.onpointerup=stop;viewport.onpointercancel=stop;viewport.onlostpointercapture=()=>{drag=null;viewport.classList.remove('is-panning')};
}
export function sizeBattleMap(viewport,{width,height,fit,zoom}){
  const field=viewport?.querySelector('.battlefield');if(!field)return;
  const sidebar=viewport.closest('.layout-a')?.querySelector('.battle-sidebar');
  if(sidebar)sidebar.style.maxHeight=window.innerWidth>800?`${Math.max(180,window.innerHeight-sidebar.getBoundingClientRect().top-20)}px`:'';
  const floating=viewport.closest('.floating-battle');
  const availableHeight=floating?viewport.clientHeight:Math.max(120,window.innerHeight-viewport.getBoundingClientRect().top-28-(viewport.closest('.layout-a')?.querySelector('.battle-command-dock')?.getBoundingClientRect().height||0));
  viewport.style.maxHeight=`${availableHeight}px`;
  const space=viewport.querySelector('.battle-camera-space');
  const touch=window.matchMedia('(max-width: 1100px) and (hover: none) and (pointer: coarse)').matches;
  const resized=touch&&(viewport._cameraWidth!==viewport.clientWidth||viewport._cameraHeight!==availableHeight);
  const frame=floating&&space?floatingMapFrame(width,height,viewport.clientWidth,availableHeight,fit,zoom,touch):null;
  const offset=space&&viewport._cameraReady&&!resized?{x:viewport.scrollLeft-(viewport.scrollWidth-viewport.clientWidth)/2,y:viewport.scrollTop-(viewport.scrollHeight-viewport.clientHeight)/2}:{x:0,y:0};
  viewport._cameraWidth=viewport.clientWidth;viewport._cameraHeight=availableHeight;
  const pixels=frame?.pixels??(fit?fitMapWidth(width,height,viewport.clientWidth-4,availableHeight-4):width*72*zoom);
  field.style.width=`${pixels}px`;field.style.minWidth='0';
  field.style.setProperty('--map-status-size',`${Math.min(36,pixels/width*.22)}px`);
  field.style.setProperty('--lighting-cell-size',`${pixels/width}px`);
  if(frame){space.style.width=`${frame.width}px`;space.style.height=`${frame.height}px`;centerBattleMap(viewport);viewport.scrollLeft+=offset.x;viewport.scrollTop+=offset.y;viewport._cameraReady=true}
  else if(fit){viewport.scrollTop=0;viewport.scrollLeft=0}
}
