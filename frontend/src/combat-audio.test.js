import test from 'node:test';
import assert from 'node:assert/strict';
import {combatAudioSchedule} from './combat-audio.js';
import {impactTimeline} from './combat-impact.js';
test('Rapid Assembly preparation sound plays with its visual at activation',()=>{
 const events=[{type:'martial_effect',skill:'engineer_rapid_assembly',attack_event:true,attack_packet:1},{type:'sound',attack_packet:1,before_contact:true,cues:[{name:'engineer_rapid_assembly',offset:0}]}];
 assert.equal(combatAudioSchedule({},events).cues.find(c=>c.name==='engineer_rapid_assembly').delay,0);
});
test('Explosive ballista sound lands with its bolt rather than when fired',()=>{
 const events=[{type:'sound',attack_event:true,attack_packet:1,cues:[]},{type:'martial_effect',attack_event:true,attack_packet:2,impact_origin_packet:1,skill:'engineer_cross_blast'},{type:'sound',attack_packet:2,cues:[{name:'engineer_bolt_explosion',offset:0}]}];
 const cues=combatAudioSchedule({},events).cues;
 assert.equal(cues.find(c=>c.name==='engineer_bolt_explosion').delay,220);
});

test('Earthbreaker sound follows takeoff and landing rather than footsteps',()=>{
 const events=[{type:'movement',leap:true,points:[{x:0,y:0},{x:3,y:0}]},{type:'ground_impact',attack_packet:1}];
 const cues=combatAudioSchedule({},events).cues;
 assert.deepEqual(cues.map(c=>c.name),['earthbreaker_launch','earthbreaker_land','earthbreaker_crater']);
 assert.equal(cues[0].delay,0);
 assert.equal(cues[1].delay,impactTimeline(events)[1].start);
 assert.ok(cues[1].delay>400);
 assert.equal(cues[2].delay,cues[1].delay);
 assert.equal(cues[1].volume,.65);
});
test('Bard commands and Songs resolve to dedicated SFX',()=>{
 const songs=['jeering_verse','cue_strike','accelerando','quickening_chorus','war_anthem','song_of_peace'];
 for(const song of songs){
  const cues=combatAudioSchedule({},[{type:'bard_song',song}]).cues;
  assert.deepEqual(cues.map(c=>c.name),[`bard_${song}`]);
 }
});
test('Collision audio uses contact, distinguishes bodies/walls and avoids duplicate damage sounds',()=>{
 for(const bystander_id of [null,'other']){
  const events=[{type:'melee_attack',attack_packet:1},
   {type:'movement',unit_id:'target',forced:true,collision:true,attack_packet:1,points:[{x:1,y:0},{x:2,y:0}]},
   {type:'collision_recoil',unit_id:'target',attack_packet:1,after_displacement:true,bystander_id},
   {type:'combat_feedback',kind:'collision',attack_packet:1,after_displacement:true}];
  const cues=combatAudioSchedule({},events).cues.filter(c=>c.name.startsWith('body_')||c.name==='collision_hit');
  assert.equal(cues.length,1);
  assert.equal(cues[0].name,bystander_id?'body_into_body':'body_into_wall');
  assert.equal(cues[0].delay,impactTimeline(events)[2].start);
 }
});
test('Terrain gets structure impact rather than flesh impact and duplicate swing',()=>{
 const cues=combatAudioSchedule({},[{type:'melee_attack',target_kind:'terrain',hit:true,attack_packet:1},
  {type:'sound',attack_packet:1,attack_event:true,cues:[{name:'melee_swing',offset:45},{name:'structure_hit',offset:185}]}]).cues;
 assert.deepEqual(cues.map(c=>c.name),['melee_swing','structure_hit']);
});

test('wall collisions play slightly louder than body collisions',()=>{
 const body=combatAudioSchedule({},[{type:'collision_recoil',bystander_id:'other'}]).cues[0];
 const wall=combatAudioSchedule({},[{type:'collision_recoil',bystander_id:null}]).cues[0];
 assert.equal(body.volume,.5);assert.equal(wall.volume,.63);
});

