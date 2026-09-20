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

## ES-Alert decidido por el agente (20/09/2026, sustituye restricciones anteriores)

- El agente valora el peligro para la población descrito por bomberos (humos tóxicos, explosión, propagación…),
  sin esperar petición explícita ni `evolucion=critico`. `es_alert=no_solicitado` no veta esa decisión.
  Un incendio pequeño sin amenaza exterior, humo genérico o proximidad urbana no bastan; respetar negaciones.
- La acción `alert` autónoma incluye `population_risk=true` y `report_evidence` igual al `detalle` íntegro actual.
  `operations.alert_allowed` valida la vinculación; no hay detector por palabras clave ni alerta determinista
  por toxicidad. La clasificación semántica es del LLM. Petición explícita sigue siendo mandato; parte crítico
  sigue habilitando valoración; descarte/extinción bloquean. Distinguir evacuación/confinamiento en `reason`.
- `director.anchor` incluye partes para invalidar planes en vuelo tras correcciones. Se mantienen idempotencia,
  veto humano de 3 s en escenario y receptor solo simulado. No hay cambios de esquema ni migraciones Twin.
- `director_workflow.ALERT_POLICY` se comparte con `presentation_workflows.DIRECTOR_POLICY`; el guion saliente
  conserva amenazas, negaciones y exposición en `detalle` (240 caracteres), sin pedir autorización de alerta.
  Publicados con autorización: director `01a0bc22-7844-71ac-82d9-26479d46e02b`, voz saliente
  `01a0bc23-078f-75a8-96d7-ba7d29e61424`; mismos workflows, voz/tools preservados, metadatos sincronizados
  en local/Twin. La publicación del director tardó en reflejarse: GET confirmó live, no se republicó.
  Backend reiniciado con autorización, manteniendo `--presentation --allow-outbound` en 8090/8112; sin llamadas
  ni runs de prueba. Recargar mapa/marcador tras cambiar sesión.
- Verificar con `.venv/bin/python -m unittest test_operations test_director test_presentation test_scene
  test_autodispatch test_demo test_local_routes -q`: 130 pruebas, Ruff y mypy pasan. Planes/voz fixtures,
  no validan el razonamiento LLM live; GET remoto sí verificó los prompts y estado publicados.

## Cierre rápido para demo (20/09/2026, sustituye las esperas anteriores)

- Petición expresa: al apagarse el fuego, regreso inmediato e informe rápido. `Scene.evolve` y
  `AutoDispatch.lifecycle` pasan de contención a retirada en el mismo tick, sin vigilancia de 25 + 45 s.
  El regreso visual dura 5–15 s; la unidad sigue ocupada hasta llegar a sede y se respetan cortes reales
  del escenario. Las ambulancias en traslado lo completan antes de regresar; no se inicia otro al retirar.
- `Operations.tick` genera el informe al entrar en `releasing`, sin esperar `closed`. El PDF indica las
  unidades todavía ocupadas al emitirse; no declara regreso completado ni alta médica. No duplica el
  informe al cerrar. Peticiones pendientes antiguas no vuelven a movilizar medios durante la retirada.
- Verificado con 123 pruebas Python (`test_autodispatch test_scene test_operations test_presentation
  test_director test_demo test_local_routes`), 36 JS y Ruff. `verify_presentation.py` actualiza las
  expectativas a cinco testigos + llamada, comprueba PDF antes de llegar a base y descarga desde Cerebro
  en Chromium; voz/LLM fixtures, rutas locales cacheadas, sin llamadas ni cloud.

## Dispositivo automático garantizado (petición expresa 19/09/2026, posterior)

- Sustituye la regla «no hay planner determinista de respaldo» para la movilización: el usuario exige que
  **siempre** salgan bomberos de distintos parques, ambulancia y patrulla, que apaguen el fuego y vuelvan,
  y que un parte con refuerzos envíe más. `autodispatch.py` lo garantiza en todos los modos sin esperar al
  LLM (que sigue pudiendo añadir/reasignar/retirar). Base 3 camiones de sedes distintas + 1–2 ambulancias +
  1 patrulla; escala por radio, parte `empeora`/`critico` y 120 s sin contener, máximo 6 camiones; oleadas
  cada 20 s por aviso. Rutas fuera del cerrojo; `prepare` ya no lanza ante `dispatch` de unidad ocupada.
- Extinción progresiva (petición expresa): en `scene.py` el radio crece 0,0025 km/s y cada medio en el lugar
  resta 0,0022 km/s (camión 1, helicóptero 2); contención al bajar a 0,06 km. Más medios, antes; un solo camión
  no basta. Fuera del escenario `AutoDispatch.lifecycle` acumula trabajo (`CONTAIN_WORK` 90 medios·s) y sigue
  el mismo ciclo (vigilancia 25 s, retirada 45 s, regreso a sede, cierre). La tarjeta muestra `% extinción`. `Operations.held` deja de retener
  la extinción con telefonía desactivada/inalcanzable/sin parte y tiene tope `HOLD_LIMIT` 300 s.
