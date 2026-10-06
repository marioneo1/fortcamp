export function swapSkillSlots(ids,from,to){
 const next=[...ids],a=next.indexOf(from),b=next.indexOf(to);
 if(a>=0&&b>=0)[next[a],next[b]]=[next[b],next[a]];
 return next;
}
export function applySkillOrder(skills,ids=[]){
 const byId=new Map(skills.map(s=>[s.id,s]));
 return [...new Set([...ids,...byId.keys()])].filter(id=>byId.has(id)).map(id=>byId.get(id));
}
export function bindSkillSwaps(root,onSwap){
 let dragged=null;
 root?.querySelectorAll('[data-hotbar-slot]').forEach(button=>{
  button.ondragstart=e=>{dragged=button.dataset.hotbarSlot;e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',dragged);button.classList.add('dragging')};
  button.ondragend=()=>{dragged=null;root.querySelectorAll('.dragging,.drop-slot').forEach(e=>e.classList.remove('dragging','drop-slot'))};
  button.ondragover=e=>{if(dragged){e.preventDefault();e.dataTransfer.dropEffect='move';button.classList.add('drop-slot')}};
  button.ondragleave=()=>button.classList.remove('drop-slot');
  button.ondrop=e=>{e.preventDefault();e.stopPropagation();button.classList.remove('drop-slot');if(dragged&&dragged!==button.dataset.hotbarSlot)onSwap(dragged,button.dataset.hotbarSlot);dragged=null};
 });
}
