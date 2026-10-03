import test from 'node:test';
import assert from 'node:assert/strict';
import {structuralLayout,structuralConnectors,connectionPorts,wallArtStyle} from './building-joins.js';
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

const modular={fieldstone:{join_offset:.36,wall_half_thickness:.09,cap_mode:'pillar',cap_scale:.35},iron:{join_offset:.38,cap_mode:'trim'}};
const wall=(id,x,y=0,extra={})=>({id,x,y,sprite:'structure:fieldstone_wall',art_scale:1.25,...extra});
const capCount=items=>structuralConnectors(items,modular).filter(c=>c.wall_cap).length;
test('isolated walls cap both ends; connected runs cap only the outside ends',()=>{
 assert.equal(capCount([wall('alone',0)]),2);
 const run=[wall('first',0),wall('second',1),wall('third',2)];
 assert.equal(capCount(run),2);
 assert.deepEqual(structuralConnectors(run,modular).filter(c=>c.wall_cap).map(c=>c.parent_id),['first','third']);
});
test('corners and branch connections consume neighboring columns in every rotation',()=>{
 for(const rotation of [0,90,180,270]){
  const c={id:'c',x:4,y:4,sprite:'structure:fieldstone_corner',rotation};
  const ports=connectionPorts(c,modular);
  const neighbors=ports.map((p,index)=>({id:'n'+index,x:p.x,y:p.y,sprite:'structure:fieldstone_end',rotation:(p.rotation+180)%360,art_offset:[0,0]}));
  // Put each neighbor's single attached port exactly against the corner port.
  neighbors.forEach((n,index)=>{const p=connectionPorts(n,modular)[0];n.x+=ports[index].x-p.x;n.y+=ports[index].y-p.y});
  assert.equal(structuralLayout(c,modular,neighbors).connectors.filter(c=>c.wall_cap).length,0);
 }
});
test('door jambs keep wall ends connected, including open doors',()=>{
 for(const state of ['closed','open']){
  const run=[wall('left',0),wall('gate',1,0,{sprite:'structure:fieldstone_gate_'+state}),wall('right',2)];
  assert.equal(capCount(run),2);
 }
});
test('removing or destroying a neighbor exposes a cap; parallel walls do not consume it',()=>{
 const a=wall('a',0),b=wall('b',1);
 assert.equal(capCount([a,b]),2);
 assert.equal(capCount([a,{...b,destroyed:true}]),2);
 assert.equal(structuralLayout(a,modular,[{...b,destroyed:true}]).connectors.filter(c=>c.wall_cap).length,2);
 assert.equal(capCount([a,wall('parallel',0,1)]),4);
});
test('connected metal reuses post-free center strips and leaves only external caps',()=>{
 const items=[wall('a',0,0,{sprite:'structure:iron_wall'}),wall('b',1,0,{sprite:'structure:iron_wall'})];
 const parts=structuralConnectors(items,modular);
 assert.equal(parts.filter(c=>c.wall_cap).length,2);
 assert.ok(parts.filter(c=>!c.wall_cap).every(c=>c.art_clip[1]>=25&&c.art_clip[3]>=25));
 assert.equal(structuralLayout(items[0],modular).hideArt,true);
});

test('new stone terminal is a half wall with one outer cap when attached',()=>{
 const end=wall('end',0,0,{sprite:'structure:fieldstone_end'}),neighbor=wall('next',1);
 const layout=structuralLayout(end,modular,[neighbor]);
 assert.equal(layout.hideArt,true);
 assert.equal(layout.connectors.filter(c=>c.wall_cap).length,1);
 assert.equal(layout.connectors.find(c=>!c.wall_cap).art_clip[3],50);
});
test('saved perimeter offsets follow the current material without changing map geometry',()=>{
 const items=[wall('a',0,0,{edge_wall:true,wall_edges:['north'],art_offset:[0,-.5]}),wall('b',1,0,{edge_wall:true,wall_edges:['north'],art_offset:[0,-.3]})];
 assert.deepEqual(structuralLayout(items[0],modular).offset,[0,-.36]);
 assert.equal(capCount(items),2);
});
test('resolved metal strips stay visible and never recursively assemble themselves',()=>{
 const sections=structuralConnectors([wall('metal',0,0,{sprite:'structure:iron_wall'})],modular);
 for(const part of sections){
  const layout=structuralLayout(part,modular);
  assert.equal(layout.hideArt,undefined);
  assert.deepEqual(layout.connectors,[]);
  assert.deepEqual(layout.offset,part.art_offset);
 }
});

