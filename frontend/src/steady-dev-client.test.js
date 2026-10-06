import test from 'node:test';
import assert from 'node:assert/strict';
import {createHotContext,updateStyle,removeStyle} from './steady-dev-client.js';

test('Vite CSS hot context imports are safe while reload transport is disabled',()=>{
 const hot=createHotContext('/src/style.css?v=version');
 for(const name of ['accept','acceptExports','dispose','prune','on','off','send','invalidate'])assert.doesNotThrow(()=>hot[name](()=>{}));
 assert.deepEqual(hot.data,{});
});
test('CSS loads and replaces its existing style without opening any connection',()=>{
 const old=globalThis.document,styles=[];
 globalThis.document={head:{append:el=>styles.push(el)},createElement:()=>({setAttribute(){},remove(){styles.splice(styles.indexOf(this),1)}})};
 try{updateStyle('startup','.hidden{display:none}');updateStyle('startup','.hidden{display:none!important}');assert.equal(styles.length,1);assert.match(styles[0].textContent,/important/);removeStyle('startup');assert.equal(styles.length,0)}finally{if(old===undefined)delete globalThis.document;else globalThis.document=old}
});
