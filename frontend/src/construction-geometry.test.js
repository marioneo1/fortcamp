import test from 'node:test';
import assert from 'node:assert/strict';
import {defaultWallAnchor,propBounds,wallSegments,wallConnections,snapAnchor,rotatePlacement,validPlacement,wallPieces,availableWallPieces,wallLibraryEntries,wallLibraryPiece,wallPosts,nudgePlacement,placementError,constructionStepAllowed} from './construction-geometry.js';
import {constructionSVG} from './construction-render.js';
const wall=(extra={})=>({id:'wall',x:2,y:2,shape:'straight',anchor:'center',material:'timber',rotation:0,posts:'auto',...extra});
test('shared cell edges have identical ports; T and cross use exact half-cell segments',()=>{
 assert.deepEqual(wallSegments(wall({anchor:'north'})),wallSegments(wall({anchor:'south',y:1})));
 assert.equal(wallSegments(wall({shape:'tee'})).length,3);
 assert.equal(wallSegments(wall({shape:'cross'})).length,4);
 assert.deepEqual(wallSegments(wall({shape:'half',rotation:90}))[0][1],[2.5,3]);
});
test('joining straight pieces creates one node and deduplicates overlapping arms',()=>{
 const walls=[wall(),wall({id:'next',x:3}),wall({id:'vertical',rotation:90})];
 const graph=wallConnections(walls);
 assert.equal(graph.get('2.5,2.5').neighbors.size,4);
 assert.equal(graph.get('3,2.5').neighbors.size,2);
 assert.equal(wallConnections([...walls,wall()]).get('2.5,2.5').neighbors.size,4);
});
test('snapping, boundary validation and multi-cell rotation stay proportional',()=>{
 assert.equal(snapAnchor(2.02,2.49).anchor,'west');
 assert.equal(snapAnchor(2.5,2.52).anchor,'center');
 assert.ok(!validPlacement(wall({x:0,anchor:'west'}),'walls',{w:8,h:8}));
 const p={x:1,y:2,w:2,h:1,rotation:0};
 assert.deepEqual(rotatePlacement(p,'props'),{x:1,y:2,w:1,h:2,rotation:90});
 let next=p;for(let i=0;i<4;i++)next=rotatePlacement(next,'props');assert.deepEqual(next,p);
});
test('renderer uses aspect-preserving props and removes end posts at connected ports',()=>{
 const cat={ground:{},props:{crate:{file:'crate.png'}}},size={w:8,h:8};
 const plan={ground:{},props:[{id:'crate',asset:'crate',x:1,y:1,w:2,h:1,rotation:90}],walls:[wall(),wall({id:'next',x:3})]};
 const svg=constructionSVG(plan,size,cat);
 assert.match(svg,/preserveAspectRatio="xMidYMid meet"/);
 assert.equal((svg.match(/rx=".025"/g)||[]).length,2);
});


test('directional corners have two full-cell arms and stay within their cell',()=>{
 for(const piece of Object.keys(wallPieces).filter(id=>id.startsWith('corner_'))){
  const w=wall({piece,shape:'corner'}),segments=wallSegments(w);
  assert.equal(segments.length,2);
  for(const [a,b] of segments)assert.equal(Math.hypot(a[0]-b[0],a[1]-b[1]),1);
  assert.ok(validPlacement(w,'walls',{w:3,h:3}));
 }
});
test('four-step wall rotation switches native H/V pieces and returns to the original post side',()=>{
 let w=wall({piece:'horizontal_left_post',posts:'none'});
 for(const piece of ['vertical_top_post','horizontal_right_post_south','vertical_bottom_post_west','horizontal_left_post']){
  w=rotatePlacement(w,'walls');assert.equal(w.piece,piece);assert.equal(w.rotation,0);
 }
 assert.deepEqual(wallPosts(w),[[2,2.5]]);
 let plain=wall({piece:'horizontal_plain'});
 for(const piece of ['vertical_plain','horizontal_plain_south','vertical_plain_west','horizontal_plain']){
  plain=rotatePlacement(plain,'walls');assert.equal(plain.piece,piece);
 }
});
test('edge wall rotations carry the anchor around the cell and remain inside the map',()=>{
 const top=wall({piece:'horizontal_plain',x:0,y:0,anchor:'north'}),right=rotatePlacement(top,'walls');
 assert.equal(right.anchor,'east');assert.equal(right.piece,'vertical_plain');assert.ok(validPlacement(right,'walls',{w:8,h:8}));
});

test('library hides facing duplicates and rotated corners while retaining direct native vertical choices',()=>{
 const ids=wallLibraryEntries().map(([id])=>id);
 assert.ok(ids.includes('horizontal_plain')&&ids.includes('vertical_plain'));
 assert.ok(!ids.includes('horizontal_plain_south')&&!ids.includes('vertical_plain_west'));
 assert.equal(ids.filter(id=>id.startsWith('corner_')).length,1);
 for(const id of Object.keys(availableWallPieces))assert.ok(ids.includes(wallLibraryPiece(id)));
});
test('full-cell T branches connect at their midpoint; nudges respect wall sides and prop bounds',()=>{
 const w=wall({piece:'tee_north'});assert.equal(wallConnections([w]).get('2.5,2').neighbors.size,3);
 assert.equal(nudgePlacement(w,'walls','ArrowLeft').anchor,'west');
 assert.equal(nudgePlacement(w,'walls','Home').anchor,'center');
 const p={offset_x:.44,offset_y:0};assert.equal(nudgePlacement(p,'props','ArrowRight').offset_x,.49);
 assert.equal(nudgePlacement(p,'props','ArrowDown',true).offset_y,.01);
 assert.deepEqual(nudgePlacement(p,'props','Home'),{offset_x:0,offset_y:0});
});