test('perimeter faces point inside and match the adjoining corner in every rotation',()=>{
 const edges=['north','east','south','west'],normals=[[0,1],[-1,0],[0,-1],[1,0]];
 for(const family of ['fieldstone','iron'])for(let buildingTurn=0;buildingTurn<4;buildingTurn++)for(let side=0;side<4;side++){
  const rotation=((side%2)*90+buildingTurn*90)%360,edge=edges[(side+buildingTurn)%4];
  const item={id:'face',sprite:`structure:${family}_wall`,rotation,edge_wall:true,wall_edges:[edge]};
  const layout=structuralLayout(item,modular),mirror=layout.mirrorY;
  let normal=[0,mirror];for(let n=0;n<rotation/90;n++)normal=[-normal[1],normal[0]];
  assert.deepEqual(normal.map(v=>v||0),normals[(side+buildingTurn)%4]);
  assert.equal(item.rotation,rotation); // artwork must not rotate collision or saved placement
  for(const part of layout.connectors.filter(p=>!p.wall_cap))assert.equal(part.art_mirror_y,mirror);
 }
});
test('centered dividers retain their orientation; concave corners reverse their painted face',()=>{
 assert.equal(structuralLayout(wall('divider',0,0,{rotation:90}),modular).mirrorY,1);
 const inner=structuralLayout({id:'inner',sprite:'structure:fieldstone_corner',rotation:90,art_offset:[.72,.72]},modular);
 assert.ok(inner.connectors.filter(c=>!c.wall_cap).every(c=>c.art_mirror_y===-1));
});
test('metal corner textures meet at complementary diagonal cuts through the same joint',()=>{
 const o=modular.iron.join_offset;
 for(const rotation of [0,90,180,270]){
  const parts=structuralLayout({id:'corner',sprite:'structure:iron_corner',rotation},modular).connectors.filter(c=>!c.wall_cap);
  let seams=0;
  for(const part of parts){
   assert.ok(part.art_clip_polygon.length>=3);
   for(const [px,py] of part.art_clip_polygon){
    let x=(px/100-.5)*part.art_scale,y=(py/100-.5)*part.art_scale;
    for(let n=0;n<part.rotation/90;n++)[x,y]=[-y,x];
    x+=part.art_offset[0];y+=part.art_offset[1];
    for(let n=0;n<rotation/90;n++)[x,y]=[y,-x];
    const sum=x+y,isHorizontal=part.rotation===rotation;
    assert.ok(isHorizontal?sum<1e-8:sum>-1e-8);
    if(Math.abs(sum)<1e-8&&Math.abs(x-o)<.15)seams++;
   }
  }
  assert.ok(seams>=4,'both arms meet the diagonal near the corner');
 }
});
test('mirroring a painted face preserves a diagonal clip in map space',()=>{
 const item={art_mirror_y:-1,art_clip_polygon:[[20,30],[70,40],[60,80]]};
 assert.equal(wallArtStyle(item,{}),'--asset-mirror-y:-1;--asset-clip:polygon(20% 70%,70% 60%,60% 20%);--wall-art-layer:2');
});
test('mirrored breaches retain their surviving band alignment on the opposite perimeter',()=>{
 const g={timber:{join_offset:.4,breach_offset:[0,.04]}};
 const north=structuralLayout({sprite:'structure:timber_breach',rotation:0,edge_wall:true,wall_edges:['north']},g);
 const south=structuralLayout({sprite:'structure:timber_breach',rotation:0,edge_wall:true,wall_edges:['south']},g);
 close(north.offset[1],-.36);close(south.offset[1],.36);
 assert.equal(north.mirrorY,1);assert.equal(south.mirrorY,-1);
});

