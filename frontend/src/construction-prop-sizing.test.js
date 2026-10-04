import test from 'node:test';
import assert from 'node:assert/strict';
import {propBounds,propImageLayout,constructionCellBlocked} from './construction-geometry.js';
import {constructionSVG} from './construction-render.js';
import profiles from './construction-prop-sizing.json' with {type:'json'};
import art from './construction-prop-bounds.json' with {type:'json'};
const prop=(asset,extra={})=>({id:'object',asset,x:2,y:2,w:1,h:1,rotation:0,...extra});
test('all audited construction profiles have measurements and calibrated sizes fit their footprints',()=>{
 for(const [key,p] of Object.entries(profiles)){
  assert.ok(art[key]);assert.ok(p.fill>0&&p.fill<=1);
  const [w,h]=p.footprint,box=propBounds(prop(key,{w,h}));
  assert.ok(box[2]-box[0]<=w*p.fill+1e-7);assert.ok(box[3]-box[1]<=h*p.fill+1e-7);
  for(const rotation of [0,90,180,270]){
   const o=prop(key,{w:rotation%180?h:w,h:rotation%180?w:h,rotation}),[l,t,r,b]=propBounds(o);
   assert.ok(Math.abs((l+r)/2-(o.x+o.w/2))<1e-7);assert.ok(Math.abs((t+b)/2-(o.y+o.h/2))<1e-7);
  }
 }
});
test('map and lantern are small clutter; furniture and large props keep meaningful sizes',()=>{
 const span=key=>{const p=profiles[key],b=propBounds(prop(key,{w:p.footprint[0],h:p.footprint[1]}));return Math.max(b[2]-b[0],b[3]-b[1])};
 assert.ok(span('marked_farm_chart')<span('timber_chair'));
 assert.ok(span('camp_lantern')<span('wooden_table'));
 assert.ok(span('village_well')>span('wooden_table')*2);
 assert.deepEqual(profiles.wooden_bed.footprint,[1,2]);assert.deepEqual(profiles.repair_workbench.footprint,[2,1]);
});
test('placement outline is tight on transformed art, noninteractive, and invalid preview is red',()=>{
 const p=prop('marked_farm_chart',{rotation:90,offset_x:.23,offset_y:-.12}),b=propBounds(p),layout=propImageLayout(p);
 const cat={ground:{},props:{marked_farm_chart:{file:'chart.png'}}};
 const svg=constructionSVG({ground:{},props:[],walls:[]},{w:8,h:8},cat,{ghost:{layer:'props',item:p,error:'overlap'}});
 assert.ok(svg.includes(`x="${b[0]}" y="${b[1]}" width="${b[2]-b[0]}" height="${b[3]-b[1]}"`));
 assert.match(svg,/data-placement-bounds="prop"/);assert.match(svg,/stroke="#ff7666"/);assert.match(svg,/pointer-events="none"/);
 assert.match(svg,/<rect data-prop-hit /);assert.match(svg,/<image pointer-events="none"/);
 assert.ok(svg.includes(`width="${layout.w}" height="${layout.h}"`));
 const plain=constructionSVG({ground:{},props:[p],walls:[]},{w:8,h:8},cat);
 assert.ok(!plain.includes('data-placement-bounds'));
 assert.equal(constructionCellBlocked({props:[p],walls:[]},2,2),false);
 assert.equal(constructionCellBlocked({props:[{...p,blocking:true}],walls:[]},2,2),true);
});
