export function statusDetails(status,definitions={}){
  if(['animal_mounted','summon_order','summon_overload','engineer_mounted','engineer_construction','engineer_overclock','engineer_disruption','engineer_machine'].includes(status.id))return {name:status.name,description:status.description,details:status.turns==null?[]:[`${status.turns} owner turns remaining`]};
  if(status.id==='innate_resistance')return {name:'Innate resistances',description:'Always active. Unlisted debuffs have no innate resistance.',details:[...Object.entries(status.statuses||{}).map(([id,value])=>`${id.replaceAll('_',' ')}: ${id==='burn'?value+'% damage reduction; Burn still applies':value===100?'immune':value+'% chance to resist'}`),...(status.knockback?[`Push / pull: ${status.knockback}% chance to resist`]:[]),...(status.control_duration_limit?[`Stun, sleep, freeze, paralysis and binding last at most ${status.control_duration_limit} target turn`]:[])]};
  if(status.id==='passive_readiness')return {name:status.name,description:status.description,details:[status.spent?'Used for this battle':status.active_window?'Active now':status.ready?'Ready to trigger':`Ready in ${status.cooldown_remaining} of this character's turns`]};
  const base=definitions[status.id]||{name:status.id,icon:'•',description:'Status effect'};
  const details=[];
  if(status.id==='weapon_enchant'){
    const effect={fire:'Each successful weapon hit applies 1 Burn stack. Multi-hit attacks apply it per hit.',frost:'Each successful weapon hit has a 20% chance to Freeze, subject to resistance. Further damage can break elemental ice.',lightning:'Each successful weapon hit against Wet has a 25% chance to Paralyze. Can successfully Paralyze each target only once per enchantment; Wet is not consumed.'};
    return {...base,name:`${status.element?status.element[0].toUpperCase()+status.element.slice(1):'Weapon'} Enchantment`,description:effect[status.element]||base.description,details:[...(status.turns!=null?[`${status.turns} owner turns remaining`]:[]),...(status.element==='lightning'?[`${status.paralyzed_targets?.length||0} targets already paralyzed by this application`]:[]),...(status.source_name?[`From ${status.source_name}`]:[])]};
  }
  if(status.id==='freeze'&&status.elemental_freeze)return {...base,name:'Frozen',description:'Cannot act. Direct HP damage breaks the ice after the full hit; ending it applies Wet.',details:[`${status.turns} target turns remaining`,`${status.wet_turns||2} turns of Wet when ice ends`]};
  if(status.id==='freeze')return {...base,description:'Cannot move; direct damage received +25%.',details:[`${status.turns??1} target turns remaining`]};

  if(status.id==='deployment')return {name:'Temporary deployment',icon:'◆',description:`Owned by ${status.owner_name}. ${status.policy==='automatic'?'Automatic targeting; shares owner output budget.':'Attack commands spend the owner action.'} No extra initiative turn, loot or prisoner reward.`,details:[status.ready?'Ready this owner activation':'Ready from the next owner activation',status.stationary?'Stationary device':'Uses its own movement budget']};
  if(status.id==='wild_form')return {name:status.name,icon:'◆',description:status.description,details:[status.turns==null?'Until you change form · shared HP':' '+status.turns+' owner activations remaining · no HP refill']};
  if(status.id==='palm_exposure')return {...base,details:[`+${10*(status.stacks||1)}% direct attack damage taken; ${status.turns} target turns remaining`,'Refreshes on each landed punch; maximum 30%']};
  if(status.id==='iron_reversal_evasion')return {...base,details:[`Against ${status.enemy_name||'the struck enemy'} only`,'Expires at next Monk turn start']};
  if(status.id==='monk_siphon')return {...base,details:[`${Math.max(0,(status.turns||1)-1)} future Monk turns remaining`,'3 HP per landed hit; does not overheal']};
  if(status.id==='dash_parry')return {...base,details:['Expires at next Monk turn start','Excludes magic and area attacks']};
  if(['open_guard','flowing_footwork','iron_reversal'].includes(status.id))return {...base,details:[status.id==='iron_reversal'?'One incoming direct attack · expires at next personal turn start':`${status.turns} turn window remaining · expires at ${status.source_name||'owner'}’s turn end`,...(status.source_name?[`From ${status.source_name}`]:[])]};
  if(status.id==='poison')return {...base,name:'Poison',description:'Lose 10% max HP at turn end, before damage modifiers. Extra stacks extend duration, not damage. Ignores Armor.',details:[`${status.layers?.length??status.stacks??status.turns??1} turns remaining; one stack expires after each tick`]};
  if(['burn','bleed'].includes(status.id))return {...base,description:status.id==='burn'?'At turn end, lose 2% max HP per stack (minimum 1 per stack before modifiers), then lose one stack. Flame entry adds a stack and triggers Burn without decay.':'At turn end, lose 5% max HP per stack, then lose one stack. Movement does not trigger damage.',details:[`${status.layers?.length??status.stacks??1} damage stacks; ignores Armor`,...(status.id==='burn'?['Burn resistance reduces final damage; suppresses Regeneration']:[])]};
  if(status.layers)details.push(`${status.layers.length} stacks; each expires independently${status.id==='hobbled'?'; movement is halved once':''}`);
  if(status.id==='barrier')details.push(`${status.amount} damage absorption remaining`);

  if(status.id==='mark'&&status.quarry)return {...base,name:'Mark Quarry',description:'The marking Ranger has guaranteed accuracy against this target. Other attackers gain no benefit.',details:[`Owner: ${status.source_name||'unknown'}`,`${status.turns} target turns remaining`]};
  if(status.id==='mark')details.push(`Owner: ${status.source_name||'unknown'} · +${status.accuracy||10} accuracy on their first hit`);
  if(status.id==='reaction')return {name:status.ready?'Reaction ready':'Reaction spent',icon:status.ready?'↶':'↷',description:`${(status.reactions||[]).join(' / ')}. One shared reaction, refreshed at activation start. Cannot chain.`,details:[]};
  if(status.id==='footing')return {name:'Knockback resistance',icon:'▣',description:`${status.resistance}% chance to resist a push or pull.`,details:[]};
  if(['druid_rejuvenation','living_armor'].includes(status.id))return {name:status.name,description:status.id==='living_armor'?'Take 25% less damage from all sources. Living leaves restore health gradually.':'Gradually restores health; no instant healing.',details:[`Heals ${status.heal_percent}% maximum HP at each of the next ${Math.max(0,status.ticks)} turn starts`,...(status.retaliation?['Direct attackers receive Bleed once per attack action']:[])]};
  if(status.id==='cleric_rest')details.push(`${status.completed_turns||0} completed turns in this Rest session`);
  if(status.remaining!=null)details.push(`${status.remaining} Hold ticks remaining`);
  const duration=status.ticks??status.rounds??status.turns??status.duration;
  if(duration!=null){
    const clock=status.rounds!=null?'round':status.expiry==='target_start'?'damage tick':'activation';
    details.push(`${duration} ${clock}${duration===1?'':'s'} remaining${status.expiry==='target_end'?' · expires at activation end':''}`);
  }
  if(status.source_name&&status.id!=='mark')details.push(`From ${status.source_name}`);
  return {...base,details};
}

