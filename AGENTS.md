# AGENTS.md — FlareAI

Instrucciones para cualquier agente IA (Claude Code, Cursor, Codex CLI, etc.) que trabaje en
este repositorio.

## Proyecto

**FlareAI**: observatorio web de incendios en España (anomalías térmicas NASA FIRMS, viento y
temperatura NOAA GFS, imágenes satelitales NASA GIBS y un escenario visual de avance orientado
por el viento). Servidor Python stdlib + frontend estático (Leaflet local, sin build). Lee
primero `README.md` y `docs/IMPLEMENTACION.md`.

> **Reorganización (2026-09-19):** se sustituyó la implementación anterior (S.O.S. Agentic Crisis
> Engine sobre HappyRobot) por este proyecto (FlareAI) a petición del usuario. Todo el código e
> implementación anterior (sos/, web/, config/, tests/, voice/, main.py, main_simulation.py,
> requirements.txt, deploy-state.json, .env, .local/, .venv/) se apartó a `versión-anterior/` —
> no se toca por ahora. Ese Vault (`HappyRobot-Vault/`) sigue documentando esa implementación
> anterior sobre HappyRobot.

- `app.py` — servidor HTTP (stdlib) y caché compartida entre visitantes; sirve la API y los
  estáticos.
- `gfs.py` — descarga parcial GRIB2 de NOAA GFS, validación con eccodes e interpolación de
  viento/temperatura.
- `detectar.py` — descarga y filtro geográfico/temporal de CSV globales NASA FIRMS (VIIRS).
- `incidents.py` — agrupación de focos, asignación de provincia, huellas y métricas derivadas.
- `build_emergency_db.py` — atlas independiente de infraestructura de emergencias. Python >=3.10,
  Shapely 2.x y SQLite JSON1/RTree, sin ecCodes. Compila `emergencias_espana.db`, GeoJSON y
  manifiesto; fuentes originales en `data/emergency_sources/`. Verificar con
  `python -m unittest test_emergency_db -v` y `python build_emergency_db.py --verify`;
  reconstruir sin red con `python build_emergency_db.py --offline`. No confundir cobertura
  nacional con exhaustividad ni disponibilidad operativa. Un único escritor por caché/salida.
- `satellite.py` — imágenes NASA GIBS (natural/SWIR) con caché en disco y control de cobertura.
- `static/` — frontend: `index.html`, `app.js`, `flow.js` (geometría/partículas/índice
  geográfico), `flames.js` (renderizador Canvas 2D de llamas/corrientes), `simulation.js`,
  `wind.js`, `styles.css`, GeoJSON de España/provincias, Leaflet vendorizado.
- `data/` — caché activa de descargas (FIRMS, GFS, satélite) y evidencias originales.
- `examples/` — muestra congelada para reproducir pruebas sin red.
- `docs/IMPLEMENTACION.md` — arquitectura, fórmulas, APIs y fuentes en detalle.
- `test_integration.py`, `test_flow.mjs`, `test_renderer.mjs`, `test_simulation.mjs`,
  `verify_api.py` — pruebas Python/JS existentes.
- `versión-anterior/` — implementación previa completa (S.O.S. Agentic Crisis Engine sobre
  HappyRobot: `sos/`, `web/`, `voice/`, `config/`, `tests/`, etc.), apartada por ahora.
- `HappyRobot-Vault/` — vault de **Obsidian** con la documentación de cómo funciona HappyRobot
  y de todo lo construido en esa implementación anterior (formatos de nodos por API, problemas
  resueltos, IDs, bitácora). Se mantiene aunque HappyRobot ya no sea el proyecto activo.
- `.claude/skills/obsidian-docs/` — skill de Claude Code equivalente a la sección siguiente.

FlareAI no requiere API key para NASA/NOAA. La demo de voz usa `HAPPYROBOT_API_KEY` de
`happyrobot-112/.env`, solo en backend y nunca en el repo/vault. Los secretos de la implementación
anterior siguen en `versión-anterior/.env` (`HAPPYROBOT_API_KEY`).

