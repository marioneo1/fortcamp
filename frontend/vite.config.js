import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({mode}) => {
  const env=loadEnv(mode,'..','FORTCAMP_');
  const autoReload=/^(1|true|yes)$/i.test(env.FORTCAMP_DEV_AUTO_RELOAD||'false');
  const publicHost=(env.FORTCAMP_PUBLIC_HOST||'').replace(/^https?:\/\//,'').replace(/\/.*$/,'');
  return {
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
    preview: { host: '127.0.0.1', strictPort: true },
    build: { outDir: 'dist', emptyOutDir: true }
  };
});
