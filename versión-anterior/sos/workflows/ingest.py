"""WF-Ingest: punto de entrada único de evidencias (llamadas, FIRMS, meteo, drones, simulador).

Sobre de entrada (todos los campos son texto plano; nada anidado — los objetos anidados
llegan como `map[...]` a los nodos, ver vault):

    source_type   call | firms | weather | drone | sensor | manual
    source_ref    identificador en la fuente (p.ej. "webcall:<run_id>", "firms:VIIRS:...")
    lat, lon      grados decimales
    observed_at   ISO-8601 (opcional; por defecto ahora)
    reliability   0..1 (opcional; por defecto según config.verification_hints)
    incident_type wildfire | industrial | chemical | maritime | flood | unknown (pista)
    summary       texto corto legible
    details_json  JSON string con el detalle crudo (opcional)

Flujo: preparar (Python: validar + SQL de búsqueda) → buscar (Query Twin SQL) → decidir
(Python: agrupar a incidente existente o crear uno nuevo) → guardar_incidente (Write to Twin,
upsert) → guardar_evidencia (Write to Twin) → evaluar (Call Workflow → WF-Assess).

Usa los nodos nativos de Twin (corren como la organización, sin API key).
"""

from ._builder import CallWorkflow, Python, Raw, Ref, Trigger, TwinSQL, TwinWrite, WorkflowSpec
from ._sqlgen import SQL_HELPERS

SAMPLE = {
    "source_type": "call",
    "source_ref": "webcall:demo",
    "lat": "39.70",
    "lon": "-0.47",
    "observed_at": "2026-09-18T20:00:00Z",
    "reliability": "0.5",
    "incident_type": "wildfire",
    "summary": "Humo negro detrás de Serra",
    "details_json": "{}",
}

PREPARAR = SQL_HELPERS + r'''
lat = num(input_data.get("lat")); lon = num(input_data.get("lon"))
errors = []
if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
    errors.append("lat/lon inválidos")
source_type = (input_data.get("source_type") or "manual").strip().lower()
observed_at = (input_data.get("observed_at") or "").strip() or input_data.get("now_iso") or ""
reliability = num(input_data.get("reliability"))
incident_type = (input_data.get("incident_type") or "unknown").strip().lower()
summary = (input_data.get("summary") or "").strip()
details = input_data.get("details_json") or "{}"
try:
    details_obj = _json.loads(details) if isinstance(details, str) else details
except Exception:
    details_obj = {"raw": details}

# Incidente abierto cercano (radio y ventana desde config) — el más reciente.
sql_find = (
    "SELECT id::text AS id, type, status, lat, lon FROM incidents WHERE status NOT IN ('closed','dismissed') "
    "AND created_at > now() - (%s * interval '1 hour') AND %s <= %s ORDER BY created_at DESC LIMIT 1"
    % (cfg_num("cluster_window_hours"), haversine_sql("lat", "lon", lat or 0, lon or 0), cfg_num("cluster_radius_km"))
)
output = {
    "ok": not errors, "errors": ", ".join(errors),
    "lat": lat, "lon": lon, "source_type": source_type, "source_ref": input_data.get("source_ref") or "",
    "observed_at": observed_at, "reliability": reliability if reliability is not None else "",
    "incident_type": incident_type, "summary": summary, "details": _json.dumps(details_obj, ensure_ascii=False),
    "sql_find": sql_find,
}
'''

DECIDIR = SQL_HELPERS + r'''
import uuid as _uuid
rows = input_data.get("rows") or "[]"
try:
    rows = _json.loads(rows) if isinstance(rows, str) else rows
except Exception:
    rows = []
if isinstance(rows, dict):
    rows = rows.get("rows") or []
lat = num(input_data.get("lat")); lon = num(input_data.get("lon"))
incident_type = input_data.get("incident_type") or "unknown"
summary = input_data.get("summary") or ""
reliability = num(input_data.get("reliability"))
defaults = {"call": 0.5, "firms": 0.8, "drone": 0.95, "sensor": 0.7, "weather": 0.3, "manual": 0.9}
if reliability is None:
    reliability = defaults.get(input_data.get("source_type") or "manual", 0.5)

existing = rows[0] if rows else None
is_new = existing is None
if is_new:
    output = {"incident_id": str(_uuid.uuid4()), "is_new": True, "type": incident_type, "status": "candidate",
              "inc_lat": lat, "inc_lon": lon, "inc_summary": summary[:200], "reliability": reliability}
else:
    typ = existing.get("type") or "unknown"
    output = {"incident_id": existing["id"], "is_new": False,
              "type": incident_type if typ == "unknown" else typ, "status": existing.get("status") or "candidate",
              "inc_lat": existing.get("lat", lat), "inc_lon": existing.get("lon", lon),
              "inc_summary": "", "reliability": reliability}
output["evidence_id"] = str(_uuid.uuid4())
'''

