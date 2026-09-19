# FlareAI

**España, bajo observación.** Mapa blanco con anomalías térmicas NASA, viento y temperatura NOAA, imágenes satelitales y un escenario visual orientado por el viento.

## Arranque

Servidor Python + PostgreSQL; frontend Leaflet sin compilación ni claves API. Las carreteras usan
el WMS oficial del IGN y las cámaras contactan con sus proveedores solo al abrirlas. Herramientas
locales en `.venv/` y `.local/`; no se requieren instalaciones globales.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py --host 127.0.0.1 --port 8090
```

El arranque requiere PostgreSQL. En este equipo ya está instalado en `.local/pg/dist`, con una
base independiente `flareai`, socket privado bajo `.local/pg`, sin escucha TCP. El servidor
prepara el esquema e importa los datos iniciales una sola vez. En otro equipo, instala PostgreSQL
en el proyecto o configura `FLAREAI_DATABASE_URL` con una base dedicada. No se usa la base SOS.

```bash
.venv/bin/python database.py start
.venv/bin/python database.py import
.venv/bin/python database.py stats
.venv/bin/python database.py export --directory .local/export-NUEVO
```

La exportación crea un directorio nuevo con `schema.sql` y JSONL por tabla, leyendo mediante
cursores en una transacción consistente. No borra ni sobrescribe la base original. Los medios
referenciados se copian aparte al migrar. Véase la sección PostgreSQL de `docs/IMPLEMENTACION.md`.

Abrir `http://127.0.0.1:8090` en el navegador de **esa máquina**. Para una máquina remota, usar un túnel SSH o un proxy HTTPS. `--host 0.0.0.0` permite conexiones a sus interfaces de red. La vista previa de Devin utiliza este modo; no es un despliegue permanente.

El ZIP incluye datos del **19 de septiembre de 2026** e imágenes del **18 de septiembre**. Al arrancar, el servidor sirve esa caché e intenta actualizarla. Consulta siempre las fechas de cada fuente.

### Sin conexión

```bash
python app.py --offline --host 127.0.0.1 --port 8090
```

Muestra el periodo de la muestra guardada, identificado como tal, aunque hayan transcurrido días. Las imágenes de Igea en ambas capas están guardadas. Otras zonas solo tendrán imagen offline si se consultaron antes con conexión. No se contacta con NASA ni NOAA en este modo.

## Demo webcall 112 → mapa

La webcall reutiliza `happyrobot-112/`; **no llama al 112 real**. Solo esta integración requiere
`HAPPYROBOT_API_KEY` en `happyrobot-112/.env` (ignorado por Git), junto con
`HAPPYROBOT_WORKFLOW_ID` o el identificador de `happyrobot-112/workflow.json`. El workflow debe
estar publicado en `production` y disponer de la tool silenciosa `actualizar_ficha`. La clave
permanece en el backend; no hace falta Twin. No ejecutes el servidor independiente del marcador
al mismo tiempo: ocuparía el puerto 8112 sin conectar con el mapa.

Desde la raíz, en dos terminales:

```bash
.venv/bin/python app.py --host 127.0.0.1 --port 8090
```

```bash
.venv/bin/python demo.py publish
```

El segundo comando requiere el binario local `.local/cloudflared/cloudflared`, comprueba el
puerto móvil y publica solo `127.0.0.1:8112` mediante Cloudflare Quick Tunnel, sin cuenta.
Imprime una URL HTTPS temporal terminada en `/112/`; ábrela en el móvil y mantén ambos procesos
activos. Abre el mapa en `http://127.0.0.1:8090` después de lanzar el túnel para que su enlace
**Webcall demo** recoja esa URL. `--mobile-port` en `app.py` y `--port` en `demo.py publish`
permiten cambiar el puerto móvil, usando el mismo valor en ambos.

1. Marca **112 en el teclado de la web**, pulsa llamar y permite el micrófono.
2. Di, por ejemplo: «Hay un incendio forestal en Igea, La Rioja».
3. Cuando el agente registre `actualizar_ficha` con incendio y ubicación suficiente, el mapa
   confirma el foco más cercano a ≤3 km de su huella o crea un aviso ilustrativo nuevo.
   La actualización es automática, sin código de vinculación ni botón de confirmación.
