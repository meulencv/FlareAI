import argparse
import getpass
import inspect
import json
import os
import time
from pathlib import Path

from gateway_vision import ENDPOINT, MODEL, PROMPT, SCHEMA, TIMED_SCHEMA, TIMED_PROMPT, request_body, timed_request_body, validate_response, validate_timed_response
from recency import MAX_AGE_SECONDS, resolve_zone, parse_overlay_time, refresh_recency, apply_recency
from happyrobot import API, EVENTS, pair, paragraph, ref
from traffic_catalog import Catalog, IMAGE_RULES, allowed_snapshot

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "runtime/vercel-workflow-state.json"
POST_EVENT = "01926f2b-2973-7ebf-ada1-e984251e27ec"
GET_EVENT = "01926f2a-b1f5-7e65-8203-86c5cd8838b6"


def load():
    return json.loads(STATE.read_text(encoding="utf-8"))


def save(value, credential_update=False):
    current = load() if STATE.exists() else {}
    merged = {**current, **value}
    if not credential_update:
        for key in ("gateway_credential_configured", "budget_usd_authorized"):
            if key in current:
                merged[key] = current[key]
    STATE.parent.mkdir(exist_ok=True)
    temporary = STATE.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(STATE)


def prepare_draft(api):
    if STATE.exists():
        value = load()
    else:
        workflow = api.request("POST", "/workflows/", {
            "name": "FlareAI · Traffic Vision · Vercel", "version": {"name": "v1 · pendiente de configuración"}})
        value = {"workflow_id": workflow["id"], "workflow_slug": workflow.get("slug"),
                 "version_id": workflow["latest_version"]["id"], "published": False,
                 "model": MODEL, "budget_usd_authorized": 0,
                 "status": "needs_gateway_credential_and_budget"}
        save(value)
    if not value.get("credential_variable_id"):
        variable = api.request("POST", f"/workflows/{value['workflow_id']}/variables", {
            "key": "AI_GATEWAY_API_KEY", "value_production": "", "value_staging": "", "value_development": "",
            "is_hidden_in_ui": True})
        value["credential_variable_id"] = variable["id"]
        save(value)
    if not value.get("trigger_id"):
        nodes = api.request("POST", f"/versions/{value['version_id']}/nodes", {"nodes": [{
            "type": "trigger", "event_id": EVENTS["trigger"], "name": "Recibir cámara para análisis remoto",
            "configuration": {"params": ["camera_id", "image_url"]}}]})
        value["trigger_id"] = nodes[0]["id"]
        save(value)
    return value


def timezone_payload():
    import base64
    from importlib.resources import files
    return {name: base64.b64encode(files("tzdata.zoneinfo").joinpath(*name.split("/")).read_bytes()).decode()
            for name in ("Europe/Madrid", "Atlantic/Canary")}


def prepare_code():
    return ("import json, re, base64, io\nfrom urllib.parse import urlsplit\nfrom datetime import datetime, timezone\nfrom zoneinfo import ZoneInfo, ZoneInfoNotFoundError\n"
            + f"EMBEDDED_TZDATA = {timezone_payload()!r}\n" + inspect.getsource(resolve_zone) + "\n"
            + f"IMAGE_RULES = {IMAGE_RULES!r}\nMODEL = {MODEL!r}\nPROMPT = {PROMPT!r}\nSCHEMA = {SCHEMA!r}\n"
            + f"TIMED_SCHEMA = {TIMED_SCHEMA!r}\nTIMED_PROMPT = {TIMED_PROMPT!r}\n"
            + inspect.getsource(allowed_snapshot) + "\n" + inspect.getsource(request_body) + "\n" + inspect.getsource(timed_request_body) + "\n"
            + 'camera_id = input_data.get("camera_id", "")\n'
              'if not isinstance(camera_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", camera_id):\n'
              '    raise ValueError("Identificador de cámara no permitido")\n'
              'time_zone = input_data.get("time_zone") or "Europe/Madrid"\n'
              'if time_zone not in ("Europe/Madrid", "Atlantic/Canary"):\n'
              '    raise ValueError("Zona horaria no admitida")\n'
              'resolve_zone(time_zone)\n'
              'body = timed_request_body({"image_url": input_data.get("image_url")})\n'
              'output = {"body_json": json.dumps(body, ensure_ascii=False), "camera_id": camera_id, "time_zone": time_zone,\n'
              '          "image_url": input_data["image_url"], "requested_at": datetime.now(timezone.utc).isoformat()}\n')


