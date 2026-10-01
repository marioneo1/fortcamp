import {test} from 'node:test';
import assert from 'node:assert/strict';
import {selectBattleSkill,skillPicker} from './equipment-skills.js';
import {describeGear} from './equipment-ui.js';

test('skill selection substitutes authoritative range previews without changing server view',()=>{
 const first={id:'blade',name:'Blade'},second={id:'lance',name:'Lance',source_name:'Projector'};
 const b={current_unit_id:'p',units:{p:{id:'p',skills:[first,second],special:first}},attack_previews:{e:{attack:{range:1},skill:{range:1}}},skill_previews:{lance:{e:{range:5}}}};
 const v=selectBattleSkill(b,'lance');assert.equal(v.units.p.special,second);assert.equal(v.attack_previews.e.skill.range,5);assert.equal(b.units.p.special,first);assert.equal(b.attack_previews.e.skill.range,1);
 assert.equal(selectBattleSkill(b,'missing').units.p.special,first);
 const html=skillPicker({...v.units.p,special_used:true},s=>s.replaceAll('<','&lt;'));
 assert.match(html,/disabled/);assert.match(html,/Projector/);assert.match(html,/share one use/);
});
test('resistance descriptions only advertise the statuses actually resisted',()=>{
 const fire=describeGear({combat_rules:{resistances:['fire','burn']}},{}).join(' ');
 assert.match(fire,/Burn proc chance halved/);assert.doesNotMatch(fire,/Poison procs blocked/);
 const poison=describeGear({combat_rules:{resistances:['poison']}},{}).join(' ');
 assert.match(poison,/Poison procs blocked/);assert.doesNotMatch(poison,/Burn proc chance halved/);
});