4. El rojo lleva la etiqueta **Llamada web · demo**, nunca confirmación oficial. Un aviso nuevo
   no inventa observaciones NASA, FRP, hectáreas ni perímetro quemado. Una ubicación ambigua
   queda pendiente hasta que el agente la precise.

Cada arranque online crea una sesión vacía: no recupera avisos ni cookies de sesiones anteriores.
Recarga el marcador después de reiniciar. El respaldo SQL conserva los registros anteriores sin
reaplicarlos al mapa; no se borran tablas. `--offline` no habilita la integración de voz.

El puerto 8112 solo sirve el marcador y su API `/112/`, no el mapa, SQL ni archivos del proyecto.
La sesión del navegador se prepara automáticamente con cookie HttpOnly/SameSite; no es una
contraseña: cualquiera con la URL puede iniciar llamadas de demo y consumir cuota de HappyRobot.
Comparte el enlace solo durante la prueba y detén el túnel con Ctrl+C al terminar. El subproceso
excluye variables `HAPPYROBOT_*`, `TUNNEL_*` y `CLOUDFLARE_*` y no usa la configuración global.

Comprobaciones sin iniciar una llamada:

```bash
curl http://127.0.0.1:8112/112/api/status
curl http://127.0.0.1:8090/api/demo/setup
FLAREAI_TEST_DATABASE=1 .venv/bin/python -m unittest -v test_demo test_database
```

`configured: true` indica configuración local, no prueba de audio ni de permisos remotos.
Validado: HTTPS público, cookie segura automática, carga del SDK LiveKit, aislamiento, workflow
publicado/live, reinicio limpio con SQL y flujo HTTP con proveedor simulado. El 19/09/2026 entró
una **webcall real sobre Tarragona**: mensajes de usuario/asistente y `actualizar_ficha` en
HappyRobot, aviso creado automáticamente y seleccionado como confirmado demo en Chromium, sin
errores JavaScript. La calidad de escucha en el móvil requiere confirmación del usuario; no se
ha medido latencia de audio ni probado exhaustivamente Safari/iOS.

Para desplegar el frontend en Vercel u otro hosting, conserva un backend para la clave, los tokens,
el polling de HappyRobot y PostgreSQL. La demo actual usa rutas relativas y cookies del mismo
origen: requiere un proxy `/112/api/*` hacia ese backend, o adaptar explícitamente esa separación.
Publicar solo los estáticos no ejecuta `app.py` ni su adquisición en segundo plano.

## Director autónomo de la demo

El mapa arranca sin selección ni paneles abiertos. `flareai +` recupera la exploración manual.
Gasolineras e instalaciones aparecen desde zoom 13 y se ocultan si tapan la huella del fuego.

Cuando una llamada aporta un aviso localizado, un **Reasoning Agent de HappyRobot** recibe el
contexto territorial, la meteorología fechada, los recursos y la memoria reciente. Decide mediante
`publicar_plan`; el backend local valida la revisión, los IDs, la disponibilidad y las rutas antes
de mostrar movimientos. No se sustituye el LLM por reglas locales. El workflow de voz no cambia.

Mensajes breves, un borde multicolor de actividad, estaciones y vehículos muestran lo que ocurre.
La flota es ficticia sobre sedes del atlas real; el discreto `modo demo` permanece visible. No se
movilizan servicios reales, no hay SMS y ES-Alert es solo una vista previa. Las cámaras no intervienen
todavía en las rutas. La memoria se conserva durante la sesión; reiniciar crea una nueva, sin borrar
el historial SQL anterior.

El seguimiento visual aleja el mapa, recorre la distancia y vuelve a acercarse al aviso o al
trayecto. Tras recibir actividad, alterna entre los avisos de la sesión y vehículos en movimiento.
Arrastrar, hacer zoom o explorar manualmente suspende este seguimiento; **Reanudar seguimiento IA**
lo recupera. La pausa y la preferencia de movimiento reducido también se respetan.

