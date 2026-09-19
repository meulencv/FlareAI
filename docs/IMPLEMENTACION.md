# Implementación de FlareAI

## 1. Flujo de datos

```text
CSV globales VIIRS → filtro de España y 24 h → agrupación a 3 km
                                               ↓
GFS .idx → cuatro peticiones Range → GRIB2 → interpolación en cada grupo
                                               ↓
                                      /api/data → interfaz
                                               ↓
selección de una zona → GIBS WMS → caché PNG → panel satelital
```

La cartografía y Leaflet se sirven localmente. No hay claves, fuentes tipográficas remotas ni una cuenta de teselas de pago.

## 2. Contrato HTTP

### `GET /api/data`

Devuelve:

- `generated_at`: momento de generación de la respuesta.
- `status`: `ready`, `stale` u `offline`.
- `errors`: fallos de adquisición por fuente.
- `fires_checked_at`: corte temporal usado para analizar FIRMS.
- `window_hours`: 24.
- `incidents`: grupos con detecciones, geometría aproximada y meteorología.
- `wind`: malla regional GFS, metadatos de ciclo/validez y componentes.

Añadir `?download=1` solicita un archivo adjunto JSON.

### `GET /api/incidents.csv`

Una fila por grupo: coordenadas, observaciones, fechas, estado contrastado, FRP máximo, brillo I4, huella aproximada, temperatura ambiente, viento y rachas. `burned_area_ha` queda vacío porque no disponemos de perímetros quemados confirmados. Las detecciones individuales y las geometrías se conservan en JSON.

### `GET /api/context?id=<id>`

Contexto de la zona seleccionada, calculado por `context.Atlas`. Lee una vez los CSV del atlas
local (511.226 celdas, 44.787 elementos OSM) en memoria; no requiere base de datos, GeoPandas,
Rasterio, Osmium ni conexión externa. La carga se sincroniza entre peticiones y no bloquea
`/api/data`. Un atlas ausente devuelve 503 sin impedir consultar los focos.

La respuesta contiene `population`, `facilities`, `landcover`, `wind`, `points`, `coverage`,
`level`, `method` y `sources`. Se seleccionan centros de celdas y puntos OSM a ≤5 km de cualquier
componente de la huella térmica. Se usa una proyección local aproximada en kilómetros,
`x = Δlon × 111,32 × cos(lat)` e `y = Δlat × 111,32`, y distancia mínima a la geometría con
Shapely. No es un buffer geodésico exacto ni una medición desde perímetros de instalaciones.

Población: suma por celda, nunca por instalación; no se distribuyen habitantes en píxeles.
Suelo: media ponderada por `superficie_clasificada_km2`; nulos conservados, no convertidos a cero.
`coverage=no_grid_cells` no equivale a territorio vacío. Los conteos OSM son elementos, no
establecimientos únicos. Las coordenadas censales son representativas, no poblaciones con nombre.

Dirección: `(wind_from_degrees + 180) % 360`, comparada con el rumbo desde el punto más cercano
de la huella hasta cada centro/punto. Sector ±30°, viento ≥3 km/h; puntos dentro de la huella
no reciben una dirección arbitraria. Solo se emite `level=attention` con viento válido actual y
población o instalaciones de prioridad alta orientativa en ese sector. Validez meteorológica
±2 h, ciclo ≤12 h, sin error de fuente; offline usa `historical`, nunca alerta actual.
No es un modelo de propagación ni de humo y no interviene en el escenario ilustrativo.

La interfaz no presenta tablas ni puntos de contexto: al pulsar un foco se encuadra automáticamente
su huella +5 km y `static/heat.js` pinta un **mapa de calor continuo** con las muestras de
`potential.samples`. Solo una leyenda discreta; no hay botón de activación. Las actualizaciones
periódicas no reencuadran el mapa. El calor se retira al cerrar o filtrar la selección y ante
fallos; las respuestas tardías no sustituyen la selección actual.

