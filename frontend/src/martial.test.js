import test from 'node:test';
import assert from 'node:assert/strict';
import {furyMarkup} from './martial-ui.js';
import {MARTIAL_ICON_ART,skillIcon,skillCategory} from './ability-icons.js';
import {combatAudioSchedule} from './combat-audio.js';
import {impactTimeline} from './combat-impact.js';
import {martialAuraMarkup} from './martial-effects.js';
import {fighterEffectMarkup} from './fighter-effects.js';

test('Fury clamps five visible segments and stays exclusive to conscious Barbarians',()=>{
 const html=furyMarkup({fury:3,fury_cap:5});
 assert.equal((html.match(/<i class=/g)||[]).length,5);
 assert.equal((html.match(/class="filled"/g)||[]).length,3);
 assert.match(furyMarkup({fury:20,fury_cap:5}),/Fury 5 of 5/);
 for(const unit of [{fury_cap:0},{fury_cap:5,alive:false},{fury_cap:5,conscious:false}])assert.equal(furyMarkup(unit),'');
});
test('All eleven martial abilities use dedicated painted square icons',()=>{
 assert.equal(Object.keys(MARTIAL_ICON_ART).length,11);
 for(const [id,file] of Object.entries(MARTIAL_ICON_ART))assert.equal(skillIcon({id}),file);
 assert.equal(skillCategory({self_only:true,effects:[{type:'area_attack'}]}),'damage');
 assert.equal(skillCategory({self_only:true,effects:[{type:'status'}]}),'self');
});
test('Martial contact effects and sounds share weapon contact; enemy waits for their completion',()=>{
 const events=[{type:'melee_attack',attack_packet:1,hit:true,melee_style:'slash',impact_surface:'flesh'},
 {type:'martial_effect',attack_packet:1,skill:'skullbreaker'},
 {type:'movement',unit_id:'enemy',points:[{x:1,y:0},{x:2,y:0}]}];
 const rows=impactTimeline(events),cues=combatAudioSchedule({},events).cues;
 const weapon=cues.find(c=>c.name==='melee_slash_flesh'),skill=cues.find(c=>c.name==='barbarian_skullbreaker');
 assert.equal(weapon.delay,skill.delay);
 assert.ok(rows[2].start>=rows[1].start+rows[1].duration);
});
test('Groundbreaker has its own physical sound and four alpha phases; no Earthbreaker launch',()=>{
 const events=[{type:'ground_impact',attack_packet:1,effect_art:'groundbreaker'},
 {type:'sound',attack_packet:1,cues:[{name:'barbarian_groundbreaker'}]}];
 assert.deepEqual(combatAudioSchedule({},events).cues.map(c=>c.name),['barbarian_groundbreaker']);
 const html=fighterEffectMarkup({...events[0],x:2,y:2},{width:8,height:8});
 assert.equal((html.match(/ground-phase/g)||[]).length,4);
 assert.doesNotMatch(html,/earth-impact|<i>/);
});
test('Self protection and restoration use physical cues, and auras disappear after death',()=>{
 const cues=combatAudioSchedule({},[{type:'martial_effect',skill:'brace'},{type:'martial_effect',skill:'second_wind'}]).cues;
 assert.deepEqual(cues.map(c=>c.name),['martial_brace','martial_second_wind']);
 assert.match(martialAuraMarkup({statuses:[{id:'brace_defense'}]}),/protection-3/);
 assert.equal(martialAuraMarkup({alive:false,statuses:[{id:'brace_defense'}]}),'');
});
