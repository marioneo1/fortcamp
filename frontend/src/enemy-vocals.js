// Only explicit identities and the previously saved audited enemy profiles opt in.
export const VOCAL_KEYS=Object.freeze(['human','goblin'].flatMap(race=>['male','female'].flatMap(gender=>
 ['guardian','strategist','opportunist','survivor'].map(personality=>`${race}_${gender}_${personality}`))));
const allowed=new Set(VOCAL_KEYS);
export const VOCAL_FILES=Object.freeze(Object.fromEntries(VOCAL_KEYS.flatMap(key=>
 ['attack','hurt','death'].flatMap(event=>[1,2,3].map(variant=>[
  `vocal_${key}_${event}_${variant}`,`${key.startsWith('goblin_female_')||(key.startsWith('human_female_')&&event==='attack')?'enemy-vocals-female-v2':'enemy-vocals-v1'}/${key}_${event}_${variant}.wav`])))));
export function vocalKey(unit){
 if(!unit||unit.creature||unit.species_profile||unit.temporary)return null;
 if(allowed.has(unit.combat_voice_key))return unit.combat_voice_key;
 if(!['road_enforcer','road_cutpurse'].includes(unit.encounter_profile))return null;
 const key=`${String(unit.race||'').toLowerCase()}_${unit.gender}_${unit.personality_id}`;
 return allowed.has(key)?key:null;
}
export function battleVocalFiles(battle){
 const keys=new Set(Object.values(battle?.units||{}).map(vocalKey).filter(Boolean));
 return Object.fromEntries(Object.entries(VOCAL_FILES).filter(([name])=>
  [...keys].some(key=>name.startsWith(`vocal_${key}_`))));
}

export function humanoidVocalCues(battle,rows){
 const cues=[],played=new Set(),last=new Map();
 const unit=id=>battle?.units?.[id];
 const vocal=(id,event,row,index)=>{
  const key=vocalKey(unit(id));if(!key)return;
  const packet=row.event.attack_packet??`event:${index}`;
  const signature=`${id}:${event}:${event==='death'?'once':packet}`;
  if(played.has(signature))return;
  const channel=`${id}:${event}`;
  if(event!=='death'&&row.start-(last.get(channel)??-Infinity)<(event==='attack'?900:500))return;
  played.add(signature);last.set(channel,row.start);
  const hash=[id,packet,battle.round||0,unit(id)?.ability_activation||0,event].join(':')
   .split('').reduce((n,c)=>(n*31+c.charCodeAt(0))>>>0,0);
  cues.push({name:`vocal_${key}_${event}_${1+hash%3}`,volume:event==='attack'?.21:event==='hurt'?.25:.3,delay:row.start});
 };
 const fatal=e=>rows.some(({event:f})=>['death_burst','knockout'].includes(f.type)&&f.unit_id===e.unit_id&&f.attack_packet===e.attack_packet);
 rows.forEach((row,index)=>{
  const e=row.event;
  if(['melee_attack','net_cast','chain_attack','rogue_knife'].includes(e.type)||e.attack_event){
   if(e.target_kind!=='terrain')vocal(e.attacker_id,'attack',row,index);
  }else if(e.type==='combat_feedback'&&e.amount>0&&['physical','magic','fire','frost','ice','lightning','collision','fall','resolve'].includes(e.kind)&&!fatal(e)){
   vocal(e.unit_id,'hurt',row,index);
  }else if(['death_burst','knockout'].includes(e.type)){
   vocal(e.unit_id,e.type==='death_burst'?'death':'hurt',row,index);
  }
  if(e.type==='sound'){
   // Older ranged packets can carry their outcome without a collapse event.
   for(const cue of e.cues||[])if(['unit_death','unit_unconscious'].includes(cue.name)&&
    !rows.some(({event:f})=>['death_burst','knockout'].includes(f.type)&&f.unit_id===e.target_id&&f.attack_packet===e.attack_packet)){
     vocal(e.target_id,cue.name==='unit_death'?'death':'hurt',{...row,start:row.start+(cue.offset||0)},index);
    }
  }
  if(e.type==='melee_attack'&&e.hit&&['dead','unconscious'].includes(e.target_condition)&&
   !rows.some(({event:f})=>['death_burst','knockout'].includes(f.type)&&f.unit_id===e.target_id&&f.attack_packet===e.attack_packet)){
   vocal(e.target_id,e.target_condition==='dead'?'death':'hurt',{...row,start:row.start+(e.contact_ms??185)},index);
  }
 });
 return cues;
}
