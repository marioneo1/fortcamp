import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({mode}) => {
  const env=loadEnv(mode,'..','FORTCAMP_');
  const publicHost=(env.FORTCAMP_PUBLIC_HOST||'').replace(/^https?:\/\//,'').replace(/\/.*$/,'');
  return {
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      headers: {'Cache-Control': 'no-store, max-age=0'},
      allowedHosts: ['dev.fortcampgame.fyi','.trycloudflare.com','.ts.net',...(publicHost?[publicHost]:[])],
      proxy: {
        '/api': {target: env.FORTCAMP_API_TARGET || 'http://127.0.0.1:8000',changeOrigin:false}
      }
    },
    build: { outDir: 'dist', emptyOutDir: true }
  };
});