- `auto.enabled=False` (o `store.auto_dispatch=False`) solo para pruebas del camino LLM. Verificar con
  `python -m unittest test_autodispatch test_director test_scene test_operations test_presentation test_demo`.
  `verify_scene.py` pasa todo el recorrido con la capa activa pero su paso final del marcador 123 está
  obsoleto (el botón 123 se retiró del frontend antes de este cambio).
- Una corrección de ubicación conserva el `demo_report.run_id`: las asignaciones guardan `report_run_id`.
  `AutoDispatch.reconcile_locations` redirige desde la posición actual si están a ≤20 km del punto corregido;
  si están más lejos, regresan y `ensure` envía medios nuevos. No presentar la corrección como otro incendio.
  Los canvas animados y el seguimiento de cámara se limitan a ~30 Hz y DPR 1,5 para mantener fluido el zoom.
- Al cerrar un incendio, `static/operations.js` retira del mapa la llamada 112 y sus testigos, sin borrar
  historial ni informes. Usa primero la fase de `/api/director` (escenario/auto) para no esperar al
  refresco de `/api/data`; también retira operaciones con informe final o aviso cancelado. Colgar no
  oculta avisos todavía activos. Regresión de retirada real de marcadores en `test_operations.mjs`.

## Presentación: centro local y datos dinámicos Twin (19/09/2026, revisión final)

- Decisión expresa: centro Python, atlas, grafos, cartografía y cachés siguen locales. **Twin solo para
  datos dinámicos**: contactos, llamadas, partes, decisiones, asignaciones, informes y memorias. No migrar
  el grafo de 48 MB ni el atlas estático. `twin.py::TwinDatabase` conserva los métodos estáticos de `Database`.
- Modo nuevo: `app.py --presentation`; implica escenario Barcelona y Twin. `--allow-outbound` permite
  llamadas telefónicas reales a contactos autorizados; sin él nunca llama. No activar en tests sin consentimiento.
  123 retirado de HTTP/frontend; los partes llegan por workflow saliente vinculado a la llegada de bomberos.
- `FLAREAI_TWIN_API_KEY` puede cargarse de `.env.presentation` (ignorado por Git). La clave ya instalada de
  voz permite leer Twin pero no SQL; la facilitada para Twin sí. El agente no pudo escribir ese archivo por
  protección de archivos ignorados: debe prepararlo el usuario. Nunca volcar claves ni teléfonos en docs.
- `flare_contacts` tiene emisor, principal y respaldo con prioridad; valores solo en Twin, no en código.
  `outbound.py` persiste el intento antes de llamar, prueba el respaldo tras fallo terminal y no repite
  un inicio incierto. Llamada real autorizada: principal busy/SIP 480; respaldo completado en 71 s, run
  `a3fc7f51-d439-40b2-a890-9b6d7299cd01`. Parte confirmado/crítico, sin peticiones de recursos registradas.
- Director existente actualizado con autorización: workflow `01a0b948-d14b-7883-bb58-2c9a014f27f4`, versión
  `01a0baae-e74e-7b09-8e65-a096fb403660`. Conserva hook literal. El director nuevo `01a0ba98-422f-7d5e-8bac-e27b846dafdc`
  dio 401/502 al disparar y queda candidato a limpieza, no se usa. No re-publicar ante respuesta tardía:
  verificar `is_live` por GET. Voz saliente: workflow `01a0ba93-b11b-7ed2-8e1d-2bc94b7eba1e`, live.
- `operations.py`: cinco testimonios sintéticos por aviso (`WAVE_SIZE`: tres coherentes, un dudoso, una broma;
  antes 24, reducidos el 19/09/2026 a petición expresa) cada 0,5–2 s, separados de la llamada real. El LLM recibe todos,
  debe evaluarlos antes del primer despacho y no recibe las etiquetas de referencia. No hay planner ficticio
  de respaldo. Solicitudes explícitas de bomberos se tramitan determinísticamente por mandato, con rutas,
  disponibilidad y cumplimiento; no se confunden con decisiones LLM. Cierre espera parte y refuerzos en destino.
- ES-Alert solo por solicitud explícita o evolución crítica comunicada en parte; urbano/humo no bastan.
  Mantiene temporizador de servidor de 3 s y veto. Nunca envía Cell Broadcast ni moviliza servicios reales.
- `reports.py`: informe, PDF stdlib y memorias breves en `FlareAI-Memoria/` (ignorado), enlazadas con Twin.
  `static/operations.js` presenta testimonios y grafo. Impactos son supuestos no calibrados; superficie máxima
  de escenario, no huella NASA. CO2 y precios 10/30/60 EUR/t son escenarios, no cotizaciones ni créditos emitidos.
- 112 cloud: `happyrobot-112/cloud/route.js`, preparado para Next.js, con cookies firmadas, origen, código
  privado de demo y reserva de llamada en Twin. `package_112.py` genera un ZIP sin secretos. Publicación aún
  pendiente de acceso a HappyRobot Apps; no confundir paquete preparado con sitio desplegado. Los enlaces
  cloud se leen de `flare_live_settings['phone-web'].url`; `FLAREAI_DEMO_ACCESS_CODE` se comparte en fragmento.
