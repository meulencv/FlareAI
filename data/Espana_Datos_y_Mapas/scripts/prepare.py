from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "output"
COUNTS = {
    "T": "poblacion",
    "M": "hombres",
    "F": "mujeres",
    "Y_LT15": "menores_15",
    "Y15-64": "edad_15_64",
    "Y_GE65": "mayores_65",
    "EMP": "ocupados",
    "NAT": "nacidos_espana",
    "EU_OTH": "nacidos_otro_pais_ue",
    "OTH": "nacidos_fuera_ue",
    "SAME": "misma_residencia",
    "CHG_IN": "mudanza_dentro_espana",
    "CHG_OUT": "mudanza_desde_extranjero",
}


def main() -> None:
    cols = [
        "STAT", "SPATIAL", "OBS_VALUE", "LAND_SURFACE", "POPULATED",
        "OBS_STATUS", "SPECIAL_VALUE", "OBS_NOTE",
        "APPROXIMATELY_LOCATED_POPULATION_PROPORTION",
        "CONVENTIONALLY_LOCATED_PROPORTION", "NOT_COUNTED_PROPORTION",
    ]
    with ZipFile(RAW / "ESTAT_Census_2021_country.csv.zip") as archive:
        with archive.open("CENSUS_GRID_N_ES_2021.csv") as file:
            data = pd.read_csv(file, usecols=cols, low_memory=False)
    print("Raw shape:", data.shape, flush=True)
    diagnostics = {}
    for col in cols:
        if col not in {"SPATIAL", "OBS_VALUE", "LAND_SURFACE"}:
            diagnostics[col] = {
                str(key): int(value)
                for key, value in data[col].value_counts(dropna=False).head(30).items()
            }
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2), flush=True)
    (OUT / "diagnostico_censo.json").write_text(
        json.dumps(diagnostics, ensure_ascii=False, indent=2)
    )
    assert not data.duplicated(["SPATIAL", "STAT"]).any()
    base = data.loc[data.STAT.eq("T")].set_index("SPATIAL").drop(
        columns=["STAT", "OBS_VALUE"]
    )
    values = data.pivot(index="SPATIAL", columns="STAT", values="OBS_VALUE")
    values = values.rename(columns=COUNTS)
    values.columns.name = None
    values = values.mask(values < 0)
    df = base.join(values).reset_index().rename(
        columns={
            "SPATIAL": "grid_id",
            "LAND_SURFACE": "superficie_terrestre_censo_km2",
            "POPULATED": "habitada_fuente",
            "OBS_STATUS": "estado_observacion_poblacion",
            "SPECIAL_VALUE": "valor_especial_poblacion",
            "OBS_NOTE": "nota_poblacion",
            "APPROXIMATELY_LOCATED_POPULATION_PROPORTION": "proporcion_localizada_aprox",
            "CONVENTIONALLY_LOCATED_PROPORTION": "proporcion_localizada_conv",
            "NOT_COUNTED_PROPORTION": "proporcion_no_contada",
        }
    )
    coords = df.grid_id.str.extract(r"N(?P<north>\d+)E(?P<east>\d+)$")
    assert coords.notna().all().all()
    df["x_min_3035"] = coords.east.astype("int32")
    df["y_min_3035"] = coords.north.astype("int32")
    transformer = Transformer.from_crs(3035, 4326, always_xy=True)
    df["lon"], df["lat"] = transformer.transform(
        df.x_min_3035 + 500, df.y_min_3035 + 500
    )
    df["lon"] = df.lon.round(6)
    df["lat"] = df.lat.round(6)
    df["zona"] = np.select(
        [df.lon.lt(-12), df.lon.gt(1), df.lat.lt(36) & df.lon.lt(-4),
         df.lat.lt(36) & df.lon.ge(-4)],
        ["Canarias", "Baleares_o_Peninsula", "Ceuta", "Melilla"],
        default="Peninsula",
    )
    df.loc[df.lon.gt(1) & df.lat.lt(40.2), "zona"] = "Baleares"
    df.loc[df.zona.eq("Baleares_o_Peninsula"), "zona"] = "Peninsula"
    for name in COUNTS.values():
        df[name] = df[name].astype("Int32")
    df["densidad_celda_hab_km2"] = df.poblacion.astype("float64")
    df["densidad_tierra_hab_km2"] = (
        df.poblacion / df.superficie_terrestre_censo_km2.replace(0, np.nan)
    ).round(3)
    for name in ["hombres", "mujeres", "menores_15", "edad_15_64", "mayores_65"]:
        ratio = 100 * df[name] / df.poblacion.replace(0, np.nan)
        df[f"pct_{name}"] = ratio.where(ratio.between(0, 100)).round(3)
    ratio = 100 * (df.nacidos_otro_pais_ue + df.nacidos_fuera_ue) / df.poblacion.replace(0, np.nan)
    df["pct_nacidos_extranjero"] = ratio.where(ratio.between(0, 100)).round(3)
    df["edad_suma_distinta_total"] = (
        df.menores_15 + df.edad_15_64 + df.mayores_65
    ).ne(df.poblacion)
    df["sexo_suma_distinta_total"] = (df.hombres + df.mujeres).ne(df.poblacion)
    df["anio_censo"] = 2021
    df.to_parquet(OUT / "censo_preparado.parquet", index=False)
    regions = gpd.read_file(RAW / "nuts2_2024.geojson")
    regions = regions.loc[regions.CNTR_CODE.eq("ES")].copy()
    regions.to_file(OUT / "regiones_espana.geojson", driver="GeoJSON")
    print("TOTALS", df[list(COUNTS.values())].sum().to_dict(), flush=True)
    print("ZONES", df.groupby("zona").agg(
        celdas=("grid_id", "count"), poblacion=("poblacion", "sum"),
        lat_min=("lat", "min"), lat_max=("lat", "max")
    ).to_string(), flush=True)
    print("REGIONS", regions[["NUTS_ID", "NAME_LATN"]].to_string(), flush=True)


if __name__ == "__main__":
    main()
