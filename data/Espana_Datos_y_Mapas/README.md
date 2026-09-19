# España: población, suelo y atención preventiva ante incendios

Paquete elaborado el **19 de septiembre de 2026**, con fuentes gratuitas. Cubre Península, Baleares, Canarias, Ceuta y Melilla, según las rejillas y límites de las fuentes.

## Abrir primero

- **Atlas_Espana.pdf**: 36 páginas; portada, metodología, 29 mapas por variable y 5 mapas de instalaciones.
- **mapas/**: los mismos 34 mapas como imágenes PNG de 2.520 × 1.890 píxeles. `indice_mapas.json` relaciona cada imagen con su variable.
- **output/espana_rejilla_1km.csv.gz**: tabla principal comprimida, con **511.226 celdas** de 1 km², coordenadas y 54 campos. Puede descomprimirse como CSV, abrirse en QGIS o leerse directamente con pandas.
- **output/espana_rejilla_1km.parquet**: la misma tabla, más eficiente para análisis.
- **output/espana_rejilla_1km.geoparquet**: los mismos datos con cuadrados geográficos en EPSG:3035.
- **output/instalaciones_atencion_incendios.geojson**: **44.787 elementos OSM** con puntos WGS84, nombre cuando existe, categoría, criterio preventivo y enlace al elemento original. También se entrega en CSV y Parquet.
- **output/diccionario_campos.csv**: significado, unidad, tipo y valores ausentes de todas las columnas.
- **FUENTES.md**: descargas directas, servicios, fechas y licencias.
- **output/comprobaciones.json** y los demás JSON de validación: controles numéricos y limitaciones observadas.

Las imágenes son mapas de valores por celda, sin suavizado artificial. Las instalaciones son mapas de puntos. No hace falta registrarse ni utilizar una clave API para abrir o descargar estas fuentes.

## Qué contiene la rejilla

Población residente del **censo de 2021**, publicado por INE/Eurostat, con un total de **47.400.134 habitantes**. Incluye total, hombres, mujeres, tres grupos de edad, ocupados, lugar de nacimiento y situación de residencia un año antes del censo.

La cobertura del suelo procede de **Copernicus CGLS-LC100 de 2019**, con píxeles originales de aproximadamente 100 m. Se ha agregado a la rejilla de 1 km, distinguiendo bosque, urbano, cultivos, matorral, herbáceas, suelo desnudo, agua, humedales, nieve/hielo y musgos/líquenes. Esta última clase no aparece en las celdas procesadas; se conserva y se muestra su mapa vacío para no ocultarlo.

`lon` y `lat` son las coordenadas del **centro de la celda**, en WGS84/EPSG:4326; no son la ubicación exacta de sus habitantes. `x_min_3035` e `y_min_3035` permiten reconstruir el cuadrado en metros, con esquina superior opuesta `(x+1000, y+1000)`.

`densidad_celda_hab_km2` es la población dividida entre 1 km². `densidad_tierra_hab_km2` utiliza la superficie terrestre censal y puede aumentar mucho en celdas costeras; si la superficie es cero, queda vacía.

## Cómo interpretar población y bosque/ciudad

Cada fila permite consultar simultáneamente cuántas personas viven en una celda y qué porcentaje de su superficie está clasificado como bosque o urbano. **No se ha repartido la población entre los píxeles de suelo**: vivir en una celda predominantemente forestal no significa vivir dentro del bosque.

`suelo_dominante` es la clase de mayor porcentaje; no necesariamente supera el 50 %. `suelo_mixto=true` identifica las celdas cuyo máximo es menor del 50 %. En empates se toma la primera clase en el orden documentado en `scripts/aggregate.py`; no es una clasificación oficial de ciudades.

`poblacion_por_suelo_dominante.csv` suma personas en celdas con cada clase dominante. Su superficie es la superficie clasificada de esas celdas, **no** la superficie pura de esa clase. `superficie_por_cobertura.csv` sí aproxima esta última, ponderando cada porcentaje por la superficie clasificada.

## Instalaciones y criterio preventivo

Se han procesado íntegramente los extractos OSM de España y Canarias, fechados **2026-09-18T20:21:10Z**, seleccionando nodos y áreas mediante etiquetas públicas. Se mantienen las etiquetas relevantes en `tags_fuente` y el vínculo `url_osm`.

| Categoría | Elementos OSM | Prioridad |
|---|---:|---|
| Áreas industriales | 22.575 | Revisar |
| Gasolineras | 12.038 | Alta orientativa |
| Fábricas | 4.915 | Alta orientativa |
| Centros de residuos | 2.122 | Revisar |
| Combustibles / química | 964 | Alta orientativa |
| Vertederos | 910 | Alta orientativa |
| Puertos | 575 | Alta orientativa |
| Aeropuertos / aeródromos | 358 | Alta orientativa |
| Centrales de combustión | 151 | Alta orientativa |
| Puertos deportivos | 144 | Revisar |
| Helipuertos | 35 | Revisar |

**19.911 elementos** tienen prioridad alta orientativa y **24.876** quedan para revisar. El rojo del mapa de prioridad indica atención preventiva por actividad o consecuencias potenciales; **no** probabilidad alta de incendio acreditada.

- Combustibles y química: etiquetas explícitas de refinería, química, petroquímica, gas, petróleo, almacenamiento o depósitos cuyo contenido declara combustible.
- Gasolineras: `amenity=fuel`.
- Aeropuertos/aeródromos: `aeroway=aerodrome`. Incluye pequeños aeródromos; no equivale al listado de aeropuertos comerciales de AENA. Helipuertos solo con `aeroway=heliport`; no se incluyen todos los helipads.
- Puertos: `landuse=port`, `industrial=port`, `harbour=yes/port` o `seamark:type=harbour`. Puertos deportivos: `leisure=marina`.
- Fábricas: `man_made=works`; no basta con que un edificio sea industrial.
- Áreas industriales: `landuse=industrial`; representan recintos o suelo industrial, no una empresa por punto.
- Centrales: `power=plant` y fuente declarada petróleo, gas, carbón, biomasa o residuos. No se incluyen indiscriminadamente todas las instalaciones solares/eólicas.
- Residuos: vertederos, centros de reciclaje y estaciones de transferencia; se excluyen contenedores de reciclaje ordinarios.

Una etiqueta específica prevalece sobre una genérica: por ejemplo, una refinería se clasifica como combustibles/química antes que fábrica. Se excluyen elementos declarados como abandonados, demolidos o en desuso mediante las etiquetas comprobadas en el script.

### Límites del inventario

**No son todas las instalaciones reales de España ni establecimientos únicos.** OSM es colaborativo y puede omitir, duplicar o conservar instalaciones antiguas. Se eliminan duplicados del mismo tipo/ID OSM entre extractos; no se fusionan nodos, recintos y edificios distintos que podrían corresponder a un mismo complejo. Tampoco se garantiza que toda fábrica esté etiquetada con `man_made=works`.

Los polígonos se convierten a un punto interior; no se entregan perímetros de peligro. Se filtra con los límites españoles y se admiten puertos hasta 1 km fuera de su línea cartográfica generalizada para conservar instalaciones en el agua. Hay **369** de estos puntos costeros, marcados para revisión. Se excluyeron **263** candidatos fuera del ámbito y falló la geometría de **1** candidato.

Las columnas `poblacion_celda_1km`, `pct_bosque_celda_1km` y `pct_urbano_celda_1km` son contexto de la celda que contiene el punto. **No representan personas expuestas, zonas de evacuación ni un radio de afección**, y no se suman entre puntos.

`riesgo_oficial=no_evaluado` en todas las filas. No se han verificado procesos, sustancias, inventarios, medidas de protección, accidentes históricos, vulnerabilidad o meteorología. Para peligro y riesgo forestal oficial se incluyen enlaces a **EFFIS**; sus capas no se han descargado ni fusionado con este inventario.

## Calidad y diferencias entre fuentes

- 111.812 celdas tienen población positiva; 399.414 tienen cero.
- 1.293 celdas no tienen suelo clasificado; contienen 3.585 habitantes. Se conservan con porcentajes vacíos, nunca como 0 % de bosque.
- La superficie terrestre censal suma aproximadamente 501.307,39 km²; la superficie clasificada del cruce suma 505.683,49 km². Las máscaras, fechas, resoluciones y definiciones difieren. No se fuerza su igualdad.
- Los porcentajes de suelo se normalizan por píxeles clasificados dentro de España, excluyendo mar y nodata. Suman 100 % salvo redondeo máximo observado de 0,002 puntos.
- La reproyección a 100 m usa vecino más próximo; la agregación es una aproximación raster, no una intersección exacta de cada píxel original con polígonos.
- En 81.705 celdas, hombres + mujeres difiere del total; en 79.206, los grupos de edad difieren del total. Eurostat documenta estos efectos del control de confidencialidad. No se corrigen ni se inventan recuentos.
- Los códigos negativos de ausencia de dato se convierten en nulos. Los cocientes demográficos imposibles, fuera de 0–100 %, quedan vacíos. Los mapas porcentuales ocultan además celdas con menos de 20 habitantes; las tablas conservan sus cocientes válidos.
- Los mapas de recuentos usan escala logarítmica; los de porcentajes, 0–100 lineal. Las leyendas y las fechas aparecen en cada imagen.
- Los límites NUTS son cartográficos, escala nominal 1:1.000.000. No son cartografía catastral. Las islas menores y las celdas limítrofes pueden verse afectadas por generalización.
- El campo `zona` es una agrupación territorial para los mapas; `nuts2` de las instalaciones se asigna por proximidad geométrica, no por un registro administrativo oficial.
- Población 2021, suelo 2019 e instalaciones 2026 no constituyen una observación simultánea ni datos en tiempo real.

## Uso rápido en Python

Ejecutar desde la carpeta descomprimida:

```python
import pandas as pd
from pyproj import Transformer

grid = pd.read_parquet("output/espana_rejilla_1km.parquet")
poi = pd.read_parquet("output/instalaciones_atencion_incendios.parquet")

# Áreas de mayoría forestal con población:
forestales = grid[(grid.pct_suelo_bosque >= 50) & (grid.poblacion > 0)]
print(forestales[["grid_id", "lon", "lat", "poblacion", "pct_suelo_bosque"]].head())

# Consulta de una coordenada: celda del centro de Madrid.
x, y = Transformer.from_crs(4326, 3035, always_xy=True).transform(-3.7038, 40.4168)
celda = grid[(grid.x_min_3035 == (x // 1000) * 1000) &
             (grid.y_min_3035 == (y // 1000) * 1000)]
print(celda[["poblacion", "densidad_celda_hab_km2", "pct_suelo_urbano"]])

# Puertos y aeródromos para revisión:
infraestructura = poi[poi.categoria.isin(["puerto", "aeropuerto_aerodromo"])]
print(infraestructura[["nombre", "lon", "lat", "criterio", "url_osm"]].head())
```

En QGIS: añadir el GeoJSON de instalaciones; para la rejilla, abrir GeoParquet en una versión con soporte Parquet/GDAL, o importar el CSV descomprimido con `lon`/`lat` y EPSG:4326. El CSV representa centros; GeoParquet conserva cuadrados completos.

## Reproducir

Python 3.10.12 y las versiones de `requirements.txt` son las usadas en esta entrega. Desde la carpeta descomprimida:

```bash
python -m pip install -r requirements.txt
python scripts/download_sources.py
python scripts/download_landcover.py
python scripts/prepare.py
python scripts/aggregate.py
python scripts/poi.py
python scripts/maps.py
python scripts/validate_package.py
python -m ruff check scripts
python -m mypy --ignore-missing-imports scripts
```

La descarga completa necesita aproximadamente 2–3 GB de fuentes y varios GB de espacio/memoria durante el proceso. La entrega excluye los PBF y los grandes ZIP originales para reducir su tamaño. Incluye los recortes de suelo, metadatos originales y huellas SHA-256. Los enlaces `latest` de Geofabrik cambian diariamente: una ejecución futura producirá otro inventario. Para repetir exactamente esta fecha, conservar los PBF originales o conseguir una instantánea cuyo hash coincida con `output/huellas_fuentes.json`.

No hay SQL porque el procesamiento utiliza archivos públicos mediante pandas, GeoPandas, Rasterio y Osmium. Los scripts entregados contienen las consultas, filtros y transformaciones completos.

## Licencias

Cada fuente mantiene sus condiciones; **no se aplica una licencia única a todo el ZIP**. La base derivada de OSM se entrega bajo ODbL 1.0, Copernicus bajo CC BY 4.0 y el censo bajo la política de reutilización de Eurostat. Los límites GISCO tienen condiciones específicas que pueden restringir el uso comercial. Antes de incorporarlos a un producto comercial, comprobar dichas condiciones o sustituir los límites por una fuente autorizada para ese uso. Véase **FUENTES.md**.
