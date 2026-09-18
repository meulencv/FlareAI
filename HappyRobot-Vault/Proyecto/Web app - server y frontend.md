---
tags: [happyrobot, proyecto, código]
---

# Web app — server y frontend

Carpeta: `voice/` en la raíz del repo `FlareAI`.

```
voice/
├── server.py     # servidor Python (stdlib, sin dependencias)
└── index.html    # frontend con botón de llamada
```

## `server.py`

Servidor HTTP mínimo (`http.server`) con dos responsabilidades:
1. Servir `index.html` como estáticos.
2. `POST /token`: recibe la petición del navegador, y **desde el servidor** (nunca desde el
   cliente) llama a `POST {API_BASE}/voice/tokens/` de HappyRobot con la API key, y reenvía la
   respuesta JSON (url, token, room_name, run_id) al navegador.

Variables de entorno que usa:

| Variable | Default | Uso |
|---|---|---|
| `HAPPYROBOT_API_KEY` | *(obligatoria, sin default)* | Key de HappyRobot. Si falta, el server no arranca. |
| `HAPPYROBOT_API_BASE` | `https://platform.eu.happyrobot.ai/api/v2` | Host del clúster (ver [[Autenticación y hosts API]]) |
| `HAPPYROBOT_WORKFLOW_ID` | `01a0b665-2a84-725f-a714-947e427ea6d2` | El workflow FlareAI Web Voice |
| `PORT` | `8000` | Puerto local |

Por qué así: la API key **nunca debe llegar al navegador** — si la pusiéramos en el frontend,
cualquiera que abra la página podría robarla e iniciar llamadas a tu cuenta ilimitadamente.
Por eso el token de LiveKit (de corta vida, scoped a una sala) se pide desde este backend.

## `index.html`

Frontend estático, sin build (usa el SDK `livekit-client` desde CDN `jsdelivr`).

Flujo del botón "🎙️ Iniciar llamada":
1. `fetch('/token', {method:'POST'})` → recibe `{url, token}`.
2. Crea un `Room` de LiveKit, se suscribe a `RoomEvent.TrackSubscribed` para reproducir el
   audio remoto (`track.attach()` cuando `track.kind === Track.Kind.Audio`).
3. `room.connect(url, token)` + `room.localParticipant.setMicrophoneEnabled(true)` → el
   navegador pide permiso de micrófono y empieza a enviar audio.
4. Botón cambia a "⏹️ Colgar" → `room.disconnect()`.

No hay backend de estado ni base de datos: cada pulsación de "Iniciar llamada" genera un
`run_id` nuevo en HappyRobot.

Relacionado: [[Cómo arrancar todo]] · [[Voice Tokens y LiveKit]] · [[FlareAI Web Voice - workflow]]
