import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {frozenMarkup,frozenTransitionPlan,scorchedArtwork,surfaceSeed} from './mage-surfaces.js';
const frozen={id:'test',alive:true,statuses:[{id:'freeze',elemental_freeze:true}]};
test('Frozen overlays the portrait surface, leaves identity untouched and chooses stable art',()=>{
 const before=structuredClone(frozen),markup=frozenMarkup(frozen);assert.match(markup,/ice-surface/);assert.match(markup,/mage-frozen-v2\/frozen_/);assert.equal(markup,frozenMarkup(frozen));assert.deepEqual(frozen,before);assert.equal(frozenMarkup({...frozen,alive:false}),'');assert.equal(frozenMarkup({...frozen,statuses:[{id:'freeze'}]}),'');
});
test('Freeze onset and shatter follow real contact; poison expiry melts instead',()=>{
 const normal={id:'test',statuses:[]},view=u=>({units:{test:u}});
 assert.deepEqual(frozenTransitionPlan(view(normal),view(frozen),[{start:240,event:{type:'combat_feedback',unit_id:'test',kind:'status',status_id:'freeze'}}]),[{id:'test',mode:'freeze',delay:240}]);
 assert.deepEqual(frozenTransitionPlan(view(frozen),view(normal),[{start:350,event:{type:'combat_feedback',unit_id:'test',kind:'physical',amount:8}}]),[{id:'test',mode:'break',delay:350}]);
 assert.equal(frozenTransitionPlan(view(frozen),view(normal),[{start:20,event:{type:'combat_feedback',unit_id:'test',kind:'poison',amount:8}}])[0].mode,'thaw');
 assert.deepEqual(frozenTransitionPlan(view(frozen),view(frozen),[]),[]);
});
test('Scorched material joins cells with one soft region mask and sparse flames',()=>{
 const z={id:'region',cells:Array.from({length:25},(_,i)=>({x:i%5,y:Math.floor(i/5)}))};
 const html=scorchedArtwork(z,0,0,5,5,'test');assert.equal(html,scorchedArtwork(z,0,0,5,5,'test'));assert.match(html,/feGaussianBlur/);assert.equal((html.match(/<mask /g)||[]).length,1);assert.ok((html.match(/class="scorch-flame"/g)||[]).length<z.cells.length/2);assert.doesNotMatch(html,/fire_contact|scorched_tile/);assert.ok(surfaceSeed('a')!==surfaceSeed('b'));
});
test('Both complete surface packs and the aligned flame strip exist',()=>{
 for(const kind of ['freeze','frozen','break','thaw'])for(let i=1;i<=4;i++)assert.ok(existsSync(new URL(`../public/assets/mage-frozen-v2/${kind}_${i}.png`,import.meta.url)));
 for(const kind of ['soot','ash','flame'])for(let i=1;i<=4;i++)assert.ok(existsSync(new URL(`../public/assets/mage-scorched-v2/${kind}_${i}.png`,import.meta.url)));
 for(const file of ['ember_1','ember_2','smoke_1','smoke_2','flame_strip'])assert.ok(existsSync(new URL(`../public/assets/mage-scorched-v2/${file}.png`,import.meta.url)));
 const css=readFileSync(new URL('./mage-surfaces.css',import.meta.url),'utf8');assert.match(css,/prefers-reduced-motion/);assert.match(css,/steps\(1,end\)/);
});
