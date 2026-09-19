from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import threading
import time
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import cv2
import numpy as np

from cameras import CAMERAS
from happyrobot import API, STATE, run_result, start_run
from traffic import Detector, analyze, freshness

ROOT = Path(__file__).resolve().parent


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        target = urlsplit(newurl)
        if target.scheme != "https" or target.hostname != "informo.madrid.es":
            raise ValueError("Redirección del proveedor no permitida")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def decode_image(body):
    if not body or len(body) > 4_000_000:
        raise ValueError("Imagen vacía o demasiado grande")
    image = cv2.imdecode(np.frombuffer(body, np.uint8), cv2.IMREAD_COLOR)
    if image is None or max(image.shape[:2]) > 4096:
        raise ValueError("Imagen inválida o resolución no admitida")
    return image


class Lab:
    def __init__(self):
        self.detector = Detector()
        self.lock = threading.Lock()
        self.cache = {}
        self.observations = {}
        self.runs = set()
        self.cloud_runs = {}
        self.cloud_lock = threading.Lock()
        self.api = API() if os.environ.get("HAPPYROBOT_API_KEY") else None

    def inspect(self, camera_id, mode):
        if camera_id not in CAMERAS or mode not in ("demo", "live"):
            raise ValueError("Cámara o modo no permitido")
        camera = CAMERAS[camera_id]
        key = (camera_id, mode)
        with self.lock:
            cached = self.cache.get(key)
            if cached and time.monotonic() - cached[0] < 180:
                evidence = cached[1]["evidence"]
                evidence["freshness"] = freshness(evidence["source"].get("source_updated_at"))
                warning = "Fecha de actualización ausente, inválida o antigua"
                if evidence["freshness"] != "recent" and warning not in evidence["warnings"]:
                    evidence["warnings"].append(warning)
                return cached[1]
            downloaded = datetime.now(timezone.utc).isoformat()
            if mode == "demo":
                body = (ROOT / f"samples/cam_{camera_id}.jpg").read_bytes()
                http = json.loads((ROOT / f"samples/cam_{camera_id}.http.json").read_text(encoding="utf-8"))
                modified = http.get("last_modified")
                downloaded = http["descargada_utc"]
                if hashlib.sha256(body).hexdigest() != http["sha256"]:
                    raise ValueError("La muestra no coincide con su evidencia SHA-256")
            else:
                request = urllib.request.Request(camera["url"], headers={"User-Agent": "FlareAI-TrafficLab/1.0", "Accept": "image/jpeg"})
                opener = urllib.request.build_opener(SameHostRedirect())
                with opener.open(request, timeout=20) as response:
                    if response.status != 200 or not response.headers.get("Content-Type", "").startswith("image/"):
                        raise ValueError("El proveedor no ha devuelto una imagen")
                    body = response.read(4_000_001)
                    modified = response.headers.get("Last-Modified")
            try:
                updated = parsedate_to_datetime(modified).isoformat() if modified else None
            except (ValueError, TypeError):
                updated = None
            digest = hashlib.sha256(body).hexdigest()
            metadata = {"camera_id": camera_id, "name": camera["name"], "url": camera["url"],
                        "mode": mode, "downloaded_at": downloaded, "source_updated_at": updated,
                        "sha256": digest, "roi_reference": camera["roi_reference"]}
            result, annotated = analyze(decode_image(body), self.detector, camera["zones"], metadata)
            ok, encoded = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 88])
            if not ok:
                raise ValueError("No se pudo codificar la evidencia")
            observation_id = hashlib.sha256((digest + mode + result["analyzed_at"]).encode()).hexdigest()[:24]
            payload = {"observation_id": observation_id, "evidence": result,
                       "image": "data:image/jpeg;base64," + base64.b64encode(encoded).decode()}
            self.observations[observation_id] = result
            if len(self.observations) > 100:
                self.observations.pop(next(iter(self.observations)))
            self.cache[key] = (time.monotonic(), payload)
            runtime = ROOT / "runtime"
            runtime.mkdir(exist_ok=True)
            (runtime / f"{camera_id}-{mode}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
            (runtime / f"{camera_id}-{mode}.jpg").write_bytes(encoded.tobytes())
            return payload


class Handler(BaseHTTPRequestHandler):
    lab: Lab

    def send(self, value, status=200, mime="application/json; charset=utf-8"):
        body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode() if mime.startswith("application/json") else value
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def trusted_request(self):
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        origin = self.headers.get("Origin")
        return self.headers.get("Host") in hosts and (not origin or origin in {"http://" + h for h in hosts})

    def do_GET(self):
        if not self.trusted_request():
            return self.send({"error": "Host u origen no permitido"}, 403)
        parsed = urlsplit(self.path)
        assets = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
        if parsed.path in assets:
            name, mime = assets[parsed.path]
            return self.send((ROOT / name).read_bytes(), mime=mime)
        if parsed.path == "/api/cameras":
            return self.send({"cameras": list(CAMERAS.values()), "cloud_ready": self.lab.api is not None and STATE.exists()})
        if parsed.path == "/api/run":
            identifier = parse_qs(parsed.query).get("id", [""])[0]
            if identifier not in self.lab.runs or self.lab.api is None:
                return self.send({"error": "Ejecución no iniciada por esta sesión"}, 404)
            try:
                return self.send(run_result(self.lab.api, identifier))
            except (RuntimeError, OSError, ValueError):
                return self.send({"error": "No se ha podido consultar HappyRobot"}, 502)
        self.send({"error": "No encontrado"}, 404)

    def do_POST(self):
        if not self.trusted_request():
            return self.send({"error": "Host u origen no permitido"}, 403)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 2048:
                return self.send({"error": "Petición demasiado grande o vacía"}, 413)
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Se requiere un objeto JSON")
            if self.path == "/api/analyze":
                return self.send(self.lab.inspect(data.get("camera_id"), data.get("mode", "demo")))
            if self.path == "/api/workflow":
                if not self.lab.api or not STATE.exists():
                    return self.send({"error": "Falta desplegar HappyRobot o configurar la clave del servidor"}, 503)
                evidence = self.lab.observations.get(data.get("observation_id"))
                if evidence is None:
                    return self.send({"error": "Primero analiza una cámara"}, 400)
                with self.lab.cloud_lock:
                    observation_id = data["observation_id"]
                    identifier = self.lab.cloud_runs.get(observation_id)
                    if not identifier:
                        result = start_run(self.lab.api, evidence)
                        identifier = result.get("run_id", result.get("id"))
                        if not identifier:
                            raise RuntimeError("HappyRobot no ha devuelto un identificador de ejecución")
                        self.lab.cloud_runs[observation_id] = identifier
                        self.lab.runs.add(identifier)
                return self.send({"run_id": identifier}, 202)
            self.send({"error": "No encontrado"}, 404)
        except (ValueError, TypeError, KeyError) as error:
            self.send({"error": str(error)}, 400)
        except (OSError, RuntimeError, cv2.error) as error:
            self.send({"error": str(error)}, 502)

    def log_message(self, fmt, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description="Traffic Lab: visión local y workflow HappyRobot independiente")
    parser.add_argument("--port", type=int, default=8790)
    parser.add_argument("--analyze", choices=[*CAMERAS, "all"])
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    args = parser.parse_args()
    lab = Lab()
    if args.analyze:
        for identifier in CAMERAS if args.analyze == "all" else [args.analyze]:
            result = lab.inspect(identifier, args.mode)["evidence"]
            print(json.dumps({"camera": identifier, "quality": result["quality"]["status"], "zones": [{k: z[k] for k in ("id", "vehicle_count", "density", "box_coverage_pct")} for z in result["zones"]], "elapsed_ms": result["elapsed_ms"]}))
        return
    Handler.lab = lab
    print(f"Traffic Lab: http://127.0.0.1:{args.port} | HappyRobot: {'configurado' if lab.api else 'sin clave'}", flush=True)
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
