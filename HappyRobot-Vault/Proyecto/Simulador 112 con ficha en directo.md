---
tags: [happyrobot, proyecto, voz]
---

# Simulador 112 con ficha en directo

Aplicación independiente en `happyrobot-112/`, al mismo nivel que FlareAI pero sin importar ni
modificar su código. Simula una conversación de emergencia en el navegador y convierte el
transcript de HappyRobot en una ficha mínima: ubicación, emergencia, personas, riesgos y contacto.

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

## Arranque reproducible

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
