---
tags: [happyrobot, proyecto]
---

# Dashboard y simulador

## FlareAI actual: recálculos visuales esporádicos (2026-09-20)

El usuario pidió dar algo de aleatoriedad al historial y representar visualmente algún recálculo,
no muchas rutas a la vez. Se añadió un ensayo puramente de frontend para no provocar cortes ni
modificar desplazamientos que ya están coordinados en el servidor.

- `static/director.js`: elige al azar una unidad terrestre en marcha con ruta visible y no aproximada.
  Primera oportunidad a los 12–24 s (hay trayectos acelerados de solo 45 s); después espera 45–90 s entre efectos. Seis segundos de resaltado
  violeta con trazo discontinuo en movimiento, seguido de «Ruta revisada · simulación».
- Motivos aleatorios: viento cambiado, vehículo averiado y acceso alternativo. Mensajes identificados
  como simulación; no representan observaciones NOAA, cálculos nuevos ni decisiones del LLM.
- `static/scene.js`: eventos visuales intercalados por fecha con el historial, separados de SQL/Twin,
  hasta 40 entradas locales. Desaparecen al recargar o cambiar sesión, no sobrescriben pasos reales.
- No añade llamadas HTTP, no mueve la cámara para mostrar el efecto y no altera rutas, ETA o viento.
  Los eventos reales tienen prioridad. Pausa, ocultación, desconexión y cambios de ruta cancelan el ensayo.
  Movimiento reducido mantiene el resaltado estático.
- Regresión: cadencia, elección aleatoria, rutas excluidas, cancelación e inmutabilidad. Suite JavaScript:
  `.local/node-v22.19.0-darwin-arm64/bin/node --test test_*.mjs`.
- Verificación de navegador: Chromium de escritorio y viewport móvil con movimiento reducido,
  sobre Leaflet real y estado fixture. Se comprobaron historial, un único trazo animado, finalización,
  pausa, prioridad de un evento real y limpieza al cambiar sesión, sin errores JavaScript ni llamadas
  externas. No es un ensayo live del director ni una nueva prueba de voz.

## Tráfico visual local (2026-09-20)

Petición: algo de movimiento junto a los camiones y las carreteras próximas, sin coches por todo el mapa;
un obstáculo puntual puede explicar un ensayo de recálculo, pero no debe inventarse una causa real.

Se conserva el aspecto de los coches. Aparecen progresivamente entre zoom 13 y 14, solo alrededor de
unidades terrestres visibles: ≤650 m y ≤220 px, máximo 24 tramos y 48 coches. La selección sigue el
marcador, también en pausa y con movimiento reducido. Barcelona usa cajas locales de su red preparada;
fuera de ella se reutiliza la geometría de las rutas disponibles, sin descargar ni fabricar calles.

El ensayo de tráfico muestra ahora un coche averiado y «Avería · simulación» durante seis segundos,
unos 80 m por delante de una unidad. Solo se ensaya en vista cercana; no cambia rutas, tiempos ni órdenes.
Los cortes reales del escenario siguen separados, con su identificador de tramo y el recálculo del servidor.

Verificación: regresiones Node de proximidad, presupuesto, vuelos/rutas aproximadas, pausa, respuesta tardía
y avería. Recorrido Chromium con Leaflet/director reales y estado fixture: 21 coches, avería, pausa, zoom,
zona vacía, móvil y retirada al terminar; sin errores JavaScript ni servicios externos. No es tráfico observado.

Los apartados siguientes describen el dashboard **anterior**, apartado en `versión-anterior/`.

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
