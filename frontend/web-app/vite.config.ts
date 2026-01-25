import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'node:url';
import type { Plugin } from 'vite';
import { defineConfig } from 'vite';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const landingMiddleware = (): Plugin => ({
  name: 'serve-public-landing',
  configureServer(server) {
    const publicDir = path.resolve(__dirname, 'public');
    const landingIndex = path.join(publicDir, 'index.html');
    const landingDir = path.join(publicDir, 'landing');
    server.middlewares.use((req, res, next) => {
      if (!req?.url) return next();
      const urlPath = req.url.split('?')[0];
      if (urlPath === '/' || urlPath === '/index.html') {
        if (fs.existsSync(landingIndex)) {
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
          fs.createReadStream(landingIndex).pipe(res);
          return;
        }
      }
      if (urlPath.startsWith('/landing/')) {
        const filePath = path.join(landingDir, urlPath.replace('/landing/', ''));
        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
          const ext = path.extname(filePath);
          const mime =
            {
              '.css': 'text/css',
              '.js': 'application/javascript',
              '.html': 'text/html',
              '.svg': 'image/svg+xml',
            }[ext] || 'application/octet-stream';
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
      '@shared-ui': path.resolve(__dirname, '../shared-ui'),
      '@web-ui': path.resolve(__dirname, '../shared-ui/web-app'),
      '@web-src': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 8080,
    host: true,
    proxy: {
      '/docs': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/redoc': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/status': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/observability': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/patterns': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/mind': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      }
    }
  },
});
