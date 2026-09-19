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

Leaflet y la cartografía administrativa se sirven localmente. La red viaria usa el WMS público
SCNE/IGN, con caché local. No hay claves, fuentes tipográficas remotas ni cuenta de teselas de pago.
PostgreSQL es la fuente de datos del servidor; los archivos originales se conservan para importar
y reproducir pruebas.

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

Contexto calculado por `context.Atlas` sobre las filas seleccionadas en PostgreSQL por
`Database.nearby_atlas()`. El índice `(lon, lat)` prefiltra la caja de la huella más 5 km antes
del cálculo preciso con Shapely. No se cargan las 511.226 celdas ni las 44.787 instalaciones en
cada consulta. El CSV completo se conserva para importar y comparar resultados en pruebas.
No requiere GeoPandas, Rasterio, Osmium ni una consulta geográfica externa.

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

Al pulsar un foco se encuadra automáticamente su huella +5 km y `static/heat.js` pinta un
**mapa de calor continuo** con `potential.samples`. `static/infrastructure.js` añade iconos por
actividad y fichas al pulsar las instalaciones de `potential.facilities`. No hay botón de
activación. Las actualizaciones no reencuadran el mapa. Calor e instalaciones se retiran al
cerrar o filtrar la selección; respuestas tardías no sustituyen la selección vigente.
Las agrupaciones se separan al acercarse y los elementos coincidentes tienen una lista de elección.

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

### Capas territoriales y cámaras

- `GET /api/webcams`: subconjunto integrable con verificación vigente, más fuentes/licencias.
  SQL conserva los 2.926 registros originales: DGT 1.948, Madrid 357, Euskadi 295, Hispacams 164,
  SCT 130, MeteoGalicia 31 y CanariasWebcams 1. No es inventario exhaustivo ni se sincroniza su
  catálogo automáticamente. `Database.catalog()` permite consultar todos los registros internos;
  `catalog(verified=True)` filtra estados, método, caducidad y plantillas conocidas. La interfaz
  refresca este subconjunto cada minuto y solo dibuja iconos desde zoom 10.
- `GET /api/webcam?id=<id>`: consulta de captura o resolución de iframe público por ID almacenado.
  Descarga al abrir el visor o al auditar disponibilidad; TTL por proveedor y ocho descargas concurrentes.
  URLs, puertos, hosts y rutas permitidas se validan de nuevo en cada redirección. Hasta 5 MB
  por imagen, validación con Pillow, timeout y límites de tamaño. No admite URL arbitraria.
- `/territorial/<hash>.img`: imagen con referencia en `flare_assets`, tipo MIME validado y ruta
  restringida. El JSON informa de recuperación, Last-Modified y copia offline; ninguno garantiza
  la hora exacta de captura. Al cerrar el popup se cancelan las renovaciones y se retira el medio.
- Los vídeos requieren prueba real de reproducción (`verify_camera_players.py`), además de HTTP,
  markup y política de iframe válidos. El verificador carga un iframe con la misma política/origen
  local de la app, intenta Play y exige ancho de vídeo, readyState y tiempo avanzando. Un HTML con
  `<video>` puede bloquear otros dominios o no emitir: no basta para activar su icono. No se falsea
  Referer ni se extraen manifiestos, tokens o miniaturas estáticas como si fueran capturas actuales.
  Si la página publica una captura en su elemento principal `img#player`, se intenta usarla;
  se ignoran las fotos de cámaras relacionadas y anuncios. Sin medio integrable, el registro se
  conserva en SQL pero desaparece del mapa. `/webcams/sources` mantiene las atribuciones.
- `/roads/<z>/<x>/<y>.png`: proxy acotado a España, zoom 4–16, WMS 1.1.1 EPSG:3857 de
  `https://servicios.idee.es/wms-inspire/transportes`, capa `TN.RoadTransportNetwork.RoadLink`.
  Teselas transparentes 256×256, caché de 30 días y metadatos en SQL. Se consultan solo las
  zonas visibles, sin descarga masiva. Es cartografía de referencia, no un grafo de rutas,
  inventario de cortes o garantía de accesibilidad. Licencia CC BY 4.0, atribución SCNE/IGN.
- Offline: no se contacta con los proveedores; solo se sirven imágenes/teselas ya guardadas.
  Los fallos se muestran, no se interpretan como ausencia de infraestructura.

