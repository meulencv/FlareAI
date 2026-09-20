---
tags: [happyrobot, proyecto, voz]
---

# Simulador 112 con ficha en directo

Marcador web en `happyrobot-112/`, reutilizado por la demo integrada de FlareAI mediante
`demo.py`. Conserva un modo independiente, pero el arranque actual se hace desde `app.py` para
que la llamada actualice automáticamente el mapa. Simula una conversación de emergencia y
convierte tool calls de HappyRobot en una ficha estructurada.

No es el 112 real y la web lo indica de forma permanente. Durante la conversación, sin embargo,
el agente actúa como operador del 112: no rompe el rol ni deriva al llamante a otro 112.

## Por qué esta arquitectura

- Se creó un workflow nuevo desde `inbound-voice-agent`: una web call no necesita SIP ni realiza
  llamadas telefónicas reales. Es el mismo patrón validado en [[Voice Tokens y LiveKit]].
- La API key solo vive en `happyrobot-112/.env` (ignorado por Git). El backend solicita un token
  LiveKit temporal; el navegador nunca recibe la key.
- La ficha se deriva de la sesión real de HappyRobot mediante
  `GET /runs/{run_id}/sessions` y `GET /sessions/{session_id}/messages`. No se usa reconocimiento
  paralelo del navegador, porque habría dos transcripciones potencialmente diferentes.
- Primera versión descartada: el prompt pronunciaba una línea `Ficha: ...` al final de cada turno.
  Como HappyRobot sintetiza todo el texto del agente, decía etiquetas y «pendiente»; además, una
  interrupción podía cortar la ficha antes de completar los campos.
- Solución: tool silenciosa `actualizar_ficha(ubicacion, emergencia, personas, riesgos, contacto)`.
  El modelo la invoca después de cada aportación y conversa por separado de forma natural. La web
  lee `message.tool_calls` y fusiona correcciones; las fichas habladas antiguas y unas inferencias
  urgentes conservadoras quedan solo como respaldo.
- Modelo elegido tras consultar `available_options.models` del schema real:
  `gpt-5.6-sol-low` (familia frontier, esfuerzo bajo para equilibrar comprensión y latencia).
  Transcripción `advanced`; voz Ana HR v3. Se descartó `sol-max`: esta tarea es extracción breve
  en tiempo real y el razonamiento máximo aumentaría la espera sin una ventaja proporcionada.
- El backend no persiste audio ni transcript. HappyRobot sí conserva la sesión según la política
  de la organización.
- Interfaz de hackathon tipo marcador Android: teclado numérico, solo `112` inicia la web call,
  pantalla de contacto «Emergencias», cronómetro y botón de colgar. La ficha no ocupa la pantalla:
  queda oculta por defecto en una hoja inferior accesible desde **Datos recopilados**.

## Recursos

- Workflow: `Simulador 112 · Asistente de voz`
- Workflow ID: `01a0b8bc-b078-7eb0-86fc-b91a7abb6ca8`
- Version ID actual: `01a0b9cb-262d-7f76-b81b-d7ef983ed615` (guion breve; fork autorizado el 19/09/2026)
- Entorno: `production`, publicado y live
- LLM: `gpt-5.6-sol-low`
- Tool: `actualizar_ficha`, con un hijo Python de confirmación sin efectos externos
- Transcriber tier: `advanced`
- Voz: Ana HR; idioma `es`, acento `es-es`
- Web local: `http://127.0.0.1:8112`

## Integración actual con el mapa FlareAI

Petición: una llamada desde el móvil debe confirmar en rojo un foco cercano o crear un aviso
nuevo, sin pulsar nada en el mapa y sin código de vinculación. No hay Twin disponible.

- Se reutilizó el marcador y su proveedor en lugar de crear otra app o workflow. La integración
  está en `demo.py`; el servidor independiente sigue siendo posible pero no actualiza el mapa.
- Se abandonó el código de vinculación para reducir pasos durante la demo. El navegador abre
  `/112/api/session` automáticamente y recibe una cookie HttpOnly/SameSite, Secure bajo HTTPS.
  Esto no es autenticación: cualquiera con el enlace puede consumir cuota. Hay límites locales
  de 64 navegadores, 256 llamadas por sesión y 16 llamadas activas combinadas de 112/123.
  Inicios concurrentes con reservas atómicas y polling independiente por run; colgar libera capacidad.