- Twin devuelve int8 como strings y limita SELECT a 500 filas/1 MB. Lectura paginada rechaza truncamientos.
  El endpoint rechazó WITH…INSERT; `flare_live_save_director_v1` guarda estado/eventos atómicamente. No fingir
  transacciones persistentes por HTTP. Lease renovable para un único director, fallo explícito al perderlo.
- Verificar: `python -m unittest test_twin test_operations test_presentation test_director test_scene test_demo -v`
  y `PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_presentation.py`.
  `verify_presentation.py --cloud` consume un run LLM, sin teléfono; `--phone` llama realmente y exige permiso.
  Run real `10f7c498-ee10-4bbc-a73e-f80ef0df9ade`: 24 testimonios evaluados, dos camiones, ambulancias y policía,
  sin ES-Alert. Entrada fixture, no voz ciudadana humana. La verificación UI de presentación usa fixtures.
- No borrar workflows antiguos sin lista/confirmación específica. Traffic Lab y prueba personal se mantienen
  aparte. `verify_director_ui.py` conserva recorrido antiguo 123: usar `verify_presentation.py` para el nuevo flujo.

## Macro simulador de sala (revisión posterior del 19/09/2026)

- Activar con `.venv/bin/python app.py --hackathon --host 127.0.0.1 --port 8090`. No recorta España.
  Preparación: `.venv/bin/python local_routes.py --prepare-demo`, 16 teselas reanudables en SQL,
  caja `[41.28, 2.00, 41.54, 2.32]` (sur/oeste/norte/este). Red verificada: 69.882 vías, 370.215 nodos.
  `barcelona-demo-road-v1` se publica solo al terminar todas las teselas; un único escritor. Las
  teselas marinas vacías son válidas; `remark` parcial no. No descargar teselas IGN masivamente.
- `scene.py` conserva el escenario separado de las observaciones; `static/scene.js` presenta historial,
  prioridad, hospitales, veto ES-Alert y controles; `static/traffic.js` dibuja coches sobre segmentos OSM.
  No conecta Traffic Lab. `--hackathon` requiere grafo precargado y director online; no es fallback LLM.
- FIRMS fuerte (FRP ≥15 MW, confianza alta, edad ≤24 h, zona preparada) persiste 8 s y entra como
  sensor sin llamada. No confirma oficialmente un incendio. Contraste por detección individual a ≤10 km;
  sin coincidencia, texto explícito «Contraste satelital simulado». Barco exclusivamente por ficha 112
  que lo comunique en Barcelona; punto marítimo ilustrativo, helicóptero al mar y tierra al encuentro costero.
- Atlas en solo lectura: se añaden dos ambulancias ficticias por hospital/base y ocho plazas ficticias
  por hospital; no representan camas disponibles. Traslado reserva plaza, llegada no da alta. El 123
  admite sensores sin inventar un run ciudadano; los controles de sala admiten partes de tres cuerpos.
- A* del escenario elimina tramos cortados, pondera congestión, conserva ruta anterior y recalcula
  desde posición interpolada. Sin alternativa se detiene (`blocked`, `held_position`). Coches de frontend
  comparten ID de tramo y se acumulan antes de la barrera. No recurrir a OSRM ignorando un corte.
- Crecimiento/contención ilustrativos separados de `footprint`, radio máximo 1,2 km (barco 150 m).
  Dos camiones o un helicóptero trabajando 45 s permiten contención; 25 s hasta vigilancia, otros
  45 s antes de retirada. Cierre solo después del regreso; no atribuir esas transiciones a NASA.
- En sala cualquier propuesta de alerta usa temporizador servidor de 3 s y veto por UUID; serializar
  envío/cancelación y mantener idempotencia/cooldown. Solo receptor web simulado, sin servicios públicos.
  Historial completo de sesión en `/api/director/history`, SQL conservado al reiniciar; refrescar navegador
  no pierde memoria. Controles POST solo puerto principal loopback, JSON acotado y Origin del mismo host.
- Director publicado con autorización: versión `01a0ba14-3e0f-700f-a77b-ebb32de57dbf`, mismo workflow.
  Voz 112/123 intacta. HappyRobot normaliza `{{grupo.data.context_json}}` a `{{ index . "grupo.data.context_json" }}`;
  `canonical_prompt` admite solo esa equivalencia, nunca ignorar otras diferencias. La publicación puede
  responder antes de reflejar `is_live`: verificar por GET antes de reintentar una sustitución.
- Run real `324cdb41-bf27-4073-9773-733c72f363f4`: dos camiones, dos ambulancias, policía y propuesta
  ES-Alert, sin bloqueos de ruta. Entrada 112 fixture, NO nueva prueba de voz humana.
- Verificación: `python -m unittest test_scene test_director test_local_routes test_demo -v`, Node
  `--test test_scene.mjs`, y `PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_scene.py`.
  `verify_scene.py --cloud` consume cuota y necesita autorización. Capturas `.local/scene-barcelona.png`
  y `.local/scene-mobile.png`; datos/planes fixture, SQL/grafo/interfaz reales. Esperar zoom inicial antes
  de `getBounds()` del tráfico, como con el calor. La prueba SQL de satélite usa Igea congelada, no el primer
  foco de la descarga mutable. La suite completa reescribe `evidence/api_offline.json` (solo fecha/puerto).

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
  sin tope local de runs/hora por petición expresa para la hackathon; ocho incidentes por contexto
  (exceso declarado), ocho acciones por plan. Mantener un solo run pendiente y validación de revisión/rutas.
  Validar revisiones antes/después de calcular rutas; sin ruta no hay despacho. Flota ficticia,
  sedes reales del SQLite en solo lectura. Llegar no libera el vehículo ni confirma extinción.
