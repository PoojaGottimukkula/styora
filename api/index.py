from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
INDEX_FILE = PUBLIC_DIR / "index.html"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in {"/", "/index.html"}:
            payload = b'{"ok": false, "message": "Not Found"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        html = INDEX_FILE.read_text(encoding="utf-8") if INDEX_FILE.exists() else "<h1>Styora</h1>"
        payload = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        payload = b'{"ok": false, "message": "Method Not Allowed"}'
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
