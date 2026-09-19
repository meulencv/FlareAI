#!/usr/bin/env python3
"""Mapa ASCII de detecciones térmicas NASA FIRMS sobre España.

- Fuente: NASA FIRMS KML fire footprints, últimas 24 h.
- Sin API key.
- Todo se dibuja en la terminal con ANSI.
- Ctrl+C para salir.
"""

from __future__ import annotations

import io
import math
import os
import shutil
import sys
import time
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone

# -----------------------------------------------------------------------------
# Configuración
# -----------------------------------------------------------------------------

REFRESH_SECONDS = 300  # 5 minutos
TIMEOUT_SECONDS = 30

# Varias pasadas/satélites VIIRS. Una misma zona puede aparecer varias veces:
# son DETECCIONES térmicas, no necesariamente incendios únicos confirmados.
SOURCES = {
    "NOAA-21": "noaa-21-viirs-c2",
    "NOAA-20": "noaa-20-viirs-c2",
}

URL_TEMPLATE = (
    "https://firms.modaps.eosdis.nasa.gov/api/kml_fire_footprints/"
    "europe/24h/{sensor}"
)

# Extensión del mapa peninsular que mostraremos.
LON_MIN, LON_MAX = -9.6, 3.5
LAT_MIN, LAT_MAX = 35.7, 44.1

# Polígono APROXIMADO de España peninsular. Sirve para excluir la mayor parte
# de Portugal/Francia sin depender de librerías GIS externas.
SPAIN_POLYGON = [
    (-9.35, 43.75), (-8.30, 43.40), (-6.20, 43.60), (-3.00, 43.50),
    (-1.70, 43.30), (0.00, 42.90), (1.70, 42.70), (3.20, 42.40),
    (3.30, 41.80), (2.80, 41.30), (1.50, 41.00), (0.70, 40.70),
    (0.10, 39.70), (-0.20, 39.10), (-0.70, 38.20), (-1.60, 37.40),
    (-2.80, 36.70), (-5.60, 36.00), (-6.50, 36.20), (-7.10, 37.20),
    (-7.20, 38.00), (-7.00, 39.00), (-7.30, 40.20), (-6.90, 41.20),
    (-6.50, 41.90), (-7.00, 42.20), (-8.70, 42.00), (-9.20, 42.80),
]

RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


@dataclass
class Detection:
    lat: float
    lon: float
    source: str
    when: str = ""
    name: str = ""


def clear_screen() -> None:
    # Activa ANSI en muchas terminales de Windows modernas.
    if os.name == "nt":
        os.system("")
    print("\033[2J\033[H", end="")