## Director HappyRobot y rutas locales (19/09/2026)

- `director.py` conecta avisos de DemoBridge con un Reasoning Agent independiente; no hay planner
  determinista de respaldo en producción. SMS/Telegram quedan fuera. Traffic Lab sigue aislado;
  las cámaras del mapa participan únicamente en la revisión visual, no en decisiones de rutas.
- `director_workflow.py`: workflow `01a0b948-d14b-7883-bb58-2c9a014f27f4`; versión corregida
  `01a0b969-9df4-7789-87b5-d2cea2da3cff`. No modificar el workflow de voz. `upgrade` prepara un fork;
  HappyRobot exige despublicar la versión viva antes de publicar otra: pedir confirmación específica.
- `Incoming hook` entrega `data.context_json`, NO `context_json` en la raíz. El prompt referencia
  el ID persistente del grupo de `available-vars`, que puede diferir del ID del nodo tras un fork.
  Las tool calls reales pueden contener `name`/`args` y además `function.arguments`: no detener la
  búsqueda en el wrapper sin argumentos. Regresiones en `test_director.py`.
- La credencial literal del webhook permanece en `flare_settings['director-workflow']`, solo backend.
  El valor que devuelve `configuration.api_key` puede estar transformado: `sync` conserva la clave
  literal, no la sustituye por ese valor. No imprimir credenciales ni pedir pegarlas en el chat.
  `Database.export` elimina `hook_key`. API de cuenta y clave de hook son distintas.
- Migración 4: estado y eventos en `flare_director_state`/`flare_director_events`. Nueva sesión en cada
  arranque, histórico conservado. Un worker con advisory lock, revisión por cambios/cada 180 s,
  hasta 30 runs/hora, ocho incidentes por contexto (exceso declarado), ocho acciones por plan.
  Validar revisiones antes/después de calcular rutas; sin ruta no hay despacho. Flota ficticia,
  sedes reales del SQLite en solo lectura. Llegar no libera el vehículo ni confirma extinción.
- `local_routes.py`: A* local sobre geometrías OSM descargadas por zona vía Overpass, caché SQL.
  No usa servicios de routing externos. Sentidos/acceso básicos, sin tráfico/gálibos/giros completos.
  Máximo 60 km entre extremos, descarga 24 MB, caché siete días. Trayectos visuales acelerados.
- UI inicial solo mapa, instalaciones desde zoom 13 y exclusión sobre huellas; cámaras desde 10.
  `static/director.js`: decisiones temporales, borde de actividad y camiones por distancia acumulada.
  ES-Alert puede llegar al receptor web de demo (nunca Cell Broadcast real). Sin parte habilitante
  sigue siendo solo vista previa. Dos vehículos de la misma sede salen escalonados.
- Seguimiento visual: viaje en tres fases (alejar, recorrer, acercar), ronda de avisos demo y
  vehículos activos tras un evento reciente. Los refrescos no reencuadran; interacción manual
  suspende hasta pulsar «Reanudar seguimiento IA». Respetar pausa, pestaña oculta y movimiento reducido.
  Limitar el delta por fotograma evita saltos si el render tarda. No limpiar el calor antes de
  tener zoom inicial: `heat.paint()` necesita `getPixelOrigin()` de un mapa inicializado.
- Evidencias automáticas: FIRMS por detección a ≤10 km del aviso, no por centroide; brillo máximo
  etiquetado como máximo del grupo, separado de ambiente NOAA GFS. GIBS SWIR/color natural vía
  proxies existentes, sin imagen automática cuando no hay detecciones cercanas. Cámaras del catálogo
  verificado reciente, captura automática o vídeo por apertura explícita. Fechas/offline visibles,
  respuestas tardías canceladas. Es revisión visual de fuentes, NO visión artificial ni confirmación
  oficial. Nunca modifica llamadas, planes o clasificación. No integrar Traffic Lab por este flujo.
  `verify_director_ui.py` añade recorrido entre zonas, GIBS offline real y cámara fixture, pausa,
  control manual y móvil; captura generada en `.local/director-evidence.png`.
