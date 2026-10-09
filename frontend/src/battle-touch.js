// Touch gestures are independent of desktop mouse controls and HUD preferences.
export const MOBILE_BATTLE_QUERY='(max-width: 1100px) and (hover: none) and (pointer: coarse)';
export function bindBattleTouch(viewport,{onInspect=()=>{},onZoom=()=>{},zoomAt=()=>1}={}){
 viewport._battleTouch?.abort();
 const controller=new AbortController(),{signal}=controller;viewport._battleTouch=controller;
 const points=new Map();let origin=null,pinch=null,timer=null,suppressUntil=0;
 const clear=()=>{clearTimeout(timer);timer=null};
 const suppress=()=>{suppressUntil=performance.now()+700};
 const distance=()=>{const [a,b]=[...points.values()];return Math.hypot(a.x-b.x,a.y-b.y)};
 viewport.addEventListener('pointerdown',e=>{
  if(e.pointerType!=='touch')return;
  if(points.size===0)suppressUntil=0;
  points.set(e.pointerId,{x:e.clientX,y:e.clientY});clear();
  if(points.size===1){
   const badge=e.target.closest?.('[data-unit-status]');
   origin={id:e.pointerId,x:e.clientX,y:e.clientY,left:viewport.scrollLeft,top:viewport.scrollTop,moved:false};
   const unit=e.target.closest?.('[data-battle-unit]')?.dataset.battleUnit;
   if(unit)timer=setTimeout(()=>{origin.moved=true;suppress();onInspect(unit,e,badge?{id:badge.dataset.unitStatus,owner:badge.dataset.statusOwner}:null)},450);
  }else if(points.size===2){
   origin=null;pinch={distance:Math.max(1,distance()),zoom:zoomAt()};suppress();
   for(const id of points.keys())viewport.setPointerCapture(id);
  }
 },{signal});
 viewport.addEventListener('pointermove',e=>{
  if(!points.has(e.pointerId))return;
  points.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(points.size>=2&&pinch){
   clear();suppress();e.preventDefault();
   const [a,b]=[...points.values()];onZoom(Math.max(.25,Math.min(3,pinch.zoom*distance()/pinch.distance)),{x:(a.x+b.x)/2,y:(a.y+b.y)/2});
  }else if(origin&&origin.id===e.pointerId){
   if(Math.hypot(e.clientX-origin.x,e.clientY-origin.y)>8){origin.moved=true;clear();suppress();viewport.setPointerCapture(e.pointerId)}
   if(origin.moved){e.preventDefault();viewport.scrollLeft=origin.left+origin.x-e.clientX;viewport.scrollTop=origin.top+origin.y-e.clientY}
  }
 },{signal,passive:false});
 const finish=e=>{
  if(!points.has(e.pointerId))return;
  clear();if(origin?.moved||pinch)suppress();points.delete(e.pointerId);origin=null;
  if(points.size===0)pinch=null;
  // Lifting one finger after a pinch never turns the other finger into a tap.
  if(viewport.hasPointerCapture(e.pointerId))viewport.releasePointerCapture(e.pointerId);
 };
 viewport.addEventListener('pointerup',finish,{signal});viewport.addEventListener('pointercancel',finish,{signal});
 viewport.addEventListener('click',e=>{if(performance.now()<suppressUntil){e.preventDefault();e.stopImmediatePropagation();suppressUntil=0}},{signal,capture:true});
 signal.addEventListener('abort',()=>{clear();points.clear()},{once:true});
 return controller;
}
