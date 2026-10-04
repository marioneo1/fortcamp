import test from 'node:test';
import assert from 'node:assert/strict';
import {availableWallPieces} from './construction-geometry.js';
import {wallArt,wallArtImage} from './construction-wall-art.js';
import {constructionSVG} from './construction-render.js';

const wall=piece=>({id:piece,piece,shape:availableWallPieces[piece].shape,x:2,y:3,anchor:'center',rotation:0,material:'timber',posts:'none'});
test('all 24 pieces resolve to nine originals; vertical sources never come from horizontal',()=>{
 const originals=new Set();
 for(const piece of Object.keys(availableWallPieces)){
  const art=wallArt(piece,'plain_wood_v1');assert.ok(art,piece);originals.add(art.file);
  if(piece.startsWith('vertical'))assert.ok(art.source.startsWith('vertical'));
  const svg=wallArtImage(wall(piece),'plain_wood_v1');assert.ok(!svg.includes('rotate('));assert.match(svg,/preserveAspectRatio="xMidYMid meet"/);
 }
 assert.equal(originals.size,9);
});
test('post positions, opposite facings and corners use the required reflections',()=>{
 const h=wallArt('horizontal_right_post_south','plain_wood_v1');assert.equal(h.source,'horizontal_one_post');assert.ok(h.flipX&&h.flipY);
 const v=wallArt('vertical_bottom_post_west','plain_wood_v1');assert.equal(v.source,'vertical_one_post');assert.ok(v.flipX&&v.flipY);
 const corner=wallArt('corner_south_east','plain_wood_v1');assert.equal(corner.source,'corner');assert.ok(corner.flipX&&corner.flipY);
});
test('kit switching replaces all wall art without changing geometry; normal view uses placeholders',()=>{
 const plan={ground:{},props:[],walls:Object.keys(availableWallPieces).map(wall)},before=structuredClone(plan),cat={ground:{},props:{}},size={w:8,h:8};
 assert.ok(!constructionSVG(plan,size,cat).includes('data-wall-original'));
 const painted=constructionSVG(plan,size,cat,{wallKit:'plain_wood_v1'});
 assert.equal((painted.match(/data-wall-original=/g)||[]).length,24);
 assert.deepEqual(plan,before);
 assert.equal(wallArtImage({...wall('gate_horizontal'),open:true},'plain_wood_v1'),'');
});
