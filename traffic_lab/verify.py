import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


class Probe:
    def __init__(self, url):
        self.url = url.rstrip("/")

    def request(self, path, body=None, expected=200, headers=None):
        options = {"Content-Type": "application/json", **(headers or {})}
        request = urllib.request.Request(self.url + path, data=json.dumps(body).encode() if body is not None else None, headers=options)
        try:
            response = urllib.request.urlopen(request, timeout=60)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            if response.code != expected:
                raise AssertionError(f"{path}: HTTP {response.code}, esperado {expected}")
            return json.load(response)


def main():
    parser = argparse.ArgumentParser(description="Verifica HTTP y el detector; --cloud ejecuta tres runs reales de HappyRobot")
    parser.add_argument("--url", default="http://127.0.0.1:8790")
    parser.add_argument("--cloud", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    probe = Probe(args.url)
    catalog = probe.request("/api/cameras")
    probe.request("/runtime/happyrobot-state.json", expected=404)
    probe.request("/api/cameras", expected=403, headers={"Host": "untrusted.example"})
    probe.request("/api/analyze", {"camera_id": "bad"}, expected=400)
    probe.request("/api/analyze", {"camera_id": "08301"}, expected=403, headers={"Origin": "https://untrusted.example"})
    report = {"verified_at": datetime.now(timezone.utc).isoformat(), "http_checks": "passed", "observations": [], "cloud_runs": []}
    mode = "live" if args.live else "demo"
    for camera in catalog["cameras"]:
        payload = probe.request("/api/analyze", {"camera_id": camera["id"], "mode": mode})
        evidence = payload["evidence"]
        if evidence["source"]["camera_id"] != camera["id"] or not evidence["requires_human_review"]:
            raise AssertionError("Contrato de evidencia incorrecto")
        if not payload["image"].startswith("data:image/jpeg;base64,"):
            raise AssertionError("Falta imagen anotada")
        if any(z["speed_kmh"] is not None or z["road_blocked"] is not None for z in evidence["zones"]):
            raise AssertionError("El detector ha inventado velocidad o bloqueo")
        if evidence["calibration"]["status"] != "aligned" and any(zone["vehicle_count"] is not None or zone["density"] != "unknown" for zone in evidence["zones"]):
            raise AssertionError("Se han usado zonas de un encuadre no validado")
        if evidence.get("capture_time_verified"):
            raise AssertionError("La fecha HTTP no verifica la captura")
        report["observations"].append(evidence)
        print(json.dumps({"camera_id": camera["id"], "quality": evidence["quality"]["status"], "zones": evidence["zones"]}, ensure_ascii=True), flush=True)
        if not args.cloud:
            continue
        if not catalog["cloud_ready"]:
            raise AssertionError("Servidor sin credenciales o workflow sin desplegar")
        body = {"observation_id": payload["observation_id"]}
        if evidence["calibration"]["status"] != "aligned" or not any((zone["vehicle_count"] or 0) > 0 for zone in evidence["zones"]) or (mode == "live" and evidence["freshness"] != "recent"):
            probe.request("/api/workflow", body, 409)
            report["cloud_runs"].append({"camera_id": camera["id"], "status": "blocked_before_cloud"})
            continue
        run_id = probe.request("/api/workflow", body, 202)["run_id"]
        if probe.request("/api/workflow", body, 202)["run_id"] != run_id:
            raise AssertionError("Reenvío duplicado: debe reutilizar la ejecución")
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            status = probe.request("/api/run?id=" + run_id)
            if status["status"] == "failed":
                raise AssertionError("Run fallido: " + run_id)
            if status["status"] == "completed":
                result = json.loads(status["output"]["result_json"])
                if result["camera_id"] != camera["id"] or result["dispatch_authorized"] or result["recommended_route"] is not None:
                    raise AssertionError("Contrato cloud incorrecto")
                if result["operator_summary"].startswith("Resumen de IA no disponible"):
                    raise AssertionError("El resumen del nodo de IA no ha llegado al resultado")
                if result["evidence"].get("incidents_status") != "not_assessed":
                    raise AssertionError("El workflow debe declarar que no evalúa incidentes")
                if mode == "demo" and result["current_visual_evidence"]:
                    raise AssertionError("La muestra histórica no es evidencia actual")
                if evidence["quality"]["status"] == "unusable" and result["density"] != "unknown":
                    raise AssertionError("Imagen inutilizable clasificada como tráfico conocido")
                report["cloud_runs"].append({"run_id": run_id, "result": result})
                print(json.dumps({"run_id": run_id, "result": result}, ensure_ascii=True), flush=True)
                break
            time.sleep(2)
        else:
            raise TimeoutError("Run pendiente: " + run_id)
    destination = Path(__file__).resolve().parent / f"verification-{mode}-alignment.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Verificacion completa: {destination.name}")


if __name__ == "__main__":
    main()
