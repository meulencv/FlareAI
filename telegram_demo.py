from __future__ import annotations

import argparse
import json
import re
import secrets
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from sms_demo import ROOT, HappyRobotClient, HappyRobotError, NoRedirect, SMSService, make_server

STATE_PATH = ROOT / "telegram-workflow.json"
SIMULATION_PREFIX = "SIMULACRO — No es una orden real de evacuación.\n\n"
TRIGGER_EVENT = "b329e750-2e0e-4618-ba65-e04bb6a93c5f"
POST_EVENT = "01926f2b-2973-7ebf-ada1-e984251e27ec"
TOKEN_VARIABLE = "TELEGRAM_BOT_TOKEN"


class TelegramError(RuntimeError):
    def __init__(self, code: int):
        self.code = code
        hints = {401: "Telegram rechaza el token. Comprueba el token de BotFather.",
                 409: "Hay otro proceso o webhook usando este bot. Usa un bot dedicado para la prueba.",
                 429: "Telegram limita temporalmente las peticiones. Espera antes de consultar de nuevo."}
        super().__init__(hints.get(code, "No se pudo consultar Telegram. Comprueba la conexión y el bot."))


class TelegramClient:
    def __init__(self, token: str):
        if not isinstance(token, str) or not re.fullmatch(r"[0-9]{5,}:[A-Za-z0-9_-]{20,}", token):
            raise ValueError("Token de bot inválido.")
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect)

    def call(self, method: str, body: dict | None = None) -> Any:
        if method not in {"getMe", "getWebhookInfo", "getUpdates"}:
            raise ValueError("Método de Telegram no permitido en el servidor local.")
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{self.token}/{method}",
            data=json.dumps(body or {}).encode(), method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with self.opener.open(request, timeout=20) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            raise TelegramError(exc.code) from None
        except (OSError, ValueError):
            raise TelegramError(503) from None
        if not isinstance(data, dict) or not data.get("ok"):
            raise TelegramError(data.get("error_code", 502) if isinstance(data, dict) else 502)
        return data.get("result")


def prepare_workflow(client: HappyRobotClient, path: Path = STATE_PATH) -> dict:
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def save() -> None:
        path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    if not state:
        workflow = client.request("POST", "/workflows/", {
            "name": "FlareAI Telegram Demo", "icon": "send", "skip_test_all": True,
            "version": {"name": "Simulacro Telegram"},
        })
        workflow = workflow.get("data", workflow)
        state = {"workflow_id": workflow["id"], "version_id": workflow["latest_version"]["id"],
                 "hook_slug": workflow["slug"], "published": False}
        save()
    workflow_path = f"/workflows/{state['workflow_id']}"
    if state.get("published"):
        response = client.request("GET", workflow_path + "/versions")
        versions = response.get("data", []) if isinstance(response, dict) else response
        live = next((v for v in versions if v.get("is_live") and v.get("environment") == "production"), None)
        if not live:
            raise RuntimeError("Publica el workflow de Telegram en producción antes de continuar.")
        if live["id"] != state["version_id"]:
            nodes = client.request("GET", f"/versions/{live['id']}/nodes")["data"]
            trigger = next(n for n in nodes if n.get("event_id") == TRIGGER_EVENT and n.get("parent_id") is None)
            sender = next(n for n in nodes if n.get("event_id") == POST_EVENT)
            state.update(version_id=live["id"], trigger_id=trigger["id"], send_node_id=sender["id"])
            save()
    version_path = f"/versions/{state['version_id']}"
    if not state.get("token_variable_id"):
        response = client.request("POST", workflow_path + "/variables", {
            "key": TOKEN_VARIABLE, "value_production": "NOT_CONFIGURED",
            "value_staging": "NOT_CONFIGURED", "value_development": "NOT_CONFIGURED",
            "is_hidden_in_ui": True,
        })
        variable = response.get("data", response)
        state["token_variable_id"] = variable["id"]
        save()
    if not state.get("trigger_id"):
        response = client.request("POST", version_path + "/nodes", {"nodes": [{
            "type": "trigger", "event_id": TRIGGER_EVENT, "name": "Solicitud de simulacro Telegram",
            "configuration": {"params": ["telegram_body"], "enhanced_security": True,
                              "auth_type": "api_key", "api_key": str(uuid4())},
        }]})
        state["trigger_id"] = response["data"][0]["id"]
        save()
    if not state.get("send_node_id"):
        trigger_id = state["trigger_id"]
        client.request("PUT", version_path + f"/nodes/{trigger_id}/custom-output", {
            "data": {"telegram_body": json.dumps({"chat_id": 0, "text": SIMULATION_PREFIX + "Configuración."})},
        })
        response = client.request("POST", version_path + "/nodes", {"nodes": [{
            "type": "action", "event_id": POST_EVENT, "name": "Enviar simulacro por Telegram",
            "parent_node_id": trigger_id,
            "configuration": {
                "url": [{"type": "paragraph", "children": [
                    {"text": "https://api.telegram.org/bot"},
                    {"type": "variable", "children": [{"text": ""}],
                     "group_id": "use_case_variables", "variable_id": TOKEN_VARIABLE},
                    {"text": "/sendMessage"},
                ]}],
                "webhookSchemaVersion": 2, "authType": "none", "ignore5XX": False,
                "body": {"schemaVersion": 2, "contentType": "application/json",
                         "raw": "{{$var:" + trigger_id + ".telegram_body}}"},
            },
        }]})
        state["send_node_id"] = response["data"][0]["id"]
        save()
    if not state.get("published"):
        result = client.request("POST", version_path + "/publish", {"environment": "production"})
        state["published"] = bool(result.get("is_published") and result.get("is_live"))
        save()
        if not state["published"]:
            raise RuntimeError("El workflow no quedó publicado. Revisa HappyRobot.")
    trigger = client.request("GET", version_path + f"/nodes/{state['trigger_id']}")
    trigger = trigger.get("data", trigger)
    config = trigger.get("configuration", {})
    if not config.get("enhanced_security") or not config.get("api_key"):
        raise RuntimeError("El webhook necesita Enhanced Security y una clave válida.")
    client.hook_key = config["api_key"]
    return state


