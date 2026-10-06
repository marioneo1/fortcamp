import test from 'node:test';
import assert from 'node:assert/strict';
import {createNavigationInput} from './navigation-input.js';
test('entrance spam is suppressed until units, doors or context change',()=>{
 const q=createNavigationInput(),b={current_unit_id:'p',units:{p:{id:'p',x:1,y:2},n:{id:'n',x:3,y:2}},terrain:[{id:'d',state:'closed'}],objects:{}};
 const command={action:'navigate',x:5,y:2};assert.equal(q.accept('turn',b,command),true);
 for(let i=0;i<100;i++)assert.equal(q.accept('turn',structuredClone(b),command),false);
 b.units.n.x=4;assert.equal(q.accept('turn',b,command),true);
 b.terrain[0].state='opened';assert.equal(q.accept('turn',b,command),true);
 assert.equal(q.accept('other',b,command),true);q.clear();assert.equal(q.accept('other',b,command),true);
});