- Pruebas: `.venv/bin/python -m unittest test_director test_local_routes -v`;
  `PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_director_ui.py`
  (fixtures, ruta Tarragona debe estar cacheada). `verify_director.py --cloud` o el verificador UI
  con `--cloud` consumen cuota real; no ejecutarlos automáticamente en CI.
- Run real verificado `87e54d53-bfb5-489e-8def-b3ab2d6f932b`: contexto Tarragona, plan del LLM,
  dos camiones y ruta local 2,08 km. Entrada de llamada fixture, NO nueva prueba de audio real.
  Mypy global conserva un error previo ajeno en `sms_demo.py:271`; los archivos del director pasan.

## Bomberos 123, ES-Alert móvil y manos libres (19/09/2026)

- Mismo marcador `/112/`: 112 ciudadano y **123 ficticio** bomberos. El 123 exige seleccionar aviso
  activo y permite elegir unidad. Backend vincula el parte al run civil y a sus coordenadas; una
  corrección de ubicación invalida partes de la posición anterior. No es autenticación de bomberos reales.
- Workflow de voz independiente `01a0b99b-dad8-7751-8e0a-cc7e5423f152`, versión
  `01a0b99b-dae5-7ad8-8f08-38a49710aa7a`, publicado/live. Metadatos en
  `flare_settings['firefighter-workflow']`; `director_workflow.py deploy-responder` solo despliega
  el borrador propio, nunca despublica otro. 112 y director remoto no se modificaron.
- Solo `actualizar_parte` del asistente aporta llegada/incendio/solicitudes/evolución/zona urbana.
  Enums validados, revisión y procedencia por campo: notas de una llamada antigua no resucitan una
  confirmación que otra unidad ya retiró. SQL existente conserva roles, vinculación y parte en JSON.
  Confirmación de bomberos sigue siendo DEMO. Descartado/extinguido retira avisos call sin borrar NASA.
- `director.py` ingiere partes incluso si el planner está desconectado. Una solicitud explícita de
  ES-Alert es un mandato de demo, no un planner alternativo. El LLM decide refuerzos/reasignación y puede
  emitir al receptor si hay fuego confirmado + urbano declarado, o población y ≥5 % urbano en el
  atlas cercano (heurística de demo, no protocolo). Llegada solo actualiza la unidad que informa.
- Helicópteros ficticios sobre helipuertos reales del atlas. `air_route()` es una línea ilustrativa
  hasta 180 km, no ruta aeronáutica; nunca usar A* de carretera para vuelo. Despacho exige petición
  aérea o parte confirmado que empeora/critico. No implica disponibilidad real de medios aéreos.
- `/112/alerts/`: activar antes de emitir; sonido Web Audio acotado a 8 s y botón de silencio.
  Polling `/112/api/alerts` con cookie, secuencia y UUID de sesión; no reproduce histórico al abrir,
  no duplica alertas ni las confunde entre reinicios. Sin push/Cell Broadcast; mantener pantalla
  abierta, volumen habilitado. No garantiza recepción con móvil bloqueado o web suspendida.
- Geocodificación: solo municipio exacto se resuelve localmente; calle/POI pasa a IGN, alias
  carrer/calle, avda/avenida, etc. No degrada una dirección a ciudad ni toma un homónimo ambiguo.
  Las ubicaciones precisas conservan su punto comunicado, no el centro del grupo NASA cercano.
- `happyrobot-112/static/audio.js`: botón Altavoz funcional, mezcla remota por Web Audio + relay
  HTMLMediaElement; intenta salida de altavoz explícita con setSinkId. Si no hay soporte, lo informa
  y remite al selector del sistema. No forzar audioSession playback mientras se captura micrófono.
  La ruta física del altavoz en Safari/iOS requiere validación humana en el dispositivo.