class TelegramService(SMSService):
    def __init__(self, client: HappyRobotClient | None, state: dict, state_path: Path | None = None):
        super().__init__(client, state.get("workflow_id", "") if state.get("published") else "",
                         state.get("hook_slug", ""))
        self.state = state
        self.state_path = state_path
        self.workflow_verified = False
        self.bot: TelegramClient | None = None
        self.bot_info: dict = {}
        self.chat: dict | None = None
        self.offset = 0
        self.pair_nonce = ""
        self.pair_started = 0.0
        self.pair_expires = 0.0

    def renew_pairing(self) -> None:
        self.pair_nonce = secrets.token_urlsafe(24)
        self.pair_started = time.time()
        self.pair_expires = self.pair_started + 600

    def config(self) -> dict:
        configured = bool(self.client and self.workflow_id and self.client.hook_key)
        reason = ""
        if not configured:
            reason = "Falta preparar el workflow de HappyRobot o su autenticación."
        elif not self.bot:
            reason = "Conecta un bot dedicado de Telegram para comenzar."
        elif not self.chat:
            reason = "Abre el enlace del bot, pulsa Iniciar y después Comprobar vinculación."
        elif not self.workflow_verified:
            reason = "Falta comprobar la autenticación del workflow de HappyRobot."
        if self.bot and not self.chat and time.time() >= self.pair_expires:
            self.renew_pairing()
        username = self.bot_info.get("username", "")
        link = f"https://t.me/{username}?start={self.pair_nonce}" if username and self.pair_nonce and not self.chat else ""
        return {"channel": "telegram", "ready": not reason, "workflow_configured": configured,
                "workflow_id": self.workflow_id, "csrf_token": self.csrf_token, "reason": reason,
                "bot_username": username, "chat": self.chat, "pair_link": link,
                "simulation_prefix": SIMULATION_PREFIX, "workflow_verified": self.workflow_verified,
                "workflow_url": "https://platform.eu.happyrobot.ai/hackspainteam3/workflows/" + self.hook_slug}

    def verify_workflow(self, body: Any) -> tuple[int, dict]:
        with self.lock:
            if not self.client:
                return 503, {"error": "Falta la conexión con HappyRobot."}
            if self.workflow_verified:
                return 200, self.config()
            try:
                state = prepare_workflow(self.client, self.state_path or STATE_PATH)
                response = self.client.trigger_hook(state["hook_slug"], {"telegram_body": json.dumps({
                    "chat_id": 0, "text": SIMULATION_PREFIX + "Verificación sin destinatario.",
                })})
                if not response.get("run_id"):
                    return 502, {"error": "HappyRobot no confirmó el inicio de la comprobación."}
            except HappyRobotError as exc:
                if exc.status in (401, 403):
                    return 502, {"error": "El webhook rechaza la clave. En FlareAI Telegram Demo, crea una versión editable, regenera la API Key del primer nodo y publica en Production. Después vuelve a comprobar aquí; no copies la clave al chat."}
                return 502, {"error": "No se pudo comprobar HappyRobot. Revisa el workflow y la conexión."}
            except (OSError, ValueError, KeyError, RuntimeError, StopIteration):
                return 502, {"error": "No se encontró una versión publicada compatible del workflow de Telegram."}
            self.state = state
            self.workflow_id = state["workflow_id"]
            self.hook_slug = state["hook_slug"]
            self.workflow_verified = True
            return 200, self.config()

    def connect(self, body: Any) -> tuple[int, dict]:
        if not isinstance(body, dict) or body.get("confirmed_store_token") is not True:
            raise ValueError("Confirma que autorizas guardar el token en el workflow de HappyRobot.")
        token = body.get("token")
        if not isinstance(token, str):
            raise ValueError("Introduce el token del bot.")
        bot = TelegramClient(token.strip())
        with self.lock:
            if not self.client or not self.workflow_id:
                return 503, {"error": "El workflow de HappyRobot todavía no está preparado."}
            if self.bot:
                return 409, {"error": "Ya hay un bot conectado. Reinicia el servidor para cambiarlo."}
            try:
                info = bot.call("getMe")
                if not isinstance(info, dict) or not info.get("is_bot") or not re.fullmatch(
                    r"[A-Za-z0-9_]{5,32}", info.get("username", "")
                ):
                    return 400, {"error": "Telegram no devolvió un bot válido."}
                webhook = bot.call("getWebhookInfo")
                if webhook.get("url"):
                    return 409, {"error": "Este bot ya tiene un webhook configurado. Usa un bot nuevo dedicado; no se ha modificado el existente."}
                self.client.request("PATCH", f"/workflows/{self.workflow_id}/variables/{self.state['token_variable_id']}", {
                    "value_production": token.strip(), "is_hidden_in_ui": True,
                })
            except TelegramError as exc:
                return 502, {"error": str(exc)}
            except (HappyRobotError, OSError, ValueError, AttributeError):
                return 502, {"error": "No se pudo preparar la conexión. Revisa las credenciales y los permisos en HappyRobot."}
            self.bot = bot
            self.bot_info = {"id": info["id"], "username": info["username"]}
            self.renew_pairing()
            return 200, self.config()

    def pair(self, body: Any) -> tuple[int, dict]:
        with self.lock:
            if not self.bot:
                return 409, {"error": "Conecta primero el bot."}
            if self.chat:
                return 200, self.config()
            if time.time() >= self.pair_expires:
                return 409, {"error": "El enlace de vinculación ha caducado. Recarga la página para generar otro."}
            try:
                updates = self.bot.call("getUpdates", {"offset": self.offset, "timeout": 0,
                                                      "limit": 100, "allowed_updates": ["message"]})
            except TelegramError as exc:
                return 502, {"error": str(exc)}
            for update in updates:
                self.offset = max(self.offset, int(update["update_id"]) + 1)
                message = update.get("message", {})
                chat, sender = message.get("chat", {}), message.get("from", {})
                if (message.get("text") != f"/start {self.pair_nonce}"
                        or message.get("date", 0) < int(self.pair_started)
                        or chat.get("type") != "private" or sender.get("is_bot")
                        or not isinstance(chat.get("id"), int) or chat["id"] <= 0
                        or sender.get("id") != chat["id"]):
                    continue
                self.chat = {"id": chat["id"], "name": str(chat.get("first_name") or chat.get("username") or "Chat privado")}
                self.pair_nonce = ""
                self.pair_expires = 0
                break
            return (200 if self.chat else 202), self.config()

    def parse_message(self, body: Any) -> tuple[str, str, str]:
        if not isinstance(body, dict) or body.get("confirmed") is not True:
            raise ValueError("Confirma el envío de este simulacro al chat vinculado.")
        message = body.get("message")
        if not isinstance(message, str) or not message.strip() or len(message.strip()) > 1500 or "\x00" in message:
            raise ValueError("Introduce entre 1 y 1500 caracteres.")
        message = message.strip()
        message.encode("utf-8")
        request_id = str(UUID(str(body.get("request_id", ""))))
        return str(self.chat["id"]) if self.chat else "", SIMULATION_PREFIX + message, request_id

    def workflow_payload(self, to: str, message: str) -> dict:
        return {"telegram_body": json.dumps({"chat_id": int(to), "text": message,
                                            "link_preview_options": {"is_disabled": True}})}

    def failure_detail(self, run_id: str) -> dict:
        return {"error": "HappyRobot no completó el envío a Telegram. Revisa el nodo HTTP y que no hayas bloqueado el bot antes de repetir."}


