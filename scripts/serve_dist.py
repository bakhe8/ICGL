import http.server
import os
import socketserver
from urllib.parse import urlparse

ROOT = os.path.join(os.path.dirname(__file__), "..", "frontend", "web-app", "dist")
PORT = 8081


class AppHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # strip query
        path = urlparse(path).path
        # if path starts with /app, remove the prefix
        if path.startswith("/app"):
            new_path = path[len("/app") :]
            if new_path == "" or new_path == "/":
                new_path = "/index.html"
        else:
            new_path = path
        full_path = os.path.join(ROOT, new_path.lstrip("/"))
        return full_path


if __name__ == "__main__":
    os.chdir(ROOT)
    with socketserver.TCPServer(("", PORT), AppHandler) as httpd:
        print(f"Serving dist at http://127.0.0.1:{PORT}/app/")
        httpd.serve_forever()
