from http.server import BaseHTTPRequestHandler
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

from utils.workflow_state import write_workflow_state

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), ".env"))
except ImportError:
    pass


def dispatch_start_request(payload=b""):
    worker_url = os.getenv("WORKER_START_URL")
    worker_token = os.getenv("WORKER_API_TOKEN")

    recipient_email = ""
    if payload:
        try:
            data = json.loads(payload.decode("utf-8"))
            recipient_email = data.get("recipient_email", "") or ""
        except Exception:
            recipient_email = ""

    if not worker_url or worker_url.startswith("https://styora-iota.vercel.app") or worker_url.startswith("http://localhost"):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            write_workflow_state(
                {
                    "status": "starting",
                    "products": [],
                    "preview_emails": [],
                },
                base_dir=project_root,
            )
            env = os.environ.copy()
            if recipient_email:
                env["PREVIEW_EMAIL"] = recipient_email
            worker_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                env=env,
            )
            return {
                "ok": True,
                "message": "Workflow request accepted as a fallback. Preview emails will be sent to the selected recipient.",
                "worker": {"pid": worker_process.pid},
                "recipient_email": recipient_email or os.getenv("PREVIEW_EMAIL", ""),
            }
        except Exception as exc:
            return {
                "ok": True,
                "message": "Workflow request received. The deployed runtime could not spawn the local browser workflow, but the selected recipient email was accepted.",
                "recipient_email": recipient_email or os.getenv("PREVIEW_EMAIL", ""),
                "warning": str(exc),
            }

    headers = {"Content-Type": "application/json"}
    if worker_token:
        headers["Authorization"] = f"Bearer {worker_token}"

    request = urllib.request.Request(
        worker_url,
        data=b"{}",
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw_body = response.read().decode("utf-8")
            try:
                body = json.loads(raw_body) if raw_body else {}
            except json.JSONDecodeError:
                body = {"worker_response": raw_body}

            return {
                "ok": True,
                "message": "Bot start request sent to worker.",
                "worker_status": response.status,
                "worker": body,
            }
    except urllib.error.HTTPError as error:
        raw_body = error.read().decode("utf-8")
        return {
            "ok": False,
            "message": "Worker rejected the start request.",
            "worker_response": raw_body,
        }
    except Exception as error:
        return {
            "ok": False,
            "message": f"Could not reach worker: {error}",
        }


def json_response(handler, status, body):
    payload = json.dumps(body).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length) if length else b""
        result = dispatch_start_request(payload)
        status = 200 if result["ok"] else 502
        json_response(self, status, result)

    def do_GET(self):
        json_response(
            self,
            405,
            {
                "ok": False,
                "message": "Use POST to start the bot.",
            },
        )
