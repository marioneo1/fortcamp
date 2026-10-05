import test from 'node:test';
import assert from 'node:assert/strict';
import {impactTimeline,feedbackText,protectionMarkup} from './combat-impact.js';

test('push starts at melee impact; collision follows movement; next enemy waits',()=>{
  const events=[{type:'melee_attack',attack_packet:1},
    {type:'combat_feedback',attack_packet:1,kind:'physical',amount:20},
    {type:'movement',attack_packet:1,forced:true,points:[{x:1,y:1},{x:2,y:1}]},
    {type:'combat_feedback',attack_packet:1,after_displacement:true,kind:'collision',amount:10},
    {type:'death_burst',attack_packet:1,after_displacement:true},
    {type:'melee_attack',attack_packet:2}];
  const rows=impactTimeline(events);
  assert.deepEqual(rows.slice(0,5).map(r=>r.start),[0,185,185,405,405]);
  assert.ok(rows[5].start>=rows[4].start+rows[4].duration);
});
test('projectile and its cues share a start; damage lands with projectile',()=>{
  const rows=impactTimeline([{type:'magic_projectile',attack_packet:3},
    {type:'sound',attack_event:true,duration:490,attack_packet:3},
    {type:'combat_feedback',attack_packet:3},
    {type:'sound',duration:0,attack_packet:3}]);
  assert.deepEqual(rows.map(r=>r.start),[0,0,220,0]);
});
test('unrelated DoT feedback does not add a full second of turn delay',()=>{
  const rows=impactTimeline([{type:'combat_feedback',kind:'burn'}, {type:'movement',points:[{},{}]}]);
  assert.equal(rows[1].start,100);
});
test('typed numbers have labels as well as colors',()=>{
  assert.equal(feedbackText({kind:'poison',amount:4}).value,'−4');
  assert.equal(feedbackText({kind:'heal',amount:5}).value,'+5');
  assert.equal(feedbackText({kind:'physical',amount:0,absorbed:8}).value,'Blocked');
  assert.equal(feedbackText({kind:'status',status_id:'bind'},{bind:{name:'Bind',icon:'X'}}).label,'Bind');
});
test('barrier capacity has a visible display; corpses do not have shields',()=>{
  assert.match(protectionMarkup({statuses:[{id:'barrier',amount:12}]}),/12/);
  assert.equal(protectionMarkup({condition:'dead',statuses:[{id:'barrier',amount:12}]}),'');
  assert.match(protectionMarkup({guarding:true}),/unit-guard-halo/);
});
