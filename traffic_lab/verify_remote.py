import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from remote_setup import API, load, run_result, save


def inspect_run(api, state, identifier):
    result = run_result(api, identifier)
    if result["status"] != "completed":
        raise ValueError(f"Run no completado: {identifier}")
    evidence = result["result"]
    if evidence["engine"] != "multimodal_estimate_not_yolo" or evidence["dispatch_authorized"] or not evidence["requires_human_review"]:
        raise AssertionError("Contrato remoto incorrecto")
    if evidence["capture_time_verified"] or evidence["current_visual_evidence"]:
        raise AssertionError("La hora de captura no está verificada en esta integración")
    nodes = api.request("GET", f"/runs/{identifier}/nodes")
    node = next(n for n in nodes if n.get("node_id") == state["nodes"]["inference"])
    payload = api.request("GET", f"/runs/{identifier}/outputs/{node['output_id']}")
    data = payload.get("data") or {}
    usage = {key: value for key, value in (data.get("usage") or {}).items()
             if type(value) in (int, float) and math.isfinite(value) and value >= 0}
    return {"run_id": identifier, "result": evidence, "model": data.get("model"), "usage": usage}


def main():
    parser = argparse.ArgumentParser(description="Verifica runs existentes de visión remota; no genera inferencias nuevas")
    parser.add_argument("--run-id", action="append", required=True)
    args = parser.parse_args()
    state, api = load(), API()
    runs = [inspect_run(api, state, identifier) for identifier in dict.fromkeys(args.run_id)]
    costs = [run["usage"].get("cost") for run in runs]
    cost = sum(costs) if all(value is not None for value in costs) else None
    report = {"verified_at": datetime.now(timezone.utc).isoformat(), "workflow_id": state["workflow_id"],
              "version_id": state["version_id"], "remote_execution_verified": True,
              "capture_freshness_verified": False, "auth_redaction_probe": state.get("auth_probe"),
              "budget_usd_authorized": state["budget_usd_authorized"],
              "vercel_reported_inference_cost_usd": cost, "runs": runs,
              "limitations": ["No benchmark etiquetado de precisión visual; conteos estimados.",
                              "Catálogo local leído, no sincronización remota de PostgreSQL.",
                              "La API de visión recibe la URL pública; no hay evidencia inmutable del fotograma exacto.",
                              "Sin cron ni despachos: ejecución bajo demanda."]}
    if cost is not None and cost > state["budget_usd_authorized"]:
        raise AssertionError("El coste informado supera el presupuesto autorizado")
    path = Path(__file__).resolve().parent / "verification-remote.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    save({"status": "remote_smoke_tests_passed", "verified_run_ids": [r["run_id"] for r in runs],
          "vercel_reported_inference_cost_usd": cost})
    print(json.dumps({"report": path.name, "remote_runs_verified": len(runs),
                      "vercel_reported_inference_cost_usd": cost,
                      "results": [{"camera_id": r["result"]["camera_id"], "density": r["result"]["density"],
                                   "vehicle_count_estimate": r["result"]["vehicle_count_estimate"]} for r in runs]}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
