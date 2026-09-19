from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LogNorm, Normalize
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
MAPS = ROOT / "mapas"
NAVY = "#153247"
MUTED = "#587080"
LAND = "#e5eaed"
OCEAN = "#f6f9fb"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "text.color": NAVY, "axes.labelcolor": NAVY, "figure.facecolor": "white",
    "savefig.facecolor": "white", "pdf.fonttype": 42,
})


@dataclass
class Metric:
    column: str
    title: str
    subtitle: str
    kind: str
    cmap: str


COUNTS = {
    "poblacion": "Concentración de población",
    "hombres": "Población masculina",
    "mujeres": "Población femenina",
    "menores_15": "Población menor de 15 años",
    "edad_15_64": "Población de 15 a 64 años",
    "mayores_65": "Población de 65 años o más",
    "ocupados": "Personas ocupadas",
    "nacidos_espana": "Personas nacidas en España",
    "nacidos_otro_pais_ue": "Personas nacidas en otro país de la UE",
    "nacidos_fuera_ue": "Personas nacidas fuera de la UE",
    "misma_residencia": "Sin cambio de residencia respecto al año anterior",
    "mudanza_dentro_espana": "Cambio de residencia dentro de España",
    "mudanza_desde_extranjero": "Cambio de residencia desde el extranjero",
}
PERCENTAGES = {
    "pct_hombres": "Porcentaje de hombres",
    "pct_mujeres": "Porcentaje de mujeres",
    "pct_menores_15": "Porcentaje de menores de 15 años",
    "pct_edad_15_64": "Porcentaje de población de 15 a 64 años",
    "pct_mayores_65": "Porcentaje de población de 65 años o más",
    "pct_nacidos_extranjero": "Porcentaje de población nacida en el extranjero",
}
SOILS = {
    "bosque": ("Cobertura de bosque", "YlGn"),
    "urbano": ("Cobertura urbana y construida", "YlOrRd"),
    "cultivos": ("Cobertura de cultivos", "YlGnBu"),
    "matorral": ("Cobertura de matorral", "YlGn"),
    "herbaceas": ("Cobertura de vegetación herbácea", "YlGn"),
    "suelo_desnudo": ("Cobertura de suelo desnudo o vegetación escasa", "YlOrBr"),
    "agua": ("Cobertura de agua permanente", "Blues"),
    "humedales": ("Cobertura de humedales herbáceos", "GnBu"),
    "nieve_hielo": ("Cobertura de nieve y hielo", "PuBu"),
    "musgos_liquenes": ("Cobertura de musgos y líquenes", "BuGn"),
}
METRICS = [
    Metric(key, title, "Censo 2021 · habitantes por celda de 1 km² · escala logarítmica",
           "count", "magma_r") for key, title in COUNTS.items()
] + [
    Metric(key, title, "Censo 2021 · % de la población · se muestran celdas con al menos 20 habitantes",
           "population_pct", "YlOrRd") for key, title in PERCENTAGES.items()
] + [
    Metric(f"pct_suelo_{key}", title,
           "Copernicus 2019 · % de superficie clasificada dentro de cada celda de 1 km²",
           "soil", cmap) for key, (title, cmap) in SOILS.items()
]
CATEGORIES = {
    "combustibles_quimica": ("Combustibles / química", "#d73027"),
    "gasolinera": ("Gasolineras", "#ff8847"),
    "central_combustion": ("Centrales de combustión", "#8b1c62"),
    "aeropuerto_aerodromo": ("Aeropuertos / aeródromos", "#2853bd"),
    "helipuerto": ("Helipuertos", "#96b7e1"),
    "puerto": ("Puertos", "#008c95"),
    "puerto_deportivo": ("Puertos deportivos", "#80c9bf"),
    "fabrica": ("Fábricas", "#6940a2"),
    "area_industrial": ("Áreas industriales", "#a8abb9"),
    "vertedero": ("Vertederos", "#82562f"),
    "gestion_residuos": ("Centros de residuos", "#b99870"),
}
REGION_ZONES = {"ES70": "Canarias", "ES53": "Baleares", "ES63": "Ceuta", "ES64": "Melilla"}
PANELS = {
    "Peninsula": (0.025, 0.22, 0.655, 0.64),
    "Baleares": (0.70, 0.62, 0.27, 0.23),
    "Canarias": (0.70, 0.32, 0.27, 0.23),
    "Ceuta": (0.06, 0.08, 0.23, 0.13),
    "Melilla": (0.34, 0.08, 0.28, 0.13),
}