- Verificación: `verify_director_ui.py` cubre 123/partes/receptor/AudioContext/refuerzos/helicópteros;
  voz y planes fixtures. `verify_director.py --cloud --response` consume cuota real: run
  `65e67946-7dc6-40c1-ad03-40d930b1c06c` asignó tres camiones de dos parques, helicóptero y ES-Alert.
- `verify_responder_voice.py --cloud --audio .local/bomberos-pcm.wav` consume cuota. Run real
  `4400cb07-88d4-4076-a338-117a7e24e151` validó habla sintética por LiveKit → todos los campos
  del parte → notificación simulada. Chromium usa `%noloop`: sin silencio, la muestra en bucle
  no cerraba turno. No confundir esa prueba con escucha humana en móvil. Usar expectativas de
  locators en Playwright para el marcador; `wait_for_function` puede chocar con su CSP sin unsafe-eval.

## Traffic Lab de Lucía (aislado)

- `traffic_lab/` conserva su propio servidor, frontend, dependencias, muestras y workflow.
  Leer `traffic_lab/AGENTS.md` antes de modificarlo. No integrarlo automáticamente con el mapa,
  la base de datos ni el marcador 112. Puerto propio: 8790, solo loopback.
- En este Mac se verificó con Python 3.12.11 en `traffic_lab/.venv/`, separado de la `.venv/`
  raíz (Python 3.14). Mantener las versiones de `traffic_lab/requirements.txt` sin instalarlas
  en el entorno de FlareAI. Intérprete auxiliar y herramientas locales bajo `.local/`.
- Desde la raíz: `traffic_lab/.venv/bin/python traffic_lab/launch.py --local` arranca sin
  HappyRobot. Pruebas: `traffic_lab/.venv/bin/python -m unittest discover -s traffic_lab -v`.
- No ejecutar `launch.py` con clave, `happyrobot.py deploy`, `publish-draft` ni `verify.py --cloud`
  como parte de una comprobación de merge: pueden crear/modificar workflows o consumir cuota.
  `verify.py` sobrescribe el informe versionado; conservar las evidencias originales de Lucía.

## Demo webcall 112 integrada

- `demo.py` reutiliza el proveedor de `happyrobot-112/server.py`; no necesita Twin. Requiere
  workflow publicado en `production` con `actualizar_ficha`, ID en `happyrobot-112/workflow.json`
  o `HAPPYROBOT_WORKFLOW_ID`. No ejecutar `setup_happyrobot.py` sin pedirlo: modifica el workflow remoto.
- Arranque online: `.venv/bin/python app.py --host 127.0.0.1 --port 8090`; en otra terminal,
  `.venv/bin/python demo.py publish`. Cloudflared local en `.local/cloudflared/cloudflared`.
  `--offline` no activa la demo. No arrancar además el servidor independiente de `happyrobot-112/`.
- Puerto 8090: mapa. Puerto 8112: solo `/112/` y su API; el túnel publica exclusivamente este
  último. Puertos alternativos: `app.py --mobile-port N` y `demo.py publish --port N`.
  El enlace del mapa consulta `/api/demo/setup` al cargar: abrir/recargar después de lanzar el túnel.
- Sin código de vinculación: cookie de navegador automática, HttpOnly, SameSite=Strict y Secure
  vía HTTPS. Cualquiera con la URL temporal puede consumir cuota; no es autenticación de producción.
  Mantener el túnel solo durante la demo. Nunca publicar el puerto del mapa por este túnel.
- Cada `Store` online crea una `DemoBridge` vacía con UUID nuevo. Cookies previas inválidas hasta
  recargar el marcador. SQL conserva las sesiones/avisos de la migración 3 pero no los restaura.
- Solo `actualizar_ficha` del asistente confirma avisos demo; no inferir confirmaciones desde texto
  libre del llamante ni confianza FIRMS. Geocodificación local + CartoCiudad/IGN conservadora.
  Emparejar a ≤3 km de la huella, no del centroide; ambiguo = pendiente de ubicación.