Al revisar un aviso se muestran evidencias disponibles: detecciones FIRMS a ≤10 km, brillo I4
máximo del grupo (no temperatura de las llamas), ambiente/viento NOAA GFS y, si hay coincidencias
FIRMS, mosaico NASA GIBS SWIR con opción de color natural. Las cámaras verificadas cercanas muestran
una captura o permiten abrir explícitamente el vídeo del proveedor. Cada fuente lleva su fecha;
la ausencia de imagen o detección **no descarta la llamada**. Es contraste visual automático de
fuentes, no un análisis de píxeles por IA ni una confirmación oficial. No conecta el Traffic Lab
ni cambia decisiones del Reasoning Agent.

Las rutas se calculan **localmente con A\***: se descargan geometrías OSM acotadas vía Overpass y se
cachean en PostgreSQL. No se llama a un servicio externo de routing. Se respetan sentidos únicos
y acceso básico, pero no hay cortes/tráfico real, gálibos ni todas las restricciones de giro. Sin
ruta conectada no se inventa un trayecto. La animación está acelerada, no representa una ETA real.

```bash
.venv/bin/python director_workflow.py status
.venv/bin/python -m unittest test_director test_local_routes -v
PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_director_ui.py
```

La prueba visual sin `--cloud` usa fixtures y requiere la ruta de Tarragona ya cacheada. Para
verificar un razonamiento real con cuota, ejecutar expresamente:

```bash
.venv/bin/python verify_director.py --cloud
PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_director_ui.py --cloud
```

Verificado el 19/09/2026: el LLM real decidió asignar dos camiones del parque de Tarragona y se
aplicaron rutas locales de 2,08 km. El aviso de entrada era una fixture, no una nueva llamada de
voz. El workflow nuevo está separado del marcador; credenciales solo en backend. `sync` conserva
la clave literal del hook, pues el valor devuelto por la API puede estar transformado. Nunca
copiar claves al frontend ni al repositorio. La exportación SQL omite la clave del hook.

## Qué puedes hacer

- Seleccionar una superficie de calor o una zona de la lista.
- Buscar provincias y filtrar el caso contrastado en prensa.
- Cambiar entre Península, Baleares, Canarias y Ceuta/Melilla.
- Ver viento, rachas, temperatura ambiente y brillo térmico.
- Pulsar un foco para encuadrar automáticamente su entorno y ver el **mapa de calor de riesgo inmediato alrededor**, de crema a coral, con iconos de instalaciones.
- Pulsar una instalación para ver actividad, distancia a la huella, prioridad orientativa, fecha y enlace OSM.
- Ver cámaras **solo al acercarte** (zoom 10 o superior), sin iconos en la vista general. Del catálogo de 2.926 registros se muestran únicamente capturas o vídeos integrables comprobados; los enlaces externos y las cámaras no disponibles quedan ocultos, no borrados.
- Ver la **red de carreteras IGN** siempre activada, con detalle por zoom. Se descarga por teselas visibles y se almacena en caché; no es una copia vectorial nacional ni informa de carreteras transitables.
- Pasar el ratón por el calor para leer qué hay en ese punto: instalaciones, residentes censados, vegetación y distancia a la huella.
- El potencial combina proximidad, población, vegetación, instalaciones y viento vigente. Es una prioridad exploratoria de revisión, no una probabilidad de incendio ni una recomendación operativa. Los datos y los motivos quedan en `/api/context?id=<id>` para análisis posterior por una IA.
- Consultar color natural o SWIR y ampliar la imagen.
- Acercar la huella aproximada de los píxeles.
- Ver bordes de llama, núcleos de calor y chispas que siguen el viento local.
- Explorar corrientes animadas, con zoom continuo centrado en el cursor y reproyección durante el arrastre.
- Pausar las animaciones con **Ⅱ** junto a los controles del mapa. Se respeta la preferencia del sistema de reducir movimiento.
- Pulsar **Escenario**: elegir avance supuesto y reproducir de 0 a 6 horas.
- Exportar JSON con el botón superior, o CSV desde `/api/incidents.csv`.

## Cómo interpretar el mapa

**No todas las señales son incendios forestales.** Se agrupan observaciones térmicas, incluidas posibles industrias y quemas agrícolas. La detección depende del satélite, las nubes, el horario y el tamaño del fenómeno. No es un inventario exhaustivo.

