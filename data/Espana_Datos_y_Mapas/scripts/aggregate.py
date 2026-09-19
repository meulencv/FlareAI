from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import shapely
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
GROUPS = {
    "bosque": list(range(111, 117)) + list(range(121, 127)),
    "urbano": [50],
    "cultivos": [40],
    "matorral": [20],
    "herbaceas": [30],
    "suelo_desnudo": [60],
    "agua": [80],
    "humedales": [90],
    "nieve_hielo": [70],
    "musgos_liquenes": [100],
}


def main() -> None:
    df = pd.read_parquet(OUT / "censo_preparado.parquet")
    regions = gpd.read_file(OUT / "regiones_espana.geojson").to_crs(3035)
    for name in GROUPS:
        df[f"pct_suelo_{name}"] = np.nan
    df["superficie_clasificada_km2"] = 0.0
    for zone, subset in df.groupby("zona"):
        xmin, ymin = int(subset.x_min_3035.min()), int(subset.y_min_3035.min())
        xmax, ymax = int(subset.x_min_3035.max()) + 1000, int(subset.y_min_3035.max()) + 1000
        width, height = (xmax - xmin) // 100, (ymax - ymin) // 100
        transform = from_origin(xmin, ymax, 100, 100)
        print("Rasterize", zone, width, height, flush=True)
        source_name = "canarias" if zone == "Canarias" else "peninsula_baleares_ceuta_melilla"
        data = np.full((height, width), 255, dtype="uint8")
        with rasterio.open(ROOT / "raw" / f"lc2019_{source_name}.tif") as source:
            reproject(
                source=rasterio.band(source, 1),
                destination=data,
                src_transform=source.transform,
                src_crs=source.crs,
                dst_transform=transform,
                dst_crs="EPSG:3035",
                src_nodata=255,
                dst_nodata=255,
                resampling=Resampling.nearest,
                num_threads=4,
            )
        candidates = regions[regions.intersects(shapely.box(xmin, ymin, xmax, ymax))]
        mask = rasterize(
            [(geometry, 1) for geometry in candidates.geometry],
            out_shape=data.shape, transform=transform, fill=0, dtype="uint8",
        ).astype(bool)
        data[~mask] = 255
        valid = np.isin(data, [code for group in GROUPS.values() for code in group])
        shape = (height // 10, 10, width // 10, 10)
        counts = valid.reshape(shape).sum(axis=(1, 3))
        rows = ((ymax - subset.y_min_3035 - 1000) // 1000).to_numpy()
        columns = ((subset.x_min_3035 - xmin) // 1000).to_numpy()
        denominators = counts[rows, columns]
        df.loc[subset.index, "superficie_clasificada_km2"] = denominators / 100
        for name, codes in GROUPS.items():
            grouped = np.isin(data, codes).reshape(shape).sum(axis=(1, 3))
            numerator = grouped[rows, columns]
            percentage = np.divide(
                100 * numerator, denominators,
                out=np.full(len(subset), np.nan), where=denominators > 0,
            )
            df.loc[subset.index, f"pct_suelo_{name}"] = np.round(percentage, 3)
        print("Known surface", denominators.sum() / 100, flush=True)
    soil_columns = [f"pct_suelo_{name}" for name in GROUPS]
    valid_data = df.superficie_clasificada_km2.gt(0)
    df["suelo_dominante"] = "sin_datos"
    df.loc[valid_data, "suelo_dominante"] = (
        df.loc[valid_data, soil_columns].idxmax(axis=1).str.removeprefix("pct_suelo_")
    )
    df["pct_suelo_dominante"] = df[soil_columns].max(axis=1)
    df["suelo_mixto"] = df.pct_suelo_dominante.lt(50) & valid_data
    df["anio_suelo"] = 2019
    df["celda_costa_o_frontera"] = df.superficie_terrestre_censo_km2.lt(0.99)
    df.to_parquet(OUT / "espana_rejilla_1km.parquet", index=False)
    df.to_csv(OUT / "espana_rejilla_1km.csv.gz", index=False, compression="gzip")
    cells = gpd.GeoDataFrame(
        df,
        geometry=shapely.box(
            df.x_min_3035, df.y_min_3035,
            df.x_min_3035 + 1000, df.y_min_3035 + 1000,
        ),
        crs=3035,
    )
    cells.to_parquet(OUT / "espana_rejilla_1km.geoparquet", index=False)
    quality = {
        "celdas": len(df),
        "poblacion_publicada": int(df.poblacion.sum()),
        "celdas_con_poblacion": int(df.poblacion.gt(0).sum()),
        "celdas_sin_poblacion": int(df.poblacion.eq(0).sum()),
        "celdas_sin_suelo_clasificado": int((~valid_data).sum()),
        "poblacion_en_celdas_sin_suelo_clasificado": int(df.loc[~valid_data, "poblacion"].sum()),
        "celdas_suma_sexo_distinta_total": int(df.sexo_suma_distinta_total.sum()),
        "celdas_suma_edad_distinta_total": int(df.edad_suma_distinta_total.sum()),
        "superficie_censo_km2": float(df.superficie_terrestre_censo_km2.sum()),
        "superficie_clasificada_km2": float(df.superficie_clasificada_km2.sum()),
        "suma_pct_suelo_error_max": float((df.loc[valid_data, soil_columns].sum(axis=1) - 100).abs().max()),
        "poblacion_por_zona": {str(key): int(value) for key, value in df.groupby("zona").poblacion.sum().items()},
    }
    (OUT / "validacion_rejilla.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2))
    print(json.dumps(quality, ensure_ascii=False, indent=2), flush=True)
    summary = df.groupby("suelo_dominante").agg(
        celdas=("grid_id", "count"),
        poblacion_en_celda=("poblacion", "sum"),
        superficie_clasificada_km2=("superficie_clasificada_km2", "sum"),
    ).reset_index()
    summary.to_csv(OUT / "poblacion_por_suelo_dominante.csv", index=False)


if __name__ == "__main__":
    main()
