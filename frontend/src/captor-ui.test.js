import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {skillIcon} from './ability-icons.js';
import {unitInspectMarkup} from './combat-hotbar.js';
import {feedbackStyles,impactArtwork} from './combat-impact.js';
import {statusVisual} from './combat-status-presentation.js';
const escape=x=>String(x??'');
test('All Captor loadout icons use the generated family',()=>{
 for(const key of ['subduing_blow','bola','hook_and_drag','abduct','restraining_hold','blitz','restraint','clean_capture'])assert.ok(existsSync(new URL('../public'+skillIcon({id:'job:captor:'+key}),import.meta.url)));
});
test('Captor forecast separates Resolve from lethal HP and names isolation and capture odds',()=>{
 const html=unitInspectMarkup({id:'e',name:'Prisoner',hp:50,max_hp:50,resolve:20,max_resolve:50,statuses:[],passives:[]},{},escape,{capture:true,chance:90,hit_chance:90,capture_chance:2,resolve_damage:15,isolated:true});
 assert.match(html,/15 Resolve damage/);assert.match(html,/Isolated/);assert.match(html,/2% capture when ready/);assert.doesNotMatch(html,/15 HP damage/);
});
test('Resolve has distinct feedback and Captor states use readable matching icons',()=>{
 assert.equal(feedbackStyles.resolve.label,'Resolve');assert.deepEqual(impactArtwork({kind:'resolve'}),[]);
 for(const id of ['disarm','captor_held','captor_holding','captor_blitz','captor_abducted'])assert.match(statusVisual({id},{}).image,/captor-v1/);
});
test('Attack and Subdue are separate commands with their own keys',()=>{
 const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');assert.match(source,/data-combat-mode="subdue"/);assert.match(source,/<kbd>N<\/kbd> Subdue/);assert.match(source,/a:'\[data-combat-mode="attack"\]'/);
});
