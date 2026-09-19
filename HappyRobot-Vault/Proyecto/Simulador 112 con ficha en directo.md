---
tags: [happyrobot, proyecto, voz]
---

# Simulador 112 con ficha en directo

Aplicación independiente en `happyrobot-112/`, al mismo nivel que FlareAI pero sin importar ni
modificar su código. Simula una conversación de emergencia en el navegador y convierte el
transcript de HappyRobot en una ficha mínima: ubicación, emergencia, personas, riesgos y contacto.

No es el 112 real. El agente lo declara al empezar, nunca afirma que ha movilizado recursos y,
ante peligro inmediato, pide ponerse a salvo y llamar al 112 real.

## Por qué esta arquitectura

- Se creó un workflow nuevo desde `inbound-voice-agent`: una web call no necesita SIP ni realiza
  llamadas telefónicas reales. Es el mismo patrón validado en [[Voice Tokens y LiveKit]].
- La API key solo vive en `happyrobot-112/.env` (ignorado por Git). El backend solicita un token
  LiveKit temporal; el navegador nunca recibe la key.
- La ficha se deriva del transcript real de HappyRobot mediante
  `GET /runs/{run_id}/sessions` y `GET /sessions/{session_id}/messages`. No se usa reconocimiento
  paralelo del navegador, porque habría dos transcripciones potencialmente diferentes.
- El prompt termina cada respuesta con una línea pronunciable y estable:
  `Ficha: Ubicación: … | Emergencia: … | Personas: … | Riesgos: … | Contacto: …`.
  Así el llamante confirma lo entendido y el frontend puede extraer campos sin otro LLM.
- El backend no persiste audio ni transcript. HappyRobot sí conserva la sesión según la política
  de la organización.

## Recursos

- Workflow: `Simulador 112 · Asistente de voz`
- Workflow ID: `01a0b8bc-b078-7eb0-86fc-b91a7abb6ca8`
- Version ID: `01a0b8bc-b086-755f-8816-f90e5186d1a0`
- Entorno: `production`, publicado y live
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

`setup_happyrobot.py` es idempotente por nombre: crea y publica el workflow si no existe y guarda
solo identificadores no secretos en `workflow.json`.

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
- La interfaz se verificó en escritorio y responsive. El navegador automatizado no pudo establecer
  el peer connection WebRTC (`could not establish pc connection`), aunque sí obtuvo token y permiso
  de micrófono; la interfaz recupera el fallo y ofrece reintentar. La prueba de voz final requiere
  un navegador local con conectividad WebRTC.
- Cuatro pruebas unitarias cubren extracción, correcciones, campos incompletos y `Ubicacion` sin
  tilde.

Relacionado: [[FlareAI Web Voice - workflow]] · [[Voice Tokens y LiveKit]] · [[Web app - server y frontend]]
