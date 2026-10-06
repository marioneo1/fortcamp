export function intrinsicTraits(unit){
 if(!unit)return [];
 const rows=(unit.passives||[]).filter(p=>p.source_kind!=='character'&&!p.id?.startsWith('job:')).map(p=>({...p,source_name:p.source_name||'Innate'}));
 if(unit.race_summary)rows.push({id:'race',name:unit.race||'Racial traits',description:unit.race_summary,source_name:'Race'});
 if(unit.fury_cap===5)rows.push({id:'fury',name:'Innate Fury',description:unit.job_description,source_name:'Barbarian'});
 const equippedReactions=new Set((unit.passives||[]).map(p=>p.reaction?.id).filter(Boolean));
 for(const reaction of unit.reactions||[])if(!equippedReactions.has(reaction.id))rows.push({id:'reaction:'+reaction.id,name:reaction.name,description:reaction.description||'Triggers automatically when its conditions are met. Uses your shared reaction allowance.',source_name:'Equipment'});
 const labels={capture_chance:'capture chance bonus',carry_strength:'carry strength bonus',throw_range:'throw range bonus',breach_damage:'extra structure damage',guard_heal:'HP restored when guarding',wounded_damage:'extra damage while wounded',boss_damage:'extra damage against bosses',water_walk:'Cross shallow water without its movement penalty.',rubble_walk:'Cross rubble without its movement penalty.',opening_guard:'Begin combat guarding.',lifeline:'Prevent one lethal defeat this battle, leaving 1 HP.'};
 for(const [key,value] of Object.entries(unit.gear_rules||{})){
  if(key==='resistances'&&value.length)rows.push({id:key,name:'Equipment resistances',description:value.join(', '),source_name:'Equipment'});
  else if(value&&labels[key])rows.push({id:key,name:key.replaceAll('_',' '),description:typeof value==='boolean'?labels[key]:`${value} ${labels[key]}.`,source_name:'Equipment'});
 }
 return rows;
}
export function traitsMarkup(unit,escape){
 const traits=intrinsicTraits(unit);
 return `<div class="intrinsic-traits-list">${traits.map(p=>`<article tabindex="0"><small>${escape(p.source_name)}</small><b>${escape(p.name)}</b><p>${escape(p.description||'')}</p></article>`).join('')||'<p>No innate or equipment traits.</p>'}</div>`;
}