export function statusSummary(status,definitions={}){
 const d=statusDetails(status,definitions),n=status.layers?.length??status.stacks??1;
 const summaries={
  poison:'10% max HP damage at turn end. Stacks extend duration, not damage; ignores Armor.',
  burn:`${2*n}% max HP damage at turn end, minimum ${n} before modifiers. Lose one stack per turn. Flame entry adds a stack and triggers damage.`,
  bleed:`${5*n}% max HP damage at turn end; lose one stack afterward. Movement does not trigger it. Ignores Armor.`,
  armor_fracture:'Armor -30%, rounded up. Does not stack.',
  vulnerable:'The next direct damaging hit ignores 3 Armor.',
  pestilence:'ATK -25%; damage received +25%, including DoTs and collisions.',
  blind:'Accuracy -15 points for melee, -35 for ranged and magic.',
  bind:'Cannot move; may still act.',slow:'Movement -2, minimum 1.',hobbled:'Movement halved, rounded down; minimum 1. More stacks do not further reduce movement.',
  stun:'Cannot move or act.',sleep:'Cannot move or act; direct damage wakes the unit.',
  paralyze:'30% chance to lose the turn. Otherwise may act, but cannot move.',
  mute:'Cannot cast spells or make magical basic attacks. Physical actions remain available.',
  fear:'Cannot willingly approach the source; accuracy -15 points.',
  guard:'Next direct hit deals 25% less damage; expires at next turn start.',
  rally_protection:'Next direct hit deals 25% less damage. Does not stack with Guard.',
  rally_power:'Next attack deals 25% more direct damage, including all AoE targets. A miss spends it.',
  brace_defense:'All incoming damage -25%.',reckless_exposure:'All incoming damage +20% until next turn start.',
  death_defiance:'Lethal damage leaves 1 HP until next turn start. Once per battle.',
  poison_imbue:'Next damaging attack adds one Poison duration stack per damaging hit. Misses and fully absorbed hits do not spend it.',
  sharpshooter:'Damage +10%; attack/technique range +2. Ends when you change tiles.',
  palm_exposure:`Direct attack damage received +${10*n}% (maximum 30%). Refreshed by Rapid Palm; excludes DoTs and collisions.`,
  iron_reversal:'Next direct attack deals 20% less damage, including all its hits. Expires at next Monk turn start.',
  iron_reversal_evasion:`Evasion rating +25 against ${status.enemy_name||'the struck enemy'} only, until next Monk turn start.`,
  monk_siphon:'Heal 3 HP per landed hit, including multi-hit attacks and each enemy crossed by Dash. No overhealing.',
  dash_parry:'10% chance to avoid single-target physical attacks; excludes magic and AoE. Expires at next Monk turn start.',
  flowing_footwork:'Next turn: movement +1 and evasion +10. Does not stack.',
  open_guard:'Direct attack damage received +25%; excludes DoTs, ground damage and collisions.',
  bard_accelerando:'Channeling resolves immediately while settled inside the Song. Normal actions/cooldowns; no linger.',
  bard_quickening:'One extra cooldown tick at turn start; excludes the performing Bard. Lingers through your next turn.',
  bard_war_anthem:'Direct damage dealt +20%; excludes DoTs. Lingers through your next turn.',
  bard_song_peace:'Cannot start damaging actions while inside the Song. May move, heal or buff; outside attackers can attack in. No linger.',
  druid_rejuvenation:`Heal ${status.heal_percent}% max HP at each turn start; no instant healing.`,
  living_armor:`All incoming damage -25%; heal ${status.heal_percent}% max HP at turn start.${status.retaliation?' Direct attackers receive Bleed once per attack.':''}`,
 };
 if(status.id==='innate_resistance')return d.details.join('; ')+'.';
 if(status.id==='mark'&&status.quarry)return 'The marking Ranger has guaranteed accuracy against this target; other attackers gain no benefit.';
 if(status.id==='freeze'&&status.elemental_freeze)return `Cannot move or act. Direct HP damage breaks the ice after the full hit; ending Freeze applies Wet for ${status.wet_turns||2} turns.`;
 return summaries[status.id]||d.description;
}

