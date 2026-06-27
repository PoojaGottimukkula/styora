from http.server import BaseHTTPRequestHandler
import json
import os

from utils.workflow_state import read_workflow_state


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        state = read_workflow_state(base_dir=project_root)
        payload = json.dumps(state).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