def telegram_server(service: TelegramService, port: int = 8092):
    return make_server(service, port=port, assets={
        "/": ("telegram.html", "text/html; charset=utf-8"),
        "/telegram.js": ("telegram.js", "text/javascript; charset=utf-8"),
        "/sms.css": ("sms.css", "text/css; charset=utf-8"),
    }, actions={"/api/connect": service.connect, "/api/pair": service.pair,
                "/api/verify-workflow": service.verify_workflow})


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulacro Telegram con HappyRobot")
    parser.add_argument("command", choices=["prepare", "serve"], nargs="?", default="serve")
    parser.add_argument("--port", type=int, default=8092)
    args = parser.parse_args()
    client = HappyRobotClient(hook_key="")
    state = prepare_workflow(client)
    if args.command == "prepare":
        print(json.dumps(state, indent=2))
        return
    service = TelegramService(client, state, STATE_PATH)
    server = telegram_server(service, args.port)
    print(f"Telegram de prueba: http://127.0.0.1:{server.server_port}", flush=True)
    print("Conecta el bot desde la página local. No se envía nada al arrancar.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except (HappyRobotError, OSError, ValueError, KeyError, RuntimeError):
        raise SystemExit("No se pudo preparar Telegram. Revisa la API key, la conexión y la configuración del workflow.") from None