- El puerto 8112 expone solo el marcador y su API, y Cloudflare publica exclusivamente ese puerto.
  Así el enlace del móvil no abre el mapa, su API de datos, SQL ni archivos del repositorio.
- `actualizar_ficha` del asistente es la evidencia; una frase libre del llamante no basta por sí
  sola para confirmar. El backend consulta mensajes cada 2 s y el mapa cada 2,5 s. La ficha móvil
  consulta el backend cada 0,9 s. No hay webhook ni necesidad de Twin.
- Geocodificación: topónimos locales, OpenStreetMap/Nominatim y después CartoCiudad/IGN para
  direcciones/POI. Si falla, vía o municipio comunicado, etiquetado aproximado; sin zona identificable
  queda pendiente. OSM público limitado a una petición por 1,05 s global, caché SQL 24 h y ubicaciones
  públicas/ficticias, nunca datos personales. Detalle: [[2026-09-19#Llamadas concurrentes y ubicación OSM]].
- Emparejamiento a ≤3 km de la **huella**, no del centroide, porque un foco alargado puede estar
  cerca aunque su centro no lo esté. Si no coincide, se crea `source_kind=call` con geometría
  ilustrativa, sin observaciones, FRP ni hectáreas NASA. No es perímetro quemado.
- La confirmación roja lleva **Llamada web · demo**, fecha, caducidad y evidencia local. No es
  oficial y no modifica datos FIRMS ni `flare_confirmations`. Una corrección sustituye el aviso.
- Cada arranque crea una sesión vacía con UUID nuevo; las cookies anteriores dejan de servir
  hasta recargar el marcador. La migración 3 respalda resúmenes en SQL, pero no los restaura ni
  borra el historial al reiniciar. No se persiste audio ni transcript completo en FlareAI.

### Arranque integrado

Desde la raíz del repositorio, con `happyrobot-112/.env` ya configurado y workflow publicado:

```bash
.venv/bin/python app.py --host 127.0.0.1 --port 8090
```

En otra terminal:

```bash
.venv/bin/python demo.py publish
```

Cloudflared está instalado localmente en `.local/cloudflared/cloudflared`. El comando imprime
la URL temporal HTTPS con `/112/`; mantener ambos procesos activos. Abrir después el mapa en
`http://127.0.0.1:8090` para que **Webcall demo** recoja la dirección. No guardar una URL temporal
como dirección permanente. Ctrl+C en el publicador cierra el túnel. No usar `--offline` para voz
ni arrancar simultáneamente `happyrobot-112/server.py`: competiría por el mismo puerto.

`publish()` comprueba el aislamiento antes de publicar y no pasa variables `HAPPYROBOT_*`,
`TUNNEL_*` ni `CLOUDFLARE_*` al subproceso. Usa configuración vacía y HOME local de cloudflared.

### Verificación de la integración sin código (19/09/2026)

- GET al workflow real: `is_published=true`, `is_live=true`; no se modificó ni republicó.
- Chromium sobre el HTTPS real: SDK LiveKit cargado, sesión automática, cookie Secure/HttpOnly/
  SameSite=Strict, botón habilitado y cero excepciones JavaScript. No se usó `unsafe-eval`.
- Cinco rutas ajenas al marcador devolvieron 404 públicamente; el enlace del mapa usó el túnel
  actual. La sesión arrancó con cero llamadas y cero confirmaciones demo.
- Prueba SQL nueva: tras una llamada simulada persistida, otro `Store` no recupera avisos ni
  acepta la cookie anterior, mientras el registro anterior sigue existiendo. Transacción de
  prueba revertida, sin borrar historial real. Prueba nueva del entorno filtrado de cloudflared.
- Tras entregar la URL al usuario entró una **webcall real sobre Tarragona**. La API real devolvió
  22 mensajes en la comprobación: 11 de usuario, 8 de asistente, 2 eventos y 1 tool. Se extrajeron
  ubicación y emergencia desde `actualizar_ficha`, sin copiar el transcript a la documentación.
  El servidor activo no recibió mocks: creó `Aviso · Tarragona`, `source_kind=call`, sin errores
  de sincronización. Chromium abrió el mapa y verificó selección automática, clase `confirmed`,
  etiqueta **Confirmado por llamada · demo** y cero errores JS, sin hacer clic en el foco.
- Resultado de regresiones: 57 pruebas Python raíz con SQL, 6 del marcador, 42 JavaScript,
  Ruff, mypy y ESLint. El código funcional existente no necesitó cambios para esta prueba.
- **Pendiente:** valoración humana de la calidad de escucha en el móvil y cobertura de otros
  navegadores. El flujo real proveedor → mapa está probado; no se ha medido la latencia de audio.

### Modo independiente histórico (sin integración de mapa)

```bash
cd /Users/meulencv/development/projects/FlareAI/happyrobot-112
cp .env.example .env
# Completar HAPPYROBOT_API_KEY sin versionarla.
python3 setup_happyrobot.py
python3 server.py
```

`setup_happyrobot.py` es idempotente por nombre: crea o actualiza prompt, modelo, voz y tool,
republica el workflow y guarda solo identificadores no secretos en `workflow.json`.

Pruebas:

```bash
python3 test_server.py
../.local/node-v22.19.0-darwin-arm64/bin/node --check static/app.js
```

## ES-Alert por peligro para la población (2026-09-20)

Petición: «la decisión de activar […] la debe tomar el agente, no el bombero». En presentación el parte
llega por llamada saliente vinculada a la llegada del equipo, no por el antiguo marcador 123.

Se identificaron dos bloqueos: el prompt solo admitía petición explícita o evolución crítica y el backend
interpretaba `no_solicitado` como veto. Se prepararon una política compartida para ambos directores y un
cambio del guion saliente: conservar amenazas, negaciones y posible exposición en el `detalle`, sin preguntar
si hay que activar ES-Alert. El director decide si humos tóxicos u otro peligro amenazan a la población;
no basta un incendio pequeño, humo genérico o estar cerca de viviendas. Evacuación y confinamiento son
medidas distintas: la instrucción de simulación depende de la amenaza, no se evacúa automáticamente al humo.

Para vincular la conclusión a la evidencia, `alert` admite `population_risk=true` y `report_evidence` con
el `detalle` íntegro actual. El servidor comprueba esa copia, pero la valoración semántica sigue siendo del
LLM, no de un buscador de palabras. Se mantienen las peticiones explícitas sin esperar al director, los
partes críticos como habilitantes, el bloqueo por descarte/extinción, la deduplicación y el veto humano de
tres segundos. Una corrección del parte invalida planes pendientes. No se modifica el esquema SQL/Twin.

Se reprodujo primero el fallo mediante pruebas, luego se corrigieron ejecutor y prompts. Verificación:

```bash
.venv/bin/python -m unittest test_operations test_director test_presentation test_scene test_autodispatch test_demo test_local_routes -q
```

Resultado: 130 pruebas, Ruff y mypy pasan. Usan parte y decisión fixtures: no prueban interpretación de audio
ni razonamiento remoto.

### Registro de publicación y activación

1. El usuario autorizó sustituir los dos prompts. Antes de cada cambio se comprobó que no había runs activos.
2. Director, mismo workflow `01a0b948-d14b-7883-bb58-2c9a014f27f4`: versión nueva
   `01a0bc22-7844-71ac-82d9-26479d46e02b`. La comprobación inicial falló por visibilidad tardía de publicación;
   un GET posterior confirmó `is_live`/`is_published` y prompt exacto, sin repetir la publicación.
3. Voz saliente, mismo workflow `01a0ba93-b11b-7ed2-8e1d-2bc94b7eba1e`: versión nueva
   `01a0bc23-078f-75a8-96d7-ba7d29e61424`, publicada/live. Se compararon configuración de voz, herramienta,
   modelo y saludo antes/después: conservados. 112 ciudadano no se modificó.
4. Metadatos sincronizados en la configuración existente local/Twin, sin migrar esquema ni alterar contactos.
5. Con una segunda autorización, cierre ordenado y reinicio de `app.py --presentation --allow-outbound
   --host 127.0.0.1 --port 8090 --mobile-port 8112`. API director en `idle`, sin asignaciones/alertas,
   marcador HTTP 200. Sesión nueva: recargar mapa/marcador; historial guardado conservado.

No se iniciaron llamadas ni runs de prueba. **Pendiente opcional:** ensayo de la nueva decisión con LLM/audio
real, que requiere autorización aparte; publicación verificada no equivale a haber ensayado la conversación.

## Sonido de la alerta móvil (2026-09-20)

Petición: «haz que suene fuerte […] ahora mismo no suena». La revisión encontró un tono atenuado
(ganancia 0,18), activación sin prueba audible y recuperación de audio detrás del modal de alerta;
el polling además sobrescribía el aviso de suspensión.

1. Se reprodujeron los fallos de activación y recuperación con pruebas del receptor.
2. Se elevó la ganancia a 0,85, conservando seno alterno 800/1000 Hz sin saturación y máximo ocho segundos.
3. Activar reproduce una prueba de 0,8 s antes de la red; el botón permite repetirla. Se solicita sesión
   `playback` cuando el navegador lo permite, exclusivamente en el receptor sin captura de micrófono.
4. El estado de sonido ya no depende del texto de conexión. Si se suspende, se detiene el tono y el modal
   ofrece **Activar sonido de esta alerta**. Aceptación, cancelación y fin natural liberan el audio.
5. Verificados Node `--test test_director.mjs` y Chromium en viewport móvil: Web Audio real con pico 0,85,
   prueba breve, recuperación tras suspensión y silencio; sin errores JS. API fixture, sin llamadas,
   cambios de workflows ni escrituras remotas.

**Pendiente:** recargar `/112/alerts/` y confirmar escucha en el móvil físico, especialmente Safari/iOS.
Hay que pulsar activar y subir el volumen multimedia; la web no controla el volumen del dispositivo
ni garantiza reproducción con la pantalla bloqueada o el navegador suspendido.

## Comportamientos comprobados

- Creación/publicación por API, workflow live, Ana HR y español.
- `POST /api/call` devuelve `url`, `token`, `room_name` y `run_id`.
- Antes de que LiveKit cree una sesión, `/runs/{id}/sessions` puede responder 404. La web lo trata
  como `waiting`, no como fallo.
- Tras recuperar la conectividad, el navegador automatizado estableció la llamada: estado
  `En llamada`, sesión `in-progress` y apertura «Emergencias 112…».
- Flujo visual verificado: marcar `1-1-2`, abrir/cerrar la hoja de datos, conectar la llamada,
  mostrar cronómetro y regresar al marcador al colgar.
- Interfaz revisada como app de teléfono real: iconos Material en SVG (`<symbol>` + `<use>`) para
  llamar, colgar, borrar, micrófono, altavoz y teclado, en lugar de glifos tipográficos como `☎`.
  El auricular rojo se gira 135° igual que en Android y el botón de silenciar corta el micrófono
  de verdad vía `setMicrophoneEnabled`.
- Medido sin scroll en 320×568, 375×667, 393×852 y 412×915: teclas de 49 a 68 px y botón de llamar
  de 54 a 68 px, escalados con `clamp(..., min(vw, dvh), ...)`. En escritorio (≥600 px) se dibuja
  el marco de móvil centrado de 400 px.
- Replay de la llamada problemática anterior: recupera `calle Rosetas, 18`,
  `Incendio / fuego` y `personas atrapadas; peligro vital indicado`, aunque las respuestas antiguas
  habían quedado interrumpidas.
- Seis pruebas unitarias cubren fichas parciales/vacías, correcciones, tool calls en dos formatos,
  respaldo urgente y `Ubicacion` sin tilde.

Relacionado: [[FlareAI Web Voice - workflow]] · [[Voice Tokens y LiveKit]] · [[Web app - server y frontend]]


## Sala independiente de Render (2026-09-20)

Render quedaba en `standby` porque el local conservaba el lease Twin `804030`. Ahora `TwinDatabase`
usa un prefijo estable derivado de `RENDER_SERVICE_ID` para el lease, heartbeat y documentos remotos.
El local conserva sus identificadores. Cada sala mantiene un único director; no se desactiva el cerrojo.
El marcador de Render apunta a su propio `/112/`, y su reset se limita a sesiones del proceso y
sus documentos de sala. No cambia workflows, contactos ni autorización de llamadas salientes.

20 pruebas de Twin/presentación y Ruff pasan con proveedores simulados; no se lanzó una llamada real.
Después del despliegue hay que recargar mapa y marcador e iniciar una llamada nueva.


## Exhibición visual autónoma de Render (2026-09-20)

La decisión posterior sustituye la sincronización de llamadas y la sala Twin en Render: el jurado
ve hasta dos fuegos ficticios con movimientos y extinción automáticos. `visual_demo.py` dirige el
simulador existente, sin proveedor LLM ni teléfono. Avisos y decisiones aparecen como simulados;
se muestran imágenes guardadas y fechadas de NASA GIBS y de una cámara de Barcelona.
Cortes, viento y potencia modifican el escenario. Solo se activa automáticamente bajo Render;
local sigue intacto. `FLAREAI_VISUAL_DEMO=0` permite volver al modo conectado.

Relacionado: [[Dashboard y simulador]] · [[2026-09-20]].
