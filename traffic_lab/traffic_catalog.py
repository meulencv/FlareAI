import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data/espana-en-directo/data/catalog.json"
IMAGE_RULES = {
    "etraffic.dgt.es": r"/camarasEtraffic/[\w-]+\.jpg",
    "informo.madrid.es": r"/cameras/Camara\d+\.jpg",
    "www.trafikoa.eus": r"/static/files/tr/camaras/\d+\.jpg",
    "www.trafikoa.net": r"/static/files/tr/camaras/\d+\.jpg",
    "www.trafikoa.euskadi.eus": r"/static/files/tr/camaras/\d+\.jpg",
    "www.bilbao.eus": r"/camarastrafico/[\w/-]+\.jpg",
    "emap.terrassa.cat": r"/it_terrassa/cam\d+\.jpeg",
}


def allowed_snapshot(url):
    if not isinstance(url, str):
        return False
    try:
        parsed = urlsplit(url)
        return bool(parsed.scheme == "https" and parsed.hostname in IMAGE_RULES and not parsed.username
                    and not parsed.password and parsed.port in (None, 443) and not parsed.query
                    and not parsed.fragment and re.fullmatch(IMAGE_RULES[parsed.hostname], parsed.path))
    except ValueError:
        return False


def candidate(camera):
    if not isinstance(camera, dict) or camera.get("category") != "traffic" or camera.get("kind") != "snapshot":
        return False
    lat, lon = camera.get("lat"), camera.get("lon")
    return bool(isinstance(camera.get("id"), str) and camera["id"]
                and type(lat) in (int, float) and type(lon) in (int, float)
                and math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180
                and allowed_snapshot(camera.get("imageUrl")))


def normalize_incident(value):
    if not isinstance(value, dict):
        raise ValueError("Se requiere una ubicación o incidente")
    lat, lon, radius = value.get("lat"), value.get("lon"), value.get("radius_km", 10)
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in (lat, lon, radius)):
        raise ValueError("Coordenadas y radio deben ser números finitos")
    if not 27 <= lat <= 44.5 or not -19 <= lon <= 5 or not 1 <= radius <= 30:
        raise ValueError("Usa coordenadas de España y un radio entre 1 y 30 km")
    return {"id": str(value.get("id") or "manual")[:80], "lat": lat, "lon": lon, "radius_km": radius,
            "description": str(value.get("description") or "Revisar tráfico cerca del incidente")[:500]}


def nearby_cameras(cameras, incident, limit=12):
    incident = normalize_incident(incident)
    selected = []
    latitude = math.radians(incident["lat"])
    for camera in cameras:
        delta_lat = math.radians(camera["lat"] - incident["lat"])
        delta_lon = math.radians(camera["lon"] - incident["lon"])
        a = math.sin(delta_lat / 2) ** 2 + math.cos(latitude) * math.cos(math.radians(camera["lat"])) * math.sin(delta_lon / 2) ** 2
        distance = 6371.0088 * 2 * math.asin(min(1, math.sqrt(max(0, a))))
        if distance <= incident["radius_km"]:
            selected.append({**camera, "distance_km": round(distance, 3)})
    return sorted(selected, key=lambda camera: (camera["distance_km"], camera["id"]))[:min(12, max(1, limit))]


class Catalog:
    def __init__(self, value):
        if not isinstance(value, dict) or not isinstance(value.get("cameras"), list):
            raise ValueError("Catálogo sin lista cameras")
        self.rows = value["cameras"]
        self.cameras = {}
        for row in self.rows:
            if candidate(row):
                if row["id"] in self.cameras:
                    raise ValueError("Identificador de cámara duplicado")
                self.cameras[row["id"]] = row

    @classmethod
    def load(cls, path=CATALOG_PATH):
        with Path(path).open(encoding="utf-8") as stream:
            return cls(json.load(stream))

    def summary(self):
        return {"records": len(self.rows), "kinds": dict(Counter(r.get("kind", "unknown") for r in self.rows if isinstance(r, dict))),
                "https_traffic_snapshot_candidates": len(self.cameras),
                "candidate_sources": dict(Counter(r["source"] for r in self.cameras.values())),
                "live_availability_verified": False, "database_connection": False,
                "mode": "read_only_source_catalog", "catalog_path": str(CATALOG_PATH)}

    def get(self, identifier):
        if identifier not in self.cameras:
            raise ValueError("Cámara ausente o no compatible con imágenes de tráfico HTTPS")
        row = self.cameras[identifier]
        return {"id": row["id"], "name": row["name"], "source": row["source"], "lat": row["lat"], "lon": row["lon"],
                "image_url": row["imageUrl"], "refresh_seconds": row.get("refreshSeconds"),
                "availability": "not_verified", "catalog_is_live_database": False,
                "time_zone": "Atlantic/Canary" if 27 <= row["lat"] <= 30 and -19 <= row["lon"] <= -12 else "Europe/Madrid"}

    def nearby(self, incident, limit=12):
        return nearby_cameras([self.get(identifier) for identifier in self.cameras], incident, limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consulta de solo lectura del catálogo fuente de la base de datos")
    parser.add_argument("--camera")
    args = parser.parse_args()
    catalog = Catalog.load()
    print(json.dumps(catalog.get(args.camera) if args.camera else catalog.summary(), ensure_ascii=True, indent=2))
