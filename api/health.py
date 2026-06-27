from http.server import BaseHTTPRequestHandler
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), ".env"))
except ImportError:
    pass


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = {
            "ok": True,
            "service": "styora",
            "runtime": "vercel",
            "email_configured": bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD")),
            "preview_email_configured": bool(os.getenv("PREVIEW_EMAIL")),
            "worker_start_configured": bool(os.getenv("WORKER_START_URL")),
        }

        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