test('junctions are retired from brushes but saved native junctions remain renderable',()=>{
 assert.ok(Object.values(availableWallPieces).every(p=>!['tee','cross','half'].includes(p.shape)));
 const saved=wall({piece:'tee_north',shape:'tee'});
 assert.equal(wallSegments(saved).length,2);
 assert.deepEqual(rotatePlacement(saved,'walls'),saved);
});

test('shared-edge duplicate detection ignores owning cell, facing, posts and material but allows perpendicular joins',()=>{
 const existing=wall({piece:'horizontal_plain',anchor:'south'}),plan={walls:[existing],props:[]},size={w:8,h:8};
 assert.match(placementError(wall({id:'new',piece:'horizontal_right_post_south',anchor:'north',y:3,material:'iron'}),'walls',size,plan),/already occupies/);
 assert.equal(placementError(wall({id:'join',piece:'vertical_plain',anchor:'east'}),'walls',size,plan),'');
 assert.equal(placementError({...existing},'walls',size,plan),'');
});

test('prop collision follows its shifted artwork footprint and checks both placement directions',()=>{
 const w=wall({piece:'vertical_plain',anchor:'west'}),p={id:'crate',x:2,y:2,w:1,h:1,rotation:0,offset_x:0,offset_y:0};
 const size={w:8,h:8};
 assert.match(placementError(p,'props',size,{walls:[w],props:[]}),/overlaps a wall/);
 assert.equal(placementError({...p,offset_x:.15},'props',size,{walls:[w],props:[]}),'');
 assert.match(placementError(w,'walls',size,{walls:[],props:[p]}),/overlaps a prop/);
 assert.match(placementError({...p,w:2,x:1},'props',size,{walls:[wall({piece:'vertical_plain'})],props:[]}),/overlaps a wall/);
});

test('edge walls permit entry from the free side and movement alongside; center walls block the cell',()=>{
 const size={w:8,h:8},plan={props:[],walls:[wall({piece:'vertical_plain',anchor:'west'})]};
 assert.ok(constructionStepAllowed(plan,size,3,2,2,2));
 assert.ok(!constructionStepAllowed(plan,size,1,2,2,2));
 assert.ok(!constructionStepAllowed(plan,size,2,2,1,2));
 assert.ok(constructionStepAllowed(plan,size,2,2,2,3));
 plan.walls[0].anchor='east';assert.ok(!constructionStepAllowed(plan,size,3,2,2,2));
 plan.walls[0].anchor='center';assert.ok(!constructionStepAllowed(plan,size,3,2,2,2));
 plan.walls[0].shape='gate';plan.walls[0].open=true;assert.ok(constructionStepAllowed(plan,size,3,2,2,2));
 plan.walls[0].open=false;plan.walls[0].broken=true;assert.ok(constructionStepAllowed(plan,size,3,2,2,2));
});

test('full corner boundary arms and shifted interior arms use their real world positions',()=>{
 const size={w:8,h:8},plan={props:[],walls:[wall({piece:'corner_north_west'})]};
 assert.ok(constructionStepAllowed(plan,size,3,2,2,2));
 assert.ok(constructionStepAllowed(plan,size,2,3,2,2));
 assert.ok(!constructionStepAllowed(plan,size,1,2,2,2));
 assert.ok(!constructionStepAllowed(plan,size,2,1,2,2));
 plan.walls[0].anchor='east';assert.ok(!constructionStepAllowed(plan,size,3,2,2,2));
});


test('visible prop fits between three edge walls but cannot cross a center wall',()=>{
 const p={id:'crate',asset:'crate_closed',x:2,y:2,w:1,h:1,rotation:0};
 const walls=[wall({piece:'horizontal_plain',anchor:'north'}),wall({id:'left',piece:'vertical_plain',anchor:'west'}),wall({id:'right',piece:'vertical_plain',anchor:'east'})];
 assert.equal(placementError(p,'props',{w:8,h:8},{props:[],walls}),'');
 assert.match(placementError(p,'props',{w:8,h:8},{props:[],walls:[wall({piece:'horizontal_plain',anchor:'center'})]}),/overlaps/);
 assert.match(placementError({...p,offset_y:-.3},'props',{w:8,h:8},{props:[],walls}),/overlaps/);
 const bottom=wall({piece:'horizontal_plain',anchor:'south'});
 assert.equal(placementError(p,'props',{w:8,h:8},{props:[],walls:[bottom]}),'');
 assert.match(placementError({...p,w:2,h:2},'props',{w:8,h:8},{props:[],walls:[wall({piece:'vertical_plain',anchor:'east'})]}),/overlaps/);
 const bounds=propBounds({...p,w:2,h:1,rotation:90});assert.ok(bounds[2]-bounds[0]<bounds[3]-bounds[1]);
});
test('new wall defaults put straight pieces at edges and corners at center',()=>{
 assert.equal(defaultWallAnchor('horizontal_left_post'),'north');
 assert.equal(defaultWallAnchor('vertical_top_post'),'west');
 assert.equal(defaultWallAnchor('corner_north_west'),'center');
});