test('chain misses do not play a flesh impact',()=>{
 const cues=combatAudioSchedule({},[{type:'chain_attack',hit:false,attack_packet:1}]).cues;
 assert.deepEqual(cues.map(c=>c.name),['melee_swing','attack_miss']);
});


test('weapon swings and impacts use the family and shared contact; misses have no hit sound',()=>{
 for(const style of ['slash','hack','crush','blunt','fist','stab'])for(const hit of [true,false]){
  const cues=combatAudioSchedule({},[{type:'melee_attack',melee_style:style,hit,attack_packet:1}]).cues;
  assert.deepEqual(cues.map(c=>c.name),[`melee_${style}_swing`,hit?`melee_${style}_hit`:'attack_miss']);
  assert.equal(cues.at(-1).delay,185);
 }
});
test('net success and slip play at the result marker without flesh or damage sounds',()=>{
 for(const hit of [true,false]){
  const cues=combatAudioSchedule({},[{type:'net_cast',hit,attack_packet:1}]).cues;
  assert.deepEqual(cues.map(c=>c.name),['capture_net_cast',hit?'capture_net_cinch':'capture_net_slip']);
  assert.equal(cues[1].delay,320);
 }
});


test('flesh gets wet or padded contacts while armor and automatons retain original hits',()=>{
 for(const style of ['slash','hack','crush','stab','blunt','fist'])for(const surface of ['flesh','metal','rigid']){
  const cues=combatAudioSchedule({},[{type:'melee_attack',melee_style:style,impact_surface:surface,hit:true}]).cues;
  assert.equal(cues.at(-1).name,`melee_${style}_${surface==='flesh'?'flesh':'hit'}`);
  assert.equal(cues.at(-1).delay,185);
 }
 const cues=combatAudioSchedule({},[{type:'melee_attack',melee_style:'slash',impact_surface:'flesh',hit:true,attack_packet:1},{type:'combat_feedback',kind:'physical',amount:0,absorbed:20,attack_packet:1}]).cues;
 assert.ok(!cues.some(c=>c.name==='melee_slash_flesh'));
});
test('a landed but escaped net squeezes then slips while a miss never cinches',()=>{
 const cues=combatAudioSchedule({},[{type:'net_cast',hit:true,captured:false}]).cues;
 assert.deepEqual(cues.map(c=>c.name),['capture_net_cast','capture_net_cinch','capture_net_slip']);
 assert.equal(cues[1].delay,320);assert.equal(cues[2].delay,450);
});

test('flesh sword cut uses the approved flesh contact alone, while metal and misses retain their swing',()=>{
 for(const [surface,hit] of [['flesh',true],['metal',true],['flesh',false]]){
  const cues=combatAudioSchedule({},[{type:'melee_attack',melee_style:'slash',impact_surface:surface,hit}]).cues;
  if(surface==='flesh'&&hit)assert.deepEqual(cues.map(c=>c.name),['melee_slash_flesh']);
  else assert.equal(cues[0].name,'melee_slash_swing');
 }
});

test('melee family and chain swings remain quieter than their contact, including structures',()=>{
 for(const type of ['melee_attack','chain_attack']){
  const cues=combatAudioSchedule({},[{type,melee_style:'hack',impact_surface:'flesh',hit:true}]).cues;
  assert.equal(cues[0].volume,.12);assert.equal(cues[1].volume,.55);
 }
 const cues=combatAudioSchedule({},[{type:'sound',cues:[{name:'melee_swing',offset:45},{name:'structure_hit',offset:185}]}]).cues;
 assert.equal(cues[0].volume,.12);assert.equal(cues[1].volume,.55);
});

