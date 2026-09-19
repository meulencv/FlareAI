from __future__ import annotations

import argparse
import getpass
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from cloud_steps import FINALIZE, PROMPT, VALIDATE

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "runtime/happyrobot-state.json"
BASE = "https://platform.eu.happyrobot.ai/api/v2"
EVENTS = {"trigger": "019d95d2-e3e0-779a-9731-893810e5691f", "python": "019dde7b-3500-7a3c-8f5e-1c2d4e6a8b9c", "extract": "01926f30-36a3-7394-8f73-eeead5d7f948"}


def paragraph(text):
    return [{"type": "paragraph", "children": [text if isinstance(text, dict) else {"text": text}]}]


def ref(node, field):
    return {"type": "variable", "children": [{"text": ""}], "group_id": node, "variable_id": field}


def pair(key, node, field):
    return {"key": key, "value": paragraph(ref(node, field))}


class API:
    def __init__(self, key=None):
        self.key = key or os.environ.get("HAPPYROBOT_API_KEY")
        if not self.key:
            raise ValueError("Define HAPPYROBOT_API_KEY en el entorno del servidor")

    def request(self, method, path, body=None):
        data = json.dumps(body if body is not None else {}).encode() if method != "GET" else None
        request = urllib.request.Request(BASE + path, data=data, method=method,
                                         headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            try:
                detail = str(json.loads(error.read()).get("message", ""))
            except ValueError:
                detail = "Respuesta de error no JSON"
            detail = detail.replace(self.key, "[redacted]")[:1200]
            raise RuntimeError(f"HappyRobot: HTTP {error.code} en {method} {path}: {detail}") from None
        return result.get("data", result) if isinstance(result, dict) else result


def state():
    if not STATE.exists():
        raise ValueError("Primero ejecuta python happyrobot.py deploy")
    return json.loads(STATE.read_text(encoding="utf-8"))


def save_state(value):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def deploy(api):
    if STATE.exists():
        value = state()
        if value.get("published"):
            return value
    else:
        workflow = api.request("POST", "/workflows/", {"name": "FlareAI · Traffic Lab · revisión visual", "version": {"name": "v1"}})
        value = {"workflow_id": workflow["id"], "workflow_slug": workflow.get("slug"), "version_id": workflow["latest_version"]["id"], "nodes": {}, "published": False}
        save_state(value)
    version = value["version_id"]

    def add(key, kind, event, name, config, parent=None, sample=None):
        if key in value["nodes"]:
            return value["nodes"][key]
        body = {"type": kind, "event_id": EVENTS[event], "name": name, "configuration": config}
        if parent:
            body["parent_node_id"] = parent
        result = api.request("POST", f"/versions/{version}/nodes", {"nodes": [body]})
        node = result[0]["id"]
        value["nodes"][key] = node
        save_state(value)
        if sample:
            api.request("PUT", f"/versions/{version}/nodes/{node}/custom-output", {"data": sample})
        return node

    trigger = add("trigger", "trigger", "trigger", "Recibir evidencia visual de webcam", {"params": ["observation_json"]}, sample={"observation_json": "{}"})
    validation = add("validate", "action", "python", "Validar fecha, calidad y densidad", {"execution_profile": "standard", "code": VALIDATE, "input_data": [pair("observation_json", trigger, "observation_json")]}, trigger,
                     {"evidence_json": "{}", "density": "unknown", "current_visual_evidence": False, "camera_id": "08301", "valid_image_evidence": False})
    schema = {"type": "object", "properties": {"summary": {"type": "string"}, "operator_check": {"type": "string"}}, "required": ["summary", "operator_check"], "additionalProperties": False}
    extract = add("extract", "action", "extract", "IA: resumir evidencia para el operador", {"prompt": paragraph(PROMPT), "input": paragraph(ref(validation, "evidence_json")), "json_schema": paragraph(json.dumps(schema))}, validation,
                  {"response": {"summary": "Muestra no actual: requiere revisión", "operator_check": "¿Se ha revisado el encuadre?"}})
    add("finalize", "action", "python", "Emitir propuesta sin autorizar despachos", {"execution_profile": "standard", "code": FINALIZE, "input_data": [pair("evidence_json", validation, "evidence_json"), pair("summary", extract, "response.summary"), pair("operator_check", extract, "response.operator_check")]}, extract,
        {"result_json": "{}", "density": "unknown", "review_priority": "verify_evidence", "dispatch_authorized": False, "requires_human_review": True})
    publish = api.request("POST", f"/workflows/{value['workflow_id']}/publish", {"environment": "production"})
    value.update(published=True, environment="production", missing_variables=publish.get("missing_variables", []))
    save_state(value)
    return value


def publish_draft(api, version_id):
    value = state()
    workflow = api.request("GET", f"/workflows/{value['workflow_id']}")
    if workflow["latest_version"]["id"] != version_id:
        raise ValueError("La versión no es el último borrador del workflow de Traffic Lab")
    api.request("POST", f"/workflows/{value['workflow_id']}/unpublish", {"environment": "production"})
    api.request("POST", f"/versions/{version_id}/unlock", {})
    nodes = api.request("GET", f"/versions/{version_id}/nodes")
    names = {"trigger": "Recibir evidencia visual de webcam", "validate": "Validar fecha, calidad y densidad",
             "extract": "IA: resumir evidencia para el operador", "finalize": "Emitir propuesta sin autorizar despachos"}
    selected = {key: next(n for n in nodes if n["name"] == name) for key, name in names.items()}
    ids = {key: node["id"] for key, node in selected.items()}
    groups = {key: node.get("persistent_id", node["id"]) for key, node in selected.items()}
    api.request("PUT", f"/versions/{version_id}/nodes/{ids['validate']}", {
        "type": "action", "event_id": EVENTS["python"], "configuration": {
            "execution_profile": "standard", "code": VALIDATE,
            "input_data": [pair("observation_json", groups["trigger"], "observation_json")]}})
    schema = {"type": "object", "properties": {"summary": {"type": "string"}, "operator_check": {"type": "string"}},
              "required": ["summary", "operator_check"], "additionalProperties": False}
    api.request("PUT", f"/versions/{version_id}/nodes/{ids['extract']}", {
        "type": "action", "event_id": EVENTS["extract"], "configuration": {
            "prompt": paragraph(PROMPT), "input": paragraph(ref(groups["validate"], "evidence_json")),
            "json_schema": paragraph(json.dumps(schema))}})
    api.request("PUT", f"/versions/{version_id}/nodes/{ids['finalize']}", {
        "type": "action", "event_id": EVENTS["python"], "configuration": {
            "execution_profile": "standard", "code": FINALIZE, "input_data": [
                pair("evidence_json", groups["validate"], "evidence_json"),
                pair("summary", groups["extract"], "response.summary"),
                pair("operator_check", groups["extract"], "response.operator_check")]}})
    api.request("PUT", f"/versions/{version_id}/nodes/{ids['extract']}/custom-output", {
        "data": {"response": {"summary": "Muestra no actual", "operator_check": "Revisar encuadre"}}})
    published = api.request("POST", f"/workflows/{value['workflow_id']}/publish", {"environment": "production"})
    value.update(version_id=version_id, nodes=ids, published=True,
                 missing_variables=published.get("missing_variables", []))
    save_state(value)
    return value


def start_run(api, observation):
    value = state()
    return api.request("POST", f"/workflows/{value['workflow_id']}/runs", {"environment": "production", "payload": {"observation_json": json.dumps(observation, ensure_ascii=False, allow_nan=False)}})


def run_result(api, run_id):
    nodes = api.request("GET", f"/runs/{run_id}/nodes")
    if isinstance(nodes, dict):
        nodes = nodes.get("nodes", [])
    target = state()["nodes"]["finalize"]
    for node in nodes:
        if node.get("node_id", node.get("id")) == target and node.get("output_id"):
            result = api.request("GET", f"/runs/{run_id}/outputs/{node['output_id']}")
            data = result.get("data", {})
            if result.get("error") or result.get("status") in {"failed", "canceled"}:
                return {"status": "failed", "run_id": run_id}
            if not isinstance(data, dict) or not data.get("result_json"):
                status = "failed" if result.get("status") in {"succeeded", "completed"} else "pending"
                return {"status": status, "run_id": run_id}
            return {"status": "completed", "run_id": run_id, "output": data}
    metadata = api.request("GET", f"/runs/{run_id}")
    status = "failed" if metadata.get("status") in {"failed", "canceled", "skipped", "succeeded", "completed"} else "pending"
    return {"status": status, "run_id": run_id,
            "nodes": [{"name": n.get("name"), "status": n.get("status"), "node_id": n.get("node_id", n.get("id"))} for n in nodes]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["deploy", "run", "result", "publish-draft"])
    parser.add_argument("--version-id")
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--run-id")
    args = parser.parse_args()
    api = API(os.environ.get("HAPPYROBOT_API_KEY") or getpass.getpass("HappyRobot API key (no se guarda): "))
    if args.command == "deploy":
        result = deploy(api)
    elif args.command == "publish-draft":
        if not args.version_id:
            parser.error("publish-draft requiere --version-id")
        result = publish_draft(api, args.version_id)
    elif args.command == "result":
        if not args.run_id:
            parser.error("result requiere --run-id")
        result = run_result(api, args.run_id)
    else:
        if not args.evidence:
            parser.error("run requiere --evidence")
        result = start_run(api, json.loads(args.evidence.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