**No conocemos el perímetro quemado.** La cifra de huella térmica aproxima el área cubierta por los píxeles. No equivale a hectáreas quemadas. Por eso la superficie quemada confirmada aparece como «—».

**Gris no confirmado, color fuego confirmado.** La confianza de NASA FIRMS se refiere a la detección térmica, no a la confirmación de un incendio forestal. El color fuego requiere un registro en `flare_confirmations` con fuente, fecha y vigencia, o un aviso de la sesión webcall identificado explícitamente como **demo**; una noticia histórica no basta. No hay una fuente automática de confirmaciones oficiales conectada. Las llamadas no modifican las detecciones NASA ni equivalen a una verificación oficial.

**Las llamas son un tratamiento visual.** El contorno parte de la huella de los píxeles y añade resplandor, ondulación y chispas. La silueta queda anclada al terreno: al hacer zoom escala como el mapa, sin deformarse. Al alejarse se conserva la misma animación con tamaño visual mínimo de unos 32 px, sin icono estático. Se escala el conjunto desde su centro, sin alterar la geometría medida; al acercarse más allá del mínimo recupera su tamaño geográfico. El color, la velocidad de animación y las chispas no miden temperatura, transporte de pavesas ni avance del fuego. Para ver el detalle, selecciona **Igea → Acercar a la huella detectada**.

**La imagen es un mosaico diario, no una cámara en directo.** La aplicación busca la fecha más reciente con suficiente cobertura y muestra su fecha.

**Las dos temperaturas significan cosas distintas.** GFS proporciona temperatura ambiente modelizada a 2 m. VIIRS I4 proporciona temperatura de brillo de un píxel; no es temperatura de las llamas.

**El escenario es ilustrativo.** Su velocidad de avance es un supuesto elegido en el control. Solo usa el viento para la dirección; no es un modelo de propagación ni una herramienta de emergencia.

## Contexto territorial en PostgreSQL

El atlas original se conserva en `data/Espana_Datos_y_Mapas/`. Una importación transaccional carga
511.226 celdas y 44.787 elementos OSM en tablas SQL con claves e índices. Al seleccionar un foco,
se consulta solo su caja de proximidad y se aplica la distancia a la huella con Shapely. Las
pruebas comparan el resultado SQL con el cálculo sobre el atlas completo.

`database.py` y `schema.sql` guardan además catálogos de cámaras y fuentes, instantáneas FIRMS/GFS,
focos, observaciones, confirmaciones, modelo de potencial y cartografía. Imágenes, teselas y GRIB
siguen como archivos; los medios consumidos por la aplicación tienen referencias y metadatos SQL.
El esquema usa tipos admitidos por Twin, sin PostGIS ni dependencia de HappyRobot en ejecución.
No se ha migrado nada a Twin ni se ha validado todavía la importación contra una instancia remota.

El catálogo Faro se importa desde el ZIP y conserva las fechas de cada proveedor; **no se
sincroniza automáticamente**. Su disponibilidad sí se comprueba periódicamente y se guarda en
`flare_camera_checks`. Se prueban imágenes reales (excluyendo plantillas de servicio no disponible)
y la reproducción de vídeos dentro de un iframe local. No se eluden restricciones del proveedor.
Las cámaras visibles se actualizan cada minuto; las capturas abiertas respetan su intervalo.
Recuperación no equivale a hora de captura, y un estado válido puede cambiar después.

```bash
.venv/bin/python territorial.py verify-cameras
.venv/bin/python verify_camera_players.py
```

La segunda comprobación usa Playwright de `requirements-dev.txt` y Chromium instalado bajo
`.local/playwright-browsers`. Sin navegador disponible, no se habilitan vídeos sin comprobar.
Fuentes y derechos: `/webcams/sources`. Las carreteras retienen las teselas anteriores durante
el zoom para no desaparecer mientras llegan las del nuevo nivel.