El renderizado sigue la técnica habitual de mapas de calor: por cada muestra se acumula un
degradado radial en escala de opacidad (`sampleAlpha`, tope 0,55 y gamma 0,75) con radio de unos
1,6 km de terreno acotado a 18–190 px, y después se traduce la densidad acumulada a color con una
paleta de 256 pasos (`heatPalette`, crema → ámbar → coral). El canvas se dibuja al 60 % de la
resolución con desenfoque CSS, se compone en `multiply` bajo el fuego y se repinta una vez por
fotograma mediante `requestAnimationFrame`, sin peticiones de red al mover o hacer zoom.

El puntero informa del contenido: `nearestSample` busca la muestra más próxima en coordenadas de
contenedor, dentro de un radio ligado al del calor, y `hoverSummary` describe lo que hay
(instalaciones por nombre, residentes censados, porcentaje de vegetación, dirección del viento
cuando es actual y distancia a la huella). El rótulo no aparece sin datos, al arrastrar, al iniciar
zoom o al salir del mapa. Es una lectura del atlas estático, no una medición en tiempo real.

Contrato v2: `schema_version`, `evaluated_at` y `potential` para consumo por agentes. `potential`
contiene `model` versionado (`attention-potential-v1`), todas las `samples` e instalaciones cercanas,
`zones` GeoJSON y limitaciones. Cada muestra tiene evidencia original, contribuciones, factor de
proximidad, datos ausentes, puntuación y banda. Los 12 `points` originales se conservan solo por
compatibilidad; no se usan para calcular ni dibujar el potencial.

`POTENTIAL_MODEL` centraliza los parámetros, de carácter exploratorio y **no calibrados**:

- Población: hasta 35 puntos, `min(1, log1p(población)/log1p(1000))`.
- Vegetación: hasta 25 puntos por porcentaje de bosque + matorral + herbáceas. No mide humedad,
  combustible disponible ni continuidad forestal. Sin cobertura se conserva el dato ausente.
- Instalaciones en la celda: máximo de 40 (alta orientativa) o 20 (revisar), no suma de elementos
  OSM, para no inflar por duplicados de un mismo complejo. Se conservan todos sus IDs y fuentes.
  Instalaciones sin celda consultada generan una muestra independiente con población/suelo ausentes.
- Viento: +15 solo con evidencia positiva, alineación y viento **actual** válido. Offline no aumenta
  el índice, aunque el contexto general conserve la dirección histórica.
- Proximidad: multiplica por `1 - 0,6 × distancia/5`. Puntuación limitada a 100, nunca un porcentaje
  de probabilidad. Bandas visuales desde 12, 35 y 60; cobertura desconocida sin evidencia = `null`.
- Zonas: unión de soportes circulares de 0,7 km por banda, recortada al radio consultado. Se resta
  el área de bandas superiores para evitar contar intensidad dos veces. Son **soportes visuales**,
  no polígonos de afectación, ni límites de evacuación. `sample_ids` enlaza geometría con evidencia.

La política futura de una IA puede consultar estos factores, pero debe verificar condiciones y
fuentes antes de tomar decisiones. Este modelo no produce órdenes de intervención.

Población 2021, suelo 2019 y OSM 18/09/2026 no son datos simultáneos. `/atlas/sources` sirve
el documento original de atribución/licencias. Los campos de sexo, origen y movilidad permanecen
en el atlas, pero no se utilizan para clasificar riesgo.

### `GET /api/satellite?id=<id>&mode=natural`

`mode` admite `natural` o `swir`. Devuelve URL local, fecha del mosaico, bounding box `[oeste,sur,este,norte]`, capa, URL original y hora de comprobación. No acepta URLs arbitrarias.

`GET /satellite/<hash>.png` sirve los bytes de la imagen. Las coordenadas de la superposición roja se convierten linealmente dentro del bounding box EPSG:4326 del WMS.

Las entradas inválidas devuelven HTTP 400. Los fallos de proveedor/sistema devuelven 503. Una ruta desconocida devuelve 404. `errors` y las fechas permiten distinguir un archivo almacenado de una actualización.

## 3. FIRMS: detección térmica