- `local_routes.py`: A* local sobre geometrías OSM descargadas por zona vía Overpass, caché SQL.
  No usa servicios de routing externos. Sentidos/acceso básicos, sin tráfico/gálibos/giros completos.
  Máximo 60 km entre extremos, descarga 24 MB, caché siete días. Trayectos visuales acelerados.
- UI inicial solo mapa, instalaciones desde zoom 13 y exclusión sobre huellas; cámaras desde 10.
  `static/director.js`: decisiones temporales, borde de actividad y camiones por distancia acumulada.
  ES-Alert puede llegar al receptor web de demo (nunca Cell Broadcast real). Sin parte habilitante
  sigue siendo solo vista previa. Dos vehículos de la misma sede salen escalonados.
- Marco IA (`#agent-aura` con un canvas por capa, `static/aura.js`): preferencia expresa final (19/09/2026): **forma** del
  marco Apple Intelligence (rectángulo redondeado continuo pegado al borde, inset 7–11 px, radio 18–30 px) con el
  **aspecto** de `BottomWave.jsx` de LogiOptiAI (trazos azul `rgba(56,189,248,.4)` 26 px/blur 30 y violeta
  `rgba(168,85,247,.5)` 20 px/blur 24, resplandor 90 px/blur 45; anchos y blur ampliados respecto al SVG original para igualar su suavidad en canvas, deslizándose en sentidos opuestos). Ondulación mínima
  (2,5–3 px), casi recta: no volver a ondas grandes ni a un marco nítido. Fundido por clase `ai-active` (opacity +
  visibility diferida para Playwright) mientras el director está `thinking` o muestra una decisión; pausa y
  movimiento reducido dejan un fotograma fijo. **El blur es CSS `filter` por canvas, nunca `ctx.filter`: Safari no lo
  implementa y pintaba el marco nítido y ondulado.** Nuevos estáticos deben añadirse al allowlist de `app.py`.
  Pruebas en `test_aura.mjs`.
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

## Tráfico visual local (20/09/2026)

- `static/traffic.js`: solo con zoom >13 (opacidad completa a 14), alrededor de unidades terrestres
  visibles, usando la posición del marcador para respetar pausa/movimiento reducido. Radio máximo
  650 m y 220 px con fundido periférico; 24 tramos, hasta dos coches por tramo y 48 en total.
- Barcelona consulta únicamente cajas locales cuantizadas de la red preparada; fuera de esa red
  reutiliza segmentos de rutas existentes, nunca vuelos ni trayectorias aproximadas. No descarga
  carreteras nuevas. Invalida descargas al alejar, ocultar, quedar sin unidades o cambiar de sesión.
- Los recálculos visuales solo se ensayan en vista cercana con la unidad visible. El motivo de tráfico
  es una avería simulada: coche detenido y rótulo durante seis segundos, unos 80 m por delante.
  No se inventa una avería como explicación de un recálculo real ni se cambian rutas/ETA del servidor.
- Pruebas: Node `--test test_scene.mjs test_director.mjs`; recorrido Chromium con Leaflet/director reales
  y API fixture comprobó 21 coches, avería, pausa, zoom, zona vacía, móvil y cierre sin errores JS.
  Las capturas `.local/traffic-local-desktop.png` y `traffic-local-mobile.png` son fixtures, no tráfico real.

## Recálculos visuales aleatorios (20/09/2026)

- `static/director.js::createRouteRehearsal` espera 12–24 s y luego 45–90 s entre ensayos de 6 s
  sobre una sola ruta terrestre visible en marcha, nunca vuelos ni aproximaciones. Viento/tráfico/acceso
  son motivos de **simulación**, no observaciones ni decisiones LLM. Capa SVG independiente;
  no altera rutas, tiempos, NOAA, SQL/Twin ni dispara peticiones adicionales.
- `static/scene.js` mezcla cronológicamente hasta 40 eventos visuales locales con el historial real;
  se distinguen y no se guardan. Prioridad a eventos reales; cancela con pausa, pestaña oculta,
  desconexión, nueva sesión o revisión de ruta. Movimiento reducido conserva resaltado sin animación.
- Regresiones: `.local/node-v22.19.0-darwin-arm64/bin/node --test test_director.mjs test_scene.mjs`.

## Despliegue en Render (20/09/2026, preparado sin commit)