La migración 2 añade `flare_camera_checks`: ID/FK de cámara, estado, checked_at, valid_until,
medio y evidencia JSON. Éxitos de captura valen seis horas; fallos temporales, una hora;
enlaces/restricciones externas, un día. La validez de un vídeo nunca se amplía más allá de su
última prueba de navegador. Las plantillas conocidas de DGT, SCT/Barcelona y Madrid se rechazan
por SHA-256 tras revisión visual; una respuesta JPEG 200 no basta. Ausencia de plantilla conocida
no garantiza que una cámara no esté congelada: se muestran las fechas disponibles.

`territorial.py verify-cameras` permite una auditoría completa o por fuente. El servidor reevalúa
hasta 200 medios y 20 vídeos cada diez minutos, priorizando comprobaciones antiguas, con cuatro
workers y dos por fuente. Advisory locks separan los trabajos de capturas y navegador, evitando
duplicar el mismo barrido entre procesos. `--offline` desactiva estos trabajos y la red.
`verify_camera_players.py --retry-failed` reintenta reproducción; Playwright/Chromium son locales.

Para evitar parpadeos, `StableRoadLayer` conserva teselas entre resets de la animación de zoom:
el bucle usa `map.setView()` por fotograma y Leaflet 1.9.4 emite `viewprereset`, cuya acción por
defecto (`_invalidateAll`) destruía todas las imágenes. Solo esta capa elimina ese handler;
mantiene `viewreset`, `zoom`, `moveend`, transformaciones y retención de padres/hijos. Una prueba
real conservó 12/12 nodos de teselas en zoom fraccional y siempre hubo teselas cargadas durante
el paso al siguiente nivel. No se descargan teselas fuera del viewport para disimular el problema.

### PostgreSQL local y compatibilidad con Twin

`schema.sql` es la migración inicial, registrada en `flare_migrations`. Tablas con prefijo
`flare_`: fuentes, importaciones, rejilla, instalaciones, cámaras, instantáneas, focos,
observaciones, confirmaciones, archivos/medios y configuración. PK/FK e índices para ubicación,
clasificación y tiempo. Los datos originales adicionales del atlas permanecen en `jsonb`;
población y coordenadas se conservan también en columnas numéricas consultables.

`database.py` usa psycopg con parámetros, transacciones y timeout SQL. Las importaciones se
serializan con advisory locks y se publican completas o se revierten; `COPY` carga la rejilla
sin insertar 511.226 filas una a una. Repetir la importación no duplica los datos. No se borra
el material original. Una actualización de atlas necesitará una nueva migración/versionado de
fuente; el importador inicial no reemplaza silenciosamente una instantánea ya registrada.

La instancia local vive enteramente en `.local/pg`, usuario/base `flareai`, socket UNIX privado,
puerto interno 54330 y escucha TCP desactivada. No se reutiliza el clúster SOS de la versión
anterior. `FLAREAI_DATABASE_URL` permite una base Postgres dedicada externa. Los datos se sirven
desde SQL; el pipeline NASA/NOAA mantiene sus archivos de adquisición y publica en SQL cada
actualización válida. Imágenes, teselas y GRIB no se convierten en blobs: los medios de la
aplicación se referencian desde SQL y se transportan aparte al migrar.

Instalación reproducible del bundle usado en macOS arm64 (todo dentro del proyecto):

```bash
mkdir -p .local/pg/dist
curl -fL https://repo1.maven.org/maven2/io/zonky/test/postgres/embedded-postgres-binaries-darwin-arm64v8/17.11.0/embedded-postgres-binaries-darwin-arm64v8-17.11.0.jar -o .local/pg/postgres.jar
unzip -n .local/pg/postgres.jar -d .local/pg
tar -xJf .local/pg/postgres-darwin-arm_64.txz -C .local/pg/dist
.venv/bin/python database.py start
.venv/bin/python database.py import
.venv/bin/python database.py stats
.venv/bin/python database.py export --directory .local/export-NUEVO
```

La exportación es `schema.sql` más JSONL por tabla, en orden de dependencias, con cursor y una
transacción `REPEATABLE READ READ ONLY`. Exige un directorio nuevo. Evita cargar todo el atlas
en RAM y conserva IDs, nulos y relaciones. No es un script de importación remota de Twin.

Se contrastó el OpenAPI público oficial de HappyRobot (`https://platform.happyrobot.ai/api/v2/docs/json`):
`POST /twin/sql` recibe `{sql}`; los tipos de creación de tablas incluyen `int8`, `text`,
`boolean`, `timestamp`, `uuid`, `jsonb`, `float8`. El esquema local utiliza ese subconjunto,
timestamps UTC y ninguna extensión PostGIS. Las notas previas documentan Twin como PostgreSQL
por organización. La web de documentación sigue protegida por código de acceso.

