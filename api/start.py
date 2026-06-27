from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.error
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), ".env"))
except ImportError:
    pass


def json_response(handler, status, body):
    payload = json.dumps(body).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        worker_url = os.getenv("WORKER_START_URL")
        worker_token = os.getenv("WORKER_API_TOKEN")

        if not worker_url:
            json_response(
                self,
                503,
                {
                    "ok": False,
                    "message": "WORKER_START_URL is not configured. Deploy the bot worker, then add its start URL in Vercel environment variables.",
                },
            )
            return

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

                json_response(
                    self,
                    200,
                    {
                        "ok": True,
                        "message": "Bot start request sent to worker.",
                        "worker_status": response.status,
                        "worker": body,
                    },
                )
        except urllib.error.HTTPError as error:
            raw_body = error.read().decode("utf-8")
            json_response(
                self,
                error.code,
                {
                    "ok": False,
                    "message": "Worker rejected the start request.",
                    "worker_response": raw_body,
                },
            )
        except Exception as error:
            json_response(
                self,
                502,
                {
                    "ok": False,
                    "message": f"Could not reach worker: {error}",
                },
            )

    def do_GET(self):
        json_response(
            self,
            405,
            {
                "ok": False,
                "message": "Use POST to start the bot.",
            },
        )