- Avisos nuevos: `source_kind=call`, geometría ilustrativa, sin observaciones/FRP/hectáreas NASA.
  Overlay sin mutar originales; confirmación demo trazable en `/api/demo/report/<run_id>`.
  El mapa consulta cada 2,5 s; HappyRobot cada 2 s, ficha móvil cada 0,9 s.
- `publish()` verifica aislamiento y excluye `HAPPYROBOT_*`, `TUNNEL_*`, `CLOUDFLARE_*` del entorno
  del subproceso. Pruebas: `test_demo.py` y regresión SQL de reinicio en `test_database.py`.
- Verificación 19/09/2026: workflow publicado/live, HTTPS real, SDK LiveKit y cookie segura sin
  código, aislamiento público y flujo HTTP simulado. Webcall real sobre Tarragona: mensajes de
  usuario/asistente y `actualizar_ficha` en HappyRobot; aviso automático confirmado demo y
  seleccionado en Chromium sin errores JS. Falta valoración humana de escucha en móvil; no
  confundir `configured=true`, SDK cargado o mocks con prueba de calidad del audio.
  Pasan 57 tests Python raíz, 6 del marcador y 42 JS, Ruff/mypy/ESLint.

## Contexto territorial del atlas

- `database.py` + `schema.sql`: PostgreSQL 17 local en `.local/pg`, socket privado (puerto interno
  54330, sin TCP); psycopg en `.venv`. `python database.py start` y `python database.py import`.
  El arranque normal lo prepara automáticamente. No toca la base SOS de `versión-anterior/`.
- El servidor usa SQL para atlas, cámaras, instantáneas FIRMS/GFS, instalaciones y metadatos de
  cartografía/imágenes. `nearby_atlas()` hace un filtro indexado por caja antes del cálculo Shapely.
  `Atlas.load()` permanece como importador/referencia para pruebas, no para consultas del servidor.
- Tipos compatibles con Twin (`text`, `float8`, `int8`, `timestamp`, `jsonb`), PK/FK e índices,
  sin PostGIS. Prefijo `flare_` evita colisiones con el legado. Timestamps SQL en UTC.
  `FLAREAI_DATABASE_URL` permite otro Postgres. Nunca conectar/escribir automáticamente en Twin.
- Exportación local: `python database.py export --directory .local/export-NUEVO` genera esquema
  y JSONL con cursor, en una instantánea consistente. No es todavía un importador remoto de Twin.
  Las imágenes/GRIB permanecen en disco; SQL conserva datos procesados y referencias de medios.
- `GET /api/context?id=<id>` calcula el entorno bajo demanda, independiente de `/api/data`.
  `static/context.js` presenta el resultado; `/atlas/sources` conserva las atribuciones/licencias.
- Radio de 5 km desde la huella térmica aproximada (no desde su centro). Se seleccionan centros
  de celdas de 1 km² y puntos OSM, no viviendas ni perímetros industriales. Población 2021,
  suelo 2019, OSM 18/09/2026. No etiquetar estos datos como población afectada o riesgo oficial.
- Viento hacia `(procedencia + 180) % 360`, sector ±30°, mínimo 3 km/h; sin aviso direccional
  con viento ausente/desactualizado. Offline muestra contexto histórico, nunca alerta actual.
- Preferencia actual: heatmap automático al pulsar un foco, sin botón de activación, con iconos
  de instalaciones y ficha al pulsar (`static/infrastructure.js`). Las cámaras solo aparecen desde
  zoom 10: no hay iconos ni grupos de cámaras en el panorama. Se conservan en SQL aunque estén ocultas.
  Las actualizaciones no deben mover la cámara. El canvas del calor no captura clics.
- El calor acumula degradados radiales y traduce densidad a una paleta de 256 pasos; se dibuja
  al 60 % de resolución, en `multiply`, bajo el fuego, y se repinta una vez por fotograma.
