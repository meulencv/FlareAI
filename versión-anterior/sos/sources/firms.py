"""NASA FIRMS (detecciones térmicas por satélite) → evidencias `firms`.

API de área (CSV): https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SENSOR}/{bbox}/{días}
Requiere MAP_KEY gratuita (FIRMS_MAP_KEY en .env). Sin key, `fetch()` devuelve [].
"""

from __future__ import annotations

import csv
import io
import json
import urllib.request

SENSORS = ("VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT")
BBOX_CALDERONA = (-0.75, 39.45, -0.10, 39.95)  # (oeste, sur, este, norte) — escenario demo


def parse_csv(text: str, min_confidence: str = "nominal") -> list[dict]:
    """CSV de FIRMS → sobres de evidencia. `confidence` en VIIRS es low|nominal|high."""
    order = {"low": 0, "nominal": 1, "high": 2}
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        conf = (row.get("confidence") or "nominal").lower()
        if order.get(conf, 1) < order.get(min_confidence, 1):
            continue
        rel = {"low": 0.55, "nominal": 0.8, "high": 0.92}.get(conf, 0.8)
        acq = f"{row.get('acq_date')}T{(row.get('acq_time') or '0000').zfill(4)[:2]}:{(row.get('acq_time') or '0000').zfill(4)[2:]}:00Z"
        out.append({
            "source_type": "firms",
            "source_ref": f"firms:{row.get('satellite')}:{row.get('acq_date')}:{row.get('acq_time')}:{row.get('latitude')},{row.get('longitude')}",
            "lat": row.get("latitude"), "lon": row.get("longitude"), "observed_at": acq, "reliability": str(rel),
            "incident_type": "wildfire",
            "summary": f"Anomalía térmica satélite {row.get('satellite')} FRP={row.get('frp')} MW, confianza {conf}",
            "details_json": json.dumps({k: row.get(k) for k in ("bright_ti4", "bright_ti5", "frp", "daynight", "scan", "track", "instrument")}),
        })
    return out


def fetch(map_key: str | None, bbox: tuple[float, float, float, float] = BBOX_CALDERONA, days: int = 1, sensor: str = SENSORS[0]) -> list[dict]:
    if not map_key:
        return []
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{sensor}/{','.join(str(b) for b in bbox)}/{days}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sos-crisis-engine/1.0"}), timeout=60) as r:
        return parse_csv(r.read().decode())


def synthetic(lat: float, lon: float, n: int = 2, frp: float = 45.0, when: str = "") -> list[dict]:
    """Detecciones sintéticas alrededor de un punto (para el simulador)."""
    out = []
    for i in range(n):
        dlat, dlon = (i % 2) * 0.004 - 0.002, (i // 2) * 0.004 - 0.002
        out.append({
            "source_type": "firms", "source_ref": f"firms:SIM:{i}:{lat + dlat:.4f},{lon + dlon:.4f}",
            "lat": f"{lat + dlat:.4f}", "lon": f"{lon + dlon:.4f}", "observed_at": when, "reliability": "0.85", "incident_type": "wildfire",
            "summary": f"Anomalía térmica satélite (simulada) FRP={frp + 10 * i} MW, confianza high",
            "details_json": json.dumps({"frp": frp + 10 * i, "instrument": "VIIRS", "simulated": True}),
        })
    return out
