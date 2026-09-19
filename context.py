from __future__ import annotations

import csv
import gzip
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypeGuard

import numpy as np
import shapely
from shapely.affinity import scale, translate
from shapely.geometry import shape


ATLAS_ROOT = Path(__file__).resolve().parent / "data/Espana_Datos_y_Mapas"
RADIUS_KM = 5.0
WIND_HALF_ANGLE = 30.0
MIN_WIND_KMH = 3.0
SOILS = ("bosque", "urbano", "cultivos", "matorral", "herbaceas", "suelo_desnudo",
         "agua", "humedales", "nieve_hielo", "musgos_liquenes")
GRID_FIELDS = ("lon", "lat", "x_min_3035", "y_min_3035", "poblacion", "menores_15", "mayores_65",
               "superficie_clasificada_km2", *(f"pct_suelo_{name}" for name in SOILS))
CATEGORIES = {
    "combustibles_quimica": "Combustibles / química", "gasolinera": "Gasolinera",
    "central_combustion": "Central de combustión", "aeropuerto_aerodromo": "Aeropuerto / aeródromo",
    "helipuerto": "Helipuerto", "puerto": "Puerto", "puerto_deportivo": "Puerto deportivo",
    "fabrica": "Fábrica", "area_industrial": "Área industrial", "vertedero": "Vertedero",
    "gestion_residuos": "Centro de residuos",
}


def finite(value: Any) -> TypeGuard[float]:
    return isinstance(value, (int, float)) and math.isfinite(value)


def wind_state(weather: dict, now: datetime, offline: bool = False, weather_error: bool = False) -> dict:
    direction, speed = weather.get("wind_from_degrees"), weather.get("wind_speed_kmh")
    status = "current"
    if not finite(direction) or not finite(speed) or not 0 <= direction <= 360 or speed < 0:
        status = "missing"
    elif speed < MIN_WIND_KMH:
        status = "calm"
    elif weather_error:
        status = "stale"
    else:
        try:
            valid = datetime.fromisoformat(weather["valid_at_utc"].replace("Z", "+00:00"))
            run = datetime.fromisoformat(weather["model_run_utc"].replace("Z", "+00:00"))
            reference = valid if offline else now
            if abs((reference - valid).total_seconds()) > 7200 or not 0 <= (reference - run).total_seconds() <= 43200:
                status = "stale"
            elif offline:
                status = "historical"
        except (KeyError, TypeError, ValueError):
            status = "missing"
    usable = status in {"current", "historical"}
    return {"status": status, "usable": usable, "towards_degrees": (direction + 180) % 360 if usable and finite(direction) else None,
            "speed_kmh": speed if finite(speed) else None, "valid_at_utc": weather.get("valid_at_utc"),
            "half_angle_degrees": WIND_HALF_ANGLE, "minimum_speed_kmh": MIN_WIND_KMH}


