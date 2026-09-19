"""WF-Assess: el "cerebro". Un Reasoning Agent evalúa el caso con todo su contexto y decide.

Entrada (Workflow Function): incident_id, reason (new_evidence | wind_shift | call_result | manual).

Flujo:
  contexto  (Query Twin SQL) → una fila con JSON (texto) de incidente, evidencias, meteo, activos,
             medios, contactos y config.
  riesgo    (Python, motor determinista `sos.risk.engine`) → activos amenazados, score, prioridad,
             medios recomendados.
  resumen   (Python) → texto compacto para el prompt.
  analista  (Reasoning Agent "Analista de crisis") con tools que ESCRIBEN en Twin:
      guardar_evaluacion → incidents (status, confidence, risk, priority, summary, ai_assessment)
      guardar_plan       → plans (+ actualiza incidents.plan_id)
      proponer_accion    → actions (proposed; si no requiere aprobación → Call WF-Execute)
  El agente no devuelve texto útil aguas abajo: todo lo que decide queda en Twin vía tools.
"""

from __future__ import annotations

from pathlib import Path

from ._builder import Agent, CallWorkflow, Otherwise, Paths, Prompt, Python, Raw, Ref, Tool, Trigger, TwinSQL, TwinWrite, When, WorkflowSpec
from ._sqlgen import SQL_HELPERS

ENGINE_SRC = (Path(__file__).resolve().parent.parent / "risk" / "engine.py").read_text()

SAMPLE = {"incident_id": "00000000-0000-0000-0000-000000000000", "reason": "new_evidence"}

CONTEXT_SQL = SQL_HELPERS + r'''
iid = (input_data.get("incident_id") or "").strip()
sql = """
SELECT
  row_to_json(i)::text AS incident,
  (SELECT COALESCE(json_agg(e), '[]')::text FROM (
      SELECT id::text, source_type, source_ref, lat, lon, observed_at, reliability, payload
      FROM evidence WHERE incident_id = i.id ORDER BY observed_at DESC, created_at DESC LIMIT 25) e) AS evidence,
  (SELECT COALESCE(row_to_json(w), '{}')::text FROM (
      SELECT wind_speed_kmh, wind_dir_deg, temp_c, humidity, observed_at, source
      FROM weather_observations
      WHERE incident_id = i.id OR (%s <= 30 AND observed_at > now() - interval '3 hours')
      ORDER BY (incident_id = i.id) DESC, observed_at DESC, created_at DESC LIMIT 1) w) AS weather,
  (SELECT COALESCE(json_agg(a), '[]')::text FROM (
      SELECT id::text, ref, name, kind, lat, lon, population, insured_value, carbon_credit_value, hazard_class, priority_weight
      FROM assets WHERE %s <= 40) a) AS assets,
  (SELECT COALESCE(json_agg(r), '[]')::text FROM (
      SELECT r.id::text, r.ref, r.name, r.kind, r.capabilities, r.lat, r.lon, r.status, r.assigned_incident_id::text,
             c.ref AS contact_ref, c.name AS contact_name
      FROM resources r LEFT JOIN contacts c ON c.id = r.contact_id) r) AS resources,
  (SELECT COALESCE(json_agg(c), '[]')::text FROM (
      SELECT c.id::text, c.ref, c.name, c.role, c.phone, c.priority, c.notes, a.ref AS asset_ref, a.name AS asset_name
      FROM contacts c LEFT JOIN assets a ON a.id = c.asset_id ORDER BY c.role, c.priority) c) AS contacts,
  (SELECT COALESCE(json_agg(x), '[]')::text FROM (
      SELECT kind, status, rationale, created_at FROM actions WHERE incident_id = i.id ORDER BY created_at DESC LIMIT 20) x) AS prior_actions,
  (SELECT COALESCE(json_object_agg(key, value), '{}')::text FROM config) AS config
FROM incidents i WHERE i.id = %s
""" % (haversine_sql("lat", "lon", "i.lat", "i.lon"), haversine_sql("lat", "lon", "i.lat", "i.lon"), q(iid))
output = {"sql": " ".join(sql.split())}
'''

