---
tags: [happyrobot, proyecto]
---

# Workflows SOS (los 9 desplegados en HappyRobot)

Todos definidos en `sos/workflows/<nombre>.py` con el DSL de `_builder.py`. Ids/slugs/hooks reales
en `deploy-state.json` y en [[IDs y recursos]]. Org `hackspainteam3`, clúster EU.

| Clave | Nombre en la plataforma | Trigger | Qué hace |
|---|---|---|---|
| `ingest` | SOS · Ingesta de evidencias | hook (predefined, `callable_by_workflows`) | sobre plano → `preparar` (Python) → `buscar` (SQL: incidente abierto en radio/ventana de config) → `decidir` (Python: agrupar o crear) → `guardar_incidente`/`guardar_evidencia` (Write to Twin) → Call **assess** |
| `assess` | SOS · Evaluación de incidente | Workflow Function (`incident_id`, `reason`) | `contexto` (SQL con JSON de incidente, evidencias, meteo, activos ≤40 km, medios, contactos, acciones previas, config) → `riesgo` (motor) → `resumen` (texto) → **Reasoning Agent "Analista de crisis"** con tools `guardar_evaluacion`, `guardar_plan`, `proponer_accion` (esta última llama a **execute** si la acción no requiere aprobación) |
| `execute` | SOS · Ejecución de acción | Workflow Function (`action_id`) | rutas por tipo: llamadas → canal `webcall` (acción `ready`) o `phone` (pendiente de número); `dispatch` → medio `en_route`; `notify` → done |
| `approve` | SOS · Aprobación humana | hook (`action_id`, `decision`, `operator`) | marca approved/rejected y llama a **execute** |
| `outbound_voice` | SOS · Llamada saliente (web call) | Web call con `data` (action_id, kind, role, contact_name, place, instructions, incident_summary…) | marca `executing` + run_id → agente de voz **Flare** (es-ES, Ana HR, signals `incident.*`) → tool `registrar_resultado` (→ done/failed; si hay `new_info` → Call **ingest**) |
| `citizen_inbound` | SOS · 112 virtual (web call) | Web call | lista de lugares y de incidentes abiertos desde Twin → agente 112 → tool `registrar_aviso` (elige `lugar_ref` → lat/lon) → Call **ingest** |
| `weather_inject` | SOS · Meteo: observación y giro de viento | hook (`callable_by_workflows`) | guarda observación, compara con la anterior; si giro ≥ `config.wind_shift_deg` → **signal** `incident.<id>` + Call **assess** (`wind_shift`) |
| `weather_feeder` | SOS · Meteo: sondeo Open-Meteo (cron) | cron `*/5` | para cada incidente abierto: GET Open-Meteo → Call **weather_inject**. **Despublicado** hasta que haya Twin (evita runs fallidos) |
| `firms_feeder` | SOS · FIRMS: sondeo satélite (cron) | cron `*/10` | GET FIRMS CSV (variable `FIRMS_MAP_KEY`) → parse → Loop → Call **ingest**. **Despublicado** (sin key ni Twin) |

Variables de workflow que crea `sos deploy` en cada uno: `HAPPYROBOT_API_KEY` (oculta),
`HAPPYROBOT_API_BASE` (+ `FIRMS_MAP_KEY`, `FIRMS_BBOX` en el feeder). Se usan solo en nodos
Webhook (signal, FIRMS): los nodos Twin corren como la org.

## Extender

- Nueva fuente: adapter en `sos/sources` + (opcional) feeder cron que llame a `ingest`.
- Nuevo tipo de acción/canal: rama en `execute.py` + clave en `config.channels`/`auto_approve_kinds`.
- Nuevo tipo de desastre: solo `config.hazard_capabilities` y datos de activos/medios.
- Teléfono real: adapter `phone` en `execute.py` con **Outbound Voice Agent** (`from_number`
  obligatorio → comprar número `POST /phone-numbers/` o SIP trunk).

Relacionado: [[Formato de nodos por API]] · [[Reasoning Agent y tools]] · [[Cómo desplegar - sos deploy]] · [[Esquema de datos SOS]]
