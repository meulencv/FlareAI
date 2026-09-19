from __future__ import annotations

import hashlib
import io
import json
import threading
from datetime import timedelta
from typing import TypedDict, cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
from PIL import Image

from gfs import DATA, iso, utcnow, write_json
from incidents import Incident

GIBS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
LAYERS = {
    "natural": "VIIRS_NOAA20_CorrectedReflectance_TrueColor",
    "swir": "VIIRS_NOAA20_CorrectedReflectance_BandsM11-I2-I1",
}
LOCK = threading.Lock()


def coverage_fraction(image: Image.Image) -> float:
    pixels = np.asarray(image.convert("RGBA"))
    return float(np.mean((pixels[:, :, 3] >= 64) & (pixels[:, :, :3].max(axis=2) > 8)))


class Picture(TypedDict):
    url: str
    date: str
    bbox: list[float]
    mode: str
    source_url: str
    checked_at_utc: str


def picture(incident: Incident, mode: str, offline: bool = False) -> Picture:
    if mode not in LAYERS:
        raise ValueError("Capa desconocida")
    lon, lat = incident["lon"], incident["lat"]
    bbox = [round(lon - .24, 5), round(lat - .16, 5), round(lon + .24, 5), round(lat + .16, 5)]
    if offline:
        cached = []
        for path in (DATA / "satellite").glob("*.json"):
            if path.name.endswith(".request.json"):
                continue
            item = cast(Picture, json.loads(path.read_text()))
            if item["bbox"] == bbox and item["mode"] == mode:
                cached.append(item)
        if cached:
            return max(cached, key=lambda item: item["checked_at_utc"])
        raise ValueError("Sin imagen guardada para esta zona y capa; necesita conexión.")
    now = utcnow()
    key = hashlib.sha256(f"v2|{bbox}|{mode}|{now:%Y-%m-%d_%H}".encode()).hexdigest()[:24]
    meta = DATA / "satellite" / f"{key}.json"
    with LOCK:
        if meta.exists():
            return cast(Picture, json.loads(meta.read_text()))
        for days in range(4):
            date = (now - timedelta(days=days)).date().isoformat()
            params = {
                "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetMap",
                "LAYERS": LAYERS[mode], "STYLES": "", "SRS": "EPSG:4326",
                "BBOX": ",".join(map(str, bbox)), "WIDTH": "900", "HEIGHT": "600",
                "FORMAT": "image/png", "TRANSPARENT": "TRUE", "TIME": date,
            }
            url = GIBS + "?" + urlencode(params)
            with urlopen(Request(url, headers={"User-Agent": "FlareAIObservatorio/1.0"}), timeout=35) as response:
                body = response.read(5_000_001)
                if response.status != 200 or len(body) > 5_000_000:
                    raise ValueError("Respuesta satelital inválida")
            with Image.open(io.BytesIO(body)) as image:
                rgba = image.convert("RGBA")
                if rgba.size != (900, 600):
                    raise ValueError("Dimensiones de imagen inesperadas")
                coverage = coverage_fraction(rgba)
                if coverage < .5:
                    continue
            filename = f"{key}.png"
            (DATA / "satellite" / filename).write_bytes(body)
            result = Picture(
                url=f"/satellite/{filename}", date=date, bbox=bbox, mode=mode,
                source_url=url, checked_at_utc=iso(now),
            )
            write_json(meta, result)
            write_json(meta.with_suffix(".request.json"), {
                "url": url, "http_status": 200, "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(), "coverage_fraction": coverage,
                "received_at_utc": iso(utcnow()),
            })
            return result
    raise ValueError("Sin mosaico con cobertura suficiente en los últimos cuatro días.")
