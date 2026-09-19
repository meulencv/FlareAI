"""Descarga FIRMS VIIRS, filtra España y publica un GeoJSON auditable."""

import argparse
import csv
import hashlib
import io
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from shapely.geometry import Point, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.prepared import prep

BASE = "https://firms.modaps.eosdis.nasa.gov/data/active_fire"
SOURCES = {
    "noaa20": f"{BASE}/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv",
    "noaa21": f"{BASE}/noaa-21-viirs-c2/csv/J2_VIIRS_C2_Global_24h.csv",
    "snpp": f"{BASE}/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv",
}
BOUNDARY = (
    "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/"
    "releaseData/gbOpen/ESP/ADM0/geoBoundaries-ESP-ADM0.geojson"
)
REQUIRED = {
    "latitude", "longitude", "acq_date", "acq_time", "satellite", "confidence",
    "frp", "bright_ti4", "bright_ti5", "daynight", "scan", "track", "version",
}


def download(url: str, path: Path) -> bytes:
    started = datetime.now(timezone.utc).isoformat()
    request = Request(url, headers={"User-Agent": "SpainFireSourceValidation/1.0"})
    with urlopen(request, timeout=120) as response:
        body = response.read()
        metadata = {
            "url": url,
            "http_status": response.status,
            "requested_at_utc": started,
            "received_at_utc": datetime.now(timezone.utc).isoformat(),
            "content_type": response.headers.get("Content-Type", ""),
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "file": path.name,
        }
    path.write_bytes(body)
    path.with_suffix(path.suffix + ".request.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    return body


def load_boundary(body: bytes) -> BaseGeometry:
    document = json.loads(body)
    if document["type"] != "FeatureCollection":
        raise ValueError("El límite debe ser un GeoJSON FeatureCollection")
    geometry = unary_union([shape(f["geometry"]) for f in document["features"]])
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError("Geometría de España vacía o inválida")
    return geometry


def observation_time(row: dict[str, str]) -> datetime:
    return datetime.strptime(
        row["acq_date"] + row["acq_time"].zfill(4), "%Y-%m-%d%H%M"
    ).replace(tzinfo=timezone.utc)


def parse_csv(body: bytes) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig")))
    missing = REQUIRED.difference(reader.fieldnames or [])
    if missing:
        raise ValueError(f"CSV FIRMS inválido; faltan campos: {sorted(missing)}")
    rows = list(reader)
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("CSV con una fila incompleta o columnas adicionales")
    return rows


def run(
    input_dir: Path | None, output_dir: Path, at: datetime, hours: float
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if input_dir:
        boundary_body = (input_dir / "esp.geojson").read_bytes()
    else:
        boundary_body = download(BOUNDARY, output_dir / "esp.geojson")
    boundary = prep(load_boundary(boundary_body))
    features = []
    stats = []
    seen: set[str] = set()
    for source, url in SOURCES.items():
        filename = f"{source}_global_24h.csv"
        body = (
            (input_dir / filename).read_bytes()
            if input_dir else download(url, output_dir / filename)
        )
        rows = parse_csv(body)
        spanish = 0
        kept = 0
        latest: datetime | None = None
        for row in rows:
            observed = observation_time(row)
            latest = observed if latest is None else max(latest, observed)
            lon, lat = float(row["longitude"]), float(row["latitude"])
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise ValueError(f"Coordenadas inválidas en {source}")
            if not (-19 <= lon <= 5 and 27 <= lat <= 44):
                continue
            if not boundary.covers(Point(lon, lat)):
                continue
            spanish += 1
            if not at - timedelta(hours=hours) <= observed <= at:
                continue
            identifier = "|".join(
                [source, observed.isoformat(), row["latitude"], row["longitude"]]
            )
            if identifier in seen:
                continue
            seen.add(identifier)
            kept += 1
            numeric = {
                field: float(row[field])
                for field in ("frp", "bright_ti4", "bright_ti5", "scan", "track")
            }
            if not all(math.isfinite(value) for value in numeric.values()):
                raise ValueError(f"Valor no finito en {source}")
            features.append({
                "type": "Feature",
                "id": identifier,
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "source": source,
                    "satellite": row["satellite"],
                    "acquired_at_utc": observed.isoformat(),
                    "confidence": row["confidence"],
                    "frp_mw": numeric["frp"],
                    "brightness_i4_k": numeric["bright_ti4"],
                    "brightness_i5_k": numeric["bright_ti5"],
                    "scan_km": numeric["scan"],
                    "track_km": numeric["track"],
                    "daynight": row["daynight"],
                    "version": row["version"],
                    "classification": "thermal_anomaly_unconfirmed",
                },
            })
        stats.append({
            "source": source,
            "rows_global": len(rows),
            "rows_spain_before_time_filter": spanish,
            "rows_spain_selected": kept,
            "latest_global_observation_utc": latest.isoformat() if latest else None,
            "age_of_latest_global_hours": (
                round((at - latest).total_seconds() / 3600, 3) if latest else None
            ),
            "sha256": hashlib.sha256(body).hexdigest(),
        })
    result = {
        "type": "FeatureCollection",
        "analysis_at_utc": at.isoformat(),
        "window_hours": hours,
        "features": features,
    }
    summary = {
        "analysis_at_utc": at.isoformat(),
        "window_hours": hours,
        "selected_observations": len(features),
        "boundary_sha256": hashlib.sha256(boundary_body).hexdigest(),
        "sources": stats,
    }
    for filename, document in [
        ("focos_espana.geojson", result), ("resumen.json", summary)
    ]:
        temporary = output_dir / (filename + ".pending")
        temporary.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )
        temporary.replace(output_dir / filename)
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, help="Reutiliza CSV y límite locales")
    parser.add_argument("--output-dir", type=Path, default=Path("salida"))
    parser.add_argument("--hours", type=float, default=24)
    parser.add_argument("--at", help="UTC ISO8601 para reproducir un corte histórico")
    args = parser.parse_args()
    at = (
        datetime.fromisoformat(args.at.replace("Z", "+00:00"))
        if args.at else datetime.now(timezone.utc)
    )
    if at.utcoffset() is None:
        parser.error("--at debe incluir zona horaria: Z o +00:00")
    if not math.isfinite(args.hours) or args.hours <= 0:
        parser.error("--hours debe ser un número positivo finito")
    run(args.input_dir, args.output_dir, at.astimezone(timezone.utc), args.hours)


if __name__ == "__main__":
    main()
