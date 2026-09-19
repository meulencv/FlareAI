"""WF-FIRMS-Feeder (cron cada 10 min): detecciones térmicas NASA FIRMS → WF-Ingest.

Requiere la variable de workflow FIRMS_MAP_KEY (gratuita). Sin key el nodo HTTP falla y el
cron simplemente no aporta evidencias. En la demo el simulador inyecta detecciones sintéticas.
"""

from pathlib import Path

from ._builder import CallWorkflow, HttpGet, Loop, Python, Raw, Ref, Trigger, WorkflowSpec

PARSER_SRC = (Path(__file__).resolve().parent.parent / "sources" / "firms.py").read_text()

PARSE = PARSER_SRC + r'''

import json as _json
raw = input_data.get("body") or input_data.get("data") or ""
if raw.startswith("["):  # por si la plataforma ya lo ha convertido a JSON
    try:
        rows = _json.loads(raw)
        raw = "\n".join([",".join(rows[0].keys())] + [",".join(str(v) for v in r.values()) for r in rows]) if rows else ""
    except Exception:
        pass
detections = parse_csv(raw) if raw else []
output = {"detections": detections, "count": len(detections)}
'''

T = "entrada"

spec = WorkflowSpec(
    key="firms_feeder",
    name="SOS · FIRMS: sondeo satélite (cron)",
    icon="satellite",
    description="Cada 10 minutos descarga las anomalías térmicas de NASA FIRMS en la zona y las ingesta.",
    variables={"FIRMS_MAP_KEY": "", "FIRMS_BBOX": "-0.75,39.45,-0.10,39.95"},
    hidden_variables={"FIRMS_MAP_KEY"},
    trigger=Trigger(T, "cron", config={"cron": {"expression": "*/10 * * * *"}}).add(
        HttpGet(
            "firms", Raw("https://firms.modaps.eosdis.nasa.gov/api/area/csv/", Ref("$vars", "FIRMS_MAP_KEY"), "/VIIRS_SNPP_NRT/", Ref("$vars", "FIRMS_BBOX"), "/1"),
            outputs={"body": "latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight\n"},
        ).add(
            Python("parse", PARSE, inputs={"body": Ref("firms", "body"), "data": Ref("firms", "data")}, profile="standard",
                   outputs={"detections": [{"source_type": "firms", "source_ref": "x", "lat": "39.7", "lon": "-0.47", "observed_at": "", "reliability": "0.8",
                                            "incident_type": "wildfire", "summary": "s", "details_json": "{}"}], "count": 1}).add(
                Loop(
                    "por_deteccion", Ref("parse", "detections"), "det",
                    CallWorkflow("ingestar", "ingest", fire_and_forget=True,
                                 data={k: Ref("por_deteccion", f"det.{k}") for k in ("source_type", "source_ref", "lat", "lon", "observed_at", "reliability", "incident_type", "summary", "details_json")}),
                )
            )
        )
    ),
)
