import test from 'node:test';
import assert from 'node:assert/strict';
import {impactTimeline,movementDuration} from './combat-impact.js';
import {fighterEffectMarkup} from './fighter-effects.js';
import {skillIcon} from './ability-icons.js';
import {existsSync} from 'node:fs';
test('leap landing synchronizes impact damage and collision damage after flight',()=>{
 const events=[{type:'movement',unit_id:'actor',leap:true,points:[{x:0,y:0},{x:3,y:0}]},{type:'ground_impact',attack_packet:1},{type:'combat_feedback',kind:'physical',attack_packet:1},{type:'movement',unit_id:'enemy',forced:true,attack_packet:1,points:[{x:4,y:0},{x:5,y:0}]},{type:'collision_recoil',unit_id:'enemy',attack_packet:1},{type:'combat_feedback',kind:'collision',attack_packet:1,after_displacement:true}];
 const rows=impactTimeline(events);assert.equal(movementDuration(events[0]),420);assert.equal(rows[1].start,490);assert.equal(rows[2].start,490);assert.equal(rows[5].start,710);
});
test('chain contact uses its own attack packet and bounded world positions',()=>{
 const event={type:'chain_attack',attack_packet:2,from_point:{x:1,y:1},to_point:{x:4,y:4}};
 assert.equal(impactTimeline([event,{type:'combat_feedback',attack_packet:2}])[1].start,220);
 assert.match(fighterEffectMarkup(event,{width:8,height:8}),/viewBox="0 0 800 800"/);
 for(const id of ['cover','pull','rally'])assert.ok(existsSync(new URL('../public'+skillIcon({id:'job:fighter:'+id}),import.meta.url)));
});
