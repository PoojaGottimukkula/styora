import os
import subprocess
import sys
from flask import Flask, jsonify, request, send_from_directory

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), ".env"))
except ImportError:
    pass

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


app = Flask(__name__)
bot_process = None


def authorized():
    expected_token = os.getenv("WORKER_API_TOKEN")
    if not expected_token:
        return True

    header = request.headers.get("Authorization", "")
    return header == f"Bearer {expected_token}"


def bot_running():
    return bot_process is not None and bot_process.poll() is None


@app.get("/")
def root():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.get("/<path:path>")
def public_files(path):
    public_path = os.path.join(PUBLIC_DIR, path)
    if os.path.exists(public_path):
        return send_from_directory(PUBLIC_DIR, path)
    return jsonify({"ok": False, "message": "Not Found"}), 404


@app.get("/health")
def health():
    return jsonify(
        {
            "ok": True,
            "bot_running": bot_running(),
            "email_configured": bool(os.getenv("EMAIL_USER") and os.getenv("EMAIL_PASSWORD")),
            "preview_email_configured": bool(os.getenv("PREVIEW_EMAIL")),
        }
    )


@app.post("/api/start")
def api_start():
    return start()


@app.post("/start")
def start():
    global bot_process

    if not authorized():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    if bot_running():
        return jsonify({"ok": True, "message": "Bot is already running."})

    bot_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    return jsonify(
        {
            "ok": True,
            "message": "Bot started.",
            "pid": bot_process.pid,
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
