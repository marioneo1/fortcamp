import test from 'node:test';
import assert from 'node:assert/strict';
import {composeMotion,poseFrames,walkingFrames,createPlaybackGate,needsPlaybackLock,playbackDuration,departureGhostPlans} from './combat-playback.js';
import {impactTimeline} from './combat-impact.js';
import {recoilFrames} from './combat-animation.js';

test('dismissed summons stay represented until their late killing contact, without duplicate dissolve ghosts',()=>{
 const previous={units:{w:{id:'w',alive:true,hp:1,condition:'active',summoner_creature:true}}};
 const battle={units:{w:{id:'w',alive:false,extracted:true,condition:'dismissed',summoner_creature:true}}};
 const timeline=impactTimeline([{type:'melee_attack',attacker_id:'first',target_id:'owner',attack_packet:1},
  {type:'melee_attack',attacker_id:'second',target_id:'owner',attack_packet:2},
  {type:'melee_attack',attacker_id:'last',target_id:'w',attack_packet:3},
  {type:'death_burst',unit_id:'w',attack_packet:3},
  {type:'martial_effect',skill:'summoner_dissolve',unit_id:'w',attack_packet:4}]);
 const plans=departureGhostPlans(previous,battle,timeline);
 assert.equal(plans.length,1);assert.equal(plans[0].event.type,'death_burst');
 assert.equal(plans[0].before.hp,1);assert.ok(plans[0].start>timeline[1].start+timeline[1].duration);
});
test('Reclaim, Sacrifice and Overload dissolution also retain a presentation body until their own event',()=>{
 for(const skill of ['summoner_dissolve','summoner_sacrifice']){
  const previous={units:{s:{id:'s',alive:true,hp:20}}},battle={units:{s:{alive:false,condition:'dismissed',summoner_creature:true}}};
  const rows=[{start:900,duration:560,event:{type:'martial_effect',unit_id:'s',skill}}];
  assert.equal(departureGhostPlans(previous,battle,rows)[0].start,900);
  assert.deepEqual(departureGhostPlans(battle,battle,rows),[]);
 }
});
test('a summon born and killed during one server response still receives its conjure and departure presentation',()=>{
 const battle={units:{s:{id:'s',hp:0,max_hp:30,alive:false,extracted:true,condition:'dismissed',summoner_creature:true}}};
 const rows=[{start:0,duration:560,event:{type:'martial_effect',unit_id:'s',skill:'summoner_conjure'}},
  {start:2000,duration:560,event:{type:'martial_effect',unit_id:'s',skill:'summoner_dissolve'}}];
 const plan=departureGhostPlans({units:{}},battle,rows)[0];
 assert.equal(plan.before.hp,30);assert.equal(plan.before.condition,'active');assert.equal(plan.before.extracted,false);
 assert.equal(plan.start,2000);assert.equal(battle.units.s.hp,0);
 assert.deepEqual(departureGhostPlans({units:{}},battle,rows.slice(1)),[]);
});

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

test('every walking segment ends at its destination, never a later response position',()=>{
 for(const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]]){
  const actor={x:5+dx,y:5+dy},points=[{x:2,y:2},{x:2+dx,y:2+dy}];
  const frames=walkingFrames(points,actor,80,60);
  assert.equal(frames.at(-1).transform,`translate(${(points[1].x-actor.x)*80}px,${(points[1].y-actor.y)*60}px) scale(1)`);
 }
});

test('walk, attack, counter and walk again share continuous standing poses',()=>{
 const actor={x:5,y:2};
 const first=walkingFrames([{x:1,y:2},{x:3,y:2}],actor,100,100);
 const attack=poseFrames([{transform:'translate(0px,0px) scale(1)',offset:0},{transform:'translate(40px,0px) scale(1)',offset:.5},{transform:'translate(0px,0px) scale(1)',offset:1}],{x:3,y:2},actor,100,100);
 const next=walkingFrames([{x:3,y:2},{x:5,y:2}],actor,100,100);
 const result=composeMotion([{frames:first,delay:0,duration:220},{frames:attack,delay:290,duration:400},{frames:next,delay:760,duration:220}]);
 const held=result.frames.find(f=>f.offset===760/result.duration);
 assert.equal(held.transform,'translate(-200px,0px) translate(0px,0px) scale(1)');
 assert.equal(result.frames.at(-1).transform,'translate(0px,0px) scale(1)');
 assert.ok(result.frames.every((f,i)=>!i||f.offset>=result.frames[i-1].offset));
});

