from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import osmium
import pandas as pd
import shapely
from osmium.osm import Area, Node
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
KEYS = ["aeroway", "harbour", "landuse", "industrial", "man_made", "amenity",
        "power", "seamark:type", "leisure"]
FLAMMABLE = {
    "oil", "gas", "oil_storage", "gas_storage", "refinery", "petrochemical",
    "chemical", "fuel", "fuel_storage", "petroleum", "lpg", "lng",
}


def classify(tags: dict[str, str]) -> tuple[str, str, str] | None:
    industrial = tags.get("industrial", "")
    if industrial in FLAMMABLE:
        return (
            "combustibles_quimica", "alta_orientativa",
            f"Etiqueta industrial={industrial}; revisar sustancias y plan de emergencia.",
        )
    if tags.get("amenity") == "fuel":
        return (
            "gasolinera", "alta_orientativa",
            "Suministro de combustible identificado en OSM.",
        )
    if tags.get("man_made") in {"storage_tank", "silo"}:
        content = tags.get("content", tags.get("substance", ""))
        if set(content.split(";")) & FLAMMABLE:
            return (
                "combustibles_quimica", "alta_orientativa",
                f"Deposito con contenido declarado: {content}.",
            )
        return None
    if tags.get("aeroway") == "aerodrome":
        return (
            "aeropuerto_aerodromo", "alta_orientativa",
            "Infraestructura aeronautica; prioridad por consecuencias y operacion. "
            "No confirma almacenamiento de combustible.",
        )
    if tags.get("aeroway") == "heliport":
        return (
            "helipuerto", "revisar",
            "Instalacion aeronautica; actividad y combustible por verificar.",
        )
    if (
        tags.get("landuse") == "port" or industrial == "port"
        or tags.get("harbour") in {"yes", "port"}
        or tags.get("seamark:type") == "harbour"
    ):
        return (
            "puerto", "alta_orientativa",
            "Infraestructura portuaria; prioridad logistica. "
            "Carga peligrosa o combustible no verificados.",
        )
    if tags.get("leisure") == "marina":
        return "puerto_deportivo", "revisar", "Puerto deportivo; combustible por verificar."
    if tags.get("power") == "plant":
        source = tags.get("plant:source", "")
        if set(source.split(";")) & {"oil", "gas", "coal", "biomass", "waste"}:
            return (
                "central_combustion", "alta_orientativa",
                f"Fuente energetica declarada en OSM: {source}.",
            )
        return None
    if tags.get("landuse") == "landfill":
        return (
            "vertedero", "alta_orientativa",
            "Residuos: posible combustion o gases; inventario y estado por verificar.",
        )
    if tags.get("amenity") in {"waste_transfer_station", "recycling"}:
        if tags.get("recycling_type") == "container":
            return None
        if tags.get("amenity") == "recycling" and tags.get("recycling_type") != "centre":
            return None
        return (
            "gestion_residuos", "revisar",
            "Centro de residuos; composicion, volumen y proceso desconocidos.",
        )
    if tags.get("man_made") == "works":
        return (
            "fabrica", "alta_orientativa",
            "Fabrica mapeada; prioridad de inspeccion. Proceso y carga de fuego desconocidos.",
        )
    if tags.get("landuse") == "industrial":
        return (
            "area_industrial", "revisar",
            "Poligono o suelo industrial; no equivale a una fabrica ni acredita riesgo alto.",
        )
    return None