- **Población:** INE / Eurostat, censo 2021; centros de celdas de 1 km², no ubicaciones de viviendas ni núcleos con nombre. Las edades publicadas pueden no sumar el total por protección estadística.
- **Suelo:** Copernicus CGLS-LC100 2019; porcentajes ponderados por superficie clasificada, conservando ausencia de cobertura.
- **Instalaciones:** OSM / Geofabrik, 18/09/2026; prioridad orientativa por actividad, no riesgo oficial. Puede haber omisiones o varios elementos de un mismo complejo.
- **Viento:** sector de ±30° hacia donde sopla, desde la huella, con un mínimo de 3 km/h. Se desactiva con datos ausentes, errores meteorológicos, validez alejada más de 2 h o ciclo de más de 12 h. En modo offline solo se muestra orientación histórica.

`potential` conserva todas las muestras, instalaciones cercanas, geometrías visuales, factores, puntuación 0–100 y versión del modelo. La escala no es un porcentaje de riesgo: los pesos son heurísticos, aún no calibrados operacionalmente. El suavizado de las áreas no delimita zonas de peligro y la ausencia de color no garantiza seguridad. Las actualizaciones refrescan la capa sin cambiar el encuadre elegido por el usuario.

No se estima población afectada, tiempo de llegada ni evacuaciones. Se conservan los demás campos del atlas, pero sexo, lugar de nacimiento y movilidad no se utilizan para asignar riesgo de incendio. Fuentes y condiciones de reutilización: `data/Espana_Datos_y_Mapas/FUENTES.md` (también en `/atlas/sources`). Las condiciones de GISCO requieren revisión antes de uso comercial.

## Actualización y consumo

| Fuente | Comprobación del servidor | Frecuencia real / detalle |
|---|---:|---|
| NASA FIRMS VIIRS | Cada 30 min | Detecciones según pasadas; pueden llegar horas después |
| NOAA GFS | Cada 10 min | Pasos horarios; ciclos cada 6 h; malla de 0,25° |
| NASA GIBS | Al seleccionar zona y capa | Mosaico diario; caché por zona/capa/hora |
| Navegador (mapa) | Cada 2,5 s | Consulta únicamente a este servidor; no descarga NASA/NOAA por visitante |
| Demo HappyRobot | Cada 2 s | Solo llamadas activas; la ficha del móvil consulta el backend cada 0,9 s |

Los visitantes comparten una descarga meteorológica y una caché de focos. No se solicita GFS por visitante. El acceso público probado no requiere clave; no constituye una garantía de capacidad infinita ni de disponibilidad.

## Archivos

- `app.py`: servidor y caché compartida.
- `gfs.py`: descarga parcial GRIB2, validación ecCodes e interpolación.
- `detectar.py`: CSV globales FIRMS y filtro geográfico/temporal.
- `incidents.py`: agrupación, provincias, huellas y métricas.
- `satellite.py`: imágenes NASA GIBS con caché y control de cobertura.
- `static/`: interfaz y Leaflet local.
- `static/flow.js`: geometría, partículas, índice geográfico y presupuestos de dibujo.
- `static/flames.js`: renderizador Canvas 2D de fuego y corrientes, sin dependencia de WebGL.
- `static/heat.js`: mapa de calor del entorno (paleta, densidad acumulada y rótulo al pasar el ratón).
- `data/`: datos activos y evidencias originales de las descargas.
- `examples/`: muestra congelada para reproducir pruebas.
- `evidence/`: verificación HTTP y captura de pantalla completa.
- `docs/IMPLEMENTACION.md`: arquitectura, fórmulas, APIs y fuentes.
- `docs/VERIFICACION.md`: alcance y resultados de las comprobaciones.

## Verificar

```bash
python -m pip install -r requirements-dev.txt
python -m unittest -v
FLAREAI_TEST_DATABASE=1 python -m unittest -v test_database
ruff check *.py
python -m mypy --ignore-missing-imports *.py
python -m compileall -q *.py
# Solo para las pruebas de JavaScript: Node >= 20; probado con Node 24.
node --test test_*.mjs
npx --yes --package eslint@9.33.0 eslint static/*.js test_*.mjs
```

Con la aplicación arrancada:

```bash
python verify_api.py --url http://127.0.0.1:8090
curl http://127.0.0.1:8090/api/incidents.csv -o zonas.csv
```

Las pruebas HTTP consultan ambos productos de imagen de la primera zona. Con conexión pueden descargar dos imágenes a GIBS. En modo offline usan la caché.

## Base nacional de infraestructura de emergencias

