// Pure roster helpers: keep unavailable units out and ranking stable across polls.
export function rankedCandidates(characters, score, query='') {
  const terms=query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return characters.filter(c=>c.status==='idle'&&terms.every(term=>`${c.name} ${c.race} ${c.specialty||''} ${c.series||''}`.toLowerCase().includes(term)))
    .map(c=>({character:c,score:Number(score(c))||0}))
    .sort((a,b)=>b.score-a.score||a.character.name.localeCompare(b.character.name)||a.character.id.localeCompare(b.character.id));
}
export function suggestAssignments(characters, slots, score) {
  const used=new Set(),assignments={};
  for(const slot of slots){
    const candidate=rankedCandidates(characters,c=>score(c,slot)).find(entry=>!used.has(entry.character.id));
    if(candidate){assignments[slot.key]=candidate.character.id;used.add(candidate.character.id)}
  }
  return assignments;
}
export function matchesMission(m,filters){
  return (!filters.available||m.status==='available')&&(!filters.rank||m.rank===filters.rank)
    &&(!filters.form||m.mission_form===filters.form)
    &&`${m.name||''} ${m.description||''} ${m.story_thread?.name||''}`.toLowerCase().includes((filters.query||'').trim().toLowerCase());
}
export function equipmentEditable(c){return ['idle','incapacitated'].includes(c.status)}