RIESGO = ENGINE_SRC + r'''

import json as _json

def _load(v, default):
    if v in (None, ""):
        return default
    if isinstance(v, (dict, list)):
        return v
    try:
        return _json.loads(v)
    except Exception:
        return default

incident = _load(input_data.get("incident"), {})
weather = _load(input_data.get("weather"), {}) or None
assets = _load(input_data.get("assets"), [])
resources = _load(input_data.get("resources"), [])
config = _load(input_data.get("config"), {})
if incident:
    risk = compute_risk(incident, weather if weather and weather.get("wind_dir_deg") is not None else None, assets, resources, config)
else:
    risk = {"error": "incidente no encontrado", "risk_score": 0, "priority": 0, "priority_label": "unknown",
            "threatened_assets": [], "recommended_resources": [], "population_at_risk": 0, "needed_capabilities": []}
output = {
    "risk_json": _json.dumps(risk, ensure_ascii=False),
    "risk_score": risk.get("risk_score", 0),
    "priority": risk.get("priority", 0),
    "priority_label": risk.get("priority_label", "unknown"),
    "population_at_risk": risk.get("population_at_risk", 0),
    "threatened_refs": ",".join(t.get("ref") or "" for t in risk.get("threatened_assets", [])),
}
'''

RESUMEN = r'''
import json as _json

def _load(v, default):
    if v in (None, ""):
        return default
    try:
        return _json.loads(v)
    except Exception:
        return default

inc = _load(input_data.get("incident"), {})
ev = _load(input_data.get("evidence"), [])
wx = _load(input_data.get("weather"), {})
risk = _load(input_data.get("risk"), {})
contacts = _load(input_data.get("contacts"), [])
resources = _load(input_data.get("resources"), [])
prior = _load(input_data.get("prior_actions"), [])
cfg = _load(input_data.get("config"), {})
hints = cfg.get("verification_hints", {}) if isinstance(cfg, dict) else {}
auto = cfg.get("auto_approve_kinds", []) if isinstance(cfg, dict) else []

L = []
L.append("## Incidente")
L.append("id=%s tipo=%s estado=%s lat=%s lon=%s creado=%s" % (inc.get("id"), inc.get("type"), inc.get("status"), inc.get("lat"), inc.get("lon"), inc.get("created_at")))
if inc.get("summary"): L.append("resumen previo: %s" % inc.get("summary"))
if inc.get("ai_assessment") and inc.get("ai_assessment") != {}: L.append("evaluación previa: %s" % _json.dumps(inc.get("ai_assessment"), ensure_ascii=False)[:600])
L.append("motivo de esta evaluación: %s" % input_data.get("reason"))
L.append("\n## Evidencias (%d, más recientes primero)" % len(ev))
for e in ev[:25]:
    p = e.get("payload") or {}
    if isinstance(p, dict): p = {k: v for k, v in p.items() if k not in ("raw",)}
    L.append("- [%s] %s fiab=%s (%s,%s) %s :: %s" % (e.get("source_type"), e.get("observed_at"), e.get("reliability"), e.get("lat"), e.get("lon"), e.get("source_ref"), _json.dumps(p, ensure_ascii=False)[:300]))
L.append("\n## Meteo")
L.append(_json.dumps(wx, ensure_ascii=False) if wx else "sin datos meteorológicos")
L.append("\n## Riesgo (motor determinista)")
L.append("score=%s prioridad=%s (%s) población_en_riesgo=%s avance=%s km/h rumbo=%s alcance=%s km" % (
    risk.get("risk_score"), risk.get("priority"), risk.get("priority_label"), risk.get("population_at_risk"),
    risk.get("spread_kmh"), risk.get("spread_heading_deg"), risk.get("reach_km")))
L.append("capacidades necesarias: %s" % ",".join(risk.get("needed_capabilities", [])))
L.append("activos amenazados (orden ETA):")
for t in risk.get("threatened_assets", []):
    L.append("- %s (%s) ref=%s a %s km, ETA %s h, población %s, score %s [%s]" % (t.get("name"), t.get("kind"), t.get("ref"), t.get("distance_km"), t.get("eta_hours"), t.get("population"), t.get("score"), t.get("reason")))
L.append("medios recomendados (compatibles primero):")
for r in risk.get("recommended_resources", [])[:8]:
    L.append("- %s (%s) ref=%s compatible=%s ETA %s min" % (r.get("name"), r.get("kind"), r.get("ref"), r.get("compatible"), r.get("eta_min")))
L.append("\n## Contactos disponibles (ref → quién)")
for c in contacts:
    L.append("- ref=%s %s · %s · zona=%s%s" % (c.get("ref"), c.get("name"), c.get("role"), c.get("asset_ref"), (" · " + c["notes"]) if c.get("notes") else ""))
L.append("\n## Medios (ref → estado)")
for r in resources:
    L.append("- ref=%s %s · %s · caps=%s · estado=%s" % (r.get("ref"), r.get("name"), r.get("kind"), r.get("capabilities"), r.get("status")))
if prior:
    L.append("\n## Acciones ya propuestas/ejecutadas para este incidente")
    for a in prior:
        L.append("- %s [%s] %s" % (a.get("kind"), a.get("status"), (a.get("rationale") or "")[:120]))
L.append("\n## Pistas de verificación (config, NO son reglas duras)")
L.append(_json.dumps(hints, ensure_ascii=False)[:800])
L.append("Acciones que se ejecutan sin aprobación humana: %s" % auto)
output = {"texto": "\n".join(L), "n_evidence": len(ev), "auto_approve_kinds": _json.dumps(auto)}
'''