def finalize_code():
    return ("import json, re, math, base64, io\nfrom datetime import datetime, timezone, timedelta\nfrom zoneinfo import ZoneInfo, ZoneInfoNotFoundError\n"
            + f"SCHEMA = {SCHEMA!r}\nTIMED_SCHEMA = {TIMED_SCHEMA!r}\nMAX_AGE_SECONDS = {MAX_AGE_SECONDS}\nEMBEDDED_TZDATA = {timezone_payload()!r}\n"
            + "\n".join(inspect.getsource(fn) for fn in (resolve_zone, validate_response, parse_overlay_time, refresh_recency, apply_recency, validate_timed_response)) + "\n"
            + 'raw = input_data.get("content", "") if input_data.get("finish_reason") == "stop" else ""\n'
              'result = validate_timed_response(raw, input_data.get("camera_id", "unknown"), input_data.get("time_zone") or "Europe/Madrid")\n'
              'result["image_url"] = input_data.get("image_url")\n'
              'try:\n'
              '    cost = float(input_data.get("usage_cost", ""))\n'
              '    result["usage_cost_usd"] = cost if math.isfinite(cost) and 0 <= cost <= 0.5 else None\n'
              'except (ValueError, TypeError):\n'
              '    result["usage_cost_usd"] = None\n'
              'output = {"result_json": json.dumps(result, ensure_ascii=False), "density": result["density"],\n'
              '          "dispatch_authorized": False, "capture_time_verified": False, "freshness": result["freshness"]}\n')


def inference_config(prepare_id):
    return {"url": paragraph(ENDPOINT), "webhookSchemaVersion": 2,
            "authType": "bearer", "token": paragraph(ref("use_case_variables", "AI_GATEWAY_API_KEY")),
            "headers": [{"key": "Content-Type", "value": paragraph("application/json")}],
            "body": {"schemaVersion": 2, "contentType": "application/json", "raw": "{{$var:" + prepare_id + ".body_json}}"},
            "ignore5XX": False}


