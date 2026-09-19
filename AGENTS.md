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

Sin claves ni secretos: FlareAI no requiere API key para NASA/NOAA. Si en el futuro hiciera
falta alguna, solo en `.env` (nunca en el repo/vault). Los secretos de la implementación
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
