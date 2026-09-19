"""Escenario demo: incendio en la Serra Calderona con giro de viento de 180°.

Guion (cada paso pasa por los MISMOS workflows que corren en HappyRobot):
  1. Un vecino llama al 112 virtual → evidencia `call` → incidente candidato → el Analista pide
     reconocimiento con dron (una sola fuente).
  2. El satélite (FIRMS) detecta dos anomalías térmicas en el mismo punto → el Analista verifica
     el incidente, calcula el riesgo con viento del oeste (→ Serra, colegio, Segart, Estivella),
     guarda el plan y propone: evacuaciones, coordinación con bomberos, despachos y aviso a policía.
  3. El operador aprueba las evacuaciones y la coordinación (1 clic) → WF-Execute → llamadas
     listas para "descolgar".
  4. Se "descuelgan" las llamadas (web call): el agente habla, registra el resultado; María aporta
     información nueva → nueva evidencia.
  5. El viento gira 180° (ahora del este) → WF-Weather-Inject detecta el giro, publica un signal a
     las llamadas en curso y re-evalúa: nuevas zonas amenazadas (Olocau, Marines) → nuevas acciones.

Modo local: intérprete `sos.runtime` sobre el Postgres embebido (agentes deterministas).
Modo cloud (--cloud): dispara los hooks reales de HappyRobot (requiere Twin provisionado).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from ..db import Database
from ..sources import firms
from ..workflows import approve, assess, citizen_inbound, execute, ingest, outbound_voice, weather

FIRE = {"lat": 39.70, "lon": -0.47}


@dataclass
class Narrator:
    quiet: bool = False
    lines: list[str] = field(default_factory=list)

    def step(self, title: str) -> None:
        self.say(f"\n━━━ {title} ━━━")

    def say(self, msg: str) -> None:
        self.lines.append(msg)
        if not self.quiet:
            print(msg)


def _table(db: Database, sql: str) -> list[dict]:
    return db.rows(sql)


def print_state(db: Database, n: Narrator) -> None:
    inc = _table(db, "SELECT type, status, confidence, priority, risk_score, summary FROM incidents ORDER BY created_at")
    for i in inc:
        n.say(f"  incidente {i['type']} · {i['status']} · confianza {i['confidence']} · prioridad {i['priority']} · riesgo {i['risk_score']}")
        n.say(f"    {i['summary']}")
    acts = _table(db, "SELECT kind, status, priority, requires_approval, COALESCE(payload->>'contact_name', payload->>'resource_name', '') AS who, rationale FROM actions ORDER BY created_at")
    for a in acts:
        n.say(f"  acción {a['kind']:18} {a['status']:9} p{a['priority']:<3} {'[aprobación]' if a['requires_approval'] else '[auto]'} {a['who']} — {a['rationale'][:70]}")
    plan = _table(db, "SELECT version, summary FROM plans ORDER BY created_at DESC LIMIT 1")
    if plan:
        n.say(f"  plan vigente: {plan[0]['summary']}")


class LocalDriver:
    """Ejecuta los workflows en local con `sos.runtime`."""

    def __init__(self, db: Database, verbose: bool = False):
        from ..runtime import LocalRuntime
        from ..runtime.agents import POLICIES

        specs = {s.key: s for s in (ingest.spec, assess.spec, execute.spec, approve.spec, outbound_voice.spec, citizen_inbound.spec, weather.inject)}
        self.rt = LocalRuntime(db, specs, POLICIES, verbose=verbose, http=self._http)
        self.rt.scenario = {}
        self.signals: list[dict] = []

    def _http(self, method: str, url: str, headers: dict, body: str | None) -> dict:
        # En local no publicamos señales reales: las registramos para mostrarlas.
        if "/signals/" in url:
            self.signals.append(json.loads(body or "{}"))
            return {"status": "published (simulado)"}
        from ..runtime.local import LocalRuntime

        return LocalRuntime._http(method, url, headers, body)

    def citizen_call(self, aviso: dict) -> None:
        self.rt.scenario["aviso"] = aviso
        self.rt.run("citizen_inbound", {})

    def ingest(self, envelope: dict) -> None:
        self.rt.run("ingest", envelope)

    def approve(self, action_id: str, operator: str = "operador-demo") -> None:
        self.rt.run("approve", {"action_id": action_id, "decision": "approve", "operator": operator, "note": ""})

    def pick_up(self, action: dict, answer: dict) -> None:
        self.rt.scenario.setdefault("outbound", {})[action["contact_name"]] = answer
        p = action["payload"] if isinstance(action["payload"], dict) else json.loads(action["payload"])
        self.rt.run("outbound_voice", {
            "action_id": action["id"], "incident_id": action["incident_id"], "kind": action["kind"], "role": p.get("contact_role") or "citizen",
            "contact_name": p.get("contact_name") or "", "place": p.get("place") or "", "instructions": p.get("instructions") or "",
            "incident_summary": action.get("incident_summary") or "", "incident_lat": str(FIRE["lat"]), "incident_lon": str(FIRE["lon"]),
        })

    def weather(self, incident_id: str, obs: dict) -> None:
        self.rt.run("weather_inject", {"incident_id": incident_id, **{k: str(v) for k, v in obs.items()}})


class CloudDriver:
    """Dispara los workflows reales en HappyRobot (hooks). Las llamadas de voz son manuales (navegador)."""

    def __init__(self, client, narrator: Narrator):
        from ..workflows.deploy import load_state

        self.c = client
        self.n = narrator
        self.wf = load_state()["workflows"]

    def _run(self, key: str, payload: dict, wait: int = 90) -> None:
        r = self.c.workflows.trigger(self.wf[key]["id"], payload)
        rid = r.get("run_id")
        self.n.say(f"  → run {key} {rid} (ver en la plataforma)")
        for _ in range(wait // 3):
            time.sleep(3)
            st = self.c.runs.get(rid).get("data", {}).get("status")
            if st in ("completed", "succeeded", "failed", "canceled"):
                self.n.say(f"    estado: {st}")
                return

    def citizen_call(self, aviso: dict) -> None:
        self.n.say("  (cloud) el aviso ciudadano se inyecta como evidencia directa; la llamada real se hace desde el dashboard")
        self.ingest({"source_type": "call", "source_ref": "sim:112", "lat": str(FIRE["lat"]), "lon": str(FIRE["lon"]), "observed_at": "",
                     "reliability": "", "incident_type": aviso.get("tipo", "wildfire"), "summary": aviso.get("descripcion", ""),
                     "details_json": json.dumps(aviso, ensure_ascii=False)})

    def ingest(self, envelope: dict) -> None:
        self._run("ingest", envelope)

    def approve(self, action_id: str, operator: str = "operador-demo") -> None:
        self._run("approve", {"action_id": action_id, "decision": "approve", "operator": operator, "note": ""})

    def pick_up(self, action: dict, answer: dict) -> None:
        self.n.say(f"  (cloud) descuelga la llamada de {action['contact_name']} desde el dashboard (Sala de llamadas)")

    def weather(self, incident_id: str, obs: dict) -> None:
        self._run("weather_inject", {"incident_id": incident_id, **{k: str(v) for k, v in obs.items()}})


def run(db: Database, driver, n: Narrator, reset: bool = True, pause: float = 0.0) -> dict:
    from ..twin import seed

    if reset:
        seed.reset_operational_data(db)
        n.say("Datos operativos reiniciados (activos, contactos, medios y config se conservan).")

    n.step("1 · Un vecino llama al 112 virtual")
    driver.citizen_call({
        "lugar_ref": "serra", "lugar_texto": "el monte detrás de la urbanización alta de Serra", "tipo": "wildfire",
        "descripcion": "Humo negro muy denso y llamas en el pinar; el humo va hacia el pueblo", "direccion_fuego": "hacia el pueblo (este)",
        "personas_en_peligro": "ninguna que sepa", "nombre": "Vicent Soler", "telefono": "+34600000099",
    })
    print_state(db, n)
    time.sleep(pause)

    n.step("2 · El satélite confirma: dos anomalías térmicas (FIRMS) + viento del oeste 40 km/h")
    inc = _table(db, "SELECT id::text AS id FROM incidents ORDER BY created_at DESC LIMIT 1")[0]["id"]
    driver.weather(inc, {"wind_speed_kmh": 40, "wind_dir_deg": 270, "temp_c": 33, "humidity": 18, "source": "aemet-sim"})
    for env in firms.synthetic(FIRE["lat"], FIRE["lon"], n=2):
        driver.ingest(env)
    print_state(db, n)
    time.sleep(pause)

    n.step("3 · El operador aprueba (1 clic) las evacuaciones y la coordinación")
    pending = _table(db, "SELECT id::text AS id, kind FROM actions WHERE status = 'proposed' AND kind IN ('evacuate_call','coordination_call','dispatch') ORDER BY priority")
    for a in pending:
        driver.approve(a["id"])
        n.say(f"  ✓ aprobada {a['kind']} {a['id'][:8]}")
    print_state(db, n)
    time.sleep(pause)

    n.step("4 · Se descuelgan las llamadas (web call): el agente habla con cada persona")
    ready = _table(db, """SELECT a.id::text AS id, a.incident_id::text AS incident_id, a.kind, a.payload::text AS payload, c.name AS contact_name,
                                 i.summary AS incident_summary FROM actions a JOIN contacts c ON c.id = a.contact_id JOIN incidents i ON i.id = a.incident_id
                          WHERE a.status = 'ready' ORDER BY a.priority""")
    answers = {
        "María Ferrer": {"outcome": "needs_help", "notes": "Tiene movilidad reducida y necesita ayuda para salir. Ve llamas a 300 m de su casa, avanzando hacia el colegio.",
                         "new_info": "Llamas a unos 300 m de la urbanización alta de Serra, avanzando hacia el colegio; una vecina mayor sola en la casa de al lado"},
        "*": {"outcome": "accepted", "notes": "Confirma que sale ahora hacia el punto de encuentro.", "new_info": ""},
    }
    for a in ready:
        driver.pick_up(a, answers.get(a["contact_name"], answers["*"]))
        n.say(f"  ☎ {a['kind']} con {a['contact_name']} → {answers.get(a['contact_name'], answers['*'])['outcome']}")
    print_state(db, n)
    time.sleep(pause)

    n.step("5 · El viento gira 180° (ahora del este): re-evaluación y aviso en las llamadas en curso")
    driver.weather(inc, {"wind_speed_kmh": 45, "wind_dir_deg": 90, "temp_c": 34, "humidity": 15, "source": "aemet-sim"})
    print_state(db, n)
    if getattr(driver, "signals", None):
        for s in driver.signals:
            n.say(f"  📡 signal {s.get('key')}: {s.get('payload', {}).get('message')}")

    n.step("Resumen")
    counts = {r["status"]: r["n"] for r in _table(db, "SELECT status, count(*) AS n FROM actions GROUP BY status")}
    ev = _table(db, "SELECT source_type, count(*) AS n FROM evidence GROUP BY source_type")
    n.say(f"  evidencias: {', '.join(f'{e['source_type']}={e['n']}' for e in ev)}")
    n.say(f"  acciones por estado: {counts}")
    n.say(f"  planes generados: {_table(db, 'SELECT count(*) AS n FROM plans')[0]['n']}")
    return {"incident_id": inc, "actions": counts}