`build_emergency_db.py` es independiente del servidor y no necesita claves, ecCodes ni servicios
agénticos. Requiere Python >= 3.10 con SQLite JSON1/RTree y Shapely 2.x (ya es dependencia del
proyecto). Instalación mínima en un entorno virtual: `python -m pip install shapely==2.1.1`.

```bash
python build_emergency_db.py
python build_emergency_db.py --verify
python -m unittest test_emergency_db -v
```

Entrega en la raíz:

- **`emergencias_espana.db`**: entidades georreferenciadas y registros oficiales pendientes de
  localizar, índice RTree, categorías múltiples, contactos y procedencia auditable.
- **`emergencias_espana.geojson`**: únicamente entidades con coordenadas, puntos WGS84
  `[longitud, latitud]`. Los centros sin posición **no se inventan ni se colocan en el centro del municipio**.
- **`emergencias_espana.manifest.json`**: recuentos por provincia/comunidad/categoría, campos
  ausentes, estado y fechas de fuentes, limitaciones y SHA-256 de ambos artefactos.
- **`data/emergency_sources/`**: respuestas originales comprimidas y evidencias de descarga.

**Fuentes incorporadas:** OpenStreetMap/Overpass para toda España (incluidas islas y ciudades
autónomas); Ministerio de Sanidad (Catálogo Nacional de Hospitales y dispositivos de urgencias
extrahospitalarias); Ayuntamiento de Madrid (bomberos); IECA/Junta de Andalucía, DERA
(salud, hospitales/centros de especialidades, bomberos, policía, Guardia Civil, coordinación,
organizaciones humanitarias y socorro). El CNH se nutre de REGCESS/SIAE: esto **no es una
extracción completa de todo REGCESS**. `datos.gob.es` se usa como catálogo de descubrimiento,
no como otra fuente de registros duplicados.

Las categorías incluyen hospitales, centros sanitarios, urgencias, bomberos, bases forestales,
policía, Protección Civil, coordinación, ambulancias, salvamento, helipuertos y organizaciones
humanitarias. Una entidad puede tener varias categorías. Un centro sanitario no implica servicio
de urgencias; un helipuerto no implica uso sanitario autorizado. La clasificación por nombre y
los enlaces entre fuentes son inferencias auditables, no certificaciones oficiales.

**Entrega del 19/09/2026:** 25.730 registros de origen, 25.136 entidades tras deduplicación,
22.575 puntos georreferenciados y 2.561 registros oficiales pendientes de localizar (499
hospitales y 2.062 dispositivos de urgencias). Hay puntos en las 52 provincias/ciudades autónomas.
Las instantáneas OSM utilizadas abarcan del **06/05/2026 al 19/09/2026**: no representan todas
el estado actual. De los puntos, 14.628 no tienen municipio publicado y 15.334 carecen de
teléfono normalizable; el manifiesto detalla el resto de carencias. SQLite ocupa 95,2 MB y
GeoJSON 26,6 MB. Pasan 25 pruebas del módulo, lint, tipos y la verificación de ambos artefactos.
La suite general necesita además ecCodes, ausente en el entorno utilizado para esta tarea.

### Reanudar, actualizar y consultar

```bash
python build_emergency_db.py --offline
python build_emergency_db.py --refresh
python build_emergency_db.py --output-dir data/emergency_release
python build_emergency_db.py --near 40.4168 -3.7038 15 --category hospital --limit 10
```

Sin `--refresh`, reutiliza respuestas válidas de la caché; **no es una actualización automática**.
`--offline` prohíbe red. Si falla una fuente, no publica archivos, devuelve código 2 y guarda el
informe en `data/emergency_sources/last_acquisition.json`; reejecutar reanuda desde la caché.
`--allow-partial` permite explícitamente una entrega incompleta, señalada en el manifiesto.
`--overpass-endpoint URL` permite indicar servidores HTTPS (repetible). `--download-only` solo
adquiere las fuentes. No ejecutar escritores concurrentes sobre la misma caché.

