import test from 'node:test';
import assert from 'node:assert/strict';
import {rectangleCells,wallRun,wallRunError} from './construction-strokes.js';
import {wallSegments} from './construction-geometry.js';
const wall=(extra={})=>({id:'preview',x:4,y:4,piece:'horizontal_plain',shape:'straight',anchor:'north',material:'timber',rotation:0,posts:'none',...extra});
const empty=()=>({ground:{},walls:[],props:[]}),size={w:12,h:10};

test('diagonal floor drag fills the rectangle including untouched cells and works backwards',()=>{
 const cells=rectangleCells({x:1,y:1},{x:2,y:2});
 assert.deepEqual(cells,[{x:1,y:1},{x:2,y:1},{x:1,y:2},{x:2,y:2}]);
 assert.deepEqual(rectangleCells({x:2,y:2},{x:1,y:1}),cells);
 assert.equal(rectangleCells({x:3,y:3},{x:3,y:3}).length,1);
 // Recompute from current corners: shrinking must not leave old stroke cells behind.
 assert.equal(rectangleCells({x:1,y:1},{x:1,y:2}).length,2);
});

test('wall drags choose a single row or column, not a rectangular fill',()=>{
 const row=wallRun(wall(),3,2);assert.equal(row.length,4);assert.ok(row.every(w=>w.y===4));
 const col=wallRun(wall(),1,-3);assert.equal(col.length,4);assert.ok(col.every(w=>w.x===4));
 assert.ok(col.every(w=>w.piece.startsWith('vertical')));
 assert.equal(wallRunError(row,empty(),size),'');assert.equal(wallRunError(col,empty(),size),'');
});

test('repeating offset wall pieces preserves exact spans and facing without gaps',()=>{
 for(const anchor of ['north','center','east','west','south']){
  const items=wallRun(wall({anchor,piece:'horizontal_right_post_south',material:'iron'}),2,0);
  assert.equal(wallRunError(items,empty(),size),'');
  for(let i=1;i<items.length;i++){
   assert.equal(items[i].piece,'horizontal_right_post_south');assert.equal(items[i].material,'iron');
   assert.deepEqual(wallSegments(items[i-1])[0][1],wallSegments(items[i])[0][0]);
  }
 }
});

test('a corner appears once and extends through matching plain arms in either direction',()=>{
 for(const piece of ['corner_north_west','corner_north_east','corner_south_west','corner_south_east'])for(const [dx,dy] of [[2,0],[-2,0],[0,2],[0,-2]]){
  const seed=wall({piece,shape:'corner',anchor:'center'}),items=wallRun(seed,dx,dy);
  assert.equal(items.filter(w=>w.shape==='corner').length,1);assert.equal(items.length,3);
  assert.equal(wallRunError(items,empty(),size),'');
  const ends=wallSegments(items[0]).flat().map(p=>p.join(','));
  assert.ok(wallSegments(items[1])[0].some(p=>ends.includes(p.join(','))));
 }
});

test('invalid wall runs reject the whole batch without modifying the source draft',()=>{
 const plan=empty();plan.walls=[wall({id:'existing',x:6})];const before=structuredClone(plan);
 assert.match(wallRunError(wallRun(wall(),3,0),plan,size),/already occupies/);
 assert.deepEqual(plan,before);
 assert.match(wallRunError(wallRun(wall({x:0,anchor:'center'}),-2,0),empty(),size),/outside/);
});