def number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def frame(title: str, subtitle: str, footer: str) -> Figure:
    fig = plt.figure(figsize=(14, 10.5))
    fig.text(0.035, 0.967, "ESPAÑA  /  ATLAS TERRITORIAL", fontsize=10, weight="bold",
             color="#008c95")
    fig.text(0.035, 0.918, title, fontsize=23, weight="bold")
    fig.text(0.035, 0.883, subtitle, fontsize=10.5, color=MUTED)
    fig.text(0.035, 0.025, footer, fontsize=8, color=MUTED, linespacing=1.5)
    return fig


def make_panels(fig: Figure, grid: pd.DataFrame, regions: gpd.GeoDataFrame) -> dict[str, Axes]:
    axes = {}
    for zone, position in PANELS.items():
        ax = fig.add_axes(position)
        axes[zone] = ax
        subset = grid[grid.zona.eq(zone)]
        xmin, xmax = subset.x_min_3035.min(), subset.x_min_3035.max() + 1000
        ymin, ymax = subset.y_min_3035.min(), subset.y_min_3035.max() + 1000
        pad = max(xmax - xmin, ymax - ymin) * 0.025
        selected = regions[regions.zona.eq(zone)]
        selected.plot(ax=ax, facecolor=LAND, edgecolor="none", zorder=1)
        ax.set_xlim(xmin - pad, xmax + pad)
        ax.set_ylim(ymin - pad, ymax + pad)
        ax.set_facecolor(OCEAN)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor("#dce4e8")
        label = "Península" if zone == "Peninsula" else zone
        if zone == "Melilla":
            label = "Melilla e islas próximas"
        ax.set_title(label, loc="left", fontsize=11, weight="bold", pad=7)
        ax.text(0.985, 0.025, "N de cuadrícula ↑", transform=ax.transAxes, ha="right",
                fontsize=8, color=MUTED)
    return axes


def grid_image(ax: Axes, subset: pd.DataFrame, metric: Metric, norm: Normalize) -> None:
    xmin, xmax = int(subset.x_min_3035.min()), int(subset.x_min_3035.max()) + 1000
    ymin, ymax = int(subset.y_min_3035.min()), int(subset.y_min_3035.max()) + 1000
    image = np.full(((ymax - ymin) // 1000, (xmax - xmin) // 1000), np.nan)
    rows = ((ymax - subset.y_min_3035 - 1000) // 1000).to_numpy()
    cols = ((subset.x_min_3035 - xmin) // 1000).to_numpy()
    values = subset[metric.column].to_numpy(dtype=float, na_value=np.nan)
    if metric.kind == "count":
        values[values <= 0] = np.nan
    elif metric.kind == "population_pct":
        values[subset.poblacion.to_numpy() < 20] = np.nan
    image[rows, cols] = values
    ax.imshow(image, extent=(xmin, xmax, ymin, ymax), origin="upper",
              cmap=metric.cmap, norm=norm, interpolation="nearest", rasterized=True, zorder=2)


def metric_map(grid: pd.DataFrame, regions: gpd.GeoDataFrame, metric: Metric) -> Figure:
    footer = (
        "Fuentes: INE/Eurostat 2021 V3; Copernicus CGLS-LC100 2019; GISCO 2024. "
        "© EuroGeographics for the administrative boundaries.\n"
        "ETRS89-LAEA (EPSG:3035) · Recuadros a distintas escalas · Gris: cero / sin dato representable "
        "en población; sin cobertura en suelo."
    )
    fig = frame(metric.title, metric.subtitle, footer)
    axes = make_panels(fig, grid, regions)
    norm: Normalize
    if metric.kind == "count":
        norm = LogNorm(vmin=1, vmax=max(10, float(grid[metric.column].max())))
    else:
        norm = Normalize(vmin=0, vmax=100)
    for zone, ax in axes.items():
        grid_image(ax, grid[grid.zona.eq(zone)], metric, norm)
        regions[regions.zona.eq(zone)].boundary.plot(
            ax=ax, color="#47677c", linewidth=0.3, alpha=0.75, zorder=3
        )
    cax = fig.add_axes((0.725, 0.195, 0.23, 0.018))
    bar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=metric.cmap),
                      cax=cax, orientation="horizontal")
    bar.ax.tick_params(labelsize=8)
    if metric.kind == "count":
        maximum = float(grid[metric.column].max())
        ticks = [t for t in [1, 10, 100, 1000, 10000, 100000] if t <= maximum]
        bar.set_ticks(ticks)
        bar.ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: number(x)))
        bar.set_label("Habitantes por km² de celda · log", fontsize=9)
        fig.text(0.725, 0.125, f"Total publicado: {number(grid[metric.column].sum())}",
                 fontsize=10, weight="bold")
        fig.text(0.725, 0.103, "Las categorías censales pueden no sumar el total.",
                 fontsize=8, color=MUTED)
    else:
        bar.set_label("% de superficie" if metric.kind == "soil" else "% de población",
                      fontsize=9)
        note = "0 %: tono más claro. No es un dato ausente."
        if metric.kind == "population_pct":
            note = "Celdas <20 habitantes: no representadas.\nPorcentajes fuera de 0–100: sin dato."
        fig.text(0.725, 0.12, note, fontsize=9, color=MUTED, linespacing=1.5)
        if grid[metric.column].fillna(0).max() == 0:
            fig.text(0.725, 0.08, "No se detecta esta clase en la rejilla.", fontsize=9)
    return fig


