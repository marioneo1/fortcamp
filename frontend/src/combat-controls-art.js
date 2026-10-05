// Basic attack identity follows the equipped weapon, rather than the character's Job.
export function basicAttackArt(unit){
 if(unit?.capture_weapon)return 'subdue';
 if(unit?.attack_elevation_rule==='ballistic')return 'ranged';
 if(['ignore','line_of_effect'].includes(unit?.attack_elevation_rule))return 'magic';
 return 'attack';
}

// One cursor overlay, event-driven. Native PNG cursors handle the non-animated states.
export function createBattleCursor(){
 let field=null,node=null,inside=false,last=null;
 const hide=()=>{inside=false;if(node)node.hidden=true};
 function sync(){
  const busy=inside&&field?.isConnected&&!field.closest('.hidden')&&field.closest('.battle-playing');
  if(!busy||!last){if(node)node.hidden=true;return}
  if(!node){node=document.createElement('img');node.className='battle-loading-cursor';node.src='/assets/combat-controls-v2/loading.png';node.alt='';node.setAttribute('aria-hidden','true');document.body.append(node)}
  node.hidden=false;node.style.left=last.x+'px';node.style.top=last.y+'px';
 }
 const move=e=>{inside=true;last={x:e.clientX,y:e.clientY};sync()};
 function mount(next){
  if(field!==next){field?.removeEventListener('pointermove',move);field?.removeEventListener('pointerleave',hide);hide();field=next;field?.addEventListener('pointermove',move);field?.addEventListener('pointerleave',hide)}
  sync();
 }
 return {mount,sync};
}
