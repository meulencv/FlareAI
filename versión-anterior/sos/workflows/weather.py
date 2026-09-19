"""Meteo: registro de observaciones, detección de giro de viento y re-evaluación.

- WF-Weather-Inject (hook): recibe una observación para un incidente (la envía el feeder o el
  simulador), la guarda, compara con la anterior y, si el giro supera `config.wind_shift_deg`,
  re-evalúa el incidente (WF-Assess, reason=wind_shift) y publica un **signal** al topic
  `incident.<id>` para que los agentes de voz en llamada cambien las instrucciones en directo.
- WF-Weather-Feeder (cron cada 5 min): para cada incidente abierto consulta Open-Meteo (sin API
  key) y llama a WF-Weather-Inject.
"""

from ._builder import CallWorkflow, HttpGet, HttpPost, Loop, Otherwise, P, Paths, Python, Raw, Ref, Trigger, TwinSQL, TwinWrite, When, WorkflowSpec
from ._sqlgen import SQL_HELPERS

INJECT_SAMPLE = {"incident_id": "00000000-0000-0000-0000-000000000000", "wind_speed_kmh": "40", "wind_dir_deg": "270",
                 "temp_c": "31", "humidity": "20", "source": "open-meteo"}

SQL_PREV = SQL_HELPERS + r'''
iid = (input_data.get("incident_id") or "").strip()
output = {"sql": ("SELECT wind_dir_deg, wind_speed_kmh, observed_at::text, i.lat, i.lon, (SELECT (value::text)::float8 FROM config WHERE key = 'wind_shift_deg') AS shift_deg "
                  "FROM incidents i LEFT JOIN LATERAL (SELECT wind_dir_deg, wind_speed_kmh, observed_at FROM weather_observations w WHERE w.incident_id = i.id ORDER BY observed_at DESC, created_at DESC LIMIT 1) w ON true "
                  "WHERE i.id = %s") % q(iid)}
'''

DELTA = r'''
import json as _json, uuid as _uuid
def num(v):
    try: return float(v)
    except (TypeError, ValueError): return None
rows = input_data.get("rows") or "[]"
try: rows = _json.loads(rows) if isinstance(rows, str) else rows
except Exception: rows = []
prev = rows[0] if rows else {}
new_dir = num(input_data.get("wind_dir_deg")); prev_dir = num(prev.get("wind_dir_deg"))
threshold = num(prev.get("shift_deg")) or 60.0
delta = None
if new_dir is not None and prev_dir is not None:
    delta = abs((new_dir - prev_dir + 180) % 360 - 180)
shift = delta is not None and delta >= threshold
output = {"obs_id": str(_uuid.uuid4()), "lat": prev.get("lat", ""), "lon": prev.get("lon", ""), "prev_dir": prev_dir if prev_dir is not None else "",
          "delta": delta if delta is not None else "", "shift": shift, "threshold": threshold,
          "signal_key": "incident." + (input_data.get("incident_id") or ""),
          "signal_payload": _json.dumps({"event": "wind_shift", "incident_id": input_data.get("incident_id"), "wind_dir_deg": new_dir,
                                         "wind_speed_kmh": num(input_data.get("wind_speed_kmh")), "delta_deg": delta,
                                         "message": "ATENCIÓN: el viento ha girado %s grados. Las zonas amenazadas cambian; espere nuevas instrucciones del centro y no vuelva a su domicilio." % (round(delta) if delta is not None else "?")}, ensure_ascii=False)}
'''

T = "entrada"

