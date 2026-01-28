import react from '@vitejs/plugin-react';
import fs from 'fs';
import { fileURLToPath } from 'node:url';
import os from 'os';
import path from 'path';
import type { Plugin } from 'vite';
import { defineConfig } from 'vite';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const landingMiddleware = (): Plugin => ({
  name: 'serve-public-landing',
  configureServer(server) {
    try {
      const logDir = path.resolve(__dirname, '..', '..', 'logs');
      fs.mkdirSync(logDir, { recursive: true });
    } catch { /* ignore */ }
    const LOGFILE = path.resolve(__dirname, '..', '..', 'logs', 'vite_requests.log');
    (function attachHttpLogger(retries = 10) {
      try {
        const srv = server.httpServer;
        // @ts-ignore
        if (srv && typeof srv.on === 'function') {
          srv.on('request', (req: any) => {
            try {
              const line = `[http-request] url=${req.url} pid=${process.pid} ts=${Date.now()}${os.EOL}`;
              try { fs.appendFileSync(LOGFILE, line); } catch { /* ignore */ }
            } catch { /* ignore */ }
          });
          return;
        }
      } catch { /* fallthrough */ }
      if (retries > 0) {
        setTimeout(() => attachHttpLogger(retries - 1), 50);
      }
    })();
    const publicDir = path.resolve(__dirname, 'public');
    const landingIndex = path.join(publicDir, 'index.html');
    const landingDir = path.join(publicDir, 'landing-static');
    server.middlewares.use(async (req: any, res: any, next: any) => {
      if (!req?.url) return next();
      const urlPath = req.url.split('?')[0];
      if (urlPath === '/' || urlPath === '/index.html') {
        if (fs.existsSync(landingIndex)) {
          try {
            const html = fs.readFileSync(landingIndex, 'utf-8');
            const transformedHtml = await server.transformIndexHtml(req.url, html);
            res.setHeader('Content-Type', 'text/html; charset=utf-8');
            res.end(transformedHtml);
            return;
          } catch (e) {
            console.error('Error transforming landing index:', e);
          }
        }
      }
      if (urlPath.startsWith('/landing/') || urlPath.startsWith('/app/landing/')) {
        const landingSubPath = urlPath.replace(/^\/(app\/)?landing\//, '');
        const filePath = path.join(landingDir, landingSubPath);
        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
          const ext = path.extname(filePath);
          const mime = { '.css': 'text/css', '.js': 'application/javascript', '.html': 'text/html', '.svg': 'image/svg+xml' }[ext] || 'application/octet-stream';
          res.setHeader('Content-Type', mime);
          fs.createReadStream(filePath).pipe(res);
          return;
        }
      }
      next();
    });
  },
});

export default defineConfig({
  plugins: [react(), landingMiddleware()],
  base: '/app/',
  resolve: {
    alias: {
      '@shared-ui': path.resolve(__dirname, './src/shared/ui'),
      '@shared-layout': path.resolve(__dirname, './src/shared/layout'),
      '@shared-features': path.resolve(__dirname, './src/shared/features'),
      '@web-src': path.resolve(__dirname, './src'),
    },
  },
  build: {
    minify: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],
          'vendor-tanstack': ['@tanstack/react-router', '@tanstack/react-query'],
          'vendor-icons': ['lucide-react']
        }
      }
    }
  },
  server: {
    port: 8080,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/ws': { target: 'ws://127.0.0.1:8000', ws: true, changeOrigin: true }
    }
  }
});