- `render.yaml` (validado contra `https://render.com/schema/render.yaml.json`): web `flareai` Python, plan
  `1c-2g` Frankfurt, `preDeployCommand: python database.py import`, `startCommand: python app.py
  --presentation --host 0.0.0.0 --port $PORT`, `healthCheckPath: /healthz`; base `flareai-db` Postgres 17
  `0.1c-256mb`, 5 GB. `.python-version` = 3.13: numpy 2.2.6/shapely 2.1.1 no tienen ruedas cp314 y se
  compilarían en Render. `requirements.txt` fija `eccodeslib==2.48.3.28` (la instalada en `.venv`; 2.48.2.27
  no existe para macOS). Guía: `docs/DESPLIEGUE_RENDER.md`. Nada de esto se ha desplegado todavía.
- `app.py`: `--port` toma `PORT`; `FLAREAI_ALLOW_OUTBOUND=1` ≡ `--allow-outbound`; `SIGTERM` → `KeyboardInterrupt`
  (cierre ordenado, libera lease Twin); `GET /healthz`; `FLAREAI_PUBLIC_CONTROLS=1` sustituye la exigencia de
  loopback en `/api/scenario`, `cancel-alert`, `admin/reset` y `/api/demo/setup` (tras el proxy no hay loopback;
  queda la comprobación `Origin == Host`). Sin la variable el comportamiento es el anterior. `/api/demo/setup`
  enlaza `/112/` sobre `RENDER_EXTERNAL_URL`/`FLAREAI_PUBLIC_URL` cuando no hay túnel ni App alojada.
- Petición expresa (mañana del 20/09/2026): los datos estáticos viajan con el código, sin clonar la base.
  `data/seed/assets.jsonl.gz` (17 MB, versionado, gzip `mtime=0` reproducible) contiene `SEED_ASSET_KINDS`
  (red Barcelona, `local_road_graph`, `director_route`, `geocoding`, `player`; sin teselas de preparación ni
  `path`). `database.py seed` lo regenera desde la base local; `bootstrap()` → `import_seed()` lo carga una
  vez por contenido (`flare_imports` `seed:<sha256>`, lock 804027) con `ON CONFLICT DO NOTHING`: nunca pisa
  cachés más recientes. **`flare_settings` (hook_key) no va al repo**; presentación los lee de Twin.
  Primer deploy real: el INSERT jsonb del grafo (43 MB JSON) tiró la conexión en Postgres 256 MB; ahora las filas
  > `SEED_INLINE_LIMIT` (4 MB) no se insertan y `get_asset()` cae a `seed_asset()` (lectura del archivo) si la
  base no tiene la fila. Regresión `test_database.test_seed_assets_load_once_and_never_overwrite`. Al cambiar grafos/rutas en local
  y querer que viajen: `seed` y versionar el archivo.
- `database.py push --url <destino>` queda como opción: upsert idempotente de `flare_sources`, `flare_settings`
  (solo necesarios en `--hackathon`), activos `PUSH_ASSET_KINDS` y comprobaciones de cámaras vigentes con
  catálogo presente. No copia atlas/catálogo ni medios con `path`. Rechaza origen == destino.
  `SET LOCAL statement_timeout=0` para la fila de 14,6 MB.
- Verificado en local con copia de solo archivos versionados + CPython 3.13.15 (`.local/py313`, descarga
  python-build-standalone) contra bases vacías `flareai_render`/`flareai_render2` del clúster local: import
  40 s con semilla (0,6 s la segunda vez), push 255 activos, servidor `--hackathon` en 0.0.0.0 con
  `PORT`/`FLAREAI_PUBLIC_CONTROLS`/`RENDER_EXTERNAL_URL` desde IP de red local (también sobre base sembrada
  solo por `import`, sin push), cierre por SIGTERM. No se probó `--presentation` para no
  competir por el lease Twin ni consumir cuota. Ruff/mypy pasan. Puertos 10001/10002 en este Mac los ocupa
  un proceso Java en loopback: usar puertos altos para pruebas.
- Un solo director por sala Twin: con el local en `--presentation`, Render queda en `standby` (y viceversa).
  Disco de Render efímero (cachés se rehacen); sin disco persistente porque ocultaría `data/` versionado.
  Playwright no va en `requirements.txt`: la verificación de vídeo queda pendiente en Render, las imágenes sí.

## Rendimiento del mapa (20/09/2026, petición expresa de fluidez)

- Perfil real (Chromium headless, rueda de zoom): >55 % de la CPU era Leaflet reproyectando y recortando en
  SVG los ~111.000 vértices de `spain/neighbors/provinces.geojson` en cada fotograma. Ahora los dibuja
  `static/cartography.js` en un solo canvas: proyección una vez a coordenadas de mundo (zoom 0, relativas
  a un origen para no perder precisión en float32), un `Path2D` por entidad y nivel de detalle
  (Douglas-Peucker, `LEVELS`: zoom ≤7, ≤10, completo), islotes subpíxel omitidos en niveles gruesos, recorte
  por caja de la vista y una transformación afín por fotograma. No se tocan los GeoJSON ni `incident.footprint`.
  España y vecinos cargan antes del primer fotograma; las provincias (3,4 MB) llegan después sin bloquear.
- Los GeoJSON se sirven desde SQL serializados/gzip una vez por proceso (`app.py::Cartography`), con `ETag`,
  `304` y `Cache-Control: public, max-age=86400`; el resto de la API sigue `no-store`.