def poi_map(
    grid: pd.DataFrame, regions: gpd.GeoDataFrame, points: gpd.GeoDataFrame,
    categories: list[str], title: str,
) -> Figure:
    dates = " / ".join(sorted(points.fecha_datos_osm.str[:10].unique()))
    fig = frame(
        title, f"Inventario OSM · extractos {dates} · puntos por tipo de instalación",
        "© OpenStreetMap contributors · https://www.openstreetmap.org/copyright · ODbL 1.0 · Geofabrik. "
        "Clasificación propia.\n"
        "Límites GISCO 2024: © EuroGeographics for the administrative boundaries.\n"
        "No es un mapa oficial de riesgo ni un inventario completo. Elementos OSM, no establecimientos únicos. "
        "Recuadros a distintas escalas.",
    )
    axes = make_panels(fig, grid, regions)
    selected = points[points.categoria.isin(categories)]
    point_zones = selected.nuts2.map(REGION_ZONES).fillna("Peninsula")
    for zone, ax in axes.items():
        part = selected[point_zones.eq(zone)]
        for key in categories:
            group = part[part.categoria.eq(key)]
            if group.empty:
                continue
            ax.scatter(group.geometry.x, group.geometry.y,
                       s=5 if key not in {"aeropuerto_aerodromo", "puerto"} else 12,
                       color=CATEGORIES[key][1], alpha=0.7, linewidths=0,
                       rasterized=True, zorder=2)
        regions[regions.zona.eq(zone)].boundary.plot(ax=ax, linewidth=0.35, color="#607889")
    handles = [
        Line2D([0], [0], marker="o", linestyle="", markersize=5, color=CATEGORIES[key][1],
               label=f"{CATEGORIES[key][0]} ({number((selected.categoria == key).sum())})")
        for key in categories
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.692, 0.305),
               frameon=False, fontsize=8.3, labelspacing=0.42)
    return fig