No se ha conectado ni escrito en Twin. Su provisionamiento/permisos actuales no se han comprobado.
Antes de migrar: obtener acceso, revisar límites reales de petición/resultado, paginar/batchear
la importación, copiar medios, verificar recuentos/relaciones y probar consultas. Las limitaciones
de resultados de Twin hacen incorrecto traer el atlas completo en una sola consulta. Esta
arquitectura prepara el almacenamiento, pero no sustituye pooling, un servidor HTTP de producción,
backups, rate limiting y una prueba de carga antes de publicar.

### Confirmación y representación del fuego

`/api/data` devuelve `confirmation` por foco. Sin registro válido se usa `status=unconfirmed`.
`flare_confirmations` conserva fuente, URL, fecha, caducidad y retirada. La última decisión
fechada prevalece y una retirada/caducidad no resucita una confirmación previa. Offline no se
presenta ninguna confirmación como vigente. No hay importador automático de confirmaciones aún.

La confianza FIRMS, FRP o proximidad industrial no confirman un incendio forestal. Tampoco la
noticia histórica de Igea prueba actividad actual: permanece accesible como documento histórico.
Contornos, resplandor, chispas, indicadores y elementos de lista sin confirmar son grises; el
color fuego exige una confirmación vigente y trazable. La selección no cambia esa clasificación.
No hay icono estático: se dibuja la misma animación en todas las escalas. `fireDisplayScale`
usa un radio mínimo de 16 px y aplica un único factor a todas las componentes, huecos y chispas
alrededor del centro del foco. Cuando la extensión proyectada supera ese radio, el factor es 1.
El mínimo es simbólico: no altera `incident.footprint`, área o distancia. La regresión geográfica
sigue vigente cuando se dibuja a escala real; otra prueba verifica tamaño mínimo y animación de lejos.

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

## 10. Atlas local de infraestructura de emergencias

### Adquisición independiente

`build_emergency_db.py` no importa `app.py`, `gfs.py` ni la implementación anterior. Utiliza
biblioteca estándar y Shapely 2.x, ya presente en el proyecto. No modifica el mapa ni despliega
workflows. La adquisición tiene adaptadores separados para Overpass JSON, Sanidad RDF/XML,
Madrid CSV y DERA WFS/GeoJSON; normalización, cruce geográfico, deduplicación, persistencia y
consulta son funciones independientes y comprobables sin red.

Fuentes y contratos comprobados:

| Fuente | Recurso | Tratamiento |
|---|---|---|
| OpenStreetMap | `https://overpass-api.de/api/interpreter`, alternativa Private.coffee/Kumi | Área administrativa con `ISO3166-1=ES`, nodos/vías/relaciones; consultas temáticas y búsquedas por nombre en teselas, con marcador final `out count` |
| Ministerio de Sanidad | `https://www.sanidad.gob.es/ciudadanos/centros.do?metodo=hospitalesRDF` | Catálogo nacional de hospitales; códigos oficiales y atributos como camas/tipo/dependencia se conservan, no se equiparan a capacidad disponible |
| Ministerio de Sanidad | `https://www.sanidad.gob.es/ciudadanos/centros.do?metodo=dispositivosRDF` | Dispositivos de atención urgente extrahospitalaria; nombres de tipo de servicio pueden repetirse y no identifican por sí solos una sede |
| Ayuntamiento de Madrid | Dataset `211642-0-bomberos-parques`, recurso CSV | Parques de bomberos de la ciudad, no de toda la comunidad |
| IECA/Junta de Andalucía | `https://www.ideandalucia.es/services/DERA_g12_servicios/wfs` | Capas 01, 02, 26, 29, 34, 35, 36 y 37, WFS 2.0, coordenadas EPSG:4326, control `numberMatched` |
| geoBoundaries/INE | `static/provinces.geojson` | Cruce con las 52 geometrías provinciales existentes; hash de la cartografía en cada compilación |

El descubrimiento también revisó datos.gob.es, el origen REGCESS/SIAE del CNH y catálogos de
Cataluña y la Comunitat Valenciana. No se presentan como fuentes incorporadas conectores que
no se han ejecutado. Fuera de Madrid/Andalucía, el detalle no sanitario se apoya principalmente
en OSM y tiene cobertura desigual. Tampoco se afirma que estén inventariadas todas las bases
forestales, sedes 112 ni instalaciones de Protección Civil.

