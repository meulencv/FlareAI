"""Open-Meteo (sin API key) → observación meteo actual para un punto."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request


def current(lat: float, lon: float) -> dict:
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "wind_speed_unit": "kmh",
                                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"})
    with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?{q}", timeout=30) as r:
        cur = json.load(r).get("current", {})
    return {"wind_speed_kmh": cur.get("wind_speed_10m"), "wind_dir_deg": cur.get("wind_direction_10m"),
            "temp_c": cur.get("temperature_2m"), "humidity": cur.get("relative_humidity_2m"), "source": "open-meteo"}
