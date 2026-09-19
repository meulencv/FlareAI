from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta
from typing import TypedDict, cast

from shapely.affinity import scale, translate
from shapely.geometry import Point, box, mapping, shape
from shapely.ops import unary_union

from detectar import SOURCES, download, run
from gfs import DATA, ROOT, Snapshot, iso, point, utcnow, write_json


class Properties(TypedDict):
    acquired_at_utc: str
    frp_mw: float
    brightness_i4_k: float
    brightness_i5_k: float
    scan_km: float
    track_km: float
    confidence: str
    satellite: str
    source: str


class Geometry(TypedDict):
    coordinates: list[float]


class Observation(TypedDict):
    id: str
    geometry: Geometry
    properties: Properties


class Collection(TypedDict):
    analysis_at_utc: str
    features: list[Observation]


class Incident(TypedDict):
    id: str
    name: str
    province: str
    lon: float
    lat: float
    first_seen: str
    last_seen: str
    observations: int
    passes: int
    satellites: list[str]
    frp_peak_mw: float
    brightness_i4_k: float
    brightness_i4_c: float
    brightness_at_utc: str
    low_confidence: int
    documented: bool
    documentation_url: str | None
    burned_area_ha: None
    footprint_ha: float
    footprint: dict[str, object]
    detections: list[dict[str, object]]
    weather: dict[str, str | float | None]


def distance(a: list[float], b: list[float]) -> float:
    x, y = a
    xx, yy = b
    return math.hypot((xx - x) * 111.32 * math.cos(math.radians((y + yy) / 2)),
                      (yy - y) * 111.32)


def cluster(observations: list[Observation], radius: float = 3) -> list[list[Observation]]:
    groups: list[list[Observation]] = []
    for observation in observations:
        matches = [
            group for group in groups if any(
                distance(observation["geometry"]["coordinates"], item["geometry"]["coordinates"]) <= radius
                for item in group
            )
        ]
        merged = [observation]
        for group in matches:
            merged.extend(group)
            groups.remove(group)
        groups.append(merged)
    return groups


def footprint(observations: list[Observation], lon: float, lat: float) -> tuple[dict[str, object], float]:
    xscale = 111320 * math.cos(math.radians(lat))
    rectangles = []
    for item in observations:
        x, y = item["geometry"]["coordinates"]
        props = item["properties"]
        dx, dy = max(props["scan_km"], .375) * 500, max(props["track_km"], .375) * 500
        x, y = (x - lon) * xscale, (y - lat) * 111320
        rectangles.append(box(x - dx, y - dy, x + dx, y + dy))
    union = unary_union(rectangles)
    degrees = translate(scale(union, xfact=1 / xscale, yfact=1 / 111320, origin=(0, 0)), lon, lat)
    return dict(mapping(degrees)), round(union.area / 10000, 1)


def assemble(collection: Collection, weather: Snapshot, at: datetime | None = None) -> list[Incident]:
    now = at or utcnow()
    provinces = json.loads((ROOT / "static/provinces.geojson").read_text())["features"]
    names = {"Rioja, La": "La Rioja", "Balears, Illes": "Illes Balears", "Coruña, A": "A Coruña", "Palmas, Las": "Las Palmas"}
    boundaries = [(names.get(f["properties"]["shapeName"], f["properties"]["shapeName"]), shape(f["geometry"])) for f in provinces]
    observations = [
        item for item in collection["features"]
        if now - timedelta(hours=24) <= datetime.fromisoformat(item["properties"]["acquired_at_utc"]) <= now
    ]
    incidents: list[Incident] = []
    for group in cluster(observations):
        lon = sum(f["geometry"]["coordinates"][0] for f in group) / len(group)
        lat = sum(f["geometry"]["coordinates"][1] for f in group) / len(group)
        province = next((name for name, boundary in boundaries if boundary.covers(Point(lon, lat))), "España")
        props = [item["properties"] for item in group]
        last = max(p["acquired_at_utc"] for p in props)
        documented = distance([lon, lat], [-2.024, 42.075]) < 2 and any(
            p["acquired_at_utc"].startswith("2026-09-18") for p in props
        )
        geom, area = footprint(group, lon, lat)
        hottest = max(props, key=lambda p: p["brightness_i4_k"])
        identifier = hashlib.sha256(min(item["id"] for item in group).encode()).hexdigest()[:12]
        incidents.append(Incident(
            id=identifier, name="Igea" if documented else province, province=province,
            lon=round(lon, 5), lat=round(lat, 5),
            first_seen=min(p["acquired_at_utc"] for p in props), last_seen=last,
            observations=len(group),
            passes=len({(p["acquired_at_utc"], p["satellite"]) for p in props}),
            satellites=sorted({p["satellite"] for p in props}),
            frp_peak_mw=max(p["frp_mw"] for p in props),
            brightness_i4_k=hottest["brightness_i4_k"],
            brightness_i4_c=round(hottest["brightness_i4_k"] - 273.15, 1),
            brightness_at_utc=hottest["acquired_at_utc"],
            low_confidence=sum(p["confidence"] == "low" for p in props),
            documented=documented,
            documentation_url=(
                "https://actualidadriojabaja.com/el-incendio-de-igea-afecta-ya-a-unas-25-hectareas-de-matorral-y-arbolado/"
                if documented else None
            ),
            burned_area_ha=None, footprint_ha=area, footprint=geom,
            detections=[{"id": o['id'], "source": o['properties']['source'], "satellite": o['properties']['satellite'],
                         "lon": o["geometry"]["coordinates"][0], "lat": o["geometry"]["coordinates"][1],
                         "at": o["properties"]["acquired_at_utc"], "confidence": o["properties"]["confidence"]}
                        for o in group],
            weather=point(weather, lat, lon),
        ))
    return sorted(incidents, key=lambda i: (i["documented"], i["observations"], i["frp_peak_mw"]), reverse=True)


def refresh_fires() -> Collection:
    folder = DATA / "firms"
    for source, url in SOURCES.items():
        download(url, folder / f"{source}_global_24h.csv")
    now = utcnow()
    run(folder, folder, now, 24)
    write_json(folder / "checked.json", {"checked_at_utc": iso(now)})
    return cast(Collection, json.loads((folder / "focos_espana.geojson").read_text()))