Fuentes probadas mediante GET sin autenticación:

```text
https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv
https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-21-viirs-c2/csv/J2_VIIRS_C2_Global_24h.csv
https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv
```

La API de consulta por área de FIRMS requiere `MAP_KEY`; estos CSV públicos no la necesitaron en las pruebas.

Se validan columnas, números y hora UTC; se filtra mediante la geometría de España y una ventana de 24 h; se eliminan duplicados dentro de una fuente. Se mantienen observaciones de distintas pasadas/satélites porque no son medidas idénticas.

Cada observación conserva satélite, fuente, FRP en MW, brillo I4/I5 en K, confianza, día/noche, tamaño scan/track, versión y hora de adquisición. VIIRS tiene resolución nominal de aproximadamente 375 m; la huella efectiva varía.

### Agrupación

Se conectan pares situados a 3 km o menos y se obtienen sus componentes conexas. El centro es la media de las coordenadas. La agrupación es transitiva: sus extremos pueden estar separados por más de 3 km. No hay un identificador oficial de incendio ni garantías de separación entre incendios próximos.

El ID deriva de las observaciones y puede cambiar cuando entra o sale una pasada. Las etiquetas de la mayoría de zonas son provincias, no topónimos confirmados del foco.

Igea se distingue por coincidencia espacial a menos de 2 km de `42.075,-2.024` y temporal con el 18/09/2026, contrastada con:

https://actualidadriojabaja.com/el-incendio-de-igea-afecta-ya-a-unas-25-hectareas-de-matorral-y-arbolado/

Esta noticia no confirma actividad actual, ni proporciona aquí un perímetro geográfico oficial.

### Huella

Cada píxel se aproxima por un rectángulo local alineado con este/norte, con dimensiones `scan_km × track_km`. Se unen los rectángulos y se calcula su área en hectáreas.

Es una aproximación: no se conoce la orientación exacta de cada píxel, se combinan pasadas distintas y hay errores de geolocalización. El resultado **no es un límite de fuego ni terreno quemado**. `burned_area_ha` se mantiene a `null`.

La capa de fuego dibuja cada componente de la geometría aproximada sin escalarla por zoom: la silueta queda anclada al terreno y solo cambia con la proyección, de modo que acercarse o alejarse no la deforma. La ondulación se indexa por posición relativa en el contorno, no por número de vértices, para que el remuestreo al cambiar de escala no altere el patrón; su amplitud es proporcional a la extensión dibujada. Las huellas pequeñas se localizan por el halo, cuyo radio mínimo es de unos 9 píxeles y no usa una escala de hectáreas.

### Motor visual de fuego y viento

`static/flames.js` usa Canvas 2D y `requestAnimationFrame`. No necesita WebGL, imágenes de fuego, servicios de teselas ni descargas durante el zoom. `static/flow.js` contiene las operaciones geométricas puras.

- **Superficie:** se proyectan los polígonos de `incident.footprint`, manteniendo componentes separadas y huecos. Se subdividen los bordes (máximo 180 puntos), se suavizan y se modulan con ondas deterministas. Gradientes rojos, naranjas y amarillos forman el cuerpo, núcleos y halo; pequeñas lenguas se inclinan según la dirección de desplazamiento del viento.
- **Chispas:** nacen dentro de la huella geográfica, mediante muestreo con rechazo. Su posición se conserva en latitud/longitud y se actualiza con U/V de GFS interpolados en esa posición. Con calma o ausencia de viento no se inventa desplazamiento. Caducan a los 3,4 segundos. Hay un máximo global de 420 y el detalle aumenta con el zoom y la selección.
- **Corrientes:** hasta 240 trazos según el tamaño de la vista. Se siembran sobre España usando un índice espacial de sus anillos. Sus cabezas se mueven en coordenadas geográficas. Las colas se reconstruyen con la dirección local y una longitud visual acotada; no se conserva una estela en coordenadas antiguas de pantalla. Al cambiar de vista se rellenan las posiciones visibles sin esperar a `moveend` ni hacer peticiones de red.
- **Mapa:** la proyección se recalcula en cada fotograma y en eventos `move`, `zoom`, `resize` y `viewreset`. El canvas compensa la traslación del pane de Leaflet. No se estira una imagen de flechas durante el zoom. Rueda y botones interpolan el zoom durante 220 ms, con centro en el cursor para la rueda. El arrastre o la navegación a otra zona cancelan una transición pendiente.
- **Recursos y accesibilidad:** DPR limitado a 2; delta temporal máximo de 50 ms tras pausas; el bucle se detiene con la pestaña oculta. El botón **Ⅱ** y `prefers-reduced-motion` dejan un fotograma estático, con flechas visibles. Mover el mapa sigue actualizando su posición aunque estén pausadas las animaciones. Las zonas también se seleccionan con los botones de la lista.

