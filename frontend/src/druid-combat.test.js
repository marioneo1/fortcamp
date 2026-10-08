import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {placementCommand,selectRogueCell,rogueSession,resetRoguePlacement} from './rogue-ui.js';
import {impactTimeline} from './combat-impact.js';
import {combatAudioSchedule} from './combat-audio.js';
import {skillIcon} from './ability-icons.js';
import {statusDetails} from './combat-status-ui.js';

test('Bramble requires legal three-cell orientation and explicit confirmation',()=>{
 const id='job:druid:bramble_wall',view={seed:'bramble',current_unit_id:'a',units:{a:{special:{id}}},rogue_previews:{[id]:{kind:'bramble_wall',strips:{'3,3,0':[{x:2,y:3},{x:3,y:3},{x:4,y:3}]}}}};
 const s=rogueSession(view);selectRogueCell(view,s,{x:0,y:0});assert.equal(placementCommand(view,s),null);
 selectRogueCell(view,s,{x:3,y:3});assert.equal(s.phase,'confirm');
 assert.deepEqual(placementCommand(view,s),{action:'skill',skill_id:id,x:3,y:3,rotation:0});
 s.rotation=1;assert.equal(placementCommand(view,s),null);resetRoguePlacement();
});
test('Bramble lash, damage and sound share contact; next attack waits',()=>{
 const events=[{type:'druid_lash',attack_event:true,attack_packet:7},{type:'combat_feedback',attack_packet:7,amount:10},{type:'sound',cues:[{name:'druid_vine_lash',offset:220}],attack_packet:7},{type:'melee_attack',attack_packet:8}];
 const rows=impactTimeline(events);assert.equal(rows[1].start,220);assert.ok(rows[3].start>=500);
 const cues=combatAudioSchedule({},events).cues;assert.equal(cues.find(c=>c.name==='druid_vine_lash').delay,220);
});
test('Druid pool and humanoid return have their own installed icons',()=>{
 for(const key of ['prowler','bulwark','rat','rejuvenation','bramble_wall','living_armor','natures_persistence','wild_instinct'])
  assert.ok(existsSync(new URL('../public'+skillIcon({id:'job:druid:'+key}),import.meta.url)));
 assert.match(skillIcon({id:'job:druid:prowler',form_return:true}),/humanoid\.png$/);
});
test('Persistent forms and regeneration explain their actual clocks',()=>{
 const form=statusDetails({id:'wild_form',name:'Rat',description:'Any HP damage kills.'});
 assert.match(form.details.join(' '),/Until you change form/);assert.ok(!form.details.join(' ').includes('undefined'));
 const armor=statusDetails({id:'living_armor',name:'Living Armor',ticks:4,heal_percent:7,retaliation:true});
 assert.match(armor.description,/25%/);assert.match(armor.details.join(' '),/7%.*4 turn starts/);
});
test('Transformation sound starts with its ring and holds later attacks until completion',()=>{
 const events=[{type:'martial_effect',skill:'druid_prowler',attack_event:true,attack_packet:1},{type:'sound',cues:[{name:'druid_prowler'}],attack_packet:1},{type:'combat_feedback',kind:'form',attack_packet:1},{type:'melee_attack',attack_packet:2}];
 const t=impactTimeline(events);assert.equal(combatAudioSchedule({},events).cues[0].delay,t[0].start);assert.ok(t[3].start>=560);
});
