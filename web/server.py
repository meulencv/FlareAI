#!/usr/bin/env python3
"""Dashboard operativo del S.O.S. Agentic Crisis Engine.

    python web/server.py            # http://localhost:8000
    SOS_DB=local|twin|auto          # backend de datos (auto: Twin si está usable, si no Postgres local)

API (JSON):
  GET  /api/state                     estado completo (incidentes, activos, medios, acciones, llamadas, meteo, config)
  GET  /api/log                       últimas líneas de actividad
  POST /api/actions/<id>/decide       {"decision": "approve"|"reject", "operator": "..."} → WF-Approve
  POST /api/voice/token               {"mode": "112"} | {"mode": "outbound", "action_id": "..."} | {"mode": "listen", "session_id": "...", "takeover": false}
  POST /api/sim/<paso>                citizen_call | satellite | wind_shift | reset  (simulador integrado)
  POST /api/config                    {"key": "...", "value": ...} actualiza config en caliente

Modo local: los workflows se ejecutan con el intérprete `sos.runtime` sobre el Postgres embebido.
Modo cloud (Twin usable): se disparan los workflows reales de HappyRobot.
La API key de HappyRobot nunca llega al navegador (los tokens de voz se piden aquí).
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sos.db import get_database  # noqa: E402
from sos.happyrobot import HappyRobotClient, HappyRobotError  # noqa: E402
from sos.settings import Settings  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"
PORT = int(os.environ.get("PORT", "8000"))
# Workflow de voz de reserva (solo habla) para cuando Twin no está provisionado.
FALLBACK_VOICE_WF = os.environ.get("HAPPYROBOT_VOICE_FALLBACK_WORKFLOW_ID", "01a0b665-2a84-725f-a714-947e427ea6d2")


class App:
    def __init__(self) -> None:
        self.settings = Settings.from_env()
        self.client = HappyRobotClient(self.settings)
        self.db = get_database(client=self.client)
        self.lock = threading.Lock()
        self.log: list[dict] = []
        self.mode = "cloud" if self.db.name == "twin" else "local"
        from sos.workflows.deploy import load_state

        self.wf = load_state().get("workflows", {})
        from sos.simulation import scenario_wind_shift as sc

        self.sc = sc
        if self.mode == "local":
            self.driver = sc.LocalDriver(self.db, verbose=False)
            self.driver.rt.verbose = False
            self._hook_runtime_log()
        else:
            self.driver = sc.CloudDriver(self.client, sc.Narrator(quiet=True))
        self.say(f"dashboard iniciado en modo {self.mode} (backend {self.db.name})")

    # ---- log ------------------------------------------------------------------------------------
    def say(self, msg: str, kind: str = "info") -> None:
        self.log.append({"t": time.time(), "kind": kind, "msg": msg})
        del self.log[:-300]

    def _hook_runtime_log(self) -> None:
        rt = self.driver.rt
        orig = rt._log

        def _log(ctx, msg):
            orig(ctx, msg)
            if msg.startswith("▶") or msg.startswith("  ⚙"):
                self.say(msg.strip(), "run")

        rt._log = _log

    # ---- estado ---------------------------------------------------------------------------------
    def state(self) -> dict:
        with self.lock:
            return self._state()

    def _state(self) -> dict:
        q = self.db.rows
        incidents = q("""SELECT i.id::text AS id, i.type, i.status, i.lat, i.lon, i.confidence, i.risk_score, i.priority, i.summary,
                                i.ai_assessment, i.created_at::text AS created_at, i.updated_at::text AS updated_at,
                                (SELECT count(*) FROM evidence e WHERE e.incident_id = i.id) AS evidence_count,
                                (SELECT row_to_json(w) FROM (SELECT wind_speed_kmh, wind_dir_deg, temp_c, humidity, observed_at::text AS observed_at
                                     FROM weather_observations w WHERE w.incident_id = i.id ORDER BY observed_at DESC, created_at DESC LIMIT 1) w) AS weather,
                                (SELECT row_to_json(p) FROM (SELECT summary, priorities, resource_plan, notification_order, created_at::text AS created_at
                                     FROM plans p WHERE p.incident_id = i.id ORDER BY created_at DESC LIMIT 1) p) AS plan
                         FROM incidents i ORDER BY i.priority DESC, i.created_at DESC LIMIT 20""")
        evidence = q("""SELECT id::text AS id, incident_id::text AS incident_id, source_type, source_ref, lat, lon, observed_at::text AS observed_at,
                               reliability, payload FROM evidence ORDER BY observed_at DESC, created_at DESC LIMIT 60""")
        actions = q("""SELECT a.id::text AS id, a.incident_id::text AS incident_id, a.kind, a.status, a.requires_approval, a.priority, a.rationale,
                              a.payload, a.result, a.run_id, a.session_id, a.decided_by, a.created_at::text AS created_at, a.updated_at::text AS updated_at,
                              c.name AS contact_name, c.role AS contact_role, r.name AS resource_name
                       FROM actions a LEFT JOIN contacts c ON c.id = a.contact_id LEFT JOIN resources r ON r.id = a.resource_id
                       ORDER BY a.created_at DESC LIMIT 100""")
        assets = q("SELECT id::text AS id, ref, name, kind, lat, lon, population, insured_value, carbon_credit_value, hazard_class FROM assets")
        resources = q("SELECT id::text AS id, ref, name, kind, capabilities, lat, lon, status, assigned_incident_id::text AS assigned_incident_id FROM resources")
        config = {r["key"]: r["value"] for r in q("SELECT key, value FROM config")}
        return {"mode": self.mode, "backend": self.db.name, "now": time.time(), "incidents": incidents, "evidence": evidence,
                "actions": actions, "assets": assets, "resources": resources, "config": config,
                "workflows": {k: {"id": v["id"], "slug": v["slug"]} for k, v in self.wf.items()},
                "voice_fallback": self.mode == "local"}

    # ---- acciones -------------------------------------------------------------------------------
    def decide(self, action_id: str, decision: str, operator: str) -> dict:
        with self.lock:
            self.say(f"operador {operator}: {decision} {action_id[:8]}", "human")
            if self.mode == "local":
                self.driver.rt.run("approve", {"action_id": action_id, "decision": decision, "operator": operator, "note": ""})
            else:
                self.client.workflows.trigger(self.wf["approve"]["id"], {"action_id": action_id, "decision": decision, "operator": operator, "note": ""})
        return {"ok": True}

    def voice_token(self, body: dict) -> dict:
        mode = body.get("mode")
        if mode == "listen":
            return self.client.voice.join(body["session_id"], takeover=bool(body.get("takeover")))
        if mode == "112":
            wf = FALLBACK_VOICE_WF if self.mode == "local" else self.wf["citizen_inbound"]["id"]
            self.say("llamada entrante al 112 virtual (web call)", "call")
            return self.client.voice.token(wf, ttl=1800)
        if mode == "outbound":
            with self.lock:
                a = self.db.rows("""SELECT a.id::text AS id, a.incident_id::text AS incident_id, a.kind, a.payload, c.name AS contact_name, c.role,
                                       i.summary, i.lat, i.lon FROM actions a LEFT JOIN contacts c ON c.id = a.contact_id JOIN incidents i ON i.id = a.incident_id
                                WHERE a.id = '%s'""" % body["action_id"].replace("'", ""))
            if not a:
                raise KeyError("acción no encontrada")
            a = a[0]
            p = a["payload"] if isinstance(a["payload"], dict) else json.loads(a["payload"] or "{}")
            data = {"action_id": a["id"], "incident_id": a["incident_id"], "kind": a["kind"], "role": p.get("contact_role") or a["role"] or "citizen",
                    "contact_name": a["contact_name"] or p.get("contact_name") or "", "place": p.get("place") or "",
                    "instructions": p.get("instructions") or "", "incident_summary": a["summary"] or "",
                    "incident_lat": str(a["lat"]), "incident_lon": str(a["lon"])}
            self.say(f"descolgando llamada {a['kind']} con {data['contact_name']}", "call")
            if self.mode == "local":
                # Sin Twin: usamos el workflow de voz de reserva y marcamos el resultado al colgar desde el navegador.
                tok = self.client.voice.token(FALLBACK_VOICE_WF, ttl=1800)
                tok["fallback"] = True
                tok["data"] = data
                return tok
            return self.client.voice.token(self.wf["outbound_voice"]["id"], data=data, ttl=1800)
        raise KeyError("mode desconocido")

    def call_finished(self, body: dict) -> dict:
        """Modo local: el navegador informa del fin de una llamada (no hay tool de HappyRobot que escriba en local)."""
        if self.mode != "local":
            return {"ok": True}
        action_id = body.get("action_id")
        if not action_id:
            return {"ok": False}
        with self.lock:
            self.driver.rt.scenario.setdefault("outbound", {})["*"] = {"outcome": body.get("outcome", "accepted"), "notes": body.get("notes", "Llamada realizada desde el dashboard."), "new_info": body.get("new_info", "")}
            row = self.db.rows("""SELECT a.id::text AS id, a.incident_id::text AS incident_id, a.kind, a.payload::text AS payload, c.name AS contact_name, i.summary AS incident_summary
                                  FROM actions a LEFT JOIN contacts c ON c.id = a.contact_id JOIN incidents i ON i.id = a.incident_id WHERE a.id = '%s'""" % action_id.replace("'", ""))
            if row:
                self.driver.pick_up(row[0], self.driver.rt.scenario["outbound"]["*"])
        return {"ok": True}

    def simulate(self, step: str, body: dict) -> dict:
        sc, d = self.sc, self.driver
        with self.lock:
            if step == "reset":
                from sos.twin import seed

                seed.reset_operational_data(self.db)
                self.say("simulación reiniciada", "sim")
            elif step == "citizen_call":
                self.say("SIM: un vecino llama al 112 (aviso de humo en Serra)", "sim")
                d.citizen_call({"lugar_ref": body.get("lugar_ref", "serra"), "lugar_texto": "el monte detrás de la urbanización alta de Serra", "tipo": "wildfire",
                                "descripcion": body.get("descripcion", "Humo negro muy denso y llamas en el pinar; el humo va hacia el pueblo"),
                                "direccion_fuego": "hacia el pueblo (este)", "personas_en_peligro": "ninguna que sepa", "nombre": "Vicent Soler", "telefono": "+34600000099"})
            elif step == "satellite":
                inc = self._latest_incident()
                self.say("SIM: FIRMS detecta 2 anomalías térmicas + viento del oeste 40 km/h", "sim")
                if inc:
                    d.weather(inc["id"], {"wind_speed_kmh": 40, "wind_dir_deg": 270, "temp_c": 33, "humidity": 18, "source": "aemet-sim"})
                lat, lon = (inc["lat"], inc["lon"]) if inc else (sc.FIRE["lat"], sc.FIRE["lon"])
                from sos.sources import firms

                for env in firms.synthetic(lat, lon, n=2):
                    d.ingest(env)
            elif step == "wind_shift":
                inc = self._latest_incident()
                if not inc:
                    return {"ok": False, "error": "no hay incidente"}
                cur = (inc.get("wind") or {}).get("wind_dir_deg") or 270
                new_dir = (float(cur) + 180) % 360
                self.say(f"SIM: el viento gira 180° (ahora de {new_dir:.0f}°)", "sim")
                d.weather(inc["id"], {"wind_speed_kmh": 45, "wind_dir_deg": new_dir, "temp_c": 34, "humidity": 15, "source": "aemet-sim"})
            elif step == "weather_real":
                inc = self._latest_incident()
                if not inc:
                    return {"ok": False, "error": "no hay incidente"}
                from sos.sources import open_meteo

                obs = open_meteo.current(inc["lat"], inc["lon"])
                self.say(f"meteo real (Open-Meteo): {obs}", "sim")
                d.weather(inc["id"], {k: ("" if v is None else v) for k, v in obs.items()})
            else:
                return {"ok": False, "error": "paso desconocido"}
        return {"ok": True}

    def _latest_incident(self) -> dict | None:
        # (llamado siempre con self.lock ya adquirido)
        rows = self.db.rows("""SELECT i.id::text AS id, i.lat, i.lon, (SELECT row_to_json(w) FROM (SELECT wind_dir_deg FROM weather_observations w
                               WHERE w.incident_id = i.id ORDER BY observed_at DESC, created_at DESC LIMIT 1) w) AS wind
                               FROM incidents i WHERE status NOT IN ('closed','dismissed') ORDER BY created_at DESC LIMIT 1""")
        return rows[0] if rows else None

    def set_config(self, key: str, value) -> dict:
        with self.lock:
            self.db.sql("UPDATE config SET value = '%s'::jsonb, updated_at = now() WHERE key = '%s'" % (json.dumps(value).replace("'", "''"), key.replace("'", "")))
        self.say(f"config {key} = {json.dumps(value)[:80]}", "human")
        return {"ok": True}


APP: App | None = None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def log_message(self, fmt, *args):  # silenciar acceso estático
        if "/api/" in (args[0] if args else ""):
            return

    def _json(self, code: int, obj) -> None:
        data = json.dumps(obj, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_GET(self):
        if self.path.startswith("/api/state"):
            return self._json(200, APP.state())
        if self.path.startswith("/api/log"):
            return self._json(200, APP.log[-120:])
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        try:
            body = self._body()
            parts = self.path.strip("/").split("/")
            if parts[:2] == ["api", "actions"] and len(parts) == 4 and parts[3] == "decide":
                return self._json(200, APP.decide(parts[2], body.get("decision", "approve"), body.get("operator", "operador")))
            if self.path == "/api/voice/token":
                return self._json(200, APP.voice_token(body))
            if self.path == "/api/voice/finished":
                return self._json(200, APP.call_finished(body))
            if parts[:2] == ["api", "sim"] and len(parts) == 3:
                return self._json(200, APP.simulate(parts[2], body))
            if self.path == "/api/config":
                return self._json(200, APP.set_config(body["key"], body["value"]))
            return self._json(404, {"error": "not found"})
        except HappyRobotError as exc:
            return self._json(502, {"error": str(exc), "detail": exc.body})
        except Exception as exc:  # noqa: BLE001
            return self._json(500, {"error": f"{type(exc).__name__}: {exc}"})


def main() -> None:
    global APP
    APP = App()
    print(f"Dashboard S.O.S. → http://localhost:{PORT}  (modo {APP.mode}, backend {APP.db.name})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