export function tacticalPreviewText(preview){
  if(!preview)return '';
  const parts=[];
  if(preview.hit_count)parts.push(`${preview.hit_count} hits; damage range assumes all land`);
  if(preview.damage_max!=null)parts.push(`${preview.damage_on_hit} to ${preview.damage_max} total damage`);
  if(preview.crit_chance)parts.push(`${preview.crit_chance}% critical chance: ${preview.crit_damage} damage`);
  if(preview.dot_cashout!=null)parts.push(`${preview.dot_cashout} base Poison/Bleed cashout; consumes both`);
  if(preview.rapid_pool)parts.push(`Rapid Fire: ${preview.rapid_pool.join(' / ')}`);
  if(preview.position_power)parts.push(`Cheap Shot: ${(preview.position_power/100).toFixed(1)}x positional damage`);
  if(preview.debuff_stacks)parts.push(`Exploit: ${Object.values(preview.debuff_stacks).reduce((a,b)=>a+b,0)} debuff stacks: ${(preview.exploit_power/100).toFixed(1)}x damage`);
  if(preview.intercepted_by)parts.push(`Intercepted by ${preview.intercepted_by}`);
  if(preview.barrier)parts.push(`${preview.barrier}-point Barrier`);
  for(const zone of preview.zones||[]){
    if(zone.kind==='rally')parts.push('Hold Together: remove Fear, next direct hit -25%, next attack +25%');
    else if(zone.name)parts.push(`${zone.name} · ${zone.cells.length} tiles · ${zone.turns} owner activations · ${zone.description}`);
  }
  for(const effect of preview.tactics||[]){
    const dest=effect.destination;
    parts.push(`On hit: ${effect.type} toward cell ${dest.x+1}, ${dest.y+1} · ${effect.resistance}% resistance`);
    if(effect.blocked)parts.push(`Stopped: ${effect.blocked}`);
    if(effect.pit)parts.push(effect.pit==='lethal'?'Lethal fall · body and gear lost':`${effect.pit==='deep'?'Deep':'Shallow'} pit · ${effect.pit==='deep'?'must climb out':'fall damage and Slow'}`);
    if(effect.collision_damage)parts.push(`${effect.collision_damage} collision damage if the hit and forced movement succeed${effect.collision_target_name?`; ${effect.collision_target_name} also takes ${effect.bystander_damage} damage`:''}`);
  }
  return parts.join(' · ');
}
