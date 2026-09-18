---
tags: [happyrobot, concepto, api, voz]
---

# Voice Tokens y LiveKit

HappyRobot usa **LiveKit** (WebRTC) como transporte de audio para las llamadas de voz desde
navegador ("Web call"). El flujo es:

1. **Backend** (con la API key, nunca expuesta al navegador) pide un token:
   ```
   POST /voice/tokens/
   Authorization: Bearer <api_key>
   {
     "workflow_id": "<uuid o slug del workflow>"
   }
   ```
2. La respuesta trae credenciales de LiveKit:
   ```json
   {
     "url": "wss://livekit.platform.eu.happyrobot.ai",
     "token": "eyJhbGciOi...",
     "room_name": "<workflow_id>_webcall_<uuid>",
     "run_id": "<uuid>"
   }
   ```
3. **Frontend** usa el SDK `livekit-client` para conectarse a `url` con ese `token`, activa el
   micrófono, y reproduce el audio que llega (la voz del agente) suscribiéndose a las pistas de
   audio remotas.

## Parámetros de `/voice/tokens/`

| Campo | Uso |
|---|---|
| `workflow_id` | UUID o slug del workflow. Inicia una llamada **nueva**. Excluyente con `session_id`. |
| `session_id` | UUID de una sesión **ya en curso** — para unirte a ella (escuchar o tomar el control). Excluyente con `workflow_id`. |
| `should_takeover` | Si `true` + `session_id`: tomas el control de la llamada y el agente IA se desconecta. Solo válido con `session_id`. |
| `data` | Objeto libre — se pasa al agente de voz como atributos del participante (solo con `workflow_id`). |
| `env` | `production` \| `staging` \| `development`. Default `production`. |
| `ttl_seconds` | Duración del token (60s–24h). Default 21600 (6h). El navegador debe reconectar antes de que expire; LiveKit no refresca tokens en llamadas activas. |

## Por qué el token se pide desde un backend propio

La API key de HappyRobot **nunca debe llegar al navegador**. Por eso montamos un mini-servidor
(`voice/server.py`) que hace de intermediario: el navegador le pide un token a
`POST /token` (nuestro servidor), y él internamente llama a `/voice/tokens/` con la key.
Ver [[Web app - server y frontend]].

Relacionado: [[FlareAI Web Voice - workflow]] · [[Catálogo de voces]]