def cover(grid: pd.DataFrame, points: pd.DataFrame) -> Figure:
    fig = plt.figure(figsize=(14, 10.5))
    fig.text(0.07, 0.91, "DATOS ABIERTOS  /  ESPAÑA", color="#008c95", fontsize=14, weight="bold")
    fig.text(0.07, 0.79, "Población, territorio\ny atención preventiva", fontsize=38,
             weight="bold", linespacing=1.15)
    fig.text(0.07, 0.65, "Atlas de mapas y paquete geográfico reutilizable", fontsize=18, color=MUTED)
    for x, value, label in [
        (0.07, number(grid.poblacion.sum()), "habitantes · censo de 2021"),
        (0.40, number(len(grid)), "celdas · rejilla de 1 km²"),
        (0.71, number(len(points)), "elementos OSM · instalaciones"),
    ]:
        fig.text(x, 0.52, value, fontsize=29, weight="bold")
        fig.text(x, 0.48, label, fontsize=11, color=MUTED)
    fig.text(
        0.07, 0.37,
        "29 mapas por variable + 5 mapas de instalaciones\n"
        "Península · Baleares · Canarias · Ceuta · Melilla\n\n"
        "Población: INE / Eurostat 2021, versión 3\n"
        "Suelo: Copernicus CGLS-LC100 2019, resolución original de 100 m\n"
        "Instalaciones: OpenStreetMap / Geofabrik, fecha en cada mapa",
        fontsize=15, linespacing=1.65,
    )
    fig.text(0.07, 0.105,
             "La prioridad preventiva es una clasificación exploratoria. "
             "No acredita riesgo oficial de incendio.\n"
             "Los datos de distintas fechas no describen una fotografía simultánea del territorio.",
             fontsize=12, color=MUTED, linespacing=1.6)
    return fig


def priority_map(
    grid: pd.DataFrame, regions: gpd.GeoDataFrame, points: gpd.GeoDataFrame,
) -> Figure:
    date = " / ".join(sorted(points.fecha_datos_osm.str[:10].unique()))
    fig = frame(
        "Prioridad preventiva ante incendios",
        f"Clasificación exploratoria por tipo de instalación · OSM {date} · sin acreditación de riesgo oficial",
        "© OpenStreetMap contributors · https://www.openstreetmap.org/copyright · ODbL 1.0 · Geofabrik. "
        "Clasificación propia.\n"
        "Límites GISCO 2024: © EuroGeographics for the administrative boundaries. "
        "Cobertura no exhaustiva. Recuadros a distintas escalas.",
    )
    axes = make_panels(fig, grid, regions)
    point_zones = points.nuts2.map(REGION_ZONES).fillna("Peninsula")
    priorities = {
        "revisar": ("Para revisar", "#a8b6c2"),
        "alta_orientativa": ("Alta orientativa", "#d43e2a"),
    }
    for zone, ax in axes.items():
        for key, (_, color) in priorities.items():
            part = points[point_zones.eq(zone) & points.prioridad_preventiva.eq(key)]
            ax.scatter(part.geometry.x, part.geometry.y, s=5, color=color, alpha=0.65,
                       linewidths=0, rasterized=True, zorder=2)
        regions[regions.zona.eq(zone)].boundary.plot(ax=ax, linewidth=0.3, color="#607889")
    fig.legend(handles=[
        Line2D([0], [0], marker="o", linestyle="", color=color, markersize=7,
               label=f"{title}: {number(points.prioridad_preventiva.eq(key).sum())}")
        for key, (title, color) in priorities.items()
    ], loc="upper left", bbox_to_anchor=(0.70, 0.30), frameon=False, fontsize=11)
    fig.text(
        0.705, 0.215,
        "Alta: combustibles, fábricas, puertos,\n"
        "aeródromos, vertederos y centrales\n"
        "de combustión identificados en OSM.\n\n"
        "Prioridad de revisión por actividad\n"
        "o consecuencias; no riesgo medido.",
        fontsize=10, color=MUTED, linespacing=1.4, va="top",
    )
    return fig