T = "entrada"

spec = WorkflowSpec(
    key="ingest",
    name="SOS · Ingesta de evidencias",
    icon="inbox",
    description="Recibe cualquier evidencia, la agrupa a un incidente y dispara la evaluación.",
    trigger=Trigger(T, "incoming_hook", config={"callable_by_workflows": True}, sample=SAMPLE).add(
        Python(
            "preparar",
            PREPARAR,
            inputs={**{k: Ref(T, k) for k in SAMPLE}, "now_iso": Ref("$time", "now_iso")},
            outputs={"ok": True, "errors": "", "lat": 39.7, "lon": -0.47, "source_type": "call", "source_ref": "x",
                     "observed_at": "2026-09-18T20:00:00Z", "reliability": 0.5, "incident_type": "wildfire",
                     "summary": "s", "details": "{}", "sql_find": "SELECT 1"},
        ).add(
            TwinSQL("buscar", Raw(Ref("preparar", "sql_find")), max_rows=1,
                    outputs={"rows": [{"id": "00000000-0000-0000-0000-000000000000", "type": "wildfire", "status": "candidate", "lat": 39.7, "lon": -0.47}]}).add(
                Python(
                    "decidir",
                    DECIDIR,
                    inputs={
                        "rows": Ref("buscar", "rows"),
                        "lat": Ref("preparar", "lat"), "lon": Ref("preparar", "lon"),
                        "source_type": Ref("preparar", "source_type"), "reliability": Ref("preparar", "reliability"),
                        "incident_type": Ref("preparar", "incident_type"), "summary": Ref("preparar", "summary"),
                    },
                    outputs={"incident_id": "00000000-0000-0000-0000-000000000000", "is_new": True, "type": "wildfire",
                             "status": "candidate", "inc_lat": 39.7, "inc_lon": -0.47, "inc_summary": "s",
                             "reliability": 0.5, "evidence_id": "00000000-0000-0000-0000-000000000001"},
                ).add(
                    TwinWrite(
                        "guardar_incidente", "incidents", primary="id",
                        values={
                            "id": ("uuid", Ref("decidir", "incident_id")),
                            "type": ("text", Ref("decidir", "type")),
                            "status": ("text", Ref("decidir", "status")),
                            "lat": ("float8", Ref("decidir", "inc_lat")),
                            "lon": ("float8", Ref("decidir", "inc_lon")),
                            "updated_at": ("timestamp", Ref("$time", "now_iso")),
                        },
                    ).add(
                        TwinWrite(
                            "guardar_evidencia", "evidence", primary="id",
                            values={
                                "id": ("uuid", Ref("decidir", "evidence_id")),
                                "incident_id": ("uuid", Ref("decidir", "incident_id")),
                                "source_type": ("text", Ref("preparar", "source_type")),
                                "source_ref": ("text", Ref("preparar", "source_ref")),
                                "lat": ("float8", Ref("preparar", "lat")),
                                "lon": ("float8", Ref("preparar", "lon")),
                                "observed_at": ("timestamp", Ref("preparar", "observed_at")),
                                "reliability": ("float8", Ref("decidir", "reliability")),
                                "payload": ("jsonb", Ref("preparar", "details")),
                                "run_id": ("text", Ref("$current", "run_id")),
                            },
                        ).add(
                            CallWorkflow(
                                "evaluar", "assess",
                                data={"incident_id": Ref("decidir", "incident_id"), "reason": "new_evidence"},
                                fire_and_forget=True,
                            )
                        )
                    )
                )
            )
        )
    ),
)
