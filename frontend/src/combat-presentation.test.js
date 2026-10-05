import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {COMBAT_MOTION,weaponAttackFrames,weaponHitFrames,meleeFrames,collisionFrames,collapseFrames,collapsePlacement} from './combat-animation.js';
import {impactTimeline,impactArtwork} from './combat-impact.js';
import {JOB_ICON_ART} from './ability-icon-manifest.js';
import {skillCategory,skillIcon} from './ability-icons.js';
import {zoneOverlay} from './combat-spaces-ui.js';

test('melee peak is the exact shared sound and number contact marker',()=>{
  assert.equal(meleeFrames(30,0)[2].offset*COMBAT_MOTION.melee,COMBAT_MOTION.contact);
  const events=[{type:'melee_attack',attack_packet:1},{type:'combat_feedback',attack_packet:1}];
  assert.equal(impactTimeline(events)[1].start,COMBAT_MOTION.contact);
});
test('ground damage labels arrive at each crossed tile, including forced movement',()=>{
  for(const forced of [false,true]){
    const movement={type:'movement',unit_id:'t',ground_route_id:4,forced,points:[{x:0,y:0},{x:1,y:0},{x:2,y:0},{x:3,y:0}]};
    const rows=impactTimeline([movement,...[1,2,3].map(step=>({type:'combat_feedback',kind:'burn',amount:3,ground_route_id:4,ground_step:step}))]);
    assert.deepEqual(rows.slice(1).map(r=>r.start),[1,2,3].map(step=>rows[0].duration*step/3));
    assert.ok(rows[1].start<rows[0].start+rows[0].duration);
  }
});
test('collision contact precedes bounce recovery and lethal collapse',()=>{
  const events=[{type:'melee_attack',attack_packet:1},
    {type:'movement',unit_id:'target',forced:true,attack_packet:1,points:[{x:1,y:0},{x:2,y:0}]},
    {type:'collision_recoil',unit_id:'target',attack_packet:1,after_displacement:true,toward:{x:3,y:0}},
    {type:'combat_feedback',kind:'collision',attack_packet:1,after_displacement:true},
    {type:'death_burst',attack_packet:1,after_displacement:true}];
  const before=structuredClone(events),rows=impactTimeline(events);
  assert.equal(rows[3].start,185+COMBAT_MOTION.collisionContact);
  assert.equal(rows[4].start,185+Math.max(COMBAT_MOTION.collisionMove,COMBAT_MOTION.collisionContact+COMBAT_MOTION.collisionRecoil));
  const frames=collisionFrames(events[1].points,{x:2,y:0},{x:3,y:0},100,100);
  assert.equal(frames[1].offset*rows[1].duration,COMBAT_MOTION.collisionContact);
  assert.ok(Math.abs(parseFloat(frames[1].transform.split('(')[1])-28)<.01);
  assert.match(frames.at(-1).transform,/translate\(0px,0px\)/);
  assert.deepEqual(events,before);
});
test('stationary collision still bounces before knockout and next attack',()=>{
  const rows=impactTimeline([{type:'melee_attack',attack_packet:1},
    {type:'collision_recoil',unit_id:'t',attack_packet:1,after_displacement:true},
    {type:'combat_feedback',attack_packet:1,after_displacement:true},
    {type:'knockout',attack_packet:1},{type:'melee_attack',attack_packet:2}]);
  assert.equal(rows[2].start,185+COMBAT_MOTION.stationaryContact);
  assert.equal(rows[3].start,185+Math.max(COMBAT_MOTION.stationaryBounce,COMBAT_MOTION.stationaryContact+COMBAT_MOTION.collisionRecoil));
  assert.ok(rows[4].start>=rows[3].start+COMBAT_MOTION.collapse);
  assert.equal(collapseFrames(true).at(-1).opacity,0);
});
test('all 72 Job icons resolve to actual runtime assets; gear uses same art family',()=>{
  assert.equal(Object.keys(JOB_ICON_ART).length,72);
  for(const path of Object.values(JOB_ICON_ART))assert.ok(existsSync(new URL('../public'+path,import.meta.url)),path);
  assert.ok(skillIcon({id:'gear:test',heal:5}));
  assert.equal(skillCategory({heal:5}),'heal');
  assert.equal(skillCategory({guard_ally:true}),'ally');
  assert.equal(skillCategory({effects:[{type:'status',status:'poison'}]}),'dot');
  assert.deepEqual(impactArtwork({absorbed:5,barrier_broken:true}),['barrier_break']);
});
test('ground art covers only real affected cells and omits internal grid borders',()=>{
  const html=zoneOverlay([{id:'test',kind:'ember',cells:[{x:1,y:1},{x:2,y:1},{x:1,y:2}],name:'Ember',remaining:2}],String);
  assert.equal((html.match(/<rect /g)||[]).length,3);
  assert.match(html,/clip-path="url\(#zone-art-test\)"/);
  assert.match(html,/ember_ground.png/);
  assert.doesNotMatch(html,/M100,0v100/);
});

