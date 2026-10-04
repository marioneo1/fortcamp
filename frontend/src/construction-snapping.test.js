import test from 'node:test';
import assert from 'node:assert/strict';
import {snapWall,rotateSnappedWall,wallContacts} from './construction-snapping.js';
import {placementError,wallSegments} from './construction-geometry.js';
const size={w:12,h:10};
const wall=(extra={})=>({id:'preview',x:4,y:4,piece:'corner_north_west',shape:'corner',anchor:'center',rotation:0,material:'timber',...extra});

test('corner automatically connects to the end of a top-edge horizontal row',()=>{
 const plan={props:[],walls:[wall({id:'row',x:3,piece:'horizontal_plain',shape:'straight',anchor:'north'})]};
 const result=snapWall(wall({anchor:'south'}),plan,size);
 assert.ok(result.snapped);assert.ok(result.contacts.some(([x,y])=>x===4&&y===4));
 assert.equal(placementError(result.item,'walls',size,plan),'');
});

test('snapping finds reflected corners, stays local and does not create overlaps',()=>{
 const plan={props:[],walls:[wall({id:'row',x:4,piece:'horizontal_plain',shape:'straight',anchor:'north'})]};
 const result=snapWall(wall({x:3}),plan,size);
 assert.ok(result.snapped);assert.equal(result.item.piece,'corner_north_east');
 assert.ok(result.contacts.some(([x,y])=>x===4&&y===4));
 assert.equal(placementError(result.item,'walls',size,plan),'');
 assert.ok(!snapWall(wall({x:9,y:8}),plan,size).snapped);
});

test('R retains a snapped connection, skips duplicate spans and never quarter-turns artwork',()=>{
 const plan={props:[],walls:[wall({id:'row',x:3,piece:'horizontal_plain',shape:'straight',anchor:'north'})]};
 let current=snapWall(wall(),plan,size).item;
 const first=wallContacts(current,plan)[0];
 for(let i=0;i<4;i++){
  const next=rotateSnappedWall(current,plan,size);
  assert.ok(next.snapped);assert.ok(next.contacts.some(p=>p.join(',')===first.join(',')));
  assert.equal(placementError(next.item,'walls',size,plan),'');assert.equal(next.item.rotation,0);current=next.item;
 }
});

test('geometry snapping is independent of wall material and never changes the saved draft',()=>{
 const plan={props:[],walls:[wall({id:'row',x:3,piece:'horizontal_plain',shape:'straight',anchor:'north'})]},before=structuredClone(plan);
 const base=snapWall(wall(),plan,size);
 for(const material of ['timber','fieldstone','limestone','iron']){
  const next=snapWall(wall({material}),plan,size);
  assert.deepEqual(wallSegments(next.item),wallSegments(base.item));assert.equal(next.item.material,material);
 }
 assert.deepEqual(plan,before);
});

test('straight brushes stay in their chosen family until R and props can invalidate a proposed join',()=>{
 const item=wall({x:3,piece:'horizontal_plain',shape:'straight',anchor:'north'});
 const plan={props:[],walls:[{...item,id:'placed'}]};
 assert.ok(!snapWall(item,plan,size).snapped);
 plan.props=[{id:'crate',x:4,y:4,w:1,h:1,offset_x:0,offset_y:0}];
 const result=snapWall(wall(),plan,size);
 if(result.snapped)assert.equal(placementError(result.item,'walls',size,plan),'');
});

test('a corner joining two fixed runs cannot rotate away from either connection',()=>{
 const item=wall(),plan={props:[],walls:[wall({id:'right',x:5,piece:'horizontal_plain',shape:'straight',anchor:'north'}),wall({id:'below',y:5,piece:'vertical_plain',shape:'straight',anchor:'west'})]};
 assert.equal(wallContacts(item,plan).length,2);
 const next=rotateSnappedWall(item,plan,size);
 assert.equal(placementError(next.item,'walls',size,plan),'');
 assert.ok(next.contacts.some(p=>p.join(',')==='5,4'));
 assert.ok(next.contacts.some(p=>p.join(',')==='4,5'));
});