const animalBattle={round:1,units:{rat:{species_profile:'store_rat'},wolf:{species_profile:'fence_wolf'},human:{}}};
test('boar attack belongs to free boars; mounted damage and death still vocalize',()=>{
 const free={units:{b:{species_profile:'saddle_boar'},r:{animal_mount_id:'b'}}};
 const attack={type:'melee_attack',attacker_id:'b',target_id:'human',hit:true,melee_style:'bite'};
 assert.ok(combatAudioSchedule(free,[attack]).cues.some(c=>c.name.startsWith('boar_attack_')));
 const mounted={units:{...free.units,b:{...free.units.b,rider_id:'r'}}};
 assert.ok(!combatAudioSchedule(mounted,[attack,{...attack,attacker_id:'r'}]).cues.some(c=>c.name.startsWith('boar_attack_')));
 const cues=combatAudioSchedule(mounted,[{type:'combat_feedback',unit_id:'b',kind:'physical',amount:2,attack_packet:1},{type:'combat_feedback',unit_id:'b',kind:'heal',amount:2},{type:'death_burst',unit_id:'b',attack_packet:2}]).cues;
 assert.equal(cues.filter(c=>c.name.startsWith('boar_hurt_')).length,1);
 assert.equal(cues.filter(c=>c.name.startsWith('boar_death_')).length,1);
});
test('bear claws retain flesh contact but its voice and death are animal cues',()=>{
 const b={units:{bear:{species_profile:'foraging_bear'}}};
 const cues=combatAudioSchedule(b,[{type:'melee_attack',attacker_id:'bear',target_id:'human',melee_style:'slash',impact_surface:'flesh',hit:true,attack_packet:1},{type:'death_burst',unit_id:'bear',attack_packet:2}]).cues;
 assert.ok(cues.some(c=>c.name.startsWith('bear_attack_')));
 assert.ok(cues.some(c=>c.name==='melee_slash_flesh'));
 assert.ok(cues.some(c=>c.name.startsWith('bear_death_')));
 assert.ok(!cues.some(c=>c.name==='unit_death'||c.name.startsWith('bear_bite')));
});
test('three-rat swarm has three timed bite contacts and no weapon swing',()=>{
 const cues=combatAudioSchedule(animalBattle,[{type:'melee_attack',attacker_id:'rat',target_id:'human',bite_count:3,contact_ms:460,attack_duration:540,hit:true}]).cues;
 assert.deepEqual(cues.filter(c=>c.name.startsWith('rat_bite')).map(c=>c.delay),[100,280,460]);
 assert.ok(cues.some(c=>c.name.startsWith('rat_attack')));
 assert.ok(!cues.some(c=>c.name.startsWith('melee_')));
});
test('missed animal bite has effort but no flesh contact or hurt cry',()=>{
 const cues=combatAudioSchedule(animalBattle,[{type:'melee_attack',attacker_id:'wolf',target_id:'rat',hit:false}]).cues;
 assert.ok(cues.some(c=>c.name.startsWith('wolf_attack')));
 assert.ok(!cues.some(c=>c.name.includes('_bite_')||c.name.includes('_hurt_')));
});
test('final dead state never schedules death until its resolved death event',()=>{
 const battle={units:{rat:{species_profile:'store_rat',condition:'dead',alive:false}}};
 const events=[{type:'melee_attack',attacker_id:'human',target_id:'rat',hit:true,attack_packet:2},{type:'combat_feedback',unit_id:'rat',kind:'physical',amount:6,attack_packet:2},{type:'death_burst',unit_id:'rat',attack_packet:2}];
 const cues=combatAudioSchedule(battle,events).cues;
 const deaths=cues.filter(c=>c.name.startsWith('rat_death'));
 assert.equal(deaths.length,1);assert.ok(deaths[0].delay>185);
 assert.ok(!cues.some(c=>c.name==='unit_death'||c.name.startsWith('rat_hurt')));
 assert.ok(!combatAudioSchedule(battle,[]).cues.length);
});
test('animal hurt cry follows actual damage, not zero damage or status application',()=>{
 const events=[{type:'combat_feedback',unit_id:'wolf',kind:'physical',amount:3},{type:'combat_feedback',unit_id:'wolf',kind:'physical',amount:0},{type:'combat_feedback',unit_id:'wolf',kind:'status',status_id:'hobble'}];
 const cues=combatAudioSchedule(animalBattle,events).cues;
 assert.equal(cues.filter(c=>c.name.startsWith('wolf_hurt')).length,1);
});
test('rat merge uses gathering audio and variations change across activations',()=>{
 const events=[{type:'rat_merge',unit_id:'rat',target_id:'rat2'}];
 const variants=[1,2,3].map(round=>combatAudioSchedule({...animalBattle,round},events).cues[0].name);
 assert.equal(new Set(variants).size,3);assert.ok(variants.every(n=>n.startsWith('rat_swarm')));
});