test('T and cross arms match adjoining centered walls after every quarter turn',()=>{
 const normal=part=>{
  let p=[0,part.art_mirror_y??part.mirrorY??1];
  for(let n=0;n<(part.rotation||0)/90;n++)p=[-p[1],p[0]];
  return p.map(v=>v||0);
 };
 for(const family of ['fieldstone','iron'])for(const piece of ['junction','cross','edge_junction'])for(const rotation of [0,90,180,270]){
  const result=structuralLayout({id:'branch',sprite:`structure:${family}_${piece}`,rotation},modular);
  const arms=result.connectors.filter(c=>!c.wall_cap);
  for(const arm of arms){
   if(piece==='edge_junction'&&arm.rotation===rotation)continue; // perimeter bar follows the outside boundary
   const neighbor={sprite:`structure:${family}_wall`,rotation:arm.rotation};
   assert.deepEqual(normal(arm),normal({...neighbor,...structuralLayout(neighbor,modular)}));
  }
 }
});
test('the lower perimeter T preserves its inward-facing bar while reversing only its divider stem',()=>{
 const result=structuralLayout({id:'bottom',sprite:'structure:fieldstone_edge_junction',rotation:180,wall_edges:['south']},modular);
 const arms=result.connectors.filter(c=>!c.wall_cap);
 assert.equal(arms[0].rotation,180);assert.equal(arms[0].art_mirror_y,1);
 assert.equal(arms[1].rotation,270);assert.equal(arms[1].art_mirror_y,-1);
 assert.deepEqual(arms.map(c=>c.art_offset),[[0,.36],[0,0]]);
});
test('opposite stone end posts match the horizontal wall face instead of reversing it',()=>{
 const caps=structuralConnectors([wall('branch',0)],modular).filter(c=>c.wall_cap);
 assert.equal(caps.length,2);
 assert.deepEqual(caps.map(c=>[c.rotation,c.art_mirror_y]),[[0,1],[180,-1]]);
 const end=structuralLayout(wall('terminal',0,0,{sprite:'structure:fieldstone_end',rotation:180}),modular);
 assert.equal(end.connectors.find(c=>c.id==='terminal_terminal_cap').art_mirror_y,-1);
});
test('horizontal corner and junction bands cover vertical bands in every rotation',()=>{
 for(const piece of ['corner','junction','cross','edge_junction'])for(const rotation of [0,90,180,270]){
  const arms=structuralLayout({id:'join',sprite:'structure:fieldstone_'+piece,rotation},modular).connectors.filter(c=>!c.wall_cap);
  assert.ok(arms.some(c=>c.art_layer===3));assert.ok(arms.some(c=>c.art_layer===2));
  for(const arm of arms)assert.equal(arm.art_layer,arm.rotation%180===0?3:2);
 }
});
test('calibrated stone T uses its dedicated sprite without changing connection ports',()=>{
 const g={fieldstone:{...modular.fieldstone,native_junction_offset:[0,.2881],native_junction_rotations:[90]}};
 const item={id:'native',x:4,y:3,sprite:'structure:fieldstone_junction',rotation:90};
 const layout=structuralLayout(item,g);
 assert.equal(layout.hideArt,undefined);assert.equal(layout.layer,3);assert.equal(layout.mirrorY,1);
 close(layout.offset[0],-.2881);close(layout.offset[1],0);
 assert.ok(layout.connectors.every(c=>c.wall_cap));
 assert.deepEqual(connectionPorts(item,g),connectionPorts(item,modular));
 assert.equal(structuralLayout({...item,rotation:180},g).hideArt,true);
 assert.deepEqual(structuralLayout({...item,destroyed:true},g).connectors,[]);
});