PROMPT_ANALISTA = """# Rol
Eres el **Analista de crisis** de un centro de coordinación de emergencias (España). Evalúas UN incidente
con todo su contexto y decides: si es real, su prioridad, el plan y las acciones concretas. Trabajas en
español, con criterio operativo y sin inventar datos que no estén en el contexto.

# Contexto del caso
{{CTX}}

# Cómo decidir
1. **Verificación**: valora la coherencia de las evidencias (fuentes distintas, cercanía espacial y
   temporal, fiabilidad de cada fuente, detalle del relato). Varias fuentes independientes que coinciden
   → alta confianza. Una sola llamada sin más → "candidate" con confianza baja, salvo relato muy
   concreto. Datos contradictorios → confianza media y pide reconocimiento (dron) antes de evacuar.
   Si claramente es un falso positivo → "dismissed".
2. **Prioridad**: manda el riesgo para vidas humanas en la trayectoria del viento (usa el motor de
   riesgo: activos amenazados y ETA). Después, activos críticos (hospital, colegio, planta química),
   activos asegurados y reservas con bonos de carbono.
3. **Medios**: agua/hidroaviones para masa forestal; espuma/hazmat para industrial, químico o barcos.
   Usa solo medios `available` y compatibles.
4. **Notificación**: primero ciudadanos en la trayectoria (menor ETA primero), luego mando de bomberos,
   policía/tráfico, alcaldía.

# Qué debes hacer (usa las herramientas; NO escribas nada fuera de ellas)
- Llama **exactamente una vez** a `guardar_evaluacion` con tu veredicto.
- Si el veredicto es `verified` o `active` y la prioridad es ≥ 2: llama **una vez** a `guardar_plan`
  y después a `proponer_accion` **una vez por acción** (máximo 6 acciones): una `evacuate_call` por
  cada contacto ciudadano cuya zona esté amenazada (orden de ETA), una `coordination_call` al mando
  más adecuado, y `dispatch` por cada medio que asignes. No repitas acciones ya propuestas para este
  incidente salvo que cambie la situación (p.ej. giro de viento → nuevas zonas).
- Si el veredicto es `candidate` con confianza < 0.6 y hay dron disponible: propone un `dispatch`
  del dron para confirmar (reconocimiento), nada más.
- Termina con una frase de cierre breve. No vuelvas a llamar a una herramienta que ya haya respondido OK.
"""

T = "entrada"


def _ctx_ref(field: str) -> Ref:
    return Ref("contexto", f"rows.0.{field}")


