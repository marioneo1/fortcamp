import {test} from 'node:test';
import assert from 'node:assert/strict';
import {webSessionKey,activitySessionKey,restoreWebSession} from './web-login.js';

test('web and Activity cache keys distinguish environment/database namespaces',()=>{
 const a={session_namespace:'dev-db'},b={session_namespace:'release-db'};
 assert.notEqual(webSessionKey(a),webSessionKey(b));assert.notEqual(activitySessionKey(a,'1'),activitySessionKey(b,'1'));assert.notEqual(activitySessionKey(a,'1'),activitySessionKey(a,'2'));
});
test('cached browser session restores identity without another Discord authorization',async()=>{
 const cfg={session_namespace:'dev'},data=new Map([[webSessionKey(cfg),JSON.stringify({session_token:'token'})]]),storage={getItem:k=>data.get(k),removeItem:k=>data.delete(k)};
 const api=async(path,options)=>{assert.equal(path,'/api/state');assert.equal(options.headers.Authorization,'Bearer token');return {identity:{guild_id:'1',user_id:'2'}}};
 assert.deepEqual(await restoreWebSession(api,storage,cfg),{session_token:'token',identity:{guild_id:'1',user_id:'2'}});
});
test('expired tokens are discarded while transient failures do not force reauthorization',async()=>{
 const cfg={session_namespace:'dev'},data=new Map([[webSessionKey(cfg),' {"session_token":"token"}']]),storage={getItem:k=>data.get(k),removeItem:k=>data.delete(k)};
 const fail=status=>async()=>{throw Object.assign(Error('Failure'),{status})};
 await assert.rejects(restoreWebSession(fail(502),storage,cfg));assert.equal(data.size,1);
 assert.equal(await restoreWebSession(fail(403),storage,cfg),null);assert.equal(data.size,1);
 assert.equal(await restoreWebSession(fail(401),storage,cfg),null);assert.equal(data.size,0);
});
