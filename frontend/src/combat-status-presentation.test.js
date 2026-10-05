import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {visibleStatuses,statusVisual,mapStatusMarkup,statusTrayMarkup,statusListMarkup,stunMarkup,stunOnsets} from './combat-status-presentation.js';
import {impactArtwork} from './combat-impact.js';
const esc=s=>String(s??'').replaceAll('<','&lt;').replaceAll('"','&quot;');
const defs={stun:{name:'Stun',description:'Cannot act during the next activation.'},poison:{name:'Poison',description:'Takes damage each activation.'},rally_power:{name:'Attack boost',description:'Next attack +25%.'}};
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
test('map limits clutter but tray and inspection retain every effect and its description',()=>{
 const unit={id:'a',statuses:[{id:'poison',turns:2},{id:'stun',turns:1},{id:'rally_power'}]};
 const map=mapStatusMarkup(unit,defs,esc);assert.equal((map.match(/data-unit-status=/g)||[]).length,2);assert.match(map,/\+1/);
 const tray=statusTrayMarkup(unit,defs,esc);assert.match(tray,/Buffs/);assert.match(tray,/Debuffs/);assert.equal((tray.match(/data-unit-status=/g)||[]).length,3);
 const list=statusListMarkup(unit,defs,esc);assert.match(list,/Cannot act/);assert.match(list,/Next attack \+25%/);assert.match(list,/2 activations/);
 assert.equal(mapStatusMarkup({...unit,alive:false},defs,esc),'');
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
