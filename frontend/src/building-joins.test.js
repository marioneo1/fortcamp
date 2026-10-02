import test from 'node:test';
import assert from 'node:assert/strict';
import {structuralLayout,structuralConnectors} from './building-joins.js';
const geometry={fieldstone:{join_offset:.36,corner_offset:[-.015,-.015]},timber:{join_offset:.4}};
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
test('all four corners use the same beam thickness and follow both wall edges',()=>{
 for(const rotation of [0,90,180,270]){
  const result=structuralLayout({id:'c',sprite:'structure:fieldstone_corner',x:3,y:2,rotation,art_scale:1.25},geometry);
  assert.equal(result.hideArt,true);
  assert.equal(result.connectors.length,2);
  assert.ok(result.connectors.every(c=>c.sprite==='structure:fieldstone_wall'&&c.art_scale===1.25));
  assert.deepEqual(result.connectors.map(c=>c.rotation),[rotation,(rotation+90)%360]);
 }
 const [h,v]=structuralLayout({id:'c',sprite:'structure:fieldstone_corner'},geometry).connectors;
 close(h.art_offset[1],-.36);close(v.art_offset[0],.36);
 close(h.art_clip[1],14);close(v.art_clip[3],21.2);
});
test('perimeter Ts ignore obsolete image offsets and follow their rotated edge',()=>{
 for(const [rotation,offset] of [[0,[0,-.4]],[90,[.4,0]],[180,[0,.4]],[270,[-.4,0]]]){
  const result=structuralLayout({id:'t',sprite:'structure:timber_edge_junction',rotation,art_offset:[.09,-.12]},geometry);
  close(result.connectors[0].art_offset[0],offset[0]);close(result.connectors[0].art_offset[1],offset[1]);
  assert.equal(result.hideArt,true);
 }
 const centered=structuralLayout({id:'t',sprite:'structure:timber_junction'},geometry);
 assert.deepEqual(centered.connectors[0].art_offset,[0,0]);
 assert.ok(centered.connectors[1].art_clip[3]>0);
 const cross=structuralLayout({id:'x',sprite:'structure:timber_cross'},geometry);
 assert.deepEqual(cross.connectors[1].art_clip,[0,0,0,0]);
});
test('inward corner translations remain intact; destroying a wall removes assembled beams',()=>{
 const item={id:'inner',sprite:'structure:fieldstone_corner',rotation:90,art_offset:[.72,.72]};
 const beams=structuralLayout(item,geometry).connectors;
 close(beams[0].art_offset[0],1.08);close(beams[0].art_offset[1],.72);
 assert.deepEqual(structuralConnectors([{...item,destroyed:true}],geometry),[]);
 assert.deepEqual(structuralConnectors([{id:'prop',sprite:'wooden_handcart'}],geometry),[]);
});
test('half-wall ends meet the next wall and rotate with their attached side',()=>{
 const g={timber:{end_offset:[.27,0]}};
 for(const [rotation,expected] of [[0,[.27,0]],[90,[0,.27]],[180,[-.27,0]],[270,[0,-.27]]]){
  const layout=structuralLayout({sprite:'structure:timber_end',rotation},g);
  close(layout.offset[0],expected[0]);close(layout.offset[1],expected[1]);
 }
});
test('damaged corners align their surviving arms without closing the broken center',()=>{
 const g={timber:{join_offset:.4,broken_corner_offset:[.03,-.02]}};
 const layout=structuralLayout({id:'broken',sprite:'structure:timber_corner_broken',rotation:90},g);
 close(layout.offset[0],.02);close(layout.offset[1],.03);
 assert.equal(layout.hideArt,undefined);
 assert.equal(layout.connectors.length,2);
 assert.ok(layout.connectors.every(c=>c.art_clip.some(v=>v>50)));
});
test('a breach aligns its surviving beam even after destruction and rotation',()=>{
 const g={timber:{breach_offset:[0,.04]}};
 const result=structuralLayout({sprite:'structure:timber_breach',art_offset:[.4,0],rotation:90,destroyed:true},g);
 close(result.offset[0],.36);assert.equal(result.offset[1],0);assert.deepEqual(result.connectors,[]);
});
