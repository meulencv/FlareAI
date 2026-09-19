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

Sin claves ni secretos: FlareAI no requiere API key para NASA/NOAA. Si en el futuro hiciera
falta alguna, solo en `.env` (nunca en el repo/vault). Los secretos de la implementación
anterior siguen en `versión-anterior/.env` (`HAPPYROBOT_API_KEY`).

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
  de instalaciones y ficha al pulsar (`static/infrastructure.js`). Cámaras públicas con icono,
  agrupadas al alejar y separadas en detalle; agrupaciones coincidentes permiten elegir un elemento.
  Las actualizaciones no deben mover la cámara. El canvas del calor no captura clics.
- El calor acumula degradados radiales y traduce densidad a una paleta de 256 pasos; se dibuja
  al 60 % de resolución, en `multiply`, bajo el fuego, y se repinta una vez por fotograma.
- Carreteras IGN: WMS nacional `TN.RoadTransportNetwork.RoadLink`, siempre visible, teselas
  solicitadas por viewport vía `/roads/z/x/y.png`, caché y metadatos SQL; no es un grafo viario
  descargado completo ni contiene cortes/tráfico. No descargar masivamente teselas.
- Webcams: 2.926 registros del catálogo Faro importados en SQL; no inventario exhaustivo ni
  sincronización automática de catálogos. Capturas solo al abrir, con intervalos del proveedor;
  reproductores públicos tras clic explícito, enlaces originales si no integrables. Allowlists
  de hosts/rutas y redirecciones, límites de bytes, concurrencia y tiempo en `territorial.py`.
- Detecciones sin confirmar en gris. `flare_confirmations` requiere fuente, fecha y caducidad;
  alta confianza FIRMS o noticia histórica no confirma actividad actual. Offline conserva gris.
  Localizador de llama de hasta 32 px al alejarse, distinto de la huella real anclada al terreno.
- La huella del incendio está **anclada al terreno**: no escalar componentes pequeñas según el zoom
  (causaba deformación al acercar). La ondulación se indexa por posición relativa del contorno, no
  por índice de vértice, y su amplitud es proporcional a la extensión dibujada.
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
