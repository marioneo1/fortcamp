import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createServer as createHttpServer,request} from 'node:http';
import {fileURLToPath} from 'node:url';
import {createServer as createViteServer} from 'vite';

test('actual development proxy preserves public host and Origin for browser OAuth',async()=>{
 const backend=createHttpServer((req,res)=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify({host:req.headers.host,origin:req.headers.origin}))});
 await new Promise(r=>backend.listen(0,'127.0.0.1',r));
 const probe=createHttpServer();await new Promise(r=>probe.listen(0,'127.0.0.1',r));const port=probe.address().port;await new Promise(r=>probe.close(r));
 const previous=process.env.FORTCAMP_API_TARGET;process.env.FORTCAMP_API_TARGET=`http://127.0.0.1:${backend.address().port}`;
 let vite;
 try{
  vite=await createViteServer({root:fileURLToPath(new URL('../',import.meta.url)),configFile:fileURLToPath(new URL('../vite.config.js',import.meta.url)),server:{port,strictPort:true},logLevel:'silent'});
  await vite.listen(port);
  const data=await new Promise((resolve,reject)=>{const req=request({hostname:'127.0.0.1',port,path:'/api/web/select',method:'POST',headers:{Host:'dev.fortcampgame.fyi',Origin:'https://dev.fortcampgame.fyi','Content-Type':'application/json'}},res=>{let body='';res.on('data',c=>body+=c);res.on('end',()=>resolve({status:res.statusCode,data:JSON.parse(body)}))});req.on('error',reject);req.end('{}')});
  assert.equal(data.status,200);
  assert.deepEqual(data.data,{host:'dev.fortcampgame.fyi',origin:'https://dev.fortcampgame.fyi'});
 }finally{
  if(vite)await vite.close();
  await new Promise(r=>backend.close(r));
  if(previous===undefined)delete process.env.FORTCAMP_API_TARGET;else process.env.FORTCAMP_API_TARGET=previous;
 }
});
