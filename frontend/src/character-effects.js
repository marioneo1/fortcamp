export function perkModifiers(character,items,definitions,section){
  const perks=new Set(character.traits||[]);
  for(const item of items)(item?.granted_perks||[]).forEach(p=>perks.add(p));
  const totals={};for(const p of perks)for(const [key,value] of Object.entries(definitions?.[p]?.modifiers?.[section]||{}))totals[key]=(totals[key]||0)+value;
  const caps={move:2,armor:3,evasion:12,accuracy:15,magic_reduction:40,regeneration:4,hp:15,initiative:6,damage_goblin:3,damage_deathless:3,melee_damage:2};
  return Object.fromEntries(Object.entries(totals).map(([key,value])=>[key,Math.min(value,caps[key]??4)]));
}
export function raceEffects(profile){
  if(!profile)return [];
  const effects=[],percent=Math.round((profile.hp_multiplier-1)*100),signed=n=>`${n>0?'+':''}${n}`;
  if(percent)effects.push(`${signed(percent)}% maximum HP`);
  if(profile.hp_bonus)effects.push(`${signed(profile.hp_bonus)} maximum HP`);
  for(const [key,label] of [['move_bonus','movement'],['evasion','evasion (percentage points)'],['armor_bonus','armor'],['initiative_bonus','initiative']])if(profile[key])effects.push(`${signed(profile[key])} ${label}`);
  if(profile.movement_type==='flying')effects.push('Flight: crosses pits and ignores climbing cost');
  Object.entries(profile.mission_bonuses||{}).forEach(([key,value])=>effects.push(`${signed(value)} ${key} checks`));
  Object.entries(profile.form_bonuses||{}).forEach(([key,value])=>effects.push(`${signed(value)} ${key} mission checks`));
  if(profile.resistances?.includes('magic'))effects.push('20% less incoming magic damage');
  if(profile.weaknesses?.includes('magic'))effects.push('20% more incoming magic damage');
  return effects;
}
