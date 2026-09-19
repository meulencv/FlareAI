#!/usr/bin/env python3
"""Crea y publica el workflow aislado del simulador 112."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
WORKFLOW_NAME = "Simulador 112 · Asistente de voz"
VOICE_EVENT_ID = "0192e5dc-08df-78bf-a549-f43c6bf9f087"
MODEL_ID = "gpt-5.6-sol-low"
MODEL_NAME = "gpt-5.6-sol"
TOOL_NAME = "actualizar_ficha"

PROMPT = """# Rol
Eres el operador del 112 durante esta simulación. Para el llamante, tú eres el 112: atiendes el
aviso, tomas el control de la conversación y registras los datos. Hablas siempre en español de
España, con calma, autoridad y máxima brevedad.

# Regla absoluta
- NUNCA digas que eres una demostración.
- NUNCA digas al llamante que llame al 112: ya está hablando contigo, el operador del 112.
- NUNCA afirmes que has enviado recursos si todavía faltan datos esenciales.
- No uses introducciones, disculpas ni explicaciones sobre tu funcionamiento.

# Extracción rápida
Escucha la explicación completa e infiere inmediatamente todos los campos que estén explícitos o
se deduzcan sin duda razonable:
- "fuego", "se quema" o "arde" => Emergencia: incendio.
- "atrapado", "no puedo salir" => Riesgos: personas atrapadas.
- "me quemo", "no respira", "sangra" => registra el peligro vital indicado.
- Una cantidad junto a personas, heridos o atrapados => Personas: esa cantidad y estado.
- Une calle, número, municipio, planta y referencias en Ubicación.
No obligues al llamante a responder campo por campo si ya dio varios datos en una frase. Si algo es
ambiguo, conserva lo seguro y pregunta solo por la ambigüedad crítica. No inventes.

# Ficha silenciosa
Después de CADA intervención del llamante, invoca `actualizar_ficha` ANTES de responder si has
obtenido o corregido cualquier dato. Pasa todos los campos confirmados o inferidos que conozcas y
omite los desconocidos. Esta tool es tu memoria estructurada y actualiza la pantalla.
- No digas que llamas a una tool.
- No leas la ficha, sus etiquetas ni valores en voz alta.
- No pronuncies "pendiente", JSON, listas de campos ni resúmenes técnicos.
- Si el llamante rectifica, vuelve a invocar la tool con el valor nuevo.

# Conversación
- Primera prioridad: ubicación suficiente para llegar y peligro vital.
- Haz como máximo UNA pregunta por turno, de no más de 12 palabras.
- Si el llamante da información nueva, regístrala antes de preguntar.
- Si rectifica, sustituye el dato anterior.
- Da instrucciones inmediatas simples solo si evitan un peligro evidente; no hagas interrogatorios
  largos ni instrucciones médicas complejas.
