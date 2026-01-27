#!/usr/bin/env python3
"""
Serve `frontend/web-app/dist` at http://127.0.0.1:8081 and map the URL prefix
`/app/` to the dist directory so asset paths produced with base `/app/` work.
"""

import http.server
import mimetypes
import os
import socketserver
import urllib.parse

PORT = 8081
HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.normpath(os.path.join(HERE, "..", "frontend", "web-app", "dist"))


class AppRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        # Redirect root to /app/
        if path == "/" or path == "":
            self.send_response(302)
            self.send_header("Location", "/app/")
            self.end_headers()
            return

        if path.startswith("/app"):
            rel = path[len("/app") :]
            if rel == "" or rel == "/":
                rel = "/index.html"
            # Prevent path traversal
            rel = os.path.normpath(rel).lstrip(os.sep)
            # Try candidates: dist/<rel>, dist/app/<rel>
            candidates = [
                os.path.join(DIST, rel),
                os.path.join(DIST, "app", rel.lstrip(os.sep)),
            ]
            fs_path = None
            for cand in candidates:
                if os.path.isdir(cand):
                    cand = os.path.join(cand, "index.html")
                if os.path.exists(cand) and os.path.isfile(cand):
                    fs_path = cand
                    break

            if fs_path:
                self.send_response(200)
                ctype, _ = mimetypes.guess_type(fs_path)
                if not ctype:
                    ctype = "application/octet-stream"
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(os.path.getsize(fs_path)))
                self.end_headers()
                with open(fs_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                # SPA fallback: serve index.html for any unknown route under /app
                index_candidates = [
                    os.path.join(DIST, "index.html"),
                    os.path.join(DIST, "app", "index.html"),
                ]
                for idx in index_candidates:
                    if os.path.exists(idx) and os.path.isfile(idx):
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html; charset=utf-8")
                        self.send_header("Content-Length", str(os.path.getsize(idx)))
                        self.end_headers()
                        with open(idx, "rb") as f:
                            self.wfile.write(f.read())
                        return
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not Found")
                return

        # For any other path, return 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")
        # Try to serve common files at root (favicon, robots, etc.) from dist
        if path == "/favicon.ico" or path == "/robots.txt":
            candidates = [
                os.path.join(DIST, path.lstrip("/")),
                os.path.join(DIST, "assets", path.lstrip("/")),
                os.path.join(DIST, "app", path.lstrip("/")),
                os.path.join(DIST, "app", "assets", path.lstrip("/")),
            ]
            for cand in candidates:
                if os.path.exists(cand) and os.path.isfile(cand):
                    self.send_response(200)
                    ctype, _ = mimetypes.guess_type(cand)
                    if not ctype:
                        ctype = "application/octet-stream"
                    self.send_header("Content-Type", ctype)
                    self.send_header("Content-Length", str(os.path.getsize(cand)))
                    self.end_headers()
                    with open(cand, "rb") as f:
                        self.wfile.write(f.read())
                    return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")


if __name__ == "__main__":
    if not os.path.isdir(DIST):
        print("Error: dist directory not found at", DIST)
        raise SystemExit(1)
    print("Serving", DIST, "at http://127.0.0.1:%d/app/" % PORT)
    handler = AppRequestHandler
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down")
            httpd.server_close()