test("collapse ends at the final body centre, including edge-aligned corpses",()=>{
 const placement=collapsePlacement({x:100,y:100,width:80,height:80},{x:92,y:123,width:60,height:60});
 const frame=collapseFrames(false,placement).at(-1);
 assert.equal(frame.translate,"-18px 13px");assert.equal(frame.scale,"0.75");assert.equal(frame.rotate,"-18deg");
});


test('six melee families share contact but have distinct attack and hit poses',()=>{
 const styles=['slash','hack','crush','blunt','fist','stab'];
 const attacks=styles.map(s=>weaponAttackFrames(s,30,0));
 assert.equal(new Set(attacks.map(JSON.stringify)).size,6);
 assert.equal(new Set(styles.map(s=>JSON.stringify(weaponHitFrames(s,10,0)))).size,6);
 for(const frames of attacks){
  assert.equal(frames[2].offset*COMBAT_MOTION.melee,COMBAT_MOTION.contact);
  assert.match(frames.at(-1).transform,/translate\(0(?:px)?,0(?:px)?\)/);
 }
 for(const style of styles)for(const phase of ['contact','fade'])assert.ok(existsSync(new URL(`../public/assets/melee-families-v1/${style}_${phase}.png`,import.meta.url)));
 for(const phase of ['folded','opening','spread','cinched'])assert.ok(existsSync(new URL(`../public/assets/capture-net-v1/${phase}.png`,import.meta.url)));
});

test('net results coincide with cinching and recovery precedes defeat animation',()=>{
 const rows=impactTimeline([{type:'net_cast',attack_packet:9},{type:'combat_feedback',kind:'captured',attack_packet:9},{type:'knockout',attack_packet:9}]);
 assert.equal(rows[1].start,COMBAT_MOTION.netContact);
 assert.ok(rows[2].start>=COMBAT_MOTION.netContact+COMBAT_MOTION.recoil);
 assert.deepEqual(impactArtwork({kind:'captured'}),[]);
 assert.deepEqual(impactArtwork({kind:'capture_failed'}),[]);
});


test('blood contact art is confined to damaging organic cutting, piercing and crushing hits',()=>{
 for(const style of ['slash','hack','crush','stab']){
  assert.ok(impactArtwork({kind:'physical',amount:4,melee_style:style,impact_surface:'flesh'})[0].startsWith('flesh:'));
  assert.ok(impactArtwork({kind:'physical',amount:4,melee_style:style,impact_surface:'metal'})[0].startsWith('melee:'));
 }
 for(const style of ['blunt','fist'])assert.ok(impactArtwork({kind:'physical',amount:4,melee_style:style,impact_surface:'flesh'})[0].startsWith('melee:'));
 assert.deepEqual(impactArtwork({kind:'restraint',amount:3}),[]);
 assert.deepEqual(impactArtwork({kind:'physical',amount:0,absorbed:9,melee_style:'slash',impact_surface:'flesh'}),['barrier_hit']);
});
