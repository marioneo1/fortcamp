import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {VOCAL_KEYS,VOCAL_FILES,vocalKey,battleVocalFiles} from './enemy-vocals.js';
import {combatAudioSchedule} from './combat-audio.js';
import {impactTimeline} from './combat-impact.js';
const unit=(key)=>({combat_voice_key:key});
const battle={round:1,units:{a:unit('human_male_guardian'),b:unit('goblin_female_survivor')}};
const vocals=(events,b=battle)=>combatAudioSchedule(b,events).cues.filter(c=>c.name.startsWith('vocal_'));

test('all 16 opt-in identities have three valid mono clips per combat event',()=>{
 assert.equal(VOCAL_KEYS.length,16);assert.equal(Object.keys(VOCAL_FILES).length,144);
 const manifest=JSON.parse(fs.readFileSync(new URL('../public/assets/sfx/voice-tester/manifest.json',import.meta.url)));
 assert.deepEqual([...manifest.keys].sort(),[...VOCAL_KEYS].sort());
 for(const file of Object.values(VOCAL_FILES)){
  const data=fs.readFileSync(new URL(`../public/assets/sfx/${file}`,import.meta.url));
  assert.equal(data.toString('ascii',0,4),'RIFF');assert.equal(data.toString('ascii',8,12),'WAVE');
  assert.equal(data.readUInt16LE(22),1);assert.equal(data.readUInt32LE(24),48000);
  assert.ok(data.length>4000&&data.length<240100,file);
 }
});
test('ordinary player avatars, animals, temporary units and unknown identities retain existing sound routing',()=>{
 assert.equal(vocalKey({race:'Goblin',gender:'female',personality_id:'survivor'}),null);
 assert.equal(vocalKey({combat_voice_key:'elf_female_guardian'}),null);
 assert.equal(vocalKey({...unit('human_male_guardian'),temporary:true}),null);
 assert.equal(vocalKey({...unit('goblin_male_guardian'),species_profile:'store_rat'}),null);
 assert.equal(vocalKey({race:'Human',gender:'female',personality_id:'strategist',encounter_profile:'road_cutpurse'}),'human_female_strategist');
 assert.equal(Object.keys(battleVocalFiles(battle)).length,18);
 assert.deepEqual(battleVocalFiles({units:{plain:{race:'Human'}}}),{});
});

