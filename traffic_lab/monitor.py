import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from budget import Budget
from incident_workflow import STATE as INCIDENT_STATE, load as incident_state, read_run
from recency import refresh_recency
from remote_setup import load as vision_state
from traffic_catalog import Catalog, allowed_snapshot, normalize_incident

ROOT = Path(__file__).resolve().parent


class PublicImageRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if not allowed_snapshot(newurl):
            raise ValueError("Redirección fuera de los proveedores permitidos")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


class Monitor:
    def __init__(self, api):
        self.api = api
        self.catalog = Catalog.load()
        self.lock = threading.RLock()
        self.jobs = {}
        self.images = {}
        self.active = None
        try:
            vision = vision_state()
        except (OSError, ValueError):
            vision = {}
        cap = min(2, vision.get("budget_usd_authorized", 0))
        self.budget = Budget(ROOT / "runtime/monitor-budget.sqlite", cap, vision.get("vercel_reported_inference_cost_usd", 0)) if cap > 0 else None

    def budget_status(self):
        return self.budget.status() if self.budget else {"cap_usd": 0, "remaining_usd": 0, "used_or_reserved_usd": 0}

    def status(self):
        try:
            state = incident_state()
        except (OSError, ValueError):
            state = {}
        return {"ready": self.api is not None and self.budget is not None and state.get("published", False), "budget": self.budget_status(),
                "workflow_name": "FlareAI · Tráfico · Selección por incidente", "workflow_id": state.get("workflow_id"),
                "catalog_count": state.get("catalog_count", 0), "catalog_copied_at": state.get("catalog_copied_at"),
                "catalog_mode": "read_only_snapshot", "max_cameras": 2, "max_age_seconds": 600,
                "active_job_id": self.active}

    def start(self, incident):
        incident = normalize_incident(incident)
        if not self.api or self.budget is None or not INCIDENT_STATE.exists() or not incident_state().get("published"):
            raise ValueError("El flujo remoto no está configurado en este proceso")
        key = hashlib.sha256(json.dumps(incident, sort_keys=True).encode()).hexdigest()
        with self.lock:
            if self.active:
                current = self.jobs[self.active]
                if current["key"] == key:
                    return {"job_id": self.active, "cached": True}
                raise ValueError("Hay otra consulta en curso; espera a que termine")
            for identifier, job in reversed(list(self.jobs.items())):
                if job["key"] == key and job["status"] == "completed" and time.monotonic() - job["finished_monotonic"] < 60:
                    return {"job_id": identifier, "cached": True}
            identifier = str(uuid.uuid4())
            self.budget.reserve(identifier, 2)
            self.jobs[identifier] = {"job_id": identifier, "key": key, "incident": incident,
                                     "status": "starting", "selected": [], "results": [], "run_id": None}
            self.active = identifier
            while len(self.jobs) > 30:
                self.jobs.pop(next(iter(self.jobs)))
            threading.Thread(target=self.work, args=(identifier,), daemon=True).start()
            return {"job_id": identifier, "cached": False}

    def work(self, identifier):
        job = self.jobs[identifier]
        try:
            state = incident_state()
            started = self.api.request("POST", f"/workflows/{state['workflow_id']}/runs", {
                "environment": "production", "payload": {"incident_json": json.dumps(job["incident"], ensure_ascii=False)}})
            run_id = started.get("run_id")
            if not run_id:
                raise RuntimeError("HappyRobot no devolvió un identificador de ejecución")
            with self.lock:
                job.update(run_id=run_id, status="pending")
            deadline = time.monotonic() + 240
            while time.monotonic() < deadline:
                result = read_run(self.api, run_id)
                with self.lock:
                    job.update(result)
                    if result["status"] not in {"completed", "failed"}:
                        job["status"] = "pending"
                if result["status"] in {"completed", "failed"}:
                    found = {item["camera_id"]: item for item in result["results"]}
                    costs = [found.get(camera["id"], {}).get("usage_cost_usd") for camera in result["selected"]]
                    if result.get("call_attempt_count") == 0:
                        costs = []
                    elif not result.get("selection_verified"):
                        costs = None
                    self.budget.settle(identifier, costs)
                    break
                time.sleep(2)
            else:
                raise TimeoutError("La consulta sigue pendiente en HappyRobot. No se reintenta automáticamente.")
        except (OSError, RuntimeError, ValueError, KeyError) as error:
            with self.lock:
                job.update(status="failed", error=str(error)[:250])
            if not job["run_id"] and isinstance(error, RuntimeError) and any(code in str(error) for code in ("HTTP 400", "HTTP 401", "HTTP 403", "HTTP 404")):
                self.budget.settle(identifier, [])
        finally:
            with self.lock:
                job["finished_monotonic"] = time.monotonic()
                self.active = None
                public = self.get(identifier)
            directory = ROOT / "runtime/monitor-jobs"
            directory.mkdir(exist_ok=True)
            (directory / f"{identifier}.json").write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")

    def restore(self, identifier):
        try:
            if str(uuid.UUID(identifier)) != identifier:
                raise ValueError("ID inválido")
            path = ROOT / "runtime/monitor-jobs" / f"{identifier}.json"
            if path.stat().st_size > 1000000:
                raise ValueError("Registro demasiado grande")
            stored = json.loads(path.read_text(encoding="utf-8"))
            run_id = str(uuid.UUID(stored["run_id"]))
            if not self.api:
                raise ValueError("Sin conexión autenticada")
            metadata = self.api.request("GET", f"/runs/{run_id}")
            if metadata.get("workflow_id") != incident_state()["workflow_id"]:
                raise ValueError("Workflow no admitido")
            proof = read_run(self.api, run_id)
            incident = normalize_incident(stored["incident"])
            restored = {"job_id": identifier, "incident": incident, **proof,
                        "key": hashlib.sha256(json.dumps(incident, sort_keys=True).encode()).hexdigest(), "finished_monotonic": -1000000000}
            if self.budget and proof["status"] == "completed" and len(proof["results"]) == len(proof["selected"]):
                self.budget.reconcile_actual(identifier, proof)
            with self.lock:
                self.jobs[identifier] = restored
        except (OSError, ValueError, KeyError, TypeError):
            raise KeyError("Consulta no recuperable") from None

    def get(self, identifier):
        with self.lock:
            missing = identifier not in self.jobs
        if missing:
            self.restore(identifier)
        with self.lock:
            job = self.jobs[identifier]
            public = {key: value for key, value in job.items() if key not in {"key", "finished_monotonic"}}
            public = json.loads(json.dumps(public))
        public["results"] = [refresh_recency(result) for result in public["results"]]
        public["budget"] = self.budget_status()
        return public

    def image(self, job_id, camera_id):
        job = self.get(job_id)
        if camera_id not in {camera["id"] for camera in job.get("selected", [])}:
            raise ValueError("La cámara no pertenece a esta consulta")
        camera = self.catalog.get(camera_id)
        key = (job_id, camera_id)
        with self.lock:
            if key in self.images:
                return self.images[key]
        request = urllib.request.Request(camera["image_url"], headers={"User-Agent": "FlareAI-TrafficLab/1.0", "Accept": "image/*"})
        with urllib.request.build_opener(PublicImageRedirect()).open(request, timeout=15) as response:
            body = response.read(4_000_001)
            mime = response.headers.get("Content-Type", "").split(";")[0]
        if len(body) > 4_000_000 or mime not in {"image/jpeg", "image/png", "image/gif", "image/webp"}:
            raise ValueError("La fuente no devolvió una imagen admitida")
        with self.lock:
            self.images[key] = (body, mime)
            while len(self.images) > 32:
                self.images.pop(next(iter(self.images)))
        return body, mime

    def flare_incidents(self):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8090/api/data", timeout=2) as response:
                raw = response.read(10_000_001)
            if len(raw) > 10_000_000:
                raise ValueError("Respuesta demasiado grande")
            value = json.loads(raw)
            incidents = []
            for item in value.get("incidents", [])[:500]:
                try:
                    incident = normalize_incident({"id": item["id"], "lat": item["lat"], "lon": item["lon"],
                                                   "description": item.get("name") or item.get("province") or "Incidente FlareAI", "radius_km": 10})
                    incidents.append(incident)
                except (KeyError, ValueError, TypeError):
                    continue
            return {"available": True, "incidents": incidents, "source_status": value.get("status"),
                    "source": "FlareAI local · consulta de solo lectura"}
        except (OSError, ValueError, TypeError):
            return {"available": False, "incidents": [], "reason": "El mapa FlareAI no responde en el puerto 8090. Puedes introducir la ubicación manualmente."}
