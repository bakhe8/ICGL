import http.server
import socketserver
import urllib.request
from urllib.parse import urljoin

TARGET = "http://127.0.0.1:8082"
PORT = 8080


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("--- incoming request ---")
            print(self.command, self.path)
            print("Headers:")
            for k, v in self.headers.items():
                print(f"{k}: {v}")
            target_url = urljoin(TARGET, self.path)
            print("Forwarding to", target_url)
            with urllib.request.urlopen(target_url) as resp:
                data = resp.read()
                self.send_response(resp.getcode())
                for k, v in resp.getheaders():
                    if k.lower() == "transfer-encoding":
                        continue
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            print("Proxy error", e)
            self.send_response(502)
            self.end_headers()
            self.wfile.write(b"Bad Gateway")


if __name__ == "__main__":
    print("Starting logging proxy on port", PORT, "->", TARGET)
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        httpd.serve_forever()
