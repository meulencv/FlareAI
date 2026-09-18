#!/usr/bin/env python3
"""Servidor mínimo para la web de voz con HappyRobot.

- Sirve index.html.
- POST /token: pide un token LiveKit a HappyRobot y lo devuelve al navegador.
  La API key nunca llega al frontend.

Uso:
    export HAPPYROBOT_API_KEY=sk_live_...
    python3 server.py
"""

import json
import os
import sys
import urllib.error
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

API_BASE = os.environ.get("HAPPYROBOT_API_BASE", "https://platform.eu.happyrobot.ai/api/v2")
WORKFLOW_ID = os.environ.get("HAPPYROBOT_WORKFLOW_ID", "01a0b665-2a84-725f-a714-947e427ea6d2")
API_KEY = os.environ.get("HAPPYROBOT_API_KEY")
PORT = int(os.environ.get("PORT", "8000"))


class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/token":
            self.send_error(404)
            return

        req = urllib.request.Request(
            f"{API_BASE}/voice/tokens/",
            data=json.dumps({"workflow_id": WORKFLOW_ID}).encode(),
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                body, status = r.read(), r.status
        except urllib.error.HTTPError as e:
            body, status = e.read(), e.code

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    if not API_KEY:
        sys.exit("Falta HAPPYROBOT_API_KEY en el entorno")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"http://localhost:{PORT}")
    HTTPServer(("", PORT), Handler).serve_forever()
