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
    // ensure log dir exists
    try {
      const logDir = path.resolve(__dirname, '..', '..', 'logs');
      fs.mkdirSync(logDir, { recursive: true });
    } catch (e) {
      // ignore
    }
    const LOGFILE = path.resolve(__dirname, '..', '..', 'logs', 'vite_requests.log');
    // Attach a low-level HTTP request logger; if `server.httpServer` is
    // not yet available, poll briefly until it's present. This ensures we
    // capture raw incoming URLs regardless of Vite internals timing.
    (function attachHttpLogger(retries = 10) {
      try {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        const srv = server.httpServer;
        if (srv && typeof srv.on === 'function') {
          srv.on('request', (req: any) => {
            try {
              const line = `[http-request] url=${req.url} pid=${process.pid} ts=${Date.now()}${os.EOL}`;
              try { fs.appendFileSync(LOGFILE, line); } catch (e) { /* ignore */ }
              // eslint-disable-next-line no-console
              console.log(line.trim());
            } catch (e) { }
          });
          return;
        }
      } catch (e) {
        // fallthrough to retry
      }
      if (retries > 0) {
        setTimeout(() => attachHttpLogger(retries - 1), 50);
      }
    })();
    const publicDir = path.resolve(__dirname, 'public');
    const landingIndex = path.join(publicDir, 'index.html');
    const landingDir = path.join(publicDir, 'landing');
    server.middlewares.use((req, res, next) => {
      if (!req?.url) return next();
      const urlPath = req.url.split('?')[0];
      // Debug log to help diagnose dev server path handling
      try {
        const line = `[vite-middleware] incoming request urlPath=${urlPath} ts=${Date.now()}${os.EOL}`;
        try { fs.appendFileSync(LOGFILE, line); } catch (e) { }
        // eslint-disable-next-line no-console
        console.log(line.trim());
      } catch (e) {
        // ignore
      }

      // Serve the public landing page at root
      if (urlPath === '/' || urlPath === '/index.html') {
        if (fs.existsSync(landingIndex)) {
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
          fs.createReadStream(landingIndex).pipe(res);
          return;
        }
      }

      // Serve the SPA entry at /app/ (dev server) to support client-side routing
      // Accept any path under /app (e.g. /app/, /app/dashboard, /app/agents/123)
      // Match any path containing the `/app` application base so dev server
      // will serve the SPA entry regardless of subtle URL rewriting.
      if (
        urlPath === '/app' ||
        urlPath === '/app/' ||
        urlPath === '/app/index.html' ||
        urlPath.startsWith('/app/') ||
        urlPath.includes('/app')
      ) {
        const appIndex = path.join(publicDir, 'app', 'index.html');
        const fileToServe = fs.existsSync(appIndex) ? appIndex : landingIndex;
        if (fs.existsSync(fileToServe)) {
          res.setHeader('Content-Type', 'text/html; charset=utf-8');
          fs.createReadStream(fileToServe).pipe(res);
          return;
        }
      }

      // Serve specific landing static files
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

    // Simple redirect: if dev requests `/app` paths, redirect to `/` where
    // the dev server serves the SPA entry. This is a pragmatic fallback
    // while the more specific middleware is diagnosed.
    // NOTE: removed automatic redirect from `/app*` to `/` to allow the
    // SPA dev-serving middleware above to handle `/app/*` routes directly.

    // Move this middleware to the front of the stack so it runs before
    // Vite's static file handler which may otherwise return a 404 early.
    try {
      // access underlying stack and move the last-registered layer to front
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      const stack = server.middlewares.stack;
      if (Array.isArray(stack) && stack.length > 0) {
        const layer = stack.pop();
        if (layer) {
          stack.unshift(layer);
        }
      }

      try {
        // Create and insert a direct logging/serving layer at the very
        // front of the stack to guarantee we see requests during dev.
        const myLayer = {
          name: 'serve-public-landing-direct',
          route: '',
          handle: (req: any, _res: any, next: any) => {
            try {
              const line = `[landing-direct] raw url=${req.url} ts=${Date.now()}${os.EOL}`;
              try { fs.appendFileSync(LOGFILE, line); } catch (e) { }
              // eslint-disable-next-line no-console
              console.log(line.trim());
            } catch (e) { }
            next();
          },
        };
        if (Array.isArray(stack)) {
          stack.unshift(myLayer);
        }
      } catch (e) {
        // ignore
      }

      try {
        // Log stack contents to help diagnose ordering issues
        // eslint-disable-next-line no-console
        console.log('[vite-middleware] middleware stack length=', Array.isArray(stack) ? stack.length : 'unknown');
        if (Array.isArray(stack)) {
          const names = stack.slice(0, 8).map((s: any, i: number) => s?.name || s?.handle?.name || `layer-${i}`);
          // eslint-disable-next-line no-console
          console.log('[vite-middleware] top layers=', names);
        }
      } catch (e) { }
    } catch (e) {
      // ignore if internal structure differs across Vite versions
    }
  },
});

const base = process.env.NODE_ENV === 'production' ? '/app/' : '/';

export default defineConfig({
  // Ensure the SPA-serving middleware runs before other plugins so
  // it can intercept requests to `/app/*` before Vite's static handler.
  plugins: [landingMiddleware(), react()],
  // Use production base `/app/` when building for production, otherwise
  // use `/` for local development so dev server routes work naturally.
  base,
  resolve: {
    alias: {
      '@shared-ui': path.resolve(__dirname, './src/shared'),
      '@web-ui': path.resolve(__dirname, './src/shared'),
      '@web-src': path.resolve(__dirname, './src'),
      '@icgl/ui-components': path.resolve(__dirname, './src/stubs/ui-components.tsx'),
    },
  },
  server: {
    port: 8082,
    host: '127.0.0.1',
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
