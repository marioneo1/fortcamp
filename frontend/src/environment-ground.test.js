import {test} from 'node:test';
import assert from 'node:assert/strict';
import {environmentGroundStyle} from './environment-ground.js';

test('adjacent cells use different portions of one continuous ground image',()=>{
 const base={sprite:'herbs_sage',texture_span:2,origin:[5,3]};
 const left=environmentGroundStyle({...base,x:5,y:3});
 const right=environmentGroundStyle({...base,x:6,y:3});
 assert.ok(left.includes('--ground-span:200%'));
 assert.ok(left.includes('--ground-x:0%'));assert.ok(right.includes('--ground-x:100%'));
 assert.ok(environmentGroundStyle({...base,x:5,y:4}).includes('--ground-y:100%'));
});
test('unregistered art and older battles retain ordinary terrain',()=>{
 assert.equal(environmentGroundStyle(), '');
 assert.equal(environmentGroundStyle({sprite:'not_registered'}), '');
 assert.ok(environmentGroundStyle({sprite:'garden_soil',x:4,y:4,texture_span:1}).includes('--ground-x:50%'));
});
