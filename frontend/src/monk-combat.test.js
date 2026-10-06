import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {impactTimeline,impactArtwork} from './combat-impact.js';
import {combatAudioSchedule} from './combat-audio.js';
import {comboMarkup} from './martial-ui.js';
import {skillIcon} from './ability-icons.js';
import {statusVisual} from './combat-status-presentation.js';
import {hotbarMarkup,areaForecastMarkup} from './combat-hotbar.js';

test('Monk punches share authored contact markers with damage and audio',()=>{
 const events=[{type:'monk_technique',attack_packet:1,duration:740}];
 for(let i=0;i<3;i++)events.push({type:'melee_attack',attack_packet:i+2,impact_origin_packet:1,impact_offset:i*210+83,contact_ms:83,attack_duration:180,hit:true,melee_style:'fist',impact_surface:'flesh'},
  {type:'combat_feedback',kind:'physical',amount:6,attack_packet:i+2,impact_origin_packet:1,impact_offset:i*210+83});
 const rows=impactTimeline(events);
 assert.deepEqual(rows.filter(r=>r.event.type==='melee_attack').map(r=>r.start),[0,210,420]);
 assert.deepEqual(rows.filter(r=>r.event.type==='combat_feedback').map(r=>r.start),[83,293,503]);
 const hits=combatAudioSchedule({},events).cues.filter(c=>c.name==='melee_fist_flesh');
 assert.deepEqual(hits.map(c=>c.delay),[83,293,503]);
});

test('Enemy actions wait for the final Monk hit and lethal collapse',()=>{
 const events=[{type:'monk_technique',attack_packet:1,duration:740},
  {type:'melee_attack',attack_packet:2,impact_origin_packet:1,impact_offset:503,contact_ms:83,attack_duration:180},
  {type:'death_burst',attack_packet:2,impact_origin_packet:1,impact_offset:503},
  {type:'melee_attack',attack_packet:3}];
 const rows=impactTimeline(events),death=rows[2],enemy=rows[3];
 assert.ok(enemy.start>=death.start+death.duration);
});

test('Combo UI explains stage, next-turn gating and expiry without granting actions',()=>{
 assert.match(comboMarkup({combo:{stage:'follow_up',available:false,turns_remaining:3}}),/Available next personal turn/);
 assert.match(comboMarkup({combo:{stage:'finisher',available:true,turns_remaining:2}}),/Finisher Ready/);
 assert.match(comboMarkup({combo:{stage:'finisher',available:true,turns_remaining:2}}),/2 personal turns remaining/);
 assert.equal(comboMarkup({alive:false,combo:{stage:'finisher'}}),'');
 const skill={id:'job:monk:heaven_piercing',name:'Heaven-Piercing Strike',type:'active',source_kind:'character',range:3,
   availability:{available:false,reason:'Requires Finisher Ready',cooldown_remaining:0}};
 const html=hotbarMarkup({skills:[skill]},0,null,String);
 assert.match(html,/Requires Finisher Ready/);assert.match(html,/unavailable/);
});

test('All eight Monk icons and status artwork resolve to imported assets',()=>{
 for(const key of ['rapid_palm','crushing_fist','iron_reversal','breaking_combination','heaven_piercing','sweeping_dash','perfect_rhythm','flowing_footwork']){
  const url=skillIcon({id:'job:monk:'+key});assert.ok(existsSync(new URL('../public'+url,import.meta.url)),url);
 }
 for(const id of ['iron_reversal','flowing_footwork','open_guard'])assert.match(statusVisual({id}).image,/assets\/monk-v1\//);
 assert.deepEqual(impactArtwork({kind:'physical',monk_skill:'rapid_palm'}),['monk:palm_contact']);
 assert.deepEqual(impactArtwork({kind:'combo'}),[]);
});