- Tu respuesta hablada debe sonar como una conversación real del 112: natural, directa y breve."""

INITIAL_MESSAGE = (
    "Emergencias 112. Dígame qué ocurre y dónde se encuentra."
)


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


class HappyRobot:
    def __init__(self) -> None:
        self.base = os.environ.get(
            "HAPPYROBOT_API_BASE", "https://platform.eu.happyrobot.ai/api/v2"
        ).rstrip("/")
        self.key = os.environ.get("HAPPYROBOT_API_KEY", "")
        if not self.key:
            raise SystemExit("Falta HAPPYROBOT_API_KEY en .env o en el entorno")

    def request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> Any:
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
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")
            raise RuntimeError(f"HappyRobot {method} {path}: HTTP {error.code}: {detail}") from error


def data_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        items = payload.get("data", payload.get("items", payload.get("results", [])))
        return items if isinstance(items, list) else []
    return []


def unwrap(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]
    if isinstance(payload, dict):
        return payload
    raise RuntimeError("Respuesta inesperada de HappyRobot")


def find_or_create_workflow(client: HappyRobot) -> tuple[dict[str, Any], bool]:
    workflows = data_items(client.request("GET", "/workflows/?limit=100"))
    matches = [item for item in workflows if item.get("name") == WORKFLOW_NAME]
    if matches:
        return unwrap(client.request("GET", f"/workflows/{matches[0]['id']}")), False

    created = client.request(
        "POST",
        "/workflows/",
        {
            "name": WORKFLOW_NAME,
            "icon": "phone",
            "from_template": {
                "template": "inbound-voice-agent",
                "inputs": {
                    "agent_name": "Operador 112 Demo",
                    "prompt": {
                        "prompt_md": PROMPT,
                        "initial_message": INITIAL_MESSAGE,
                        "initial_message_uninterruptible": False,
                    },
                },
            },
        },
    )
    return unwrap(created), True


def configure_spanish_voice(
    client: HappyRobot, version_id: str, nodes: list[dict[str, Any]]
) -> None:
    voice = next((node for node in nodes if node.get("event_id") == VOICE_EVENT_ID), None)
    if not voice:
        raise RuntimeError("El template no contiene el nodo Inbound Voice Agent esperado")

    configuration = dict(voice.get("configuration") or {})
    agent = dict(configuration.get("agent") or {})
    agent.update(
        {
            "name": [{"type": "paragraph", "children": [{"text": "Operador 112 Demo"}]}],
            "voices": [
                {"type": "static", "static": {"id": "31hktsdrgix8", "name": "Ana HR"}}
            ],
            "languages": [
                {"type": "static", "static": {"id": "es", "name": "Spanish"}}
            ],
            "language_accents": [
                {
                    "type": "static",
                    "static": {"id": "es-es", "name": "Spanish (Spain)"},
                }
            ],
        }
    )
    configuration["agent"] = agent
    configuration["transcriber_tier"] = "advanced"
    client.request(
        "PUT",
        f"/versions/{version_id}/nodes/{voice['id']}",
        {
            "type": voice["type"],
            "event_id": voice["event_id"],
            "name": voice["name"],
            "configuration": configuration,
        },
    )


def configure_prompt(
    client: HappyRobot, version_id: str, nodes: list[dict[str, Any]]
) -> None:
    prompt_summary = next((node for node in nodes if node.get("type") == "prompt"), None)
    if not prompt_summary:
        raise RuntimeError("El template no contiene el nodo Prompt esperado")
    prompt = unwrap(
        client.request("GET", f"/versions/{version_id}/nodes/{prompt_summary['id']}")
    )
    client.request(
        "PUT",
        f"/versions/{version_id}/nodes/{prompt['id']}",
        {
            "type": "prompt",
            "name": prompt.get("name", "Prompt"),
            "configuration": prompt.get("configuration") or {},
            "prompt_md": PROMPT,
            "initial_message": INITIAL_MESSAGE,
            "initial_message_uninterruptible": False,
            "model": {
                "type": "static",
                "static": {"id": MODEL_ID, "name": MODEL_NAME},
            },
        },
    )


def paragraph(text: str) -> list[dict[str, Any]]:
    return [{"type": "paragraph", "children": [{"text": text}]}]


def ensure_summary_tool(
    client: HappyRobot,
    version_id: str,
    prompt_id: str,
    nodes: list[dict[str, Any]],
) -> str:
    existing = next(
        (
            node
            for node in nodes
            if node.get("type") == "tool" and node.get("name") == TOOL_NAME
        ),
        None,
    )
    if existing:
        return str(existing["id"])

    parameters = [
        {
            "name": "ubicacion",
            "description": paragraph(
                "Dirección y referencias confirmadas: vía, número, municipio, planta o punto kilométrico."
            ),
            "required": False,
            "example": "Calle Rosetas 18, Barcelona, tercera planta",
        },
        {
            "name": "emergencia",
            "description": paragraph(
                "Tipo de emergencia inferido de lo narrado, por ejemplo incendio, accidente o emergencia médica."
            ),
            "required": False,
            "example": "Incendio en vivienda",
        },
        {
            "name": "personas",
            "description": paragraph(
                "Número y estado de personas afectadas, heridas, atrapadas o en peligro."
            ),
            "required": False,
            "example": "34 personas atrapadas",
        },
        {
            "name": "riesgos",
            "description": paragraph(
                "Peligros inmediatos confirmados o deducidos con seguridad: humo, llamas, gas, tráfico o armas."
            ),
            "required": False,
            "example": "Personas atrapadas y humo intenso",
        },
        {
            "name": "contacto",
            "description": paragraph("Teléfono de contacto indicado por el llamante."),
            "required": False,
            "example": "600123123",
        },
    ]
    created = client.request(
        "POST",
        f"/versions/{version_id}/nodes",
        {
            "nodes": [
                {
                    "type": "tool",
                    "name": TOOL_NAME,
                    "parent_node_id": prompt_id,
                    "function": {
                        "description": paragraph(
                            "Actualiza silenciosamente la ficha visible del aviso. Invócala tras cada "
                            "intervención que aporte o corrija datos; omite campos desconocidos."
                        ),
                        "parameters": parameters,
                        "message": {"type": "none"},
                    },
                }
            ]
        },
    )
    tool_id = str(data_items(created)[0]["id"])
    child = client.request(
        "POST",
        f"/versions/{version_id}/nodes",
        {
            "nodes": [
                {
                    "type": "action",
                    "event_id": "019dde7b-3500-7a3c-8f5e-1c2d4e6a8b9c",
                    "name": "confirmar_actualizacion",
                    "parent_node_id": tool_id,
                    "configuration": {
                        "execution_profile": "standard",
                        "code": 'output = {"ok": True}',
                    },
                }
            ]
        },
    )
    child_id = str(data_items(child)[0]["id"])
    client.request(
        "PUT",
        f"/versions/{version_id}/nodes/{child_id}/custom-output",
        {"data": {"ok": True}},
    )
    generated = unwrap(
        client.request(
            "POST",
            f"/versions/{version_id}/tools/{tool_id}/tool-call-result/generate",
            {},
        )
    )
    for node in generated.get("nodes", []):
        fields = [field["path"] for field in node.get("fields", [])]
        client.request(
            "PUT",
            f"/versions/{version_id}/tools/{tool_id}/tool-call-result/visibility",
            {"node_id": node["node_id"], "exposed_fields": fields},
        )
    return tool_id


def main() -> int:
    load_env()
    client = HappyRobot()
    workflow, created = find_or_create_workflow(client)
    workflow_id = workflow["id"]
    version = workflow.get("latest_version") or {}
    version_id = version.get("id")
    if not version_id:
        workflow = unwrap(client.request("GET", f"/workflows/{workflow_id}"))
        version_id = (workflow.get("latest_version") or {}).get("id")
    if not version_id:
        raise RuntimeError("No se pudo determinar la versión del workflow")

    if version.get("is_published") or version.get("is_live"):
        client.request("POST", f"/workflows/{workflow_id}/unpublish", {})
    client.request("POST", f"/versions/{version_id}/unlock", {})
    nodes = data_items(client.request("GET", f"/versions/{version_id}/nodes"))
    prompt_node = next((node for node in nodes if node.get("type") == "prompt"), None)
    if not prompt_node:
        raise RuntimeError("El template no contiene el nodo Prompt esperado")
    configure_spanish_voice(client, version_id, nodes)
    configure_prompt(client, version_id, nodes)
    ensure_summary_tool(client, version_id, str(prompt_node["id"]), nodes)
    client.request(
        "POST",
        f"/workflows/{workflow_id}/publish",
        {"environment": "production"},
    )

    config = {
        "workflow_id": workflow_id,
        "version_id": version_id,
        "name": WORKFLOW_NAME,
        "environment": "production",
    }
    (ROOT / "workflow.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    action = "creado y publicado" if created else "actualizado y republicado"
    print(f"Workflow {action}: {WORKFLOW_NAME} ({workflow_id})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, urllib.error.URLError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