inject = WorkflowSpec(
    key="weather_inject",
    name="SOS · Meteo: observación y giro de viento",
    icon="wind",
    description="Guarda una observación meteo; si el viento gira, re-evalúa y avisa a las llamadas en curso.",
    trigger=Trigger(T, "incoming_hook", config={"callable_by_workflows": True}, sample=INJECT_SAMPLE).add(
        Python("sql_prev", SQL_PREV, inputs={"incident_id": Ref(T, "incident_id")}, outputs={"sql": "SELECT 1"}).add(
            TwinSQL("previa", Raw(Ref("sql_prev", "sql")), max_rows=1,
                    outputs={"rows": [{"wind_dir_deg": 270.0, "wind_speed_kmh": 40.0, "observed_at": "", "lat": 39.7, "lon": -0.47, "shift_deg": 60.0}]}).add(
                Python("delta", DELTA, inputs={"rows": Ref("previa", "rows"), "incident_id": Ref(T, "incident_id"),
                                                 "wind_dir_deg": Ref(T, "wind_dir_deg"), "wind_speed_kmh": Ref(T, "wind_speed_kmh")},
                       outputs={"obs_id": "00000000-0000-0000-0000-000000000004", "lat": 39.7, "lon": -0.47, "prev_dir": 270.0, "delta": 180.0,
                                "shift": True, "threshold": 60.0, "signal_key": "incident.x", "signal_payload": "{}"}).add(
                    TwinWrite(
                        "guardar_obs", "weather_observations", primary="id",
                        values={
                            "id": ("uuid", Ref("delta", "obs_id")),
                            "incident_id": ("uuid", Ref(T, "incident_id")),
                            "lat": ("float8", Ref("delta", "lat")),
                            "lon": ("float8", Ref("delta", "lon")),
                            "wind_speed_kmh": ("float8", Ref(T, "wind_speed_kmh")),
                            "wind_dir_deg": ("float8", Ref(T, "wind_dir_deg")),
                            "temp_c": ("float8", Ref(T, "temp_c")),
                            "humidity": ("float8", Ref(T, "humidity")),
                            "observed_at": ("timestamp", Ref("$time", "now_iso")),
                            "source": ("text", Ref(T, "source")),
                        },
                        outputs={"ok": True},
                    ).add(
                        Paths(
                            "rutas",
                            When(
                                "giro", Ref("delta", "shift"), "boolean_true", None,
                                HttpPost(
                                    "signal", Raw(Ref("$vars", "HAPPYROBOT_API_BASE"), "/signals/"),
                                    Raw('{"key": "', Ref("delta", "signal_key"), '", "env": "production", "payload": ', Ref("delta", "signal_payload"), "}"),
                                    headers={"Authorization": P("Bearer ", Ref("$vars", "HAPPYROBOT_API_KEY"))},
                                    outputs={"status": "published"}, ignore_5xx=True,
                                ).add(
                                    CallWorkflow("reevaluar", "assess", data={"incident_id": Ref(T, "incident_id"), "reason": "wind_shift"}, fire_and_forget=True)
                                ),
                            ),
                            Otherwise("sin_giro", Python("fin", "output={'shift': False}", outputs={"shift": False})),
                        )
                    )
                )
            )
        )
    ),
)

PARSE_METEO = r'''
import json as _json
def g(d, *ks):
    for k in ks:
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d if d != {} else ""
cur = input_data.get("current") or "{}"
try: cur = _json.loads(cur) if isinstance(cur, str) else cur
except Exception: cur = {}
output = {"wind_speed_kmh": cur.get("wind_speed_10m", ""), "wind_dir_deg": cur.get("wind_direction_10m", ""),
          "temp_c": cur.get("temperature_2m", ""), "humidity": cur.get("relative_humidity_2m", ""), "ok": bool(cur)}
'''

feeder = WorkflowSpec(
    key="weather_feeder",
    name="SOS · Meteo: sondeo Open-Meteo (cron)",
    icon="cloud",
    description="Cada 5 minutos consulta el viento en cada incidente abierto y lo inyecta en el sistema.",
    trigger=Trigger(T, "cron", config={"cron": {"expression": "*/5 * * * *"}}).add(
        TwinSQL("abiertos", "SELECT id::text AS id, lat, lon FROM incidents WHERE status NOT IN ('closed','dismissed')", max_rows=50,
                outputs={"rows": [{"id": "00000000-0000-0000-0000-000000000000", "lat": 39.7, "lon": -0.47}]}).add(
            Loop(
                "por_incidente", Ref("abiertos", "rows"), "inc",
                HttpGet(
                    "open_meteo", "https://api.open-meteo.com/v1/forecast",
                    params={"latitude": Ref("por_incidente", "inc.lat"), "longitude": Ref("por_incidente", "inc.lon"),
                            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m", "wind_speed_unit": "kmh"},
                    outputs={"current": {"temperature_2m": 30.0, "relative_humidity_2m": 20.0, "wind_speed_10m": 40.0, "wind_direction_10m": 270.0}},
                ).add(
                    Python("parse", PARSE_METEO, inputs={"current": Ref("open_meteo", "current")},
                           outputs={"wind_speed_kmh": 40.0, "wind_dir_deg": 270.0, "temp_c": 30.0, "humidity": 20.0, "ok": True}).add(
                        CallWorkflow("inyectar", "weather_inject", fire_and_forget=True,
                                     data={"incident_id": Ref("por_incidente", "inc.id"), "wind_speed_kmh": Ref("parse", "wind_speed_kmh"),
                                           "wind_dir_deg": Ref("parse", "wind_dir_deg"), "temp_c": Ref("parse", "temp_c"),
                                           "humidity": Ref("parse", "humidity"), "source": "open-meteo"})
                    )
                ),
            )
        )
    ),
)
