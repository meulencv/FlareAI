"""Motor de riesgo: qué activos están en la trayectoria del fuego/humo y con qué urgencia.

Restricciones deliberadas: solo `math`/`json` (perfil *Standard* del Python Sandbox de
HappyRobot, sin red). Este mismo fichero se embebe en el nodo de código de WF-Assess
(ver `sos/workflows/assess`), así que lo que se testea en local es lo que corre allí.

Convenciones:
- `wind_dir_deg` es dirección meteorológica (de dónde VIENE el viento). El fuego avanza
  hacia `wind_dir_deg + 180`.
- Valores económicos en millones de euros.
- Todo peso/umbral llega en `config` (tabla Twin `config`, clave `risk`).
"""

from __future__ import annotations

import math

# ---- geometría --------------------------------------------------------------

EARTH_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Rumbo (0=N, 90=E) desde el punto 1 al punto 2."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def angle_diff(a: float, b: float) -> float:
    d = abs((a - b + 180) % 360 - 180)
    return d


# ---- modelo ------------------------------------------------------------------

DEFAULT_RISK = {
    "horizon_hours": 3,
    "cone_half_angle_deg": 30,
    "spread_kmh_per_wind_kmh": 0.12,
    "min_spread_kmh": 0.5,
    "perimeter_km": 1.0,
    "weights": {"population": 1.0, "insured_value_per_meur": 0.3, "carbon_credit_per_meur": 0.5},
    "kind_multiplier": {"hospital": 3.0, "school": 2.5, "town": 1.0, "plant": 1.5, "port": 1.2, "forest_reserve": 0.8},
    "priority_thresholds": {"critical": 500, "high": 150, "medium": 40},
}

SPEED_KMH = {"hydroplane": 250, "drone": 60, "brigade": 60, "foam_unit": 50, "police": 70}


def _merge(base: dict, override: dict | None) -> dict:
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **v}
        else:
            out[k] = v
    return out


def compute_risk(incident: dict, weather: dict | None, assets: list[dict], resources: list[dict] | None = None, config: dict | None = None) -> dict:
    """Devuelve activos amenazados (ordenados por ETA), score, prioridad y medios recomendados.

    incident: {lat, lon, type}
    weather:  {wind_speed_kmh, wind_dir_deg} (puede ser None → sin viento: solo perímetro)
    assets:   [{id|ref, name, kind, lat, lon, population, insured_value, carbon_credit_value, priority_weight}]
    resources:[{id|ref, name, kind, capabilities, lat, lon, status}]
    config:   {"risk": {...}, "hazard_capabilities": {...}}
    """
    cfg = _merge(DEFAULT_RISK, (config or {}).get("risk"))
    hazard_caps = (config or {}).get("hazard_capabilities") or {"wildfire": ["water"], "unknown": ["water"]}

    lat, lon = float(incident["lat"]), float(incident["lon"])
    wind_speed = float((weather or {}).get("wind_speed_kmh") or 0)
    wind_dir = (weather or {}).get("wind_dir_deg")
    heading = (float(wind_dir) + 180) % 360 if wind_dir is not None else None
    spread = max(cfg["min_spread_kmh"], wind_speed * cfg["spread_kmh_per_wind_kmh"])
    reach_km = spread * cfg["horizon_hours"]

    w = cfg["weights"]
    threatened = []
    for a in assets:
        d = haversine_km(lat, lon, float(a["lat"]), float(a["lon"]))
        b = bearing_deg(lat, lon, float(a["lat"]), float(a["lon"]))
        in_cone = heading is not None and angle_diff(b, heading) <= cfg["cone_half_angle_deg"] and d <= reach_km
        in_perimeter = d <= cfg["perimeter_km"]
        if not (in_cone or in_perimeter):
            continue
        eta_h = 0.0 if in_perimeter else d / spread
        urgency = 1.0 / (1.0 + eta_h)
        value = (
            float(a.get("population") or 0) * w["population"]
            + float(a.get("insured_value") or 0) * w["insured_value_per_meur"]
            + float(a.get("carbon_credit_value") or 0) * w["carbon_credit_per_meur"]
        )
        mult = cfg["kind_multiplier"].get(a.get("kind"), 1.0) * float(a.get("priority_weight") or 1)
        score = value * mult * urgency
        threatened.append({
            "id": a.get("id"), "ref": a.get("ref") or a.get("key"), "name": a.get("name"), "kind": a.get("kind"),
            "distance_km": round(d, 2), "bearing_deg": round(b, 1), "eta_hours": round(eta_h, 2),
            "reason": "perimetro" if in_perimeter else "cono_de_viento",
            "population": int(a.get("population") or 0), "score": round(score, 1),
        })
    threatened.sort(key=lambda t: (t["eta_hours"], -t["score"]))

    total = sum(t["score"] for t in threatened)
    th = cfg["priority_thresholds"]
    if total >= th["critical"]:
        priority, label = 4, "critical"
    elif total >= th["high"]:
        priority, label = 3, "high"
    elif total >= th["medium"]:
        priority, label = 2, "medium"
    else:
        priority, label = 1, "low"

    needed = hazard_caps.get(incident.get("type") or "unknown", hazard_caps.get("unknown", ["water"]))
    recommended = []
    for r in resources or []:
        caps = r.get("capabilities") or []
        if isinstance(caps, str):
            import json as _json
            caps = _json.loads(caps)
        if r.get("status", "available") != "available":
            continue
        compatible = any(c in caps for c in needed)
        d = haversine_km(lat, lon, float(r["lat"]), float(r["lon"]))
        eta_min = d / SPEED_KMH.get(r.get("kind"), 60) * 60
        recommended.append({
            "id": r.get("id"), "ref": r.get("ref") or r.get("key"), "name": r.get("name"), "kind": r.get("kind"),
            "compatible": compatible, "distance_km": round(d, 1), "eta_min": round(eta_min, 0),
        })
    recommended.sort(key=lambda r: (not r["compatible"], r["eta_min"]))

    return {
        "spread_heading_deg": heading,
        "spread_kmh": round(spread, 2),
        "reach_km": round(reach_km, 2),
        "wind": {"speed_kmh": wind_speed, "dir_deg": wind_dir},
        "threatened_assets": threatened,
        "population_at_risk": sum(t["population"] for t in threatened),
        "risk_score": round(total, 1),
        "priority": priority,
        "priority_label": label,
        "needed_capabilities": needed,
        "recommended_resources": recommended,
    }