- Carreteras IGN: WMS nacional `TN.RoadTransportNetwork.RoadLink`, siempre visible, teselas
  solicitadas por viewport vía `/roads/z/x/y.png`, caché y metadatos SQL; no es un grafo viario
  descargado completo ni contiene cortes/tráfico. No descargar masivamente teselas.
  `StableRoadLayer` excluye `viewprereset` de sus eventos (Leaflet local 1.9.4): el zoom continuo
  usa `map.setView` por fotograma y ese evento destruía todas las teselas. Conserva `viewreset`,
  `zoom`, `moveend` y la retención normal de padres/hijos para mantener cobertura al cargar.
- Webcams: catálogo original de 2.926 registros en SQL, no exhaustivo ni sincronizado automáticamente.
  La migración 2 añade `flare_camera_checks` (FK, estado, método, fecha, caducidad). `/api/webcams`
  solo devuelve medios comprobados, integrables y vigentes; se excluyen enlaces externos, candidatos
  sin verificar y plantillas conocidas de imagen no disponible. No borrar sus registros originales.
  La UI refresca la lista cada minuto y oculta una cámara que falle al abrirla.
- Auditoría: `python territorial.py verify-cameras` (cuatro workers, dos por fuente, límites de
  tamaño/tiempo y allowlists de redirección); `python verify_camera_players.py` prueba el iframe
  con Playwright desde el origen local real, sin falsear Referer ni extraer tokens/manifiestos.
  Un HTTP 200 o `<video>` no prueba reproducción: exige fotogramas y avance de tiempo. El servidor
  reevalúa lotes de 200 medios y hasta 20 vídeos cada diez minutos; locks SQL evitan barridos duplicados.
- Detecciones sin confirmar en gris; **confirmadas en rojo/fuego animado**, también al alejarse.
  `flare_confirmations` exige fuente, fecha y caducidad; confianza FIRMS alta no es confirmación.
- Preferencia visual actual: **la misma animación en todas las escalas, sin icono estático**.
  `fireDisplayScale` mantiene un radio visual mínimo de 16 px, con un factor común para toda la
  huella, huecos y chispas. Al superar ese tamaño usa escala geográfica 1:1. Nunca modifica
  `incident.footprint` ni cálculos de superficie/distancia. No ampliar componentes por separado.
  La ondulación sigue anclada a la forma y se respetan pausa y movimiento reducido.
- API v2: `potential` contiene `model`, `samples`, `zones` GeoJSON, `facilities`, `status` y
  limitaciones. `POTENTIAL_MODEL` centraliza pesos/umbrales versionados; cada muestra incluye
  evidencia, contribuciones, proximidad y datos ausentes. Se usan todas las celdas y los puntos OSM
  del radio, no los 12 puntos de compatibilidad del endpoint. No sumar población desde instalaciones.
- Potencial es prioridad exploratoria de revisión, **no probabilidad ni plan de actuación**. El viento
  histórico/desactualizado no aumenta la puntuación; los polígonos suavizados no son perímetros de
  peligro. No colorear cobertura totalmente desconocida como si fuera riesgo bajo.
- Pruebas: `FLAREAI_TEST_DATABASE=1 .venv/bin/python -m unittest -v` incluye regresiones con
  PostgreSQL importado; sin esa variable se omiten únicamente las pruebas SQL.
  Lint: `.venv/bin/ruff check *.py`,
  `.venv/bin/python -m mypy --ignore-missing-imports --cache-dir .local/mypy-cache *.py`.
  Node local: `.local/node-v22.19.0-darwin-arm64/bin/node --test test_*.mjs`.
- Herramientas instaladas únicamente dentro del proyecto: Python en `.venv/`, Node y cachés
  en `.local/`. No instalar herramientas globales. Playwright de comprobación usa
  `PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers"`.
- El servidor habitual se ejecuta **online**, sin `--offline`; el atlas siempre es una instantánea
  estática. La actualización online puede modificar cachés y evidencias bajo `data/`.