- Teselas IGN: `infrastructure.js::roadLayerMixin` congela la rejilla durante el zoom continuo (eventos
  `flare:zoomstart`/`flare:zoomend` que emiten `zoomTo` de `app.js` y `createCameraTour` de `director.js`):
  solo escala por CSS los niveles cargados, pide teselas al cruzar un zoom entero sin podar y poda al
  descongelar. Quien añada otro zoom programático por fotograma debe emitir esos eventos (y `zoomend` al
  cancelar), o las teselas quedarán congeladas.
- `/api/director` devuelve solo los últimos `PUBLIC_EVENTS` (200) eventos; el historial completo sigue en
  `/api/director/history`. Chispas sin `shadowBlur` (halo como disco tenue); tarjetas del escenario solo se
  reconstruyen si cambia su texto; etiquetas de lugar y rótulo del mapa no se reescriben si no cambian.
- Regresiones: `node --test test_cartography.mjs test_infrastructure.mjs test_director.mjs`. Medir con
  Playwright + CDP `Profiler` antes de optimizar: las cifras absolutas en headless (SwiftShader) no son las
  del navegador real, pero el reparto de tiempo sí. `verify_director_ui.py` falla desde el dispositivo
  automático (locator `.response-vehicle` estricto con seis vehículos), no por estos cambios.

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

## Concurrencia y geocodificación de demo (actualización 19/09/2026)

- `DemoBridge`: hasta 16 llamadas activas combinadas 112/123, 256 por sesión. Reservas atómicas
  permiten inicios simultáneos; 16 workers actualizan fichas sin esperar al run lento, sin duplicar
  polling de un run. Colgar libera capacidad, manteniendo 20 s de recuperación final. Una llamada por
  pestaña; cookies y vinculaciones de bomberos siguen independientes. La cuota remota puede limitarlo.
- Sustituye la política anterior de ubicación pendiente: dirección/POI primero en OpenStreetMap
  Nominatim y después IGN; si falla, intentar vía y municipio explícito, marcando aproximación.
  No inventar un municipio ausente ni confundir un número de portal distinto. Una aproximación no
  confirma un grupo NASA cercano; conserva su punto ilustrativo. `brief` incluye precisión y fuente.
- Nominatim público: un solo proceso, máximo una petición por 1,05 s global, caché SQL 24 h en
  `flare_assets` y caché de sesión. No reintenta periódicamente geocodificación sin cambio de ubicación.
  `FLAREAI_NOMINATIM_URL` permite proveedor propio; vacío desactiva OSM. Solo datos ficticios/públicos
  de demo, nunca información confidencial. Atribución OSM visible. No escalar este endpoint público.
- Guiones breves publicados con autorización: 112 versión `01a0b9cb-262d-7f76-b81b-d7ef983ed615`;
  123 versión `01a0b9cb-2fa1-72d3-a162-57a0284ac3d4`. Mismos workflows/voz/tools, director intacto.
  Dos aclaraciones máximo en 112, una en 123; registrar y cerrar sin interrogatorio ni corte forzado.
  `replace_voice_prompt` exige autorización, verifica versión/llamadas activas, crea fork y publica
  con `unpublish_version_id` explícito; nunca `force`. No invocarlo automáticamente.
- Pruebas: `test_demo` incluye ocho inicios concurrentes, aislamiento, errores, carrera al colgar,
  OSM/IGN/fallback/caché/rate limit. `verify_director_ui.py` comprueba dos 112 y dos 123 activos,
  partes independientes y precisión visible con voz fixture. Usa `examples/` congelado para evitar
  que nuevas detecciones FIRMS invaliden la caché GIBS del ensayo. No es prueba de voz concurrente real.

## Routing MVP: revisión posterior del 19/09/2026

- Sustituye la descripción anterior de routing exclusivamente local: por petición expresa del usuario,
  prima una API de rutas OSM/OSRM para ubicaciones nuevas, con dos proveedores HTTPS (Project OSRM y
  routing.openstreetmap.de), caché SQL, timeout 6 s, 1,05 s entre peticiones y enfriamiento 30 s por
  proveedor caído. A* conserva grafos cacheados como respaldo; ya no descarga Overpass durante el
  despacho. Sin geometría real no inventa una línea de carretera. No hay SLA ni tráfico en las APIs demo.
- El fallo Sagrada Familia no era falta de parques: LLM pidió dos camiones de Llevant y patrulla,
  pero Overpass dio 504 al descargar una caja excesiva. La ruta comprobada de Llevant mide 3,18 km
  en A* local; OSRM devuelve 3,28 km. No se descargó la red nacional; osmium quedó instalado en el
  entorno durante la exploración, pero no es dependencia de ejecución ni está en requirements.
- Dos camiones ficticios por parque, una patrulla por comisaría, un helicóptero por helipuerto.
  Contexto considera seis parques cercanos (antes tres). `stations` publica total/disponible/ocupado;
  mapa muestra disponibles/total y popup. Llegar no libera una unidad; volver sí.
