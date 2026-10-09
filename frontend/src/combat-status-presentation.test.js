import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {visibleStatuses,statusVisual,mapStatusMarkup,statusTrayMarkup,statusListMarkup,statusInspectMarkup,statusCardNotes,stunMarkup,stunOnsets} from './combat-status-presentation.js';
import {impactArtwork} from './combat-impact.js';
const esc=s=>String(s??'').replaceAll('<','&lt;').replaceAll('"','&quot;');

test('Cleric regeneration shows remaining healing ticks with its new matching icon',()=>{
 const visual=statusVisual({id:'cleric_regeneration',ticks:2,healing:6});
 assert.equal(visual.count,2);assert.match(visual.image,/cleric-v1\/sanctuary.png/);
});
const defs={stun:{name:'Stun',description:'Cannot act during the next activation.'},poison:{name:'Poison',description:'Takes damage each activation.'},rally_power:{name:'Attack boost',description:'Next attack +25%.'}};
test('effects tray stays available to position even with no active effects',()=>{
 const tray=statusTrayMarkup({id:'a',statuses:[]},defs,esc);
 assert.match(tray,/No active effects/);assert.match(tray,/data-all-effects/);
});
test('effects dock provides wrapping icons while the popup retains every effect',()=>{
 const unit={id:'a',statuses:['poison','burn','bleed','blind','stun','slow','wet','fear'].map(id=>({id,turns:2}))};
 const tray=statusTrayMarkup(unit,defs,esc);
 assert.equal((tray.match(/data-unit-status=/g)||[]).length,8);
 assert.match(tray,/status-tray-icons/);
 assert.equal((statusListMarkup(unit,defs,esc,{cards:true}).match(/data-effect-id=/g)||[]).length,8);
});
test('control takes priority, guard is visible and same effect is not duplicated',()=>{
 const unit={guarding:true,statuses:[{id:'poison',turns:2},{id:'stun',turns:1},{id:'poison',turns:2}]};
 assert.deepEqual(visibleStatuses(unit).map(s=>s.id),['stun','poison','guard']);
 assert.deepEqual(visibleStatuses({...unit,alive:false}),[]);
 assert.deepEqual(visibleStatuses({...unit,conscious:false}),[]);
});
test('different owners of a Mark remain separate and counts keep their meaning',()=>{
 assert.equal(visibleStatuses({statuses:[{id:'mark',source_id:'a'},{id:'mark',source_id:'b'}]}).length,2);
 assert.equal(statusVisual({id:'barrier',amount:12,turns:1}).count,12);
 assert.equal(statusVisual({id:'rally_power'}).count,'1×');
 assert.equal(statusVisual({id:'poison',turns:2}).count,2);
});
test('supported effects reuse installed painted artwork',()=>{
 for(const id of ['stun','sleep','freeze','poison','burn','bleed','charm','confuse','berserk','blind','bind','slow','paralyze','mute','fear','barrier','braced','rally_power','rally_protection','wild_form']){
  const visual=statusVisual({id});assert.ok(visual.image,id);
  assert.ok(existsSync(new URL('../public'+visual.image,import.meta.url)),id);
 }
});
test('Bard song statuses use the extracted Bard artwork',()=>{
 for(const id of ['bard_accelerando','bard_quickening','bard_war_anthem','bard_song_peace','bard_jeering','bard_jeer_vulnerable']){
  const visual=statusVisual({id});
  assert.ok(visual.image,id);
  assert.ok(existsSync(new URL('../public'+visual.image,import.meta.url)),id);
 }
});
test('map, tray and inspection retain every effect and its description',()=>{
 const unit={id:'a',statuses:[{id:'poison',turns:2},{id:'stun',turns:1},{id:'rally_power'}]};
 const map=mapStatusMarkup(unit,defs,esc);assert.equal((map.match(/data-unit-status=/g)||[]).length,3);assert.doesNotMatch(map,/status-overflow/);
 const tray=statusTrayMarkup(unit,defs,esc);assert.match(tray,/buffs, debuffs/);assert.match(tray,/All effects/);assert.equal((tray.match(/data-unit-status=/g)||[]).length,3);
 const list=statusListMarkup(unit,defs,esc);assert.match(list,/Cannot act/);assert.match(list,/Next attack \+25%/);assert.match(list,/one stack expires after each tick/);
 assert.equal(mapStatusMarkup({...unit,alive:false},defs,esc),'');
});

test('cards use precise remaining clocks while badge hover retains the full explanation',()=>{
 assert.deepEqual(statusCardNotes({id:'poison',stacks:5}),['5 turns remaining; one stack expires after each tick']);
 assert.deepEqual(statusCardNotes({id:'living_armor',ticks:3}),['3 healing ticks remaining at turn start']);
 assert.match(statusCardNotes({id:'bard_song_peace',turns:1}).join(' '),/Only while inside/);
 assert.doesNotMatch(statusCardNotes({id:'bard_song_peace',turns:1}).join(' '),/turns remaining/);
 const status={id:'poison',stacks:5},unit={id:'a',name:'Enemy',statuses:[status]};
 const full=statusInspectMarkup(unit,status,defs,esc);assert.match(full,/before damage modifiers/);assert.match(full,/Right-click to keep this effect open/);
 const cards=statusListMarkup(unit,defs,esc,{cards:true});assert.match(cards,/data-effect-id="poison"/);assert.match(cards,/5 turns remaining/);assert.doesNotMatch(cards,/turns \/ stacks/);
});
test('stun uses a persistent orbit rather than binding art, and clears on recovery or defeat',()=>{
 const unit={statuses:[{id:'stun',turns:1}]};assert.match(stunMarkup(unit),/unit-stun-effect/);assert.equal((stunMarkup(unit).match(/class="stun-star"/g)||[]).length,3);
 assert.equal(stunMarkup({statuses:[]}), '');assert.equal(stunMarkup({...unit,conscious:false}), '');
 assert.deepEqual(impactArtwork({kind:'status',status_id:'stun'}),[]);
 assert.deepEqual(impactArtwork({kind:'poison'}),['poison_cloud']);
});

test('new Stun orbit waits for the actual collision status contact',()=>{
 const events=[{type:'melee_attack',attack_packet:1},{type:'movement',unit_id:'a',attack_packet:1,forced:true,collision:true,points:[{x:0,y:0},{x:1,y:0}]},{type:'combat_feedback',unit_id:'a',kind:'status',status_id:'stun',attack_packet:1,after_displacement:true}];
 assert.ok(stunOnsets(events).get('a')>185);
 assert.equal(stunOnsets([]).size,0);
 assert.match(stunMarkup({statuses:[{id:'stun'}]},250),/--stun-onset:250ms/);
});

test('innate resistances share one buff, including knockback and control duration',()=>{
 const unit={alive:true,statuses:[{id:'innate_resistance',statuses:{stun:25,poison:100,burn:50},knockback:25,control_duration_limit:1}]};
 const html=statusListMarkup(unit,{},esc);assert.match(html,/Buffs/);assert.match(html,/Push \/ pull: 25%/);assert.match(html,/stun: 25%/);assert.match(html,/poison: immune/);assert.match(html,/Burn still applies/);assert.match(html,/at most 1 target turn/);assert.doesNotMatch(html,/Resistances &amp; recovery/);
 assert.equal(visibleStatuses(unit).length,1);assert.equal(statusVisual(unit.statuses[0]).kind,'buff');
});