class Atlas:
    def __init__(self, grid: np.ndarray, facilities: list[dict]) -> None:
        self.grid = grid
        self.facilities = facilities
        self.facility_coords = np.array([(p["lon"], p["lat"]) for p in facilities], dtype=float).reshape(-1, 2)

    @classmethod
    def load(cls, root: Path = ATLAS_ROOT) -> Atlas:
        with gzip.open(root / "output/espana_rejilla_1km.csv.gz", "rt", encoding="utf-8", newline="") as stream:
            reader = csv.reader(stream)
            header = next(reader)
            indexes = [header.index(name) for name in GRID_FIELDS]
            grid = np.fromiter((tuple(float(row[i]) if row[i] else math.nan for i in indexes) for row in reader),
                               dtype=[(name, "f8") for name in GRID_FIELDS])
        if not len(grid) or not np.isfinite(grid["lon"]).all() or not np.isfinite(grid["lat"]).all():
            raise ValueError("Rejilla del atlas vacía o con coordenadas inválidas")
        facilities, seen = [], set()
        with (root / "output/instalaciones_atencion_incendios.csv").open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                identifier = f"{row['osm_type']}:{row['osm_id']}"
                if identifier in seen:
                    continue
                seen.add(identifier)
                lon, lat = float(row["lon"]), float(row["lat"])
                if not (math.isfinite(lon) and math.isfinite(lat)):
                    raise ValueError("Instalación con coordenadas inválidas")
                facilities.append({
                    "id": identifier, "lon": lon, "lat": lat, "name": row["nombre"],
                    "category": row["categoria"], "priority": row["prioridad_preventiva"],
                    "reason": row["criterio"], "source_url": row["url_osm"],
                    "coordinate_method": row["metodo_coordenada"], "boundary_location": row["ubicacion_limite"],
                    "source_date": row["fecha_datos_osm"],
                })
        return cls(grid, facilities)

    def analyze(self, incident: dict, *, now: datetime | None = None,
                offline: bool = False, weather_error: bool = False) -> dict:
        now = now or datetime.now(timezone.utc)
        wind = wind_state(incident["weather"], now, offline, weather_error)
        lon, lat = incident["lon"], incident["lat"]
        xscale = 111.32 * math.cos(math.radians(lat))
        footprint = scale(translate(shape(incident["footprint"]), -lon, -lat),
                          xfact=xscale, yfact=111.32, origin=(0, 0))
        if footprint.is_empty or not footprint.is_valid:
            raise ValueError("Huella térmica inválida para consultar el entorno")
        west, south, east, north = footprint.bounds

        def neighbors(lons: np.ndarray, lats: np.ndarray) -> tuple:
            candidates = np.flatnonzero(
                (lons >= lon + (west - RADIUS_KM) / xscale) & (lons <= lon + (east + RADIUS_KM) / xscale)
                & (lats >= lat + (south - RADIUS_KM) / 111.32) & (lats <= lat + (north + RADIUS_KM) / 111.32))
            points = shapely.points((lons[candidates] - lon) * xscale, (lats[candidates] - lat) * 111.32)
            distances = shapely.distance(footprint, points)
            keep = distances <= RADIUS_KM
            candidates, points, distances = candidates[keep], points[keep], distances[keep]
            downwind = np.zeros(len(candidates), dtype=bool)
            if wind["usable"] and len(points):
                nearest = shapely.get_point(shapely.shortest_line(footprint, points), 0)
                bearings = np.degrees(np.arctan2(shapely.get_x(points) - shapely.get_x(nearest),
                                                shapely.get_y(points) - shapely.get_y(nearest))) % 360
                delta = (bearings - wind["towards_degrees"] + 180) % 360 - 180
                downwind = (np.abs(delta) <= WIND_HALF_ANGLE) & (distances > 1e-6)
            return candidates, distances, downwind

        cell_ids, cell_distances, cell_downwind = neighbors(self.grid["lon"], self.grid["lat"])
        poi_ids, poi_distances, poi_downwind = neighbors(self.facility_coords[:, 0], self.facility_coords[:, 1])
        cells = self.grid[cell_ids]
        known_population = np.isfinite(cells["poblacion"]) & (cells["poblacion"] >= 0)
        inhabited = known_population & (cells["poblacion"] > 0)

        def total(field: str, mask: np.ndarray) -> int | None:
            values = cells[field][mask]
            valid = np.isfinite(values) & (values >= 0)
            return int(values[valid].sum()) if valid.any() else None

        population = {
            "residents": total("poblacion", known_population),
            "children_under_15": total("menores_15", known_population),
            "adults_65_plus": total("mayores_65", known_population),
            "inhabited_cells": int(inhabited.sum()), "missing_cells": int((~known_population).sum()),
            "age_missing_cells": int((~np.isfinite(cells["menores_15"]) | ~np.isfinite(cells["mayores_65"])).sum()),
            "downwind_residents": (int(cells["poblacion"][known_population & cell_downwind].sum())
                                   if wind["usable"] and known_population.any() else None),
            "nearest_km": round(float(cell_distances[inhabited].min()), 2) if inhabited.any() else None,
            "reference_year": 2021,
        }
        surface = cells["superficie_clasificada_km2"]
        valid_soil = np.isfinite(surface) & (surface > 0)
        percentages = {}
        for soil in SOILS:
            values = cells[f"pct_suelo_{soil}"]
            valid = valid_soil & np.isfinite(values) & (values >= 0) & (values <= 100)
            percentages[soil] = round(float(np.sum(values[valid] * surface[valid]) / surface[valid].sum()), 1) if valid.any() else None
        high = np.array([self.facilities[i]["priority"] == "alta_orientativa" for i in poi_ids], dtype=bool)
        categories: dict[str, int] = {}
        for i in poi_ids:
            category = self.facilities[i]["category"]
            categories[category] = categories.get(category, 0) + 1
        facilities = {"count": len(poi_ids), "high_priority": int(high.sum()),
                      "downwind_high_priority": int((high & poi_downwind).sum()) if wind["usable"] else None,
                      "categories": categories, "snapshot_date": "2026-09-18", "official_risk": "not_evaluated"}
        population_order = sorted(np.flatnonzero(inhabited), key=lambda i: (
            not cell_downwind[i], cell_distances[i], -cells["poblacion"][i]))[:6]
        facility_order = sorted(range(len(poi_ids)), key=lambda i: (
            not (poi_downwind[i] and high[i]), not high[i], poi_distances[i]))[:6]
        points = []
        for i in population_order:
            row = cells[i]
            points.append({
                "id": f"cell:{int(row['x_min_3035'])}:{int(row['y_min_3035'])}", "kind": "population",
                "name": "Celda habitada · censo 2021", "lon": float(row["lon"]), "lat": float(row["lat"]),
                "residents": int(row["poblacion"]), "distance_km": round(float(cell_distances[i]), 2),
                "downwind": bool(cell_downwind[i]), "priority": "population",
            })
        for i in facility_order:
            source = self.facilities[poi_ids[i]]
            points.append({**source, "kind": "facility", "category_label": CATEGORIES.get(source["category"], source["category"]),
                           "name": source["name"] or CATEGORIES.get(source["category"], "Instalación sin nombre"),
                           "distance_km": round(float(poi_distances[i]), 2), "downwind": bool(poi_downwind[i])})
        attention = wind["status"] == "current" and ((inhabited & cell_downwind).any() or (high & poi_downwind).any())
        return {
            "incident_id": incident["id"], "status": "ready", "radius_km": RADIUS_KM,
            "level": "attention" if attention else "nearby" if inhabited.any() or len(poi_ids) else "unverified",
            "coverage": "grid_centres_in_radius" if len(cells) else "no_grid_cells", "grid_cells": len(cells),
            "population": population, "facilities": facilities, "wind": wind,
            "landcover": {"percentages": percentages, "classified_km2": round(float(surface[valid_soil].sum()), 2),
                          "missing_cells": int((~valid_soil).sum()), "reference_year": 2019},
            "points": points, "points_truncated": int(inhabited.sum()) + len(poi_ids) > len(points),
            "method": "Centros de celdas de 1 km² y puntos OSM a ≤5 km de la huella térmica aproximada. "
                      "Distancias locales aproximadas, no a viviendas ni perímetros industriales. "
                      "A favor del viento: ±30° desde el punto más cercano de la huella, con viento ≥3 km/h. "
                      "No predice propagación, afección, evacuaciones ni riesgo oficial.",
            "sources": {"population": "INE / Eurostat · Census Grid 2021 · © European Union",
                        "landcover": "Buchhorn et al. · Copernicus CGLS-LC100 2019 · CC BY 4.0",
                        "facilities": "© OpenStreetMap contributors · Geofabrik · 18/09/2026 · ODbL 1.0",
                        "boundaries": "GISCO 2024 · © EuroGeographics for the administrative boundaries",
                        "details_url": "/atlas/sources"},
        }
