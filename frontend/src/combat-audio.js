import {impactTimeline} from './combat-impact.js';
import {COMBAT_MOTION} from './combat-animation.js';
export function combatAudioSchedule(battle,events=battle?.animation_events||[]){
  if(!battle)return {cues:[],duration:0};
  const cues=[],playSfx=(name,volume,delay=0)=>cues.push({name,volume,delay});
  let end=0;const impactSounds=new Set();
  for(const {event,start:delay,duration} of impactTimeline(events)){
    end=Math.max(end,delay+duration);
    if(event.type==='movement'&&event.leap)playSfx('earthbreaker_launch',.4,delay);
    else if(event.type==='ground_impact'){playSfx('earthbreaker_land',.65,delay);playSfx('earthbreaker_crater',.38,delay)}
    else if(event.type==='collision_recoil')playSfx(event.bystander_id?'body_into_body':'body_into_wall',event.bystander_id ? .5 : .63,delay);
    else if(event.type==='net_cast'){playSfx('capture_net_cast',.32,delay+35);playSfx(event.hit?'capture_net_cinch':'capture_net_slip',.4,delay+COMBAT_MOTION.netContact)}
    else if(event.type==='chain_attack'){playSfx('melee_swing',.35,delay+40);playSfx(event.hit?'melee_hit_light':'attack_miss',.4,delay+220)}
    else if(event.type==='sound'){
      for(const cue of event.cues||[]){if(['unit_death','unit_unconscious'].includes(cue.name)&&events.some(e=>['death_burst','knockout'].includes(e.type)&&e.attack_packet===event.attack_packet))continue;playSfx(cue.name,cue.name==='barrier_absorb'?.28:cue.name==='shield_block'?.35:.4,delay+(cue.offset||0))}
    }else if(event.type==='melee_attack'&&event.target_kind!=='terrain'){
      const style=['slash','hack','crush','blunt','fist','stab'].includes(event.melee_style)?event.melee_style:null;
      playSfx(style?`melee_${style}_swing`:'melee_swing',.32,delay+45);
      playSfx(event.hit?(event.target_condition==='unconscious'?'subdue_hit':style?`melee_${style}_hit`:'melee_hit_light'):'attack_miss',.45,delay+COMBAT_MOTION.contact);
      if(event.hit&&!events.some(e=>e.type==='death_burst'&&e.attack_packet===event.attack_packet)&&event.target_condition==='dead')playSfx('unit_death',.4,delay+330);
      else if(event.hit&&!events.some(e=>e.type==='knockout'&&e.attack_packet===event.attack_packet)&&event.target_condition==='unconscious')playSfx('unit_unconscious',.4,delay+315);
    }else if(event.type==='death_burst'||event.type==='knockout'){
      playSfx(event.type==='knockout'?'unit_unconscious':'unit_death',.4,delay+COMBAT_MOTION.collapse*.65);
    }else if(event.type==='combat_feedback'){
      if(event.kind==='collision'&&!events.some(e=>e.type==='collision_recoil'&&e.attack_packet===event.attack_packet)){
        const key=`collision:${event.attack_packet??delay}`;
        if(!impactSounds.has(key)){impactSounds.add(key);playSfx('collision_hit',.5,delay)}
      }else if(['burn','poison'].includes(event.kind))playSfx(`${event.kind}_tick`,.22,delay);
      else if(event.kind==='status'&&['burn','poison'].includes(event.status_id))playSfx(`${event.status_id}_tick`,.16,delay);
      else if(['bleed','thorns'].includes(event.kind)&&!event.attack_packet)playSfx('melee_hit_light',.16,delay);
    }else if(event.type==='movement'&&!event.forced&&!event.leap){
      // Walking cadence remains owned by the main audio player.
    }
  }
  return {cues,duration:end};
}
