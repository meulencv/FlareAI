from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TypedDict, cast
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
from eccodes import (
    codes_get,
    codes_get_values,
    codes_new_from_message,
    codes_release,
)
from numpy.typing import NDArray
from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
BASE = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
FIELDS = {
    "u": ("UGRD", "10 m above ground"),
    "v": ("VGRD", "10 m above ground"),
    "gust": ("GUST", "surface"),
    "temperature": ("TMP", "2 m above ground"),
}


class Region(TypedDict):
    name: str
    west: float
    south: float
    step: float
    nx: int
    ny: int
    u: list[float]
    v: list[float]
    gust: list[float]
    temperature: list[float]


class Snapshot(TypedDict):
    source: str
    source_url: str
    model_run_utc: str
    valid_at_utc: str
    downloaded_at_utc: str
    checked_at_utc: str
    forecast_hour: int
    grid_degrees: float
    units: str
    classification: str
    index_sha256: str
    regions: list[Region]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")),
        encoding="utf-8",
    )
    temporary.replace(path)


def fetch(url: str, path: Path, byte_range: tuple[int, int] | None = None) -> bytes:
    headers = {"User-Agent": "SpainWindOpenData/1.0"}
    if byte_range:
        headers["Range"] = f"bytes={byte_range[0]}-{byte_range[1]}"
    started = iso(utcnow())
    with urlopen(Request(url, headers=headers), timeout=60) as response:
        if byte_range and response.status != 206:
            raise ValueError("El servidor no respeta Range; no se descargará el GRIB global.")
        limit = 8_000_000
        body = response.read(limit + 1)
        if len(body) > limit:
            raise ValueError("Respuesta superior al límite de seguridad de 8 MB.")
        content_range = response.headers.get("Content-Range", "")
        if byte_range:
            expected = f"bytes {byte_range[0]}-{byte_range[1]}/"
            if not content_range.startswith(expected):
                raise ValueError("Content-Range no coincide con la petición.")
            if len(body) != byte_range[1] - byte_range[0] + 1:
                raise ValueError("Descarga GRIB incompleta.")
        record = {
            "url": url,
            "range": headers.get("Range"),
            "http_status": response.status,
            "requested_at_utc": started,
            "received_at_utc": iso(utcnow()),
            "content_type": response.headers.get("Content-Type"),
            "last_modified": response.headers.get("Last-Modified"),
            "etag": response.headers.get("ETag"),
            "content_range": content_range,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "file": path.name,
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    write_json(path.with_suffix(path.suffix + ".request.json"), record)
    return body


def ranges(index: str) -> dict[str, tuple[int, int]]:
    records = [line.split(":") for line in index.splitlines() if line.strip()]
    if not records or any(len(row) < 7 for row in records):
        raise ValueError("Índice GRIB inválido.")
    offsets = [int(row[1]) for row in records]
    if offsets != sorted(set(offsets)):
        raise ValueError("Offsets GRIB inválidos.")
    result = {}
    for name, (variable, level) in FIELDS.items():
        matches = [i for i, row in enumerate(records) if row[3:5] == [variable, level]]
        if len(matches) != 1 or matches[0] + 1 >= len(records):
            raise ValueError(f"No se puede delimitar el campo {variable}:{level}.")
        position = matches[0]
        result[name] = offsets[position], offsets[position + 1] - 1
    return result


def decode(body: bytes, variable: str, run: datetime, valid: datetime) -> NDArray[np.float64]:
    if body[:4] != b"GRIB" or body[-4:] != b"7777":
        raise ValueError("Respuesta no GRIB o truncada.")
    handle = codes_new_from_message(body)
    try:
        expected = {
            "gridType": "regular_ll",
            "Ni": 1440,
            "Nj": 721,
            "latitudeOfFirstGridPointInDegrees": 90,
            "longitudeOfFirstGridPointInDegrees": 0,
            "iDirectionIncrementInDegrees": 0.25,
            "jDirectionIncrementInDegrees": 0.25,
            "iScansNegatively": 0,
            "jScansPositively": 0,
            "jPointsAreConsecutive": 0,
            "dataDate": int(run.strftime("%Y%m%d")),
            "dataTime": run.hour * 100,
            "validityDate": int(valid.strftime("%Y%m%d")),
            "validityTime": valid.hour * 100,
            "units": "K" if variable == "temperature" else "m s**-1",
            "shortName": {"u": "10u", "v": "10v", "gust": "gust", "temperature": "2t"}[variable],
            "numberOfMissing": 0,
        }
        for key, value in expected.items():
            actual = codes_get(handle, key)
            if actual != value:
                raise ValueError(f"GRIB {key}: esperado {value!r}, recibido {actual!r}.")
        values = np.asarray(codes_get_values(handle), dtype=np.float64).reshape(721, 1440)
        if not np.isfinite(values).all():
            raise ValueError("GRIB contiene valores no finitos.")
        return values
    finally:
        codes_release(handle)


def region(name: str, west: float, south: float, east: float, north: float,
           fields: dict[str, NDArray[np.float64]]) -> Region:
    nx, ny = round((east - west) * 4) + 1, round((north - south) * 4) + 1
    latitudes = south + np.arange(ny) * 0.25
    longitudes = west + np.arange(nx) * 0.25
    rows = np.rint((90 - latitudes) * 4).astype(int)
    columns = np.rint((longitudes % 360) * 4).astype(int)
    values = {
        key: np.round(array[np.ix_(rows, columns)], 4).ravel().tolist()
        for key, array in fields.items()
    }
    return Region(name=name, west=west, south=south, step=0.25, nx=nx, ny=ny,
                  u=values["u"], v=values["v"], gust=values["gust"], temperature=values["temperature"])


def update(output: Path = DATA / "latest.json", at: datetime | None = None) -> Snapshot:
    now = at or utcnow()
    if now.utcoffset() != timedelta(0):
        raise ValueError("La fecha de referencia debe usar UTC.")
    valid = now.replace(minute=0, second=0, microsecond=0)
    newest = valid.replace(hour=(valid.hour // 6) * 6)
    index = ""
    for back in range(5):
        run = newest - timedelta(hours=6 * back)
        forecast_hour = int((valid - run).total_seconds() // 3600)
        stem = f"gfs.t{run:%H}z.pgrb2.0p25.f{forecast_hour:03d}"
        url = f"{BASE}/gfs.{run:%Y%m%d}/{run:%H}/atmos/{stem}"
        folder = DATA / "evidence" / f"{run:%Y%m%d_%H}_f{forecast_hour:03d}"
        try:
            index = fetch(url + ".idx", folder / (stem + ".idx")).decode("utf-8")
            break
        except HTTPError as error:
            if error.code != 404:
                raise
    else:
        raise RuntimeError("No hay una salida GFS disponible en las últimas 24 horas.")
    selected = ranges(index)
    if output.exists():
        previous = cast(Snapshot, json.loads(output.read_text(encoding="utf-8")))
        if previous["source_url"] == url and previous.get("index_sha256") == hashlib.sha256(index.encode()).hexdigest() and all("temperature" in r for r in previous["regions"]):
            previous["checked_at_utc"] = iso(utcnow())
            write_json(output, previous)
            return previous
    arrays = {}
    for variable, byte_range in selected.items():
        path = folder / f"{variable}.grib2"
        body = fetch(url, path, byte_range)
        arrays[variable] = decode(body, variable, run, valid)
    result = Snapshot(
        source="NOAA GFS / AWS Open Data",
        source_url=url,
        model_run_utc=iso(run),
        valid_at_utc=iso(valid),
        downloaded_at_utc=iso(utcnow()),
        checked_at_utc=iso(utcnow()),
        forecast_hour=forecast_hour,
        grid_degrees=0.25,
        units="u,v,gust: m/s; temperature: K",
        classification="model_forecast_not_station_observation",
        index_sha256=hashlib.sha256(index.encode()).hexdigest(),
        regions=[
            region("peninsula", -10, 35, 5, 44.5, arrays),
            region("canarias", -18.5, 27.25, -13, 29.75, arrays),
        ],
    )
    write_json(output, result)
    return result


def interpolate(grid: Region, lat: float, lon: float, key: str) -> float:
    x = (lon - grid["west"]) / grid["step"]
    y = (lat - grid["south"]) / grid["step"]
    if not (0 <= x <= grid["nx"] - 1 and 0 <= y <= grid["ny"] - 1):
        raise ValueError("Fuera de la región.")
    x0, y0 = min(math.floor(x), grid["nx"] - 2), min(math.floor(y), grid["ny"] - 2)
    dx, dy = x - x0, y - y0
    values = {"u": grid["u"], "v": grid["v"], "gust": grid["gust"], "temperature": grid["temperature"]}[key]
    i = y0 * grid["nx"] + x0
    return (
        values[i] * (1 - dx) * (1 - dy)
        + values[i + 1] * dx * (1 - dy)
        + values[i + grid["nx"]] * (1 - dx) * dy
        + values[i + grid["nx"] + 1] * dx * dy
    )


def point(snapshot: Snapshot, lat: float, lon: float) -> dict[str, str | float | None]:
    if not (math.isfinite(lat) and math.isfinite(lon)):
        raise ValueError("Coordenadas inválidas.")
    for grid in snapshot["regions"]:
        try:
            u, v, gust = [interpolate(grid, lat, lon, key) for key in ("u", "v", "gust")]
        except ValueError:
            continue
        speed = math.hypot(u, v)
        direction = (math.degrees(math.atan2(-u, -v)) + 360) % 360 if speed >= 0.2 else None
        return {
            "latitude": lat, "longitude": lon,
            "wind_speed_kmh": round(speed * 3.6, 1),
            "wind_gust_kmh": round(gust * 3.6, 1),
            "air_temperature_c": round(interpolate(grid, lat, lon, "temperature") - 273.15, 1),
            "wind_from_degrees": round(direction, 1) if direction is not None else None,
            "u_ms": round(u, 4), "v_ms": round(v, 4),
            "valid_at_utc": snapshot["valid_at_utc"],
            "model_run_utc": snapshot["model_run_utc"],
            "method": "bilinear_components_on_0.25_degree_forecast_grid",
        }
    raise ValueError("Fuera de las regiones descargadas.")


def export_csv(snapshot: Snapshot, output: Path = DATA / "viento_espana.csv") -> None:
    country = shape(json.loads((ROOT / "static/spain.geojson").read_text())["geometry"])
    places = json.loads((ROOT / "static/places.json").read_text())
    rows = []
    for grid in snapshot["regions"]:
        for y in range(grid["ny"]):
            for x in range(grid["nx"]):
                lat, lon = grid["south"] + y * grid["step"], grid["west"] + x * grid["step"]
                if country.covers(Point(lon, lat)):
                    rows.append({"name": "", "kind": "grid", **point(snapshot, lat, lon)})
    for place in places:
        rows.append({"name": place["name"], "kind": "interpolated_city",
                     **point(snapshot, place["lat"], place["lon"])})
    temporary = output.with_suffix(".csv.part")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga viento GFS sin claves ni cuenta.")
    parser.add_argument("--output", type=Path, default=DATA / "latest.json")
    parser.add_argument("--at", help="Fecha UTC ISO; para reproducir un archivo reciente.")
    args = parser.parse_args()
    reference = datetime.fromisoformat(args.at.replace("Z", "+00:00")) if args.at else None
    snapshot = update(args.output, reference)
    if (ROOT / "static/places.json").exists():
        export_csv(snapshot, args.output.parent / "viento_espana.csv")
    print(json.dumps({k: v for k, v in snapshot.items() if k != "regions"}, indent=2))
