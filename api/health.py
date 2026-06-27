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
        email_user = os.getenv("EMAIL_USER") or os.getenv("SMTP_USERNAME") or ""
        email_password = os.getenv("EMAIL_PASSWORD") or os.getenv("SMTP_PASSWORD") or ""
        preview_email = os.getenv("PREVIEW_EMAIL") or os.getenv("EMAIL_TO") or ""
        worker_url = os.getenv("WORKER_START_URL") or os.getenv("WORKER_URL") or ""

        body = {
            "ok": True,
            "service": "styora",
            "runtime": "vercel",
            "email_configured": bool(email_user and email_password),
            "preview_email_configured": bool(preview_email),
            "worker_start_configured": bool(worker_url),
        }

        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