def build(api):
    value = prepare_draft(api)
    if value.get("published"):
        raise ValueError("El workflow ya está publicado; no se modifica automáticamente")
    version = value["version_id"]
    nodes = value.setdefault("nodes", {})

    def add(key, event, name, config, parent, sample):
        body = {"type": "action", "event_id": event, "name": name, "configuration": config}
        if key in nodes:
            api.request("PUT", f"/versions/{version}/nodes/{nodes[key]}", body)
        else:
            body["parent_node_id"] = parent
            created = api.request("POST", f"/versions/{version}/nodes", {"nodes": [body]})
            nodes[key] = created[0]["id"]
            save(value)
        api.request("PUT", f"/versions/{version}/nodes/{nodes[key]}/custom-output", {"data": sample})
        return nodes[key]

    trigger = value["trigger_id"]
    groups = value.get("groups", {})
    trigger_group = groups.get("trigger", trigger)
    api.request("PUT", f"/versions/{version}/nodes/{trigger}", {
        "type": "action", "event_id": EVENTS["trigger"], "configuration": {"params": ["camera_id", "image_url", "time_zone"]}})
    api.request("PUT", f"/versions/{version}/nodes/{trigger}/custom-output", {
        "data": {"camera_id": "madrid-08301", "image_url": "https://informo.madrid.es/cameras/Camara08301.jpg", "time_zone": "Europe/Madrid"}})
    prepare = add("prepare", EVENTS["python"], "Validar fuente y preparar imagen para Vercel", {
        "execution_profile": "standard", "code": prepare_code(),
        "input_data": [pair("camera_id", trigger_group, "camera_id"), pair("image_url", trigger_group, "image_url"),
                       pair("time_zone", trigger_group, "time_zone")]}, trigger,
        {"body_json": "{}", "camera_id": "madrid-08301", "image_url": "https://informo.madrid.es/cameras/Camara08301.jpg", "time_zone": "Europe/Madrid"})
    prepare_group = groups.get("prepare", prepare)
    inference = add("inference", POST_EVENT, "Vercel AI Gateway · visión remota", inference_config(prepare_group), prepare,
                    {"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}], "usage": {"cost": 0.001}})
    inference_group = groups.get("inference", inference)
    add("finalize", EVENTS["python"], "Validar visión y emitir evidencia sin despacho", {
        "execution_profile": "standard", "code": finalize_code(),
        "input_data": [pair("camera_id", prepare_group, "camera_id"), pair("image_url", prepare_group, "image_url"),
                       pair("time_zone", prepare_group, "time_zone"), pair("content", inference_group, "choices.0.message.content"),
                       pair("usage_cost", inference_group, "usage.cost"),
                       pair("finish_reason", inference_group, "choices.0.finish_reason")]}, inference,
        {"result_json": "{}", "density": "unknown", "dispatch_authorized": False, "capture_time_verified": False, "freshness": "unknown"})
    value["status"] = "built_pending_credentials_auth_probe_and_budget"
    save(value)
    return {"workflow_id": value["workflow_id"], "published": False, "nodes": nodes, "status": value["status"]}


def probe_auth(api):
    value = load()
    if value.get("published"):
        raise ValueError("La prueba de autenticación requiere un borrador sin publicar")
    path = f"/versions/{value['version_id']}/nodes/{value['nodes']['inference']}"
    marker = "flareai-redaction-probe-not-a-real-credential"
    passed, started = False, False
    try:
        api.request("PUT", path, {"type": "action", "event_id": GET_EVENT, "configuration": {
            "url": paragraph("https://ai-gateway.vercel.sh/v1/models"),
            "webhookSchemaVersion": 2, "authType": "bearer", "token": paragraph(marker),
            "headers": [], "params": [], "ignore5XX": False,
            "body": {"schemaVersion": 2, "contentType": "none", "raw": ""}}})
        api.request("POST", f"/workflows/{value['workflow_id']}/publish", {"environment": "production"})
        started = True
        run = api.request("POST", f"/workflows/{value['workflow_id']}/runs", {"environment": "production", "payload": {
            "camera_id": "madrid-08301", "image_url": "https://informo.madrid.es/cameras/Camara08301.jpg"}})
        value["auth_probe_run_id"] = run["run_id"]
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            nodes = api.request("GET", f"/runs/{run['run_id']}/nodes")
            target = next((n for n in nodes if n.get("node_id") == value["nodes"]["inference"] and n.get("output_id")), None)
            if target and target.get("status") in {"succeeded", "completed", "failed"}:
                result = api.request("GET", f"/runs/{run['run_id']}/outputs/{target['output_id']}")
                passed = marker not in json.dumps(result, ensure_ascii=False)
                value["auth_probe_http_status"] = target.get("status")
                break
            if any(n.get("status") == "failed" for n in nodes):
                value["auth_probe_error"] = "Un nodo anterior al HTTP ha fallado"
                break
            time.sleep(2)
    finally:
        if started:
            api.request("POST", f"/workflows/{value['workflow_id']}/unpublish", {"environment": "production"})
            api.request("POST", f"/versions/{value['version_id']}/unlock", {})
        api.request("PUT", path, {"type": "action", "event_id": POST_EVENT,
                                  "configuration": inference_config(value["nodes"]["prepare"])})
    value["auth_probe"] = "passed" if passed else "requires_review"
    save(value)
    return {"auth_probe": value["auth_probe"], "used_real_gateway_key": False, "paid_inference": False}


def publish(api):
    value = load()
    if value.get("auth_probe") != "passed" or value.get("budget_usd_authorized", 0) <= 0 or not value.get("gateway_credential_configured"):
        raise ValueError("Faltan credencial, consentimiento de presupuesto o comprobación de autenticación")
    result = api.request("POST", f"/workflows/{value['workflow_id']}/publish", {"environment": "production"})
    value.update(published=True, status="published_pending_smoke_test", missing_variables=result.get("missing_variables", []))
    save(value)
    return {"workflow_id": value["workflow_id"], "published": True}


def upgrade_timed(api):
    value = load()
    if value.get("timed_clock_enabled") and value.get("published"):
        return value
    if not value.get("timed_draft"):
        previous = value["version_id"]
        version = api.request("POST", f"/versions/{previous}/fork", {})
        value.update(previous_version_id=previous, version_id=version["id"], published=False, timed_draft=True)
        nodes = api.request("GET", f"/versions/{version['id']}/nodes")
        names = {"trigger": "Recibir cámara para análisis remoto", "prepare": "Validar fuente y preparar imagen para Vercel",
                 "inference": "Vercel AI Gateway · visión remota", "finalize": "Validar visión y emitir evidencia sin despacho"}
        selected = {key: next(n for n in nodes if n["name"] == name) for key, name in names.items()}
        value["trigger_id"] = selected["trigger"]["id"]
        value["nodes"] = {key: selected[key]["id"] for key in ("prepare", "inference", "finalize")}
        value["groups"] = {key: node.get("persistent_id", node["id"]) for key, node in selected.items()}
        save(value)
    build(api)
    api.request("POST", f"/workflows/{value['workflow_id']}/unpublish", {"environment": "production"})
    publish(api)
    save({"timed_clock_enabled": True, "status": "timed_vision_published"})
    return {"workflow_id": value["workflow_id"], "version_id": value["version_id"], "published": True, "max_age_seconds": 600}


def refresh_timed(api):
    value = load()
    if not value.get("timed_clock_enabled"):
        raise ValueError("Solo se puede actualizar la versión temporal creada por Traffic Lab")
    api.request("POST", f"/workflows/{value['workflow_id']}/unpublish", {"environment": "production"})
    api.request("POST", f"/versions/{value['version_id']}/unlock", {})
    save({"published": False})
    build(api)
    return publish(api)


def start_run(api, camera_id):
    value = load()
    if not value.get("published"):
        raise ValueError("El workflow no está publicado")
    camera = Catalog.load().get(camera_id)
    used = value.get("test_runs_reserved", 0)
    if used >= 3 or (used + 1) * 0.5 > value.get("budget_usd_authorized", 0):
        raise ValueError("Límite conservador de pruebas alcanzado; no se reintenta automáticamente")
    value["test_runs_reserved"] = used + 1
    save(value)
    result = api.request("POST", f"/workflows/{value['workflow_id']}/runs", {
        "environment": "production", "payload": {"camera_id": camera["id"], "image_url": camera["image_url"]}})
    return {"run_id": result.get("run_id"), "status": result.get("status"), "camera_id": camera["id"]}


def run_result(api, run_id):
    value = load()
    nodes = api.request("GET", f"/runs/{run_id}/nodes")
    for node in nodes:
        if node.get("error") or node.get("status") == "failed":
            return {"run_id": run_id, "status": "failed", "node": node.get("name")}
        if node.get("node_id") == value["nodes"]["finalize"] and node.get("output_id"):
            result = api.request("GET", f"/runs/{run_id}/outputs/{node['output_id']}")
            data = result.get("data") or {}
            if data.get("result_json"):
                return {"run_id": run_id, "status": "completed", "result": json.loads(data["result_json"])}
    return {"run_id": run_id, "status": "pending"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "build", "probe-auth", "publish", "upgrade-timed", "refresh-timed", "run", "result"], nargs="?", default="init")
    parser.add_argument("--camera")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    key = os.environ.get("HAPPYROBOT_API_KEY") or getpass.getpass("HappyRobot API key (no se guarda): ")
    api = API(key)
    if args.command == "run":
        result = start_run(api, args.camera)
    elif args.command == "result":
        result = run_result(api, args.run_id)
    else:
        result = {"init": prepare_draft, "build": build, "probe-auth": probe_auth, "publish": publish, "upgrade-timed": upgrade_timed, "refresh-timed": refresh_timed}[args.command](api)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