- `dispatch` conserva tipo/cantidad del plan del LLM y prueba hasta tres sedes alternativas libres si
  falla la ruta elegida. No roba unidades ocupadas ni reservadas para otra acción; evento `alternative`
  conserva `requested_resource_id`. Si todas fallan, revisión con backoff 15–180 s y cuota existente.
  `return`/`reassign` no cambian de vehículo. Revisión de avisos antes/después de preparar rutas intacta.
- Verificado con APIs reales: Barcelona, Madrid, Valencia, Sevilla, Roda de Ter y Las Palmas.
  Regresiones `test_local_routes`/`test_director`: proveedor caído, geometría/endpoint inválido,
  alternativa libre, reservas de otras acciones, inventario y reintento. No garantiza cualquier
  ubicación fuera de carretera; siguen vigentes 60 km entre extremos y anclaje a ≤750 m de una vía.

## Revisión de estabilidad de la demo (19/09/2026)

- Retirado por petición expresa el tope local de 30 runs/hora: dejaba el director en `limited`
  sin despachar nuevos avisos. No reinstaurar límites de gasto para esta hackathon. Se conservan
  un run pendiente, validación de planes/rutas y backoff de errores. El máximo de ocho acciones
  por plan no se ha cambiado, ni los workflows publicados.
- Regresión en `test_director`: despacho después de 30/100 runs y ausencia de inicios duplicados.
  `test_demo` HTTP usa `examples/` congelado, no detecciones NASA mutables. Mypy global pasa tras
  precisar el tipo de servidor en `sms_demo.py`; no se ejecutó ningún envío SMS.
- `static/director.js` muestra un aviso persistente ante desconexión, falta de configuración,
  autenticación o worker en standby, incluso con historial cerrado.
- Verificados 181 tests Python con SQL, 6 del marcador, 63 JS, Ruff/mypy/ESLint, atlas y suites UI
  `verify_scene.py` / `verify_director_ui.py`. Voz y planes de las suites UI son fixtures.
- Cloud Barcelona: `eec094b7-5e2b-483c-9b35-9167bb491dbf` movilizó dos camiones, dos ambulancias,
  policía y propuesta ES-Alert. `d6eb9d7b-c742-4e78-a9ff-a4c59a742970` recibió parte crítico pero
  eligió medios terrestres sin helicóptero: `verify_scene.py --cloud --response` falla expresamente
  en ese caso. No garantizar apoyo aéreo ni confundir estas fichas fixture con audio real.
- Para demo fiable usar «Sagrada Familia, Barcelona» o «Plaça de Catalunya, Barcelona»: resolución
  y ruta local verificadas. Ejercicio Collserola `[2.115,41.425]` también tiene ruta. «Tibidabo,
  Barcelona» fallaba (12 acciones `blocked` en tres runs el 19/09/2026) porque `nearest()` anclaba al
  nodo OSM más próximo aunque fuera un fragmento aislado (grafo con 487 componentes <50 nodos), y el
  A* agotaba 300k expansiones. Corregido: `RoadGraph.connected` (componente principal) es el único
  anclaje, con radio ampliado y hueco declarado en `start/end_gap_m`. No se inventa geometría viaria.

## Garantía de ruta (petición expresa 19/09/2026)

- El usuario exige que **siempre** salga una movilización. Cadena en `director.prepare`: ruta estricta
  por sede y hasta tres alternativas → `relaxed=True` (ignora sentidos de circulación, nunca cortes del
  escenario; `approximate: true`) desde la unidad pedida → `ground_fallback()` recta ilustrativa
  (`mode: ground_fallback`). Evento `approximate` con la limitación; el mapa añade «trayectoria aproximada».
  Las rutas aproximadas no se cachean. `blocked` por ruta ya no ocurre para despacho; sigue existiendo por
  fase de retirada, política de helicópteros y cortes en marcha del escenario.

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
  de instalaciones y ficha al pulsar (`static/infrastructure.js`). Petición expresa (19/09/2026):
  los iconos de instalaciones son solo una muestra, máximo dos por familia de icono y ocho en
  total (`relevantFacilities`); no volver a dibujar todas. Las cámaras se mantienen sin recorte. Las cámaras solo aparecen desde
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

## Informes retirados del frontend (20/09/2026, petición posterior)

- El usuario permite limitar la retirada al frontend. Cerebro conserva base y aprendizajes, pero excluye
  notas `report`, enlaces a informes, descargas PDF, contadores y leyenda de informes. Director e historial
  omiten eventos `report_ready`, también al recuperar el historial. No volver a mostrar esta funcionalidad.
- La generación backend, sus endpoints y los documentos existentes se conservan porque comparten el cierre
  con las memorias. No se cambian extinción, regreso ni retirada de testigos; `reported`/`report_id` siguen
  siendo señales internas de finalización. No se borran datos ni se modifican workflows.
- Regresiones: Node `--test test_operations.mjs test_scene.mjs test_director.mjs`; `verify_presentation.py`
  comprueba que el backend conserva el informe pero Cerebro no lo muestra ni ofrece descargas.

## Cerebro y PDF (20/09/2026)

- `reports.base_notes()` define cuatro notas curadas enlazadas, visibles sin operaciones previas.
  `decision_memories()` incorpora esa base y hasta 30 memorias al contexto existente del director;
  no cambia ni publica workflows. Disponibilidad en contexto no demuestra uso por cada decisión.
