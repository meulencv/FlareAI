from __future__ import annotations

import hashlib
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from PIL import Image
from pyproj import Transformer

from aggregate import GROUPS
from prepare import COUNTS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
DESCRIPTIONS = {
    "grid_id": ("Identificador original de celda censal española", "texto"),
    "proporcion_no_contada": ("Proporción no contada declarada por el censo; nula si no informada", "fuente"),
    "estado_observacion_poblacion": ("OBS_STATUS de la variable T en la fuente", "código fuente"),
    "superficie_terrestre_censo_km2": ("LAND_SURFACE original, entre 0 y 1", "km²"),
    "valor_especial_poblacion": ("SPECIAL_VALUE de T en la fuente", "código fuente"),
    "proporcion_localizada_aprox": ("Proporción localizada aproximadamente, según fuente", "fuente"),
    "nota_poblacion": ("OBS_NOTE de T en la fuente", "texto"),
    "proporcion_localizada_conv": ("Proporción localizada convencionalmente, según fuente", "fuente"),
    "habitada_fuente": ("POPULATED original; puede diferir de poblacion>0 por confidencialidad", "0/1"),
    "x_min_3035": ("Este de esquina inferior izquierda de celda EPSG:3035", "m"),
    "y_min_3035": ("Norte de esquina inferior izquierda de celda EPSG:3035", "m"),
    "lon": ("Longitud WGS84 del centro de celda o punto de instalación", "grados"),
    "lat": ("Latitud WGS84 del centro de celda o punto de instalación", "grados"),
    "zona": ("Agrupación territorial de visualización; puede faltar en instalaciones sin celda", "categoría"),
    "densidad_celda_hab_km2": ("Población dividida por el km² completo de la celda", "hab/km²"),
    "densidad_tierra_hab_km2": ("Población / LAND_SURFACE; vacío si superficie cero", "hab/km² terrestre"),
    "edad_suma_distinta_total": ("Menores 15 + 15–64 + 65 y más difiere de T", "booleano"),
    "sexo_suma_distinta_total": ("M + F difiere de T", "booleano"),
    "anio_censo": ("Año de referencia de la población", "año"),
    "superficie_clasificada_km2": ("Píxeles válidos de 100 m interiores al límite español; excluye mar", "km²"),
    "suelo_dominante": ("Grupo de mayor porcentaje; sin_datos si no hay píxeles válidos", "categoría"),
    "pct_suelo_dominante": ("Máximo porcentaje entre las clases de suelo", "%"),
    "suelo_mixto": ("La clase dominante representa menos del 50 %; falso también sin datos", "booleano"),
    "anio_suelo": ("Año de referencia de Copernicus LC100", "año"),
    "celda_costa_o_frontera": ("LAND_SURFACE <0,99; indicador heurístico, no geometría de costa", "booleano"),
    "osm_type": ("Tipo de elemento OSM: node, way o relation", "categoría"),
    "osm_id": ("ID OSM; solo es único en combinación con osm_type", "entero"),
    "nombre": ("Etiqueta name; vacío cuando OSM no informa", "texto"),
    "categoria": ("Tipo de instalación asignado por etiquetas OSM", "categoría"),
    "prioridad_preventiva": ("alta_orientativa o revisar; no es una evaluación oficial", "categoría"),
    "criterio": ("Razón de la clasificación preventiva por etiqueta/actividad", "texto"),
    "riesgo_oficial": ("Siempre no_evaluado; no se ha obtenido un riesgo oficial por instalación", "categoría"),
    "metodo_coordenada": ("Nodo original o punto interior de polígono; no un perímetro", "categoría"),
    "operador": ("Etiqueta operator de OSM, cuando existe", "texto"),
    "iata": ("Código IATA declarado en OSM, cuando existe", "texto"),
    "icao": ("Código ICAO declarado en OSM, cuando existe", "texto"),
    "url_osm": ("Enlace al elemento público original", "URL"),
    "tags_fuente": ("Objeto JSON con etiquetas relevantes conservadas", "JSON"),
    "fecha_datos_osm": ("Timestamp de replicación de la cabecera PBF, no fecha de visita", "UTC"),
    "ubicacion_limite": ("Interior del límite o puerto exterior dentro de tolerancia de 1 km", "categoría"),
    "nuts2": ("Región más próxima al punto con la cartografía GISCO", "código NUTS2"),
    "comunidad": ("Nombre de la región NUTS2 más próxima", "texto"),
    "distancia_region_m": ("Distancia proyectada al polígono NUTS2 más cercano; 0 si interior", "m"),
    "poblacion_celda_1km": ("Población 2021 de la celda del punto, no población expuesta", "habitantes"),
    "pct_bosque_celda_1km": ("Porcentaje forestal 2019 de la celda del punto", "%"),
    "pct_urbano_celda_1km": ("Porcentaje urbano 2019 de la celda del punto", "%"),
}
COUNT_DESCRIPTIONS = {
    "poblacion": "Total de residentes, T",
    "hombres": "Hombres, M", "mujeres": "Mujeres, F",
    "menores_15": "Menores de 15 años, Y_LT15",
    "edad_15_64": "Edad 15–64, Y15-64", "mayores_65": "65 años o más, Y_GE65",
    "ocupados": "Personas ocupadas, EMP; no es tasa de empleo",
    "nacidos_espana": "Nacidos en España, NAT",
    "nacidos_otro_pais_ue": "Nacidos en otro país UE, EU_OTH",
    "nacidos_fuera_ue": "Nacidos fuera de la UE, OTH",
    "misma_residencia": "Residencia igual un año antes del censo, SAME",
    "mudanza_dentro_espana": "Cambio de residencia dentro de España respecto al año anterior, CHG_IN",
    "mudanza_desde_extranjero": "Cambio de residencia desde fuera de España, CHG_OUT",
}


