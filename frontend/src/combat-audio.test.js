import test from 'node:test';
import assert from 'node:assert/strict';
import {combatAudioSchedule} from './combat-audio.js';
import {impactTimeline} from './combat-impact.js';

test('Earthbreaker sound follows takeoff and landing rather than footsteps',()=>{
 const events=[{type:'movement',leap:true,points:[{x:0,y:0},{x:3,y:0}]},{type:'ground_impact',attack_packet:1}];
 const cues=combatAudioSchedule({},events).cues;
 assert.deepEqual(cues.map(c=>c.name),['earthbreaker_launch','earthbreaker_land']);
 assert.equal(cues[0].delay,0);
 assert.equal(cues[1].delay,impactTimeline(events)[1].start);
 assert.ok(cues[1].delay>400);
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
