import test from 'node:test';
import assert from 'node:assert/strict';
import {composeMotion,poseFrames,createPlaybackGate,needsPlaybackLock,playbackDuration} from './combat-playback.js';
import {impactTimeline} from './combat-impact.js';

const move=(from,to,delay,duration)=>({frames:[{transform:`translate(${from}px,0)`,offset:0},{transform:`translate(${to}px,0)`,offset:1}],delay,duration});
test('later enemy movement cannot prefill the pose before the initial push',()=>{
  const {frames,duration}=composeMotion([move(-100,0,185,220),move(0,100,700,220)]);
  assert.equal(duration,920);
  assert.equal(frames[0].transform,'translate(-100px,0)');
  assert.equal(frames.find(f=>f.offset===185/920).transform,'translate(-100px,0)');
  assert.equal(frames.find(f=>f.offset===700/920).transform,'translate(0px,0)');
  assert.ok(frames.every((f,i)=>!i||f.offset>=frames[i-1].offset));
});
test('Earthbreaker holds a victim at its original cell until wave contact, then permits pursuit',()=>{
  const events=[{type:'movement',leap:true,unit_id:'p',points:[{x:0,y:0},{x:3,y:0}]},
    {type:'ground_impact',attack_packet:1},
    {type:'movement',forced:true,unit_id:'e',attack_packet:2,impact_origin_packet:1,impact_offset:267,points:[{x:4,y:0},{x:5,y:0}]},
    {type:'movement',unit_id:'e',points:[{x:5,y:0},{x:6,y:0}]}];
  const rows=impactTimeline(events);
  const result=composeMotion(rows.filter(r=>r.event.unit_id==='e').map(r=>move(r.event.points[0].x*100,r.event.points.at(-1).x*100,r.start,r.duration)));
  assert.equal(result.frames[0].transform,'translate(400px,0)');
  const initial=result.frames.find(f=>f.offset===rows[2].start/result.duration);
  assert.equal(rows[2].start,757);assert.equal(initial.transform,'translate(400px,0)');
  assert.ok(rows[3].start>=rows[2].start+rows[2].duration);
});
test('an enemy lunge is anchored at its attack cell even when the final cell differs',()=>{
  const frames=poseFrames([{transform:'translate(30px,0) scale(1)'}],{x:3,y:2},{x:5,y:2},100,100);
  assert.equal(frames[0].transform,'translate(-200px,0px) translate(30px,0) scale(1)');
});
test('commands remain locked through the final enemy animation, but not lingering text',()=>{
  let time=100;const gate=createPlaybackGate(()=>time);
  const rows=[{event:{type:'movement'},start:600,duration:420},{event:{type:'combat_feedback'},start:900,duration:900}];
  gate.hold('encounter',playbackDuration(rows));time=1119;
  assert.equal(gate.blocked('encounter'),true);time=1120;
  assert.equal(gate.blocked('encounter'),false);
  gate.hold('encounter',500);assert.equal(gate.blocked('other'),false);
  gate.clear();assert.equal(gate.blocked('encounter'),false);
});
test('free player repositioning stays interruptible; attacks and enemy movement lock',()=>{
  const battle={units:{p:{team:'player'},e:{team:'enemy'}}};
  assert.equal(needsPlaybackLock([{type:'movement',unit_id:'p'}],battle),false);
  assert.equal(needsPlaybackLock([{type:'movement',unit_id:'e'}],battle),true);
  assert.equal(needsPlaybackLock([{type:'melee_attack'}],battle),true);
});
