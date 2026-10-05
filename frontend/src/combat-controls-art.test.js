import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {basicAttackArt} from './combat-controls-art.js';
import {chainLifetime,chainTravel,displacementPreviewMarkup} from './fighter-effects.js';

test('basic attack art follows weapon rules and capture overrides ranged magic',()=>{
 assert.equal(basicAttackArt({attack_elevation_rule:'ballistic'}),'ranged');
 assert.equal(basicAttackArt({attack_elevation_rule:'line_of_effect'}),'magic');
 assert.equal(basicAttackArt({attack_elevation_rule:'ignore',capture_weapon:true}),'subdue');
 assert.equal(basicAttackArt({attack_elevation_rule:'melee'}),'attack');
 for(const name of ['ranged','magic','pointer','loading','unavailable','chain_hook'])assert.ok(existsSync(new URL(`../public/assets/combat-controls-v2/${name}.png`,import.meta.url)));
});
test('hook reaches target at contact and lasts through movement and rebound',()=>{
 const event={type:'chain_attack',attack_packet:1};
 const events=[event,{type:'movement',unit_id:'target',forced:true,attack_packet:1,points:[{x:4,y:0},{x:3,y:0}]},{type:'collision_recoil',attack_packet:1,unit_id:'target',after_displacement:true}];
 assert.deepEqual(chainTravel({x:0,y:0},{x:100,y:40},110),{x:50,y:20});
 assert.deepEqual(chainTravel({x:0,y:0},{x:100,y:40},220),{x:100,y:40});
 assert.ok(chainLifetime(event,events)>520);
});
test('displacement markers distinguish endpoint and actual impact damage',()=>{
 const html=displacementPreviewMarkup({tactics:[{type:'pull',destination:{x:3,y:2},collision_cell:{x:2,y:2},solid_collision:true,collision_damage:6,collision_target_name:'Guard',bystander_damage:4}]},{width:8,height:8},String);
 assert.match(html,/PULL ENDS HERE/);assert.match(html,/IMPACT \+6 \/ Guard 4/);
 assert.equal(displacementPreviewMarkup(null,{width:8,height:8},String),'');
});
