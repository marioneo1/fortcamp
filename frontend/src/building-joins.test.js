import test from 'node:test';
import assert from 'node:assert/strict';
import {structuralLayout,structuralConnectors} from './building-joins.js';

const geometry={fieldstone:{join_offset:.36,corner_offset:[-.015,-.015]},
                timber:{join_offset:.4,corner_offset:[.005,.005]}};
test('corners align both axes and sleeve each end without scaling the art',()=>{
 const item={id:'corner',sprite:'structure:fieldstone_corner',x:3,y:2,art_scale:1.25,rotation:0};
 const layout=structuralLayout(item,geometry);
 assert.deepEqual(layout.offset,[-.015,-.015]);
 assert.deepEqual(layout.connectors.map(c=>c.art_offset),[[-.5,-.36],[.36,.5]]);
 assert.deepEqual(layout.connectors.map(c=>c.rotation),[0,90]);
 assert.ok(layout.connectors.every(c=>c.art_scale===1.25&&c.art_clip.join(',')==='0,33,0,33'));
});
test('T sleeves span the grid seam, independent of the calibrated T image offset',()=>{
 const item={id:'t',sprite:'structure:timber_edge_junction',x:3,y:0,rotation:0,art_offset:[.007,-.076]};
 const top=structuralLayout(item,geometry);
 assert.deepEqual(top.offset,item.art_offset);
 assert.deepEqual(top.connectors[0].art_offset,[0,.5]);
 const bottom=structuralLayout({...item,rotation:180},geometry);
 assert.equal(bottom.connectors[0].art_offset[1],-.5);
 assert.equal(bottom.connectors[0].rotation,270);
});
test('rotated inward corners retain their placement and destruction removes sleeves',()=>{
 const item={id:'inward',sprite:'structure:fieldstone_corner',x:3,y:2,rotation:90,art_offset:[.72,.72]};
 const layout=structuralLayout(item,geometry);
 assert.ok(Math.abs(layout.offset[0]-.735)<1e-8);
 assert.deepEqual(layout.connectors.map(c=>c.rotation),[90,180]);
 assert.deepEqual(structuralConnectors([{...item,destroyed:true}],geometry),[]);
 assert.deepEqual(structuralConnectors([{id:'prop',sprite:'wooden_handcart'}],geometry),[]);
});
