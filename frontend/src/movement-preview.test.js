import test from 'node:test';
import assert from 'node:assert/strict';
import {previewMovement} from './movement-preview.js';
const battle=()=>({status:'active',current_unit_id:'p',round:1,units:{p:{id:'p',team:'player',x:0,y:0}},movement_tree:[
  {x:0,y:0,cost:0,parent:null},{x:1,y:0,cost:1,parent:[0,0]},
  {x:2,y:0,cost:3,parent:[1,0]},{x:1,y:1,cost:2,parent:[1,0]},
]});
test('immediate preview uses server path/costs without mutating authoritative input',()=>{
  const b=battle(),p=previewMovement(b,{x:2,y:0});
  assert.deepEqual(p.movement_path,[{x:1,y:0,cost:1},{x:2,y:0,cost:3}]);
  assert.equal(p.units.p.x,2);assert.equal(b.units.p.x,0);assert.equal(p.units.p.moved,true);
});
test('redirecting uses displayed position and joins validated branches without cutting corners',()=>{
  const b=battle();b.units.p.x=2;
  const p=previewMovement(b,{x:1,y:1},{x:1.1,y:0});
  assert.deepEqual(p.preview_movement_points,[{x:1,y:0,cost:1},{x:1,y:1,cost:2}]);
  const q=previewMovement(b,{x:1,y:1},{x:2,y:0});
  assert.deepEqual(q.preview_movement_points.map(({x,y})=>[x,y]),[[2,0],[1,0],[1,1]]);
});
test('outside-range, enemy, committed and malformed routes cannot be previewed',()=>{
  const b=battle();assert.equal(previewMovement(b,{x:3,y:0}),null);
  b.units.p.team='enemy';assert.equal(previewMovement(b,{x:1,y:0}),null);
  b.units.p.team='player';b.units.p.acted=true;assert.equal(previewMovement(b,{x:1,y:0}),null);
  b.units.p.acted=false;b.movement_tree[1].parent=[1,0];assert.equal(previewMovement(b,{x:1,y:0}),null);
});
test('moving a carried body previews its position and preserves the original activation origin',()=>{
  const b=battle();b.units.p.carrying='body';b.units.body={x:0,y:0};
  const p=previewMovement(b,{x:1,y:0}),q=previewMovement(p,{x:0,y:0});
  assert.equal(p.units.body.x,1);assert.equal(b.units.body.x,0);
  assert.deepEqual(q.movement_origin,{x:0,y:0});assert.equal(q.units.p.moved,false);
});
