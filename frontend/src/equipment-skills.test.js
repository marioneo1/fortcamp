import {test} from 'node:test';
import assert from 'node:assert/strict';
import {selectBattleSkill,skillPicker,skillAvailability,skillTiming} from './equipment-skills.js';
import {describeGear} from './equipment-ui.js';

test('switching to support exposes self and allies missing from offensive target list',()=>{
 const wall={id:'wall',target:'enemy'},heal={id:'heal',target:'ally'};
 const b={current_unit_id:'p',units:{p:{id:'p',skills:[wall,heal],special:wall}},attack_previews:{e:{attack:{chance:90}}},skill_previews:{heal:{p:{support:true,chance:100},ally:{support:true,chance:100}}}};
 const v=selectBattleSkill(b,'heal');assert.equal(v.attack_previews.p.skill.support,true);assert.equal(v.attack_previews.ally.skill.support,true);
 assert.equal(v.attack_previews.e.skill,null);assert.equal(v.attack_previews.e.attack.chance,90);assert.equal(b.attack_previews.p,undefined);
});

test('skill selection substitutes authoritative range previews without changing server view',()=>{
 const first={id:'blade',name:'Blade'},second={id:'lance',name:'Lance',source_name:'Projector'};
 const b={current_unit_id:'p',units:{p:{id:'p',skills:[first,second],special:first}},attack_previews:{e:{attack:{range:1},skill:{range:1}}},skill_previews:{lance:{e:{range:5}}}};
 const v=selectBattleSkill(b,'lance');assert.equal(v.units.p.special,second);assert.equal(v.attack_previews.e.skill.range,5);assert.equal(b.units.p.special,first);assert.equal(b.attack_previews.e.skill.range,1);
 assert.equal(selectBattleSkill(b,'missing').units.p.special,first);
 const html=skillPicker({...v.units.p,special_used:true},s=>s.replaceAll('<','&lt;'));
 assert.match(html,/disabled/);assert.match(html,/Projector/);assert.match(html,/share one use/);
});
test('techniques can be selected independently while another is cooling down',()=>{
 const shot={id:'shot',name:'Shot',ability_version:1,availability:{available:false,cooldown_remaining:2,uses_remaining:null}};
 const lance={id:'lance',name:'Lance',ability_version:1,availability:{available:true,cooldown_remaining:0,uses_remaining:1}};
 const actor={skills:[shot,lance],special:shot,special_used:true,acted:false};
 assert.equal(skillAvailability(actor).available,false);
 assert.equal(skillAvailability(actor,lance).available,true);
 assert.equal(skillTiming(shot),'Ready in 2 turns');
 assert.equal(skillTiming(lance),'1 use left');
 const html=skillPicker(actor,s=>s);
 assert.doesNotMatch(html,/disabled/);assert.match(html,/own cooldown/);assert.match(html,/Ready in 2 turns/);
 assert.equal(skillAvailability({...actor,acted:true},lance).available,false);
 assert.match(skillPicker({...actor,acted:true},s=>s),/disabled/);
});
test('resistance descriptions only advertise the statuses actually resisted',()=>{
 const fire=describeGear({combat_rules:{resistances:['fire','burn']}},{}).join(' ');
 assert.match(fire,/Burn proc chance halved/);assert.doesNotMatch(fire,/Poison procs blocked/);
 const poison=describeGear({combat_rules:{resistances:['poison']}},{}).join(' ');
 assert.match(poison,/Poison procs blocked/);assert.doesNotMatch(poison,/Burn proc chance halved/);
});

test('character and all gear abilities remain accessible alongside passive descriptions',()=>{
 const skills=Array.from({length:8},(_,i)=>({id:`s${i}`,name:`Skill ${i}`,ability_version:1,source_kind:i<3?'character':'equipment'}));
 const html=skillPicker({skills,passives:[{name:'Footwork',description:'Gain 5 evasion.'}]},s=>s);
 assert.equal((html.match(/<option /g)||[]).length,8);
 assert.match(html,/Character skills/);assert.match(html,/Equipment and proficiency/);
 assert.match(html,/Gain 5 evasion/);
});
