#!/usr/bin/env python3
"""Servidor local del simulador 112: estáticos, token de voz y ficha del transcript."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
FIELDS = ("ubicacion", "emergencia", "personas", "riesgos", "contacto")
LABELS = {
    "ubicación": "ubicacion",
    "ubicacion": "ubicacion",
    "emergencia": "emergencia",
    "personas": "personas",
    "riesgos": "riesgos",
    "contacto": "contacto",
}


def load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def workflow_id() -> str:
    configured = os.environ.get("HAPPYROBOT_WORKFLOW_ID")
    if configured:
        return configured
    path = ROOT / "workflow.json"
    if path.exists():
        value = json.loads(path.read_text(encoding="utf-8")).get("workflow_id")
        if value:
            return str(value)
    raise RuntimeError("Ejecuta primero: python3 setup_happyrobot.py")


def empty_summary() -> dict[str, str]:
    return {field: "pendiente" for field in FIELDS}


def tool_argument_maps(value: Any) -> list[dict[str, Any]]:
    """Localiza argumentos estructurados aunque HappyRobot cambie el envoltorio."""
    found: list[dict[str, Any]] = []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return found
        return tool_argument_maps(parsed)
    if isinstance(value, list):
        for item in value:
            found.extend(tool_argument_maps(item))
        return found
    if not isinstance(value, dict):
        return found
    if any(key in value for key in FIELDS):
        found.append(value)
    for key in ("arguments", "parameters", "params", "input", "function", "tool_call"):
        if key in value:
            found.extend(tool_argument_maps(value[key]))
    return found


def parse_summary(messages: list[dict[str, Any]]) -> dict[str, str]:
    """Fusiona fichas completas o interrumpidas, priorizando la información más reciente."""
    summary = empty_summary()
    structured: set[str] = set()
    for message in messages:
        for arguments in tool_argument_maps(message.get("tool_calls")):
            for raw_label, raw_value in arguments.items():
                key = LABELS.get(str(raw_label).strip().casefold())
                value = re.sub(r"\s+", " ", str(raw_value or "")).strip()[:240]
                if key and value and value.casefold() not in {"pendiente", "desconocido"}:
                    summary[key] = value
                    structured.add(key)

    found = set(structured)
    for message in reversed(messages):
        content = str(message.get("content") or "")[-4000:]
        if "Ficha:" not in content:
            continue
        ficha = content.rsplit("Ficha:", 1)[-1].split("\n", 1)[0]
        for part in ficha.split("|"):
            clean = re.sub(r"[*_`#]", "", part).strip().strip(".")
            if ":" not in clean:
                continue
            label, value = clean.split(":", 1)
            key = LABELS.get(label.strip().casefold())
            if not key or key in found:
                continue
            value = re.sub(r"\s+", " ", value).strip()[:240]
            summary[key] = value or "pendiente"
            found.add(key)
        if len(found) == len(FIELDS):
            break

    caller_text = " ".join(
        str(message.get("content") or "")
        for message in messages
        if str(message.get("role") or "").casefold() in {"user", "caller"}
    ).casefold()
    if summary["emergencia"] == "pendiente":
        if re.search(r"\b(fuego|incendio|arde|ardiendo|quema|quemando)\b", caller_text):
            summary["emergencia"] = "Incendio / fuego"
        elif re.search(r"\b(accidente|choque|colisi[oó]n|atropello)\b", caller_text):
            summary["emergencia"] = "Accidente"
        elif re.search(r"\b(no respira|inconsciente|desmayad[oa]|sangra)\b", caller_text):
            summary["emergencia"] = "Emergencia médica"
    if summary["riesgos"] == "pendiente":
        risks = []
        if re.search(r"\b(atrapad[oa]s?|no (?:puedo|podemos) salir)\b", caller_text):
            risks.append("personas atrapadas")
        if re.search(r"\b(humo|llamas?|explosi[oó]n|gas)\b", caller_text):
            risks.append("humo, llamas o riesgo de explosión")
        if re.search(r"\b(no respira|me quemo|se quema|sangra)\b", caller_text):
            risks.append("peligro vital indicado")
        if risks:
            summary["riesgos"] = "; ".join(dict.fromkeys(risks))
    return summary


class HappyRobotError(RuntimeError):
    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class HappyRobotClient:
    def __init__(self) -> None:
        self.base = os.environ.get(
            "HAPPYROBOT_API_BASE", "https://platform.eu.happyrobot.ai/api/v2"
        ).rstrip("/")
        self.key = os.environ.get("HAPPYROBOT_API_KEY", "")

    def request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> Any:
        if not self.key:
            raise RuntimeError("Falta HAPPYROBOT_API_KEY")
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:500]
            raise HappyRobotError(
                f"HappyRobot respondió HTTP {error.code}: {detail}", error.code
            ) from error
        except urllib.error.URLError as error:
            raise HappyRobotError("No se pudo contactar con HappyRobot") from error


CLIENT: HappyRobotClient
SESSION_IDS: dict[str, str] = {}


def list_data(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    return payload if isinstance(payload, list) else []


class Handler(SimpleHTTPRequestHandler):
    server_version = "HappyRobot112/1.0"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "microphone=(self)")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' wss://*.happyrobot.ai https://*.happyrobot.ai; "
            "style-src 'self'; media-src 'self' blob:; img-src 'self' data:",
        )
        super().end_headers()

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if urllib.parse.urlsplit(self.path).path != "/api/call":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada"})
            return
        try:
            token = CLIENT.request(
                "POST",
                "/voice/tokens/",
                {
                    "workflow_id": workflow_id(),
                    "env": "production",
                    "ttl_seconds": 3600,
                    "data": {"source": "simulador-112-local"},
                },
            )
            allowed = {
                key: token[key]
                for key in ("url", "token", "room_name", "run_id")
                if key in token
            }
            self.send_json(HTTPStatus.OK, allowed)
        except RuntimeError as error:
            self.send_json(HTTPStatus.BAD_GATEWAY, {"error": str(error)})

    def do_GET(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path != "/api/brief":
            super().do_GET()
            return
        run_id = urllib.parse.parse_qs(parsed.query).get("run_id", [""])[0]
        try:
            run_id = str(uuid.UUID(run_id))
        except ValueError:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "run_id no válido"})
            return
        try:
            session_id = SESSION_IDS.get(run_id)
            if not session_id:
                try:
                    sessions = list_data(
                        CLIENT.request(
                            "GET", f"/runs/{run_id}/sessions?page=1&page_size=10&sort=desc"
                        )
                    )
                except HappyRobotError as error:
                    if error.status != HTTPStatus.NOT_FOUND:
                        raise
                    sessions = []
                if not sessions:
                    self.send_json(
                        HTTPStatus.OK,
                        {"status": "waiting", "summary": empty_summary(), "updated_at": None},
                    )
                    return
                session = next(
                    (item for item in sessions if item.get("run_id") == run_id), sessions[0]
                )
                session_id = str(uuid.UUID(str(session["id"])))
                if len(SESSION_IDS) >= 100:
                    SESSION_IDS.pop(next(iter(SESSION_IDS)))
                SESSION_IDS[run_id] = session_id
            else:
                session = {"status": "active"}
            messages = list_data(
                CLIENT.request(
                    "GET",
                    f"/sessions/{session_id}/messages?page=1&page_size=100&sort=asc",
                )
            )
            updated_at = messages[-1].get("timestamp") if messages else None
            self.send_json(
                HTTPStatus.OK,
                {
                    "status": session.get("status", "active"),
                    "summary": parse_summary(messages),
                    "updated_at": updated_at,
                },
            )
        except (KeyError, ValueError, RuntimeError) as error:
            self.send_json(HTTPStatus.BAD_GATEWAY, {"error": str(error)})

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    global CLIENT
    load_env()
    CLIENT = HappyRobotClient()
    if not CLIENT.key:
        raise SystemExit("Falta HAPPYROBOT_API_KEY en .env o en el entorno")
    try:
        workflow_id()
    except RuntimeError as error:
        raise SystemExit(str(error)) from error
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8112"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Simulador 112 disponible en http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