## Documentar en el vault de Obsidian (`HappyRobot-Vault/`)

Cuando el usuario pida **documentar**, **añadir al vault**, **apuntar esto en Obsidian**, o al
cerrar una sesión de trabajo relevante sobre HappyRobot/FlareAI que deba recordarse después,
sigue estas reglas.

### Por qué existe

El vault es la memoria persistente y legible del proyecto: para que cualquiera (otro agente,
otra sesión, otra persona) entienda el qué, el cómo y el porqué sin releer el historial del
chat.

### Estructura

```
HappyRobot-Vault/
├── 00 Índice.md        # mapa de navegación — actualizar SIEMPRE sus enlaces al añadir notas
├── Conceptos/           # cómo funciona HappyRobot en general (API, auth, nodos, voces...)
├── Proyecto/            # lo específico construido aquí (workflows, código, cómo arrancarlo)
├── Referencia/           # chuletas: IDs, endpoints, catálogos, problemas/soluciones
└── Bitácora/             # una nota por fecha (YYYY-MM-DD.md) con el registro cronológico
```

Si el vault no existe todavía, créalo con esta misma estructura antes de escribir notas.

### Reglas de estilo (toda nota nueva o editada)

1. **Frontmatter YAML** al inicio:
   ```yaml
   ---
   tags: [happyrobot, <categoría: concepto|proyecto|referencia|bitácora>]
   ---
   ```
   Las notas de Bitácora añaden también `date: YYYY-MM-DD`.
2. **Wikilinks (`[[Nombre de la nota]]`)** liberalmente. Cada nota termina con una línea
   `Relacionado: [[...]] · [[...]]`. Un link a una nota que aún no existe está bien.
3. **Una nota = un tema concreto**, nombre de fichero descriptivo en español, título estilo
   frase (`Autenticación y hosts API.md`, no `auth.md`). Evita notas cajón de sastre.
4. **Actualiza `00 Índice.md`** cada vez que crees una nota nueva: añade su enlace en la
   sección correspondiente y refresca el bloque "Estado actual" si algo cambió.
5. **Prioriza el "por qué" sobre el "qué"**: decisiones, alternativas descartadas, motivos
   concretos ("elegimos X porque Y falló con este error exacto").
6. **Comandos/código reproducibles** en bloques \`\`\`bash / \`\`\`json cuando documentes un
   procedimiento técnico.
7. **Nunca guardes secretos completos** (API keys, tokens, contraseñas). Si hay que
   referenciar una credencial, usa solo los últimos 3-4 caracteres o un alias, y anota dónde
   vive el valor real (variable de entorno, gestor de secretos).
8. **Bitácora**: al cerrar una sesión con cambios relevantes, añade o actualiza
   `Bitácora/YYYY-MM-DD.md` (fecha real) con: petición inicial del usuario, pasos realizados en
   orden, resultado al cierre, y "Pendiente / próximos pasos" si aplica. Si ya existe una nota
   de ese día, amplíala en vez de sobreescribirla.

### Flujo a seguir

1. Comprueba si `HappyRobot-Vault/` ya existe. Si no, créala.
2. Repasa qué se descubrió (comportamientos, límites de la API) y qué se construyó/cambió
   (código, workflows, IDs) en la sesión.
3. Decide carpeta (Conceptos / Proyecto / Referencia) para cada pieza; prefiere ampliar una
   nota existente antes que duplicar (busca primero con grep/búsqueda de archivos).
4. Escribe/edita las notas siguiendo las reglas de estilo.
5. Actualiza `00 Índice.md`.
6. Añade la entrada de `Bitácora/YYYY-MM-DD.md` del día.
7. Antes de terminar, verifica que no haya secretos completos filtrados
   (`grep -rn "sk_live_\|sk-\|Bearer " HappyRobot-Vault/`, ajustando el patrón al secreto
   relevante).
8. Resume al usuario qué notas se crearon/actualizaron, enlazando el índice.