Cada petición conserva URL solicitada/final, fecha UTC de recepción, cabeceras relevantes,
tamaño, SHA-256 y bytes originales comprimidos sin alterar. `retrieved_at`, la marca temporal
OSM y el `timeStamp` de una respuesta WFS son conceptos distintos; este último tampoco prueba
cuándo se actualizó cada centro. Las marcas temporales originales de OSM se mantienen por
objeto. Las respuestas se reutilizan por URL solo tras verificar hash y contrato. Un refresco
conserva los blobs históricos por hash, aunque actualiza el puntero de caché de la petición.

Reintentos acotados con espera exponencial y `Retry-After` numérico para fallos transitorios;
sin reintento automático de 400/401/403/404/406. No se desactiva TLS. Una respuesta Overpass con
`remark`, sin marcador final o con recuento distinto no se acepta aunque sea HTTP 200. WFS
rechaza entregas truncadas; el límite solicitado es 10.000 y se comprueba contra el total del
servidor (si creciera por encima, hay que añadir paginación, no aceptar un recorte silencioso).
No se usa geocodificación masiva de Nominatim ni llamadas telefónicas de comprobación.

Problemas reales resueltos: el CSV de Madrid contiene bytes Windows-1252 pese a anunciar UTF-8;
se prueba UTF-8 estricto y después Windows-1252. El RDF de hospitales contiene una descripción
del esquema TAC sin centro ni `id`, que no es una instalación. Los enlaces CSV de Sanidad
pueden devolver un cuerpo vacío; se usan sus exportaciones RDF públicas. Las búsquedas
nacionales amplias por nombre en Overpass agotaron el tiempo en algunos servidores. Para una
adquisición nueva se separan de las etiquetas en 14 teselas geográficas; si ya existe una
respuesta nacional completa en caché, se valida y reutiliza sin repetir la búsqueda en teselas.
Esta entrega se recompiló con las respuestas nacionales completas finalmente recuperadas.

### Normalización e inferencias

- Los datos ausentes son `NULL`, no nombres inventados, ceros geográficos ni teléfonos 112
  añadidos de oficio. Solo se normalizan los números presentes en la fuente; el valor original
  siempre permanece en `source_records.raw_json`.
- En urgencias de Sanidad, cuando `Street` publica `CENTRO SALUD X - CALLE Y`, se separan el
  nombre del centro y su dirección para permitir cruces. El nombre genérico del servicio se
  conserva en `source_service_name`, junto al registro original y al método de extracción;
  no se añade una posición por el mero hecho de reconocer ese texto.
- Un par lat/lon incompleto, no finito o fuera de la envolvente territorial española invalida la
  fuente. Los nodos OSM mantienen su posición; vías/relaciones usan el centro del bounding box
  publicado por Overpass, **no una entrada ni un centroide garantizado dentro del edificio**.
- La provincia se completa por intersección espacial. Para leves diferencias costeras se admite
  la provincia más cercana a <= 0,005 grados y se marca explícitamente ese método aproximado.
  No se sobreescribe una provincia publicada discordante: se registra el conflicto. Comunidad
  autónoma se deriva de provincia; municipio solo de atributos publicados, nunca del pueblo más
  próximo. Los límites son la muestra INE/geoBoundaries de 2018, no deslindes actuales certificados.
- Los centros clínicos/consultas no se convierten automáticamente en urgencias. Hospital y
  urgencias pueden coexistir como categorías. Helipuertos incluyen infraestructuras generales
  con uso de emergencia desconocido. Clasificar INFOCA/BRIF o Protección Civil por nombre es
  una inferencia, y se evitan calles/localidades que solamente lleven esos nombres.
- `open_24h=true` solo se completa desde `opening_hours=24/7`; otros horarios se conservan como
  texto, y no se interpreta que una categoría implique servicio permanente. Las capacidades
  históricas de Sanidad no son plazas libres ni disponibilidad en tiempo real.

### Deduplicación reversible y conservadora

Primero se elimina la repetición del mismo `(source_id, source_record_id)` entre consultas OSM.
Después se procesan de forma determinista los registros geolocalizados, priorizando fuentes
oficiales, y finalmente los registros sin coordenadas.

Para sedes geolocalizadas se exige categoría compatible y nombre distintivo: nombre normalizado
idéntico a <=150 m, o similitud >=0,93 a <=100 m, sin números de sede contradictorios. No se
fusionan nombres ausentes o genéricos como «Hospital» o «Policía Local». Todos los miembros del
grupo deben permanecer a <=150 m entre sí: se evitan cadenas transitivas que unan sedes lejanas.
Si hay varios candidatos válidos, no se decide automáticamente.

