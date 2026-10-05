export function loadoutSelection(current,id,capacity=5){
  if(current.includes(id))return current.filter(key=>key!==id);
  return current.length<capacity?[...current,id]:current;
}

export function jobSkillRows(job,known,practice=0){
  const ids=[...(job?.starter_skills||[]),...(job?.unlocks||[]).map(u=>u.skill_id),...known];
  return [...new Set(ids)].map(id=>({id,learned:known.includes(id),remaining:Math.max(0,(job?.unlocks||[]).find(u=>u.skill_id===id)?.contracts-practice||0)}));
}
