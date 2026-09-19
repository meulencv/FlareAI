from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import UUID

ROOT = Path(__file__).resolve().parent
API_BASE = "https://platform.eu.happyrobot.ai/api/v2"
HOOK_BASE = "https://workflows.platform.eu.happyrobot.ai/hooks"
SENDER = "+15304471317"
STATE_PATH = ROOT / "sms-workflow.json"


class HappyRobotError(RuntimeError):
    def __init__(self, status: int, detail: str):
        self.status = status
        super().__init__(f"HappyRobot HTTP {status}: {detail}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def load_api_key() -> str:
    key = os.environ.get("HAPPYROBOT_API_KEY", "").strip()
    if not key:
        path = ROOT / "versión-anterior" / ".env"
        if path.exists():
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                name, separator, value = line.strip().removeprefix("export ").partition("=")
                if separator and name.strip() == "HAPPYROBOT_API_KEY":
                    key = value.strip().strip("\"'")
                    break
    if not key:
        raise RuntimeError("Falta HAPPYROBOT_API_KEY en el entorno o en versión-anterior/.env.")
    return key


class HappyRobotClient:
    def __init__(self, api_key: str | None = None, hook_key: str | None = None):
        self.api_key = api_key if api_key is not None else load_api_key()
        self.hook_key = hook_key if hook_key is not None else os.environ.get("HAPPYROBOT_SMS_HOOK_KEY", "").strip()
        self.opener = urllib.request.build_opener(NoRedirect)

    def exchange(self, request: urllib.request.Request) -> Any:
        try:
            with self.opener.open(request, timeout=30) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                data = json.loads(raw)
                detail = str(data.get("message") or data.get("error") or data.get("title") or "Petición rechazada")
            except (ValueError, AttributeError):
                detail = "Petición rechazada"
            for key in (self.api_key, self.hook_key):
                if key:
                    detail = detail.replace(key, "[redacted]")
            raise HappyRobotError(exc.code, detail) from None
        return json.loads(raw) if raw else {}

    def request(self, method: str, path: str, body: Any = None) -> Any:
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("Ruta API inválida.")
        if body is None and method != "GET":
            body = {}
        request = urllib.request.Request(
            API_BASE + path,
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json", "Accept": "application/json"},
        )
        return self.exchange(request)

    def trigger_hook(self, slug: str, payload: dict) -> Any:
        if not self.hook_key or not re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
            raise ValueError("Falta configurar el webhook autenticado.")
        request = urllib.request.Request(
            f"{HOOK_BASE}/{slug}", data=json.dumps(payload).encode(), method="POST",
            headers={"X-API-Key": self.hook_key, "Content-Type": "application/json", "Accept": "application/json"},
        )
        return self.exchange(request)


def inspect_account(client: HappyRobotClient) -> None:
    integrations = client.request("GET", "/integrations/")
    items = integrations.get("data", integrations) if isinstance(integrations, dict) else integrations
    selected = [{key: item.get(key) for key in ("id", "name")} for item in items if any(
        word in str(item.get("name", "")).lower() for word in ("text", "sms")
    )]
    numbers = client.request("GET", "/phone-numbers/")
    items = numbers.get("data", numbers) if isinstance(numbers, dict) else numbers
    selected_numbers = [{key: item.get(key) for key in ("id", "name", "number", "type")}
                        for item in items if item.get("number") == SENDER]
    print(json.dumps({"integrations": selected, "phone_numbers": selected_numbers}, indent=2))


def validate_sms(body: Any) -> tuple[str, str, str]:
    if not isinstance(body, dict):
        raise ValueError("Se esperaba un objeto JSON.")
    if body.get("confirmed") is not True:
        raise ValueError("Confirma que quieres enviar un SMS real a ese destinatario.")
    to, message = body.get("to"), body.get("message")
    if not isinstance(to, str) or not isinstance(message, str):
        raise ValueError("Introduce un destinatario y un mensaje.")
    to = re.sub(r"[\s()-]", "", to)
    message = message.strip()
    if not re.fullmatch(r"\+[1-9][0-9]{7,14}", to) or to == SENDER:
        raise ValueError("Usa un móvil con prefijo internacional, distinto del remitente.")
    if not message or len(message) > 480 or "\x00" in message:
        raise ValueError("El mensaje debe tener entre 1 y 480 caracteres, sin caracteres nulos.")
    try:
        message.encode("utf-8")
        request_id = str(UUID(str(body.get("request_id", ""))))
    except (ValueError, UnicodeError):
        raise ValueError("Mensaje o identificador de petición inválido; recarga la página.") from None
    return to, message, request_id


class SMSService:
    def __init__(self, client: HappyRobotClient | None, workflow_id: str, hook_slug: str = ""):
        self.client = client
        self.workflow_id = workflow_id
        self.hook_slug = hook_slug
        self.csrf_token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.requests: dict[str, tuple[str, tuple[int, dict]]] = {}
        self.runs: set[str] = set()
        self.last_send = float("-inf")

    def config(self) -> dict:
        reason = ""
        if not self.client or not self.workflow_id:
            reason = "Falta configurar la API key o publicar el workflow SMS."
        elif self.hook_slug and not self.client.hook_key:
            reason = "Workflow publicado. Pendiente: configurar HAPPYROBOT_SMS_HOOK_KEY con una clave válida del webhook."
        return {"ready": not reason, "sender": SENDER, "workflow_id": self.workflow_id,
                "csrf_token": self.csrf_token, "reason": reason}

    def parse_message(self, body: Any) -> tuple[str, str, str]:
        return validate_sms(body)

    def workflow_payload(self, to: str, message: str) -> dict:
        return {"to": to, "message": message}

    def send(self, body: Any) -> tuple[int, dict]:
        to, message, request_id = self.parse_message(body)
        if not self.config()["ready"] or not self.client:
            return 503, {"error": self.config()["reason"]}
        digest = hashlib.sha256(json.dumps([to, message]).encode()).hexdigest()
        with self.lock:
            if request_id in self.requests:
                previous_digest, result = self.requests[request_id]
                if previous_digest != digest:
                    return 409, {"error": "Esta petición ya se usó con otro mensaje."}
                return result
            if len(self.requests) >= 100:
                return 429, {"error": "Límite de 100 pruebas por sesión. Reinicia el servidor para continuar."}
            if time.monotonic() - self.last_send < 10:
                return 429, {"error": "Espera 10 segundos entre envíos."}
            self.last_send = time.monotonic()
            try:
                payload = self.workflow_payload(to, message)
                if self.hook_slug:
                    response = self.client.trigger_hook(self.hook_slug, payload)
                else:
                    response = self.client.request("POST", f"/workflows/{self.workflow_id}/runs", {
                        "environment": "production", "payload": payload,
                    })
                data = response.get("data", response)
                run_id = data.get("run_id") or data.get("id")
                if not isinstance(run_id, str) or not run_id:
                    raise ValueError("Respuesta sin identificador de ejecución.")
                self.runs.add(run_id)
                result = (202, {"run_id": run_id, "status": "accepted"})
            except (HappyRobotError, OSError, ValueError, AttributeError):
                result = (502, {"error": "No se pudo confirmar la petición. Comprueba las ejecuciones "
                               "en HappyRobot antes de repetir; el mensaje podría haberse procesado."})
            self.requests[request_id] = (digest, result)
            return result

    def run_status(self, run_id: str) -> tuple[int, dict]:
        with self.lock:
            known = run_id in self.runs
        if not known or not self.client:
            return 404, {"error": "Ejecución desconocida en esta sesión local."}
        try:
            response = self.client.request("GET", f"/runs/{urllib.parse.quote(run_id, safe='')}")
            data = response.get("data", response)
            if data.get("workflow_id") != self.workflow_id:
                return 404, {"error": "La ejecución no corresponde a este workflow."}
            result = {"run_id": run_id, "status": data.get("status", "unknown")}
            if result["status"] == "failed":
                result.update(self.failure_detail(run_id))
            return 200, result
        except (HappyRobotError, OSError, ValueError, AttributeError):
            return 502, {"error": "No se pudo consultar el estado. No vuelvas a enviar: revisa HappyRobot."}

    def failure_detail(self, run_id: str) -> dict:
        fallback = {"error": "Revisa el nodo que falló en HappyRobot antes de repetir el envío."}
        if not self.client:
            return fallback
        try:
            response = self.client.request("GET", f"/runs/{urllib.parse.quote(run_id, safe='')}/nodes")
            nodes = response.get("data", []) if isinstance(response, dict) else response
            if not isinstance(nodes, list):
                return fallback
            hints = {
                "40013": "Telnyx 40013: el proveedor rechaza el número remitente. Revisa su formato y habilitación para SMS.",
                "40305": "Telnyx 40305: el remitente no está asociado al perfil de mensajería usado. Hay que corregir esa asociación antes de repetir.",
            }
            for node in nodes:
                if node.get("status") != "failed":
                    continue
                error = str(node.get("error") or "")
                code = re.search(r'"code"\s*:\s*"(\d{5})"', error)
                if error.startswith("Telnyx returned ") and code and code[1] in hints:
                    return {"provider_error_code": code[1], "error": hints[code[1]]}
        except (HappyRobotError, OSError, ValueError, AttributeError):
            return fallback
        return fallback


def make_server(service: SMSService, port: int = 8091,
                assets: dict[str, tuple[str, str]] | None = None,
                actions: dict[str, Any] | None = None) -> ThreadingHTTPServer:
    static_routes = assets or {"/": ("sms.html", "text/html; charset=utf-8"),
                              "/sms.js": ("sms.js", "text/javascript; charset=utf-8"),
                              "/sms.css": ("sms.css", "text/css; charset=utf-8")}
    post_routes = {"/api/send": service.send, **(actions or {})}

    class Handler(BaseHTTPRequestHandler):
        server: ThreadingHTTPServer

        def log_message(self, format, *args):
            pass

        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def respond(self, status: int, body: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; "
                             "style-src 'self'; connect-src 'self'; frame-ancestors 'none'; "
                             "base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)

        def json_response(self, status: int, body: dict):
            self.respond(status, json.dumps(body, ensure_ascii=False).encode(), "application/json; charset=utf-8")

        def allowed(self) -> bool:
            hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            if host not in hosts or (origin is not None and origin != f"http://{host}"):
                self.json_response(403, {"error": "Solo se permite acceso desde esta página local."})
                return False
            return True

        def do_GET(self):
            if not self.allowed():
                return
            path = urllib.parse.urlsplit(self.path).path
            if path in static_routes:
                filename, mime = static_routes[path]
                self.respond(200, (ROOT / "static" / filename).read_bytes(), mime)
            elif path == "/api/config":
                self.json_response(200, service.config())
            elif path.startswith("/api/runs/"):
                self.json_response(*service.run_status(path.removeprefix("/api/runs/")))
            else:
                self.json_response(404, {"error": "No encontrado."})

        def do_POST(self):
            if not self.allowed():
                return
            action = post_routes.get(self.path)
            if action is None:
                self.json_response(404, {"error": "No encontrado."})
                return
            token = self.headers.get("X-CSRF-Token", "")
            if not secrets.compare_digest(token.encode(), service.csrf_token.encode()):
                self.json_response(403, {"error": "Sesión inválida. Recarga la página."})
                return
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                self.json_response(415, {"error": "Usa application/json."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 8192:
                    self.json_response(413, {"error": "Tamaño de petición inválido."})
                    return
                body = json.loads(self.rfile.read(length))
                self.json_response(*action(body))
            except (ValueError, UnicodeError):
                self.json_response(400, {"error": "Petición inválida: revisa los campos y la confirmación."})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prueba local de SMS HappyRobot")
    parser.add_argument("command", choices=["inspect", "serve"], nargs="?", default="serve")
    parser.add_argument("--port", type=int, default=8091)
    args = parser.parse_args()
    if args.command == "inspect":
        inspect_account(HappyRobotClient())
        return
    try:
        client = HappyRobotClient()
    except RuntimeError:
        client = None
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
    workflow_id = state.get("workflow_id", "") if state.get("published") else ""
    service = SMSService(client, workflow_id, state.get("hook_slug", ""))
    server = make_server(service, args.port)
    print(f"SMS de prueba: http://127.0.0.1:{server.server_port}", flush=True)
    print("Preparado para solicitar envíos." if service.config()["ready"] else service.config()["reason"], flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
