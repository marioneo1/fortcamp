import test from 'node:test';
import assert from 'node:assert/strict';
import {snapHud,hudPosition,hudScale,resizeHudScale} from './battle-hud-geometry.js';

test('panel resizing preserves defaults and proportions while fitting the viewport',()=>{
 const panel={width:1200,height:300},window={width:1440,height:900};
 assert.equal(hudScale(undefined,panel,window),1);
 assert.equal(resizeHudScale(1,-240,-60,panel,window),.8);
 assert.equal(resizeHudScale(1,-2400,-600,panel,window),.5);
 assert.ok(hudScale(1,panel,{width:600,height:400})*panel.width<=592);
 assert.ok(hudScale(1,{width:300,height:500},{width:600,height:200})*500<=192);
});

test('HUD groups snap to viewport centers and neighboring edges',()=>{
 const bounds={width:1000,height:700};
 const center=snapHud({x:397,y:201,width:200,height:80},[],bounds);
 assert.equal(center.x,400);assert.ok(center.guides.some(g=>g.axis==='x'&&g.value===500));
 const neighbor=snapHud({x:298,y:173,width:150,height:70},[{x:100,y:100,width:200,height:80}],bounds);
 assert.equal(neighbor.x,300);assert.equal(neighbor.y,180);
});
test('free placement skips near snapping and all positions stay inside the window',()=>{
 const bounds={width:1000,height:700};
 assert.equal(snapHud({x:397,y:201,width:200,height:80},[],bounds,0).x,397);
 const outside=snapHud({x:1200,y:-30,width:200,height:80},[],bounds);
 assert.equal(outside.x,800);assert.equal(outside.y,0);
 assert.deepEqual(hudPosition({x:1,y:1},{width:1200,height:900},bounds,{x:0,y:0}),{x:0,y:0});
});
test('saved placements retain relative alignment after window changes',()=>{
 assert.deepEqual(hudPosition({x:.5,y:1},{width:200,height:80},{width:1000,height:700},{x:0,y:0}),{x:400,y:620});
 assert.deepEqual(hudPosition(null,{width:200,height:80},{width:600,height:400},{x:.5,y:1}),{x:200,y:320});
});
