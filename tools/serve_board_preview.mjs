// Local-only fixture preview with Vite module resolution for Pixi dependencies.
import {createServer} from '../frontend/node_modules/vite/dist/node/index.js';
import {fileURLToPath} from 'node:url';
import configure from '../frontend/vite.config.js';
const root=fileURLToPath(new URL('../',import.meta.url));
const server=await createServer({configFile:false,plugins:configure({mode:'development'}).plugins,root,publicDir:'frontend/public',cacheDir:'frontend/node_modules/.vite-board-preview',optimizeDeps:{force:true,entries:['staging-ui/mission-board-v1/board-preview.html']},server:{hmr:false,watch:null,host:'127.0.0.1',port:8766,strictPort:true},logLevel:'warn'});
await server.listen();console.log('Board preview: http://127.0.0.1:8766/staging-ui/mission-board-v1/board-preview.html');
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,async()=>{await server.close();process.exit(0)});
