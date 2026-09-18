---
tags: [happyrobot, proyecto]
---

# Dashboard y simulador

## Dashboard (`web/server.py` + `web/static/index.html`)

Servidor stdlib (`ThreadingHTTPServer`), sin dependencias; frontend con Leaflet (mapa oscuro CARTO)
y `livekit-client` por CDN. `python web/server.py` → http://localhost:8000.

- Mapa: incidentes 🔥 con círculo por prioridad y **cono de trayectoria** (rumbo = viento+180,
  alcance del motor), activos ▲, medios ■ (ocupados), evidencias (puntos).
- Panel de incidentes: estado, confianza, riesgo, plan vigente, razonamiento del analista.
- **Acciones propuestas**: Aprobar/Rechazar (→ WF-Approve). Historial con resultados de llamada.
- **Sala de llamadas**: "Llamar al 112 virtual" (tú eres el ciudadano), "Descolgar" en acciones
  `ready` (tú eres la persona llamada), "Escuchar"/"Tomar el control" en `executing` (cloud, vía
  `voice/tokens` con `session_id`).
- Simulador integrado (botones): aviso 112, satélite + viento O, giro 180°, meteo real (Open-Meteo), reset.
- Config en caliente: `wind_shift_deg`, `cluster_radius_km`, `auto_approve_kinds`.
- API: `GET /api/state`, `/api/log`, `POST /api/actions/{id}/decide`, `/api/voice/token`,
  `/api/voice/finished` (local), `/api/sim/{paso}`, `/api/config`.
- La API key nunca llega al navegador. Modo `local`/`cloud` automático según Twin.
- En local, la voz usa el workflow básico **FlareAI Web Voice** (`HAPPYROBOT_VOICE_FALLBACK_WORKFLOW_ID`)
  porque los workflows SOS de voz fallan en su primer nodo Twin; el resultado de la llamada se marca
  con botones al colgar.

## Simulador (`main_simulation.py` → `sos/simulation/scenario_wind_shift.py`)

Guion en 5 pasos → [[Escenario demo - giro de viento]]. `--cloud` dispara los hooks reales (las
llamadas de voz quedan para el navegador), `--verbose` traza cada nodo, `--pause N` para presentar.

Relacionado: [[SOS Crisis Engine - arquitectura]] · [[Voice Tokens y LiveKit]] · [[Cómo arrancar todo]]
