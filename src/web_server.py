from __future__ import annotations

import threading
import time
from flask import Flask, jsonify, request, redirect, url_for, Response

from . import config
from .light_controller import make_controller
from .weather_service import WeatherService


app = Flask(__name__)

controller = make_controller()
controller.setup()
service = WeatherService(controller)

_active = False
_lock = threading.Lock()


def _auth_ok() -> bool:
    # If no creds configured, allow
    if not (config.AUTH_USERNAME and config.AUTH_PASSWORD):
        return True
    auth = request.authorization
    return bool(auth and auth.username == config.AUTH_USERNAME and auth.password == config.AUTH_PASSWORD)


def _require_auth():
    if _auth_ok():
        return None
    return Response("Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Weather Board"'})


def _worker():
    global _active
    while True:
        time.sleep(1)
        with _lock:
            if not _active:
                continue
        try:
            service.fetch_and_update()
        except Exception as e:
            print("Update error:", e)
        time.sleep(max(1, config.REFRESH_SECONDS))


thread = threading.Thread(target=_worker, daemon=True)
thread.start()


@app.route("/")
def index() -> Response:
    guard = _require_auth()
    if guard is not None:
        return guard
    html = f"""
<!doctype html>
<html>
  <head>
    <meta name=viewport content="width=device-width, initial-scale=1" />
    <title>Weather Board</title>
    <style>
      body {{ font-family: system-ui, Arial, sans-serif; margin: 2rem; text-align: center; }}
      h1 {{ margin-bottom: 0.25rem; }}
      .muted {{ color: #666; margin-top: 0; }}
      button {{ padding: 1rem 1.5rem; font-size: 1.1rem; margin: 0.5rem; border-radius: 10px; border: 0; cursor: pointer; }}
      .start {{ background: #2ea44f; color: white; }}
      .stop {{ background: #d73a49; color: white; }}
      .refresh {{ background: #0366d6; color: white; }}
      .row {{ margin-top: 1rem; }}
    </style>
  </head>
  <body>
    <h1>Weather Board Control</h1>
    <p class="muted">Orange Pi 5 — Refresh every {config.REFRESH_SECONDS//60} min</p>
    <div class="row">
      <button class="start" onclick="fetch('/start', {{method:'POST'}}).then(()=>location.reload())">Start</button>
      <button class="stop" onclick="fetch('/stop', {{method:'POST'}}).then(()=>location.reload())">Stop</button>
      <button class="refresh" onclick="fetch('/refresh', {{method:'POST'}}).then(()=>location.reload())">Refresh Now</button>
    </div>
  </body>
 </html>
    """
    return Response(html, mimetype="text/html")


@app.post("/start")
def start():
    guard = _require_auth()
    if guard is not None:
        return guard
    global _active
    with _lock:
        _active = True
    return jsonify({"active": _active})


@app.post("/stop")
def stop():
    guard = _require_auth()
    if guard is not None:
        return guard
    global _active
    with _lock:
        _active = False
    controller.clear()
    return jsonify({"active": _active})


@app.post("/refresh")
def refresh():
    guard = _require_auth()
    if guard is not None:
        return guard
    try:
        summary = service.fetch_and_update()
        return jsonify({"ok": True, **summary})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


def run():
    # Startup flash indicates whether API key is present
    if config.CHECKWX_API_KEY:
        controller.flash((20, 0, 0), seconds=0.2, repeats=2)  # Green
    else:
        controller.flash((0, 25, 0), seconds=0.2, repeats=2)  # Red
    app.run(host=config.HOST or "0.0.0.0", port=int(config.PORT or 8080))
