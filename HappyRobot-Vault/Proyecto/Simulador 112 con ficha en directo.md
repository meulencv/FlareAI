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
- Version ID: `01a0b8bc-b086-755f-8816-f90e5186d1a0`
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
  de 64 navegadores, 20 llamadas por sesión y 3 llamadas en seguimiento simultáneo.
- El puerto 8112 expone solo el marcador y su API, y Cloudflare publica exclusivamente ese puerto.
  Así el enlace del móvil no abre el mapa, su API de datos, SQL ni archivos del repositorio.
- `actualizar_ficha` del asistente es la evidencia; una frase libre del llamante no basta por sí
  sola para confirmar. El backend consulta mensajes cada 2 s y el mapa cada 2,5 s. La ficha móvil
  consulta el backend cada 0,9 s. No hay webhook ni necesidad de Twin.
- Geocodificación: topónimos locales primero; CartoCiudad/IGN para direcciones españolas sin
  API key. Se exige coincidencia inequívoca y dentro de España: lo ambiguo queda pendiente.
  Un municipio sigue siendo aproximado; no se inventa el punto exacto del incendio.
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
- **Pendiente:** conversación humana real desde móvil → `actualizar_ficha` → cambio automático
  del mapa. Se entregó la URL al usuario; no confundir estas pruebas ni los mocks con voz real.

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