def field_description(column: str) -> tuple[str, str]:
    if column in DESCRIPTIONS:
        return DESCRIPTIONS[column]
    if column in COUNT_DESCRIPTIONS:
        return COUNT_DESCRIPTIONS[column], "habitantes"
    if column.startswith("pct_suelo_"):
        group = column.removeprefix("pct_suelo_")
        return f"Porcentaje de {group} sobre superficie clasificada; vacío sin cobertura", "%"
    if column.startswith("pct_"):
        return (
            f"{column.removeprefix('pct_')}: porcentaje sobre T; vacío sin habitantes o fuera de 0–100",
            "%",
        )
    raise ValueError(f"Campo sin documentar: {column}")


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def main() -> None:
    grid = pd.read_parquet(OUT / "espana_rejilla_1km.parquet")
    poi = pd.read_parquet(OUT / "instalaciones_atencion_incendios.parquet")
    geometry = gpd.read_parquet(OUT / "espana_rejilla_1km.geoparquet")
    counts = list(COUNTS.values())
    soils = [f"pct_suelo_{name}" for name in GROUPS]
    assert grid.grid_id.is_unique
    assert grid[["x_min_3035", "y_min_3035"]].mod(1000).eq(0).all().all()
    assert len(grid) == len(geometry) == 511226
    assert int(grid.poblacion.sum()) == 47400134
    assert grid[counts].ge(0).all().all()
    assert grid[counts].notna().all().all()
    assert geometry.crs.to_epsg() == 3035
    assert np.allclose(geometry.area, 1_000_000)
    assert geometry.grid_id.equals(grid.grid_id)
    transform = Transformer.from_crs(4326, 3035, always_xy=True)
    x, y = transform.transform(grid.lon.to_numpy(), grid.lat.to_numpy())
    coordinate_error = np.hypot(x - grid.x_min_3035 - 500, y - grid.y_min_3035 - 500)
    assert coordinate_error.max() < 0.15
    valid_soil = grid.superficie_clasificada_km2.gt(0)
    assert grid.loc[~valid_soil, soils].isna().all().all()
    assert grid.loc[valid_soil, soils].ge(0).all().all()
    assert grid.loc[valid_soil, soils].le(100).all().all()
    soil_error = (grid.loc[valid_soil, soils].sum(axis=1) - 100).abs().max()
    assert soil_error <= 0.005
    for column in [c for c in grid if c.startswith("pct_")]:
        assert grid[column].dropna().between(0, 100).all()
    assert grid.densidad_celda_hab_km2.eq(grid.poblacion).all()
    assert not poi.duplicated(["osm_type", "osm_id"]).any()
    assert poi.url_osm.is_unique
    assert poi.lon.between(-19, 5).all() and poi.lat.between(27, 44.5).all()
    assert poi.riesgo_oficial.eq("no_evaluado").all()
    assert poi.nuts2.nunique() == 19
    assert set(poi.prioridad_preventiva) == {"alta_orientativa", "revisar"}
    assert poi.distancia_region_m.le(1000.01).all()
    airports = poi[poi.categoria.eq("aeropuerto_aerodromo")]
    assert {"MAD", "BCN", "PMI", "LPA"}.issubset(set(airports.iata))
    dictionary = []
    for name, table in [("rejilla", grid), ("instalaciones", poi)]:
        for column in table:
            description, unit = field_description(column)
            dictionary.append({
                "tabla": name, "campo": column, "descripcion": description,
                "unidad": unit, "tipo_pandas": str(table[column].dtype),
                "nulos": int(table[column].isna().sum()),
            })
    pd.DataFrame(dictionary).to_csv(OUT / "diccionario_campos.csv", index=False)
    pd.DataFrame([
        {
            "cobertura": group,
            "superficie_aproximada_km2": round(float(
                (grid[f"pct_suelo_{group}"] * grid.superficie_clasificada_km2 / 100).sum()
            ), 3),
        }
        for group in GROUPS
    ]).to_csv(OUT / "superficie_por_cobertura.csv", index=False)
    images = sorted((ROOT / "mapas").glob("*.png"))
    assert len(images) == 34
    for path in images:
        with Image.open(path) as image:
            assert image.size == (2520, 1890), (path, image.size)
            image.verify()
    report = {
        "resultado": "OK",
        "celdas": len(grid),
        "columnas_rejilla": len(grid.columns),
        "columnas_instalaciones": len(poi.columns),
        "poblacion_total": int(grid.poblacion.sum()),
        "coordenadas_error_max_m": float(coordinate_error.max()),
        "suma_porcentajes_suelo_error_max": float(soil_error),
        "geoparquet_crs": f"EPSG:{geometry.crs.to_epsg()}",
        "area_cada_celda_m2": 1000000,
        "instalaciones": len(poi),
        "regiones_nuts2_instalaciones": int(poi.nuts2.nunique()),
        "instalaciones_sin_celda_censo": int(poi.grid_id.isna().sum()),
        "instalaciones_sin_nombre": int(poi.nombre.eq("").sum()),
        "sin_suelo": int((~valid_soil).sum()),
        "porcentajes_demograficos_fuera_0_100": 0,
        "imagenes_png_validadas": len(images),
        "controles_airports_iata": ["MAD", "BCN", "PMI", "LPA"],
    }
    (OUT / "comprobaciones.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)
    )
    hashes = {}
    for filename in [
        "Eurostat_Census-GRID_2021_V3.zip", "ESTAT_Census_2021_country.csv.zip",
        "nuts2_2024.geojson", "spain.osm.pbf", "canarias.osm.pbf",
        "lc2019_peninsula_baleares_ceuta_melilla.tif", "lc2019_canarias.tif",
    ]:
        path = ROOT / "raw" / filename
        if path.exists():
            hashes[filename] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    (OUT / "huellas_fuentes.json").write_text(json.dumps(hashes, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
