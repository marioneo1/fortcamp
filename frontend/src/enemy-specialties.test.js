import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {skillIcon} from './ability-icons.js';
import {statusVisual} from './combat-status-presentation.js';
import {zoneOverlay} from './combat-spaces-ui.js';

test('all eight specialty icons and nine physical sounds are installed',()=>{
 for(const kind of ['tripline','shakedown','parting_cut','ankle_bite','goliath_shot','tag_team','cornered_fury','heel_cut']){
  const icon=skillIcon({id:'npc:bandit:'+kind});assert.match(icon,/enemy-specialties-v1/);
  assert.ok(existsSync(new URL('../public'+icon,import.meta.url)));
 }
 for(const kind of ['tripline_set','tripline_snap','shakedown','parting_cut','ankle_bite','goliath_shot','tag_team','heel_cut','cornered_fury']){
  const bytes=readFileSync(new URL('../public/assets/sfx/specialty_'+kind+'.wav',import.meta.url));
  assert.equal(bytes.toString('ascii',0,4),'RIFF');assert.equal(bytes.toString('ascii',8,12),'WAVE');assert.ok(bytes.length>1000);
 }
});
test('specialty status art resolves actual NPC ids rather than fictitious job ids',()=>{
 for(const id of ['sword_exposed','heel_wound','tag_team_power'])assert.match(statusVisual({id,turns:1}).image,/enemy-specialties-v1/);
 assert.equal(statusVisual({id:'intimidated',turns:1}).kind,'debuff');
 assert.equal(statusVisual({id:'feigned_death'}).kind,'buff');
});
test('tripline renders one continuous rope with two endpoints and no extra outline',()=>{
 const base={id:'trip',name:'Tripline',kind:'tripline',remaining:3,owner_name:'QA',description:'First crossing snaps.'};
 const horizontal=zoneOverlay([{...base,cells:[{x:2,y:3},{x:3,y:3},{x:4,y:3}]}],String);
 assert.equal((horizontal.match(/tripline_prop/g)||[]).length,1);
 assert.match(horizontal,/width="268" height="64"/);
 assert.match(horizontal,/clipPath id="tripline-strip-trip"/);
 assert.doesNotMatch(horizontal,/class="zone-boundary"/);
 const vertical=zoneOverlay([{...base,cells:[{x:2,y:3},{x:2,y:4},{x:2,y:5}]}],String);
 assert.match(vertical,/rotate\(90/);
 assert.equal((vertical.match(/tripline_prop/g)||[]).length,1);
});
