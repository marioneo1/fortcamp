import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createServer as createHttpServer} from 'node:http';
import {createServer} from 'vite';
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

test('source dev serves CSS and API with a socket-free reload client',async()=>{
 const root=await mkdtemp(join(tmpdir(),'fortcamp-steady-dev-'));
 const api=createHttpServer((req,res)=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify({path:req.url,debug:true}))});
 await new Promise(resolve=>api.listen(0,'127.0.0.1',resolve));let server;
 try {
  await writeFile(join(root,'index.html'),'<html><body>Dev game<script type="module" src="/game.js"></script></body></html>');
  await writeFile(join(root,'game.js'),'import "./style.css";window.gameLoaded=true;');
  await writeFile(join(root,'style.css'),'.game{color:red}');
  const config=configure({mode:'development'});
  server=await createServer({...config,configFile:false,root,optimizeDeps:{noDiscovery:true,include:[]},server:{...config.server,port:0,proxy:{'/api':{target:`http://127.0.0.1:${api.address().port}`,changeOrigin:false}}}});await server.listen();
  const origin=`http://127.0.0.1:${server.httpServer.address().port}`;
  const html=await (await fetch(origin)).text();assert.match(html,/Dev game/);
  const client=await (await fetch(origin+'/@vite/client')).text();assert.match(client,/export function updateStyle/);assert.match(client,/export function createHotContext/);assert.doesNotMatch(client,/WebSocket|location\.reload|transport\.connect/);
  assert.match(await (await fetch(origin+'/game.js')).text(),/gameLoaded/);
  const css=await (await fetch(origin+'/style.css?v=startup-regression')).text();assert.match(css,/updateStyle/);assert.match(css,/color:red/);
  assert.deepEqual(await (await fetch(origin+'/api/state')).json(),{path:'/api/state',debug:true});
  assert.equal((await fetch(origin)).headers.get('cache-control'),'no-store, max-age=0');
 } finally {if(server)await server.close();await new Promise(resolve=>api.close(resolve));await rm(root,{recursive:true,force:true})}
});