spec = WorkflowSpec(
    key="assess",
    name="SOS · Evaluación de incidente",
    icon="brain",
    description="Un Reasoning Agent evalúa el incidente: verificación, riesgo, plan y acciones.",
    trigger=Trigger(T, "workflow_function_request", sample=SAMPLE).add(
        Python(
            "sql_contexto", CONTEXT_SQL, inputs={"incident_id": Ref(T, "incident_id")}, outputs={"sql": "SELECT 1"},
        ).add(
            TwinSQL(
                "contexto", Raw(Ref("sql_contexto", "sql")), max_rows=1,
                outputs={"rows": [{"incident": "{}", "evidence": "[]", "weather": "{}", "assets": "[]", "resources": "[]",
                                   "contacts": "[]", "prior_actions": "[]", "config": "{}"}]},
            ).add(
                Python(
                    "riesgo", RIESGO, profile="standard",
                    inputs={"incident": _ctx_ref("incident"), "weather": _ctx_ref("weather"), "assets": _ctx_ref("assets"),
                            "resources": _ctx_ref("resources"), "config": _ctx_ref("config")},
                    outputs={"risk_json": "{}", "risk_score": 0.0, "priority": 1, "priority_label": "low",
                             "population_at_risk": 0, "threatened_refs": ""},
                ).add(
                    Python(
                        "resumen", RESUMEN,
                        inputs={"incident": _ctx_ref("incident"), "evidence": _ctx_ref("evidence"), "weather": _ctx_ref("weather"),
                                "risk": Ref("riesgo", "risk_json"), "contacts": _ctx_ref("contacts"), "resources": _ctx_ref("resources"),
                                "prior_actions": _ctx_ref("prior_actions"), "config": _ctx_ref("config"), "reason": Ref(T, "reason")},
                        outputs={"texto": "## Incidente ...", "n_evidence": 1, "auto_approve_kinds": "[\"notify\"]"},
                    ).add(
                        Agent(
                            "analista", "reasoning_agent",
                            Prompt(PROMPT_ANALISTA.split("{{CTX}}")[0], Ref("resumen", "texto"), PROMPT_ANALISTA.split("{{CTX}}")[1]),
                            config={"name": [{"type": "paragraph", "children": [{"text": "Analista de crisis"}]}],
                                    "maxSessionDurationMinutes": [{"type": "paragraph", "children": [{"text": "6"}]}]},
                            initial_message=None,
                            model=None,
                        ).add(
                            # ---- tool 1: veredicto ----
                            Tool(
                                "guardar_evaluacion",
                                "Guarda tu veredicto sobre el incidente. Llámala exactamente una vez.",
                                [
                                    {"name": "status", "description": "verified | active | candidate | dismissed | contained", "required": True, "example": "verified"},
                                    {"name": "confidence", "description": "Confianza 0..1 de que el incidente es real", "required": True, "example": "0.85"},
                                    {"name": "incident_type", "description": "wildfire | industrial | chemical | maritime | flood | unknown", "required": True, "example": "wildfire"},
                                    {"name": "summary", "description": "Resumen operativo en 1-2 frases (qué, dónde, hacia dónde avanza)", "required": True, "example": "Incendio forestal al oeste de Serra, avanza hacia el este con viento de 40 km/h"},
                                    {"name": "rationale", "description": "Por qué has llegado a este veredicto (fuentes, coherencia)", "required": True, "example": "Llamada + 2 detecciones FIRMS coincidentes en 1 km"},
                                ],
                                Python(
                                    "eval_prep",
                                    r'''
import json as _json
c = input_data.get("confidence");
try: c = max(0.0, min(1.0, float(c)))
except Exception: c = 0.5
st = (input_data.get("status") or "candidate").strip().lower()
if st not in ("verified", "active", "candidate", "dismissed", "contained", "closed"): st = "candidate"
try: risk = _json.loads(input_data.get("risk_json") or "{}")
except Exception: risk = {}
assessment = {"status": st, "confidence": c, "rationale": input_data.get("rationale"), "risk": {k: risk.get(k) for k in ("risk_score", "priority", "priority_label", "population_at_risk", "spread_heading_deg", "reach_km")},
              "threatened_assets": [t.get("ref") for t in risk.get("threatened_assets", [])], "evaluated_at": input_data.get("now"), "run_id": input_data.get("run_id")}
output = {"status": st, "confidence": c, "incident_type": (input_data.get("incident_type") or "unknown").lower(),
          "summary": (input_data.get("summary") or "")[:400], "assessment_json": _json.dumps(assessment, ensure_ascii=False),
          "risk_score": risk.get("risk_score", 0), "priority": risk.get("priority", 0)}
''',
                                    inputs={"status": Ref("guardar_evaluacion", "status"), "confidence": Ref("guardar_evaluacion", "confidence"),
                                            "incident_type": Ref("guardar_evaluacion", "incident_type"), "summary": Ref("guardar_evaluacion", "summary"),
                                            "rationale": Ref("guardar_evaluacion", "rationale"), "risk_json": Ref("riesgo", "risk_json"),
                                            "now": Ref("$time", "now_iso"), "run_id": Ref("$current", "run_id")},
                                    outputs={"status": "verified", "confidence": 0.8, "incident_type": "wildfire", "summary": "s",
                                             "assessment_json": "{}", "risk_score": 10.0, "priority": 3},
                                ).add(
                                    TwinWrite(
                                        "eval_write", "incidents", primary="id",
                                        values={
                                            "id": ("uuid", Ref(T, "incident_id")),
                                            "type": ("text", Ref("eval_prep", "incident_type")),
                                            "status": ("text", Ref("eval_prep", "status")),
                                            "lat": ("float8", _ctx_ref("incident.lat")),
                                            "lon": ("float8", _ctx_ref("incident.lon")),
                                            "confidence": ("float8", Ref("eval_prep", "confidence")),
                                            "risk_score": ("float8", Ref("eval_prep", "risk_score")),
                                            "priority": ("int8", Ref("eval_prep", "priority")),
                                            "summary": ("text", Ref("eval_prep", "summary")),
                                            "ai_assessment": ("jsonb", Ref("eval_prep", "assessment_json")),
                                            "updated_at": ("timestamp", Ref("$time", "now_iso")),
                                        },
                                        outputs={"ok": True},
                                    )
                                ),
                                expose=["status", "confidence"],
                            ),
                            # ---- tool 2: plan ----
                            Tool(
                                "guardar_plan",
                                "Guarda el plan de respuesta del incidente (una vez por evaluación). Después propón las acciones con proponer_accion.",
                                [
                                    {"name": "summary", "description": "Plan en 2-4 frases: prioridades, estrategia, medios", "required": True},
                                    {"name": "priorities", "description": "Lista ordenada de zonas/activos a proteger, separados por ';'", "required": True, "example": "Serra; CEIP Sant Josep; Segart"},
                                    {"name": "resource_plan", "description": "Medios y cometido, separados por ';'", "required": True, "example": "brig_forestal: ataque directo flanco este; hidro_1: descargas sobre cabeza"},
                                    {"name": "notification_order", "description": "Orden de aviso, refs de contacto separadas por ';'", "required": True, "example": "maria; pep; cmd_forestal; policia"},
                                ],
                                Python(
                                    "plan_prep",
                                    r'''
import json as _json, uuid as _uuid
def lst(s): return [x.strip() for x in (s or "").split(";") if x.strip()]
output = {"plan_id": str(_uuid.uuid4()), "summary": (input_data.get("summary") or "")[:1000],
          "priorities": _json.dumps(lst(input_data.get("priorities"))), "resource_plan": _json.dumps(lst(input_data.get("resource_plan"))),
          "notification_order": _json.dumps(lst(input_data.get("notification_order")))}
''',
                                    inputs={"summary": Ref("guardar_plan", "summary"), "priorities": Ref("guardar_plan", "priorities"),
                                            "resource_plan": Ref("guardar_plan", "resource_plan"), "notification_order": Ref("guardar_plan", "notification_order")},
                                    outputs={"plan_id": "00000000-0000-0000-0000-000000000002", "summary": "s", "priorities": "[]", "resource_plan": "[]", "notification_order": "[]"},
                                ).add(
                                    TwinWrite(
                                        "plan_write", "plans", primary="id",
                                        values={
                                            "id": ("uuid", Ref("plan_prep", "plan_id")),
                                            "incident_id": ("uuid", Ref(T, "incident_id")),
                                            "summary": ("text", Ref("plan_prep", "summary")),
                                            "priorities": ("jsonb", Ref("plan_prep", "priorities")),
                                            "resource_plan": ("jsonb", Ref("plan_prep", "resource_plan")),
                                            "notification_order": ("jsonb", Ref("plan_prep", "notification_order")),
                                            "status": ("text", "current"),
                                            "created_by_run": ("text", Ref("$current", "run_id")),
                                        },
                                        outputs={"ok": True},
                                    )
                                ),
                                expose=["plan_id"],
                            ),
                            # ---- tool 3: acción ----
                            Tool(
                                "proponer_accion",
                                "Propone UNA acción concreta para el incidente. Las que requieren aprobación humana quedan pendientes en el panel; las demás se ejecutan.",
                                [
                                    {"name": "kind", "description": "evacuate_call | coordination_call | dispatch | notify", "required": True, "example": "evacuate_call"},
                                    {"name": "contact_ref", "description": "ref del contacto (para llamadas). Vacío si no aplica.", "required": False, "example": "maria"},
                                    {"name": "resource_ref", "description": "ref del medio (para dispatch). Vacío si no aplica.", "required": False, "example": "hidro_1"},
                                    {"name": "priority", "description": "1 = más urgente … 100", "required": True, "example": "1"},
                                    {"name": "instructions", "description": "Qué debe decir/hacer: instrucciones claras para el agente de voz o el medio (ruta de evacuación, punto de encuentro, cometido)", "required": True},
                                    {"name": "rationale", "description": "Por qué esta acción ahora", "required": True},
                                ],
                                Python(
                                    "accion_prep",
                                    r'''
import json as _json, uuid as _uuid
def _load(v, d):
    try: return _json.loads(v) if isinstance(v, str) and v else d
    except Exception: return d
contacts = _load(input_data.get("contacts"), []); resources = _load(input_data.get("resources"), [])
auto = _load(input_data.get("auto_approve_kinds"), [])
kind = (input_data.get("kind") or "notify").strip().lower()
cref = (input_data.get("contact_ref") or "").strip(); rref = (input_data.get("resource_ref") or "").strip()
contact = next((c for c in contacts if c.get("ref") == cref), None)
resource = next((r for r in resources if r.get("ref") == rref), None)
try: prio = int(float(input_data.get("priority") or 50))
except Exception: prio = 50
requires = kind not in auto
payload = {"instructions": input_data.get("instructions"), "contact_ref": cref, "resource_ref": rref,
           "contact_name": (contact or {}).get("name"), "contact_role": (contact or {}).get("role"), "contact_phone": (contact or {}).get("phone"),
           "place": (contact or {}).get("asset_name"), "resource_name": (resource or {}).get("name"), "channel": "webcall"}
output = {"action_id": str(_uuid.uuid4()), "kind": kind, "requires_approval": requires, "auto": (not requires),
          "contact_id": (contact or {}).get("id") or "", "resource_id": (resource or {}).get("id") or "", "priority": prio,
          "rationale": (input_data.get("rationale") or "")[:600], "payload_json": _json.dumps(payload, ensure_ascii=False),
          "status": "proposed" if requires else "approved"}
''',
                                    inputs={"kind": Ref("proponer_accion", "kind"), "contact_ref": Ref("proponer_accion", "contact_ref"),
                                            "resource_ref": Ref("proponer_accion", "resource_ref"), "priority": Ref("proponer_accion", "priority"),
                                            "instructions": Ref("proponer_accion", "instructions"), "rationale": Ref("proponer_accion", "rationale"),
                                            "contacts": _ctx_ref("contacts"), "resources": _ctx_ref("resources"),
                                            "auto_approve_kinds": Ref("resumen", "auto_approve_kinds")},
                                    outputs={"action_id": "00000000-0000-0000-0000-000000000003", "kind": "evacuate_call", "requires_approval": True, "auto": False,
                                             "contact_id": "", "resource_id": "", "priority": 1, "rationale": "r", "payload_json": "{}", "status": "proposed"},
                                ).add(
                                    TwinWrite(
                                        "accion_write", "actions", primary="id",
                                        values={
                                            "id": ("uuid", Ref("accion_prep", "action_id")),
                                            "incident_id": ("uuid", Ref(T, "incident_id")),
                                            "kind": ("text", Ref("accion_prep", "kind")),
                                            "status": ("text", Ref("accion_prep", "status")),
                                            "requires_approval": ("boolean", Ref("accion_prep", "requires_approval")),
                                            "contact_id": ("uuid", Ref("accion_prep", "contact_id")),
                                            "resource_id": ("uuid", Ref("accion_prep", "resource_id")),
                                            "priority": ("int8", Ref("accion_prep", "priority")),
                                            "rationale": ("text", Ref("accion_prep", "rationale")),
                                            "payload": ("jsonb", Ref("accion_prep", "payload_json")),
                                            "run_id": ("text", Ref("$current", "run_id")),
                                            "updated_at": ("timestamp", Ref("$time", "now_iso")),
                                        },
                                        outputs={"ok": True},
                                    ).add(
                                        Paths(
                                            "accion_rutas",
                                            When("accion_auto", Ref("accion_prep", "auto"), "boolean_true", None,
                                                 CallWorkflow("ejecutar_auto", "execute", data={"action_id": Ref("accion_prep", "action_id")}, fire_and_forget=True)),
                                            Otherwise("accion_pendiente", Python("accion_espera", "output={'pending': True}", outputs={"pending": True})),
                                        )
                                    )
                                ),
                                expose=["action_id", "kind", "status", "requires_approval"],
                            ),
                        )
                    )
                )
            )
        )
    ),
)