def point_in_polygon(lon: float, lat: float, polygon=SPAIN_POLYGON) -> bool:
    """Ray casting simple para filtrar aproximadamente España peninsular."""
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        if (yi > lat) != (yj > lat):
            x_cross = (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
            if lon < x_cross:
                inside = not inside
        j = i
    return inside


def _download(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "NASA-FIRMS-Terminal-Map/1.0",
            "Accept": "application/vnd.google-earth.kml+xml, application/vnd.google-earth.kmz, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def _unpack_kml(payload: bytes) -> bytes:
    """Admite tanto KML directo como KMZ (ZIP)."""
    if payload[:2] != b"PK":
        return payload

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        kml_names = [n for n in zf.namelist() if n.lower().endswith(".kml")]
        if not kml_names:
            raise ValueError("NASA devolvió un KMZ sin archivo KML")
        return zf.read(kml_names[0])


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_kml(payload: bytes, source: str) -> list[Detection]:
    """Extrae un centro aproximado por Placemark/píxel de detección."""
    root = ET.fromstring(_unpack_kml(payload))
    detections: list[Detection] = []

    for placemark in (el for el in root.iter() if _local(el.tag) == "Placemark"):
        coords: list[tuple[float, float]] = []
        name = ""
        when = ""

        for el in placemark.iter():
            tag = _local(el.tag)
            text = (el.text or "").strip()

            if tag == "name" and text and not name:
                name = text
            elif tag == "when" and text and not when:
                when = text
            elif tag == "coordinates" and text:
                # KML: lon,lat[,alt] lon,lat[,alt] ...
                for token in text.replace("\n", " ").split():
                    parts = token.split(",")
                    if len(parts) >= 2:
                        try:
                            lon = float(parts[0])
                            lat = float(parts[1])
                            if math.isfinite(lon) and math.isfinite(lat):
                                coords.append((lon, lat))
                        except ValueError:
                            pass

        if not coords:
            continue

        # En fire-footprints suele ser un polígono de píxel; usamos su centro.
        # Si es un Point, la media es ese mismo punto.
        lon = sum(p[0] for p in coords) / len(coords)
        lat = sum(p[1] for p in coords) / len(coords)

        if point_in_polygon(lon, lat):
            detections.append(Detection(lat=lat, lon=lon, source=source, when=when, name=name))

    return detections


def fetch_detections() -> tuple[list[Detection], list[str]]:
    detections: list[Detection] = []
    errors: list[str] = []

    for source, sensor in SOURCES.items():
        url = URL_TEMPLATE.format(sensor=sensor)
        try:
            payload = _download(url)
            detections.extend(parse_kml(payload, source))
        except Exception as exc:
            errors.append(f"{source}: {exc}")

    return detections, errors


def lonlat_to_cell(lon: float, lat: float, width: int, height: int) -> tuple[int, int]:
    x = round((lon - LON_MIN) / (LON_MAX - LON_MIN) * (width - 1))
    y = round((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * (height - 1))
    return max(0, min(width - 1, x)), max(0, min(height - 1, y))


def draw_line(grid: list[list[str]], x0: int, y0: int, x1: int, y1: int, char: str) -> None:
    """Bresenham para dibujar el contorno aproximado de España."""
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        if 0 <= y0 < len(grid) and 0 <= x0 < len(grid[0]):
            grid[y0][x0] = char
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def render_map(detections: list[Detection]) -> str:
    term_width = shutil.get_terminal_size((100, 30)).columns
    width = max(55, min(100, term_width - 2))
    height = max(20, min(32, int(width * 0.32)))

    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Contorno aproximado
    border = []
    for lon, lat in SPAIN_POLYGON:
        border.append(lonlat_to_cell(lon, lat, width, height))
    border.append(border[0])

    for (x0, y0), (x1, y1) in zip(border, border[1:]):
        draw_line(grid, x0, y0, x1, y1, "·")

    # Detecciones. Si varias caen en la misma celda, se ve un único ●,
    # pero el contador inferior conserva el total real de detecciones.
    fire_cells = set()
    for d in detections:
        fire_cells.add(lonlat_to_cell(d.lon, d.lat, width, height))

    for x, y in fire_cells:
        grid[y][x] = f"{RED}●{RESET}"

    lines = ["".join(row) for row in grid]
    return "\n".join(lines)


def compact_rows(detections: list[Detection], limit: int = 30) -> str:
    if not detections:
        return f"{YELLOW}No se encontraron detecciones dentro del filtro peninsular.{RESET}"

    # Orden aproximado por marca temporal si NASA la incluye.
    rows = sorted(detections, key=lambda d: d.when or "", reverse=True)
    out = []
    out.append(f"{BOLD}{'LAT':>9} {'LON':>10}  {'SATÉLITE':<8}  HORA/FECHA NASA{RESET}")
    out.append("-" * 62)
    for d in rows[:limit]:
        when = d.when[:25] if d.when else "-"
        out.append(f"{d.lat:9.4f} {d.lon:10.4f}  {d.source:<8}  {when}")
    if len(rows) > limit:
        out.append(f"... y {len(rows) - limit} detecciones más")
    return "\n".join(out)


def main() -> None:
    print("NASA FIRMS terminal map — Ctrl+C para salir")
    time.sleep(0.4)

    while True:
        detections, errors = fetch_detections()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        clear_screen()
        print(f"{BOLD}{CYAN}NASA FIRMS — detecciones térmicas en España peninsular (últimas 24 h){RESET}")
        print(f"Actualizado localmente: {now}")
        print(
            f"Detecciones recibidas dentro del filtro: {BOLD}{len(detections)}{RESET}  "
            f"| celdas visibles en mapa: {len({lonlat_to_cell(d.lon, d.lat, 80, 25) for d in detections})}"
        )
        print(f"{RED}●{RESET} = detección térmica NASA/VIIRS   {DIM}· = contorno aproximado{RESET}\n")
        print(render_map(detections))
        print()
        print(compact_rows(detections))

        if errors:
            print(f"\n{YELLOW}Avisos de descarga:{RESET}")
            for err in errors:
                print(" -", err)

        print(
            f"\n{DIM}Nota: FIRMS marca active fires/thermal anomalies. "
            "Una detección no equivale necesariamente a un incendio forestal confirmado.\n"
            f"Se vuelve a consultar NASA en {REFRESH_SECONDS // 60} min. Ctrl+C para salir.{RESET}"
        )

        try:
            time.sleep(REFRESH_SECONDS)
        except KeyboardInterrupt:
            print("\nSaliendo.")
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo.")
        sys.exit(0)
