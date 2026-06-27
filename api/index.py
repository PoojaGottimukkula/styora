from http.server import BaseHTTPRequestHandler


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

        html = """<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Styora Control</title>
    <style>
      :root { color-scheme: light; --bg: #f6f7f9; --panel: #ffffff; --text: #18202a; --muted: #677281; --line: #d9dee7; --accent: #0f766e; --accent-dark: #0b5f59; --shadow: 0 12px 34px rgba(24, 32, 42, 0.08); }
      * { box-sizing: border-box; }
      body { margin: 0; min-height: 100vh; background: var(--bg); color: var(--text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
      main { width: min(960px, calc(100% - 32px)); margin: 0 auto; padding: 40px 0; }
      h1 { margin: 0 0 10px; font-size: 36px; }
      p { margin: 0; color: var(--muted); line-height: 1.6; }
      .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--shadow); padding: 24px; margin-top: 20px; }
      .pill { display: inline-block; margin-top: 10px; padding: 8px 14px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); font-size: 14px; }
      button, .cta { display: inline-block; margin-top: 18px; padding: 12px 18px; border-radius: 8px; background: var(--accent); color: white; text-decoration: none; font-weight: 700; border: 0; cursor: pointer; }
      button:hover, .cta:hover { background: var(--accent-dark); }
      button:disabled { opacity: 0.7; cursor: not-allowed; }
      #result { margin-top: 14px; color: var(--muted); white-space: pre-wrap; }
    </style>
  </head>
  <body>
    <main>
      <div class=\"pill\">Vercel • Python • Workflow UI</div>
      <h1>Styora Control</h1>
      <p>This is the live control panel for your Styora workflow. It sends the start request to the worker endpoint and shows the response.</p>
      <div class=\"panel\">
        <h2>Run the workflow</h2>
        <button id=\"runButton\" type=\"button\">Start workflow</button>
        <div id=\"result\">Click the button to trigger the end-to-end flow.</div>
      </div>
    </main>
    <script>
      const runButton = document.getElementById('runButton');
      const result = document.getElementById('result');
      runButton.addEventListener('click', async () => {
        runButton.disabled = true;
        result.textContent = 'Starting...';
        try {
          const res = await fetch('/api/start', { method: 'POST' });
          const data = await res.json();
          result.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
          result.textContent = 'Could not reach the workflow endpoint. ' + error;
        } finally {
          runButton.disabled = false;
        }
      });
    </script>
  </body>
</html>"""
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
