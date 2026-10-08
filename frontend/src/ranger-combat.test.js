import {test} from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {skillIcon,skillCategory} from './ability-icons.js';
import {statusDetails,tacticalPreviewText} from './combat-status-ui.js';
import {statusVisual,visibleStatuses} from './combat-status-presentation.js';
import {impactTimeline,feedbackText} from './combat-impact.js';

test('All eight Ranger skills use matching art with readable tactical categories',()=>{
 for(const key of ['mark_quarry','longshot','multi_shot','rapid_fire','poison_attack','pestilence_shot','rupturing_blow','sharpshooter']){
  const path=skillIcon({id:'job:ranger:'+key});assert.ok(existsSync(new URL('../public'+path,import.meta.url)));
 }
 assert.equal(skillCategory({ranger_kind:'poison_attack'}),'dot');
 assert.equal(skillCategory({ranger_kind:'rapid_fire'}),'self');
});
test('Owner marks and Poison layers are explicit with one-stack turn-end decay',()=>{
 const marks=['Alice','Bob'].map(name=>({id:'mark',quarry:true,source_id:name,source_name:name,turns:3}));
 assert.equal(visibleStatuses({statuses:marks}).length,2);
 assert.match(statusDetails(marks[0]).description,/guaranteed accuracy/);
 assert.match(statusDetails(marks[0]).details.join(' '),/Alice.*3 target turns/);
 const poison=statusDetails({id:'poison',turns:2,layers:[{tick_damage:2},{tick_damage:1}]});
 assert.match(poison.description,/10% max HP at turn end/);assert.match(poison.details.join(' '),/2 turns remaining/);
 for(const id of ['pestilence','poison_imbue','sharpshooter'])assert.ok(statusVisual({id}).image.includes('/ranger-v1/'));
});
test('Ranger forecasts explain variable arrows, crits, cashout and Rapid Fire',()=>{
 const text=tacticalPreviewText({hit_count:'2-4',damage_on_hit:20,damage_max:40,crit_chance:20,crit_damage:60,dot_cashout:12,rapid_pool:['Multi-Shot','Basic Attack']});
 for(const part of ['2-4 hits','20 to 40','20% critical','12 base Poison/Bleed','Multi-Shot / Basic Attack'])assert.ok(text.includes(part));
 assert.equal(feedbackText({kind:'physical',amount:40,critical:true}).label,'Critical');
 assert.equal(feedbackText({kind:'rupture',amount:12}).label,'Rupture');
});
test('Volley arrow contacts serialize before the next enemy starts',()=>{
 const events=[];
 for(let i=1;i<=4;i++)events.push({type:'sound',attack_event:true,ranger_skill:'multi_shot',attack_packet:i,duration:490},{type:'combat_feedback',attack_packet:i,kind:'physical',amount:15});
 events.push({type:'movement',unit_id:'enemy',points:[{x:0,y:0},{x:1,y:0}]});
 const t=impactTimeline(events);for(let i=0;i<4;i++)assert.equal(t[i*2+1].start,i*490+220);
 assert.ok(t.at(-1).start>=1960);
});
