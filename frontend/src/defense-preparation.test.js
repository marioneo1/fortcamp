import test from 'node:test';
import assert from 'node:assert/strict';
import {preparationCells,preparationPreview} from './defense-preparation.js';

const battle={units:{enemy:{team:'enemy',x:7,y:3,alive:true}},preparation:{zone:Array.from({length:9},(_,n)=>({x:4+n%3,y:2+Math.floor(n/3)})),placements:[]}};
test('caltrop footprints rotate and must fit wholly inside preparation zone',()=>{
 const option={deploy_kind:'caltrops'};
 assert.deepEqual(preparationCells(option,5,3,true),[{x:5,y:2},{x:5,y:3},{x:5,y:4}]);
 assert.equal(preparationPreview(battle,option,5,3).valid,true);
 assert.equal(preparationPreview(battle,option,4,3).valid,false);
});
test('armed explosive preview includes trigger radius and refuses enemy contact',()=>{
 const p=preparationPreview(battle,{id:'proximity_dynamite'},6,3);
 assert.equal(p.area.length,9);assert.equal(p.valid,false);
 assert.equal(preparationPreview(battle,{deploy_kind:'proximity_charge'},4,3).valid,true);
});
test('occupied preparation cells cannot be reused and preview is read-only',()=>{
 const b=structuredClone(battle);b.preparation.placements.push({cells:[{x:5,y:3}]});
 const saved=structuredClone(b);
 assert.equal(preparationPreview(b,{id:'pit'},5,3).valid,false);
 assert.deepEqual(b,saved);
});