La velocidad se normaliza en píxeles por segundo para hacer legible incluso un viento flojo. Los colores de fuego son una paleta visual: **no codifican temperatura medida ni intensidad de combustión**. Ni el desplazamiento de las chispas ni la ondulación modifican la geometría observada, las hectáreas del panel o los datos exportados. La malla GFS de 0,25° no adquiere resolución adicional al ampliar el mapa.

## 4. GFS: viento y temperatura

Catálogo: https://registry.opendata.aws/noaa-gfs-bdp-pds/

Repositorio público:

```text
https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.AAAAMMDD/HH/atmos/gfs.tHHz.pgrb2.0p25.fFFF
```

Se descarga primero el índice `.idx`. Se buscan cuatro campos:

| Campo | Nivel | Unidad | Identificador ecCodes |
|---|---|---|---|
| UGRD | 10 m above ground | m/s | 10u |
| VGRD | 10 m above ground | m/s | 10v |
| GUST | surface | m/s | gust |
| TMP | 2 m above ground | K | 2t |

Los offsets del índice permiten peticiones HTTP Range. Se exige HTTP 206, `Content-Range` correcto, longitud exacta y firma GRIB válida. ecCodes verifica malla, dimensiones, ciclo, validez, nivel mediante `shortName`, unidades, orientación y ausencia de datos faltantes. Se guarda hash de índice y evidencia de cada descarga.

Se recortan dos regiones regulares de 0,25°: península/Baleares/Ceuta/Melilla y Canarias. La interpolación bilineal se hace sobre U/V, no sobre el ángulo.

Fórmulas:

```text
velocidad_kmh = sqrt(u² + v²) × 3,6
dirección_de_procedencia = (atan2(-u,-v) × 180/π) mod 360
dirección_de_desplazamiento = (procedencia + 180) mod 360
temperatura_ambiente_C = TMP_K − 273,15
```

La flecha apunta **hacia donde va el aire**. Con velocidad menor de 0,2 m/s se omite la dirección. Las rachas se interpolan como escalar.

La malla no resuelve calles, cortafuegos ni vientos locales de ladera. Tiene un espaciado aproximado de 20–28 km en España. La meteorología mostrada corresponde a la validez horaria del modelo, que puede ser distinta de la hora de la detección satelital.

El proceso comprueba novedades cada 600 s; los ciclos reales son 00, 06, 12 y 18 UTC. La caché evita descargar campos repetidos del mismo índice.

## 5. Temperatura satelital

`brightness_i4_k` es el máximo brillo I4 entre las observaciones agrupadas. Se conserva la hora de la observación que lo aporta.

```text
brightness_i4_c = brightness_i4_k − 273,15
```

Se muestra en °C equivalentes para facilitar lectura, además del valor en K. Es temperatura de brillo de un píxel que mezcla superficies, no un termómetro de llama ni temperatura ambiente. El canal puede saturarse. La imagen SWIR tampoco proporciona una temperatura cuantitativa por sí sola.

## 6. GIBS: fotografía real

Documentación: https://nasa-gibs.github.io/gibs-api-docs/

Endpoint:

```text
https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi
```

WMS 1.1.1, `SRS=EPSG:4326`, `FORMAT=image/png`, `TRANSPARENT=TRUE`, 900×600 píxeles. Capas:

