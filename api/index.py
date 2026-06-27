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
      .cta { display: inline-block; margin-top: 18px; padding: 12px 18px; border-radius: 8px; background: var(--accent); color: white; text-decoration: none; font-weight: 700; }
      .cta:hover { background: var(--accent-dark); }
    </style>
  </head>
  <body>
    <main>
      <div class=\"pill\">Vercel • Python • Workflow UI</div>
      <h1>Styora Control</h1>
      <p>This is the live control panel for your Styora workflow. It is connected to the deployed Vercel app and ready for your automation actions.</p>
      <div class=\"panel\">
        <h2>What you can do</h2>
        <p>Start the worker flow, review health status, and trigger the automation endpoints from the deployed app.</p>
        <a class=\"cta\" href=\"/health\">Check health</a>
      </div>
    </main>
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
