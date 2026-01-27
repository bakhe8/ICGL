#!/usr/bin/env python3
"""Simple HTTP proxy: listen on 127.0.0.1:8001 and forward to 127.0.0.1:8000.

This is a lightweight dev helper to make services expecting :8001 reach the
actual backend on :8000. It forwards method, path, headers and body.

Limitations: does not proxy WebSockets; intended for HTTP API endpoints only.
"""

import http.server
import socketserver
import sys
import urllib.error
import urllib.request

TARGET = "http://127.0.0.1:8000"


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def _proxy(self):
        url = TARGET + self.path
        method = self.command
        headers = {k: v for k, v in self.headers.items()}
        data = None
        if "content-length" in self.headers:
            length = int(self.headers.get("content-length", "0"))
            data = self.rfile.read(length)

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                self.send_response(resp.getcode())
                for key, val in resp.getheaders():
                    # Skip hop-by-hop headers
                    if key.lower() in (
                        "transfer-encoding",
                        "connection",
                        "keep-alive",
                        "proxy-authenticate",
                        "proxy-authorization",
                        "te",
                        "trailers",
                        "upgrade",
                    ):
                        continue
                    self.send_header(key, val)
                self.end_headers()
                body = resp.read()
                if body:
                    self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for key, val in e.headers.items():
                self.send_header(key, val)
            self.end_headers()
            try:
                self.wfile.write(e.read())
            except Exception:
                pass
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))

    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_PATCH(self):
        self._proxy()

    def log_message(self, format, *args):
        # Keep logs concise
        sys.stdout.write(
            "[proxy] %s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args)
        )


def run():
    with socketserver.TCPServer(("127.0.0.1", 8001), ProxyHandler) as httpd:
        print("Proxy running: 127.0.0.1:8001 -> 127.0.0.1:8000")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run()