- `VIIRS_NOAA20_CorrectedReflectance_TrueColor`
- `VIIRS_NOAA20_CorrectedReflectance_BandsM11-I2-I1`

El recorte abarca ±0,24° en longitud y ±0,16° en latitud desde el centro de la zona. Se prueban hoy y hasta tres fechas anteriores. Se exige al menos 50 % de cobertura con alfa ≥64 y algún canal RGB >8. Así se rechazan tanto PNG transparentes como PNG negros opacos que el proveedor puede devolver antes de disponer de datos. No es un detector de nubes.

La fecha es la del mosaico diario solicitado, no una hora exacta de captura para cada píxel. La resolución de exportación de 900×600 no aumenta la resolución nativa VIIRS. Los puntos superpuestos pertenecen al periodo de detecciones; su fecha puede diferir de la imagen.

Caché: zona/capa/hora. Las imágenes se sirven localmente. Cada descarga conserva URL, tamaño, hash SHA-256, fracción de cobertura y hora de recepción.

## 7. Escenario ilustrativo

Se usa una elipse orientada según el viento. La velocidad de avance, `s`, la elige el usuario: 0,1, 0,3, 0,6 o 1 km/h. Para `t` horas:

```text
r = sqrt(huella_ha / 100 / π)
d = s × t
semieje_along = r + d/2
semieje_across = r + 0,14 × d
centro = centro_observado + d/2 en dirección del viento
```

Es una representación geométrica de un supuesto. No adapta la velocidad a temperatura, humedad o viento, ni incorpora relieve, combustible, focos secundarios, humedad del combustible o extinción. No se calcula ni se exporta una cifra de hectáreas quemadas a partir de esta forma.

El contorno naranja discontinuo pertenece al escenario. Las geometrías rojas son huellas de detección. Deslizar o reproducir el control no modifica los datos observados.

## 8. Estados y reloj

- `ready`: no hay errores registrados; edad de validez meteorológica ≤2 h, análisis FIRMS ≤2 h y ciclo GFS ≤12 h.
- `stale`: falla una fuente o se superan esos umbrales. Se conservan fechas y últimos datos.
- `offline`: muestra guardada y ningún acceso de adquisición externo.

`ready` no significa que los incendios sigan activos ni que todos los datos sean observaciones del minuto presente.

Las observaciones envejecidas se retiran en las reconstrucciones periódicas; en lectura se ocultan grupos cuya última observación ya supera las 24 h. El conteo de pasadas individuales puede conservar las del último corte hasta la siguiente reconstrucción. La interfaz muestra ese corte.

## 9. Fuentes, atribución y mantenimiento

- NASA FIRMS/VIIRS: https://www.earthdata.nasa.gov/data/tools/firms
- GIBS: https://nasa-gibs.github.io/gibs-api-docs/
- NOAA GFS/AWS: https://registry.opendata.aws/noaa-gfs-bdp-pds/
- Límites de España: metadata conservada en `data/esp_boundary_metadata.json`.
- Provincias: geoBoundaries gbOpen ESP ADM2, fuente INE, año representado 2018, 52 unidades. `boundaryID=ESP-ADM2-93216281`.
- Geometría provincial utilizada: https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ESP/ADM2/geoBoundaries-ESP-ADM2_simplified.geojson
- Países vecinos: Natural Earth, dominio público: https://www.naturalearthdata.com/about/terms-of-use/
- Leaflet 1.9.4: licencia BSD de 2 cláusulas conservada en `static/vendor/LEAFLET-LICENSE.txt`.

Conservar créditos de NASA/NOAA y atribución/licencia de las geometrías al redistribuir. Revisar las condiciones vigentes de cada proveedor para una implantación comercial; el acceso sin clave no implica un SLA ni una capacidad ilimitada.

Para una integración operativa de incendios harían falta perímetros contrastados y un modelo de propagación validado. Esta versión entrega el observatorio visual y las observaciones disponibles sin inventar esas capas.
