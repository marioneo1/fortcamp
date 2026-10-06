import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {skillIcon,skillCategory} from './ability-icons.js';
import {enchantCommand,mageStatusMarkup} from './mage-effects.js';
import {impactTimeline} from './combat-impact.js';
import {combatAudioSchedule} from './combat-audio.js';
import {zoneOverlay} from './combat-spaces-ui.js';
import {statusDetails} from './combat-status-ui.js';
import {selectBattleSkill} from './equipment-skills.js';
const escape=String;
test('Mage kit has eight matching painted icons and distinct tactical categories',()=>{
 for(const id of ['chain_lightning','flash_freeze','singularity','meteor','fireball','enchant_weapon','typhoon','debuffer'])assert.ok(existsSync(new URL('../public'+skillIcon({id:'job:mage:'+id}),import.meta.url)));
 assert.equal(skillCategory({mage_kind:'enchant_weapon'}),'ally');assert.equal(skillCategory({mage_kind:'flash_freeze'}),'control');assert.equal(skillCategory({mage_kind:'fireball'}),'dot');
});
test('Enchant choice preserves target, movement approach and skill; invalid choice rejected',()=>{
 const c={action:'skill',skill_id:'job:mage:enchant_weapon',target_id:'ally',move_to:{x:1,y:2}};assert.deepEqual(enchantCommand(c,'frost'),{...c,element:'frost'});assert.ok(!c.element);assert.throws(()=>enchantCommand(c,'random'));
});
test('Elemental ice, Wet and channel display attach only to living character',()=>{
 const u={statuses:[{id:'freeze',elemental_freeze:true},{id:'wet'},{id:'channeling'}]};assert.match(mageStatusMarkup(u),/mage-ice-shell/);assert.match(mageStatusMarkup(u),/mage-channel-orbit/);assert.equal(mageStatusMarkup({...u,alive:false}),'');assert.doesNotMatch(mageStatusMarkup({statuses:[{id:'freeze'}]}),/mage-ice-shell/);
});
test('Mage impact, collision and next enemy are sequenced together',()=>{
 const events=[{type:'mage_cast',attack_packet:1,contact_ms:240},{type:'combat_feedback',unit_id:'victim',kind:'magic',attack_packet:2,impact_origin_packet:1,impact_offset:0},{type:'movement',forced:true,unit_id:'victim',attack_packet:2,points:[{x:2,y:2},{x:3,y:2}]},{type:'melee_attack',attack_packet:3}];const t=impactTimeline(events);assert.equal(t[1].start,240);assert.equal(t[2].start,240);assert.ok(t[3].start>=790);
});
test('Chain bounces use short contact offsets, preserving flight/damage synchronization',()=>{
 const t=impactTimeline([{type:'mage_cast',attack_packet:1,contact_ms:240},{type:'mage_cast',attack_packet:2,contact_ms:240,impact_origin_packet:1,impact_offset:120},{type:'combat_feedback',attack_packet:2}]);assert.equal(t[1].start,120);assert.equal(t[2].start,360);
});
test('Meteor sound is a physical layered landing and fire; no magical shrill release',()=>{
 const s=combatAudioSchedule({units:{}},[{type:'mage_cast',mage_skill:'meteor',attack_packet:1,contact_ms:420}]);assert.equal(s.cues.filter(c=>c.name==='magic_cast').length,0);assert.ok(s.cues.every(c=>c.delay===420));assert.ok(s.cues.some(c=>c.name==='earthbreaker_crater'));
 for(const id of ['lightning','freeze','gravity','fireball','typhoon'])assert.ok(existsSync(new URL('../public/assets/sfx/mage_'+id+'.wav',import.meta.url)));
});
test('Ground warnings and scorch use explicit labels and painted top-down art',()=>{
 const z={cells:[{x:2,y:3}],owner_name:'Mage',name:'Meteor',remaining:1,description:'Leave before impact'};assert.match(zoneOverlay([{...z,kind:'meteor_armed'}],escape),/METEOR INCOMING/);assert.match(zoneOverlay([{...z,kind:'flash_freeze_armed'}],escape),/FREEZE ARMED/);assert.match(zoneOverlay([{...z,kind:'scorched'}],escape),/mage-v1\/scorched_tile/);
});
test('Enchantment and Frozen tooltips disclose element, duration and ice breaking',()=>{
 const e=statusDetails({id:'weapon_enchant',element:'lightning',turns:2,paralyzed_targets:['enemy']});assert.ok(e.details.some(v=>v.includes('LIGHTNING')));const f=statusDetails({id:'freeze',elemental_freeze:true,turns:2,wet_turns:4});assert.match(f.description,/Cannot act/);assert.ok(f.details.some(v=>v.includes('4 turns of Wet')));
});
test('Selecting Mage ally spell exposes ally preview even after an enemy spell',()=>{
 const s={id:'job:mage:enchant_weapon',target:'ally'};const v={current_unit_id:'p',units:{p:{skills:[s]}},attack_previews:{p:{},e:{skill:{}}},skill_previews:{[s.id]:{p:{support:true}}}};assert.equal(selectBattleSkill(v,s.id).attack_previews.p.skill.support,true);
});
