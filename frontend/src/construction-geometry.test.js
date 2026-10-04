import test from 'node:test';
import assert from 'node:assert/strict';
import {wallSegments,wallConnections,snapAnchor,rotatePlacement,validPlacement} from './construction-geometry.js';
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