test('approved female revisions are installed while male and Human pain/death clips retain their pack',()=>{
 for(const key of VOCAL_KEYS){
  for(const event of ['attack','hurt','death']){
   const expected=key.startsWith('goblin_female_')||(key.startsWith('human_female_')&&event==='attack')?'enemy-vocals-female-v2':'enemy-vocals-v1';
   for(const variant of [1,2,3])assert.equal(VOCAL_FILES[`vocal_${key}_${event}_${variant}`],`${expected}/${key}_${event}_${variant}.wav`);
  }
 }
});
test('misses have attack effort but no hurt vocal; direct hit preserves its weapon impact',()=>{
 const miss=[{type:'melee_attack',attacker_id:'a',target_id:'b',hit:false,attack_packet:1}];
 assert.equal(vocals(miss).length,1);assert.match(vocals(miss)[0].name,/_attack_[123]$/);
 const hit=[{...miss[0],hit:true,melee_style:'slash',impact_surface:'flesh'},
  {type:'combat_feedback',unit_id:'b',kind:'physical',amount:3,attack_packet:1}];
 const cues=combatAudioSchedule(battle,hit).cues;
 assert.ok(cues.some(c=>c.name==='melee_slash_flesh'&&c.delay===185));
 assert.equal(cues.filter(c=>c.name.includes('_hurt_')).length,1);
 assert.equal(cues.find(c=>c.name.includes('_hurt_')).delay,185);
});
test('death is heard at the late killing event, never inferred from final dead state',()=>{
 const b={...battle,units:{...battle.units,b:{...battle.units.b,alive:false,condition:'dead'}}};
 assert.deepEqual(vocals([],b),[]);
 const events=[{type:'melee_attack',attacker_id:'a',target_id:'b',hit:true,attack_packet:1},
  {type:'combat_feedback',unit_id:'b',kind:'physical',amount:2,attack_packet:1},
  {type:'melee_attack',attacker_id:'a',target_id:'b',hit:true,attack_packet:2},
  {type:'combat_feedback',unit_id:'b',kind:'physical',amount:5,attack_packet:2},
  {type:'death_burst',unit_id:'b',attack_packet:2},
  {type:'sound',target_id:'b',attack_packet:2,cues:[{name:'unit_death',offset:350}]}];
 const cues=combatAudioSchedule(b,events).cues,death=cues.filter(c=>c.name.includes('_death_'));
 assert.equal(death.length,1);assert.equal(death[0].delay,impactTimeline(events)[4].start);
 assert.ok(death[0].delay>185);assert.ok(!cues.some(c=>c.name==='unit_death'));
 assert.equal(cues.filter(c=>c.name.includes('_hurt_')).length,1);
});
test('zero damage, buffs, healing and DoT ticks do not produce a hurt chorus',()=>{
 const events=[['physical',0],['heal',5],['burn',3],['poison',3],['bleed',3],['status',3]].map(([kind,amount])=>({type:'combat_feedback',unit_id:'b',kind,amount}));
 assert.deepEqual(vocals(events),[]);
 assert.equal(vocals([{type:'combat_feedback',unit_id:'b',kind:'fire',amount:4}]).length,1);
});
test('ranged attacks and net subdual use the same identity, with unconsciousness using pain rather than death',()=>{
 const events=[{type:'sound',attack_event:true,attacker_id:'a',target_id:'b',attack_packet:1,
  cues:[{name:'bow_release',offset:45},{name:'unit_unconscious',offset:350}]}];
 const cues=combatAudioSchedule(battle,events).cues;
 assert.equal(cues.filter(c=>c.name.includes('_attack_')).length,1);
 assert.equal(cues.filter(c=>c.name.includes('_hurt_')).length,1);
 assert.ok(!cues.some(c=>c.name.includes('_death_')||c.name==='unit_unconscious'));
 assert.equal(cues.find(c=>c.name.includes('_hurt_')).delay,350);
 const net=[{type:'net_cast',attacker_id:'a',target_id:'b',hit:true,attack_packet:2},
  {type:'combat_feedback',unit_id:'b',kind:'resolve',amount:4,attack_packet:2}];
 assert.equal(vocals(net).length,2);
});
test('multi-hit effort and pain are rate-limited, while deaths are never suppressed by that limit',()=>{
 const events=[{type:'melee_attack',attacker_id:'a',target_id:'b',hit:true,attack_packet:1},
  ...[1,2,3].map(attack_packet=>({type:'combat_feedback',unit_id:'b',kind:'physical',amount:3,attack_packet})),
  {type:'death_burst',unit_id:'b',attack_packet:3}];
 const cues=vocals(events);assert.equal(cues.filter(c=>c.name.includes('_hurt_')).length,1);
 assert.equal(cues.filter(c=>c.name.includes('_death_')).length,1);
});
test('variants change over activations without changing the assigned identity',()=>{
 const events=[{type:'melee_attack',attacker_id:'a',target_id:'b',hit:false,attack_packet:1}];
 const names=[1,2,3].map(round=>vocals(events,{...battle,round})[0].name);
 assert.equal(new Set(names).size,3);assert.ok(names.every(n=>n.startsWith('vocal_human_male_guardian_attack_')));
});

test('custom slinger attacks retain their attacker identity even when their visual is anchored to the victim',()=>{
 const cues=vocals([{type:'martial_effect',skill:'specialty_stone',unit_id:'b',attacker_id:'a',attack_event:true,attack_packet:1},
  {type:'combat_feedback',unit_id:'b',kind:'physical',amount:4,attack_packet:1}]);
 assert.equal(cues.filter(c=>c.name.startsWith('vocal_human_male_guardian_attack_')).length,1);
 assert.equal(cues.filter(c=>c.name.startsWith('vocal_goblin_female_survivor_hurt_')).length,1);
});