def main() -> None:
    factory = osmium.geom.WKBFactory()
    records = []
    metadata = {}
    geometry_errors = 0
    for filename in ["spain.osm.pbf", "canarias.osm.pbf"]:
        path = ROOT / "raw" / filename
        with osmium.io.Reader(str(path)) as reader:
            metadata[filename] = {
                "timestamp": reader.header().get("osmosis_replication_timestamp"),
                "generator": reader.header().get("generator"),
            }
        print("Processing", filename, metadata[filename], flush=True)
        processor = (
            osmium.FileProcessor(str(path))
            .with_locations()
            .with_areas(osmium.filter.KeyFilter(*KEYS))
            .with_filter(osmium.filter.KeyFilter(*KEYS))
        )
        for obj in processor:
            if not isinstance(obj, (Node, Area)):
                continue
            tags = dict(obj.tags)
            if tags.get("addr:country", "ES") != "ES":
                continue
            if any(tags.get(key) == "yes" for key in ["disused", "abandoned", "demolished"]):
                continue
            result = classify(tags)
            if result is None:
                continue
            category, priority, reason = result
            if isinstance(obj, Node):
                if not obj.location.valid():
                    geometry_errors += 1
                    continue
                point = shapely.Point(obj.location.lon, obj.location.lat)
                osm_type, osm_id, method = "node", obj.id, "coordenada_osm"
            else:
                try:
                    geometry = shapely.from_wkb(factory.create_multipolygon(obj))
                    point = geometry.representative_point()
                except (RuntimeError, ValueError):
                    geometry_errors += 1
                    continue
                osm_type = "way" if obj.from_way() else "relation"
                osm_id, method = obj.orig_id(), "punto_interior_poligono"
            kept = {
                key: value for key, value in tags.items()
                if key in set(KEYS) | {
                    "name", "operator", "iata", "icao", "plant:source",
                    "content", "substance", "product", "recycling_type",
                    "aerodrome:type", "addr:country", "start_date",
                }
            }
            records.append({
                "osm_type": osm_type, "osm_id": osm_id,
                "nombre": tags.get("name", ""),
                "categoria": category, "prioridad_preventiva": priority,
                "criterio": reason, "riesgo_oficial": "no_evaluado",
                "lon": point.x, "lat": point.y,
                "metodo_coordenada": method,
                "operador": tags.get("operator", ""),
                "iata": tags.get("iata", ""), "icao": tags.get("icao", ""),
                "url_osm": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
                "tags_fuente": json.dumps(kept, ensure_ascii=False),
                "fecha_datos_osm": metadata[filename]["timestamp"],
            })
        print("Records so far", len(records), flush=True)
    df = pd.DataFrame(records).drop_duplicates(["osm_type", "osm_id"])
    points = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326
    ).to_crs(3035)
    regions = gpd.read_file(OUT / "regiones_espana.geojson").to_crs(3035)
    country = regions.geometry.union_all()
    inside = points.intersects(country)
    coastal_category = df.categoria.isin(["puerto", "puerto_deportivo"])
    coastal = ~inside & coastal_category & points.distance(country).le(1000)
    points["ubicacion_limite"] = np.where(inside, "interior", "puerto_costa_hasta_1km")
    points = points[inside | coastal].copy()
    rejected = int(len(df) - len(points))
    nearest = gpd.sjoin_nearest(
        points, regions[["NUTS_ID", "NAME_LATN", "geometry"]],
        how="left", distance_col="distancia_region_m",
    ).drop_duplicates(["osm_type", "osm_id"])
    df = pd.DataFrame(nearest.drop(columns=["geometry", "index_right"])).rename(
        columns={"NUTS_ID": "nuts2", "NAME_LATN": "comunidad"}
    )
    transformer = Transformer.from_crs(4326, 3035, always_xy=True)
    x, y = transformer.transform(df.lon.to_numpy(), df.lat.to_numpy())
    df["x_min_3035"] = (np.floor(x / 1000) * 1000).astype("int32")
    df["y_min_3035"] = (np.floor(y / 1000) * 1000).astype("int32")
    grid = pd.read_parquet(OUT / "espana_rejilla_1km.parquet")
    df = df.merge(
        grid[["x_min_3035", "y_min_3035", "grid_id", "zona", "poblacion",
              "pct_suelo_bosque", "pct_suelo_urbano"]],
        how="left", on=["x_min_3035", "y_min_3035"], validate="many_to_one",
    ).rename(columns={
        "poblacion": "poblacion_celda_1km",
        "pct_suelo_bosque": "pct_bosque_celda_1km",
        "pct_suelo_urbano": "pct_urbano_celda_1km",
    })
    df["lon"] = df.lon.round(6)
    df["lat"] = df.lat.round(6)
    df.to_csv(OUT / "instalaciones_atencion_incendios.csv", index=False)
    df.to_parquet(OUT / "instalaciones_atencion_incendios.parquet", index=False)
    gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326
    ).to_file(OUT / "instalaciones_atencion_incendios.geojson", driver="GeoJSON")
    summary = {
        "extractos": metadata,
        "elementos": len(df),
        "errores_geometria": geometry_errors,
        "excluidos_fuera_ambito": rejected,
        "puertos_costa_revisar": int(coastal.sum()),
        "categorias": {str(k): int(v) for k, v in df.categoria.value_counts().items()},
        "prioridades": {str(k): int(v) for k, v in df.prioridad_preventiva.value_counts().items()},
        "comunidades": {str(k): int(v) for k, v in df.comunidad.value_counts().items()},
    }
    (OUT / "validacion_instalaciones.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
