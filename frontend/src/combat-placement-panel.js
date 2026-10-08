// Shared, persistent placement-window position; dragging never issues a command.
export function bindPlacementPanel(panel,key,signal){
 const storageKey=`fortcamp:placement:${key}`;
 const place=(x,y)=>{const left=Math.max(8,Math.min(innerWidth-panel.offsetWidth-8,x)),top=Math.max(8,Math.min(innerHeight-panel.offsetHeight-8,y));Object.assign(panel.style,{position:'fixed',left:`${left}px`,top:`${top}px`,transform:'none'});return {x:left/innerWidth,y:top/innerHeight}};
 try{const p=JSON.parse(localStorage.getItem(storageKey));if(Number.isFinite(p?.x)&&Number.isFinite(p?.y))requestAnimationFrame(()=>{if(panel.isConnected)place(p.x*innerWidth,p.y*innerHeight)})}catch{}
 let drag=null;
 panel.addEventListener('pointerdown',e=>{if(e.button!==0||!e.target.closest('[data-placement-handle]'))return;const r=panel.getBoundingClientRect();drag={id:e.pointerId,x:e.clientX-r.left,y:e.clientY-r.top};panel.setPointerCapture(e.pointerId);e.preventDefault()},{signal});
 panel.addEventListener('pointermove',e=>{if(drag?.id!==e.pointerId)return;const p=place(e.clientX-drag.x,e.clientY-drag.y);try{localStorage.setItem(storageKey,JSON.stringify(p))}catch{}},{signal});
 panel.addEventListener('pointerup',()=>{drag=null},{signal});panel.addEventListener('lostpointercapture',()=>{drag=null},{signal});
}

export function placementPoint(field,view,e){const r=field.getBoundingClientRect();return {x:Math.floor((e.clientX-r.left)/r.width*view.width),y:Math.floor((e.clientY-r.top)/r.height*view.height)}}
export function placementCursor(field,valid){field.classList.toggle('placement-cursor-valid',valid);field.classList.toggle('placement-cursor-invalid',!valid)}
export function clearPlacementCursor(field){field?.classList.remove('placement-cursor-valid','placement-cursor-invalid')}
