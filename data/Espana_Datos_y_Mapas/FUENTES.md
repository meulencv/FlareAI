# Fuentes gratuitas, descargas y licencias

Consulta y procesamiento: 19 de septiembre de 2026.

## 1. Población: INE / Eurostat, Census Grid 2021 V3

- Catálogo oficial: https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution/population-grids
- Descarga utilizada: https://gisco-services.ec.europa.eu/census/2021/Eurostat_Census-GRID_2021_V3.zip
- Dentro: `ESTAT_Census_2021_country.csv.zip`, miembro `CENSUS_GRID_N_ES_2021.csv`.
- Año de referencia: **2021**; no confundirlo con la fecha de publicación o descarga.
- El `read.me` de V3 indica datos recibidos el 22/01/2025; el catálogo consultado presenta la distribución más reciente de V3 con fecha 30/05/2026. Se conserva ese `read.me` en `raw/`.
- Rejilla: **1 km²**, ETRS89-LAEA, EPSG:3035.
- 13 variables publicadas, según Reglamento (UE) 2018/1799: https://eur-lex.europa.eu/eli/reg_impl/2018/1799/oj
- Alternativa gratuita identificada, no usada para la tabla final: https://gisco-services.ec.europa.eu/census/2021/INSPIRE/Data/ES_PD_3035_CSV.zip
- Reutilización: https://ec.europa.eu/eurostat/web/main/about-us/policies/copyright
- Atribución: **Fuente: INE / Eurostat, Census Grid 2021. © European Union. Tratamiento, cruce y visualización propios; los resultados no son una publicación oficial de Eurostat.**

Códigos -8888 y -9999: confidencialidad y otras causas de ausencia. La documentación advierte que los grupos de población pueden no sumar el total por protección estadística.

## 2. Suelo: Copernicus Global Land Service CGLS-LC100

- Registro y archivos: https://zenodo.org/records/3939050
- DOI: https://doi.org/10.5281/zenodo.3939050
- Título: *Copernicus Global Land Service: Land Cover 100m: collection 3: epoch 2019: Globe*.
- Año: **2019**, versión 3.0.1, clasificación discreta; resolución original aproximada de 100 m en EPSG:4326.
- GeoTIFF: https://zenodo.org/records/3939050/files/PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif
- Metadatos programáticos: https://zenodo.org/api/records/3939050
- Licencia: **CC BY 4.0**, https://creativecommons.org/licenses/by/4.0/
- Atribución: **Buchhorn, M., Smets, B., Bertels, L., De Roo, B., Lesiv, M., Tsendbazar, N.-E., Herold, M. y Fritz, S. Copernicus Global Land Service, Land Cover 100m, Collection 3, epoch 2019. DOI: 10.5281/zenodo.3939050. Recorte, reproyección y agregación propios.**

Se agrupan los códigos:

| Grupo | Códigos |
|---|---|
| Bosque | 111–116 y 121–126, bosque cerrado y abierto |
| Urbano / construido | 50 |
| Cultivos | 40 |
| Matorral | 20 |
| Herbáceas | 30 |
| Desnudo / vegetación escasa | 60 |
| Agua permanente | 80 |
| Humedales herbáceos | 90 |
| Nieve / hielo | 70 |
| Musgos / líquenes | 100 |

Mar (200) y nodata no entran en el denominador. La clase bosque no equivale necesariamente a una definición jurídica española de monte o terreno forestal.

## 3. Límites: GISCO NUTS 2024, nivel 2

- Catálogo: https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics
- API de distribución: https://gisco-services.ec.europa.eu/distribution/v2/nuts/nuts-2024-files.html
- GeoJSON utilizado: https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2024_4326_LEVL_2.geojson
- Filtro: `CNTR_CODE == "ES"`. Resolución cartográfica **1:1.000.000**, año NUTS 2024.
- Atribución: **© EuroGeographics for the administrative boundaries. Fuente: Eurostat/GISCO.**
- Condiciones específicas enlazadas por la API: https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units
- Información general: https://ec.europa.eu/eurostat/web/gisco/overview

La gratuidad de descarga no implica reutilización comercial irrestricta. GISCO señala condiciones específicas para estos datos; comprobar los derechos con GISCO/EuroGeographics antes de un uso comercial. No extender automáticamente la política abierta de los valores censales a los polígonos administrativos.

## 4. Instalaciones: OpenStreetMap / Geofabrik

- España: https://download.geofabrik.de/europe/spain.html
- PBF España: https://download.geofabrik.de/europe/spain-latest.osm.pbf
- Canarias: https://download.geofabrik.de/africa/canary-islands.html
- PBF Canarias: https://download.geofabrik.de/africa/canary-islands-latest.osm.pbf
- Fecha interna de **ambos PBF efectivamente procesados**: **2026-09-18T20:21:10Z**. Se obtiene de la cabecera, no de una página web almacenada en caché.
- Atribución: **© OpenStreetMap contributors. Datos distribuidos por Geofabrik.**
- Copyright y atribución: https://www.openstreetmap.org/copyright
- Licencia de la base de datos y del inventario derivado entregado: **Open Database License (ODbL) 1.0**, https://opendatacommons.org/licenses/odbl/1-0/

Se entrega el inventario derivado para que pueda reutilizarse conforme a ODbL. Mantener atribución y las obligaciones aplicables a bases derivadas. Las estadísticas de población/suelo conservan además sus propias condiciones de origen.

## 5. EFFIS: referencia oficial complementaria para incendios

Estas fuentes se incluyen como **enlaces de consulta**, no como capas descargadas ni como fundamento numérico del mapa de prioridad de instalaciones.

- Datos y servicios: https://forest-fire.emergency.copernicus.eu/applications/data-and-services
- Instrucciones oficiales de acceso: https://forest-fire.emergency.copernicus.eu/downloads-instructions
- WMS: https://maps.effis.emergency.copernicus.eu/effis
- Consulta de capacidades: https://maps.effis.emergency.copernicus.eu/effis?SERVICE=WMS&REQUEST=GetCapabilities&VERSION=1.3.0
- Visor de riesgo forestal: https://forest-fire.emergency.copernicus.eu/apps/fire.risk.viewer/
- Metodología: https://forest-fire.emergency.copernicus.eu/about-effis/technical-background/wildfire-risk-assessment
- Licencia: https://forest-fire.emergency.copernicus.eu/about-effis/data-license

El servicio oficial documenta descarga WMS de, por ejemplo, `ecmwf007.fwi` (Fire Weather Index), usando parámetros `LAYERS`, `BBOX`, `SRS`, `WIDTH`, `HEIGHT`, `FORMAT` y **TIME**. Para un día concreto, verificar primero fechas y capas disponibles en GetCapabilities; la documentación incluye un ejemplo histórico. Un índice meteorológico de peligro, un modelo de riesgo forestal y la prioridad de una instalación son magnitudes diferentes.

## Actualización y trazabilidad

`output/huellas_fuentes.json` registra tamaños y SHA-256 de las fuentes locales. `output/validacion_instalaciones.json` registra fecha de los extractos OSM. Los scripts conservan URLs, filtros y parámetros. No se ha utilizado una API de pago ni una base de datos privada.
