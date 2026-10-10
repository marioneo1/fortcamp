import {JOB_ICON_ART} from './ability-icon-manifest.js';
export const SKILL_CATEGORIES={damage:{label:'Damage',color:'#d97c64',badge:'✦'},dot:{label:'Damage over time',color:'#dfab51',badge:'⋮'},
  control:{label:'Control',color:'#aa91dc',badge:'↔'},self:{label:'Self buff',color:'#d3bc74',badge:'●'},ally:{label:'Ally support',color:'#82b6dd',badge:'◈'},
  heal:{label:'Restoration',color:'#8dbf91',badge:'+'},summon:{label:'Summon / device',color:'#79bdb4',badge:'◆'}};
export const MARTIAL_ICON_ART=Object.fromEntries([
 ['fighter','brace','brace'],['fighter','second_wind','second-wind'],['fighter','victory_strike','victory-strike'],
 ['barbarian','bloodfury','bloodfury'],['barbarian','reckless_blow','reckless-blow'],['barbarian','skullbreaker','skullbreaker'],
 ['barbarian','groundbreaker','groundbreaker'],['barbarian','bloodied_strength','bloodied-strength'],
 ['barbarian','too_angry_to_fall','too-angry-to-fall'],['barbarian','bloodthirst','bloodthirst'],['barbarian','unstoppable','unstoppable']
].map(([job,key,file])=>[`job:${job}:${key}`,`/assets/martial-jobs-v1/${file}.png`]));
export function skillCategory(skill){
  if(skill.engineer_kind)return ['sentry_turret','heavy_emplacement'].includes(skill.engineer_kind)?'summon':['dynamite','scuttle_protocol'].includes(skill.engineer_kind)?'damage':skill.engineer_kind==='proximity_charge'?'control':'self';
  if(skill.summoner_kind==='orders')return 'control';
  if(skill.summoner_kind)return ['bound_companion','wisp_swarm'].includes(skill.summoner_kind)?'summon':skill.summoner_kind==='life_pact'?'heal':skill.summoner_kind==='transposition'?'control':skill.summoner_kind==='overload'?'ally':'damage';
  const effects=skill.effects||[],has=type=>effects.some(e=>e.type===type);
  if(skill.druid_kind)return skill.druid_kind==='bramble_wall'?'control':skill.druid_kind==='rejuvenation'?'heal':skill.druid_kind==='living_armor'?'ally':'self';
  if(skill.cleric_kind)return ['mend','heal','sanctuary','rest'].includes(skill.cleric_kind)?'heal':skill.cleric_kind==='smite'?'self':'control';
  if(skill.bard_kind==='jeering_verse')return 'control';
  if(skill.bard_kind==='cue_the_strike')return 'ally';
  if(['accelerando','quickening_chorus','war_anthem','song_of_peace','maestro','battle_musician'].includes(skill.bard_kind))return 'self';
  if(skill.mage_kind)return skill.mage_kind==='enchant_weapon'?'ally':['flash_freeze','singularity','typhoon'].includes(skill.mage_kind)?'control':skill.mage_kind==='fireball'?'dot':'damage';
  if(['poison_attack','pestilence_shot','rupturing_blow'].includes(skill.ranger_kind))return 'dot';
  if(skill.ranger_kind==='rapid_fire')return 'self';
  if(skill.rogue_kind==='caltrops')return 'dot';
  if(['shadowstep','backflip'].includes(skill.rogue_kind))return 'self';
  if(skill.rogue_kind==='crippling_cut')return 'control';
  if(has('area_attack'))return 'damage';
  if(skill.self_only&&!has('heal'))return 'self';
  if(has('deploy'))return 'summon';
  if(skill.heal||skill.cleanses||has('heal')||has('cleanse')||effects.some(e=>e.status==='regeneration'))return 'heal';
  if(skill.reaction?.id==='intercept')return 'ally';
  if(['riposte','returning_hand'].includes(skill.reaction?.id))return 'damage';
  if(has('form')||skill.type==='passive')return 'self';
  if(skill.guard_ally||has('barrier')||has('guard'))return skill.target==='self'?'self':'ally';
  if(effects.some(e=>['burn','poison','bleed'].includes(e.status)||['ember','thorns'].includes(e.zone))||['burn','poison','bleed'].includes(skill.on_hit?.id))return 'dot';
  if(has('displace')||has('mark')||has('zone')||has('status'))return 'control';
  if(skill.target==='ally')return 'ally';
  return 'damage';
}
export const FIGHTER_ICON_ART={'job:fighter:cover':'chain-snare','job:fighter:pull':'earthbreaker','job:fighter:rally':'hold-together'};
export function skillIcon(skill){
  if(skill.mount_kind)return `/assets/boar-mount-v1/${skill.self_only?'dismount_icon':'mount_icon'}.png`;
  if(['tripline','shakedown','parting_cut','ankle_bite','goliath_shot','tag_team','cornered_fury','heel_cut'].includes(skill.id?.split(':').at(-1))&&skill.id.startsWith('npc:bandit:'))return `/assets/enemy-specialties-v1/${skill.id.split(':').at(-1)}.png`;
  if(skill.id==='npc:bandit:road_bola')return '/assets/captor-v1/bola.png';
  if(/^job:captor:(subduing_blow|bola|hook_and_drag|abduct|restraining_hold|blitz|restraint|clean_capture)$/.test(skill.id))return `/assets/captor-v1/${skill.id.split(':').at(-1)}.png`;
  if(skill.engineer_kind)return `/assets/engineer-v2/${skill.engineer_kind}.png`;
  if(skill.id==='innate:summoner:orders')return '/assets/summoner-v1/bound_companion.png';
  if(/^job:summoner:(transposition|bound_companion|wisp_swarm|spirit_projection|sacrifice|overload|life_pact|rapid_conjuration)$/.test(skill.id))return `/assets/summoner-v1/${skill.id.split(':').at(-1)}.png`;
  if(/^job:druid:(prowler|bulwark|rat|rejuvenation|bramble_wall|living_armor|natures_persistence|wild_instinct)$/.test(skill.id))return `/assets/druid-v1/${skill.form_return?'humanoid':skill.id.split(':').at(-1)}.png`;
  if(/^job:cleric:(mend|heal|sanctuary|rest|smite|exorcist|holy_light|battle_priest)$/.test(skill.id))return `/assets/cleric-v1/${skill.id.split(':').at(-1)}.png`;
  if(/^job:bard:(jeering_verse|cue_the_strike|battle_musician|accelerando|quickening_chorus|war_anthem|song_of_peace|maestro)$/.test(skill.id))return `/assets/bard-v1/${skill.id.split(':').at(-1).replaceAll('_','-')}.png`;
  if(/^job:mage:(chain_lightning|flash_freeze|singularity|meteor|fireball|enchant_weapon|typhoon|debuffer)$/.test(skill.id))return `/assets/mage-v1/${skill.id.split(':').at(-1)}.png`;
  if(/^job:ranger:(mark_quarry|longshot|multi_shot|rapid_fire|poison_attack|pestilence_shot|rupturing_blow|sharpshooter)$/.test(skill.id))return `/assets/ranger-v1/${skill.id.split(':').at(-1)}.png`;
  if(/^job:rogue:(cheap_shot|crippling_cut|exploit_weakness|shadowstep|caltrops|backflip|trap_expert|throwing_knife)$/.test(skill.id))return `/assets/rogue-v1/${skill.id.split(':').at(-1)}.png`;
  if(/^job:monk:(rapid_palm|crushing_fist|iron_reversal|breaking_combination|heaven_piercing|sweeping_dash|perfect_rhythm|flowing_footwork)$/.test(skill.id))return `/assets/monk-v1/${skill.id.split(':').at(-1)}.png`;
  if(MARTIAL_ICON_ART[skill.id])return MARTIAL_ICON_ART[skill.id];
  if(FIGHTER_ICON_ART[skill.id])return '/assets/combat-fighter-v3/'+FIGHTER_ICON_ART[skill.id]+'.png';
  if(JOB_ICON_ART[skill.id])return JOB_ICON_ART[skill.id];
  const category=skillCategory(skill),effects=skill.effects||[];
  const dot=effects.find(e=>['burn','poison','bleed'].includes(e.status))?.status||skill.on_hit?.id;
  const fallback={damage:skill.elevation_rule==='ballistic'?'job:ranger:mark':skill.elevation_rule==='melee'?'job:fighter:bash':'job:mage:scorch',
    dot:dot==='poison'?'job:ranger:poison':dot==='bleed'?'job:rogue:bleed':'job:mage:embers',
    control:effects.some(e=>e.type==='displace')?'job:captor:pull':'job:captor:bind',self:'job:monk:stance',ally:'job:cleric:barrier',heal:'job:cleric:mend',summon:'job:summoner:wisps'};
  return JOB_ICON_ART[fallback[category]];
}
export function skillIconMarkup(skill,escape){
  const category=skillCategory(skill),meta=SKILL_CATEGORIES[category];
  return `<span class="ability-icon category-${category}" style="--skill-accent:${meta.color}" title="${escape(meta.label)}"><img src="${skillIcon(skill)}" alt="" draggable="false" loading="lazy"><span class="ability-category-badge" aria-hidden="true">${meta.badge}</span>${skill.type==='passive'?'<span class="ability-passive-badge">P</span>':''}</span>`;
}