test('enemy pursuit waits for the whole landing effect and all collision recovery',()=>{
 const rows=impactTimeline([{type:'ground_impact',attack_packet:1},
  {type:'movement',unit_id:'a',forced:true,attack_packet:2,impact_origin_packet:1,impact_offset:133,points:[{x:1,y:1},{x:2,y:1}]},
  {type:'movement',unit_id:'b',forced:true,attack_packet:3,impact_origin_packet:1,impact_offset:377,points:[{x:1,y:2},{x:2,y:2}]},
  {type:'collision_recoil',unit_id:'b',attack_packet:3,after_displacement:true},
  {type:'movement',unit_id:'a',points:[{x:2,y:1},{x:3,y:1}]}]);
 assert.ok(rows.at(-1).start>=rows[0].start+rows[0].duration);
 for(const row of rows.slice(1,-1))assert.ok(rows.at(-1).start>=row.start+row.duration);
});

test('an interrupted preview settles before attack contact, without a pose jump',()=>{
 const actor={x:3,y:2},points=[{x:1.4,y:2},{x:3,y:2}];
 const rows=impactTimeline([{type:'movement',unit_id:'p',preview_settle:true,duration:220,points},
  {type:'melee_attack',attacker_id:'p',attack_packet:1}]);
 assert.equal(rows[1].start,290);
 const frames=walkingFrames(points,actor,100,100);
 assert.equal(frames[0].transform,'translate(-160px,0px) scale(1)');
 assert.equal(frames.at(-1).transform,'translate(0px,0px) scale(1)');
});
test('a delayed hit reaction holds the neutral pose until contact',()=>{
 const frames=recoilFrames(12,0);
 assert.equal(frames[0].transform,'translate(0px,0px) scale(1)');
 assert.equal(frames[0].filter,'brightness(1)');
 assert.equal(frames.at(-1).transform,'translate(0,0) scale(1)');
});

test('lethal knockback completes its rebound before collapse and the next enemy',()=>{
 const rows=impactTimeline([{type:'melee_attack',attack_packet:42},
  {type:'death_burst',unit_id:'e',attack_packet:42},
  {type:'movement',unit_id:'e',forced:true,attack_packet:42,points:[{x:2,y:2},{x:3,y:2}]},
  {type:'collision_recoil',unit_id:'e',attack_packet:42},
  {type:'movement',unit_id:'next',points:[{x:4,y:2},{x:5,y:2}]}]);
 const push=rows.find(r=>r.event.forced),death=rows.find(r=>r.event.type==='death_burst');
 assert.ok(death.start>=push.start+push.duration);
 assert.ok(rows.at(-1).start>=death.start+death.duration);
});
test('walking retains its hop and tilt; forced movement stays a slide',()=>{
 const p=[{x:1,y:1},{x:2,y:1}],u={x:2,y:1};
 const walk=walkingFrames(p,u,100,100),slide=walkingFrames(p,u,100,100,1,false,'slide');
 assert.match(walk[1].transform,/,-5px/);assert.match(walk[1].transform,/rotate\(-2deg\)/);
 assert.match(slide[1].transform,/,0px/);assert.match(slide[1].transform,/scale\(1\)/);
 assert.equal(walk.at(-1).transform,'translate(0px,0px) scale(1)');
});

test('a pulled enemy cannot start its own attack until both collision rebounds finish',()=>{
 const events=[{type:'chain_attack',attack_packet:1,attacker_id:'p',target_id:'e'},
  {type:'movement',unit_id:'e',forced:true,attack_packet:1,points:[{x:5,y:2},{x:4,y:2}]},
  {type:'collision_recoil',unit_id:'e',bystander_id:'ally',attack_packet:1,after_displacement:true},
  {type:'melee_attack',attacker_id:'e',target_id:'ally',attack_packet:2}];
 const rows=impactTimeline(events),collision=rows[2],attack=rows[3];
 assert.ok(attack.start>=collision.start+collision.duration+100);
 assert.ok(attack.start>=rows[1].start+rows[1].duration);
});


test('rat merging keeps the departing body until the merge and blocks subsequent motion',()=>{
 const events=[{type:'movement',unit_id:'rat',points:[{x:1,y:1},{x:2,y:1}]},
 {type:'rat_merge',unit_id:'rat',target_id:'swarm',unit_snapshot:{id:'rat',alive:true,hp:5}},
 {type:'melee_attack',attacker_id:'wolf',attack_packet:2}];
 const rows=impactTimeline(events);
 assert.ok(rows[1].start>=rows[0].start+rows[0].duration);
 assert.ok(rows[2].start>=rows[1].start+400);
});
