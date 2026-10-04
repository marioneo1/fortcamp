import test from 'node:test';
import assert from 'node:assert/strict';
import {propsOverlap,propBounds,placementError} from './construction-geometry.js';
import {snapSeat} from './construction-prop-snapping.js';
import {constructionSVG} from './construction-render.js';
const crate={id:'one',asset:'crate_closed',x:2,y:2,w:1,h:1,rotation:0,offset_x:-.4};
const table={id:'table',asset:'horticulture_round_table',x:3,y:3,w:1,h:1,rotation:0};
const seat={id:'seat',asset:'horticulture_round_stool',x:3,y:3,w:1,h:1,rotation:0};
test('props share a cell only when visible bounds fit; overlap does not depend on IDs or insertion order',()=>{
 const other={...crate,id:'two',offset_x:.4};
 assert.ok(!propsOverlap(crate,other));
 assert.equal(placementError(other,'props',{w:8,h:8},{props:[crate],walls:[]}),'');
 assert.ok(propsOverlap(crate,{...other,offset_x:0}));
 assert.ok(propsOverlap({...other,offset_x:0},crate));
});
test('seat docking allows a small tuck, rejects a seat inside table, and stays optional/nearby',()=>{
 assert.ok(propsOverlap(table,seat));
 const [l,t,r,b]=propBounds(table),[sl,st,sr,sb]=propBounds(seat);
 const y=b+(sb-st)*.3,delta=y-(st+sb)/2;
 const near={...seat,y:4,offset_y:delta-1+.08};
 const plan={props:[table],walls:[]},size={w:8,h:8};
 const snap=snapSeat(near,plan,size);
 assert.ok(snap.snapped);assert.equal(snap.tableId,'table');
 assert.ok(!propsOverlap(snap.item,table));
 const bounds=propBounds(snap.item);assert.ok(bounds[1]<b); // actually tucked, not merely adjacent
 assert.ok(!snapSeat({...seat,y:7},plan,size).snapped);
 assert.ok(!snapSeat(crate,plan,size).snapped);
 const blocked={props:[table,{...snap.item,id:'occupied'}],walls:[]};
 assert.ok(!snapSeat(near,blocked,size).snapped);
});
test('tables draw over seats regardless of insertion order and source aspect is retained',()=>{
 const cat={ground:{},props:{horticulture_round_table:{file:'table.png'},horticulture_round_stool:{file:'seat.png'}}};
 for(const props of [[table,seat],[seat,table]]){
  const svg=constructionSVG({ground:{},props,walls:[]},{w:8,h:8},cat);
  assert.ok(svg.indexOf('data-construction-id="seat"')<svg.indexOf('data-construction-id="table"'));
 }
});

test('spacing adjustments tuck farther or pull out while keeping the same table and side',()=>{
 const [l,t,r,b]=propBounds(table),[sl,st,sr,sb]=propBounds(seat),height=sb-st;
 const near={...seat,offset_y:b+height*.3-(st+sb)/2};
 const plan={props:[table],walls:[]},size={w:8,h:8};
 const dock=snapSeat(near,plan,size);assert.ok(dock.snapped);
 const deep=snapSeat({...dock.item,table_spacing:-.6},plan,size,{reference:dock.item});
 assert.ok(deep.snapped);assert.equal(deep.tableId,table.id);
 assert.ok(!propsOverlap(deep.item,table));
 assert.ok(Math.abs(propBounds(deep.item)[1]-(b-height*.6))<.002);
 const out=snapSeat({...deep.item,table_spacing:.6},plan,size,{reference:deep.item});
 assert.ok(out.snapped);assert.equal(out.tableId,table.id);
 assert.ok(Math.abs(propBounds(out.item)[1]-(b+height*.6))<.002);
 assert.equal(out.item.table_spacing,.6);
 assert.ok(propsOverlap(seat,table));
 const blocked={props:[table,{...out.item,id:'obstacle'}],walls:[]};
 assert.ok(!snapSeat({...deep.item,table_spacing:.6},blocked,size,{reference:deep.item}).snapped);
});
