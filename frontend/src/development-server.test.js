import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createServer as createHttpServer} from 'node:http';
import {preview} from 'vite';
import configure from '../vite.config.js';

test('normal play mode disables watchers; live edit is explicit',()=>{
 const old=process.env.FORTCAMP_DEV_AUTO_RELOAD;
 try {
  process.env.FORTCAMP_DEV_AUTO_RELOAD='false';let config=configure({mode:'development'});
  assert.equal(config.server.hmr,false);assert.equal(config.server.watch,null);
  process.env.FORTCAMP_DEV_AUTO_RELOAD='true';config=configure({mode:'development'});
  assert.equal(config.server.hmr,true);assert.deepEqual(config.server.watch,{});
 } finally {if(old===undefined)delete process.env.FORTCAMP_DEV_AUTO_RELOAD;else process.env.FORTCAMP_DEV_AUTO_RELOAD=old}
});

test('built dev preview serves game files without a reload client and proxies API',async()=>{
 const root=await mkdtemp(join(tmpdir(),'fortcamp-steady-dev-'));
 const api=createHttpServer((req,res)=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify({path:req.url,debug:true}))});
 await new Promise(resolve=>api.listen(0,'127.0.0.1',resolve));let server;
 try {
  await mkdir(join(root,'dist'));await writeFile(join(root,'dist','index.html'),'<html><body>Dev game<script type="module" src="/game.js"></script></body></html>');
  await writeFile(join(root,'dist','game.js'),'window.gameLoaded=true;');
  const config=configure({mode:'development'});
  server=await preview({...config,configFile:false,root,preview:{...config.preview,port:0,proxy:{'/api':{target:`http://127.0.0.1:${api.address().port}`,changeOrigin:false}}}});
  const origin=`http://127.0.0.1:${server.httpServer.address().port}`;
  const html=await (await fetch(origin)).text();assert.match(html,/Dev game/);assert.doesNotMatch(html,/@vite\/client|WebSocket/);
  assert.match(await (await fetch(origin+'/game.js')).text(),/gameLoaded/);
  assert.deepEqual(await (await fetch(origin+'/api/state')).json(),{path:'/api/state',debug:true});
  await writeFile(join(root,'unrelated-source.js'),'changed');
  assert.equal(await (await fetch(origin)).text(),html);
 } finally {if(server)await new Promise(resolve=>server.httpServer.close(resolve));await new Promise(resolve=>api.close(resolve));await rm(root,{recursive:true,force:true})}
});