def notes() -> Figure:
    fig = frame("Cómo leer y reutilizar este atlas", "Método · unidades · límites de interpretación", "")
    blocks = [
        ("01  Población real por celda",
         "Cada cuadrado mide 1 km × 1 km en EPSG:3035. Los mapas de recuentos equivalen a habitantes\n"
         "por km² de celda completa; la escala logarítmica permite ver ciudades y núcleos rurales.\n"
         "El CSV también conserva la densidad dividida por superficie terrestre censal, distinta en costas."),
        ("02  Suelo y población se cruzan espacialmente",
         "Las clases de 100 m de Copernicus se reproyectan y agrupan por celda. Los porcentajes se calculan\n"
         "sobre los píxeles clasificados dentro del límite español, excluyendo el mar. No se asigna cada\n"
         "persona a un píxel: población en una celda de bosque no significa que viva literalmente en el bosque."),
        ("03  Confidencialidad y valores ausentes",
         "La protección estadística de Eurostat puede hacer que edades o sexos no sumen el total.\n"
         "Se conservan los recuentos publicados. Los cocientes fuera de 0–100 se dejan vacíos; los mapas\n"
         "demográficos porcentuales solo muestran celdas de 20 habitantes o más."),
        ("04  Instalaciones para revisión preventiva",
         "Puertos, aeródromos, fábricas, combustibles y residuos se extraen por etiquetas OSM. Áreas\n"
         "industriales, helipuertos y puertos deportivos se distinguen como categorías para revisar.\n"
         "Una instalación puede ocupar varios elementos OSM. La cobertura y las etiquetas no son exhaustivas."),
        ("05  Riesgo de incendio y datos actuales",
         "No se ha calculado una probabilidad de incendio ni se han verificado sustancias o condiciones\n"
         "operativas. Para riesgo forestal y peligro meteorológico, consultar EFFIS (enlaces en FUENTES.md).\n"
         "Las coordenadas de instalaciones son nodos o puntos interiores, no perímetros de seguridad."),
        ("06  Archivos abiertos",
         "CSV comprimido: tablas con longitud y latitud WGS84. Parquet: análisis eficiente.\n"
         "GeoParquet: cuadrados EPSG:3035 para QGIS/Python. GeoJSON: instalaciones en EPSG:4326.\n"
         "README, diccionario de campos, validaciones y scripts acompañan a los mapas PNG y este PDF."),
    ]
    for y, (title, text) in zip([0.80, 0.665, 0.53, 0.395, 0.26, 0.125], blocks):
        fig.text(0.05, y, title, fontsize=14, weight="bold", color="#008c95")
        fig.text(0.05, y - 0.035, text, fontsize=11, linespacing=1.5, va="top")
    return fig


def main() -> None:
    MAPS.mkdir(exist_ok=True)
    grid = pd.read_parquet(OUT / "espana_rejilla_1km.parquet")
    regions = gpd.read_file(OUT / "regiones_espana.geojson").to_crs(3035)
    regions["zona"] = regions.NUTS_ID.map(REGION_ZONES).fillna("Peninsula")
    poi = pd.read_parquet(OUT / "instalaciones_atencion_incendios.parquet")
    points = gpd.GeoDataFrame(poi, geometry=gpd.points_from_xy(poi.lon, poi.lat),
                              crs=4326).to_crs(3035)
    catalog = []
    with PdfPages(ROOT / "Atlas_Espana.pdf") as pdf:
        pdf.infodict()["Title"] = "España: población, suelo y atención preventiva"
        for fig in [cover(grid, poi), notes()]:
            pdf.savefig(fig, dpi=150)
            plt.close(fig)
        for metric in METRICS:
            fig = metric_map(grid, regions, metric)
            target = MAPS / f"{metric.column}.png"
            fig.savefig(target, dpi=180)
            pdf.savefig(fig, dpi=150)
            plt.close(fig)
            catalog.append({"archivo": target.name, "variable": metric.column,
                            "titulo": metric.title, "subtitulo": metric.subtitle})
            print(target.name, flush=True)
        point_maps = [
            ("instalaciones_todas", list(CATEGORIES), "Instalaciones de atención preventiva"),
            ("puertos_aeropuertos", ["aeropuerto_aerodromo", "helipuerto", "puerto", "puerto_deportivo"],
             "Puertos e infraestructuras aeronáuticas"),
            ("fabricas_areas_industriales", ["fabrica", "area_industrial"],
             "Fábricas y áreas industriales"),
            ("combustibles_residuos", ["combustibles_quimica", "gasolinera", "central_combustion",
                                      "vertedero", "gestion_residuos"],
             "Combustibles, química, energía y residuos"),
        ]
        for name, categories, title in point_maps:
            fig = poi_map(grid, regions, points, categories, title)
            fig.savefig(MAPS / f"{name}.png", dpi=180)
            pdf.savefig(fig, dpi=150)
            plt.close(fig)
            catalog.append({"archivo": f"{name}.png", "variable": "categoria", "titulo": title})
        fig = priority_map(grid, regions, points)
        fig.savefig(MAPS / "prioridad_preventiva.png", dpi=180)
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
        catalog.append({"archivo": "prioridad_preventiva.png",
                        "variable": "prioridad_preventiva",
                        "titulo": "Prioridad preventiva ante incendios"})
    (MAPS / "indice_mapas.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