- `/api/brain` combina base, aprendizajes e informes. El grafo claro y minimalista de `static/operations.js`
  ofrece búsqueda, selección, enlaces entrantes/salientes, desplazamiento, zoom y refresco al estar abierto.
  `.brain-view .brain-graph` debe superar la especificidad de `svg:not(.leaflet-zoom-animated)`:
  esa regla de iconos lo dejaba en 20 px de ancho. Verificar dimensiones reales, no solo presencia de nodos.
  `mergeBrainNotes()` muestra cuatro notas locales de inmediato, fusiona por ID y admite servidores antiguos;
  solo indica contexto IA conectado si el backend también devuelve las cuatro notas base.
  Los Markdown base se sincronizan a `FlareAI-Memoria/`; su origen no se atribuye a aprendizaje de IA.
- PDF stdlib con encabezado, tipografías regular/negrita, tarjetas de balance, secciones y paginación.
  Es un informe final del simulacro; mantiene estimaciones y metodología, sin presentar créditos emitidos.
- Verificación enfocada: `.venv/bin/python -m unittest test_presentation.ReportTests -v`,
  Node `--test test_operations.mjs`, Ruff y recorrido Playwright con API fixture (no llamadas/cloud).
  Comprobación posterior sobre la web real en 8090: dimensiones del grafo, búsqueda, selección, móvil y API caída.
  Capturas claras en `evidence/brain-light-desktop.png` y `evidence/brain-light-mobile.png`.

## Editor manual del escenario (20/09/2026)

- Lápiz rojo a la izquierda de Ajustes (`static/operations.js::createScenarioEditor`); Cerebro se desplaza
  a su izquierda. Panel con selector de incendio, corte aleatorio, dirección del viento hacia 0–359° y
  potencia -100–100 (apagar/normal/avivar). Envía al soltar el slider, serializa órdenes, conserva foco
  de teclado y descarta respuestas de sesiones anteriores. Sin escenario explica el modo requerido.
- Reutiliza POST local `/api/scenario` y sus controles de origen. `random_closure` elige una vía sin cortar
  por delante de una unidad terrestre en marcha; excluye vuelos/rutas aproximadas. A* local recalcula
  desde posición interpolada; sin desvío conserva `held_position`, nunca usa OSRM para saltarse el corte.
  El corte afecta a todas las rutas que usan ese tramo, no solo al incendio elegido para los sliders.
- `fire_power=0` conserva evolución normal; negativo introduce reducción manual hasta 0,0125 km/s;
  positivo añade crecimiento hasta 0,0125 km/s. Los medios siguen restando su trabajo y permanecen los
  topes de radio. Puede reactivar contenido/vigilancia, nunca retirada/cierre; no modifica NASA/NOAA.
  El viento manual marca `wind_changed` para evitar que un giro programado lo sobrescriba.
- Verificar: `.venv/bin/python -m unittest test_scene test_local_routes test_autodispatch test_director test_operations test_presentation`
  y Node `--test test_operations.mjs test_scene.mjs test_director.mjs`.
  UI aislada: `PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_presentation.py --editor`.
  Usa voz/LLM fixtures, atlas/grafo cacheado y HTTP real, sin llamadas ni cloud. Las otras rutas del
  verificador conservan expectativas históricas: `--editor` permite probar este panel independientemente.

## Estadísticas en el historial (20/09/2026)

- El bloque «Control del escenario · Barcelona» se sustituye por cuatro tarjetas de impacto; los controles
  quedan en el editor del lápiz. `static/scene.js::sessionImpact` suma métricas finales de la sesión desde
  `operations.incidents`, deduplicadas por `report_id`, sin mostrar informes ni enlaces PDF.
- CO₂ evitado, superficie preservada y valor hipotético del carbono usan el modelo backend existente;
  no son ahorro de prevención acreditado, ingresos ni créditos. Se indica cobertura parcial y se conserva
  «sin datos» en lugar de inventar ceros. La cuarta tarjeta cuenta operaciones con balance disponible.
- Verificación rápida: Node `--test test_scene.mjs test_operations.mjs test_director.mjs` (43 pruebas).

## Sonido del receptor móvil (20/09/2026)

- `happyrobot-112/static/alerts.js`: ganancia 0,85 (antes 0,18), tono alterno 800/1000 Hz sin saturación,
  prueba audible de 0,8 s al activar antes de la red y alarma de máximo 8 s. Botón de prueba reutilizable.
- Solicita `navigator.audioSession.type = 'playback'` si existe, solo en el receptor sin micrófono.
  Suspensión/interrupción detiene el tono y muestra estado persistente separado del polling; la alerta
  incluye su propio botón de reactivación para no dejarlo detrás del modal. No reproduce histórico.
- Verificación: Node `--test test_director.mjs`; Chromium móvil con API fixture, AudioContext real y pico
  medido 0,85, recuperación tras suspend y silencio. No llamadas, cloud ni escrituras de sesión reales.
  Safari/iOS y volumen físico requieren escucha humana; no garantiza sonido con pantalla bloqueada.
