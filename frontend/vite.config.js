import { defineConfig, loadEnv } from 'vite';
import {readFileSync} from 'node:fs';

export default defineConfig(({mode}) => {
  const env=loadEnv(mode,'..','FORTCAMP_');
  const autoReload=/^(1|true|yes)$/i.test(env.FORTCAMP_DEV_AUTO_RELOAD||'false');
  const publicHost=(env.FORTCAMP_PUBLIC_HOST||'').replace(/^https?:\/\//,'').replace(/\/.*$/,'');
  return {
    plugins: autoReload ? [] : [{name:'fortcamp-steady-play-client',configureServer(server){
      const client=readFileSync(new URL('./src/steady-dev-client.js',import.meta.url),'utf8');
      server.middlewares.use((req,res,next)=>{
        if(req.url?.split('?')[0]!=='/@vite/client')return next();
        res.setHeader('Content-Type','application/javascript');res.setHeader('Cache-Control','no-store');res.end(client);
      });
    }}],
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      hmr: autoReload,
      watch: autoReload ? {} : null,
      headers: {'Cache-Control': 'no-store, max-age=0'},
      allowedHosts: ['dev.fortcampgame.fyi','.trycloudflare.com','.ts.net',...(publicHost?[publicHost]:[])],
      proxy: {
        '/api': {target: env.FORTCAMP_API_TARGET || 'http://127.0.0.1:8000',changeOrigin:false}
      }
    },
    build: { outDir: 'dist', emptyOutDir: true }
  };
});
