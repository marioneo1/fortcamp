import test from 'node:test';
import assert from 'node:assert/strict';
import {combatAudioSchedule} from './combat-audio.js';
import {impactTimeline} from './combat-impact.js';

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
  assert.equal(cues[1].delay,185);
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
  assert.equal(cues[1].name,`melee_${style}_${surface==='flesh'?'flesh':'hit'}`);
  assert.equal(cues[1].delay,185);
 }
 const cues=combatAudioSchedule({},[{type:'melee_attack',melee_style:'slash',impact_surface:'flesh',hit:true,attack_packet:1},{type:'combat_feedback',kind:'physical',amount:0,absorbed:20,attack_packet:1}]).cues;
 assert.ok(!cues.some(c=>c.name==='melee_slash_flesh'));
});
test('a landed but escaped net squeezes then slips while a miss never cinches',()=>{
 const cues=combatAudioSchedule({},[{type:'net_cast',hit:true,captured:false}]).cues;
 assert.deepEqual(cues.map(c=>c.name),['capture_net_cast','capture_net_cinch','capture_net_slip']);
 assert.equal(cues[1].delay,320);assert.equal(cues[2].delay,450);
});
