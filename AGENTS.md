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

## Prueba SMS independiente (2026-09-19)

- `sms_demo.py` + `static/sms.{html,css,js}`: interfaz local de SMS, independiente de `app.py`.
  Arranque: `python sms_demo.py serve` → `http://127.0.0.1:8091` (solo loopback).
- `sms-workflow.json` contiene únicamente IDs/estado, nunca claves. Workflow remoto
  `FlareAI SMS Test`, remitente Telnyx `+15304471317`, trigger con `to`/`message` → Send SMS.
- Autenticación resuelta con una clave regenerada desde la UI y Version 3 publicada. Usar el
  valor literal del trigger en `HAPPYROBOT_SMS_HOOK_KEY`, enviado como `X-API-Key` al hook.
  No sustituirlo por la clave de cuenta ni su hash. Republicar Version 2 sin regenerar no resolvió
  los 401 anteriores. La causa interna no se confirmó; mantener Enhanced Security activado.
  `HAPPYROBOT_API_KEY` sirve para consultas de estado y admite lectura de `versión-anterior/.env`,
  autorizada por el usuario. La ruta API para iniciar runs devolvió 502; se usa el webhook directo.
- Las claves proporcionadas en chat se pasaron por entorno de proceso, no se guardaron en archivos.
  Reiniciar el servidor requiere volver a proporcionar las variables. Nunca imprimir config completa
  de nodos: el trigger puede contener campos secretos incluso si la API lo devuelve con `type: action`.
  En Windows, terminar la shell puede dejar vivo el hijo `python sms_demo.py serve`: comprobar
  los PID antes de reiniciar y confirmar `/api/config` después para no servir la sesión anterior.
- Verificación aislada: `python -m unittest test_sms_demo -v`,
  `python -m py_compile sms_demo.py test_sms_demo.py`, `node --check static/sms.js`,
  `npx --yes --package eslint@9.33.0 eslint static/sms.js`.
  Pruebas con mocks; no enviar SMS reales sin autorización del destinatario/texto concreto.
- La publicación de versiones puede ejecutar nodos de prueba automáticamente. No dejar un
  destinatario real en los ejemplos. El run autenticado `2bf83087-a39b-4865-b1bb-1c4373eb6e41`
  con destinatario vacío inició Version 3 y falló en Send SMS con `to is required` (esperado).
  No se ha probado la entrega real. No confundir `completed` con SMS entregado.

## Prueba Telegram independiente (2026-09-19)

- SMS queda pendiente del mentor: Telnyx rechazó un envío autorizado con 40305 (asociación al
  Messaging Profile); el número Twilio comprado en HappyRobot no aparece en la opción gestionada
  de toll-free. No comprar más números ni reintentar mensajes idénticos sin resolver la configuración.
- `telegram_demo.py` reutiliza el servidor protegido y la deduplicación de `sms_demo.py`.
  `static/telegram.{html,js}` reutiliza `static/sms.css`; no cambia el observatorio ni el atlas.
- Arranque con `HAPPYROBOT_API_KEY` en el entorno: `python telegram_demo.py serve` →
  `http://127.0.0.1:8092`. `prepare` crea/reanuda únicamente su workflow, sin destinatario real.
- Workflow `FlareAI Telegram Demo`: `01a0b90b-bc5e-7b7c-b080-71f35f139200`, slug `qinusphyej9n`.
  `telegram-workflow.json` guarda solo IDs/estado. El token del bot se introduce en la web local,
  se verifica con getMe/getWebhookInfo y, con consentimiento, se guarda como variable oculta
  `TELEGRAM_BOT_TOKEN` en producción de HappyRobot. No archivos locales ni almacenamiento del navegador.
- Un enlace `/start` de un solo uso vincula un chat privado, con nonce y caducidad de 10 minutos.
  No usar bots que ya tengan webhook: la aplicación los rechaza sin modificarlo. No hay difusión
  masiva, geolocalización ni órdenes operativas; el servidor fuerza el prefijo SIMULACRO.
- El webhook creado por API devolvió 401 aun usando una clave UUID. Pendiente regenerar esa clave
  desde la UI en una versión editable y publicar Production. El botón de comprobar HappyRobot
  descubre la versión Live, lee su clave en memoria y prueba con chat_id=0, nunca un chat real.
  Envío bloqueado hasta tener bot, chat vinculado y autenticación comprobada. No desactivar seguridad.
- Verificación: `python -m unittest test_sms_demo test_telegram_demo -v` (27 pruebas sin red),
  `python -m py_compile sms_demo.py telegram_demo.py test_sms_demo.py test_telegram_demo.py`,
  `npx --yes --package eslint@9.33.0 eslint static/sms.js static/telegram.js`.
  Pendiente la recepción real en Telegram. Una ejecución completada no confirma lectura.
- Reiniciar pierde vinculación, bot en memoria y deduplicación. Hay que conectar/vincular de nuevo.
  El token permanece en la variable oculta de HappyRobot hasta que su propietario lo cambie/revoque.

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