**Cobertura nacional no significa exhaustividad ni vigencia operativa.** Consultar siempre
`source_status`, las fechas OSM, los campos ausentes y `unlocated_facilities`. La fecha de
descarga no es la de actualización del centro. No se ha comprobado por teléfono la existencia,
disponibilidad, capacidad o autorización de movilización de cada recurso. No conectar estas
fichas directamente a llamadas/despachos autónomos sin verificación y aprobación.

### Tablas y consultas para agentes

| Tabla / vista | Contenido |
|---|---|
| `facilities` | UUID, nombre, dirección, municipio, provincia, comunidad, lat/lon, contacto principal, método de coordenadas, metadatos JSON |
| `categories`, `facility_categories` | Catálogo y relación muchos-a-muchos |
| `contacts` | Todos los teléfonos publicados normalizables; los códigos 112/061 siguen siendo códigos generales |
| `sources`, `downloads` | Publicador, licencia, ámbito, URLs, fechas, hashes y evidencias |
| `source_records` | Identificador original, registro crudo/normalizado, enlace a entidad y método/puntuación/distancia del enlace |
| `facility_rtree` | Índice espacial sincronizado mediante triggers de inserción, cambio y borrado |
| `coverage`, `unlocated_facilities`, `build_metadata` | Cobertura, pendientes de geolocalización y metadatos de compilación |

```sql
SELECT * FROM coverage WHERE province = 'Madrid';
SELECT id, name, municipality FROM unlocated_facilities;
SELECT s.name, r.source_url, r.match_method, r.raw_json
FROM source_records r JOIN sources s ON s.id = r.source_id
WHERE r.facility_id = :facility_id;
```

Para distancia esférica en kilómetros (no tiempo de conducción), la función Python registra
`distance_km` en SQLite, prefiltra con RTree y aplica haversine. No requiere SpatiaLite:

```python
import sqlite3
from contextlib import closing
from build_emergency_db import proximity

with closing(sqlite3.connect("file:emergencias_espana.db?mode=ro", uri=True)) as db:
    hospitals = proximity(db, lat=40.4168, lon=-3.7038, radius_km=15,
                          category="hospital", limit=10)
    print([(r["name"], round(r["distance_km"], 2)) for r in hospitals])
```

SQL equivalente, tras registrar `db.create_function("distance_km", 4, distance_km)`:

```sql
SELECT f.id, f.name, distance_km(:lat, :lon, f.lat, f.lon) AS km
FROM facility_rtree r JOIN facilities f ON f.pk = r.pk
WHERE r.max_lon >= :west AND r.min_lon <= :east
  AND r.max_lat >= :south AND r.min_lat <= :north
  AND distance_km(:lat, :lon, f.lat, f.lon) <= :radius_km
ORDER BY km LIMIT :limit;
```

Los parámetros del rectángulo deben envolver el círculo; usar `proximity()` para calcularlos
sin perder candidatos. Para PostgreSQL/PostGIS, conservar los UUID y claves originales,
transformar los JSON a JSONB y reemplazar RTree por un índice GiST sobre `geography(Point,4326)`
y `ST_DWithin(..., radio_metros)`. No se han desplegado integraciones en HappyRobot.

Atribución: © OpenStreetMap contributors, ODbL 1.0; Ministerio de Sanidad
([condiciones](https://www.sanidad.gob.es/avisoLegal/home.htm)); Ayuntamiento de Madrid e
IECA/Junta de Andalucía, CC BY 4.0; límites provinciales geoBoundaries/INE. Mantener licencias,
procedencia y fechas al redistribuir; el acceso público no implica SLA. Más detalle en
`docs/IMPLEMENTACION.md`, sección 10.

## Implantación

Este servidor es un prototipo reproducible con la biblioteca estándar de Python. Para servicio público persistente, ejecutar un único proceso de adquisición, almacenar cachés y evidencias en un volumen persistente y servir los recursos mediante un proxy HTTPS. Configurar límites de concurrencia y peticiones en el proxy; para tráfico alto, trasladar el servidor a un framework de producción. Evitar iniciar varios escritores sobre el mismo directorio `data/`.

Probado localmente en macOS arm64 con PostgreSQL 17.11. No se han validado Windows ni cargas de
producción. SQL e índices preparan el almacenamiento para crecer; no sustituyen un servidor HTTP
de producción, pooling, límites de clientes, backups y monitorización al desplegar.