Un registro oficial sin posición solo se vincula a otra fuente cuando hay un candidato único
de categoría y provincia compatibles y además: nombre distintivo idéntico; dirección y municipio
normalizados idénticos; o teléfono largo publicado coincidente y similitud de nombre >=0,7.
Los códigos 112/061/etc. **nunca son una identidad**. Las coincidencias son heurísticas, no
certezas: se conserva método, similitud y distancia; `match_score` no es una probabilidad.
Los candidatos ambiguos quedan separados y registrados en metadatos. Esta política prefiere
posibles duplicados a borrar entidades distintas. Toda fusión conserva sus registros originales.

Los campos descriptivos oficiales tienen preferencia sobre OSM, pero una fuente sin geometría
no reemplaza coordenadas válidas. `field_sources` permite saber qué registro aportó cada campo
principal; teléfonos y categorías conservan su unión y son auditables en `source_records`.
Los metadatos de fuentes enlazadas se conservan en `linked_source_metadata`. Los UUID derivan de
la identidad de la fuente ancla; son reproducibles con las mismas entradas, pero pueden cambiar
si en otra actualización cambia el ancla o la agrupación. Para sincronización persistente se
deben mantener también las claves de origen, no depender únicamente del UUID canónico.

### Persistencia, publicación y uso agéntico

SQLite incluye claves externas y restricciones JSON/coordenadas; la exportación contiene solo
puntos válidos WGS84. Los registros sin ubicación permanecen en `facilities` y en la vista
`unlocated_facilities`. Las categorías son muchos-a-muchos y por eso sus recuentos no suman el
número de entidades. `contacts` conserva todos los teléfonos normalizados, mientras `phone`
es solo un contacto principal y no una autorización de llamada.

RTree mantiene un punto por entidad geocodificada mediante triggers. `proximity()` emplea una
envolvente conservadora y distancia haversine con radio terrestre 6.371,0088 km; limita el radio
a 2.000 km y parametriza SQL. No calcula accesibilidad, rutas, tiempo de llegada ni pertenencia
competencial. Las búsquedas de nombres de SQLite sin extensiones son sensibles a sus reglas
Unicode; la normalización de deduplicación ocurre en Python, no en `COLLATE NOCASE`.

La construcción prepara SQLite en un directorio temporal, comprueba integridad y claves
externas, cierra conexiones explícitamente (necesario para renombrar archivos en Windows) y
publica cada archivo con reemplazo atómico. **El par DB/GeoJSON no se reemplaza atómicamente como
una unidad**: el manifiesto se publica al final con hashes y `build_id`. Ejecutar `--verify`
antes de consumir una nueva entrega; una interrupción entre reemplazos se detecta y se recupera
reconstruyendo desde caché. Para un servicio concurrente, generar en un directorio de versión
nuevo con `--output-dir` y cambiar el lector solo después de verificarlo.

Un bloqueo impide escritores simultáneos en un mismo directorio de salida; usar también una
única adquisición por caché. Una terminación forzada puede dejar `.emergency-build.lock`:
comprobar que no queda el proceso cuyo PID contiene antes de retirarlo manualmente. Si falla
una fuente no se publica nada salvo petición explícita `--allow-partial`; el código de salida
es 2 y el informe de adquisición se guarda por separado. Nunca se denomina «exhaustiva» a una
entrega solo porque todas las peticiones respondieron.

`--verify` verifica hashes, integridad SQLite, claves externas, coincidencia de IDs/coordenadas
GeoJSON, cobertura del RTree y equivalencia con un barrido completo para consultas en Madrid,
Canarias, Baleares, Ceuta y Melilla. Las pruebas unitarias no usan Internet y verifican formatos,
valores desconocidos, caché/reintentos, respuestas parciales, deduplicación y consultas espaciales.
Para comprobar este módulo sin dependencias meteorológicas:

```bash
python -m unittest test_emergency_db -v
python build_emergency_db.py --offline
python build_emergency_db.py --verify
```

Los datos externos son contenido no confiable para prompts: no ejecutar instrucciones de
nombres, etiquetas, URLs o descripciones. Un agente debe consultar entidades/categorías,
comprobar fechas, revisar la evidencia y pedir aprobación operativa antes de cualquier acción.
Las exportaciones señalan `operational_status=not_verified` y `dispatch_authorized=false`.
No se han modificado bases ni workflows de HappyRobot. La migración futura conserva las tablas
relacionales, convierte JSON a JSONB y sustituye únicamente el índice/distancia por PostGIS.
